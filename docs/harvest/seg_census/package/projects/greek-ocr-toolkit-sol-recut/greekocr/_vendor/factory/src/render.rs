//! Strip renderer: NFC text -> 48px grayscale f32 (1.0 = white). Shaping = rustybuzz on a SINGLE
//! face (no fallback — a .notdef glyph means the font is ineligible: the TeX-Gyre lesson), raster
//! = ttf-parser outlines through zeno. Emits the ink channel + the top-band y for mark-survival.

use crate::codec::Codec;
use anyhow::{bail, Context, Result};
use rustybuzz::ttf_parser;
use std::collections::HashSet;
use std::path::Path;

pub const STRIP_H: usize = 48;
pub const MIN_W: usize = 64;
pub const MAX_W: usize = 2560;
const PX_PER_EM: f32 = 30.0;
const MARGIN_X: f32 = 6.0;

pub struct FontEntry {
    pub stem: String,
    pub data: Vec<u8>,
    pub sha16: String,
    pub charset: HashSet<char>,
    pub x_height_frac: f32, // x-height / upem
}

pub struct FontPool {
    pub fonts: Vec<FontEntry>,
}

impl FontPool {
    pub fn load(dir: &str, held_out: &[String]) -> Result<FontPool> {
        let mut fonts = Vec::new();
        let mut paths: Vec<_> = std::fs::read_dir(dir)
            .with_context(|| format!("fonts dir {dir}"))?
            .filter_map(|e| e.ok().map(|e| e.path()))
            .filter(|p| {
                p.extension()
                    .and_then(|x| x.to_str())
                    .is_some_and(|x| matches!(x.to_lowercase().as_str(), "ttf" | "otf"))
            })
            .collect();
        paths.sort();
        for p in paths {
            let stem = p.file_stem().and_then(|s| s.to_str()).unwrap_or("").to_string();
            if held_out.iter().any(|h| h == &stem) {
                continue;
            }
            match FontEntry::load(&p, stem.clone()) {
                Ok(f) => fonts.push(f),
                Err(e) => eprintln!("[fonts] SKIP {stem}: {e}"),
            }
        }
        if fonts.is_empty() {
            bail!("no usable fonts in {dir}");
        }
        Ok(FontPool { fonts })
    }

    /// All font stems (ttf/otf) present in `dir`, sorted. Used to INVERT `held_out` for the
    /// transfer-dev render (render with the held-out trio only — prereg_t1 §6a).
    pub fn stems_in(dir: &str) -> Result<Vec<String>> {
        let mut stems: Vec<String> = std::fs::read_dir(dir)
            .with_context(|| format!("fonts dir {dir}"))?
            .filter_map(|e| e.ok().map(|e| e.path()))
            .filter(|p| {
                p.extension()
                    .and_then(|x| x.to_str())
                    .is_some_and(|x| matches!(x.to_lowercase().as_str(), "ttf" | "otf"))
            })
            .filter_map(|p| p.file_stem().and_then(|s| s.to_str()).map(|s| s.to_string()))
            .collect();
        stems.sort();
        Ok(stems)
    }

    /// Fonts whose cmap covers every codepoint of the NFC render string (strict coverage gate).
    pub fn eligible(&self, nfc: &str) -> Vec<usize> {
        let need: HashSet<char> = nfc.chars().filter(|c| *c != ' ').collect();
        self.fonts
            .iter()
            .enumerate()
            .filter(|(_, f)| need.iter().all(|c| f.charset.contains(c)))
            .map(|(i, _)| i)
            .collect()
    }
}

impl FontEntry {
    fn load(path: &Path, stem: String) -> Result<FontEntry> {
        let data = std::fs::read(path)?;
        let face = ttf_parser::Face::parse(&data, 0).map_err(|e| anyhow::anyhow!("parse: {e}"))?;
        let upem = face.units_per_em() as f32;
        let mut charset = HashSet::new();
        if let Some(sub) = face.tables().cmap {
            for t in sub.subtables {
                if t.is_unicode() {
                    t.codepoints(|cp| {
                        if let Some(c) = char::from_u32(cp) {
                            charset.insert(c);
                        }
                    });
                }
            }
        }
        let x_height = face
            .x_height()
            .map(|x| x as f32 / upem)
            .unwrap_or(0.48);
        use sha2::{Digest, Sha256};
        let sha16 = format!("{:x}", Sha256::digest(&data))[..16].to_string();
        Ok(FontEntry { stem, data, sha16, charset, x_height_frac: x_height })
    }
}

