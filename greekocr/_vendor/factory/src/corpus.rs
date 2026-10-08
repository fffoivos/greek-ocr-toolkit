//! Corpus ingest: JSONL line records -> quality-gated, codec-encodable, deduped candidate pool.
//! Every rejection is ACCOUNTED (reason x source), never silent.

use crate::codec::Codec;
use crate::recipe::Recipe;
use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::io::BufRead;
use xxhash_rust::xxh3::xxh3_64_with_seed;

pub const SPLIT_SALT: &str = "greek-page-ocr/v1";

fn d_provenance() -> String {
    "born_digital".into()
}

#[derive(Deserialize)]
struct RawLine {
    text: String,
    source_dataset: String,
    #[serde(default)]
    source_doc_id: String,
    #[serde(default)]
    license: String,
    /// "born_digital" (trust content — a stray Latin/Cyrillic char is CONTENT) or "ocr"
    /// (historic scans — mixed-script words are misread homoglyphs, weed them).
    /// Owner rule 2026-07-07: character-content weeding is only valid for OCR-derived sources.
    #[serde(default = "d_provenance")]
    provenance: String,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct PoolLine {
    pub gt_nfd: String,
    pub script_class: String,
    pub split: String,
    pub line_id: String,
    pub source_dataset: String,
    pub source_doc_id: String,
    pub license: String,
}

#[derive(Serialize, Default)]
pub struct IngestReport {
    pub read: usize,
    pub kept: usize,
    /// reason -> source_dataset -> count
    pub rejected: HashMap<String, HashMap<String, usize>>,
    pub split_counts: HashMap<String, usize>,
    pub class_counts: HashMap<String, usize>,
    pub pool_cap_trims: HashMap<String, usize>,
}

fn reject(rep: &mut IngestReport, reason: &str, src: &str) {
    *rep.rejected.entry(reason.into()).or_default().entry(src.into()).or_default() += 1;
}

pub fn split_of(gt_nfd: &str) -> &'static str {
    let seed = xxh3_64_with_seed(SPLIT_SALT.as_bytes(), 0);
    let b = xxh3_64_with_seed(gt_nfd.as_bytes(), seed) % 1000;
    if b >= 985 {
        "reserved"
    } else if b >= 940 {
        "val"
    } else {
        "train"
    }
}

pub fn line_id_of(gt_nfd: &str) -> String {
    let seed = xxh3_64_with_seed(SPLIT_SALT.as_bytes(), 0);
    format!("{:016x}", xxh3_64_with_seed(gt_nfd.as_bytes(), seed))
}

fn is_greek(c: char) -> bool {
    matches!(c, '\u{0370}'..='\u{03FF}' | '\u{1F00}'..='\u{1FFF}')
}
fn is_latin(c: char) -> bool {
    c.is_ascii_alphabetic() || matches!(c, '\u{00C0}'..='\u{024F}')
}
fn is_cyrillic(c: char) -> bool {
    matches!(c, '\u{0400}'..='\u{04FF}')
}

/// Marks whose presence on a Greek base makes a line polytonic (NFD space).
fn is_poly_mark(c: char) -> bool {
    matches!(c, '\u{0313}' | '\u{0314}' | '\u{0342}' | '\u{0345}' | '\u{0300}' | '\u{0304}' | '\u{0306}')
}

