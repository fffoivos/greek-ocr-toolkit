//! Selection: pool -> render jobs matching the recipe's content marginals, severity mix, and
//! floors. Reuse is HARD-capped with no bypass; floors are met by supply or the build fails
//! loudly (docs/data_contracts.md §5.2).

use crate::codec::Codec;
use crate::corpus::{line_id_of, split_of, PoolLine};
use crate::recipe::Recipe;
use anyhow::{bail, Result};
use rand::seq::SliceRandom;
use rand::{Rng, SeedableRng};
use rand_chacha::ChaCha20Rng;
use serde::Serialize;
use std::collections::{BTreeMap, HashMap, HashSet};

#[derive(Clone, Serialize)]
pub struct Job {
    pub line: PoolLine,
    /// another line's NFC render form — the verso page text for show-through (None = self-ghost)
    pub verso_nfc: Option<String>,
    /// adjacent-line text for the segmentation-spill stratum (full-ink slice at a strip edge)
    pub neighbor_nfc: Option<String>,
    pub severity: u8,
    pub polarity_light: bool,
    pub bg_type: String,
    pub letterspaced: bool,
    pub reuse_index: u32,
    pub cs_synthetic: bool,
    /// minted into the letterpress ink-DEGRADATION cohort (`ink_transfer_v2` + historical-cut routing).
    /// A rendering regime, not a source property. Always false unless `recipe.ink_transfer.enabled`.
    #[serde(default)]
    pub letterpress: bool,
    /// minted into the LUNATE-sigma set (σ→ς in image+label, historical-cut routing) — an INDEPENDENT
    /// draw from `letterpress`, so lunate rows may be clean or degraded. False unless enabled.
    #[serde(default)]
    pub lunate: bool,
}

#[derive(Serialize, Default)]
pub struct SelectReport {
    pub target_total: usize,
    pub n_selected: usize,
    pub class_realized: BTreeMap<String, usize>,
    pub class_target: BTreeMap<String, usize>,
    pub class_shortfall: BTreeMap<String, usize>,
    pub cs_synthesized: usize,
    pub furniture_synthesized: usize,
    pub reuse_hist: BTreeMap<u32, usize>,
    pub max_reuse: u32,
    pub atom_deficits: BTreeMap<String, usize>,
    pub atom_floor: usize,
    pub long_line_fraction: f64,
    pub excluded_by_manifest: usize,
    pub reserved_rendered: usize,
}

fn weighted_pick<R: Rng>(rng: &mut R, w: &[(String, f64)]) -> String {
    let tot: f64 = w.iter().map(|(_, v)| v).sum();
    let mut x = rng.gen::<f64>() * tot;
    for (k, v) in w {
        x -= v;
        if x <= 0.0 {
            return k.clone();
        }
    }
    w.last().expect("nonempty weights").0.clone()
}

fn sev_pick<R: Rng>(rng: &mut R, w: &[f64; 4]) -> u8 {
    let tot: f64 = w.iter().sum();
    let mut x = rng.gen::<f64>() * tot;
    for (i, v) in w.iter().enumerate() {
        x -= v;
        if x <= 0.0 {
            return i as u8;
        }
    }
    3
}

/// Deterministic style draw for one job.
fn styled<R: Rng>(rng: &mut R, recipe: &Recipe, line: PoolLine, reuse_index: u32, cs: bool) -> Job {
    let bg = weighted_pick(
        rng,
        &[
            ("flat".into(), recipe.bg_weights.flat),
            ("gradient".into(), recipe.bg_weights.gradient),
            ("textured".into(), recipe.bg_weights.textured),
        ],
    );
    let greekish = line.script_class.starts_with("greek");
    Job {
        verso_nfc: None,
        neighbor_nfc: None,
        severity: sev_pick(rng, &recipe.severity_weights),
        polarity_light: rng.gen::<f64>() < recipe.polarity_light_fraction,
        bg_type: bg,
        letterspaced: greekish && rng.gen::<f64>() < recipe.letterspacing_fraction,
        // `&&` short-circuits: when the cohort is disabled (default) the rng is NOT drawn, so the
        // stream — and thus recipe_sha/shards — is byte-identical to a letterpress-less build.
        letterpress: recipe.ink_transfer.enabled
            && greekish
            && rng.gen::<f64>() < recipe.ink_transfer.cohort_fraction,
        // INDEPENDENT draw (separate rng) from `letterpress`: lunate ⊥ degradation. Gated `> 0.0` so a
        // 0 fraction draws nothing (keeps the degradation-cohort stream identical to a lunate-off build).
        lunate: recipe.ink_transfer.enabled
            && greekish
            && recipe.ink_transfer.lunate_sigma_fraction > 0.0
            && rng.gen::<f64>() < recipe.ink_transfer.lunate_sigma_fraction,
        reuse_index,
        cs_synthetic: cs,
        line,
    }
}

