//! Distortion engine: ink-stage ops (stroke weight, ink starvation), composition over paper,
//! image-stage ops in a fixed physical order (illumination -> bleed -> photometric -> blur ->
//! noise -> stamp -> geometry -> lowres -> binarize -> jpeg). Severity 0 is clean by design.
//! Registry grounded on the reference 1899 letterpress scan (docs/factory_design.md §3).

use rand::Rng;
use rand_chacha::ChaCha20Rng;

/// Assets available to ops (loaded once per build; empty in unit tests unless provided).
#[derive(Default)]
pub struct OpCtx {
    /// alpha masks (1 = full stamp ink), from recipe.watermarks_dir
    pub watermarks: Vec<(String, Vec<f32>, usize, usize)>, // (name, alpha, w, h)
}

pub struct Style {
    pub bg_type: String,       // flat | gradient | textured
    pub polarity_light: bool,  // light-on-dark strip
    pub severity: u8,
}


fn smooth_field(rng: &mut ChaCha20Rng, w: usize, h: usize, cell: usize, lo: f32, hi: f32) -> Vec<f32> {
    #[allow(non_snake_case)] let H = h;
    // coarse random grid, bilinear-upsampled — cheap low-frequency field
    let gw = w / cell + 2;
    let gh = H / cell + 2;
    let grid: Vec<f32> = (0..gw * gh).map(|_| rng.gen_range(lo..hi)).collect();
    let mut out = vec![0f32; H * w];
    for y in 0..H {
        let fy = y as f32 / cell as f32;
        let y0 = fy as usize;
        let ty = fy - y0 as f32;
        for x in 0..w {
            let fx = x as f32 / cell as f32;
            let x0 = fx as usize;
            let tx = fx - x0 as f32;
            let g = |yy: usize, xx: usize| grid[(yy.min(gh - 1)) * gw + xx.min(gw - 1)];
            let v = g(y0, x0) * (1.0 - tx) * (1.0 - ty)
                + g(y0, x0 + 1) * tx * (1.0 - ty)
                + g(y0 + 1, x0) * (1.0 - tx) * ty
                + g(y0 + 1, x0 + 1) * tx * ty;
            out[y * w + x] = v;
        }
    }
    out
}

fn gaussian_blur(img: &mut [f32], w: usize, h: usize, sigma: f32) {
    #[allow(non_snake_case)] let H = h;
    if sigma < 0.3 {
        return;
    }
    let r = (sigma * 3.0).ceil() as isize;
    let k: Vec<f32> = (-r..=r).map(|i| (-((i * i) as f32) / (2.0 * sigma * sigma)).exp()).collect();
    let s: f32 = k.iter().sum();
    let k: Vec<f32> = k.iter().map(|v| v / s).collect();
    let mut tmp = vec![0f32; img.len()];
    for y in 0..H {
        for x in 0..w {
            let mut acc = 0.0;
            for (j, kv) in k.iter().enumerate() {
                let xx = (x as isize + j as isize - r).clamp(0, w as isize - 1) as usize;
                acc += img[y * w + xx] * kv;
            }
            tmp[y * w + x] = acc;
        }
    }
    for y in 0..H {
        for x in 0..w {
            let mut acc = 0.0;
            for (j, kv) in k.iter().enumerate() {
                let yy = (y as isize + j as isize - r).clamp(0, H as isize - 1) as usize;
                acc += tmp[yy * w + x] * kv;
            }
            img[y * w + x] = acc;
        }
    }
}

fn morph(ink: &mut Vec<f32>, w: usize, h: usize, dilate: bool) {
    #[allow(non_snake_case)] let H = h;
    let src = ink.clone();
    for y in 0..H {
        for x in 0..w {
            let mut v = src[y * w + x];
            for (dy, dx) in [(0i32, 1i32), (0, -1), (1, 0), (-1, 0)] {
                let yy = y as i32 + dy;
                let xx = x as i32 + dx;
                if yy >= 0 && (yy as usize) < H && xx >= 0 && (xx as usize) < w {
                    let n = src[yy as usize * w + xx as usize];
                    v = if dilate { v.max(n * 0.85) } else { v.min(1.0 - (1.0 - n) * 0.85 + 0.0) };
                }
            }
            ink[y * w + x] = if dilate { v } else { v.min(src[y * w + x]) * 0.92 + src[y * w + x] * 0.08 };
        }
    }
}

/// ---- ink stage ----
/// REFERENCES: Augraphy (MIT, ICDAR 2023) InkBleed/InkMottling/Letterpress — the ink-phase model;
/// Kanungo et al., IEEE TPAMI 2000 — boundary pixel-flip degradation (the canonical local model).
pub fn ink_ops(rng: &mut ChaCha20Rng, ink: &mut Vec<f32>, w: usize, h: usize, sev: u8, applied: &mut Vec<String>, force_all: bool, s_override: Option<f32>, only: Option<&str>, letterpress: bool) {
    #[allow(non_snake_case)] let H = h;
    // letterpress cohort: the field-driven ink_transfer_v2 REPLACES the three ink-amount ops
    // (ink_bleed / stroke_loss / ink_starve) — all three just pushed ink up or down, now done
    // coherently by the T/R/P fields. It runs at every severity (incl. s0 ≈ well-printed), before the
    // sev-0 early return. `edge_noise` (below) is KEPT: the model's morphological edges are too clean.
    // Skipped under `only` (single-op isolation for tests).
    if letterpress && only.is_none() {
        ink_transfer_v2(rng, ink, w, H, sev, applied);
    }
    if sev == 0 && !force_all && s_override.is_none() {
        return;
    }
    let s = s_override.unwrap_or(if force_all { 3.0 } else { sev as f32 });
    let want = |n: &str, p: f64, rng: &mut ChaCha20Rng| -> bool {
        match only {
            Some(o) => o == n,
            None => force_all || rng.gen_bool(p),
        }
    };
    // ink bleed: ANISOTROPIC spread beyond the outline (letterpress squash) — direction-weighted,
    // so spill is uneven, not a uniform dilate. (Augraphy InkBleed/Letterpress)
    if !letterpress && want("ink_bleed", (0.18 + 0.10 * s as f64).min(0.55), rng) {
        let wts: [f32; 4] = [
            rng.gen_range(0.3..1.0), // right
            rng.gen_range(0.3..1.0), // left
            rng.gen_range(0.2..0.9), // down
            rng.gen_range(0.2..0.9), // up
        ];
        let gain = 0.55 + 0.15 * s;
        let src = ink.clone();
        for y in 0..H {
            for x in 0..w {
                let mut v = src[y * w + x];
                let dirs = [(0i32, 1i32, 0usize), (0, -1, 1), (1, 0, 2), (-1, 0, 3)];
                for (dy, dx, di) in dirs {
                    let (yy, xx) = (y as i32 + dy, x as i32 + dx);
                    if yy >= 0 && (yy as usize) < H && xx >= 0 && (xx as usize) < w {
                        v = v.max(src[yy as usize * w + xx as usize] * wts[di] * gain);
                    }
                }
                ink[y * w + x] = v.min(1.0);
            }
        }
        applied.push("ink_bleed".into());
    } else if !letterpress && only.is_none() && rng.gen_bool((0.10 + 0.06 * s as f64).min(0.3)) {
        morph(ink, w, h, false);
        applied.push("stroke_loss".into());
    }
    // ink mottling / starvation: MULTI-OCTAVE field — big faint regions + small blotches
    // (the fainter words of the 1899 reference; Augraphy InkMottling)
    if !letterpress && want("ink_starve", (0.12 + 0.12 * s as f64).min(0.5), rng) {
        let s = cap_s("ink_starve", s);
        let f1 = smooth_field(rng, w, h, 48, (1.0 - 0.20 * s).max(0.0), 1.0);
        let f2 = smooth_field(rng, w, h, 10, (1.0 - 0.12 * s).max(0.0), 1.0);
        for i in 0..ink.len() {
            ink[i] *= f1[i] * f2[i];
        }
        applied.push("ink_starve".into());
    }
    // Kanungo boundary flips: erosion holes + accretion specks ON the stroke edges — the
    // characteristic raggedness of real scans that smooth ops can't produce.
    if want("edge_noise", (0.15 + 0.10 * s as f64).min(0.45), rng) {
        let src = ink.clone();
        let p_flip = (0.06 + 0.05 * s as f64).min(0.9);
        for y in 1..H - 1 {
            for x in 1..w - 1 {
                let c = src[y * w + x];
                let grad = (src[y * w + x + 1] - src[y * w + x - 1]).abs()
                    + (src[(y + 1) * w + x] - src[(y - 1) * w + x]).abs();
                if grad > 0.35 && rng.gen_bool(p_flip) {
                    ink[y * w + x] = if c > 0.5 { rng.gen_range(0.0..0.25) } else { rng.gen_range(0.6..0.95) };
                }
            }
        }
        applied.push("edge_noise".into());
    }
}

// ---- ink_transfer_v2 — letterpress field-driven ink model (WS3, ~/letterpress_lab port) ----
// Crisp glyphs -> three independent physical fields (T type-height per-letter / R roller / P pressure)
// -> fade + connect + absent -> emits CRISP ink alpha (1=ink). The scanner (blur/noise/lowres) is the
// shared image stage (do NOT scan here). Spec: ~/letterpress_lab/regimes/ink_transfer_v2.json.

fn gauss1(rng: &mut ChaCha20Rng) -> f32 {
    let u1: f32 = rng.gen_range(1e-6..1.0);
    let u2: f32 = rng.gen_range(0.0..1.0);
    (-2.0 * u1.ln()).sqrt() * (std::f32::consts::TAU * u2).cos()
}

/// Per-letter column runs (each metal sort) by ink-mass valleys.
fn letter_runs(ink: &[f32], w: usize, h: usize) -> Vec<(usize, usize)> {
    let mut runs = Vec::new();
    let mut start: Option<usize> = None;
    for x in 0..w {
        let mut s = 0.0f32;
        for y in 0..h { s += ink[y * w + x]; }
        if s > 0.5 {
            if start.is_none() { start = Some(x); }
        } else if let Some(a) = start {
            runs.push((a, x));
            start = None;
        }
    }
    if let Some(a) = start { runs.push((a, w)); }
    runs
}

