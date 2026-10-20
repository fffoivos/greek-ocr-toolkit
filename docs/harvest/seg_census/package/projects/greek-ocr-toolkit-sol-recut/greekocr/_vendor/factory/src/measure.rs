//! `linefactory measure` — derive the appearance band from REAL page/line crops so the audit
//! gates against measured reality, never against the recipe's own declarations.

use anyhow::{bail, Context, Result};
use serde::Serialize;

#[derive(Serialize)]
struct Stats {
    n_images: usize,
    dark_on_light_fraction: f64,
    contrast_p10: f32,
    contrast_p50: f32,
    contrast_p90: f32,
    ink_fraction_p50: f32,
    // letterpress instrument stats (guidance §7.4): the ink-model signatures a contrast/ink-fraction
    // band can't see. stroke_width = 2× the distance-transform depth inside strokes; blob_frac = the
    // over-inked/merged mass (deep-interior pixels). Measured from real crops, they let a future
    // letterpress appearance band gate the ink_transfer_v2 cohort. Per-image medians, then p50/p90.
    stroke_width_p50: f32,
    stroke_width_p90: f32,
    blob_frac_p50: f32,
}

/// Chamfer distance from the nearest non-ink pixel (depth INTO strokes), 2-pass — kept local to
/// `measure` so it has no cross-module coupling.
fn dist_inside(mask: &[bool], w: usize, h: usize) -> Vec<f32> {
    let big = 1e6f32;
    let mut d: Vec<f32> = mask.iter().map(|&m| if m { big } else { 0.0 }).collect();
    for y in 0..h {
        for x in 0..w {
            let i = y * w + x;
            if d[i] == 0.0 { continue; }
            let mut m = d[i];
            if x > 0 { m = m.min(d[i - 1] + 1.0); }
            if y > 0 {
                m = m.min(d[i - w] + 1.0);
                if x > 0 { m = m.min(d[i - w - 1] + 1.41421); }
                if x + 1 < w { m = m.min(d[i - w + 1] + 1.41421); }
            }
            d[i] = m;
        }
    }
    for y in (0..h).rev() {
        for x in (0..w).rev() {
            let i = y * w + x;
            if d[i] == 0.0 { continue; }
            let mut m = d[i];
            if x + 1 < w { m = m.min(d[i + 1] + 1.0); }
            if y + 1 < h {
                m = m.min(d[i + w] + 1.0);
                if x + 1 < w { m = m.min(d[i + w + 1] + 1.41421); }
                if x > 0 { m = m.min(d[i + w - 1] + 1.41421); }
            }
            d[i] = m;
        }
    }
    d
}