const GREEK_MONTHS_POLY: &[&str] = &[
    "Ἰανουαρίου", "Φεβρουαρίου", "Μαρτίου", "Ἀπριλίου", "Μαΐου", "Ἰουνίου", "Ἰουλίου",
    "Αὐγούστου", "Σεπτεμβρίου", "Ὀκτωβρίου", "Νοεμβρίου", "Δεκεμβρίου",
];
const GREEK_MONTHS_MONO: &[&str] = &[
    "Ιανουαρίου", "Φεβρουαρίου", "Μαρτίου", "Απριλίου", "Μαΐου", "Ιουνίου", "Ιουλίου",
    "Αυγούστου", "Σεπτεμβρίου", "Οκτωβρίου", "Νοεμβρίου", "Δεκεμβρίου",
];
// F3(b) (Fable S12): full Milesian numeral atoms so the recognizer sees the archaic letters.
// Units carry both 6-forms (ϛ stigma, ϝ digamma); tens carry 90 (ϙ koppa); hundreds carry 900
// (ϡ sampi). GT == rendered text (the string IS the label), so the alternate forms stay faithful.
const GREEK_DIGITS: &[&str] = &["α", "β", "γ", "δ", "ε", "ϛ", "ϝ", "ζ", "η", "θ"];
const GREEK_TENS: &[&str] = &["ι", "κ", "λ", "μ", "ν", "ξ", "ο", "π", "ϙ"];
const GREEK_HUNDREDS: &[&str] = &["ρ", "σ", "τ", "υ", "φ", "χ", "ψ", "ω", "ϡ"];

fn greek_numeral<R: Rng>(rng: &mut R) -> String {
    let mut s = String::new();
    if rng.gen_bool(0.25) {
        s.push('\u{0375}'); // ͵ lower numeral sign (thousands), e.g. dates ͵αϡξδ
        s.push_str(GREEK_DIGITS[rng.gen_range(0..GREEK_DIGITS.len())]);
    }
    if rng.gen_bool(0.5) {
        s.push_str(GREEK_HUNDREDS[rng.gen_range(0..GREEK_HUNDREDS.len())]);
    }
    if rng.gen_bool(0.6) {
        s.push_str(GREEK_TENS[rng.gen_range(0..GREEK_TENS.len())]);
    }
    s.push_str(GREEK_DIGITS[rng.gen_range(0..GREEK_DIGITS.len())]);
    s.push('\u{02B9}'); // ʹ keraia (upper numeral sign)
    if rng.gen_bool(0.15) {
        s = s.to_uppercase(); // capital Milesian forms (Ϝ Ϙ Ϡ) as in headings/titles
    }
    s
}

/// Page furniture: folios, page numbers, running heads, dateline/signature lines — the short-strip
/// strata real pages are full of and corpora lack.
fn synth_furniture<R: Rng>(rng: &mut R, words: &[String]) -> String {
    let pick = |rng: &mut R, n: usize| -> String {
        let mut v = Vec::new();
        for _ in 0..n {
            if let Some(w) = words.choose(rng) {
                v.push(w.clone());
            }
        }
        v.join(" ")
    };
    match rng.gen_range(0..6) {
        0 => format!("{}", rng.gen_range(3..950)),
        1 => format!("— {} —", rng.gen_range(3..950)),
        2 => greek_numeral(rng),
        3 => {
            let n = rng.gen_range(2..5);
            pick(rng, n).to_uppercase()
        }
        4 => {
            let poly = rng.gen_bool(0.5);
            let m = if poly { GREEK_MONTHS_POLY } else { GREEK_MONTHS_MONO };
            let city = if poly { "Ἐν Ἀθήναις" } else { "Αθήνα" };
            format!(
                "{city}, {} {} {}",
                rng.gen_range(1..29),
                m[rng.gen_range(0..12)],
                rng.gen_range(1860..2005)
            )
        }
        _ => format!("[ {} ]", rng.gen_range(3..950)),
    }
}