/// Clean grayscale morphology, disk SE radius r (max = dilate, min = erode).
fn morph_disk(field: &[f32], w: usize, h: usize, r: usize, dilate: bool) -> Vec<f32> {
    if r == 0 { return field.to_vec(); }
    let ri = r as isize;
    let r2 = (ri * ri) as f32 + 0.5;
    let offs: Vec<(isize, isize)> = (-ri..=ri)
        .flat_map(|dy| (-ri..=ri).map(move |dx| (dy, dx)))
        .filter(|&(dy, dx)| (dx * dx + dy * dy) as f32 <= r2)
        .collect();
    let mut out = vec![0f32; w * h];
    for y in 0..h as isize {
        for x in 0..w as isize {
            let mut v = if dilate { 0f32 } else { 1e9f32 };
            for &(dy, dx) in &offs {
                let (yy, xx) = (y + dy, x + dx);
                if yy >= 0 && yy < h as isize && xx >= 0 && xx < w as isize {
                    let n = field[(yy as usize) * w + xx as usize];
                    v = if dilate { v.max(n) } else { v.min(n) };
                }
            }
            out[(y as usize) * w + x as usize] = v;
        }
    }
    out
}

fn norm_field(f: &mut [f32]) {
    let (mut lo, mut hi) = (f32::MAX, f32::MIN);
    for &v in f.iter() { lo = lo.min(v); hi = hi.max(v); }
    let d = (hi - lo).max(1e-6);
    for v in f.iter_mut() { *v = (*v - lo) / d; }
}

/// value at the (1-frac) quantile — the threshold that keeps the top `frac` of values (mutates+sorts).
fn top_quantile(vals: &mut Vec<f32>, frac: f32) -> f32 {
    if vals.is_empty() { return f32::MAX; }
    vals.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let k = ((1.0 - frac).clamp(0.0, 1.0) * vals.len() as f32) as usize;
    vals[k.min(vals.len() - 1)]
}

pub fn ink_transfer_v2(rng: &mut ChaCha20Rng, ink: &mut Vec<f32>, w: usize, h: usize, sev: u8, applied: &mut Vec<String>) {
    #[allow(non_snake_case)] let H = h;
    if w < 8 || H < 8 { return; }
    let si = (sev.min(3)) as usize;
    // frozen band means (regimes/ink_transfer_v2.json), then per-row draws + hard clamps
    let absent_m = [0.005, 0.03, 0.07, 0.11][si];
    let faint_m = [0.003, 0.01, 0.02, 0.03][si];
    let spill_m = [0.03, 0.08, 0.18, 0.28][si];
    let thsig_m: f32 = [0.06, 0.13, 0.21, 0.30][si];
    let wp = [0.06, 0.13, 0.20, 0.26][si] as f64;
    let roller_m: f32 = [0.05, 0.20, 0.40, 0.60][si];
    let press_m: f32 = [0.05, 0.17, 0.32, 0.50][si];
    let jn = |m: f32, fr: f32, rng: &mut ChaCha20Rng| (m + gauss1(rng) * fr * m).max(0.0);
    let mut absent = jn(absent_m, 0.4, rng).min(0.15);
    let mut faint = jn(faint_m, 0.4, rng).min(0.04);
    let mut spill = jn(spill_m, 0.35, rng).min(0.40);
    let thsig = rng.gen_range(0.7 * thsig_m..1.3 * thsig_m).clamp(0.04, 0.35); // spec clamp [0.04,0.35]
    let roller = rng.gen_range(0.0..roller_m.max(1e-4_f32));
    let press = rng.gen_range(0.0..press_m.max(1e-4_f32));
    // legibility invariant: normal surface >= 45% (spill+absent+faint <= 0.55) — rescale ALL THREE.
    let tot = spill + absent + faint;
    if tot > 0.55 {
        let s = 0.55 / tot;
        spill *= s;
        absent *= s;
        faint *= s;
    }

    let mask: Vec<bool> = ink.iter().map(|&v| v > 0.45).collect();
    if !mask.iter().any(|&m| m) { return; }
    let runs = letter_runs(ink, w, H);

    // T: per-letter step field, broadcast + softened + normalized
    let mut tcol = vec![1.0f32; w];
    for &(c0, c1) in &runs {
        let mut lvl = 1.0 + gauss1(rng) * thsig;
        if rng.gen_bool(wp) { lvl -= rng.gen_range(0.30..0.75); }
        if rng.gen_bool(wp) { lvl += rng.gen_range(0.20..0.55); }
        lvl = lvl.clamp(0.2, 1.9);
        for x in c0..c1 { tcol[x] = lvl; }
    }
    let mut t = vec![0f32; w * H];
    for y in 0..H {
        for x in 0..w { t[y * w + x] = tcol[x]; }
    }
    // T-blur: spec sigma = 1.4px @ H140, scaled to this strip height (was 1.0 — F1 fix).
    gaussian_blur(&mut t, w, H, 1.4 * H as f32 / 140.0);
    norm_field(&mut t);
    // R roller = norm(0.6*broad + 0.4*bands(H/7 lattice)) — the directional roller-streak structure
    // (the bands lattice was missing — F1 fix). bands = a low-VERTICAL-resolution field stretched to H.
    let mut r = smooth_field(rng, w, H, ((0.35 * w as f32) as usize).max(10), 0.0, 1.0);
    {
        let hb = (H / 7).max(4);
        let small = smooth_field(rng, w, hb, 2, 0.0, 1.0);
        for y in 0..H {
            let sy = (y as f32 * hb as f32 / H as f32).min((hb - 1) as f32);
            let (y0, fy) = (sy.floor() as usize, sy.fract());
            let y1 = (y0 + 1).min(hb - 1);
            for x in 0..w {
                let band = small[y0 * w + x] * (1.0 - fy) + small[y1 * w + x] * fy;
                r[y * w + x] = 0.6 * r[y * w + x] + 0.4 * band;
            }
        }
    }
    norm_field(&mut r);
    let mut p = smooth_field(rng, w, H, ((0.55 * H as f32) as usize).max(10), 0.0, 1.0);
    norm_field(&mut p);
    let mut fld_f = smooth_field(rng, w, H, 3, 0.0, 1.0);
    norm_field(&mut fld_f);
    let mut fld_c = smooth_field(rng, w, H, ((0.09 * H as f32) as usize).max(6), 0.0, 1.0);
    norm_field(&mut fld_c);
    // contrast-scale R/P by the drawn amplitudes
    let mut rc = vec![0f32; w * H];
    let mut pc = vec![0f32; w * H];
    for i in 0..w * H {
        rc[i] = (0.5 + (r[i] - 0.5) * roller * 2.86).clamp(0.0, 1.0);
        pc[i] = (0.5 + (p[i] - 0.5) * press * 2.0).clamp(0.0, 1.0);
    }

    let mut new = ink.clone();
    // base per-letter darkness (proud + high pressure -> darker)
    for i in 0..w * H {
        if mask[i] { new[i] = ink[i] * (0.84 + 0.16 * t[i]) * (0.80 + 0.40 * pc[i]); }
    }
    // SPILLAGE: connect (close - glyph) + fatten (dilate), where Psi_spill is in the top `spill` fraction
    let fm: Vec<f32> = mask.iter().map(|&m| if m { 1.0 } else { 0.0 }).collect();
    let r_close = ((0.021 * H as f32).round() as usize).max(1);
    let r_fat = ((0.0266 * H as f32).round() as usize).max(1); // spec fatten 3.73px@H140 = 0.0266*H (F1 fix)
    let closed = morph_disk(&morph_disk(&fm, w, H, r_close, true), w, H, r_close, false);
    let fat = morph_disk(&fm, w, H, r_fat, true);
    let psi_spill = |i: usize| 0.5 * rc[i] + 0.3 * pc[i] + 0.2 * fld_c[i];
    if spill > 0.0 {
        let mut sv: Vec<f32> = (0..w * H).filter(|&i| mask[i]).map(psi_spill).collect();
        let thr = top_quantile(&mut sv, spill);
        for i in 0..w * H {
            if psi_spill(i) >= thr && ((closed[i] > 0.5 && fm[i] < 0.5) || fat[i] > 0.5) {
                new[i] = 1.0;
            }
        }
    }
    // ABSENT (per-letter capped at 50%) + FAINT (gray) where Psi_absent is highest.
    // Ψ_absent FIELD MATH = the frozen spec: 0.5*(1-Tn) + 0.3*(1-Pc) + 0.2*F (F1 fix — was a rewritten
    // 0.4/0.25/0.15 + a `thin` term the owner never approved).
    // POISON-PROBE GUARD (spec invariants.poison_probes, "accent-band + bottom-band survival"): the
    // frozen produce_batches left mark survival to the per-letter cap + eyeball; the factory must ENFORCE
    // it, so `band_protect` damps absent-propensity where accents (top band) and ypogegrammeni (bottom
    // band) live. This is an explicit, disclosed guard SERVING the spec invariant, NOT a change to the
    // field math (body rows are unaffected: multiplier = 1.0). Structural probes (hole-survival, CC-merge)
    // + a bottom-band retention test enforce the rest; the top-band accent_survival repair loop is the
    // build-time net for accents (it does NOT cover the bottom band — that is band_protect + cap + test).
    let band_protect = |i: usize| {
        let yf = (i / w) as f32 / H as f32;
        if yf < 0.30 || yf > 0.80 { 0.35 } else { 1.0 }
    };
    let psi_absent = |i: usize| {
        (0.5 * (1.0 - t[i]) + 0.3 * (1.0 - pc[i]) + 0.2 * fld_f[i]) * band_protect(i)
    };
    if absent > 0.0 {
        let a_thr = top_quantile(&mut (0..w * H).filter(|&i| mask[i]).map(psi_absent).collect(), absent);
        let f_thr = top_quantile(&mut (0..w * H).filter(|&i| mask[i]).map(psi_absent).collect(), absent + faint);
        let mut absent_mask: Vec<bool> = (0..w * H).map(|i| mask[i] && psi_absent(i) >= a_thr).collect();
        for &(c0, c1) in &runs {
            let idx: Vec<usize> = (0..H).flat_map(|y| (c0..c1).map(move |x| y * w + x)).filter(|&i| mask[i]).collect();
            if idx.is_empty() { continue; }
            let abs_cnt = idx.iter().filter(|&&i| absent_mask[i]).count();
            if abs_cnt as f32 > 0.5 * idx.len() as f32 {
                let thr = top_quantile(&mut idx.iter().map(|&i| psi_absent(i)).collect(), 0.5);
                for &i in &idx { absent_mask[i] = psi_absent(i) >= thr; }
            }
        }
        for i in 0..w * H {
            if !mask[i] { continue; }
            if absent_mask[i] {
                new[i] = 0.0;
            } else {
                let a = psi_absent(i);
                if a >= f_thr && a < a_thr { new[i] = new[i].min(0.45); }
            }
        }
    }
    for i in 0..w * H { ink[i] = new[i].clamp(0.0, 1.0); }
    applied.push("ink_transfer_v2".into());
}