struct ZenoOutline {
    cmds: Vec<zeno::Command>,
    scale: f32,
    dx: f32,
    dy: f32, // baseline y in px, y-down output
}

impl ttf_parser::OutlineBuilder for ZenoOutline {
    fn move_to(&mut self, x: f32, y: f32) {
        self.cmds.push(zeno::Command::MoveTo(self.pt(x, y)));
    }
    fn line_to(&mut self, x: f32, y: f32) {
        self.cmds.push(zeno::Command::LineTo(self.pt(x, y)));
    }
    fn quad_to(&mut self, x1: f32, y1: f32, x: f32, y: f32) {
        self.cmds.push(zeno::Command::QuadTo(self.pt(x1, y1), self.pt(x, y)));
    }
    fn curve_to(&mut self, x1: f32, y1: f32, x2: f32, y2: f32, x: f32, y: f32) {
        self.cmds
            .push(zeno::Command::CurveTo(self.pt(x1, y1), self.pt(x2, y2), self.pt(x, y)));
    }
    fn close(&mut self) {
        self.cmds.push(zeno::Command::Close);
    }
}

impl ZenoOutline {
    fn pt(&self, x: f32, y: f32) -> zeno::Vector {
        zeno::Vector::new(self.dx + x * self.scale, self.dy - y * self.scale)
    }
}

/// Per-combining-mark geometry for automatic label repair (detector-crop). Rows are in the strip's
/// pixel frame (same as `ink`). Computed only when `want_marks` (cropping on) — see `compute_marks`.
#[derive(Clone)]
pub struct MarkGeom {
    /// BYTE offset of this combining mark within the row's `gt_nfd` (what repair drops; `drop_marks`
    /// filters on `char_indices()` byte positions — NOT a char index).
    pub gt_idx: usize,
    /// top mark (accent, cut by a TOP crop) vs bottom mark (ypogegrammeni/cedilla, cut by a BOTTOM crop).
    pub is_top: bool,
    /// first strip row of the mark's own ink (upright render frame); the profile spans [row0, row0+own.len()).
    pub row0: usize,
    /// per-row ISOLATED (own) ink mass, `own[i]` = the mark's own base-diff'd ink in strip row `row0+i`.
    /// Crop survival is measured against THIS profile, so it can never be propped up by never-cut base
    /// body ink (F1 fix — the old rectangular column window bled into base rows and floored the ratio).
    pub own: Vec<f32>,
}

pub struct RenderedStrip {
    /// ink alpha in [0,1], row-major H x W (1 = full ink)
    pub ink: Vec<f32>,
    pub w: usize,
    /// y (row) above which top-marks live for this strip (x-height top minus pad); mark band = rows [0, y)
    pub mark_band_y: usize,
    pub has_top_marks: bool,
    /// y (row) below which bottom-marks live (baseline plus pad); bottom band = rows [bot_band_y, H)
    pub bot_band_y: usize,
    pub has_bottom_marks: bool,
    /// per-mark geometry for the automatic label-repair; empty unless `want_marks`.
    pub marks: Vec<MarkGeom>,
}