/// Insert a citation fragment mid-line at a word boundary (whitespace-separated — the
/// code-switch invariant; no mixed-script tokens).
fn synth_code_switch<R: Rng>(rng: &mut R, greek: &str, latin: &str) -> Option<String> {
    let gw: Vec<&str> = greek.split(' ').collect();
    let lw: Vec<&str> = latin.split(' ').collect();
    if gw.len() < 6 || lw.len() < 2 {
        return None;
    }
    let take = rng.gen_range(2..=lw.len().min(5));
    let start = rng.gen_range(0..=lw.len() - take);
    let frag = lw[start..start + take].join(" ");
    let at = rng.gen_range(2..gw.len() - 1);
    let mut out: Vec<&str> = Vec::with_capacity(gw.len() + take + 2);
    out.extend_from_slice(&gw[..at]);
    if rng.gen_bool(0.5) {
        out.push("(");
    }
    out.push(&frag);
    if out.contains(&"(") {
        out.push(")");
    }
    out.extend_from_slice(&gw[at..]);
    Some(out.join(" ").replace("( ", "(").replace(" )", ")"))
}

/// Jobs for the transfer-dev EVAL render (prereg_t1 §6a / review F1): every reserved-band pool line,
/// styled like a normal strip so the appearance distribution matches training — but the caller renders
/// them with the HELD-OUT fonts (invert `recipe.fonts.held_out`) to make the set font-OOD. Bypasses the
/// atom-floor selection entirely: this is a held-out eval set, not a training build. Deterministic
/// (sorted by line_id, fixed seed, capped) so the eval set is frozen.
pub fn reserved_jobs(pool: &[PoolLine], recipe: &Recipe, cap: usize) -> Vec<Job> {
    let mut rng = ChaCha20Rng::seed_from_u64(recipe.seed ^ 0x7A_9D_E7);
    let mut reserved: Vec<&PoolLine> = pool.iter().filter(|l| l.split == "reserved").collect();
    reserved.sort_by(|a, b| a.line_id.cmp(&b.line_id));
    reserved.shuffle(&mut rng);
    reserved
        .into_iter()
        .take(cap)
        .map(|l| styled(&mut rng, recipe, l.clone(), 0, false))
        .collect()
}

/// Exact class quotas, no replacement, reserved-text band only. A shortfall fails closed.
pub fn eval_jobs(pool: &[PoolLine], recipe: &Recipe) -> Result<Vec<Job>> {
    let eval = recipe.eval_only.as_ref().ok_or_else(|| anyhow::anyhow!("eval-only recipe required"))?;
    anyhow::ensure!(!recipe.crop.enabled && !recipe.ink_transfer.enabled && recipe.atom_floor == 0,
        "eval-only recipe requires clean crops, no ink transfer and atom_floor=0");
    anyhow::ensure!((0.0..=1.0).contains(&eval.max_font_share), "invalid eval font share");
    let excl = load_exclusions(&recipe.exclusion_manifests)?;
    let mut rng = ChaCha20Rng::seed_from_u64(recipe.seed);
    let mut jobs = Vec::new();
    let mut remaining = recipe.target_total;
    let positive: Vec<_> = recipe.content_marginals.iter().filter(|(_, f)| **f > 0.0).collect();
    for (i, (class, fraction)) in positive.iter().enumerate() {
        let n = if i + 1 == positive.len() { remaining } else { (recipe.target_total as f64 * **fraction).floor() as usize };
        remaining -= n;
        anyhow::ensure!(n >= *eval.minimum_class_counts.get(*class).unwrap_or(&0), "eval class quota below minimum: {class}");
        let mut candidates: Vec<_> = pool.iter().filter(|l| l.split == "reserved" && &l.script_class == *class && !excl.contains(&l.gt_nfd)).collect();
        candidates.sort_by(|a,b| a.line_id.cmp(&b.line_id));
        candidates.shuffle(&mut rng);
        anyhow::ensure!(candidates.len() >= n, "eval class supply shortfall: {class}: need {n}, have {}", candidates.len());
        jobs.extend(candidates.into_iter().take(n).map(|l| styled(&mut rng, recipe, l.clone(), 0, false)));
    }
    jobs.shuffle(&mut rng);
    Ok(jobs)
}