/// Segmentation-spill (owner ask 2026-07-07): the line detector could NOT cleanly separate this
/// line — the crop includes a FULL-INK slice (5–10% of the neighbor's band height) of the line
/// above (descenders) or below (ascenders/accents). GT stays this line only: exactly the
/// robustness case real detector crops on tight leading produce. Applied to the INK channel
/// pre-compose, so the spill shares paper + scan damage with the line itself.
pub fn neighbor_spill(
    rng: &mut ChaCha20Rng,
    ink: &mut [f32],
    w: usize,
    h: usize,
    neighbor: (&[f32], usize, usize),
    applied: &mut Vec<String>,
) {
    #[allow(non_snake_case)] let H = h;
    let (nink, nw, nh) = neighbor;
    // neighbor ink band (rows with ink)
    let rows: Vec<f32> = (0..nh).map(|y| nink[y * nw..(y + 1) * nw].iter().sum()).collect();
    let mx = rows.iter().cloned().fold(0f32, f32::max);
    if mx <= 0.0 {
        return;
    }
    let (mut ny0, mut ny1) = (0usize, nh);
    while ny0 < nh && rows[ny0] < mx * 0.02 { ny0 += 1; }
    while ny1 > ny0 && rows[ny1 - 1] < mx * 0.02 { ny1 -= 1; }
    let band = (ny1 - ny0).max(4);
    let frac = rng.gen_range(0.05f32..0.10);
    let visible = ((band as f32 * frac).ceil() as usize).max(2);
    let from_below = rng.gen_bool(0.5);
    let xoff = rng.gen_range(-(w as i32) / 12..(w as i32) / 12);
    for v in 0..visible {
        let (dy, sy) = if from_below {
            (H - visible + v, ny0 + v) // neighbor-below: its TOP rows at our bottom edge
        } else {
            (v, ny1 - visible + v) // neighbor-above: its BOTTOM rows at our top edge
        };
        if sy >= nh {
            continue;
        }
        for x in 0..w {
            let sx = x as i32 + xoff;
            if sx < 0 || sx as usize >= nw {
                continue;
            }
            let a = nink[sy * nw + sx as usize];
            let p = &mut ink[dy * w + x];
            *p = p.max(a);
        }
    }
    applied.push(if from_below { "neighbor_spill_below".into() } else { "neighbor_spill_above".into() });
}

/// ---- composition ----  returns (image, bg_level, ink_level)
pub fn compose(rng: &mut ChaCha20Rng, ink: &[f32], w: usize, h: usize, style: &Style) -> (Vec<f32>, f32, f32) {
    #[allow(non_snake_case)] let H = h;
    let bg_level = rng.gen_range(0.84f32..0.96);
    let ink_level = rng.gen_range(0.04f32..0.22);
    let mut img = vec![bg_level; H * w];
    match style.bg_type.as_str() {
        "gradient" => {
            let horiz = rng.gen_bool(0.7);
            let amp = rng.gen_range(0.03f32..0.08);
            let sgn = if rng.gen_bool(0.5) { 1.0 } else { -1.0 };
            for y in 0..H {
                for x in 0..w {
                    let t = if horiz { x as f32 / w as f32 } else { y as f32 / H as f32 };
                    img[y * w + x] = (bg_level + sgn * amp * (t - 0.5)).clamp(0.0, 1.0);
                }
            }
        }
        "textured" => {
            // multi-octave fibrous paper (Augraphy NoiseTexturize/BrightnessTexturize concept)
            let f1 = smooth_field(rng, w, h, 6, -0.035, 0.035);
            let f2 = smooth_field(rng, w, h, 24, -0.03, 0.03);
            let mut tex: Vec<f32> = f1.iter().zip(f2).map(|(a, b)| a + b).collect();
            gaussian_blur(&mut tex, w, h, 1.0);
            for (p, t) in img.iter_mut().zip(tex) {
                *p = (*p + t).clamp(0.0, 1.0);
            }
        }
        _ => {}
    }
    // UNEVEN PAGE TONE (always on at sev>0, amplitude grows with severity): long-wavelength
    // toning drift — aged paper is never one flat value. (owner directive 2026-07-06)
    if style.severity > 0 {
        let amp = 0.016 + 0.015 * style.severity as f32;
        let tone = smooth_field(rng, w, h, 96, -amp, amp);
        for (p, t) in img.iter_mut().zip(tone) {
            *p = (*p + t).clamp(0.0, 1.0);
        }
    }
    for i in 0..img.len() {
        img[i] = img[i] * (1.0 - ink[i]) + ink_level * ink[i];
    }
    (img, bg_level, ink_level)
}

/// Verso show-through — the owner's "reversed and translucent letters from the other side of the
/// page": REAL other-page text (select-time verso line), MIRRORED, blurred by the paper, faded
/// unevenly by a paper-thickness field. Falls back to mirrored self when no verso ink is given.
/// Runs AFTER the accent-survival probe (it adds ink; it never destroys marks).
/// REFERENCES: DocCreator (Journet et al., J. Imaging 2017) verso bleed-through model (ideas
/// only — GPL); Augraphy BleedThrough.
pub fn verso_bleed(
    rng: &mut ChaCha20Rng,
    img: &mut [f32],
    w: usize,
    h: usize,
    sev: u8,
    verso: Option<(&[f32], usize, usize)>,
    applied: &mut Vec<String>,
    s_override: Option<f32>,
) {
    #[allow(non_snake_case)] let H = h;
    let s = s_override.unwrap_or(sev as f32);
    let alpha = rng.gen_range(0.10..0.16 + 0.10 * s);
    let dy_off = rng.gen_range(-8i32..=8);
    let mut ghost = vec![0f32; img.len()];
    match verso {
        Some((vink, vw, vh)) => {
            for y in 0..H {
                let sy = y as i32 + dy_off;
                if sy < 0 || sy >= vh as i32 {
                    continue;
                }
                for x in 0..w {
                    let sx = vw as i32 - 1 - x as i32; // mirrored (verso seen through the leaf)
                    if sx >= 0 && (sx as usize) < vw {
                        ghost[y * w + x] = vink[sy as usize * vw + sx as usize];
                    }
                }
            }
            applied.push("verso_ghost".into());
        }
        None => {
            for y in 0..H {
                let sy = y as i32 + dy_off;
                if sy < 0 || sy >= H as i32 {
                    continue;
                }
                for x in 0..w {
                    ghost[y * w + x] = 1.0 - img[sy as usize * w + (w - 1 - x)];
                }
            }
            applied.push("verso_ghost_self".into());
        }
    }
    gaussian_blur(&mut ghost, w, h, rng.gen_range(1.0..2.2));
    let thickness = smooth_field(rng, w, h, 40, 0.35, 1.0); // paper thickness varies -> uneven show-through
    for i in 0..img.len() {
        let a = (ghost[i] * alpha * thickness[i]).min(0.6);
        // ghost tone saturates toward mid-gray, never full black (it is seen THROUGH paper)
        img[i] = (img[i] - a * (img[i] - 0.35).max(0.0)).clamp(0.0, 1.0);
    }
}