/// Shape + rasterize `nfc` with font `f`. `tracking_em` adds letterspacing (gesperrt);
/// `target_ink_h` = ink-band height in px (crop-normalized contract, ~40); `y_jitter` = vertical
/// placement jitter in px (detector-crop interface-match augmentation).
pub fn render_ink(
    f: &FontEntry,
    nfc: &str,
    tracking_em: f32,
    target_ink_h: f32,
    y_jitter: f32,
    gt_nfd: &str,
    want_marks: bool,
) -> Result<RenderedStrip> {
    let face = ttf_parser::Face::parse(&f.data, 0).map_err(|e| anyhow::anyhow!("{e}"))?;
    let mut rb = rustybuzz::Face::from_slice(&f.data, 0).context("rustybuzz face")?;
    rb.set_pixels_per_em(Some((PX_PER_EM as u16, PX_PER_EM as u16)));
    let upem = face.units_per_em() as f32;
    let scale = PX_PER_EM / upem;
    let tracking_px = tracking_em * PX_PER_EM;

    let mut buf = rustybuzz::UnicodeBuffer::new();
    buf.push_str(nfc);
    let glyphs = rustybuzz::shape(&rb, &[], buf);
    let infos = glyphs.glyph_infos();
    let poss = glyphs.glyph_positions();
    if infos.iter().any(|i| i.glyph_id == 0) {
        bail!("notdef glyph — font not eligible for this text");
    }

    // pen positions in px (y-up for now), then find ink bbox to place baseline.
    let mut placed: Vec<(u16, f32, f32)> = Vec::with_capacity(infos.len());
    let mut pen_x = 0f32;
    for (i, p) in infos.iter().zip(poss) {
        placed.push((
            i.glyph_id as u16,
            pen_x + p.x_offset as f32 * scale,
            p.y_offset as f32 * scale,
        ));
        let adv = p.x_advance as f32 * scale;
        pen_x += adv + tracking_px;
    }
    // ink bbox in y (font units via glyph bboxes)
    let mut y_max = f32::MIN;
    let mut y_min = f32::MAX;
    for (gid, _, gy) in &placed {
        if let Some(bb) = face.glyph_bounding_box(ttf_parser::GlyphId(*gid)) {
            y_max = y_max.max(*gy + bb.y_max as f32 * scale);
            y_min = y_min.min(*gy + bb.y_min as f32 * scale);
        }
    }
    if y_max <= y_min {
        bail!("empty ink");
    }
    let ink_h = y_max - y_min;
    // CROP-NORMALIZED fit (2026-07-06, interface-match): scale so the ink band fills
    // target_ink_h px of the 48px strip — the SAME geometry the inference pipeline produces when
    // it resizes a detector line band to 48px (pipeline/strips.py). Em-driven sizing made
    // x-height-only lines render ~2-3x smaller than their inference crops. px_per_em clamped to
    // [14, 64] so degenerate strips (single punct) stay sane. target/jitter come from the recipe.
    let mut fit = (target_ink_h / ink_h).clamp(14.0 / PX_PER_EM, 64.0 / PX_PER_EM);
    fit = fit.min((STRIP_H as f32 - 2.0) / ink_h); // never exceed the canvas whatever the clamps
    // LETTERBOX rule for long lines (shared with pipeline/strips.py): if the strip would exceed
    // MAX_W, shrink the ink (never squeeze aspect, never clip) down to a readability floor.
    let w_est = pen_x * fit + 2.0 * MARGIN_X;
    if w_est > MAX_W as f32 {
        fit *= (MAX_W as f32 - 2.0 * MARGIN_X) / (pen_x * fit);
        if ink_h * fit < 14.0 {
            bail!("too wide (letterbox floor)"); // pathological over-length — drop, accounted
        }
    }
    let scale2 = scale * fit;
    let pen_scale = fit;
    // baseline so that [y_min, y_max] is vertically centered, plus interface jitter — clamped so
    // ink stays inside the canvas (the sibling program's canvas-clipping bug family, 2026-07-06)
    let centered = (STRIP_H as f32 + (y_max + y_min) * pen_scale) / 2.0;
    // clamp the baseline so ink stays on-canvas. When the glyph fills the whole strip (e.g. a
    // full-height drop-cap initial), lo can exceed hi by a float epsilon — guard lo<=hi so
    // `clamp` never panics (pins the baseline to hi in that degenerate case).
    let lo_b = y_max * pen_scale + 1.0;
    let hi_b = STRIP_H as f32 - 1.0 + y_min * pen_scale;
    let baseline = (centered + y_jitter).clamp(lo_b.min(hi_b), hi_b);

    let w = (pen_x * pen_scale + 2.0 * MARGIN_X).ceil() as usize;
    if w > MAX_W {
        bail!("too wide ({w}px)");
    }
    let w = w.max(MIN_W);
    let mut ink = vec![0f32; STRIP_H * w];

    for (gid, gx, gy) in &placed {
        let mut ob = ZenoOutline {
            cmds: Vec::new(),
            scale: scale2,
            dx: MARGIN_X + gx * pen_scale,
            dy: baseline - gy * pen_scale,
        };
        if face.outline_glyph(ttf_parser::GlyphId(*gid), &mut ob).is_none() {
            continue; // space/blank glyph
        }
        let mut mask = zeno::Mask::new(&ob.cmds);
        mask.style(zeno::Fill::NonZero);
        let (data, place) = mask.render();
        for yy in 0..place.height as usize {
            let oy = place.top as isize + yy as isize;
            if oy < 0 || oy >= STRIP_H as isize {
                continue;
            }
            for xx in 0..place.width as usize {
                let ox = place.left as isize + xx as isize;
                if ox < 0 || ox >= w as isize {
                    continue;
                }
                let a = data[yy * place.width as usize + xx] as f32 / 255.0;
                let px = &mut ink[oy as usize * w + ox as usize];
                *px = (*px + a * (1.0 - *px)).min(1.0);
            }
        }
    }

    // top-mark band: rows above the x-height line (in px from baseline), minus a small pad.
    let x_top = baseline - f.x_height_frac * PX_PER_EM * pen_scale;
    let mark_band_y = (x_top - 2.0).max(0.0) as usize;
    // bottom-mark band: rows below the baseline (ypogegrammeni/cedilla), plus a small pad.
    let bot_band_y = (baseline + 2.0).clamp(0.0, STRIP_H as f32) as usize;
    let (has_top_marks, has_bottom_marks) = {
        use unicode_normalization::UnicodeNormalization;
        (nfc.nfd().any(Codec::is_top_mark), nfc.nfd().any(Codec::is_bottom_mark))
    };
    // per-mark geometry (cost-gated): re-render each accented cluster in isolation at THIS strip's
    // scale/baseline and isolate each mark's OWN ink (base-diff) as a per-row mass profile — the crop then
    // measures survival against that profile, never the never-cut base body (F1 fix; no columns needed).
    let marks = if want_marks && (has_top_marks || has_bottom_marks) {
        compute_marks(f, gt_nfd, scale2, baseline)
    } else {
        Vec::new()
    };
    Ok(RenderedStrip { ink, w, mark_band_y, has_top_marks, bot_band_y, has_bottom_marks, marks })
}

