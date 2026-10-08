//! Page composer v1 — synthetic pages with FREE ground truth (line boxes, block classes,
//! reading order) to train the D-P1 line-first parser (detector + block feature classifier).
//!
//! REFERENCES
//! - Design: docs/layout_data_plan.md + docs/architecture/05 (grammars, page-vs-strip split);
//!   real-page deltas: docs/page_parsing_decision.md §3 (2026-07-07 review of owned documents).
//! - Ink is pasted as ALPHA onto one page canvas (no per-strip backgrounds → no seams); page-level
//!   photometrics run on the whole page. Strip-level ink damage reuses distort::ink_ops.
//! - v1 grammars: `book19c` (folio, body, footnote block, drop-cap, verse), `twocol` (center
//!   rule), `tablepage`, `plate`.
//! - S9 grammars (detector path, docs/execution_plan_d0d1.md S9): `apparatus` (critical-edition
//!   band + line-number marginalia), `toc` (leader dots + page numbers), `bibliography` (hanging
//!   indent), `list` (markers + hanging indent), `title` (title page), `dateline` (letterspaced
//!   dateline_signature), `handwriting` (procedural strokes as figure-class). New block classes
//!   toc_entry/list_item/bibliography_entry are composer/taxonomy.json proposed_additions
//!   (OWNER-RATIFICATION-PENDING) — fold into the active class list on ratification.
//! - S9 page infra: per-page LANGUAGE COHERENCE (one source stream per page, pool_streams);
//!   page split bands (page_split, 94/4.5/1.5); layout-diversity sampler (Layout); rayon over
//!   pages; run-level page audit (page_audit.json: grammar/class marginals, splits, contrast).
//! - GT: axis-aligned boxes v1 (page rotation deferred — noted in docs). Blocks carry taxonomy
//!   classes (composer/taxonomy.json draft); reading order = grammar order.

use crate::codec::Codec;
use crate::distort;
use crate::recipe::Recipe;
use crate::render::{render_cap, render_ink, FontEntry, FontPool, STRIP_H};
use anyhow::{Context, Result};
use rand::{Rng, SeedableRng};
use rand_chacha::ChaCha20Rng;
use rayon::prelude::*;
use serde::Serialize;
use std::collections::BTreeMap;
use xxhash_rust::xxh3::xxh3_64_with_seed;

/// page-level split salt (independent of the strip salt so page IDs and line IDs never collide in
/// the never-trainable band). 94/4.5/1.5 train/val/reserved, page-seed-hashed (S9 plan f).
pub const PAGE_SPLIT_SALT: &str = "greek-page-ocr/pages/v1";
const STREAM_SALT: u64 = 0x9E37_79B9_7F4A_7C15;

/// hash a page seed into a train/val/reserved band (matches corpus::split_of thresholds).
pub fn page_split(seed: u64) -> &'static str {
    let s = xxh3_64_with_seed(PAGE_SPLIT_SALT.as_bytes(), 0);
    let b = xxh3_64_with_seed(&seed.to_le_bytes(), s) % 1000;
    if b >= 985 {
        "reserved"
    } else if b >= 940 {
        "val"
    } else {
        "train"
    }
}

/// grammar sampling weights (S9 plan f: "class marginals vs grammar weights"). The page composer
/// samples a grammar per page by these weights; the page audit compares realized frequencies back.
/// Weighted so the rare-but-needed classes (apparatus, dateline_signature, toc/bibliography/list)
/// each reach a per-class floor for their block heads (docs/architecture/05 §5.4).
pub const GRAMMARS: &[(&str, f64)] = &[
    ("book19c", 0.40),
    ("twocol", 0.24),
    ("tablepage", 0.20),
    ("plate", 0.16),
    ("apparatus", 0.14),
    ("toc", 0.10),
    ("bibliography", 0.10),
    ("list", 0.09),
    ("title", 0.06),
    ("dateline", 0.08),
    ("handwriting", 0.06),
    // Phase-3 detector-retrain grammars (docs/reviews/guide_W3_fable.md §2.2): the two
    // under-represented regimes the detector fails on. `dense_letterpress` = the JOINT cell
    // (dense × tight-leading × justified-ish × polytonic × letterpress) that over-fragments; heavily
    // weighted because closing that cell is the retrain's headline goal. `web_digital` = born-digital
    // ragged-right flowed web text (the Wikipedia/OOD regime).
    ("dense_letterpress", 0.18),
    ("web_digital", 0.12),
];

/// Grammars whose furniture is HARDCODED Greek (ΠΕΡΙΕΧΟΜΕΝΑ/ΒΙΒΛΙΟΓΡΑΦΙΑ headings, Ἐν Ἀθήναις
/// datelines + Greek months, ΥΠΟ/ΕΝ ΑΘΗΝΑΙΣ imprints, Greek-numeral list markers, critical-apparatus
/// sigla) — they belong only on Greek-script streams (S9 plan c: per-page language coherence).
pub const GREEK_ONLY_GRAMMARS: &[&str] = &["apparatus", "toc", "bibliography", "list", "title", "dateline"];
/// Language-neutral grammars: their body text is the stream's own script and any Greek bits are
/// gated on `greek_stream` inside `compose_page`. Non-Greek streams draw ONLY from this set.
/// `dense_letterpress` + `web_digital` are neutral: their furniture (running head, folio, footnote
/// markers "1.", web heading) is the stream's OWN script, never hardcoded Greek — so a Latin stream
/// gets a dense Latin letterpress / Latin web page, keeping per-page language coherence.
pub const NEUTRAL_GRAMMARS: &[&str] =
    &["book19c", "twocol", "tablepage", "plate", "handwriting", "dense_letterpress", "web_digital"];

/// Period letterpress serif faces PREFERRED for `dense_letterpress` (worn 19c book type). Matched by
/// stem prefix; a stream whose script none of these cover falls back to any eligible font. Mirrors
/// guide_W3 §2.2 ("GFS Didot / GFSDidot_Classic / Bodoni / Artemisia / Old Standard").
const LETTERPRESS_FONTS: &[&str] = &[
    "GFSDidot", "GFSBodoni", "GFSArtemisia", "OldStandard", "TheanoDidot", "EBGaramond", "GentiumPlus", "Gentium",
];
/// Sans faces PREFERRED for `web_digital` (born-digital UI/body text). Same prefix-match + fallback.
const WEB_FONTS: &[&str] = &[
    "DejaVuSans", "NotoSans", "FiraSans", "OpenSans", "SourceSans", "Roboto", "IBMPlexSans", "AlegreyaSans",
    "LibertinusSans",
];