/// ---- detector crop (I7/I8 reframe; docs/crop_robustness_design.md) ----
/// FINAL image op (runs AFTER Geo — inference order is skew→detect→crop→resize): band-crop the finished
/// strip and resize the retained band back to 48px, interface-exact to pipeline/strips.py::extract_strip
/// (+2px + 10%/side pad, aspect-preserving resize, letterbox at MAX_W, right-pad at MIN_W). Crop DEPTH is
/// set by `tight`/`loose` ALONE — never bounded by accent legibility; the only structural bound is that the
/// cut cannot pass `top_band_y`/`bot_band_y`, so the x-height BODY (the letters) is always protected.
/// AUTOMATIC label-repair (always on): any mark whose OWN isolated ink (`MarkGeom.own`) retained across the
/// cut, measured at the EXACT boundary in the upright frame, falls below `noise_floor` is returned in
/// `dropped_gt_idxs` for the caller to drop from the label — dormant at a survivable max, self-correcting
/// if the max is raised. (Upright-frame / Geo-blind; the deep-draw up-shift tail is ~1e-4, ~0 at default.)
/// Returns (new_img 48×new_w, new_w, dropped_gt_idxs, top_band_survival_fraction). Deterministic in `rng`.
/// The 4th value is the geometric top-mark-band retention (1.0 = nothing cut) — the caller composes it with
/// the pre-crop Photo survival so `accent_survival` reflects the EMITTED image (F5).
pub fn detector_crop(
    rng: &mut ChaCha20Rng,
    img: &[f32],
    w: usize,
    top_band_y: usize,
    bot_band_y: usize,
    has_top: bool,
    _has_bottom: bool, // (kept for call-site symmetry; bottom survival is per-mark now, not band-clamped)
    marks: &[crate::render::MarkGeom],
    cfg: &crate::recipe::CropCfg,
    applied: &mut Vec<String>,
) -> (Vec<f32>, usize, Vec<usize>, f32) {
    use crate::render::{MAX_W, MIN_W};
    let h = crate::render::STRIP_H;

    // stratum pick from the (normalized) mixture
    let (mc, mt, mlx) = (cfg.mix.canonical.max(0.0), cfg.mix.tight.max(0.0), cfg.mix.loose.max(0.0));
    let total = (mc + mt + mlx).max(1e-9);
    let pick = rng.gen::<f64>() * total;

    // polarity-robust ink profile: |value − median-bg| summed per row
    let mut sorted: Vec<f32> = img.to_vec();
    sorted.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let bg = sorted[sorted.len() / 2];
    let row_mass: Vec<f32> = (0..h)
        .map(|y| (0..w).map(|x| (img[y * w + x] - bg).abs()).sum::<f32>())
        .collect();
    let maxrow = row_mass.iter().cloned().fold(0.0f32, f32::max).max(1e-6);
    let thr = 0.02 * maxrow;
    let i0 = (0..h).find(|&y| row_mass[y] > thr).unwrap_or(0);
    let i1 = (0..h).rev().find(|&y| row_mass[y] > thr).map(|y| y + 1).unwrap_or(h);
    let bh = i1.saturating_sub(i0).max(1) as f32;

    // ink (|value − bg|) over a column×row box on the POST-GEO image — the honest F4/F5 measurement.
    let ink = |c0: usize, c1: usize, r0: usize, r1: usize| -> f32 {
        let (c0, c1, r0, r1) = (c0.min(w), c1.min(w), r0.min(h), r1.min(h));
        let mut s = 0.0f32;
        for y in r0..r1 {
            for x in c0..c1 {
                s += (img[y * w + x] - bg).abs();
            }
        }
        s
    };

    let mut drops = Vec::new();
    let mut band_surv = 1.0f32;
    let mut out: Vec<f32>;
    let mut new_w: usize;
    if pick < mc {
        applied.push("crop:canonical".into()); // native render IS the canonical contract
        out = img.to_vec();
        new_w = w;
    } else {
        let stratum;
        let (a, b) = if pick < mc + mt {
            stratum = "tight"; // cut into the above-x-height (top) / below-baseline (bottom) room, asymmetric
            let ft = rng.gen::<f32>() * cfg.tight.t_max;
            let fb = rng.gen::<f32>() * cfg.tight.b_max;
            let top_zone = (top_band_y as f32 - i0 as f32).max(0.0);
            let bot_zone = (i1 as f32 - bot_band_y as f32).max(0.0);
            (i0 as f32 + ft * top_zone, i1 as f32 - fb * bot_zone)
        } else {
            stratum = "loose"; // pad OUTWARD beyond the ink band (glyphs shrink in the strip)
            let pt = cfg.loose.pad_min + rng.gen::<f32>() * (cfg.loose.pad_max - cfg.loose.pad_min);
            let pb = cfg.loose.pad_min + rng.gen::<f32>() * (cfg.loose.pad_max - cfg.loose.pad_min);
            (i0 as f32 - pt * bh, i1 as f32 + pb * bh)
        };
        // NOTE: crop depth comes from `tight`/`loose` ALONE — it is NEVER pulled back to protect accent
        // legibility. The only structural bound is geometric (the tight cut cannot pass `top_band_y` / rise
        // above `bot_band_y`, so the x-height BODY — the letters — is always protected). Accents that the
        // crop destroys are handled by the automatic label-repair below, not by clamping the crop.
        let det = 2.0 + 0.10 * (b - a).max(0.0); // +2px + 10%/side detector pad (extract_strip)
        let ra = a - det;
        let rb = b + det;
        if rb - ra < 4.0 {
            applied.push(format!("crop:{stratum}:degenerate"));
            out = img.to_vec();
            new_w = w;
        } else {
            // aspect-preserving resize band_h→48; letterbox at MAX_W, right-pad at MIN_W.
            let band_h = rb - ra;
            let want_w = (w as f32 * h as f32 / band_h).round().max(1.0) as usize;
            if want_w > MAX_W {
                let new_h = ((h as f32 * MAX_W as f32 / want_w as f32).round() as usize).max(8).min(h);
                let band = resample_band(img, w, h, ra, rb, new_h, MAX_W, bg);
                let mut canvas = vec![bg; h * MAX_W];
                let top = (h - new_h) / 2;
                canvas[top * MAX_W..(top + new_h) * MAX_W].copy_from_slice(&band);
                out = canvas;
                new_w = MAX_W;
            } else if want_w < MIN_W {
                let band = resample_band(img, w, h, ra, rb, h, want_w, bg);
                let mut canvas = vec![bg; h * MIN_W];
                for y in 0..h {
                    canvas[y * MIN_W..y * MIN_W + want_w].copy_from_slice(&band[y * want_w..(y + 1) * want_w]);
                }
                out = canvas;
                new_w = MIN_W;
            } else {
                out = resample_band(img, w, h, ra, rb, h, want_w, bg);
                new_w = want_w;
            }
            // F5: honest top-mark-band retention (geometric), over ALL columns, in the upright band.
            if has_top && top_band_y > 1 {
                let tot = ink(0, w, 0, top_band_y).max(1e-6);
                let lo = ra.max(0.0).ceil() as usize;
                let keep = if lo >= top_band_y { 0.0 } else { ink(0, w, lo, top_band_y) };
                band_surv = (keep / tot).min(1.0);
            }
            // AUTOMATIC per-mark repair (always on): survival = retained fraction of the mark's OWN isolated
            // ink profile across the cut — NOT the never-cut base body (F1 fix). Measured at the EXACT cut
            // boundary: any accent with < noise_floor of its own ink retained is dropped (masked-kept=0, no
            // hallucinated-accent labels). The det pad (+2px+10%) is the interface margin; a widened window or
            // Geo slack would re-admit base ink / mask truly-cleared accents (probe-refuted). Fires ~never at
            // a survivable max; the deepest-draw drops are Geo-borderline accents (bias: drop > hallucinate).
            for m in marks {
                let total: f32 = m.own.iter().sum::<f32>().max(1e-6);
                let retained: f32 = m
                    .own
                    .iter()
                    .enumerate()
                    .map(|(i, &v)| {
                        let row = (m.row0 + i) as f32;
                        let kept = if m.is_top { row >= ra } else { row < rb };
                        if kept { v } else { 0.0 }
                    })
                    .sum();
                if retained / total < cfg.repair.noise_floor {
                    drops.push(m.gt_idx);
                }
            }
            applied.push(format!("crop:{stratum}:a{:.1}:b{:.1}:rr{:.2}", a, b, (b - a).max(0.0) / h as f32));
        }
    }

    // F2: L/R white-margin EXPAND (label-trivial), all strata; total width capped at MAX_W.
    let mlp = if rng.gen_bool(cfg.l_margin_prob) { (rng.gen::<f32>() * cfg.margin_max as f32 * h as f32) as usize } else { 0 };
    let mrp = if rng.gen_bool(cfg.r_margin_prob) { (rng.gen::<f32>() * cfg.margin_max as f32 * h as f32) as usize } else { 0 };
    if (mlp + mrp) > 0 && new_w < MAX_W {
        let avail = MAX_W - new_w;
        let l = mlp.min(avail);
        let r = mrp.min(avail - l);
        if l + r > 0 {
            let tot_w = new_w + l + r;
            let mut canvas = vec![bg; h * tot_w];
            for y in 0..h {
                canvas[y * tot_w + l..y * tot_w + l + new_w].copy_from_slice(&out[y * new_w..(y + 1) * new_w]);
            }
            out = canvas;
            new_w = tot_w;
            applied.push(format!("crop:margin:l{l}:r{r}"));
        }
    }
    (out, new_w, drops, band_surv)
}

/// Resample source rows [ra, rb) × cols [0, w) into (out_h × out_w). Vertical maps the retained band;
/// horizontal maps the full width. Rows outside [0, H) fill with `bg` (loose crops that pad past canvas).
fn resample_band(img: &[f32], w: usize, h: usize, ra: f32, rb: f32, out_h: usize, out_w: usize, bg: f32) -> Vec<f32> {
    let mut out = vec![bg; out_h * out_w];
    let sh = (rb - ra) / out_h as f32;
    let sw = w as f32 / out_w as f32;
    for oy in 0..out_h {
        let sy = ra + oy as f32 * sh;
        if sy < 0.0 || sy > (h - 1) as f32 {
            continue; // bg fill
        }
        let y0 = sy.floor() as usize;
        let y1 = (y0 + 1).min(h - 1);
        let ty = sy - y0 as f32;
        for ox in 0..out_w {
            let sx = (ox as f32 * sw).min((w - 1) as f32);
            let x0 = sx.floor() as usize;
            let x1 = (x0 + 1).min(w - 1);
            let tx = sx - x0 as f32;
            let g = |yy: usize, xx: usize| img[yy * w + xx];
            out[oy * out_w + ox] = g(y0, x0) * (1.0 - tx) * (1.0 - ty)
                + g(y0, x1) * tx * (1.0 - ty)
                + g(y1, x0) * (1.0 - tx) * ty
                + g(y1, x1) * tx * ty;
        }
    }
    out
}

/// ---- image stage ----
/// Phases (2026-07-06, sibling-bug lesson): PHOTO = every mark-killing op (incl. binarize) runs
/// FIRST so accent survival is measured on a STATIC band; GEO = displacement ops run after the
/// probe. Rotation is width-capped so line ends can never leave the canvas (the sibling's
/// issue-#9 end-truncation bug class: ink clipped while GT keeps full text).
#[derive(Clone, Copy, PartialEq)]
pub enum Phase {
    Photo,
    Geo,
}

struct OpDef {
    name: &'static str,
    min_sev: u8,
    prob: [f64; 4], // activation prob per severity
    phase: Phase,
}

/// Per-op strength caps from the 2026-07-06 distortion-ladder review (docs/review_feedback §3.5):
/// in ISOLATION these ops cross the readability/label-fidelity cliff below the global extreme —
/// ink_starve erases whole words by ~1.5x sev3 (label poison), motion_blur smears past ~1.5x,
/// speckle specks become mark-confusable past ~2.25x. s (severity float) is clamped per-op.
pub const OP_S_CAP: &[(&str, f32)] = &[("ink_starve", 4.5), ("motion_blur", 4.5), ("speckle", 6.75)];

fn cap_s(name: &str, s: f32) -> f32 {
    OP_S_CAP.iter().find(|(n, _)| *n == name).map_or(s, |(_, c)| s.min(*c))
}

/// Every op name the engine can apply (wiring-test contract: each must be reachable AND must
/// change pixels — the sibling's "declared but not wired" bug class).
pub const OP_NAMES: &[&str] = &[
    "illumination", "brightness_contrast", "gamma", "gaussian_blur", "motion_blur",
    "gaussian_noise", "speckle", "stamp_overlay", "page_stain", "paper_watermark",
    "roller_streaks", "binarize", "jpeg", "rotate", "perspective", "baseline_wobble",
    "lowres",
];

const REGISTRY: &[OpDef] = &[
    OpDef { name: "illumination", min_sev: 1, prob: [0.0, 0.40, 0.60, 0.80], phase: Phase::Photo },
    OpDef { name: "page_stain", min_sev: 1, prob: [0.0, 0.22, 0.35, 0.50], phase: Phase::Photo },
    OpDef { name: "paper_watermark", min_sev: 1, prob: [0.0, 0.15, 0.22, 0.30], phase: Phase::Photo },
    OpDef { name: "roller_streaks", min_sev: 2, prob: [0.0, 0.0, 0.12, 0.20], phase: Phase::Photo },
    OpDef { name: "brightness_contrast", min_sev: 1, prob: [0.0, 0.55, 0.65, 0.75], phase: Phase::Photo },
    OpDef { name: "gamma", min_sev: 1, prob: [0.0, 0.30, 0.35, 0.40], phase: Phase::Photo },
    OpDef { name: "gaussian_blur", min_sev: 1, prob: [0.0, 0.30, 0.45, 0.55], phase: Phase::Photo },
    OpDef { name: "motion_blur", min_sev: 2, prob: [0.0, 0.0, 0.15, 0.25], phase: Phase::Photo },
    OpDef { name: "gaussian_noise", min_sev: 1, prob: [0.0, 0.45, 0.60, 0.75], phase: Phase::Photo },
    OpDef { name: "speckle", min_sev: 1, prob: [0.0, 0.30, 0.50, 0.70], phase: Phase::Photo },
    OpDef { name: "stamp_overlay", min_sev: 1, prob: [0.0, 0.04, 0.08, 0.12], phase: Phase::Photo },
    OpDef { name: "binarize", min_sev: 2, prob: [0.0, 0.0, 0.10, 0.22], phase: Phase::Photo },
    OpDef { name: "jpeg", min_sev: 1, prob: [0.0, 0.30, 0.45, 0.55], phase: Phase::Photo },
    OpDef { name: "rotate", min_sev: 1, prob: [0.0, 0.40, 0.50, 0.55], phase: Phase::Geo },
    OpDef { name: "perspective", min_sev: 1, prob: [0.0, 0.15, 0.25, 0.35], phase: Phase::Geo },
    OpDef { name: "baseline_wobble", min_sev: 1, prob: [0.0, 0.20, 0.30, 0.40], phase: Phase::Geo },
    OpDef { name: "lowres", min_sev: 1, prob: [0.0, 0.15, 0.30, 0.45], phase: Phase::Geo },
];