/// Isolate each combining mark's ink row-span for the automatic label-repair. For each `gt_nfd` cluster
/// (base + trailing combining marks), rasterize the base and each incremental NFC prefix
/// (base, base+m1, base+m1+m2 …) at the strip's `scale2`/`baseline` and diff consecutive masks →
/// the ink each mark ADDS. `scale2 = scale·fit` (font-units→px), `baseline` = px baseline row.
fn compute_marks(f: &FontEntry, gt_nfd: &str, scale2: f32, baseline: f32) -> Vec<MarkGeom> {
    let mut out = Vec::new();
    let Ok(face) = ttf_parser::Face::parse(&f.data, 0) else { return out };
    let Some(mut rb) = rustybuzz::Face::from_slice(&f.data, 0) else { return out };
    rb.set_pixels_per_em(Some((PX_PER_EM as u16, PX_PER_EM as u16))); // F9: match the main render's GPOS ppem
    // font-units → px: render_ink's net position multiplier is scale·fit = scale2 (positions and
    // outlines share it), so shaped x_offset/x_advance (font units) scale by scale2 exactly like outlines.
    let scale_units = scale2;
    // rasterize an NFC string in isolation → boolean ink mask on a tall canvas sharing `baseline`.
    let render_mask = |s: &str| -> Option<Vec<bool>> {
        if s.is_empty() {
            return Some(vec![false; STRIP_H * ISO_W]);
        }
        let mut buf = rustybuzz::UnicodeBuffer::new();
        buf.push_str(s);
        let g = rustybuzz::shape(&rb, &[], buf);
        if g.glyph_infos().iter().any(|i| i.glyph_id == 0) {
            return None; // notdef — cannot isolate; skip this cluster
        }
        let mut m = vec![false; STRIP_H * ISO_W];
        let mut pen = 0f32;
        for (gi, gp) in g.glyph_infos().iter().zip(g.glyph_positions()) {
            let gx = pen + gp.x_offset as f32 * scale_units;
            let gy = gp.y_offset as f32 * scale_units;
            let mut ob = ZenoOutline { cmds: Vec::new(), scale: scale2, dx: ISO_MARGIN + gx, dy: baseline - gy };
            if face.outline_glyph(ttf_parser::GlyphId(gi.glyph_id as u16), &mut ob).is_some() {
                let mut mask = zeno::Mask::new(&ob.cmds);
                mask.style(zeno::Fill::NonZero);
                let (data, place) = mask.render();
                for yy in 0..place.height as usize {
                    let oy = place.top as isize + yy as isize;
                    if oy < 0 || oy >= STRIP_H as isize { continue; }
                    for xx in 0..place.width as usize {
                        let ox = place.left as isize + xx as isize;
                        if ox < 0 || ox >= ISO_W as isize { continue; }
                        if data[yy * place.width as usize + xx] > 32 {
                            m[oy as usize * ISO_W + ox as usize] = true;
                        }
                    }
                }
            }
            pen += gp.x_advance as f32 * scale_units;
        }
        Some(m)
    };
    // dilate a mask by 1px (4-neighbour) so base-diff ignores antialiasing seams at the join.
    let dilate = |m: &[bool]| -> Vec<bool> {
        let mut d = m.to_vec();
        for y in 0..STRIP_H {
            for x in 0..ISO_W {
                if m[y * ISO_W + x] {
                    if y > 0 { d[(y - 1) * ISO_W + x] = true; }
                    if y + 1 < STRIP_H { d[(y + 1) * ISO_W + x] = true; }
                    if x > 0 { d[y * ISO_W + x - 1] = true; }
                    if x + 1 < ISO_W { d[y * ISO_W + x + 1] = true; }
                }
            }
        }
        d
    };
    for (base_idx, cl) in cluster_ranges(gt_nfd) {
        let chars: Vec<char> = cl.chars().collect();
        if chars.len() < 2 { continue; } // base only, no marks
        let is_mk = |c: char| Codec::is_top_mark(c) || Codec::is_bottom_mark(c);
        // incremental prefixes: [base], [base,m1], [base,m1,m2] …, each composed to NFC for rendering.
        let mut prev = match render_mask(&nfc_of(&chars[..1])) {
            Some(m) => dilate(&m),
            None => {
                // notdef base: the whole cluster is undropable — count EVERY mark it carries (F3c).
                MARK_SKIPS.fetch_add(chars[1..].iter().filter(|c| is_mk(**c)).count(), Ordering::Relaxed);
                continue;
            }
        };
        let mut char_off = base_idx + chars[0].len_utf8();
        for k in 1..chars.len() {
            let mk = chars[k];
            let cur = match render_mask(&nfc_of(&chars[..=k])) {
                Some(m) => m,
                None => {
                    // notdef prefix: this mark + every remaining mark in the cluster are undropable (F3c).
                    MARK_SKIPS.fetch_add(chars[k..].iter().filter(|c| is_mk(**c)).count(), Ordering::Relaxed);
                    break;
                }
            };
            // per-row ISOLATED ink: pixels where `cur` has ink that `prev` (dilated) did not → mark's own ink
            let mut row_own = [0f32; STRIP_H];
            for y in 0..STRIP_H {
                let mut c = 0f32;
                for x in 0..ISO_W {
                    if cur[y * ISO_W + x] && !prev[y * ISO_W + x] { c += 1.0; }
                }
                row_own[y] = c;
            }
            let r0 = (0..STRIP_H).find(|&y| row_own[y] > 0.0);
            let r1 = (0..STRIP_H).rev().find(|&y| row_own[y] > 0.0).map(|y| y + 1);
            match (r0, r1) {
                (Some(r0), Some(r1)) if is_mk(mk) => out.push(MarkGeom {
                    gt_idx: char_off,
                    is_top: Codec::is_top_mark(mk),
                    row0: r0,
                    own: row_own[r0..r1].to_vec(),
                }),
                _ if is_mk(mk) => { MARK_SKIPS.fetch_add(1, Ordering::Relaxed); } // empty base-diff: undropable
                _ => {}
            }
            prev = dilate(&cur);
            char_off += mk.len_utf8();
        }
    }
    out
}