/// Classify an NFD line. None => mixed in a way we refuse (accounted by caller).
/// `ocr_derived`: apply the homoglyph word-guard (OCR sources only — born-digital text is
/// trusted; its mixed-script words are real content, e.g. brand names, inline citations).
pub fn classify(gt_nfd: &str, ocr_derived: bool) -> Option<&'static str> {
    let mut greek = 0usize;
    let mut latin = 0usize;
    let mut cyr = 0usize;
    let mut poly = false;
    let mut prev_base: Option<char> = None;
    for c in gt_nfd.chars() {
        if is_greek(c) {
            greek += 1;
        } else if is_latin(c) {
            latin += 1;
        } else if is_cyrillic(c) {
            cyr += 1;
        }
        if Codec::is_mark(c) {
            if let Some(b) = prev_base {
                if is_greek(b) && is_poly_mark(c) {
                    poly = true;
                }
            }
        } else {
            prev_base = Some(c);
        }
    }
    // Homoglyph contamination guard — OCR-DERIVED SOURCES ONLY: a single WORD mixing
    // greek+latin or greek+cyrillic letters is a misread (в/β, o/ο). In born-digital text the
    // same pattern is genuine content and must be kept.
    if ocr_derived {
        for w in gt_nfd.split(' ') {
            let g = w.chars().any(is_greek);
            let l = w.chars().any(is_latin);
            let cy = w.chars().any(is_cyrillic);
            if (g && l) || (g && cy) || (l && cy) {
                return None;
            }
        }
    }
    match (greek > 0, latin > 0, cyr > 0) {
        (true, false, false) => Some(if poly { "greek_poly" } else { "greek_mono" }),
        (true, true, false) => Some("greek_latin_cs"), // genuine mid-line code-switch
        // owner G0-5 (2026-07-07): code-switch is a first-class phenomenon — own classes.
        // Entry into the TRAINING MIX is gated by the Opus-4.8 sample-health review (program D1).
        (true, false, true) => Some("greek_cyrillic_cs"),
        (false, true, true) => Some("cyrillic_latin_cs"),
        (false, true, false) => Some("latin"),
        (false, false, true) => Some("cyrillic"),
        (false, false, false) => None, // digits/punct only — furniture is synthesized, not mined
        (true, true, true) => Some("greek_latin_cs"), // tri-script: dominant pairing, accounted via class counts
    }
}