fn bilinear(img: &[f32], w: usize, h: usize, x: f32, y: f32, _fill: f32) -> f32 {
    #[allow(non_snake_case)] let H = h;
    // CLAMP-TO-EDGE sampling (2026-07-06): flat-fill corners after rotate/perspective were a
    // visible artifact class (the sibling's "rotation fix still buggy" residual) — extending the
    // edge pixels continues paper/texture naturally instead of stamping flat patches.
    let x = x.clamp(0.0, (w - 1) as f32 - 1e-3);
    let y = y.clamp(0.0, (H - 1) as f32 - 1e-3);
    let x0 = x as usize;
    let y0 = y as usize;
    let tx = x - x0 as f32;
    let ty = y - y0 as f32;
    img[y0 * w + x0] * (1.0 - tx) * (1.0 - ty)
        + img[y0 * w + x0 + 1] * tx * (1.0 - ty)
        + img[(y0 + 1) * w + x0] * (1.0 - tx) * ty
        + img[(y0 + 1) * w + x0 + 1] * tx * ty
}

fn warp(img: &Vec<f32>, w: usize, h: usize, m: [f32; 9], fill: f32) -> Vec<f32> {
    #[allow(non_snake_case)] let H = h;
    let mut out = vec![fill; img.len()];
    for y in 0..H {
        for x in 0..w {
            let d = m[6] * x as f32 + m[7] * y as f32 + m[8];
            let sx = (m[0] * x as f32 + m[1] * y as f32 + m[2]) / d;
            let sy = (m[3] * x as f32 + m[4] * y as f32 + m[5]) / d;
            out[y * w + x] = bilinear(img, w, h, sx, sy, fill);
        }
    }
    out
}

fn bg_estimate(img: &[f32]) -> f32 {
    let mut v: Vec<f32> = img.iter().copied().collect();
    v.sort_by(|a, b| a.partial_cmp(b).unwrap());
    v[(v.len() as f32 * 0.85) as usize]
}

pub fn image_ops(
    rng: &mut ChaCha20Rng,
    img: &mut Vec<f32>,
    w: usize,
    h: usize,
    sev: u8,
    applied: &mut Vec<String>,
    phase: Phase,
    force_all: bool,
    only: Option<&str>,
    s_override: Option<f32>,
    ctx: &OpCtx,
) {
    #[allow(non_snake_case)]
    let H = h;
    if sev == 0 && !force_all && s_override.is_none() {
        return;
    }
    let sev = if force_all || s_override.is_some() { 3 } else { sev };
    let si = sev as usize;
    let s = s_override.unwrap_or(sev as f32);
    let chosen: Vec<&OpDef> = REGISTRY
        .iter()
        .filter(|o| o.phase == phase && only.map_or(true, |n| n == o.name))
        .filter(|o| force_all || only.is_some() || (sev >= o.min_sev && rng.gen_bool(o.prob[si])))
        .collect();
    let fill = bg_estimate(img);
    let s_outer = s;
    for op in chosen {
        let s = cap_s(op.name, s_outer);
        match op.name {
            "illumination" => {
                let f = if rng.gen_bool(0.5) {
                    // linear
                    let amp = rng.gen_range(0.05..0.10 + 0.05 * s);
                    let horiz = rng.gen_bool(0.6);
                    (0..img.len())
                        .map(|i| {
                            let (y, x) = (i / w, i % w);
                            let t = if horiz { x as f32 / w as f32 } else { y as f32 / H as f32 };
                            1.0 - amp * t
                        })
                        .collect::<Vec<f32>>()
                } else {
                    // vignette toward one end (binding shadow)
                    let amp = rng.gen_range(0.06..0.12 + 0.04 * s);
                    let cx = if rng.gen_bool(0.5) { 0.0 } else { w as f32 };
                    (0..img.len())
                        .map(|i| {
                            let x = (i % w) as f32;
                            let d = ((x - cx).abs() / w as f32).min(1.0);
                            1.0 - amp * (1.0 - d)
                        })
                        .collect()
                };
                for (p, m) in img.iter_mut().zip(f) {
                    *p = (*p * m).clamp(0.0, 1.0);
                }
            }
            "page_stain" => {
                // damp/tea/foxing stains: 1-3 large soft-edged darker blobs (DocCreator/Augraphy
                // stain concept; the blotchy toning of the 1899 reference)
                for _ in 0..rng.gen_range(1..=3) {
                    let cx = rng.gen_range(0.0..w as f32);
                    let cy = rng.gen_range(0.0..H as f32);
                    let rx = rng.gen_range(25.0..120.0f32);
                    let ry = rng.gen_range(12.0..40.0f32);
                    let amp = rng.gen_range(0.03..0.06 + 0.03 * s);
                    let ring = rng.gen_bool(0.4); // dried stains darken at the rim
                    for y in 0..H {
                        for x in 0..w {
                            let d = (((x as f32 - cx) / rx).powi(2) + ((y as f32 - cy) / ry).powi(2)).sqrt();
                            if d < 1.3 {
                                let core = (1.0 - d).max(0.0);
                                let rim = (1.0 - (d - 1.0).abs() * 6.0).max(0.0);
                                let a = if ring { core * 0.4 + rim * 0.8 } else { core };
                                let p = &mut img[y * w + x];
                                *p = (*p - amp * a).clamp(0.0, 1.0);
                            }
                        }
                    }
                }
            }
            "paper_watermark" => {
                // paper-structure watermark: laid lines + chain lines + a lighter emblem region,
                // all sub-threshold light (visible as PAPER, transparent to ink)
                let laid_period = rng.gen_range(7.0..12.0f32);
                let chain_period = rng.gen_range(90.0..150.0f32);
                let amp = rng.gen_range(0.012..0.03);
                let ph: f32 = rng.gen_range(0.0..laid_period);
                for y in 0..H {
                    let laid = (((y as f32 + ph) / laid_period) * std::f32::consts::TAU).sin().max(0.0) * amp;
                    for x in 0..w {
                        let chain = (((x as f32) / chain_period) * std::f32::consts::TAU).sin().powi(8) * amp * 1.5;
                        let p = &mut img[y * w + x];
                        *p = (*p + laid + chain).clamp(0.0, 1.0);
                    }
                }
                if rng.gen_bool(0.5) {
                    // emblem: one soft lighter blob (the mark itself)
                    let cx = rng.gen_range(0.0..w as f32);
                    let r = rng.gen_range(14.0..30.0f32);
                    let amp2 = rng.gen_range(0.02..0.045);
                    for y in 0..H {
                        for x in 0..w {
                            let d = ((x as f32 - cx).powi(2) + (y as f32 - 24.0).powi(2)).sqrt() / r;
                            if d < 1.0 {
                                let p = &mut img[y * w + x];
                                *p = (*p + amp2 * (1.0 - d)).clamp(0.0, 1.0);
                            }
                        }
                    }
                }
            }
            "roller_streaks" => {
                // photocopier/scanner roller streaks: faint full-height vertical bands
                // (Augraphy DirtyRollers)
                for _ in 0..rng.gen_range(1..=3) {
                    let x0 = rng.gen_range(0..w);
                    let bw = rng.gen_range(2..9);
                    let dark = rng.gen_bool(0.5);
                    let amp = rng.gen_range(0.02..0.05 + 0.02 * s);
                    for y in 0..H {
                        for x in x0..(x0 + bw).min(w) {
                            let p = &mut img[y * w + x];
                            *p = if dark { (*p - amp).clamp(0.0, 1.0) } else { (*p + amp).clamp(0.0, 1.0) };
                        }
                    }
                }
            }
            "brightness_contrast" => {
                let b = rng.gen_range(-0.06 - 0.02 * s..0.06 + 0.02 * s);
                let c = rng.gen_range(0.82 - 0.05 * s..1.15);
                for p in img.iter_mut() {
                    *p = ((*p - 0.5) * c + 0.5 + b).clamp(0.0, 1.0);
                }
            }
            "gamma" => {
                let g = rng.gen_range(0.75..1.35);
                for p in img.iter_mut() {
                    *p = p.max(0.0).powf(g);
                }
            }
            "gaussian_blur" => gaussian_blur(img, w, h, rng.gen_range(0.4..0.5 + 0.35 * s)),
            "motion_blur" => {
                let len = rng.gen_range(2..=(2.0 + s).round() as i32);
                let ang: f32 = rng.gen_range(-0.6f32..0.6);
                let (dx, dy) = (ang.cos(), ang.sin());
                let src = img.clone();
                for y in 0..H {
                    for x in 0..w {
                        let mut acc = 0.0;
                        for k in 0..len {
                            let t = k as f32 - (len - 1) as f32 / 2.0;
                            acc += bilinear(&src, w, h, x as f32 + dx * t, y as f32 + dy * t, fill);
                        }
                        img[y * w + x] = acc / len as f32;
                    }
                }
            }
            "gaussian_noise" => {
                let sd = rng.gen_range(0.01..0.02 + 0.02 * s);
                for p in img.iter_mut() {
                    let u1: f32 = rng.gen_range(1e-6f32..1.0);
                    let u2: f32 = rng.gen();
                    let n = (-2.0 * u1.ln()).sqrt() * (std::f32::consts::TAU * u2).cos();
                    *p = (*p + n * sd).clamp(0.0, 1.0);
                }
            }
            "speckle" => {
                // foxing/toner specks: dark clusters on bg + pinholes in ink (the reference scan)
                let n_specks = ((w as f32 / 40.0) * (1.0 + s)) as usize;
                for _ in 0..rng.gen_range(n_specks / 2..=n_specks.max(1)) {
                    let cx = rng.gen_range(0..w);
                    let cy = rng.gen_range(0..H);
                    let r = rng.gen_range(0.5f32..1.2 + 0.4 * s);
                    let dark = rng.gen_bool(0.75);
                    let v = if dark { rng.gen_range(0.0..0.35) } else { rng.gen_range(0.75..1.0) };
                    let ri = r.ceil() as i32;
                    for dy in -ri..=ri {
                        for dx in -ri..=ri {
                            let (yy, xx) = (cy as i32 + dy, cx as i32 + dx);
                            if yy < 0 || yy >= H as i32 || xx < 0 || xx >= w as i32 {
                                continue;
                            }
                            let d2 = (dx * dx + dy * dy) as f32;
                            if d2 <= r * r {
                                let a = (1.0 - d2 / (r * r)) * 0.9;
                                let p = &mut img[yy as usize * w + xx as usize];
                                *p = *p * (1.0 - a) + v * a;
                            }
                        }
                    }
                }
            }
            "stamp_overlay" if !ctx.watermarks.is_empty() => {
                // REAL stamp/watermark asset (collected — see assets/watermarks/PROVENANCE.md):
                // a strip crop sees a horizontal SLICE of a page-scale stamp, so we scale the
                // mask to page size and let a random band of it intersect the strip.
                let (_, mask, mw, mh) = &ctx.watermarks[rng.gen_range(0..ctx.watermarks.len())];
                let target_h = rng.gen_range(90.0f32..220.0); // stamp height at page scale, px
                let sc = target_h / *mh as f32;
                let sw = (*mw as f32 * sc) as i32;
                let ox = rng.gen_range(-(sw / 2)..(w as i32 - sw / 4).max(1));
                // pick a vertical slice of the mask that actually CARRIES ink (a random slice
                // often hits the empty middle of a ring stamp → invisible; owner bug 2026-07-07)
                let row_mass: Vec<f32> = (0..*mh).map(|y| mask[y * mw..(y + 1) * mw].iter().sum()).collect();
                let mmax = row_mass.iter().cloned().fold(0f32, f32::max).max(1e-3);
                let inky: Vec<usize> = (0..*mh).filter(|y| row_mass[*y] > 0.35 * mmax).collect();
                let sy0 = if inky.is_empty() { 0 } else { inky[rng.gen_range(0..inky.len())] };
                let oy = -((sy0 as f32 * sc) as i32) + rng.gen_range(0..(H as i32 / 2));
                let a_mult = rng.gen_range(0.30..0.60);
                let tone = rng.gen_range(0.25f32..0.50);
                for y in 0..H {
                    let sy = ((y as i32 - oy) as f32 / sc) as i32;
                    if sy < 0 || sy >= *mh as i32 {
                        continue;
                    }
                    for x in 0..w {
                        let sx = ((x as i32 - ox) as f32 / sc) as i32;
                        if sx < 0 || sx >= *mw as i32 {
                            continue;
                        }
                        let a = mask[sy as usize * mw + sx as usize] * a_mult;
                        if a > 0.003 {
                            let p = &mut img[y * w + x];
                            *p = (*p - a * (*p - tone).max(0.0)).clamp(0.0, 1.0);
                        }
                    }
                }
            }
            "stamp_overlay" => {
                // procedural fallback (no assets configured): ring + inner arc
                let alpha = rng.gen_range(0.08..0.22);
                let r = rng.gen_range(16.0f32..30.0);
                let cx = if rng.gen_bool(0.5) { rng.gen_range(-r..r) } else { w as f32 + rng.gen_range(-r..r) };
                let cy = rng.gen_range(0.0..H as f32);
                let tone = rng.gen_range(0.25f32..0.5);
                for y in 0..H {
                    for x in 0..w {
                        let d = ((x as f32 - cx).powi(2) + (y as f32 - cy).powi(2)).sqrt();
                        let ring = ((d - r).abs() < 1.6) as u8 as f32
                            + 0.6 * (((d - r * 0.72).abs() < 1.0) as u8 as f32);
                        if ring > 0.0 {
                            let p = &mut img[y * w + x];
                            *p = *p * (1.0 - alpha * ring.min(1.0)) + tone * alpha * ring.min(1.0);
                        }
                    }
                }
            }
            "rotate" => {
                // WIDTH-CAPPED (sibling issue-#9 fix): the ends of a strip rotated about its
                // center displace by (w/2)·sinθ — uncapped, a 1.3° rotation clips ±28 px of ink
                // off a 2560px line while the label keeps the full text. Cap so end displacement
                // never exceeds the ~4px vertical margin; long lines get gentler rotations (their
                // real-world skew appears as wobble, which baseline_wobble supplies).
                let a_sev = 0.004 + 0.006 * s;
                let a_cap = (3.5 / (w as f32 / 2.0)).atan();
                let a_max = a_sev.min(a_cap);
                let a = rng.gen_range(-a_max..a_max);
                let (c, si_) = (a.cos(), a.sin());
                let (cx, cy) = (w as f32 / 2.0, H as f32 / 2.0);
                let m = [c, si_, cx - c * cx - si_ * cy, -si_, c, cy + si_ * cx - c * cy, 0.0, 0.0, 1.0];
                *img = warp(img, w, h, m, fill);
            }
            "baseline_wobble" => {
                // letterpress line wobble: small sinusoidal vertical shift per column — the
                // long-line skew realism that the width-capped rotate no longer fakes
                let amp = rng.gen_range(0.4..0.5 + 0.35 * s); // px, ≤ ~1.5
                let wavelen = rng.gen_range(180.0f32..420.0);
                let ph0: f32 = rng.gen_range(0.0..std::f32::consts::TAU);
                let src = img.clone();
                for y in 0..H {
                    for x in 0..w {
                        let dy = amp * (x as f32 / wavelen * std::f32::consts::TAU + ph0).sin();
                        img[y * w + x] = bilinear(&src, w, h, x as f32, y as f32 + dy, fill);
                    }
                }
            }
            "perspective" => {
                // non-degenerate floors: a near-zero draw warps nothing while recording itself
                // (caught by the wiring test 2026-07-07)
                let sgn = if rng.gen_bool(0.5) { 1.0f32 } else { -1.0 };
                let shear = sgn * rng.gen_range(0.006f32..0.02);
                let sgn2 = if rng.gen_bool(0.5) { 1.0f32 } else { -1.0 };
                let k = sgn2 * rng.gen_range(0.4..1.0 + 0.8 * s) / (w as f32 * H as f32);
                let m = [1.0, shear, 0.0, 0.0, 1.0, 0.0, 0.0, k, 1.0];
                *img = warp(img, w, h, m, fill);
            }
            "lowres" => {
                let f = rng.gen_range(1.15..1.2 + 0.5 * s);
                let (sw, sh) = ((w as f32 / f) as usize, (H as f32 / f) as usize);
                let mut small = vec![0f32; sw.max(1) * sh.max(1)];
                for y in 0..sh {
                    for x in 0..sw {
                        small[y * sw + x] = bilinear(img, w, h, x as f32 * f, y as f32 * f, fill);
                    }
                }
                for y in 0..H {
                    for x in 0..w {
                        let sx = (x as f32 / f).min(sw as f32 - 1.001);
                        let sy = (y as f32 / f).min(sh as f32 - 1.001);
                        let x0 = sx as usize;
                        let y0 = sy as usize;
                        let tx = sx - x0 as f32;
                        let ty = sy - y0 as f32;
                        let g = |yy: usize, xx: usize| small[yy.min(sh - 1) * sw + xx.min(sw - 1)];
                        img[y * w + x] = g(y0, x0) * (1.0 - tx) * (1.0 - ty)
                            + g(y0, x0 + 1) * tx * (1.0 - ty)
                            + g(y0 + 1, x0) * (1.0 - tx) * ty
                            + g(y0 + 1, x0 + 1) * tx * ty;
                    }
                }
            }
            "binarize" => {
                let mut soft = img.clone();
                gaussian_blur(&mut soft, w, h, 0.6);
                let thr = bg_estimate(&soft) - rng.gen_range(0.22..0.38);
                let softness = rng.gen_range(12.0f32..40.0);
                for (p, sp) in img.iter_mut().zip(soft) {
                    *p = 1.0 / (1.0 + (-(sp - thr) * softness).exp());
                }
            }
            "jpeg" => { /* applied at u8 stage by caller (needs encode round-trip) */ }
            _ => {}
        }
        applied.push(op.name.into());
    }
}