/// Clusters compute_marks could not isolate (notdef base / empty base-diff) — those marks are undropable
/// under the crop-repair. Empirically 0 on the current pool; build.rs surfaces it so font-pool drift is visible (F9).
pub static MARK_SKIPS: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);
use std::sync::atomic::Ordering;

const ISO_W: usize = 96;      // isolation canvas width (a single cluster fits comfortably)
const ISO_MARGIN: f32 = 24.0; // left margin inside the isolation canvas

/// NFC of a char slice (fonts carry precomposed glyphs — match the strip's render form).
fn nfc_of(chars: &[char]) -> String {
    use unicode_normalization::UnicodeNormalization;
    chars.iter().collect::<String>().nfc().collect()
}

/// Iterate `gt_nfd` as clusters (a base char plus its trailing combining marks). Yields
/// (byte_index_of_base, cluster_str).
fn cluster_ranges(gt_nfd: &str) -> Vec<(usize, String)> {
    let mut out: Vec<(usize, String)> = Vec::new();
    for (i, c) in gt_nfd.char_indices() {
        if Codec::is_mark(c) && !out.is_empty() {
            out.last_mut().unwrap().1.push(c);
        } else {
            out.push((i, c.to_string()));
        }
    }
    out
}

/// Ink mass in the top-mark band (the accent-survival numerator/denominator probe).
pub fn band_ink(strip: &[f32], w: usize, band_y: usize) -> f32 {
    strip[..band_y.min(STRIP_H) * w].iter().sum()
}