/// Load fail-closed exclusion manifests (S15a): a MISSING/unreadable path is an Err (never a silent
/// empty set), and each RAW line is normalized via `Codec::normalize_gt` so raw drafts match pool
/// `gt_nfd`. Extracted for the exclusion-machinery selftest (review_S15_recert F1 / ruling cond 3).
fn load_exclusions(manifests: &[String]) -> Result<HashSet<String>> {
    let mut excl = HashSet::new();
    for m in manifests {
        let s = std::fs::read_to_string(m)
            .map_err(|e| anyhow::anyhow!("exclusion manifest {m} unreadable (fail-closed): {e}"))?;
        for l in s.lines().filter(|l| !l.trim().is_empty()) {
            excl.insert(Codec::normalize_gt(l));
        }
    }
    Ok(excl)
}

/// verso/neighbor show-through bank eligibility (S15c review F5): a bank line must be train-split,
/// mid-length (20..100 chars), and NOT an excluded eval line — otherwise excluded eval text would
/// render as unlabeled ghost/spill ink in training strips, breaking the exclusion guarantee.
/// Extracted for the verso-bank exclusion selftest (review F8 nit).
fn verso_bank_eligible(l: &PoolLine, excl: &HashSet<String>) -> bool {
    l.split == "train" && (20..100).contains(&l.gt_nfd.chars().count()) && !excl.contains(&l.gt_nfd)
}