/// u8 conversion + optional jpeg round-trip (the only op that needs byte space).
pub fn finalize(rng: &mut ChaCha20Rng, img: &[f32], w: usize, h: usize, sev: u8, polarity_light: bool, applied: &mut Vec<String>) -> Vec<u8> {
    #[allow(non_snake_case)] let H = h;
    let mut bytes: Vec<u8> = img
        .iter()
        .map(|p| {
            let v = if polarity_light { 1.0 - *p } else { *p };
            (v.clamp(0.0, 1.0) * 255.0) as u8
        })
        .collect();
    if polarity_light {
        applied.push("polarity_invert".into());
    }
    if applied.iter().any(|a| a == "jpeg") {
        let q = match sev {
            1 => rng.gen_range(70..90),
            2 => rng.gen_range(55..80),
            _ => rng.gen_range(40..70),
        };
        let gray = image::GrayImage::from_raw(w as u32, H as u32, bytes.clone()).expect("gray");
        let mut out = Vec::new();
        let mut enc = image::codecs::jpeg::JpegEncoder::new_with_quality(&mut out, q);
        if enc.encode_image(&gray).is_ok() {
            if let Ok(back) = image::load_from_memory(&out) {
                bytes = back.to_luma8().into_raw();
            }
        }
    }
    bytes
}

/// Ink/bg contrast probe on the final float image (pre-polarity): p10 ink vs p90 bg separation.
pub fn contrast_of(img: &[f32]) -> f32 {
    let mut v: Vec<f32> = img.to_vec();
    v.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let p10 = v[(v.len() as f32 * 0.02) as usize];
    let p90 = v[(v.len() as f32 * 0.90) as usize];
    p90 - p10
}

#[cfg(test)]
mod tests {
    use super::*;
    use rand::SeedableRng;

    const H: usize = crate::render::STRIP_H;

    fn test_strip() -> (Vec<f32>, usize) {
        // synthetic strip: 400px wide, a row of "characters" (blobs) with ascender/descender bits
        let w = 400usize;
        let mut ink = vec![0f32; H * w];
        for cx in (10..w - 10).step_by(14) {
            for y in 14..34 {
                for x in cx..(cx + 8).min(w) {
                    ink[y * w + x] = 1.0;
                }
            }
            if cx % 3 == 0 {
                for y in 8..14 {
                    ink[y * w + cx + 3] = 1.0; // ascender/mark
                }
            }
        }
        (ink, w)
    }

    #[test]
    fn every_op_is_wired_and_changes_pixels() {
        // The sibling program shipped ops that were declared but never consumed, and uneven
        // distortions that were not wired. Contract: EVERY registry op, forced in isolation,
        // must (a) record itself in applied_ops and (b) change pixels (except jpeg, which is a
        // finalize-stage flag).
        let (ink, w) = test_strip();
        for op in OP_NAMES {
            let mut rng = ChaCha20Rng::seed_from_u64(42);
            let style = Style { bg_type: "flat".into(), polarity_light: false, severity: 3 };
            let (base, _, _) = compose(&mut rng, &ink, w, H, &style);
            let mut img = base.clone();
            let mut applied = Vec::new();
            for phase in [Phase::Photo, Phase::Geo] {
                image_ops(&mut rng, &mut img, w, H, 3, &mut applied, phase, false, Some(op), None, &OpCtx::default());
            }
            assert!(applied.iter().any(|a| a == op), "op {op} not recorded when forced");
            if *op != "jpeg" {
                let diff: f32 = img.iter().zip(&base).map(|(a, b)| (a - b).abs()).sum();
                assert!(diff > 0.5, "op {op} recorded but changed ~no pixels (diff {diff})");
            }
        }
    }