/// Render a SINGLE initial `ch` at ink height ~`cap_h` px on a TIGHT canvas whose height tracks the
/// cap (NOT clamped to the 48px strip) — so a drop-cap initial rasterizes as a true multi-line
/// figure (2-3 body lines) rather than a 1-line strip glyph. Returns (ink alpha in [0,1] row-major
/// h×w, w, h). Errors (notdef / blank / empty) let the caller try another candidate initial.
pub fn render_cap(f: &FontEntry, ch: &str, cap_h: f32) -> Result<(Vec<f32>, usize, usize)> {
    let face = ttf_parser::Face::parse(&f.data, 0).map_err(|e| anyhow::anyhow!("{e}"))?;
    let mut rb = rustybuzz::Face::from_slice(&f.data, 0).context("rustybuzz face")?;
    rb.set_pixels_per_em(Some((PX_PER_EM as u16, PX_PER_EM as u16)));
    let upem = face.units_per_em() as f32;
    let scale = PX_PER_EM / upem;

    let mut buf = rustybuzz::UnicodeBuffer::new();
    buf.push_str(ch);
    let glyphs = rustybuzz::shape(&rb, &[], buf);
    let infos = glyphs.glyph_infos();
    if infos.is_empty() || infos.iter().any(|i| i.glyph_id == 0) {
        bail!("notdef glyph — font not eligible for this cap");
    }
    let gid = infos[0].glyph_id as u16;
    let bb = face
        .glyph_bounding_box(ttf_parser::GlyphId(gid))
        .ok_or_else(|| anyhow::anyhow!("no glyph bbox"))?;
    let ink_h_u = (bb.y_max - bb.y_min) as f32 * scale;
    if ink_h_u <= 0.0 {
        bail!("empty cap ink");
    }
    // scale the glyph so its ink band fills cap_h px (multi-line), tight canvas around it.
    let fit = cap_h / ink_h_u;
    let scale2 = scale * fit;
    let x_min = bb.x_min as f32 * scale2;
    let glyph_w = (bb.x_max - bb.x_min) as f32 * scale2;
    let y_max = bb.y_max as f32 * scale2;
    let w = (glyph_w + 2.0 * MARGIN_X).ceil().max(MIN_W as f32) as usize;
    let h = (cap_h + 2.0).ceil() as usize;
    let mut ink = vec![0f32; w * h];
    let mut ob = ZenoOutline {
        cmds: Vec::new(),
        scale: scale2,
        dx: MARGIN_X - x_min,      // glyph left -> MARGIN_X
        dy: y_max + 1.0,           // glyph top  -> ~1px from the canvas top
    };
    if face.outline_glyph(ttf_parser::GlyphId(gid), &mut ob).is_none() {
        bail!("blank cap glyph");
    }
    let mut mask = zeno::Mask::new(&ob.cmds);
    mask.style(zeno::Fill::NonZero);
    let (data, place) = mask.render();
    for yy in 0..place.height as usize {
        let oy = place.top as isize + yy as isize;
        if oy < 0 || oy >= h as isize {
            continue;
        }
        for xx in 0..place.width as usize {
            let ox = place.left as isize + xx as isize;
            if ox < 0 || ox >= w as isize {
                continue;
            }
            let a = data[yy * place.width as usize + xx] as f32 / 255.0;
            let px = &mut ink[oy as usize * w + ox as usize];
            *px = (*px + a * (1.0 - *px)).min(1.0);
        }
    }
    Ok((ink, w, h))
}