pub fn measure(images_dir: &str, out: &str) -> Result<()> {
    let mut contrasts: Vec<f32> = Vec::new();
    let mut ink_fracs: Vec<f32> = Vec::new();
    let mut stroke_meds: Vec<f32> = Vec::new();
    let mut stroke_p90s: Vec<f32> = Vec::new();
    let mut blob_fracs: Vec<f32> = Vec::new();
    let mut dark = 0usize;
    let mut n = 0usize;
    let mut paths: Vec<_> = walkdir::WalkDir::new(images_dir)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| {
            e.path()
                .extension()
                .and_then(|x| x.to_str())
                .is_some_and(|x| matches!(x.to_lowercase().as_str(), "png" | "jpg" | "jpeg" | "tif" | "tiff"))
        })
        .map(|e| e.path().to_owned())
        .collect();
    paths.sort();
    for p in paths {
        let img = match image::open(&p) {
            Ok(i) => i.to_luma8(),
            Err(e) => {
                eprintln!("[measure] skip {p:?}: {e}");
                continue;
            }
        };
        let (iw, ih) = (img.width() as usize, img.height() as usize);
        let px: Vec<f32> = img.pixels().map(|p| p.0[0] as f32 / 255.0).collect();
        if px.len() < 256 {
            continue;
        }
        let mut sorted = px.clone();
        sorted.sort_by(|a, b| a.partial_cmp(b).unwrap());
        let p05 = sorted[(sorted.len() as f32 * 0.05) as usize];
        let p95 = sorted[(sorted.len() as f32 * 0.95) as usize];
        let thr = (p05 + p95) / 2.0;
        let ink_frac = px.iter().filter(|v| **v < thr).count() as f32 / px.len() as f32;
        let contrast = p95 - p05;
        contrasts.push(contrast);
        ink_fracs.push(ink_frac);
        if ink_frac < 0.5 {
            dark += 1;
        }
        // stroke-width / blob-fraction via the in-stroke distance transform (dark = ink here; polarity
        // is handled by the < thr binarize, so light-on-dark crops still yield ink strokes).
        let mask: Vec<bool> = px.iter().map(|v| *v < thr).collect();
        let mut dt_ink: Vec<f32> = {
            let dt = dist_inside(&mask, iw, ih);
            dt.iter().zip(&mask).filter(|(_, &m)| m).map(|(d, _)| *d).collect()
        };
        if dt_ink.len() >= 64 {
            dt_ink.sort_by(|a, b| a.partial_cmp(b).unwrap());
            let med = dt_ink[dt_ink.len() / 2];
            let p90 = dt_ink[(dt_ink.len() as f32 * 0.90) as usize];
            // scale-invariant blob mass: ink pixels thicker than 1.6× the median depth = over-inked/
            // merged regions (letterpress fill), as a fraction of ink mass.
            let thick = (1.6 * med).max(1.0);
            let blob = dt_ink.iter().filter(|d| **d >= thick).count() as f32 / dt_ink.len() as f32;
            stroke_meds.push(2.0 * med);
            stroke_p90s.push(2.0 * p90);
            blob_fracs.push(blob);
        }
        n += 1;
    }
    if n == 0 {
        bail!("no readable images under {images_dir}");
    }
    contrasts.sort_by(|a, b| a.partial_cmp(b).unwrap());
    ink_fracs.sort_by(|a, b| a.partial_cmp(b).unwrap());
    stroke_meds.sort_by(|a, b| a.partial_cmp(b).unwrap());
    stroke_p90s.sort_by(|a, b| a.partial_cmp(b).unwrap());
    blob_fracs.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let q = |v: &Vec<f32>, f: f32| v[((v.len() - 1) as f32 * f) as usize];
    let q0 = |v: &Vec<f32>, f: f32| if v.is_empty() { 0.0 } else { q(v, f) };
    let stats = Stats {
        n_images: n,
        dark_on_light_fraction: dark as f64 / n as f64,
        contrast_p10: q(&contrasts, 0.10),
        contrast_p50: q(&contrasts, 0.50),
        contrast_p90: q(&contrasts, 0.90),
        ink_fraction_p50: q(&ink_fracs, 0.50),
        stroke_width_p50: q0(&stroke_meds, 0.50),
        stroke_width_p90: q0(&stroke_p90s, 0.90),
        blob_frac_p50: q0(&blob_fracs, 0.50),
    };
    // Lenient derived gates: a correct build clears them with margin; the point is catching
    // whole-distribution divergence (50%-inverted-class bugs), not micro-managing the recipe.
    let band = serde_json::json!({
        "min_dark_on_light": (stats.dark_on_light_fraction - 0.05).clamp(0.5, 0.98),
        "contrast_p50_range": [
            (stats.contrast_p10 * 0.7).max(0.05),
            (stats.contrast_p90 * 1.2).min(1.0)
        ],
        "note": format!("derived by `linefactory measure` from {} real crops; stats: {}",
            n, serde_json::to_string(&stats).unwrap()),
    });
    std::fs::write(out, serde_json::to_string_pretty(&band)?).with_context(|| format!("write {out}"))?;
    eprintln!("[measure] {n} images -> {out}");
    Ok(())
}