    #[test]
    fn ink_ops_and_verso_change_pixels() {
        let (ink0, w) = test_strip();
        let mut rng = ChaCha20Rng::seed_from_u64(7);
        let mut ink = ink0.clone();
        let mut applied = Vec::new();
        ink_ops(&mut rng, &mut ink, w, H, 3, &mut applied, true, None, None, false);
        for name in ["ink_bleed", "ink_starve", "edge_noise"] {
            assert!(applied.iter().any(|a| a == name), "{name} missing under force");
        }
        let diff: f32 = ink.iter().zip(&ink0).map(|(a, b)| (a - b).abs()).sum();
        assert!(diff > 1.0, "ink ops changed ~nothing");
        let style = Style { bg_type: "flat".into(), polarity_light: false, severity: 2 };
        let (mut img, _, _) = compose(&mut rng, &ink0, w, H, &style);
        let base = img.clone();
        let mut ap2 = Vec::new();
        verso_bleed(&mut rng, &mut img, w, H, 2, Some((&ink0, w, H)), &mut ap2, None);
        assert!(ap2.iter().any(|a| a == "verso_ghost"));
        let diff2: f32 = img.iter().zip(&base).map(|(a, b)| (a - b).abs()).sum();
        assert!(diff2 > 0.5, "verso ghost changed ~nothing");
    }

    #[test]
    fn neighbor_spill_adds_full_ink_at_edges() {
        let (ink0, w) = test_strip();
        for seed in 0..6u64 {
            let mut rng = ChaCha20Rng::seed_from_u64(seed);
            let mut ink = ink0.clone();
            let mut ap = Vec::new();
            neighbor_spill(&mut rng, &mut ink, w, H, (&ink0, w, H), &mut ap);
            assert_eq!(ap.len(), 1, "spill must record itself");
            let top: f32 = ink[..4 * w].iter().sum::<f32>() - ink0[..4 * w].iter().sum::<f32>();
            let bot: f32 = ink[(H - 4) * w..].iter().sum::<f32>() - ink0[(H - 4) * w..].iter().sum::<f32>();
            assert!(top > 1.0 || bot > 1.0, "spill added no edge ink (seed {seed}: top {top} bot {bot})");
        }
    }

    #[test]
    fn rotation_never_clips_ink_off_canvas() {
        // width-capped rotation invariant: total darkness is preserved (clamp-to-edge sampling,
        // end displacement <= margin) even on wide strips at max severity.
        let w = 2000usize;
        let mut ink = vec![0f32; H * w];
        for x in 4..w - 4 {
            for y in 20..30 {
                ink[y * w + x] = 1.0;
            }
        }
        let mut rng = ChaCha20Rng::seed_from_u64(3);
        let style = Style { bg_type: "flat".into(), polarity_light: false, severity: 3 };
        let (img0, _, _) = compose(&mut rng, &ink, w, H, &style);
        let dark0: f32 = img0.iter().map(|p| (0.9 - p).max(0.0)).sum();
        for seed in 0..8u64 {
            let mut r = ChaCha20Rng::seed_from_u64(seed);
            let mut img = img0.clone();
            let mut ap = Vec::new();
            image_ops(&mut r, &mut img, w, H, 3, &mut ap, Phase::Geo, false, Some("rotate"), None, &OpCtx::default());
            let dark1: f32 = img.iter().map(|p| (0.9 - p).max(0.0)).sum();
            assert!(dark1 > dark0 * 0.93, "rotation lost ink: {dark1} vs {dark0} (seed {seed})");
        }
    }

    fn crop_cfg(canonical: f64, tight: f64, loose: f64) -> crate::recipe::CropCfg {
        let mut c = crate::recipe::CropCfg::default();
        c.enabled = true;
        c.mix.canonical = canonical;
        c.mix.tight = tight;
        c.mix.loose = loose;
        c
    }

    #[test]
    fn crop_canonical_is_identity() {
        let (ink, w) = test_strip();
        let mut rng = ChaCha20Rng::seed_from_u64(1);
        let style = Style { bg_type: "flat".into(), polarity_light: false, severity: 1 };
        let (img, _, _) = compose(&mut rng, &ink, w, H, &style);
        let mut cfg = crop_cfg(1.0, 0.0, 0.0);
        cfg.l_margin_prob = 0.0;
        cfg.r_margin_prob = 0.0; // isolate: no margins so canonical is a pure identity
        let mut ap = Vec::new();
        let (out, nw, drops, _bs) = detector_crop(&mut rng, &img, w, 14, 34, true, false, &[], &cfg, &mut ap);
        assert_eq!(nw, w);
        assert_eq!(out, img, "canonical stratum must be a pixel-exact identity");
        assert!(drops.is_empty());
        assert!(ap.iter().any(|a| a == "crop:canonical"));
    }

    #[test]
    fn crop_preserves_height_and_length() {
        let (ink, w) = test_strip();
        let style = Style { bg_type: "flat".into(), polarity_light: false, severity: 1 };
        for (cn, ct, cl) in [(0.0, 1.0, 0.0), (0.0, 0.0, 1.0)] {
            let cfg = crop_cfg(cn, ct, cl);
            for seed in 0..12u64 {
                let mut rng = ChaCha20Rng::seed_from_u64(seed);
                let (img, _, _) = compose(&mut rng, &ink, w, H, &style);
                let mut ap = Vec::new();
                let (out, nw, drops, _bs) =
                    detector_crop(&mut rng, &img, w, 14, 34, true, false, &[], &cfg, &mut ap);
                assert_eq!(out.len(), H * nw, "output must be 48×new_w (seed {seed})");
                assert!(nw >= crate::render::MIN_W && nw <= crate::render::MAX_W, "width in bounds");
                assert!(drops.is_empty(), "no marks supplied ⇒ no drops (seed {seed})");
            }
        }
    }

    #[test]
    fn auto_repair_drops_truly_cleared_accent_not_the_one_over_the_vowel() {
        // Two accents over vowels (x-height top = row 14):
        //   HIGH  (gt_idx 3): OWN ink rows 4..8  — sits well above x-height, a deep crop clears it entirely.
        //   REPRESENTATIVE (gt_idx 7): OWN ink rows 11..14 — 1..3px above x-height, directly over its vowel;
        //     its own ink survives every legal cut, so it must NEVER be dropped (F1: the base-body ink below
        //     it is NOT in the own profile, so removing base contamination must not spuriously drop it).
        // Survival is measured on each mark's OWN profile, not the image, so the image only sets crop geometry.
        let w = 160usize;
        let mut ink = vec![0f32; H * w];
        for y in 12..30 { for x in 30..150 { ink[y * w + x] = 1.0; } } // two vowel bodies (x-height..descender)
        for y in 4..8 { for x in 55..65 { ink[y * w + x] = 1.0; } }    // HIGH accent ink (sets i0=4)
        for y in 11..14 { for x in 100..110 { ink[y * w + x] = 1.0; } } // REPRESENTATIVE accent ink
        let style = Style { bg_type: "flat".into(), polarity_light: false, severity: 0 };
        let high = crate::render::MarkGeom { gt_idx: 3, is_top: true, row0: 4, own: vec![3.0; 4] };
        let repr = crate::render::MarkGeom { gt_idx: 7, is_top: true, row0: 11, own: vec![3.0; 3] };
        let marks = [high, repr];
        let mut cfg = crop_cfg(0.0, 1.0, 0.0);
        cfg.tight.t_max = 1.0;
        cfg.l_margin_prob = 0.0;
        cfg.r_margin_prob = 0.0;
        let mut cleared_dropped = false;
        for seed in 0..40u64 {
            let mut rng = ChaCha20Rng::seed_from_u64(seed);
            let (img, _, _) = compose(&mut rng, &ink, w, H, &style);
            let mut ap = Vec::new();
            let drops = detector_crop(&mut rng, &img, w, 14, 34, true, false, &marks, &cfg, &mut ap).2;
            assert!(!drops.contains(&7), "the accent over its vowel must never be dropped (seed {seed})");
            if drops.contains(&3) { cleared_dropped = true; }
        }
        assert!(cleared_dropped, "a truly-cleared HIGH accent must be auto-dropped on some deep crop");
        // canonical (no crop) never destroys anything → no drops
        let cfg2 = crop_cfg(1.0, 0.0, 0.0);
        let never = (0..20u64).all(|seed| {
            let mut rng = ChaCha20Rng::seed_from_u64(seed);
            let (img, _, _) = compose(&mut rng, &ink, w, H, &style);
            let mut ap = Vec::new();
            detector_crop(&mut rng, &img, w, 14, 34, true, false, &marks, &cfg2, &mut ap).2.is_empty()
        });
        assert!(never, "canonical (uncropped) never drops a mark");
    }

    // Opt-in visual check: render real Greek through the production render_ink path, apply
    // ink_transfer_v2 at s0..s3, dump a stacked PNG to eyeball-compare against the lab reference.
    //   cargo test -p linefactory dump_ink_transfer_gallery -- --ignored --nocapture
    #[test]
    #[ignore]
    fn dump_ink_transfer_gallery() {
        use unicode_normalization::UnicodeNormalization;
        let dir = "/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/assets/fonts";
        let pool = crate::render::FontPool::load(dir, &[]).expect("font pool");
        let stem = "GFSDidot_Classic";
        let fi = pool.fonts.iter().position(|f| f.stem == stem).expect("Didot Classic present");
        let texts = ["ἡ πόλις τοῦ δήμου καὶ", "ὁ λόγος ἦν πρὸς τὸν", "τῆς Ἑλλάδος ἱστορία"];
        let gap = 8usize;
        let mut rows: Vec<(usize, Vec<f32>)> = Vec::new(); // (w, ink 1=ink)
        for text in texts {
            let nfc: String = text.nfc().collect();
            let nfd: String = text.nfd().collect();
            if !pool.eligible(&nfc).contains(&fi) {
                eprintln!("SKIP (not covered by {stem}): {text}");
                continue;
            }
            let base = crate::render::render_ink(&pool.fonts[fi], &nfc, 0.0, 40.0, 0.0, &nfd, false).expect("render");
            rows.push((base.w, base.ink.clone())); // crisp reference
            for sev in 0u8..4 {
                let mut ink = base.ink.clone();
                let mut rng = ChaCha20Rng::seed_from_u64(1000 + sev as u64);
                let mut ap = Vec::new();
                ink_transfer_v2(&mut rng, &mut ink, base.w, H, sev, &mut ap);
                assert!(ap.iter().any(|a| a == "ink_transfer_v2"), "op did not record");
                rows.push((base.w, ink));
            }
        }
        let maxw = rows.iter().map(|(w, _)| *w).max().unwrap();
        let rh = H + gap;
        let total_h = rows.len() * rh;
        let mut canvas = vec![255u8; maxw * total_h];
        for (ri, (w, ink)) in rows.iter().enumerate() {
            let y0 = ri * rh;
            for y in 0..H {
                for x in 0..*w {
                    canvas[(y0 + y) * maxw + x] = ((1.0 - ink[y * w + x]).clamp(0.0, 1.0) * 255.0) as u8;
                }
            }
        }
        let out = "/Users/foivoskarounos-zamparloukos/letterpress_lab/runs/ink_dev/rust_port_gallery.png";
        image::GrayImage::from_raw(maxw as u32, total_h as u32, canvas)
            .expect("img")
            .save(out)
            .expect("save");
        eprintln!("wrote {out}  ({} rows = 3 texts × (crisp + s0..s3))", rows.len());
    }