#[cfg(test)]
mod probe {
    use super::*;
    use crate::codec::Codec;

    // Gated (CROP_PROBE=1): measures, at the deepest legal top crop over the real font pool, how many
    // truly-cleared accents the own-ink drop decision MASKS (keeps) vs SPURIOUSLY drops, per GEO_ALLOW.
    #[test]
    fn crop_own_ink_masking_probe() {
        if std::env::var("CROP_PROBE").is_err() {
            return;
        }
        let pool = FontPool::load("../assets/fonts", &[]).expect("fonts");
        let texts = [
            "Ἡ ἀξιολόγησις τῆς κρίσεως τῷ ψυχῇ ὁ ῥήγας βαρύ",
            "ἄνθρωπος ᾧ ᾆ ῷ ὧ ἇ ᾅ ῆ ὅ ἄ ἔ ἴ ὄ ὔ ὤ ἁ ἑ ἡ",
            "Θὰ τελειώσω τὰς ἁπλᾶς ταύτας γραμμάς, τὰς ὁποίας θὰ κρίνῃ ὁ ἀναγνώστης",
            "Τόμος τεύχος σελίδες βιβλιογραφία καὶ εὑρετήρια πολυτονικὸν κείμενον",
        ];
        let (mut n_top, mut cleared) = (0u32, 0u32);
        let (mut drops, mut masked, mut spurious) = ([0u32; 3], [0u32; 3], [0u32; 3]);
        for t in texts {
            let gt = Codec::normalize_gt(t);
            let nfc = Codec::render_form(&gt);
            for fi in pool.eligible(&nfc) {
                let f = &pool.fonts[fi];
                let Ok(s) = render_ink(f, &nfc, 0.0, 40.0, 0.0, &gt, true) else { continue };
                let ink_row = |y: usize| (0..s.w).any(|x| s.ink[y * s.w + x] > 0.5);
                let i0 = (0..STRIP_H).find(|&y| ink_row(y)).unwrap_or(0);
                let i1 = (0..STRIP_H).rev().find(|&y| ink_row(y)).map(|y| y + 1).unwrap_or(STRIP_H);
                let tby = s.mark_band_y;
                if tby <= i0 {
                    continue;
                }
                let (a, b) = (tby as f32, i1 as f32); // deepest legal top crop (t_max=1.0)
                let ra = a - (2.0 + 0.10 * (b - a).max(0.0));
                for m in &s.marks {
                    if !m.is_top {
                        continue;
                    }
                    n_top += 1;
                    let total: f32 = m.own.iter().sum::<f32>().max(1e-6);
                    let ret = |ga: f32| -> f32 {
                        m.own.iter().enumerate()
                            .filter(|(i, _)| (m.row0 + i) as f32 >= ra - ga)
                            .map(|(_, v)| v).sum::<f32>() / total
                    };
                    let is_cleared = ret(0.0) < 0.03;
                    if is_cleared {
                        cleared += 1;
                    }
                    let lenient = ret(4.0); // max Geo down-shift: substantial ink here ⇒ maybe-visible
                    for (gi, ga) in [0.0f32, 1.0, 2.0].iter().enumerate() {
                        let r = ret(*ga);
                        if r < 0.03 {
                            drops[gi] += 1;
                            if lenient >= 0.10 {
                                spurious[gi] += 1;
                            }
                        }
                        if is_cleared && r >= 0.03 {
                            masked[gi] += 1;
                        }
                    }
                }
            }
        }
        eprintln!("[crop-probe] top_marks={n_top} truly_cleared={cleared}");
        for (gi, ga) in [0, 1, 2].iter().enumerate() {
            eprintln!("  GEO_ALLOW={ga}: drops={} masked_kept={} spurious_drops={}", drops[gi], masked[gi], spurious[gi]);
        }
    }
}