/// Ingest all *.jsonl under `dir` into a quality-gated pool. Dedup by NFD hash.
/// Pre-IPF pool caps (per-source fraction, per-doc lines) are applied HERE (lesson #4).
pub fn ingest(dir: &str, recipe: &Recipe, codec: &Codec) -> Result<(Vec<PoolLine>, IngestReport)> {
    let mut rep = IngestReport::default();
    let mut seen: std::collections::HashSet<u64> = Default::default();
    let mut pool: Vec<PoolLine> = Vec::new();
    let mut per_doc: HashMap<(String, String), usize> = HashMap::new();

    let mut files: Vec<_> = walkdir::WalkDir::new(dir)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.path().extension().is_some_and(|x| x == "jsonl"))
        .map(|e| e.path().to_owned())
        .collect();
    files.sort();
    anyhow::ensure!(!files.is_empty(), "no *.jsonl corpus files under {dir}");

    for f in files {
        let fh = std::fs::File::open(&f).with_context(|| format!("open {f:?}"))?;
        for line in std::io::BufReader::new(fh).lines() {
            let line = line?;
            if line.trim().is_empty() {
                continue;
            }
            rep.read += 1;
            let raw: RawLine = match serde_json::from_str(&line) {
                Ok(r) => r,
                Err(_) => {
                    reject(&mut rep, "bad_json", "unknown");
                    continue;
                }
            };
            let src = raw.text.trim();
            if src.chars().any(|c| c == '\u{FFFD}') {
                reject(&mut rep, "replacement_char", &raw.source_dataset);
                continue;
            }
            if src.chars().any(|c| c.is_control()) {
                reject(&mut rep, "control_char", &raw.source_dataset);
                continue;
            }
            let gt = Codec::normalize_gt(src);
            let n = gt.chars().count();
            if n < recipe.lengths.min_chars {
                reject(&mut rep, "too_short", &raw.source_dataset);
                continue;
            }
            if n > recipe.lengths.max_chars {
                reject(&mut rep, "too_long", &raw.source_dataset);
                continue;
            }
            let digits = gt.chars().filter(|c| c.is_ascii_digit()).count();
            if digits * 2 > n {
                reject(&mut rep, "digit_heavy", &raw.source_dataset);
                continue;
            }
            if codec.encode(&gt).is_none() {
                reject(&mut rep, "unmapped_codepoint", &raw.source_dataset);
                continue;
            }
            let ocr_derived = raw.provenance == "ocr";
            let Some(class) = classify(&gt, ocr_derived) else {
                let reason = if ocr_derived { "unclassifiable_or_homoglyph" } else { "mixed_scripts_unclassed" };
                reject(&mut rep, reason, &raw.source_dataset);
                continue;
            };
            let h = xxh3_64_with_seed(gt.as_bytes(), 1);
            if !seen.insert(h) {
                reject(&mut rep, "duplicate", &raw.source_dataset);
                continue;
            }
            // per-doc cap (pre-IPF)
            if recipe.pool_caps.per_doc_max_lines > 0 && !raw.source_doc_id.is_empty() {
                let k = (raw.source_dataset.clone(), raw.source_doc_id.clone());
                let c = per_doc.entry(k).or_default();
                if *c >= recipe.pool_caps.per_doc_max_lines {
                    *rep.pool_cap_trims.entry(raw.source_dataset.clone()).or_default() += 1;
                    continue;
                }
                *c += 1;
            }
            pool.push(PoolLine {
                split: split_of(&gt).into(),
                line_id: line_id_of(&gt),
                gt_nfd: gt,
                script_class: class.into(),
                source_dataset: raw.source_dataset,
                source_doc_id: raw.source_doc_id,
                license: raw.license,
            });
        }
    }

    // per-source fraction cap (pre-IPF): trim the largest sources down, deterministically.
    if recipe.pool_caps.per_source_max_fraction > 0.0 {
        let cap = (pool.len() as f64 * recipe.pool_caps.per_source_max_fraction).ceil() as usize;
        let mut by_src: HashMap<String, usize> = HashMap::new();
        let mut kept = Vec::with_capacity(pool.len());
        // stable order: sort by line_id so the trim is content-deterministic, not file-order.
        pool.sort_by(|a, b| a.line_id.cmp(&b.line_id));
        for l in pool {
            let c = by_src.entry(l.source_dataset.clone()).or_default();
            if *c >= cap {
                *rep.pool_cap_trims.entry(l.source_dataset.clone()).or_default() += 1;
                continue;
            }
            *c += 1;
            kept.push(l);
        }
        pool = kept;
    }

    for l in &pool {
        *rep.split_counts.entry(l.split.clone()).or_default() += 1;
        *rep.class_counts.entry(l.script_class.clone()).or_default() += 1;
    }
    rep.kept = pool.len();
    Ok((pool, rep))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn split_is_deterministic_and_banded() {
        let a = split_of("τὸ καλὸν κεῖται");
        assert_eq!(a, split_of("τὸ καλὸν κεῖται"));
        let mut res = 0;
        for i in 0..20000 {
            if split_of(&format!("γραμμή {i}")) == "reserved" {
                res += 1;
            }
        }
        // ~1.5% ± slack
        assert!((150..=450).contains(&res), "reserved band {res}/20000");
    }

    #[test]
    fn classify_classes() {
        assert_eq!(classify(&Codec::normalize_gt("καλημέρα σας"), true), Some("greek_mono"));
        assert_eq!(classify(&Codec::normalize_gt("τῆς ἁπλῆς"), true), Some("greek_poly"));
        assert_eq!(classify(&Codec::normalize_gt("βλ. Wilamowitz, Homerische Untersuchungen"), true), Some("greek_latin_cs"));
        assert_eq!(classify(&Codec::normalize_gt("Война и мир"), true), Some("cyrillic"));
        // OCR-derived: homoglyph word (latin a inside greek word) refused
        assert_eq!(classify(&Codec::normalize_gt("καλημέρa"), true), None);
        // BORN-DIGITAL: the same mixed word is trusted content -> code-switch class
        assert_eq!(classify(&Codec::normalize_gt("καλημέρa"), false), Some("greek_latin_cs"));
        assert_eq!(classify(&Codec::normalize_gt("το e-mail έφτασε"), false), Some("greek_latin_cs"));
        // G0-5: cross-script code-switch = own classes (born-digital)
        assert_eq!(classify(&Codec::normalize_gt("η μελέτη του Толстой για τον πόλεμο"), false), Some("greek_cyrillic_cs"));
        assert_eq!(classify(&Codec::normalize_gt("статья опубликована в journal of history"), false), Some("cyrillic_latin_cs"));
    }
}