    #[test]
    fn ink_transfer_v2_records_changes_and_is_deterministic() {
        let (ink0, w) = test_strip();
        let mut a = ink0.clone();
        let mut ap = Vec::new();
        let mut r1 = ChaCha20Rng::seed_from_u64(99);
        ink_transfer_v2(&mut r1, &mut a, w, H, 3, &mut ap);
        assert!(ap.iter().any(|x| x == "ink_transfer_v2"), "op must record itself");
        let diff: f32 = a.iter().zip(&ink0).map(|(x, y)| (x - y).abs()).sum();
        assert!(diff > 0.5, "ink_transfer_v2 recorded but changed ~nothing (diff {diff})");
        // determinism: same seed ⇒ byte-identical output (shard reproducibility)
        let mut b = ink0.clone();
        let mut ap2 = Vec::new();
        let mut r2 = ChaCha20Rng::seed_from_u64(99);
        ink_transfer_v2(&mut r2, &mut b, w, H, 3, &mut ap2);
        assert_eq!(a, b, "same seed must give identical output");
    }

    #[test]
    fn ink_transfer_v2_honors_per_letter_absent_cap() {
        // invariant: a worn sort breaks but never fully vanishes — per-letter absent (ink→0) ≤ ~50%.
        let (ink0, w) = test_strip();
        let runs = letter_runs(&ink0, w, H);
        assert!(runs.len() > 3, "test strip should have several letters");
        for seed in 0..24u64 {
            let mut ink = ink0.clone();
            let mut ap = Vec::new();
            let mut rng = ChaCha20Rng::seed_from_u64(seed);
            ink_transfer_v2(&mut rng, &mut ink, w, H, 3, &mut ap);
            for &(c0, c1) in &runs {
                let idx: Vec<usize> = (0..H).flat_map(|y| (c0..c1).map(move |x| y * w + x)).filter(|&i| ink0[i] > 0.45).collect();
                if idx.len() < 8 {
                    continue;
                }
                let gone = idx.iter().filter(|&&i| ink[i] == 0.0).count();
                // 0.55 tolerance: the 0.50 cap plus quantile/rounding slack on tiny synthetic runs.
                assert!(
                    gone as f32 <= 0.55 * idx.len() as f32,
                    "letter {c0}..{c1} lost {gone}/{} ink pixels — cap breached (seed {seed})",
                    idx.len()
                );
            }
        }
    }

    #[test]
    fn letterpress_ink_ops_swaps_amount_ops_for_transfer_keeps_edge_noise() {
        let (ink0, w) = test_strip();
        let mut edge_seen = false;
        for seed in 0..16u64 {
            let mut ink = ink0.clone();
            let mut ap = Vec::new();
            let mut rng = ChaCha20Rng::seed_from_u64(seed);
            ink_ops(&mut rng, &mut ink, w, H, 3, &mut ap, false, None, None, true);
            assert!(ap.iter().any(|x| x == "ink_transfer_v2"), "transfer must run for cohort (seed {seed})");
            for banned in ["ink_bleed", "ink_starve", "stroke_loss"] {
                assert!(!ap.iter().any(|x| x == banned), "{banned} must NOT run for the cohort (seed {seed})");
            }
            if ap.iter().any(|x| x == "edge_noise") {
                edge_seen = true;
            }
        }
        assert!(edge_seen, "edge_noise (kept for the cohort) should fire on some seed");
    }

    // ---- F2 poison probes (spec invariants.poison_probes) ----
    fn mask_of(ink: &[f32]) -> Vec<bool> { ink.iter().map(|&v| v > 0.45).collect() }

    /// count 4-connected components of `want`-valued pixels with size >= min_sz (iterative flood fill).
    fn count_components(px: &[bool], w: usize, h: usize, want: bool, min_sz: usize) -> usize {
        let mut seen = vec![false; w * h];
        let mut n = 0;
        for start in 0..w * h {
            if seen[start] || px[start] != want { continue; }
            let mut stack = vec![start];
            seen[start] = true;
            let mut sz = 0;
            while let Some(i) = stack.pop() {
                sz += 1;
                let (x, y) = (i % w, i / w);
                let mut push = |nx: usize, ny: usize, st: &mut Vec<usize>, sn: &mut Vec<bool>| {
                    let j = ny * w + nx;
                    if !sn[j] && px[j] == want { sn[j] = true; st.push(j); }
                };
                if x > 0 { push(x - 1, y, &mut stack, &mut seen); }
                if x + 1 < w { push(x + 1, y, &mut stack, &mut seen); }
                if y > 0 { push(x, y - 1, &mut stack, &mut seen); }
                if y + 1 < h { push(x, y + 1, &mut stack, &mut seen); }
            }
            if sz >= min_sz { n += 1; }
        }
        n
    }

    /// enclosed background holes (counters): background components not reachable from the border.
    fn count_holes(mask: &[bool], w: usize, h: usize) -> usize {
        // flood the OUTSIDE background from every border pixel, then count the remaining bg components.
        let mut outside = vec![false; w * h];
        let mut stack: Vec<usize> = Vec::new();
        for x in 0..w { for &y in &[0usize, h - 1] { let i = y * w + x; if !mask[i] && !outside[i] { outside[i] = true; stack.push(i); } } }
        for y in 0..h { for &x in &[0usize, w - 1] { let i = y * w + x; if !mask[i] && !outside[i] { outside[i] = true; stack.push(i); } } }
        while let Some(i) = stack.pop() {
            let (x, y) = (i % w, i / w);
            let mut push = |nx: usize, ny: usize, st: &mut Vec<usize>, o: &mut Vec<bool>| {
                let j = ny * w + nx;
                if !o[j] && !mask[j] { o[j] = true; st.push(j); }
            };
            if x > 0 { push(x - 1, y, &mut stack, &mut outside); }
            if x + 1 < w { push(x + 1, y, &mut stack, &mut outside); }
            if y > 0 { push(x, y - 1, &mut stack, &mut outside); }
            if y + 1 < h { push(x, y + 1, &mut stack, &mut outside); }
        }
        // enclosed = background pixels not reached from the border; count components >= 3px.
        let enclosed: Vec<bool> = (0..w * h).map(|i| !mask[i] && !outside[i]).collect();
        count_components(&enclosed, w, h, true, 3)
    }

    #[test]
    fn ink_transfer_v2_poison_probes_holes_and_merges() {
        // The morphological close must not FILL too many counters (hole-survival >= 0.35) nor MERGE too
        // many letters (CC ratio >= 0.5). Real counter-rich Greek, max severity, across seeds.
        use unicode_normalization::UnicodeNormalization;
        let dir = "/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/assets/fonts";
        let pool = crate::render::FontPool::load(dir, &[]).expect("pool");
        let fi = pool.fonts.iter().position(|f| f.stem == "GFSDidot_Classic").expect("didot");
        let text = "ἡ πόλις τοῦ δήμου καὶ ὁ λόγος βασιλεία";
        let nfc: String = text.nfc().collect();
        let nfd: String = text.nfd().collect();
        let base = crate::render::render_ink(&pool.fonts[fi], &nfc, 0.0, 40.0, 0.0, &nfd, false).expect("render");
        let (w, m0) = (base.w, mask_of(&base.ink));
        let holes0 = count_holes(&m0, w, H);
        let cc0 = count_components(&m0, w, H, true, 4);
        assert!(holes0 >= 5 && cc0 >= 5, "probe text should have counters + components (holes {holes0}, cc {cc0})");
        for seed in 0..12u64 {
            let mut ink = base.ink.clone();
            let mut ap = Vec::new();
            let mut rng = ChaCha20Rng::seed_from_u64(seed);
            ink_transfer_v2(&mut rng, &mut ink, w, H, 3, &mut ap);
            let m1 = mask_of(&ink);
            let holes1 = count_holes(&m1, w, H);
            let cc1 = count_components(&m1, w, H, true, 4);
            assert!(holes1 as f32 >= 0.35 * holes0 as f32, "hole-survival {holes1}/{holes0} < 0.35 (seed {seed})");
            assert!(cc1 as f32 >= 0.5 * cc0 as f32, "CC-merge {cc1}/{cc0} < 0.5 (seed {seed})");
        }
    }

    #[test]
    fn ink_transfer_v2_preserves_bottom_band_ink() {
        // ypogegrammeni poison guard: band_protect + per-letter cap must retain most bottom-band ink at
        // max severity (the empirically first casualty; no build-time repair covers the bottom band).
        let w = 320usize;
        let mut ink0 = vec![0f32; H * w];
        for cx in (12..w - 12).step_by(18) {
            for y in 14..34 { for x in cx..(cx + 9).min(w) { ink0[y * w + x] = 1.0; } } // body
            for y in 40..46 { for x in cx + 2..(cx + 6).min(w) { ink0[y * w + x] = 1.0; } } // bottom mark
        }
        let base_cnt = (40..H).flat_map(|y| (0..w).map(move |x| y * w + x)).filter(|&i| ink0[i] > 0.45).count() as f32;
        assert!(base_cnt > 20.0);
        for seed in 0..16u64 {
            let mut ink = ink0.clone();
            let mut ap = Vec::new();
            let mut rng = ChaCha20Rng::seed_from_u64(seed);
            ink_transfer_v2(&mut rng, &mut ink, w, H, 3, &mut ap);
            let kept = (40..H).flat_map(|y| (0..w).map(move |x| y * w + x)).filter(|&i| ink0[i] > 0.45 && ink[i] > 0.0).count() as f32;
            assert!(kept >= 0.5 * base_cnt, "bottom-band retention {kept}/{base_cnt} < 0.5 (seed {seed})");
        }
    }
}