/// Route a picked grammar to be language-coherent with the page's stream. A non-Greek stream that
/// draws a Greek-only grammar is deterministically re-picked from the neutral grammars (weighted by
/// their GRAMMARS weights) so its page never mixes Greek furniture over a non-Greek body. Greek
/// streams and already-neutral grammars pass through unchanged.
fn resolve_grammar(g: &'static str, lang: &str, seed: u64) -> &'static str {
    if lang.starts_with("greek") || !GREEK_ONLY_GRAMMARS.contains(&g) {
        return g;
    }
    let neutral: Vec<(&'static str, f64)> = GRAMMARS
        .iter()
        .copied()
        .filter(|(name, _)| NEUTRAL_GRAMMARS.contains(name))
        .collect();
    let tot: f64 = neutral.iter().map(|(_, w)| w).sum();
    let h = (xxh3_64_with_seed(b"grammar-neutral", seed) % 1_000_000) as f64 / 1_000_000.0;
    let mut x = h * tot;
    for (name, w) in &neutral {
        x -= w;
        if x <= 0.0 {
            return name;
        }
    }
    neutral[0].0
}

/// weighted grammar pick from a page seed (deterministic).
fn pick_grammar(seed: u64) -> &'static str {
    let tot: f64 = GRAMMARS.iter().map(|(_, w)| w).sum();
    let h = (xxh3_64_with_seed(b"grammar", seed) % 1_000_000) as f64 / 1_000_000.0;
    let mut x = h * tot;
    for (g, w) in GRAMMARS {
        x -= w;
        if x <= 0.0 {
            return g;
        }
    }
    GRAMMARS[0].0
}

/// A per-page COHERENT text stream: one `source_dataset` (=> one language/register), so every line
/// on a composed page comes from the same stream (S9 plan c: per-page language coherence). No page
/// mixes Greek-book prose with Latin citations or Cyrillic across its blocks.
pub struct Stream {
    pub key: String,  // source_dataset
    pub lang: String, // dominant script_class of the source
    pub texts: Vec<String>,
}

#[derive(Serialize)]
pub struct LineGT {
    pub block: usize,
    pub bbox: [i32; 4],
    pub text: String,
}

#[derive(Serialize)]
pub struct BlockGT {
    pub id: usize,
    pub class: String,
    pub bbox: [i32; 4],
    pub order: usize,
}

#[derive(Serialize)]
pub struct PageGT {
    pub grammar: String,
    /// never-trainable band assignment for this page (train|val|reserved), page-seed-hashed.
    pub split: String,
    /// coherent source_dataset + dominant script_class of the single stream this page drew from.
    pub source: String,
    pub lang: String,
    pub width: usize,
    pub height: usize,
    pub severity: u8,
    pub page_ops: Vec<String>,
    pub blocks: Vec<BlockGT>,
    pub lines: Vec<LineGT>,
}

/// ink bbox of a rendered `h`×`w` canvas (rows/cols with alpha above threshold)
fn ink_bbox(ink: &[f32], w: usize, h: usize) -> Option<(usize, usize, usize, usize)> {
    let (mut x0, mut y0, mut x1, mut y1) = (usize::MAX, usize::MAX, 0usize, 0usize);
    for y in 0..h {
        for x in 0..w {
            if ink[y * w + x] > 0.05 {
                x0 = x0.min(x);
                y0 = y0.min(y);
                x1 = x1.max(x);
                y1 = y1.max(y);
            }
        }
    }
    if x0 == usize::MAX {
        None
    } else {
        Some((x0, y0, x1 + 1, y1 + 1))
    }
}

struct Placed {
    text: String,
    bbox: [i32; 4],
}

/// Render a pool line to fit slot_w (word-trimming to fit), paste its ink at (x, y_top of the
/// 48px canvas), return GT. Light ink damage applied per strip.
#[allow(clippy::too_many_arguments)]
fn place_line(
    page: &mut [f32],
    pw: usize,
    ph: usize,
    font: &FontEntry,
    texts: &[String],
    rng: &mut ChaCha20Rng,
    x: i32,
    y: i32,
    slot_w: usize,
    ink_h: f32,
    ink_level: f32,
    align: u8, // 0 left, 1 center, 2 right
) -> Option<Placed> {
    place_line_t(page, pw, ph, font, texts, rng, x, y, slot_w, ink_h, ink_level, align, 0.0)
}

/// as `place_line` but with letterspacing (tracking, em) — for gesperrt datelines/signatures.
#[allow(clippy::too_many_arguments)]
fn place_line_t(
    page: &mut [f32],
    pw: usize,
    ph: usize,
    font: &FontEntry,
    texts: &[String],
    rng: &mut ChaCha20Rng,
    x: i32,
    y: i32,
    slot_w: usize,
    ink_h: f32,
    ink_level: f32,
    align: u8, // 0 left, 1 center, 2 right
    track_em: f32,
) -> Option<Placed> {
    for _try in 0..8 {
        let mut t = texts[rng.gen_range(0..texts.len())].clone();
        for _trim in 0..6 {
            let Ok(r) = render_ink(font, &t, track_em, ink_h, 0.0, "", false) else { break };
            if r.w <= slot_w {
                let mut ink = r.ink.clone();
                let mut ap = Vec::new();
                let sev = rng.gen_range(1..=2);
                distort::ink_ops(rng, &mut ink, r.w, STRIP_H, sev, &mut ap, false, None, None, false);
                let (bx0, by0, bx1, by1) = ink_bbox(&ink, r.w, STRIP_H)?;
                let x_off = match align {
                    1 => x + ((slot_w - r.w) / 2) as i32,
                    2 => x + (slot_w - r.w) as i32,
                    _ => x,
                };
                for yy in 0..STRIP_H {
                    let py = y + yy as i32;
                    if py < 0 || py >= ph as i32 {
                        continue;
                    }
                    for xx in 0..r.w {
                        let px = x_off + xx as i32;
                        if px < 0 || px >= pw as i32 {
                            continue;
                        }
                        let a = ink[yy * r.w + xx];
                        if a > 0.003 {
                            let p = &mut page[py as usize * pw + px as usize];
                            *p = *p * (1.0 - a) + ink_level * a;
                        }
                    }
                }
                return Some(Placed {
                    text: t,
                    bbox: [
                        x_off + bx0 as i32,
                        y + by0 as i32,
                        x_off + bx1 as i32,
                        y + by1 as i32,
                    ],
                });
            }
            // too wide: trim trailing words
            let words: Vec<&str> = t.split(' ').collect();
            if words.len() <= 3 {
                break;
            }
            t = words[..words.len() - 2].join(" ");
        }
    }
    None
}

fn hrule(page: &mut [f32], pw: usize, x0: i32, x1: i32, y: i32, ink: f32) {
    for x in x0.max(0)..x1.min(pw as i32) {
        page[y as usize * pw + x as usize] = ink;
        page[(y as usize + 1) * pw + x as usize] = ink;
    }
}

fn union(boxes: &[[i32; 4]]) -> [i32; 4] {
    let mut u = boxes[0];
    for b in boxes {
        u[0] = u[0].min(b[0]);
        u[1] = u[1].min(b[1]);
        u[2] = u[2].max(b[2]);
        u[3] = u[3].max(b[3]);
    }
    u
}

/// compose-stage page tone (uneven paper) — everything else comes from the SAME distortion
/// registry as the strips (owner directive 2026-07-07: line-level distortions apply at page
/// level too), via image_ops(Photo, page height) + verso_bleed + finalize(jpeg).
fn page_tone(rng: &mut ChaCha20Rng, page: &mut [f32], w: usize, h: usize) {
    // low-frequency tone field
    let cell = 160usize;
    let gw = w / cell + 2;
    let gh = h / cell + 2;
    let amp = rng.gen_range(0.02f32..0.05);
    let grid: Vec<f32> = (0..gw * gh).map(|_| rng.gen_range(-amp..amp)).collect();
    for y in 0..h {
        for x in 0..w {
            let (fy, fx) = (y as f32 / cell as f32, x as f32 / cell as f32);
            let (y0, x0) = (fy as usize, fx as usize);
            let (ty, tx) = (fy - y0 as f32, fx - x0 as f32);
            let g = |yy: usize, xx: usize| grid[yy.min(gh - 1) * gw + xx.min(gw - 1)];
            let v = g(y0, x0) * (1.0 - tx) * (1.0 - ty)
                + g(y0, x0 + 1) * tx * (1.0 - ty)
                + g(y0 + 1, x0) * (1.0 - tx) * ty
                + g(y0 + 1, x0 + 1) * tx * ty;
            page[y * w + x] = (page[y * w + x] + v).clamp(0.0, 1.0);
        }
    }
}

fn digit_cell<R: Rng>(rng: &mut R) -> String {
    // 1890s ledger style: comma groups, optional decimals, or an em-dash/void
    match rng.gen_range(0..8) {
        0 => "—".into(),
        1 => format!("{}", rng.gen_range(1..100)),
        2..=4 => format!("{},{:03}", rng.gen_range(1..40), rng.gen_range(0..1000)),
        _ => format!("{},{:03} {:02}", rng.gen_range(1..10), rng.gen_range(0..1000), rng.gen_range(0..100)),
    }
}

fn vrule(page: &mut [f32], pw: usize, x: i32, y0: i32, y1: i32, ink: f32) {
    for y in y0.max(0)..y1.min((page.len() / pw) as i32) {
        page[y as usize * pw + x as usize] = ink;
    }
}

/// procedural plate: framed rectangle with soft interior texture (a photo/engraving stand-in)
fn draw_plate(rng: &mut ChaCha20Rng, page: &mut [f32], pw: usize, x0: i32, y0: i32, w: i32, h: i32, ink: f32) {
    for t in 0..3 {
        for x in x0..(x0 + w) {
            page[(y0 + t) as usize * pw + x as usize] = ink;
            page[(y0 + h - 1 - t) as usize * pw + x as usize] = ink;
        }
        for y in y0..(y0 + h) {
            page[y as usize * pw + (x0 + t) as usize] = ink;
            page[y as usize * pw + (x0 + w - 1 - t) as usize] = ink;
        }
    }
    for y in (y0 + 6)..(y0 + h - 6) {
        for x in (x0 + 6)..(x0 + w - 6) {
            let v = 0.45 + 0.25 * ((x as f32 * 0.05).sin() * (y as f32 * 0.04).cos()) + rng.gen_range(-0.08..0.08);
            let p = &mut page[y as usize * pw + x as usize];
            *p = (*p * 0.25 + v * 0.75).clamp(0.0, 1.0);
        }
    }
}

/// Per-page layout parameters, sampled per grammar (S9 plan d: explicit layout-diversity
/// randomization — margins/leading/size). Grammars that want tighter control still sample inline;
/// the new grammars route their geometry through here so diversity is auditable.
///
/// COLUMNS: the S9 grammars (apparatus/toc/bibliography/list/title/dateline/handwriting) are all
/// INTENTIONALLY single-column — a multi-column axis lives only in the pre-existing `twocol`
/// grammar (its own inline geometry), so `Layout` carries no `cols` field. If a future grammar
/// needs a multi-column body, add the axis here and wire it in that grammar's arm.
struct Layout {
    mx: i32,      // horizontal margin (px)
    top: i32,     // first content y
    ink_h: f32,   // body ink height (type size proxy)
    leading: f32, // line pitch = ink_h * leading
}

impl Layout {
    fn sample(rng: &mut ChaCha20Rng, grammar: &str, pw: usize) -> Layout {
        let (mxf, ink_h, leading) = match grammar {
            "toc" => (rng.gen_range(0.12f32..0.18), rng.gen_range(24.0f32..30.0), rng.gen_range(1.7f32..2.2)),
            "bibliography" => (rng.gen_range(0.11f32..0.16), rng.gen_range(22.0f32..28.0), rng.gen_range(1.5f32..1.8)),
            "list" => (rng.gen_range(0.12f32..0.18), rng.gen_range(24.0f32..30.0), rng.gen_range(1.6f32..2.0)),
            "title" => (rng.gen_range(0.14f32..0.20), rng.gen_range(30.0f32..40.0), rng.gen_range(2.0f32..2.6)),
            "apparatus" => (rng.gen_range(0.13f32..0.18), rng.gen_range(26.0f32..32.0), rng.gen_range(1.7f32..2.1)),
            "dateline" => (rng.gen_range(0.13f32..0.19), rng.gen_range(26.0f32..32.0), rng.gen_range(1.7f32..2.1)),
            "handwriting" => (rng.gen_range(0.12f32..0.17), rng.gen_range(26.0f32..32.0), rng.gen_range(1.7f32..2.1)),
            _ => (rng.gen_range(0.12f32..0.17), rng.gen_range(28.0f32..34.0), rng.gen_range(1.55f32..1.85)),
        };
        Layout {
            mx: (pw as f32 * mxf) as i32,
            top: rng.gen_range(110..175),
            ink_h,
            leading,
        }
    }
}

/// Pick ONE body font that covers a representative sample of THIS stream (language coherence: the
/// whole page renders in one script's font). Falls back to a Greek-capable font, then font 0.
fn pick_stream_font(rng: &mut ChaCha20Rng, texts: &[String], fonts: &FontPool) -> usize {
    // try a handful of sampled lines; the first with >=1 eligible font wins (that font covers the
    // stream's script). Sampling several lines tolerates the odd unusual glyph.
    for _ in 0..12 {
        let t = &texts[rng.gen_range(0..texts.len())];
        let elig = fonts.eligible(t);
        if !elig.is_empty() {
            return elig[rng.gen_range(0..elig.len())];
        }
    }
    let greek_ok = fonts.eligible("Θὰ τελειώσω τὰς ἁπλᾶς γραμμάς");
    if !greek_ok.is_empty() {
        return greek_ok[rng.gen_range(0..greek_ok.len())];
    }
    0
}

/// Like `pick_stream_font` but biased to a PREFERRED face set (matched by stem prefix), so the new
/// Phase-3 grammars render in the right typographic family — period serif for dense_letterpress,
/// sans for web_digital. A preferred face is used only if it also COVERS the stream's script (cmap
/// gate); if none of the preferred faces cover the stream, falls back to the general stream pick so
/// coverage/language-coherence is never sacrificed for style.
fn pick_stream_font_pref(rng: &mut ChaCha20Rng, texts: &[String], fonts: &FontPool, prefer: &[&str]) -> usize {
    let is_pref = |i: usize| prefer.iter().any(|p| fonts.fonts[i].stem.starts_with(p));
    for _ in 0..16 {
        let t = &texts[rng.gen_range(0..texts.len())];
        let hit: Vec<usize> = fonts.eligible(t).into_iter().filter(|&i| is_pref(i)).collect();
        if !hit.is_empty() {
            return hit[rng.gen_range(0..hit.len())];
        }
    }
    pick_stream_font(rng, texts, fonts)
}

/// Drop-cap convention (S9 plan b): the initial cap is a FIGURE-like box (own block, class
/// `figure`), and the first text line EXCLUDES it (the line GT text is placed to the right and does
/// not contain the cap glyph). Returns (cap figure box, x where the adjoining text should start).
///
/// The returned figure box is the TIGHT ink bbox of the rendered cap — no reserved-region
/// inflation. The cap is rasterized by `render_cap` at a MULTI-LINE height (`cap_h`, sized to
/// ~2-3 body lines) on a tall tight canvas — NOT the 48px line strip — so it teaches the true
/// multi-line drop-cap pattern (S9 Fable-5 MINOR). The box tracks the real ink so the GT never
/// claims figure ink beyond the glyph; the caller sizes the adjoining text indent from THIS box
/// height so the indent matches the rendered cap.
///
/// `initials` are candidate cap glyphs (derived from the page's own stream so the initial is
/// language-coherent — first letter of a sampled body line, uppercased); the first one the font
/// can render is used, so a font missing a given glyph falls back to the next candidate.
fn place_dropcap(
    page: &mut [f32],
    pw: usize,
    ph: usize,
    font: &FontEntry,
    initials: &[String],
    x: i32,
    y: i32,
    cap_h: f32,
    ink_level: f32,
) -> Option<([i32; 4], i32)> {
    for c in initials {
        let Ok((ink, cw, ch)) = render_cap(font, c, cap_h) else { continue };
        let Some((bx0, by0, bx1, by1)) = ink_bbox(&ink, cw, ch) else { continue };
        for yy in 0..ch {
            let py = y + yy as i32;
            if py < 0 || py >= ph as i32 {
                continue;
            }
            for xx in 0..cw {
                let px = x + xx as i32;
                if px < 0 || px >= pw as i32 {
                    continue;
                }
                let a = ink[yy * cw + xx];
                if a > 0.003 {
                    let p = &mut page[py as usize * pw + px as usize];
                    *p = *p * (1.0 - a) + ink_level * a;
                }
            }
        }
        let box_ = [x + bx0 as i32, y + by0 as i32, x + bx1 as i32, y + by1 as i32];
        return Some((box_, x + bx1 as i32 + 10));
    }
    None
}

/// Procedural HANDWRITING noise: wavy cursive-like polylines with pen lifts and the odd
/// ascender/descender, filling a box. Carries no text GT (handwriting is annotated as a
/// `figure`-class box, S9 plan a) — the recognizer is never asked to read it.
#[allow(clippy::too_many_arguments)]
fn draw_scribble(rng: &mut ChaCha20Rng, page: &mut [f32], pw: usize, ph: usize, x0: i32, y0: i32, w: i32, h: i32, ink: f32) {
    let n_lines = (h / 26).max(1);
    for li in 0..n_lines {
        let base_y = y0 + 14 + li * 26;
        let mut x = x0 + rng.gen_range(0..12);
        let end = x0 + w - rng.gen_range(4..24);
        let mut phase = rng.gen_range(0.0f32..6.28);
        while x < end {
            let seg = rng.gen_range(6..24);
            for dx in 0..seg {
                let xx = x + dx;
                if xx < 0 || xx >= pw as i32 {
                    continue;
                }
                let amp = rng.gen_range(3.0f32..8.0);
                let yy = base_y + (amp * (xx as f32 * 0.15 + phase).sin()) as i32 + rng.gen_range(-1..2);
                for t in 0..rng.gen_range(1..3) {
                    let py = yy + t;
                    if py >= 0 && py < ph as i32 {
                        page[py as usize * pw + xx as usize] = ink;
                    }
                }
                if rng.gen_bool(0.04) {
                    let dir = if rng.gen_bool(0.5) { -1 } else { 1 };
                    for k in 0..rng.gen_range(4..12) {
                        let py = yy + dir * k;
                        if py >= 0 && py < ph as i32 {
                            page[py as usize * pw + xx as usize] = ink;
                        }
                    }
                }
            }
            x += seg + rng.gen_range(2..10);
            phase += rng.gen_range(0.2f32..0.8);
        }
    }
}

pub fn compose_page(
    grammar: &str,
    seed: u64,
    stream: &Stream,
    fonts: &FontPool,
    ctx: &distort::OpCtx,
    severity_weights: &[f64; 4],
) -> Result<(image::GrayImage, PageGT)> {
    let mut rng = ChaCha20Rng::seed_from_u64(seed);
    let texts: &[String] = &stream.texts;
    anyhow::ensure!(!texts.is_empty(), "empty stream {}", stream.key);
    // Greek-script stream? Hardcoded Greek furniture (chapter headings, drop-cap initials) is only
    // emitted for Greek streams; a non-Greek stream keeps its own script (S9 plan c: per-page
    // language coherence). Compose_run additionally routes non-Greek streams away from the
    // Greek-only grammars, but the language-neutral grammars still gate their Greek bits here.
    let greek_stream = stream.lang.starts_with("greek");
    let (pw, ph) = (1100usize, 1600usize);
    // web_digital is a born-digital regime: crisp near-black text on a near-white page (no toned
    // paper). Every other grammar keeps the toned-paper book range.
    let web = grammar == "web_digital";
    let bg = if web { rng.gen_range(0.965f32..1.0) } else { rng.gen_range(0.86f32..0.94) };
    let ink_level = if web { rng.gen_range(0.02f32..0.09) } else { rng.gen_range(0.06f32..0.18) };
    let mut page = vec![bg; pw * ph];
    // one body font per page (book convention), coherent with the page's single text stream. The
    // Phase-3 grammars bias the pick to their typographic family (period serif / sans) but never
    // break the cmap coverage gate (pick_stream_font_pref falls back to any eligible face).
    let font_idx = match grammar {
        "dense_letterpress" => pick_stream_font_pref(&mut rng, texts, fonts, LETTERPRESS_FONTS),
        "web_digital" => pick_stream_font_pref(&mut rng, texts, fonts, WEB_FONTS),
        _ => pick_stream_font(&mut rng, texts, fonts),
    };
    let font = &fonts.fonts[font_idx];

    let mut blocks: Vec<BlockGT> = Vec::new();
    let mut lines: Vec<LineGT> = Vec::new();
    let mut add_block = |class: &str, boxes: &[[i32; 4]], order: usize, blocks: &mut Vec<BlockGT>| -> usize {
        let id = blocks.len();
        blocks.push(BlockGT { id, class: class.into(), bbox: union(boxes), order });
        id
    };

    match grammar {
        "book19c" => {
            let mx = (pw as f32 * rng.gen_range(0.13..0.17)) as i32;
            let body_w = pw as i32 - 2 * mx;
            let chapter_open = rng.gen_bool(0.25);
            // running head: text + page number (or plain folio); bottom-folio variant
            let bottom_folio = rng.gen_bool(0.3);
            if !bottom_folio {
                let mut hb: Vec<[i32; 4]> = Vec::new();
                let mut hl: Vec<(String, [i32; 4])> = Vec::new();
                if rng.gen_bool(0.55) && !chapter_open {
                    // ΤΙΤΛΟΣ-style uppercase running head centered + number outer
                    let head: String = {
                        let mut wds: Vec<String> = Vec::new();
                        for _ in 0..rng.gen_range(1..3) {
                            wds.push(texts[rng.gen_range(0..texts.len())].split(' ').next().unwrap_or("ΤΙΤΛΟΣ").to_uppercase());
                        }
                        wds.join(" ")
                    };
                    if let Some(p) = place_line(&mut page, pw, ph, font, &[head], &mut rng, mx, 52, body_w as usize, 19.0, ink_level, 1) {
                        hb.push(p.bbox);
                        hl.push((p.text, p.bbox));
                    }
                    let num = format!("{}", rng.gen_range(3..350));
                    let right = rng.gen_bool(0.5);
                    if let Some(p) = place_line(&mut page, pw, ph, font, &[num], &mut rng, mx, 52, body_w as usize, 19.0, ink_level, if right { 2 } else { 0 }) {
                        hb.push(p.bbox);
                        hl.push((p.text, p.bbox));
                    }
                } else {
                    let folio = if rng.gen_bool(0.5) { format!("{}", rng.gen_range(3..350)) } else { format!("— {} —", rng.gen_range(3..350)) };
                    if let Some(p) = place_line(&mut page, pw, ph, font, &[folio], &mut rng, mx, 55, body_w as usize, 20.0, ink_level, 1) {
                        hb.push(p.bbox);
                        hl.push((p.text, p.bbox));
                    }
                }
                if !hb.is_empty() {
                    let id = add_block("page_header", &hb, 0, &mut blocks);
                    for (t, b) in hl {
                        lines.push(LineGT { block: id, bbox: b, text: t });
                    }
                }
            }
            let mut y = 130;
            // chapter opening: big centered heading + optional subtitle, body starts lower
            if chapter_open {
                y = 200;
                // chapter heading: Greek "ΚΕΦΑΛΑΙΟΝ Xʹ" only for Greek streams; a non-Greek stream
                // gets a heading in its OWN script (uppercased stream words) so the page stays
                // language-coherent (S9 plan c).
                let kef = if greek_stream {
                    format!("ΚΕΦΑΛΑΙΟΝ {}\u{02B9}", ["Α","Β","Γ","Δ","Ε","ΣΤ","Ζ","Η"][rng.gen_range(0..8)])
                } else {
                    let mut wds: Vec<String> = Vec::new();
                    for _ in 0..rng.gen_range(1..3) {
                        let w = texts[rng.gen_range(0..texts.len())].split(' ').find(|s| !s.is_empty()).unwrap_or("").to_uppercase();
                        if !w.is_empty() { wds.push(w); }
                    }
                    if wds.is_empty() { texts[rng.gen_range(0..texts.len())].to_uppercase() } else { wds.join(" ") }
                };
                let mut hbx = Vec::new();
                let hstart = lines.len();
                if let Some(p) = place_line(&mut page, pw, ph, font, &[kef], &mut rng, mx, y, body_w as usize, 40.0, ink_level, 1) {
                    hbx.push(p.bbox);
                    lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                }
                y += 86;
                if rng.gen_bool(0.6) {
                    if let Some(p) = place_line(&mut page, pw, ph, font, texts, &mut rng, mx + body_w / 6, y, (body_w * 2 / 3) as usize, 26.0, ink_level, 1) {
                        hbx.push(p.bbox);
                        lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                    }
                    y += 70;
                }
                if !hbx.is_empty() {
                    let id = add_block("heading", &hbx, blocks.len(), &mut blocks);
                    for l in lines[hstart..].iter_mut() {
                        l.block = id;
                    }
                }
                y += 30;
            }
            // body (optionally with a centered VERSE inset)
            let ink_h = rng.gen_range(28.0f32..34.0);
            let pitch = (ink_h * rng.gen_range(1.55..1.85)) as i32;
            let n_body = if chapter_open { rng.gen_range(10..15) } else { rng.gen_range(16..22) };
            let verse_at = if rng.gen_bool(0.25) { Some(n_body / 2) } else { None };
            let mut body_boxes = Vec::new();
            let body_start = lines.len();
            let mut verse_boxes: Vec<[i32; 4]> = Vec::new();
            let mut verse_lines: Vec<usize> = Vec::new();
            // DROP CAP: a MULTI-LINE initial as a figure-like box; the first 2-3 lines start to its
            // right and exclude it (S9 plan b). Only when the page opens with body (no chapter head).
            let (mut cap_x, mut cap_rows) = (mx, 0i32);
            if !chapter_open && verse_at != Some(0) && rng.gen_bool(0.30) {
                // candidate initials from the page's OWN stream (language-coherent: Greek / Latin /
                // Cyrillic per the stream), first alphabetic char of a sampled line, uppercased.
                let mut initials: Vec<String> = Vec::new();
                for _ in 0..8 {
                    if let Some(c) = texts[rng.gen_range(0..texts.len())].chars().find(|c| c.is_alphabetic()) {
                        initials.push(c.to_uppercase().to_string());
                    }
                }
                // size the cap to a true 2-3 body lines (render_cap does NOT clamp to the strip).
                let cap_lines = rng.gen_range(2..4);
                let cap_h = pitch as f32 * (cap_lines as f32 - 0.15);
                if let Some((cbox, tx)) = place_dropcap(&mut page, pw, ph, font, &initials, mx, y, cap_h, ink_level) {
                    add_block("figure", &[cbox], blocks.len(), &mut blocks);
                    cap_x = tx;
                    // indent the body past the cap for as many lines as the cap ACTUALLY inks — keeps
                    // the indent matched to the rendered multi-line cap, not an over-reserved band.
                    cap_rows = (((cbox[3] - cbox[1]) as f32 / pitch as f32).ceil() as i32).clamp(1, 3);
                }
            }
            for k in 0..n_body {
                if Some(k) == verse_at {
                    y += 14;
                    for _ in 0..rng.gen_range(2..5) {
                        if let Some(p) = place_line(&mut page, pw, ph, font, texts, &mut rng, mx + body_w / 5, y, (body_w * 3 / 5) as usize, 24.0, ink_level, 1) {
                            verse_boxes.push(p.bbox);
                            lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                            verse_lines.push(lines.len() - 1);
                        }
                        y += 42;
                    }
                    y += 14;
                    continue;
                }
                // beside the drop cap for the first cap_rows lines: indent past the cap box.
                let (lx, lw) = if cap_rows > 0 {
                    cap_rows -= 1;
                    (cap_x, (body_w - (cap_x - mx)).max(64))
                } else {
                    (mx, body_w)
                };
                if let Some(p) = place_line(&mut page, pw, ph, font, texts, &mut rng, lx, y, lw as usize, ink_h, ink_level, 0) {
                    // occasional footnote MARKER at line end: "(1)"
                    body_boxes.push(p.bbox);
                    lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                }
                y += pitch;
            }
            if !body_boxes.is_empty() {
                let id = add_block("main_text", &body_boxes, blocks.len(), &mut blocks);
                for (k, l) in lines[body_start..].iter_mut().enumerate() {
                    if l.block == usize::MAX && !verse_lines.contains(&(body_start + k)) {
                        l.block = id;
                    }
                }
            }
            if !verse_boxes.is_empty() {
                let id = add_block("main_text", &verse_boxes, blocks.len(), &mut blocks);
                for &vi in &verse_lines {
                    lines[vi].block = id;
                }
            }
            // marginalia: 1-2 short small lines in the outer margin
            if rng.gen_bool(0.25) && mx > 120 {
                let my = rng.gen_range(300..(ph as i32 - 400));
                let mut mb = Vec::new();
                let mstart = lines.len();
                for k in 0..rng.gen_range(1..3) {
                    if let Some(p) = place_line(&mut page, pw, ph, font, texts, &mut rng, 18, my + k * 34, (mx - 40) as usize, 18.0, ink_level, 0) {
                        mb.push(p.bbox);
                        lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                    }
                }
                if !mb.is_empty() {
                    let id = add_block("marginalia", &mb, blocks.len(), &mut blocks);
                    for l in lines[mstart..].iter_mut() {
                        if l.block == usize::MAX {
                            l.block = id;
                        }
                    }
                }
            }
            // footnotes WITH markers ("1. …")
            if rng.gen_bool(0.6) {
                y += 20;
                hrule(&mut page, pw, mx, mx + body_w / 4, y, ink_level);
                y += 18;
                let mut fboxes = Vec::new();
                let fstart = lines.len();
                for k in 0..rng.gen_range(2..4) {
                    let base = texts[rng.gen_range(0..texts.len())].clone();
                    let marked = format!("{}. {}", k + 1, base);
                    if let Some(p) = place_line(&mut page, pw, ph, font, &[marked], &mut rng, mx, y, body_w as usize, 22.0, ink_level, 0) {
                        fboxes.push(p.bbox);
                        lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                    }
                    y += 40;
                }
                if !fboxes.is_empty() {
                    let id = add_block("footnote", &fboxes, blocks.len(), &mut blocks);
                    for l in lines[fstart..].iter_mut() {
                        if l.block == usize::MAX {
                            l.block = id;
                        }
                    }
                }
            }
            // bottom folio (page number at foot)
            if bottom_folio {
                let folio = format!("{}", rng.gen_range(3..350));
                if let Some(p) = place_line(&mut page, pw, ph, font, &[folio], &mut rng, mx, ph as i32 - 78, body_w as usize, 20.0, ink_level, 1) {
                    let id = add_block("page_footer_folio", &[p.bbox], blocks.len(), &mut blocks);
                    lines.push(LineGT { block: id, bbox: p.bbox, text: p.text });
                }
            }
        }
        "tablepage" => {
            // the ~1890 proceedings signature: heading + preamble + ruled table w/ header row,
            // polytonic row labels, right-aligned digit columns, totals row
            let mx = (pw as f32 * rng.gen_range(0.07..0.13)) as i32; // F1: randomize table margin
            let tw = pw as i32 - 2 * mx;
            let num = format!("— {} —", rng.gen_range(3..900));
            if let Some(p) = place_line(&mut page, pw, ph, font, &[num], &mut rng, mx, 48, tw as usize, 18.0, ink_level, 1) {
                let id = add_block("page_header", &[p.bbox], 0, &mut blocks);
                lines.push(LineGT { block: id, bbox: p.bbox, text: p.text });
            }
            let mut hbx = Vec::new();
            let hstart = lines.len();
            if let Some(p) = place_line(&mut page, pw, ph, font, texts, &mut rng, mx, 92, tw as usize, 24.0, ink_level, 1) {
                hbx.push(p.bbox);
                lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
            }
            if !hbx.is_empty() {
                let id = add_block("heading", &hbx, 1, &mut blocks);
                for l in lines[hstart..].iter_mut() {
                    l.block = id;
                }
            }
            let n_cols_num = rng.gen_range(3..6);
            // F1 (Fable S13): randomize table anchor + geometry so the `table` class is not fixed at
            // one frame position (was margin 9% / top 170 / pitch 42 / label 30% on every page).
            let label_w = (tw as f32 * rng.gen_range(0.22..0.36)) as i32;
            let col_w = (tw - label_w) / n_cols_num;
            let top = rng.gen_range(150..320);
            let row_pitch = rng.gen_range(38..48);
            let n_rows = rng.gen_range(14..24);
            let bot = top + (n_rows + 2) * row_pitch;
            // rules
            hrule(&mut page, pw, mx, mx + tw, top, ink_level);
            hrule(&mut page, pw, mx, mx + tw, top + row_pitch, ink_level);
            hrule(&mut page, pw, mx, mx + tw, bot, ink_level);
            vrule(&mut page, pw, mx, top, bot, ink_level);
            vrule(&mut page, pw, mx + tw, top, bot, ink_level);
            for kc in 0..=n_cols_num {
                vrule(&mut page, pw, mx + label_w + kc * col_w, top, bot, ink_level);
            }
            let mut tboxes = Vec::new();
            let tstart = lines.len();
            // header cells (short uppercase words)
            for kc in 0..n_cols_num {
                let word = texts[rng.gen_range(0..texts.len())].split(' ').next().unwrap_or("ΠΟΣΟΝ").to_uppercase();
                if let Some(p) = place_line(&mut page, pw, ph, font, &[word], &mut rng, mx + label_w + kc * col_w + 6, top + 4, (col_w - 12) as usize, 17.0, ink_level, 1) {
                    tboxes.push(p.bbox);
                    lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                }
            }
            for r in 0..n_rows {
                let ry = top + row_pitch * (r + 1) + 4;
                // label: 1-2 words from the bank
                let lbl: String = texts[rng.gen_range(0..texts.len())].split(' ').take(rng.gen_range(1..3)).collect::<Vec<_>>().join(" ");
                if let Some(p) = place_line(&mut page, pw, ph, font, &[lbl], &mut rng, mx + 8, ry, (label_w - 16) as usize, 19.0, ink_level, 0) {
                    tboxes.push(p.bbox);
                    lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                }
                for kc in 0..n_cols_num {
                    let cell = digit_cell(&mut rng);
                    if let Some(p) = place_line(&mut page, pw, ph, font, &[cell], &mut rng, mx + label_w + kc * col_w + 6, ry, (col_w - 14) as usize, 19.0, ink_level, 2) {
                        tboxes.push(p.bbox);
                        lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                    }
                }
            }
            if !tboxes.is_empty() {
                let id = add_block("table", &tboxes, blocks.len(), &mut blocks);
                for l in lines[tstart..].iter_mut() {
                    if l.block == usize::MAX {
                        l.block = id;
                    }
                }
            }
        }
        "plate" => {
            // 1899 plate page: heading, framed figure, caption, verse below
            let mx = (pw as f32 * 0.16) as i32;
            let body_w = pw as i32 - 2 * mx;
            if let Some(p) = place_line(&mut page, pw, ph, font, texts, &mut rng, mx, 120, body_w as usize, 40.0, ink_level, 1) {
                let id = add_block("heading", &[p.bbox], 0, &mut blocks);
                lines.push(LineGT { block: id, bbox: p.bbox, text: p.text });
            }
            let fw = (body_w as f32 * rng.gen_range(0.5..0.7)) as i32;
            let fh = (fw as f32 * rng.gen_range(1.1..1.4)) as i32;
            let fx = mx + (body_w - fw) / 2;
            let fy = 240;
            draw_plate(&mut rng, &mut page, pw, fx, fy, fw, fh, ink_level);
            add_block("figure", &[[fx, fy, fx + fw, fy + fh]], 1, &mut blocks);
            let cy = fy + fh + 26;
            if let Some(p) = place_line(&mut page, pw, ph, font, texts, &mut rng, mx, cy, body_w as usize, 24.0, ink_level, 1) {
                let id = add_block("caption", &[p.bbox], 2, &mut blocks);
                lines.push(LineGT { block: id, bbox: p.bbox, text: p.text });
            }
            let mut y = cy + 70;
            let mut vb = Vec::new();
            let vstart = lines.len();
            for _ in 0..rng.gen_range(3..6) {
                if let Some(p) = place_line(&mut page, pw, ph, font, texts, &mut rng, mx + body_w / 6, y, (body_w * 2 / 3) as usize, 24.0, ink_level, 1) {
                    vb.push(p.bbox);
                    lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                }
                y += 44;
            }
            if !vb.is_empty() {
                let id = add_block("main_text", &vb, blocks.len(), &mut blocks);
                for l in lines[vstart..].iter_mut() {
                    if l.block == usize::MAX {
                        l.block = id;
                    }
                }
            }
        }
        "apparatus" => {
            // critical edition: folio + classical main text + line-number marginalia (outer
            // margin, every 5 lines) + dense APPARATUS band at the foot (rule, smaller type,
            // lemma] variant SIGLUM : variant SIGLUM). The layout class no public dataset carries.
            let lo = Layout::sample(&mut rng, "apparatus", pw);
            let body_w = pw as i32 - 2 * lo.mx;
            let num = format!("{}", rng.gen_range(3..400));
            if let Some(p) = place_line(&mut page, pw, ph, font, &[num], &mut rng, lo.mx, 50, body_w as usize, 18.0, ink_level, 1) {
                let id = add_block("page_header", &[p.bbox], 0, &mut blocks);
                lines.push(LineGT { block: id, bbox: p.bbox, text: p.text });
            }
            let pitch = (lo.ink_h * lo.leading) as i32;
            let n_body = rng.gen_range(15..22);
            let mut y = lo.top + 10;
            let (mut body_boxes, mut marg_boxes) = (Vec::new(), Vec::new());
            let (mut body_idx, mut marg_idx): (Vec<usize>, Vec<usize>) = (Vec::new(), Vec::new());
            let mut lineno = 0;
            for _ in 0..n_body {
                if let Some(p) = place_line(&mut page, pw, ph, font, texts, &mut rng, lo.mx, y, body_w as usize, lo.ink_h, ink_level, 0) {
                    body_boxes.push(p.bbox);
                    lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                    body_idx.push(lines.len() - 1);
                    lineno += 1;
                    if lineno % 5 == 0 && lo.mx > 80 {
                        // number right-aligned in the outer margin (slot >= MIN_W=64px).
                        let ln = format!("{lineno}");
                        if let Some(pn) = place_line(&mut page, pw, ph, font, &[ln], &mut rng, 6, y, (lo.mx - 12) as usize, lo.ink_h * 0.7, ink_level, 2) {
                            marg_boxes.push(pn.bbox);
                            lines.push(LineGT { block: usize::MAX, bbox: pn.bbox, text: pn.text });
                            marg_idx.push(lines.len() - 1);
                        }
                    }
                }
                y += pitch;
                if y > ph as i32 - 380 {
                    break;
                }
            }
            if !body_boxes.is_empty() {
                let id = add_block("main_text", &body_boxes, blocks.len(), &mut blocks);
                for &i in &body_idx {
                    lines[i].block = id;
                }
            }
            if !marg_boxes.is_empty() {
                let id = add_block("marginalia", &marg_boxes, blocks.len(), &mut blocks);
                for &i in &marg_idx {
                    lines[i].block = id;
                }
            }
            // apparatus band
            let ay = (ph as i32 - 340).max(y + 20);
            hrule(&mut page, pw, lo.mx, lo.mx + body_w / 3, ay, ink_level);
            let sigla = ["A", "B", "M", "P", "V", "L", "cod.", "codd.", "om.", "add.", "cett.", "corr."];
            let pick = |r: &mut ChaCha20Rng| -> String {
                texts[r.gen_range(0..texts.len())].split(' ').find(|s| !s.is_empty()).unwrap_or("—").chars().take(12).collect()
            };
            let mut app_boxes = Vec::new();
            let astart = lines.len();
            let mut ey = ay + 18;
            for _ in 0..rng.gen_range(5..9) {
                let mut entry = String::new();
                for e in 0..rng.gen_range(1..3) {
                    if e > 0 {
                        entry.push_str("  |  ");
                    }
                    let s1 = sigla[rng.gen_range(0..sigla.len())];
                    let s2 = sigla[rng.gen_range(0..sigla.len())];
                    entry.push_str(&format!("{} {}] {} {} : {} {}", rng.gen_range(1..n_body.max(2)), pick(&mut rng), pick(&mut rng), s1, pick(&mut rng), s2));
                }
                if let Some(p) = place_line(&mut page, pw, ph, font, &[entry], &mut rng, lo.mx, ey, body_w as usize, lo.ink_h * 0.62, ink_level, 0) {
                    app_boxes.push(p.bbox);
                    lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                }
                ey += (lo.ink_h * 0.62 * 1.6) as i32;
                if ey > ph as i32 - 60 {
                    break;
                }
            }
            if !app_boxes.is_empty() {
                let id = add_block("apparatus", &app_boxes, blocks.len(), &mut blocks);
                for l in lines[astart..].iter_mut() {
                    if l.block == usize::MAX {
                        l.block = id;
                    }
                }
            }
        }
        "toc" => {
            // table of contents: centered heading + entries, each = label (left) + LEADER DOTS +
            // page number (right). Each row is a `toc_entry` block (label line + number line).
            let lo = Layout::sample(&mut rng, "toc", pw);
            let body_w = pw as i32 - 2 * lo.mx;
            let head = if rng.gen_bool(0.5) { "ΠΕΡΙΕΧΟΜΕΝΑ" } else { "ΠΙΝΑΞ ΤΩΝ ΠΕΡΙΕΧΟΜΕΝΩΝ" };
            let mut y = lo.top;
            if let Some(p) = place_line(&mut page, pw, ph, font, &[head.to_string()], &mut rng, lo.mx, y, body_w as usize, lo.ink_h * 1.15, ink_level, 1) {
                let id = add_block("heading", &[p.bbox], 0, &mut blocks);
                lines.push(LineGT { block: id, bbox: p.bbox, text: p.text });
                y += (lo.ink_h * 2.6) as i32;
            }
            let pitch = (lo.ink_h * lo.leading) as i32;
            let num_w = 110i32;
            let n = rng.gen_range(14..24);
            for _ in 0..n {
                let indent = if rng.gen_bool(0.28) { rng.gen_range(24..60) } else { 0 };
                let lx = lo.mx + indent;
                let label_slot = (body_w - indent - num_w - 40).max(64) as usize;
                let Some(pl) = place_line(&mut page, pw, ph, font, texts, &mut rng, lx, y, label_slot, lo.ink_h, ink_level, 0) else {
                    y += pitch;
                    continue;
                };
                let pnum = format!("{}", rng.gen_range(1..480));
                let nx = lo.mx + body_w - num_w;
                let mut row = vec![pl.bbox];
                let row_start = lines.len();
                lines.push(LineGT { block: usize::MAX, bbox: pl.bbox, text: pl.text });
                if let Some(pn) = place_line(&mut page, pw, ph, font, &[pnum], &mut rng, nx, y, num_w as usize, lo.ink_h, ink_level, 2) {
                    // leader dots between the label and the number, on the text baseline row.
                    let dy = (pl.bbox[1] + pl.bbox[3]) / 2 + 2;
                    let (ds, de) = (pl.bbox[2] + 12, pn.bbox[0] - 12);
                    let mut dx = ds;
                    while dx < de {
                        for yy in dy..(dy + 2).min(ph as i32) {
                            for xx in dx..(dx + 2).min(pw as i32) {
                                if xx >= 0 && yy >= 0 {
                                    page[yy as usize * pw + xx as usize] = ink_level;
                                }
                            }
                        }
                        dx += 11;
                    }
                    row.push(pn.bbox);
                    lines.push(LineGT { block: usize::MAX, bbox: pn.bbox, text: pn.text });
                }
                let id = add_block("toc_entry", &row, blocks.len(), &mut blocks);
                for l in lines[row_start..].iter_mut() {
                    l.block = id;
                }
                y += pitch;
                if y > ph as i32 - 90 {
                    break;
                }
            }
        }
        "bibliography" => {
            // bibliography / references: heading + entries with HANGING INDENT (first line flush,
            // continuation lines indented). Each entry is a `bibliography_entry` block.
            let lo = Layout::sample(&mut rng, "bibliography", pw);
            let body_w = pw as i32 - 2 * lo.mx;
            let mut y = lo.top;
            let head = if rng.gen_bool(0.5) { "ΒΙΒΛΙΟΓΡΑΦΙΑ" } else { "ΠΑΡΑΠΟΜΠΑΙ" };
            if let Some(p) = place_line(&mut page, pw, ph, font, &[head.to_string()], &mut rng, lo.mx, y, body_w as usize, lo.ink_h * 1.1, ink_level, 1) {
                let id = add_block("heading", &[p.bbox], 0, &mut blocks);
                lines.push(LineGT { block: id, bbox: p.bbox, text: p.text });
                y += (lo.ink_h * 2.4) as i32;
            }
            let pitch = (lo.ink_h * lo.leading) as i32;
            let hang = rng.gen_range(38..58);
            let n = rng.gen_range(9..15);
            for _ in 0..n {
                let entry_lines = rng.gen_range(1..4);
                let mut ebox = Vec::new();
                let estart = lines.len();
                for li in 0..entry_lines {
                    let (x, slot) = if li == 0 { (lo.mx, body_w) } else { (lo.mx + hang, body_w - hang) };
                    if let Some(p) = place_line(&mut page, pw, ph, font, texts, &mut rng, x, y, slot as usize, lo.ink_h, ink_level, 0) {
                        ebox.push(p.bbox);
                        lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                    }
                    y += pitch;
                    if y > ph as i32 - 90 {
                        break;
                    }
                }
                if !ebox.is_empty() {
                    let id = add_block("bibliography_entry", &ebox, blocks.len(), &mut blocks);
                    for l in lines[estart..].iter_mut() {
                        l.block = id;
                    }
                }
                y += (lo.ink_h * 0.4) as i32; // inter-entry gap
                if y > ph as i32 - 90 {
                    break;
                }
            }
        }
        "list" => {
            // itemized list: optional heading + items, each led by a MARKER (decimal / Greek
            // numeral / bullet / dash / paren) with hanging indent on wrapped lines. Each item is
            // a `list_item` block.
            let lo = Layout::sample(&mut rng, "list", pw);
            let body_w = pw as i32 - 2 * lo.mx;
            let mut y = lo.top;
            if rng.gen_bool(0.6) {
                let head: String = texts[rng.gen_range(0..texts.len())].split(' ').take(rng.gen_range(2..5)).collect::<Vec<_>>().join(" ").to_uppercase();
                if let Some(p) = place_line(&mut page, pw, ph, font, &[head], &mut rng, lo.mx, y, body_w as usize, lo.ink_h * 1.05, ink_level, 0) {
                    let id = add_block("heading", &[p.bbox], 0, &mut blocks);
                    lines.push(LineGT { block: id, bbox: p.bbox, text: p.text });
                    y += (lo.ink_h * 2.2) as i32;
                }
            }
            let pitch = (lo.ink_h * lo.leading) as i32;
            let style = rng.gen_range(0..5u8);
            let greek_num = ["αʹ", "βʹ", "γʹ", "δʹ", "εʹ", "ϛʹ", "ζʹ", "ηʹ", "θʹ", "ιʹ", "ιαʹ", "ιβʹ", "ιγʹ", "ιδʹ", "ιεʹ"];
            let hang = rng.gen_range(40..64);
            let n = rng.gen_range(8..15);
            for i in 0..n {
                let marker = match style {
                    0 => format!("{}.", i + 1),
                    1 => format!("{})", greek_num[i.min(greek_num.len() - 1)]),
                    2 => "•".to_string(),
                    3 => "—".to_string(),
                    _ => format!("({})", i + 1),
                };
                let t = texts[rng.gen_range(0..texts.len())].clone();
                let first = format!("{marker} {t}");
                let mut ibox = Vec::new();
                let istart = lines.len();
                if let Some(p) = place_line(&mut page, pw, ph, font, &[first], &mut rng, lo.mx, y, body_w as usize, lo.ink_h, ink_level, 0) {
                    ibox.push(p.bbox);
                    lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                    y += pitch;
                }
                // 0-1 wrapped continuation lines, hanging-indented past the marker
                if rng.gen_bool(0.4) {
                    if let Some(p) = place_line(&mut page, pw, ph, font, texts, &mut rng, lo.mx + hang, y, (body_w - hang) as usize, lo.ink_h, ink_level, 0) {
                        ibox.push(p.bbox);
                        lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                        y += pitch;
                    }
                }
                if !ibox.is_empty() {
                    let id = add_block("list_item", &ibox, blocks.len(), &mut blocks);
                    for l in lines[istart..].iter_mut() {
                        l.block = id;
                    }
                }
                y += (lo.ink_h * 0.25) as i32;
                if y > ph as i32 - 90 {
                    break;
                }
            }
        }
        "title" => {
            // title page: big centered TITLE (heading), subtitle, printer's ornament (figure),
            // author line, and a place+year imprint at the foot (dateline_signature). Sparse.
            let lo = Layout::sample(&mut rng, "title", pw);
            let body_w = pw as i32 - 2 * lo.mx;
            let words_upper = |r: &mut ChaCha20Rng, n: usize| -> String {
                texts[r.gen_range(0..texts.len())].split(' ').filter(|s| !s.is_empty()).take(n).collect::<Vec<_>>().join(" ").to_uppercase()
            };
            let mut y = rng.gen_range(230..330);
            let (mut hb, hstart) = (Vec::new(), lines.len());
            for _ in 0..rng.gen_range(1..3) {
                let k = rng.gen_range(1..4);
                let t = words_upper(&mut rng, k);
                if let Some(p) = place_line(&mut page, pw, ph, font, &[t], &mut rng, lo.mx, y, body_w as usize, lo.ink_h * 1.2, ink_level, 1) {
                    hb.push(p.bbox);
                    lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                }
                y += (lo.ink_h * 2.3) as i32;
            }
            if !hb.is_empty() {
                let id = add_block("heading", &hb, 0, &mut blocks);
                for l in lines[hstart..].iter_mut() {
                    l.block = id;
                }
            }
            y += 24;
            if rng.gen_bool(0.7) {
                if let Some(p) = place_line(&mut page, pw, ph, font, texts, &mut rng, lo.mx + body_w / 8, y, (body_w * 3 / 4) as usize, lo.ink_h * 0.72, ink_level, 1) {
                    let id = add_block("main_text", &[p.bbox], 1, &mut blocks);
                    lines.push(LineGT { block: id, bbox: p.bbox, text: p.text });
                }
                y += 90;
            }
            // printer's ornament (figure)
            let fw = rng.gen_range(130..260);
            let fh = rng.gen_range(80..150);
            let fx = lo.mx + (body_w - fw) / 2;
            let fy = y + 30;
            draw_plate(&mut rng, &mut page, pw, fx, fy, fw, fh, ink_level);
            add_block("figure", &[[fx, fy, fx + fw, fy + fh]], 2, &mut blocks);
            let ay = fy + fh + 70;
            let ka = rng.gen_range(2..4);
            let auth = format!("ΥΠΟ {}", words_upper(&mut rng, ka));
            if let Some(p) = place_line(&mut page, pw, ph, font, &[auth], &mut rng, lo.mx, ay, body_w as usize, lo.ink_h * 0.8, ink_level, 1) {
                let id = add_block("main_text", &[p.bbox], 3, &mut blocks);
                lines.push(LineGT { block: id, bbox: p.bbox, text: p.text });
            }
            // place + year imprint at the foot
            let iy = ph as i32 - rng.gen_range(220..300);
            let place = ["ΕΝ ΑΘΗΝΑΙΣ", "ΕΝ ΘΗΒΑΙΣ", "ΕΝ ΠΑΤΡΑΙΣ", "ΕΝ ΕΡΜΟΥΠΟΛΕΙ", "ΕΝ ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΙ"][rng.gen_range(0..5)];
            let mut ib = Vec::new();
            let ib_start = lines.len();
            if let Some(p) = place_line(&mut page, pw, ph, font, &[place.to_string()], &mut rng, lo.mx, iy, body_w as usize, lo.ink_h * 0.72, ink_level, 1) {
                ib.push(p.bbox);
                lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
            }
            let year = format!("{}", rng.gen_range(1850..1935));
            if let Some(p) = place_line(&mut page, pw, ph, font, &[year], &mut rng, lo.mx, iy + 56, body_w as usize, lo.ink_h * 0.66, ink_level, 1) {
                ib.push(p.bbox);
                lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
            }
            if !ib.is_empty() {
                let id = add_block("dateline_signature", &ib, 4, &mut blocks);
                for l in lines[ib_start..].iter_mut() {
                    l.block = id;
                }
            }
        }
        "dateline" => {
            // document/letter body ending in a LETTERSPACED (gesperrt) dateline + signature —
            // "Ἐν Ἀθήναις, τῇ 15 Δεκεμβρίου 1899" then a name — right-of-centre, own block.
            let lo = Layout::sample(&mut rng, "dateline", pw);
            let body_w = pw as i32 - 2 * lo.mx;
            let pitch = (lo.ink_h * lo.leading) as i32;
            let mut y = lo.top;
            let (mut body_boxes, bstart) = (Vec::new(), lines.len());
            for _ in 0..rng.gen_range(10..18) {
                if let Some(p) = place_line(&mut page, pw, ph, font, texts, &mut rng, lo.mx, y, body_w as usize, lo.ink_h, ink_level, 0) {
                    body_boxes.push(p.bbox);
                    lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                }
                y += pitch;
                if y > ph as i32 - 420 {
                    break;
                }
            }
            if !body_boxes.is_empty() {
                let id = add_block("main_text", &body_boxes, blocks.len(), &mut blocks);
                for l in lines[bstart..].iter_mut() {
                    l.block = id;
                }
            }
            // letterspaced dateline + signature, indented to the right half, own block.
            y += 40;
            let months = ["Ἰανουαρίου", "Φεβρουαρίου", "Μαρτίου", "Ἀπριλίου", "Μαΐου", "Ἰουνίου", "Ἰουλίου", "Αὐγούστου", "Σεπτεμβρίου", "Ὀκτωβρίου", "Νοεμβρίου", "Δεκεμβρίου"];
            let places = ["Ἐν Ἀθήναις", "Ἐν Θήβαις", "Ἐν Πάτραις", "Ἐν Ἑρμουπόλει", "Ἐν Κερκύρᾳ"];
            let dl = format!("{}, τῇ {} {} {}", places[rng.gen_range(0..places.len())], rng.gen_range(1..29), months[rng.gen_range(0..12)], rng.gen_range(1850..1935));
            let sx = lo.mx + body_w / 3;
            let slot = (body_w * 2 / 3) as usize;
            let track = rng.gen_range(0.10f32..0.20);
            let (mut db, dstart) = (Vec::new(), lines.len());
            if let Some(p) = place_line_t(&mut page, pw, ph, font, &[dl], &mut rng, sx, y, slot, lo.ink_h * 0.82, ink_level, 1, track) {
                db.push(p.bbox);
                lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                y += (lo.ink_h * 2.2) as i32;
            }
            // signature: letterspaced uppercase name
            let sig: String = texts[rng.gen_range(0..texts.len())].split(' ').filter(|s| !s.is_empty()).take(rng.gen_range(1..3)).collect::<Vec<_>>().join(" ").to_uppercase();
            if let Some(p) = place_line_t(&mut page, pw, ph, font, &[sig], &mut rng, sx, y, slot, lo.ink_h * 0.78, ink_level, 1, track) {
                db.push(p.bbox);
                lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
            }
            if !db.is_empty() {
                let id = add_block("dateline_signature", &db, blocks.len(), &mut blocks);
                for l in lines[dstart..].iter_mut() {
                    l.block = id;
                }
            }
        }
        "handwriting" => {
            // printed page annotated by HAND: printed main text + 1-2 handwritten-note blocks
            // (procedural strokes) marked as `figure` (no text GT) + an optional corner scrawl.
            let lo = Layout::sample(&mut rng, "handwriting", pw);
            let body_w = pw as i32 - 2 * lo.mx;
            let pitch = (lo.ink_h * lo.leading) as i32;
            let mut y = lo.top;
            let n_body = rng.gen_range(9..15);
            let (mut body_boxes, bstart) = (Vec::new(), lines.len());
            for _ in 0..n_body {
                if let Some(p) = place_line(&mut page, pw, ph, font, texts, &mut rng, lo.mx, y, body_w as usize, lo.ink_h, ink_level, 0) {
                    body_boxes.push(p.bbox);
                    lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                }
                y += pitch;
            }
            if !body_boxes.is_empty() {
                let id = add_block("main_text", &body_boxes, blocks.len(), &mut blocks);
                for l in lines[bstart..].iter_mut() {
                    l.block = id;
                }
            }
            // (1) a handwritten margin note (narrow tall box in the outer margin), if room
            if lo.mx > 110 && rng.gen_bool(0.7) {
                let mnx = 12;
                let mny = rng.gen_range(lo.top..(lo.top + 300));
                let mnw = lo.mx - 24;
                let mnh = rng.gen_range(120..320).min(ph as i32 - mny - 40);
                let ink_hw = (ink_level + rng.gen_range(0.0..0.06)).min(0.35);
                draw_scribble(&mut rng, &mut page, pw, ph, mnx, mny, mnw, mnh, ink_hw);
                add_block("figure", &[[mnx, mny, mnx + mnw, mny + mnh]], blocks.len(), &mut blocks);
            }
            // (2) a handwritten note block below the printed text
            let hy = (y + 30).min(ph as i32 - 260);
            let hh = rng.gen_range(120..240).min(ph as i32 - hy - 60);
            let hx = lo.mx + rng.gen_range(0..80);
            let hw = (body_w - rng.gen_range(0..200)).max(200);
            let ink_hw = (ink_level + rng.gen_range(0.0..0.06)).min(0.35);
            draw_scribble(&mut rng, &mut page, pw, ph, hx, hy, hw, hh, ink_hw);
            add_block("figure", &[[hx, hy, hx + hw, hy + hh]], blocks.len(), &mut blocks);
            // (3) optional corner signature scrawl
            if rng.gen_bool(0.5) {
                let sx = lo.mx + body_w - rng.gen_range(240..340);
                let sy = (hy + hh + 40).min(ph as i32 - 120);
                let sw = rng.gen_range(180..300);
                draw_scribble(&mut rng, &mut page, pw, ph, sx, sy, sw, 60, ink_level);
                add_block("figure", &[[sx, sy, sx + sw, sy + 60]], blocks.len(), &mut blocks);
            }
        }
        "dense_letterpress" => {
            // DENSE POLYTONIC LETTERPRESS (guide_W3 §2.2 dense19c): tight leading, ~30-50 nearly
            // full-width body lines, a running header + folio, and a smaller-type footnote block at
            // the foot. This is the joint cell the detector over-fragments on; the composer supplies
            // the DENSE GEOMETRY + exact per-line GT, while worn/faded LETTERPRESS APPEARANCE comes
            // from the page-scale scan-physics (Photo) ops + the training photometric degrade.
            let mx = (pw as f32 * rng.gen_range(0.10..0.14)) as i32;
            let body_w = pw as i32 - 2 * mx;
            // running header: uppercase running head (stream words -> language-neutral) centered,
            // page number set to one outer corner.
            let mut hb: Vec<[i32; 4]> = Vec::new();
            let mut hl: Vec<(String, [i32; 4])> = Vec::new();
            let head: String = {
                let mut wds: Vec<String> = Vec::new();
                for _ in 0..rng.gen_range(1..3) {
                    let w = texts[rng.gen_range(0..texts.len())].split(' ').find(|s| !s.is_empty()).unwrap_or("").to_uppercase();
                    if !w.is_empty() { wds.push(w); }
                }
                wds.join(" ")
            };
            if !head.is_empty() {
                if let Some(p) = place_line(&mut page, pw, ph, font, &[head], &mut rng, mx, 50, body_w as usize, 17.0, ink_level, 1) {
                    hb.push(p.bbox);
                    hl.push((p.text, p.bbox));
                }
            }
            let num = format!("{}", rng.gen_range(3..600));
            let num_align = if rng.gen_bool(0.5) { 0 } else { 2 };
            if let Some(p) = place_line(&mut page, pw, ph, font, &[num], &mut rng, mx, 50, body_w as usize, 17.0, ink_level, num_align) {
                hb.push(p.bbox);
                hl.push((p.text, p.bbox));
            }
            if !hb.is_empty() {
                let id = add_block("page_header", &hb, 0, &mut blocks);
                for (t, b) in hl {
                    lines.push(LineGT { block: id, bbox: b, text: t });
                }
            }
            // dense body: TIGHT leading (ratio 1.05-1.35), near-full-width lines (occasional short
            // paragraph-final line for ragged realism).
            let ink_h = rng.gen_range(23.0f32..29.0);
            let leading = rng.gen_range(1.05f32..1.35);
            let pitch = (ink_h * leading).round().max(19.0) as i32;
            let foot_reserve = rng.gen_range(230..330); // room for the footnote block
            let mut y = rng.gen_range(92..126);
            let mut body_boxes = Vec::new();
            let bstart = lines.len();
            while y < ph as i32 - foot_reserve {
                let slot = if rng.gen_bool(0.16) { (body_w as f32 * rng.gen_range(0.45..0.85)) as usize } else { body_w as usize };
                if let Some(p) = place_line(&mut page, pw, ph, font, texts, &mut rng, mx, y, slot, ink_h, ink_level, 0) {
                    body_boxes.push(p.bbox);
                    lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                }
                y += pitch;
            }
            if !body_boxes.is_empty() {
                let id = add_block("main_text", &body_boxes, blocks.len(), &mut blocks);
                for l in lines[bstart..].iter_mut() {
                    if l.block == usize::MAX {
                        l.block = id;
                    }
                }
            }
            // footnote block at the foot: rule + smaller type ("1. …"), even tighter leading.
            let mut fy = (ph as i32 - foot_reserve + 24).max(y + 12);
            hrule(&mut page, pw, mx, mx + body_w / 3, fy, ink_level);
            fy += 16;
            let f_ink = ink_h * rng.gen_range(0.66..0.78);
            let f_pitch = (f_ink * rng.gen_range(1.05..1.25)).round().max(15.0) as i32;
            let mut fboxes = Vec::new();
            let fstart = lines.len();
            for k in 0..rng.gen_range(3..7) {
                let base = texts[rng.gen_range(0..texts.len())].clone();
                let marked = format!("{}. {}", k + 1, base);
                if let Some(p) = place_line(&mut page, pw, ph, font, &[marked], &mut rng, mx, fy, body_w as usize, f_ink, ink_level, 0) {
                    fboxes.push(p.bbox);
                    lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                }
                fy += f_pitch;
                if fy > ph as i32 - 40 {
                    break;
                }
            }
            if !fboxes.is_empty() {
                let id = add_block("footnote", &fboxes, blocks.len(), &mut blocks);
                for l in lines[fstart..].iter_mut() {
                    if l.block == usize::MAX {
                        l.block = id;
                    }
                }
            }
        }
        "web_digital" => {
            // BORN-DIGITAL / WEB (guide_W3 §2.2 digital_web): white page, sans face, small
            // ragged-right flowed paragraphs with paragraph GAPS + tight leading, occasional
            // underlined link spans, and a right-side infobox rect (image/figure card). Leaving these
            // pages photometrically CLEAN (degrade gated off for web) is a training-time concern; the
            // composer sets the crisp near-white bg / near-black ink above and lays out the geometry.
            let mx = (pw as f32 * rng.gen_range(0.08..0.14)) as i32;
            let body_w = pw as i32 - 2 * mx;
            let mut y = rng.gen_range(70..110);
            // optional small top-nav line
            if rng.gen_bool(0.5) {
                let nav: String = texts[rng.gen_range(0..texts.len())].split(' ').take(rng.gen_range(3..6)).collect::<Vec<_>>().join("   ");
                if let Some(p) = place_line(&mut page, pw, ph, font, &[nav], &mut rng, mx, y, body_w as usize, 15.0, ink_level, 0) {
                    let id = add_block("page_header", &[p.bbox], 0, &mut blocks);
                    lines.push(LineGT { block: id, bbox: p.bbox, text: p.text });
                }
                y += 44;
            }
            // page title (heading), larger
            let title: String = texts[rng.gen_range(0..texts.len())].split(' ').take(rng.gen_range(2..6)).collect::<Vec<_>>().join(" ");
            let title_h = rng.gen_range(34.0f32..44.0);
            if let Some(p) = place_line(&mut page, pw, ph, font, &[title], &mut rng, mx, y, body_w as usize, title_h, ink_level, 0) {
                let id = add_block("heading", &[p.bbox], blocks.len(), &mut blocks);
                lines.push(LineGT { block: id, bbox: p.bbox, text: p.text });
                y += 78;
            }
            // right-side infobox card (image/figure placeholder) with an optional caption line. `ibx`
            // carries (ix, top, occupied_bottom) where occupied_bottom is the caption's bottom if a
            // caption is placed, else the box bottom — so the body-wrap window below spans the WHOLE
            // column (box + caption) and no body line overprints the caption (F1).
            let ibx: Option<(i32, i32, i32)> = if rng.gen_bool(0.6) {
                let iw = (body_w as f32 * rng.gen_range(0.28..0.36)) as i32;
                let ih = rng.gen_range(200..380).min(ph as i32 - y - 220);
                if ih > 120 {
                    let ix = mx + body_w - iw;
                    let iy = y;
                    draw_plate(&mut rng, &mut page, pw, ix, iy, iw, ih, ink_level);
                    add_block("figure", &[[ix, iy, ix + iw, iy + ih]], blocks.len(), &mut blocks);
                    let mut occ_bottom = iy + ih;
                    if let Some(p) = place_line(&mut page, pw, ph, font, texts, &mut rng, ix, iy + ih + 6, iw as usize, 16.0, ink_level, 0) {
                        occ_bottom = p.bbox[3];
                        let id = add_block("caption", &[p.bbox], blocks.len(), &mut blocks);
                        lines.push(LineGT { block: id, bbox: p.bbox, text: p.text });
                    }
                    Some((ix, iy, occ_bottom))
                } else {
                    None
                }
            } else {
                None
            };
            // flowed paragraphs: ragged-right (place_line trims to fit -> varying widths), tight
            // leading; the body wraps to the LEFT of the infobox column (box + caption) while it lasts,
            // then spans full width once below the caption.
            let ink_h = rng.gen_range(19.0f32..25.0);
            let pitch = (ink_h * rng.gen_range(1.15f32..1.4)).round().max(16.0) as i32;
            let mut body_boxes = Vec::new();
            let bstart = lines.len();
            for _ in 0..rng.gen_range(3..6) {
                for _ in 0..rng.gen_range(3..8) {
                    if y > ph as i32 - 90 {
                        break;
                    }
                    let mut right_edge = mx + body_w;
                    if let Some((ix, iy, occ_bottom)) = ibx {
                        if y + ink_h as i32 >= iy && y < occ_bottom {
                            right_edge = ix - 20;
                        }
                    }
                    let slot = (right_edge - mx).max(140) as usize;
                    if let Some(p) = place_line(&mut page, pw, ph, font, texts, &mut rng, mx, y, slot, ink_h, ink_level, 0) {
                        // underlined link span (~22% of lines), drawn just under the tight ink bbox.
                        if rng.gen_bool(0.22) {
                            let uy = (p.bbox[3] + 2).min(ph as i32 - 2);
                            hrule(&mut page, pw, p.bbox[0], p.bbox[2], uy, ink_level);
                        }
                        body_boxes.push(p.bbox);
                        lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                    }
                    y += pitch;
                }
                y += (pitch as f32 * 0.6) as i32; // paragraph gap
                if y > ph as i32 - 90 {
                    break;
                }
            }
            if !body_boxes.is_empty() {
                let id = add_block("main_text", &body_boxes, blocks.len(), &mut blocks);
                for l in lines[bstart..].iter_mut() {
                    if l.block == usize::MAX {
                        l.block = id;
                    }
                }
            }
        }
        _ => {
            // twocol: page number + two columns + CENTER RULE
            let num = format!("{}", rng.gen_range(3..900));
            if let Some(p) = place_line(&mut page, pw, ph, font, &[num], &mut rng, 0, 50, pw, 20.0, ink_level, 1) {
                let id = add_block("page_header", &[p.bbox], 0, &mut blocks);
                lines.push(LineGT { block: id, bbox: p.bbox, text: p.text });
            }
            // F1 (Fable S13): randomize margin/gutter/body-top + rule presence so twocol pages don't
            // collapse onto one fixed column geometry.
            let mx = (pw as f32 * rng.gen_range(0.06..0.11)) as i32;
            let gap = (pw as f32 * rng.gen_range(0.04..0.09)) as i32;
            let col_w = (pw as i32 - 2 * mx - gap) / 2;
            let ink_h = rng.gen_range(22.0f32..27.0);
            let pitch = (ink_h * rng.gen_range(1.45..1.65)) as i32;
            let n = rng.gen_range(28..36);
            let body_top = rng.gen_range(100..168);
            // center rule — present on ~70% of pages
            let rule_x = mx + col_w + gap / 2;
            if rng.gen_bool(0.7) {
                for y in (body_top - 10).max(0)..(ph as i32 - 90) {
                    page[y as usize * pw + rule_x as usize] = ink_level;
                }
            }
            for (ci, x0) in [mx, mx + col_w + gap].iter().enumerate() {
                let mut y = body_top;
                let mut cboxes = Vec::new();
                let cstart = lines.len();
                for _ in 0..n {
                    if let Some(p) = place_line(&mut page, pw, ph, font, texts, &mut rng, *x0, y, col_w as usize, ink_h, ink_level, 0) {
                        cboxes.push(p.bbox);
                        lines.push(LineGT { block: usize::MAX, bbox: p.bbox, text: p.text });
                    }
                    y += pitch;
                    if y > ph as i32 - 120 {
                        break;
                    }
                }
                if !cboxes.is_empty() {
                    let id = add_block("main_text", &cboxes, 1 + ci, &mut blocks);
                    for l in lines[cstart..].iter_mut() {
                        l.block = id;
                    }
                }
            }
        }
    }

    // web_digital is BORN-DIGITAL: NO compose-time paper tone or scan-physics (F2). Every other
    // grammar gets the gentle paper-tone field.
    if !web {
        page_tone(&mut rng, &mut page, pw, ph);
    }
    // page severity + the SAME registry as strips, at page scope (Photo family incl. stains,
    // stamps, watermarks, streaks, binarize; verso as whole-page ghost; jpeg at finalize). web_digital
    // forces sev=0 so image_ops(Photo) + verso_bleed + jpeg are ALL skipped and the page stays crisp —
    // the born-digital/OOD cell must actually be rendered clean (guide_W3 digital_web). Training-time
    // appearance variety is a separate, degrade-gated concern that deliberately leaves web pages clean.
    let sev = if web {
        0u8
    } else {
        let tot: f64 = severity_weights.iter().sum();
        let mut x = rng.gen::<f64>() * tot;
        let mut s = 3u8;
        for (i, v) in severity_weights.iter().enumerate() {
            x -= v;
            if x <= 0.0 {
                s = i as u8;
                break;
            }
        }
        s
    };
    let mut page_ops: Vec<String> = Vec::new();
    distort::image_ops(&mut rng, &mut page, pw, ph, sev, &mut page_ops, distort::Phase::Photo, false, None, None, ctx);
    if sev > 0 && rng.gen_bool([0.0, 0.15, 0.25, 0.35][sev as usize]) {
        distort::verso_bleed(&mut rng, &mut page, pw, ph, sev, None, &mut page_ops, None);
    }
    let bytes = distort::finalize(&mut rng, &page, pw, ph, sev, false, &mut page_ops);
    let img = image::GrayImage::from_raw(pw as u32, ph as u32, bytes).context("page image")?;

    // S13 fix: clamp every GT box to the page and DROP any that fell entirely off-page. A line placed
    // past the bottom margin (top >= ph) has no ink on the rendered image, so its label would be a
    // phantom; a partially-off box is clamped to what the image actually shows. This also removes the
    // overlay() out-of-bounds panic surfaced by the 40k pages_v1 build (a kept box now has top <= ph-2).
    let clamp_box = |b: [i32; 4]| -> Option<[i32; 4]> {
        let x0 = b[0].clamp(0, pw as i32);
        let y0 = b[1].clamp(0, ph as i32);
        let x1 = b[2].clamp(0, pw as i32);
        let y1 = b[3].clamp(0, ph as i32);
        (x1 - x0 >= 2 && y1 - y0 >= 2).then_some([x0, y0, x1, y1])
    };
    let lines: Vec<LineGT> = lines
        .into_iter()
        .filter_map(|mut l| {
            l.bbox = clamp_box(l.bbox)?;
            Some(l)
        })
        .collect();
    let blocks: Vec<BlockGT> = blocks
        .into_iter()
        .filter_map(|mut b| {
            b.bbox = clamp_box(b.bbox)?;
            Some(b)
        })
        .collect();
    Ok((
        img,
        PageGT {
            grammar: grammar.into(),
            split: page_split(seed).into(),
            source: stream.key.clone(),
            lang: stream.lang.clone(),
            width: pw,
            height: ph,
            severity: sev,
            page_ops,
            blocks,
            lines,
        },
    ))
}

/// Draw GT boxes on a copy (blocks dark 3px, lines mid 1px) for eyeball QA.
pub fn overlay(img: &image::GrayImage, gt: &PageGT) -> image::GrayImage {
    let mut o = img.clone();
    let (w, h) = (o.width() as i32, o.height() as i32);
    let mut rect = |b: &[i32; 4], v: u8, t: i32| {
        for dt in 0..t {
            for x in (b[0] - dt).max(0)..(b[2] + dt).min(w) {
                for &y in &[(b[1] - dt).clamp(0, h - 1), (b[3] + dt).clamp(0, h - 1)] {
                    o.put_pixel(x as u32, y as u32, image::Luma([v]));
                }
            }
            for y in (b[1] - dt).max(0)..(b[3] + dt).min(h) {
                for &x in &[(b[0] - dt).clamp(0, w - 1), (b[2] + dt).clamp(0, w - 1)] {
                    o.put_pixel(x as u32, y as u32, image::Luma([v]));
                }
            }
        }
    };
    for l in &gt.lines {
        rect(&l.bbox, 120, 1);
    }
    for b in &gt.blocks {
        rect(&b.bbox, 0, 3);
    }
    o
}

/// min ink/bg contrast inside a line box on the FINAL image (0..1). Used by the page audit's
/// per-line contrast floor (S9 plan f).
fn line_contrast(img: &image::GrayImage, b: &[i32; 4]) -> f32 {
    let (w, h) = (img.width() as i32, img.height() as i32);
    let (mut lo, mut hi) = (255u8, 0u8);
    let mut any = false;
    for y in b[1].max(0)..b[3].min(h) {
        for x in b[0].max(0)..b[2].min(w) {
            let v = img.get_pixel(x as u32, y as u32).0[0];
            lo = lo.min(v);
            hi = hi.max(v);
            any = true;
        }
    }
    if !any {
        return 1.0;
    }
    (hi - lo) as f32 / 255.0
}

/// Per-page contribution to the run audit (merged across the rayon page loop).
#[derive(Default)]
struct PageStat {
    grammar: String,
    split: String,
    lang: String,
    class_counts: BTreeMap<String, usize>,
    lines: usize,
    lines_below_contrast: usize,
}

/// Run-level page audit (S9 plan f): realized grammar frequencies vs configured weights, block
/// class marginals, split-band distribution, per-line contrast-floor breaches.
#[derive(Serialize, Default)]
pub struct PageAudit {
    pub pages: usize,
    pub forced_grammar: Option<String>,
    pub grammar_counts: BTreeMap<String, usize>,
    pub grammar_weights_expected: BTreeMap<String, f64>,
    pub class_marginals: BTreeMap<String, usize>,
    pub lang_counts: BTreeMap<String, usize>,
    pub split_counts: BTreeMap<String, usize>,
    pub lines_total: usize,
    pub lines_below_contrast: usize,
    pub contrast_floor: f32,
    pub band_ok: bool,
    pub grammar_weights_ok: bool,
    pub notes: Vec<String>,
}

pub fn compose_run(
    recipe: &Recipe,
    streams: &[Stream],
    out: &str,
    n: usize,
    forced_grammar: Option<&str>,
) -> Result<()> {
    std::fs::create_dir_all(out)?;
    anyhow::ensure!(!streams.is_empty(), "no text streams");
    let fonts = FontPool::load(&recipe.fonts.dir, &recipe.fonts.held_out)?;
    let ctx = crate::build::load_op_ctx(recipe);
    let floor = recipe.ink_contrast_floor;

    let stats: Vec<Result<PageStat>> = (0..n)
        .into_par_iter()
        .map(|i| -> Result<PageStat> {
            let seed = recipe.seed ^ ((i as u64) << 4);
            // coherent stream per page (page-seed-hashed pick).
            let si = (xxh3_64_with_seed(&seed.to_le_bytes(), STREAM_SALT) % streams.len() as u64) as usize;
            let stream = &streams[si];
            // pick the grammar, then route it to be language-coherent with the stream (a non-Greek
            // stream never draws a Greek-furniture grammar). A forced grammar (dev/A-B runs) stays
            // literal — the caller asked for exactly that arm.
            let g = match forced_grammar {
                Some(fg) => fg,
                None => resolve_grammar(pick_grammar(seed), &stream.lang, seed),
            };
            let (img, gt) = compose_page(g, seed, stream, &fonts, &ctx, &recipe.severity_weights)?;
            img.save(format!("{out}/page_{i:04}_{g}.png"))?;
            std::fs::write(format!("{out}/page_{i:04}_{g}.json"), serde_json::to_string_pretty(&gt)?)?;
            overlay(&img, &gt).save(format!("{out}/page_{i:04}_{g}_overlay.png"))?;
            let mut st = PageStat { grammar: g.into(), split: gt.split.clone(), lang: gt.lang.clone(), ..Default::default() };
            st.lines = gt.lines.len();
            for l in &gt.lines {
                if line_contrast(&img, &l.bbox) < floor {
                    st.lines_below_contrast += 1;
                }
            }
            for b in &gt.blocks {
                *st.class_counts.entry(b.class.clone()).or_default() += 1;
            }
            Ok(st)
        })
        .collect();

    let mut audit = PageAudit { contrast_floor: floor, forced_grammar: forced_grammar.map(String::from), ..Default::default() };
    let tot_w: f64 = GRAMMARS.iter().map(|(_, w)| w).sum();
    for (g, w) in GRAMMARS {
        audit.grammar_weights_expected.insert((*g).into(), w / tot_w);
    }
    for s in stats {
        let s = s?;
        audit.pages += 1;
        *audit.grammar_counts.entry(s.grammar).or_default() += 1;
        *audit.split_counts.entry(s.split).or_default() += 1;
        *audit.lang_counts.entry(s.lang).or_default() += 1;
        audit.lines_total += s.lines;
        audit.lines_below_contrast += s.lines_below_contrast;
        for (c, n) in s.class_counts {
            *audit.class_marginals.entry(c).or_default() += n;
        }
    }
    // band check: reserved ~1.5%, val ~4.5% (loose bounds; only meaningful at n>=200).
    let frac = |k: &str| *audit.split_counts.get(k).unwrap_or(&0) as f64 / audit.pages.max(1) as f64;
    audit.band_ok = if audit.pages >= 200 {
        (0.003..=0.045).contains(&frac("reserved")) && (0.02..=0.09).contains(&frac("val"))
    } else {
        audit.notes.push(format!("band check informational (n={} < 200)", audit.pages));
        true
    };
    // grammar-weight check: realized vs expected within 40% relative. Only statistically
    // meaningful at build scale — for a ~6%-weight grammar the expected count is ~120 at n=2000
    // (±48 at 40% tol) vs ~12 at n=200 where Poisson noise dominates. Below the threshold the
    // realized counts are still reported RAW; the pass/fail assertion is just deferred.
    audit.grammar_weights_ok = if forced_grammar.is_some() || audit.pages < 2000 {
        if forced_grammar.is_none() {
            audit.notes.push(format!("grammar-weight check informational (n={} < 2000)", audit.pages));
        }
        true
    } else {
        let mut ok = true;
        for (g, ew) in &audit.grammar_weights_expected {
            let rw = *audit.grammar_counts.get(g).unwrap_or(&0) as f64 / audit.pages as f64;
            if (rw - ew).abs() > 0.4 * ew.max(0.02) {
                ok = false;
                audit.notes.push(format!("grammar {g}: realized {rw:.3} vs expected {ew:.3}"));
            }
        }
        ok
    };
    std::fs::write(format!("{out}/page_audit.json"), serde_json::to_string_pretty(&audit)?)?;
    eprintln!(
        "[compose] {} pages | grammars {:?} | splits {:?} | classes {:?} | lines {} ({} below contrast {:.2}) | band_ok {} weights_ok {}",
        audit.pages, audit.grammar_counts, audit.split_counts, audit.class_marginals,
        audit.lines_total, audit.lines_below_contrast, floor, audit.band_ok, audit.grammar_weights_ok
    );
    Ok(())
}

/// pool lines -> COHERENT streams grouped by source_dataset (one language/register per stream).
/// Each stream's dominant script_class is its `lang`. Streams too small to fill a page are dropped.
pub fn pool_streams(pool: &[crate::corpus::PoolLine]) -> Vec<Stream> {
    let mut by_src: BTreeMap<String, (Vec<String>, BTreeMap<String, usize>)> = BTreeMap::new();
    for l in pool {
        if !(25..110).contains(&l.gt_nfd.chars().count()) {
            continue;
        }
        let e = by_src.entry(l.source_dataset.clone()).or_default();
        e.0.push(Codec::render_form(&l.gt_nfd));
        *e.1.entry(l.script_class.clone()).or_default() += 1;
    }
    by_src
        .into_iter()
        .filter(|(_, (t, _))| t.len() >= 40) // enough lines to fill a dense page without heavy reuse
        .map(|(key, (texts, cls))| {
            let lang = cls.into_iter().max_by_key(|(_, n)| *n).map(|(c, _)| c).unwrap_or_else(|| "unknown".into());
            Stream { key, lang, texts }
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::distort::OpCtx;

    /// EVERY composer grammar (the S9 arms + the pre-existing book19c/twocol/tablepage/plate). The
    /// default `_` arm is `twocol`; every other string maps to its own arm.
    const ALL_GRAMMARS: &[&str] = &[
        "book19c", "twocol", "tablepage", "plate", "apparatus", "toc",
        "bibliography", "list", "title", "dateline", "handwriting",
        "dense_letterpress", "web_digital",
    ];

    fn load_test_fonts() -> FontPool {
        // crate-relative: cargo test cwd is the crate dir; the fonts live at the repo root.
        let dir = concat!(env!("CARGO_MANIFEST_DIR"), "/../assets/fonts");
        FontPool::load(dir, &[]).expect("load fonts")
    }

    /// A coherent Greek text stream built from the checked-in fixture corpus (real polytonic lines).
    fn fixture_stream() -> Stream {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../data/fixtures/fixture_corpus.jsonl");
        let raw = std::fs::read_to_string(path).expect("read fixture corpus");
        let mut texts = Vec::new();
        for line in raw.lines() {
            if line.trim().is_empty() {
                continue;
            }
            let v: serde_json::Value = serde_json::from_str(line).expect("fixture json");
            if let Some(t) = v.get("text").and_then(|x| x.as_str()) {
                texts.push(t.to_string());
            }
        }
        assert!(texts.len() >= 20, "fixture corpus too small: {} lines", texts.len());
        Stream { key: "fixture_classical".into(), lang: "greek_poly".into(), texts }
    }

    /// Composer GT regression gate (S9 Fable-5 MUST-FIX): compose several pages per grammar and
    /// assert the invariants the certifier verified by hand — every grammar emits >=1 block, no
    /// degenerate or out-of-bounds boxes (blocks OR lines), every line is linked to a valid block
    /// whose box contains it, and split bands are legal. Guards future factory edits.
    #[test]
    fn composer_grammars_emit_valid_gt() {
        let fonts = load_test_fonts();
        let stream = fixture_stream();
        let ctx = OpCtx::default();
        let sw = [0.16f64, 0.20, 0.28, 0.36];
        let (pw, ph) = (1100i32, 1600i32);
        for g in ALL_GRAMMARS {
            for s in 0..14u64 {
                let seed = 0x00C0_FFEE_u64 ^ (s << 8) ^ (g.len() as u64);
                let (_img, gt) = compose_page(g, seed, &stream, &fonts, &ctx, &sw)
                    .unwrap_or_else(|e| panic!("compose {g} seed {seed}: {e}"));
                // grammar name + a legal split band, recorded honestly.
                assert_eq!(gt.grammar, *g, "grammar field mismatch");
                assert!(matches!(gt.split.as_str(), "train" | "val" | "reserved"), "bad split {}", gt.split);
                // >=1 block per page (every grammar emits at least one block).
                assert!(!gt.blocks.is_empty(), "grammar {g} seed {seed}: zero blocks");
                // blocks: ids are a dense 0..n index; boxes non-degenerate + in bounds.
                for (i, b) in gt.blocks.iter().enumerate() {
                    assert_eq!(b.id, i, "grammar {g}: block id {} != index {i}", b.id);
                    let [x0, y0, x1, y1] = b.bbox;
                    assert!(x0 < x1 && y0 < y1, "grammar {g}: degenerate block box {:?}", b.bbox);
                    assert!(x0 >= 0 && y0 >= 0 && x1 <= pw && y1 <= ph, "grammar {g}: OOB block box {:?}", b.bbox);
                }
                // lines: non-degenerate + in bounds + linked to a valid block that contains them.
                for l in &gt.lines {
                    let [x0, y0, x1, y1] = l.bbox;
                    assert!(x0 < x1 && y0 < y1, "grammar {g}: degenerate line box {:?}", l.bbox);
                    assert!(x0 >= 0 && y0 >= 0 && x1 <= pw && y1 <= ph, "grammar {g}: OOB line box {:?}", l.bbox);
                    assert!(l.block != usize::MAX, "grammar {g}: line {:?} not linked to any block", l.bbox);
                    assert!(l.block < gt.blocks.len(), "grammar {g}: line block id {} >= {} blocks", l.block, gt.blocks.len());
                    let bb = gt.blocks[l.block].bbox;
                    assert!(
                        bb[0] <= x0 && bb[1] <= y0 && bb[2] >= x1 && bb[3] >= y1,
                        "grammar {g}: line {:?} escapes its block {:?}", l.bbox, bb
                    );
                }
            }
        }
    }

    /// `page_split` is deterministic and its bands match the 94/4.5/1.5 design (S9 plan f).
    #[test]
    fn page_split_is_deterministic_and_banded() {
        for s in 0..2000u64 {
            assert_eq!(page_split(s), page_split(s), "page_split not deterministic at {s}");
        }
        let n = 40000u64;
        let (mut val, mut res, mut tr) = (0u32, 0u32, 0u32);
        for s in 0..n {
            match page_split(s) {
                "reserved" => res += 1,
                "val" => val += 1,
                "train" => tr += 1,
                other => panic!("illegal band {other}"),
            }
        }
        let f = |c: u32| c as f64 / n as f64;
        // design: reserved 1.5%, val 4.5%, train 94% — loose bounds tolerant of hash noise.
        assert!((0.008..0.024).contains(&f(res)), "reserved frac {} off band", f(res));
        assert!((0.033..0.058).contains(&f(val)), "val frac {} off band", f(val));
        assert!(f(tr) > 0.90, "train frac {} too small", f(tr));
        assert_eq!(res + val + tr, n as u32, "bands must partition");
    }

    /// S9 Fable-5 HIGH: non-Greek streams must never draw a Greek-furniture grammar (per-page
    /// language coherence). resolve_grammar routes them to a neutral grammar; Greek streams and
    /// already-neutral grammars pass through unchanged.
    #[test]
    fn non_greek_streams_route_off_greek_grammars() {
        let non_greek = ["latin", "cyrillic", "cyrillic_latin_cs", "unknown"];
        for lang in non_greek {
            for &g in GREEK_ONLY_GRAMMARS {
                for seed in 0..500u64 {
                    let r = resolve_grammar(g, lang, seed);
                    assert!(
                        NEUTRAL_GRAMMARS.contains(&r),
                        "grammar {g} on {lang} stream routed to non-neutral {r}"
                    );
                    assert!(!GREEK_ONLY_GRAMMARS.contains(&r), "{lang}: still Greek-only {r}");
                }
            }
        }
        // Greek streams keep every grammar; neutral grammars pass through for any lang.
        for lang in ["greek_poly", "greek_mono", "greek_latin_cs", "greek_cyrillic_cs"] {
            for &g in GREEK_ONLY_GRAMMARS {
                assert_eq!(resolve_grammar(g, lang, 42), g, "{lang}: Greek grammar {g} dropped");
            }
        }
        for &g in NEUTRAL_GRAMMARS {
            assert_eq!(resolve_grammar(g, "latin", 42), g, "neutral grammar {g} rerouted");
        }
        // the reroute is deterministic and covers the neutral set across seeds.
        let mut seen = std::collections::BTreeSet::new();
        for seed in 0..2000u64 {
            let r = resolve_grammar("toc", "cyrillic", seed);
            assert_eq!(r, resolve_grammar("toc", "cyrillic", seed), "reroute not deterministic");
            seen.insert(r);
        }
        assert!(seen.len() >= 4, "reroute should spread across neutral grammars, got {seen:?}");
    }

    /// Non-Greek stream pages carry NO hardcoded-Greek furniture in their line GT (the actual
    /// leak the certifier measured). Compose the neutral grammars over a synthetic Latin stream
    /// and assert no Greek codepoints appear in any emitted line text.
    #[test]
    fn non_greek_pages_have_no_greek_furniture() {
        let fonts = load_test_fonts();
        let ctx = OpCtx::default();
        let sw = [0.16f64, 0.20, 0.28, 0.36];
        let latin_words: Vec<String> = (0..80)
            .map(|i| format!("Lorem ipsum dolor sit amet consectetur numero {i}"))
            .collect();
        let stream = Stream { key: "synthetic_latin".into(), lang: "latin".into(), texts: latin_words };
        let is_greek = |c: char| ('\u{0370}'..='\u{03FF}').contains(&c) || ('\u{1F00}'..='\u{1FFF}').contains(&c);
        for g in NEUTRAL_GRAMMARS {
            for s in 0..30u64 {
                let seed = 0x0BAD_F00D_u64 ^ (s << 8) ^ (g.len() as u64);
                let (_img, gt) = compose_page(g, seed, &stream, &fonts, &ctx, &sw)
                    .unwrap_or_else(|e| panic!("compose {g} seed {seed}: {e}"));
                for l in &gt.lines {
                    assert!(
                        !l.text.chars().any(is_greek),
                        "grammar {g} on latin stream leaked Greek furniture in line: {:?}",
                        l.text
                    );
                }
            }
        }
    }
}