pub fn select(
    pool: &[PoolLine],
    recipe: &Recipe,
    codec: &Codec,
    allow_deficit: bool,
) -> Result<(Vec<Job>, SelectReport)> {
    let mut rng = ChaCha20Rng::seed_from_u64(recipe.seed);
    let mut rep = SelectReport { target_total: recipe.target_total, atom_floor: recipe.atom_floor, ..Default::default() };

    // fail-closed exclusions (load_exclusions: missing path -> Err; each RAW line -> normalize_gt)
    let excl = load_exclusions(&recipe.exclusion_manifests)?;

    let mut by_class: HashMap<&str, Vec<&PoolLine>> = HashMap::new();
    for l in pool {
        if l.split == "reserved" {
            continue; // reserved band is rendered separately, never mixed into train/val targets
        }
        if excl.contains(&l.gt_nfd) {
            rep.excluded_by_manifest += 1;
            continue;
        }
        by_class.entry(l.script_class.as_str()).or_default().push(l);
    }
    // Per-class rng (NOT the shared stream): HashMap iteration order is nondeterministic, and
    // consuming the shared rng in that order made whole builds nondeterministic (found by the
    // 2026-07-06 double-build byte-diff probe).
    {
        let mut classes: Vec<String> = by_class.keys().map(|k| k.to_string()).collect();
        classes.sort();
        for k in classes {
            if let Some(v) = by_class.get_mut(k.as_str()) {
                v.sort_by(|a, b| a.line_id.cmp(&b.line_id));
                let mut crng = ChaCha20Rng::seed_from_u64(
                    recipe.seed ^ xxhash_rust::xxh3::xxh3_64_with_seed(k.as_bytes(), 7),
                );
                v.shuffle(&mut crng);
            }
        }
    }

    let word_bank: Vec<String> = by_class
        .get("greek_mono")
        .into_iter()
        .chain(by_class.get("greek_poly"))
        .flatten()
        .take(3000)
        .flat_map(|l| l.gt_nfd.split(' ').map(|w| w.to_string()))
        .filter(|w| w.chars().count() >= 3 && w.chars().all(|c| !c.is_ascii_digit()))
        .take(20000)
        .collect();

    // F3 (Fable S12): atom-seeking. Rare atoms whose pool supply EXISTS but sits far below the floor
    // (archaic Greek numerals ϝ 60, Ϝ 9, ‡ 28 lines in 8.1M) are statistically never drawn by the
    // ~2%-per-class marginal shuffle. Move every line carrying an under-supplied atom to the FRONT of
    // its class so the marginal fill renders it first. Deterministic: rare set from the codec + pool,
    // stable cached sort (preserves the seeded shuffle order within each group).
    {
        let mut atom_pool: HashMap<char, usize> = HashMap::new();
        for v in by_class.values() {
            for l in v {
                for c in l.gt_nfd.chars() {
                    *atom_pool.entry(c).or_default() += 1;
                }
            }
        }
        let rare: HashSet<char> = codec
            .atoms
            .iter()
            .map(|a| a.ch)
            .filter(|c| {
                let n = *atom_pool.get(c).unwrap_or(&0);
                n > 0 && n < recipe.atom_floor
            })
            .collect();
        if !rare.is_empty() {
            eprintln!(
                "[select] atom-seek: {} under-supplied atoms moved to class fronts",
                rare.len()
            );
            for v in by_class.values_mut() {
                v.sort_by_cached_key(|l| !l.gt_nfd.chars().any(|c| rare.contains(&c)));
            }
        }
    }

    let mut jobs: Vec<Job> = Vec::with_capacity(recipe.target_total);
    let mut used: HashMap<String, u32> = HashMap::new(); // line_id -> renders
    let cap = recipe.reuse.max_per_line as u32;

    for (class, frac) in recipe.content_marginals.clone() {
        let want = (frac * recipe.target_total as f64).round() as usize;
        rep.class_target.insert(class.clone(), want);
        let mut got = 0usize;

        if class == "furniture" {
            for _ in 0..want {
                let text = synth_furniture(&mut rng, &word_bank);
                let gt = Codec::normalize_gt(&text);
                if gt.is_empty() || codec.encode(&gt).is_none() {
                    continue;
                }
                let line = PoolLine {
                    split: split_of(&gt).into(),
                    line_id: line_id_of(&gt),
                    gt_nfd: gt,
                    script_class: "furniture".into(),
                    source_dataset: "synth_furniture".into(),
                    source_doc_id: String::new(),
                    license: "generated".into(),
                };
                if line.split == "reserved" || excl.contains(&line.gt_nfd) {
                    continue;
                }
                jobs.push(styled(&mut rng, recipe, line, 0, false));
                got += 1;
                rep.furniture_synthesized += 1;
            }
            rep.class_realized.insert(class.clone(), got);
            if got < want {
                rep.class_shortfall.insert(class.clone(), want - got);
            }
            continue;
        }

        let src = by_class.get(class.as_str()).cloned().unwrap_or_default();
        // pass 1..=cap over the shuffled pool: reuse only begins after every distinct line was used.
        'outer: for pass in 0..cap {
            for l in &src {
                if got >= want {
                    break 'outer;
                }
                let u = used.entry(l.line_id.clone()).or_default();
                if *u != pass {
                    continue; // keeps reuse spread even: a line's k-th render happens in pass k
                }
                *u += 1;
                jobs.push(styled(&mut rng, recipe, (*l).clone(), pass, false));
                got += 1;
            }
        }

        // greek_latin_cs shortfall: synthesize genuine mid-line switches from greek x latin lines.
        if class == "greek_latin_cs" && got < want {
            let greeks: Vec<&PoolLine> = by_class
                .get("greek_mono")
                .into_iter()
                .chain(by_class.get("greek_poly"))
                .flatten()
                .copied()
                .collect();
            let latins = by_class.get("latin").cloned().unwrap_or_default();
            if !greeks.is_empty() && !latins.is_empty() {
                let mut tries = 0usize;
                while got < want && tries < want * 20 {
                    tries += 1;
                    let g = greeks[rng.gen_range(0..greeks.len())];
                    let l = latins[rng.gen_range(0..latins.len())];
                    let gu = used.entry(g.line_id.clone()).or_default();
                    if *gu >= cap {
                        continue; // the reuse cap binds synthesis too — no bypass
                    }
                    let Some(text) = synth_code_switch(&mut rng, &g.gt_nfd, &l.gt_nfd) else {
                        continue;
                    };
                    let gt = Codec::normalize_gt(&text);
                    if gt.chars().count() > recipe.lengths.max_chars || codec.encode(&gt).is_none() {
                        continue;
                    }
                    if crate::corpus::classify(&gt, false) != Some("greek_latin_cs") {
                        continue;
                    }
                    if excl.contains(&gt) {
                        continue;
                    }
                    *gu += 1;
                    let line = PoolLine {
                        split: g.split.clone(), // inherits the GREEK source line's split (leak-safe)
                        line_id: line_id_of(&gt),
                        gt_nfd: gt,
                        script_class: "greek_latin_cs".into(),
                        source_dataset: format!("cs:{}+{}", g.source_dataset, l.source_dataset),
                        source_doc_id: g.source_doc_id.clone(),
                        license: g.license.clone(),
                    };
                    jobs.push(styled(&mut rng, recipe, line, 0, true));
                    got += 1;
                    rep.cs_synthesized += 1;
                }
            }
        }

        rep.class_realized.insert(class.clone(), got);
        if got < want {
            rep.class_shortfall.insert(class.clone(), want - got);
        }
    }

    // reserved band: render each reserved pool line ONCE (frozen internal eval), capped at 2%.
    let res_cap = recipe.target_total / 50;
    let mut reserved: Vec<&PoolLine> = pool.iter().filter(|l| l.split == "reserved").collect();
    reserved.sort_by(|a, b| a.line_id.cmp(&b.line_id));
    reserved.shuffle(&mut rng);
    for l in reserved.into_iter().take(res_cap) {
        jobs.push(styled(&mut rng, recipe, l.clone(), 0, false));
        rep.reserved_rendered += 1;
    }

    // verso bank: real other-page text for show-through (train-split only — defense in depth).
    // S15c review F5: the bank must ALSO honor the exclusion manifest — otherwise excluded eval text
    // renders as unlabeled ghost/spill ink in ~300-550 training strips, breaking the exclusion guarantee.
    {
        let bank: Vec<String> = pool
            .iter()
            .filter(|l| verso_bank_eligible(l, &excl))
            .take(4000)
            .map(|l| Codec::render_form(&l.gt_nfd))
            .collect();
        if !bank.is_empty() {
            for j in jobs.iter_mut() {
                let own = Codec::render_form(&j.line.gt_nfd);
                let mut draw_other = |rng: &mut ChaCha20Rng| -> Option<String> {
                    for _ in 0..4 {
                        let cand = &bank[rng.gen_range(0..bank.len())];
                        if *cand != own {
                            return Some(cand.clone());
                        }
                    }
                    None // tiny pools only; better none than the same line (owner rule 2026-07-07)
                };
                if rng.gen_bool(0.6) {
                    j.verso_nfc = draw_other(&mut rng);
                }
                if rng.gen_bool(0.5) {
                    j.neighbor_nfc = draw_other(&mut rng);
                }
            }
        }
    }

    // ---- accounting + gates ----
    for j in &jobs {
        *rep.reuse_hist.entry(j.reuse_index).or_default() += 1;
        rep.max_reuse = rep.max_reuse.max(j.reuse_index + 1);
    }
    if rep.max_reuse > cap {
        bail!("reuse invariant broken: max {} > cap {cap}", rep.max_reuse); // must be impossible
    }
    let non_furniture: Vec<&Job> = jobs
        .iter()
        .filter(|j| j.line.script_class != "furniture" && j.line.split != "reserved")
        .collect();
    let long = non_furniture
        .iter()
        .filter(|j| j.line.gt_nfd.chars().count() >= recipe.lengths.long_chars)
        .count();
    rep.long_line_fraction = if non_furniture.is_empty() { 0.0 } else { long as f64 / non_furniture.len() as f64 };

    // atom floors on TRAIN rows: met by supply or fail loudly (never by reuse).
    let mut atom_counts: HashMap<char, usize> = HashMap::new();
    for j in &jobs {
        if j.line.split == "train" {
            for c in j.line.gt_nfd.chars() {
                *atom_counts.entry(c).or_default() += 1;
            }
        }
    }
    for a in &codec.atoms {
        let n = atom_counts.get(&a.ch).copied().unwrap_or(0);
        if n < recipe.atom_floor {
            rep.atom_deficits.insert(format!("{} {}", a.cp, a.ch), recipe.atom_floor - n);
        }
    }
    rep.n_selected = jobs.len();

    if !rep.class_shortfall.is_empty() || !rep.atom_deficits.is_empty() {
        let msg = format!(
            "supply gates: class_shortfall={:?} atom_deficits={} (floor {})",
            rep.class_shortfall,
            rep.atom_deficits.len(),
            recipe.atom_floor
        );
        if allow_deficit {
            eprintln!("[select] DEFICIT DISCLOSED (allow-deficit): {msg}");
        } else {
            bail!("{msg}\nFloors are met by SUPPLY, not reuse: add sources or pass --allow-deficit to build disclosed.");
        }
    }
    Ok((jobs, rep))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;

    #[test]
    fn exclusion_manifest_fail_closed_on_missing_path() {
        // S15a ruling cond 3(ii): a missing/unreadable manifest is an Err, never a silent empty set.
        assert!(
            load_exclusions(&["/no/such/exclusion_manifest_xyz.txt".to_string()]).is_err(),
            "missing exclusion manifest must fail-closed (Err)"
        );
    }

    #[test]
    fn exclusion_manifest_normalizes_raw_lines() {
        // S15a ruling cond 3(i): a RAW manifest line is normalize_gt'd, so it matches a pool gt_nfd
        // even when the raw form carries a G0-3 confusable (lunate sigma ϲ U+03F2 -> σ). A pool line
        // whose gt_nfd equals this is then dropped at select.rs (excl.contains(&l.gt_nfd)).
        let path = std::env::temp_dir().join(format!("s15a_excl_test_{}.txt", std::process::id()));
        {
            let mut f = std::fs::File::create(&path).unwrap();
            writeln!(f, "\u{03F2}\u{03C5}\u{03BD}\u{03B5}\u{03C3}\u{03B9}\u{03C2}").unwrap(); // ϲυνεσιϲ (raw)
            writeln!(f).unwrap(); // blank line -> ignored
        }
        let excl = load_exclusions(&[path.to_str().unwrap().to_string()]).unwrap();
        std::fs::remove_file(&path).ok();
        let pool_gt = Codec::normalize_gt("\u{03F2}\u{03C5}\u{03BD}\u{03B5}\u{03C3}\u{03B9}\u{03C2}");
        assert!(excl.contains(&pool_gt), "normalized raw manifest line must match pool gt_nfd: {excl:?}");
        assert_eq!(excl.len(), 1, "blank manifest lines must be ignored");
    }

    #[test]
    fn verso_bank_honors_exclusion_and_split() {
        // S15c review F5 / F8: the show-through bank must reject (a) excluded eval lines, (b) non-train
        // splits, and (c) too-short/too-long lines — else excluded text ghosts into training strips.
        let mk = |gt: &str, split: &str| PoolLine {
            gt_nfd: gt.to_string(),
            script_class: "greek_mono".into(),
            split: split.into(),
            line_id: "x".into(),
            source_dataset: "t".into(),
            source_doc_id: "d".into(),
            license: "l".into(),
        };
        let mut excl = HashSet::new();
        let excluded = "ΤΟ ΕΞΑΙΡΟΥΜΕΝΟ ΚΕΙΜΕΝΟ ΑΞΙΟΛΟΓΗΣΗΣ"; // 34 chars, train-split, but excluded
        excl.insert(excluded.to_string());
        assert!(!verso_bank_eligible(&mk(excluded, "train"), &excl), "excluded eval line must not bank");
        let clean = "ΕΝΑ ΚΑΘΑΡΟ ΚΕΙΜΕΝΟ ΓΙΑ ΤΗΝ ΤΡΑΠΕΖΑ"; // 34 chars, train, not excluded
        assert!(verso_bank_eligible(&mk(clean, "train"), &excl), "clean mid-length train line banks");
        assert!(!verso_bank_eligible(&mk(clean, "reserved"), &excl), "reserved split must not bank");
        assert!(!verso_bank_eligible(&mk(clean, "val"), &excl), "val split must not bank");
        assert!(!verso_bank_eligible(&mk("σύντομο", "train"), &excl), "too-short (<20) must not bank");
    }
}
