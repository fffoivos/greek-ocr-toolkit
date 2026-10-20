//! Audit hard-gate: realized-vs-recipe marginals PLUS the config-independent appearance band
//! (the lesson from the sibling program: a recipe can declare an OOD distribution and pass a
//! realized-vs-declared audit — the band file is measured from real pages and gates regardless).

use crate::recipe::Recipe;
use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

/// Metadata-only view of a built row (no image bytes).
pub struct RowMeta {
    pub script_class: String,
    pub split: String,
    pub severity: u8,
    pub polarity_light: bool,
    pub bg_type: String,
    pub font: String,
    pub accent_survival: f32,
    pub has_top_marks: bool,
    pub reuse_index: u32,
    pub gt_len: usize,
    pub source_dataset: String,
    pub source_doc_id: String,
    pub contrast: f32,
    /// minted into the letterpress ink cohort (`ink_transfer_v2` ran + historical-cut routing).
    /// Equivalent to `applied_ops ∋ "ink_transfer_v2"` since the op always records itself.
    pub letterpress: bool,
    /// the lunate-sigma rewrite (σ→ς) was applied to this row (INDEPENDENT of `letterpress`).
    pub lunate: bool,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct AppearanceBand {
    /// measured from real page crops via `linefactory measure`
    pub min_dark_on_light: f64,
    pub contrast_p50_range: [f32; 2],
    #[serde(default)]
    pub note: String,
}

#[derive(Serialize)]
pub struct Check {
    pub name: String,
    pub ok: bool,
    pub detail: serde_json::Value,
}

#[derive(Serialize)]
pub struct AuditReport {
    pub ok: bool,
    pub n_rows: usize,
    pub checks: Vec<Check>,
}

fn frac<T: PartialEq>(rows: &[&RowMeta], f: impl Fn(&RowMeta) -> T, v: T) -> f64 {
    if rows.is_empty() {
        return 0.0;
    }
    rows.iter().filter(|r| f(r) == v).count() as f64 / rows.len() as f64
}

pub fn audit(
    rows: &[RowMeta],
    recipe: &Recipe,
    band: Option<&AppearanceBand>,
    drops: &BTreeMap<String, usize>,
    repairs: &BTreeMap<String, usize>,
) -> Result<AuditReport> {
    let mut checks = Vec::new();
    let main: Vec<&RowMeta> = rows.iter().filter(|r| recipe.eval_only.is_some() || r.split != "reserved").collect();
    if let Some(eval) = &recipe.eval_only {
        checks.push(Check { name: "eval_only_strata".into(),
            ok: !rows.is_empty() && rows.iter().all(|r| r.split == "reserved" && eval.fonts.contains(&r.font))
                && eval.minimum_class_counts.iter().all(|(c, n)| rows.iter().filter(|r| &r.script_class == c).count() >= *n),
            detail: serde_json::json!({"minimum_class_counts": eval.minimum_class_counts, "fonts": eval.fonts}) });
    }
    let n = main.len().max(1);

    // 1. content marginals (tol 0.03 abs)
    {
        let mut detail = serde_json::Map::new();
        let mut worst = 0.0f64;
        for (k, want) in &recipe.content_marginals {
            let got = frac(&main, |r| r.script_class.clone(), k.clone());
            worst = worst.max((got - want).abs());
            detail.insert(k.clone(), serde_json::json!({"want": want, "got": got}));
        }
        checks.push(Check {
            name: "content_marginals".into(),
            ok: worst <= 0.03,
            detail: serde_json::json!({"worst_abs_drift": worst, "per_class": detail}),
        });
    }
    // 2. severity / polarity / bg marginals — n-AWARE tolerance: max(0.04, 2.5·SE(p,n)), so
    // fixture-scale builds don't false-quarantine on sampling noise while 200k builds keep the
    // tight bound (the sibling builder's n-aware-TVD practice).
    {
        let tot: f64 = recipe.severity_weights.iter().sum();
        let nn = n as f64;
        let mut ok2 = true;
        let mut det = vec![];
        for s in 0..4u8 {
            let want = recipe.severity_weights[s as usize] / tot;
            let got = frac(&main, |r| r.severity, s);
            let tol = (2.5 * (want * (1.0 - want) / nn).sqrt()).max(0.04);
            if (got - want).abs() > tol {
                ok2 = false;
            }
            det.push(serde_json::json!({"sev": s, "want": want, "got": got, "tol": tol}));
        }
        let pol = frac(&main, |r| r.polarity_light, true);
        let pw = recipe.polarity_light_fraction;
        let pol_tol = (2.5 * (pw * (1.0 - pw) / nn).sqrt()).max(0.015);
        let pol_ok = (pol - pw).abs() <= pol_tol;
        checks.push(Check {
            name: "distortion_marginals".into(),
            ok: ok2 && pol_ok,
            detail: serde_json::json!({"severity": det, "polarity_light": pol, "polarity_tol": pol_tol}),
        });
    }
    // 3. shared appearance band check
    checks.push(appearance_check(&main, band));
    // 4. reuse invariant (re-verified on rows, not trusted from select)
    {
        let mx = rows.iter().map(|r| r.reuse_index + 1).max().unwrap_or(0);
        let mut hist: BTreeMap<u32, usize> = BTreeMap::new();
        for r in rows {
            *hist.entry(r.reuse_index).or_default() += 1;
        }
        checks.push(Check {
            name: "reuse_cap".into(),
            ok: mx as usize <= recipe.reuse.max_per_line,
            detail: serde_json::json!({"max_renders": mx, "cap": recipe.reuse.max_per_line, "hist": hist}),
        });
    }
    // 5. accent survival p10 over top-marked strips
    {
        let mut s: Vec<f32> = main.iter().filter(|r| r.has_top_marks).map(|r| r.accent_survival).collect();
        s.sort_by(|a, b| a.partial_cmp(b).unwrap());
        let p10 = s.get(s.len() / 10).copied().unwrap_or(1.0);
        checks.push(Check {
            name: "accent_survival".into(),
            ok: p10 >= recipe.accent_survival_floor,
            detail: serde_json::json!({"p10": p10, "floor": recipe.accent_survival_floor, "n_marked": s.len()}),
        });
    }
    // 6. shared length-distribution check
    checks.push(length_check(&main, recipe));
    // 7. concentration (report; pool caps already enforced pre-IPF)
    {
        let mut by_src: BTreeMap<String, usize> = BTreeMap::new();
        let mut by_doc: BTreeMap<String, usize> = BTreeMap::new();
        for r in &main {
            *by_src.entry(r.source_dataset.clone()).or_default() += 1;
            if !r.source_doc_id.is_empty() {
                *by_doc.entry(format!("{}:{}", r.source_dataset, r.source_doc_id)).or_default() += 1;
            }
        }
        let top_src = by_src.iter().max_by_key(|(_, v)| **v).map(|(k, v)| (k.clone(), *v));
        let top_doc = by_doc.iter().max_by_key(|(_, v)| **v).map(|(k, v)| (k.clone(), *v));
        checks.push(Check {
            name: "concentration".into(),
            ok: true, // report-only; enforcement is pre-IPF pool caps
            detail: serde_json::json!({"top_source": top_src, "top_doc": top_doc, "distinct_docs": by_doc.len(), "n_sources": by_src.len()}),
        });
    }
    // 8. drop accounting (visible truncation; gate on excessive coverage loss)
    {
        let total_drops: usize = drops.values().sum();
        let rate = total_drops as f64 / (rows.len() + total_drops).max(1) as f64;
        checks.push(Check {
            name: "drop_accounting".into(),
            ok: rate <= 0.02,
            detail: serde_json::json!({"drops": drops, "repairs": repairs, "drop_rate": rate, "policy": "repair-not-drop; drops only for no-eligible-font/too-wide/unrenderable"}),
        });
    }
    // 9. per-font coverage spread (no single font dominating)
    {
        let mut by_font: BTreeMap<String, usize> = BTreeMap::new();
        for r in &main {
            *by_font.entry(r.font.clone()).or_default() += 1;
        }
        let top = by_font.values().max().copied().unwrap_or(0) as f64 / n as f64;
        checks.push(Check {
            name: "font_spread".into(),
            ok: top <= recipe.eval_only.as_ref().map(|e| e.max_font_share).unwrap_or(0.25),
            detail: serde_json::json!({"n_fonts_used": by_font.len(), "top_share": top, "per_font": by_font,
                "max_share": recipe.eval_only.as_ref().map(|e| e.max_font_share).unwrap_or(0.25)}),
        });
    }

    // 10. letterpress cohort (gated on recipe.ink_transfer.enabled): realized share of the greek block,
    //     mark survival on the cohort (the poison-probe gate — the ink model must not erase accents),
    //     and historical-font routing. Named letterpress_RENDERED (synthetic regime, never `_real`).
    {
        let lp: Vec<&&RowMeta> = main.iter().filter(|r| r.letterpress).collect();
        let greek_n = main.iter().filter(|r| r.script_class.starts_with("greek")).count();
        let realized_of_greek = if greek_n == 0 { 0.0 } else { lp.len() as f64 / greek_n as f64 };
        let mut cs: Vec<f32> = lp.iter().filter(|r| r.has_top_marks).map(|r| r.accent_survival).collect();
        cs.sort_by(|a, b| a.partial_cmp(b).unwrap());
        let cs_p10 = cs.get(cs.len() / 10).copied().unwrap_or(1.0);
        let hist = &recipe.ink_transfer.historical_fonts;
        let non_hist = lp.iter().filter(|r| !hist.iter().any(|h| h == &r.font)).count();
        // INDEPENDENT lunate set: realized fraction of greek, and how many lunate rows are ALSO degraded
        // (should track the independent degrade rate, not 100% — proves lunate ⊥ degradation).
        let lun: Vec<&&RowMeta> = main.iter().filter(|r| r.lunate).collect();
        let lun_of_greek = if greek_n == 0 { 0.0 } else { lun.len() as f64 / greek_n as f64 };
        let lun_also_degraded = if lun.is_empty() { 0.0 } else { lun.iter().filter(|r| r.letterpress).count() as f64 / lun.len() as f64 };
        let (ok, gating) = if recipe.ink_transfer.enabled {
            let want = recipe.ink_transfer.cohort_fraction;
            let nn = greek_n.max(1) as f64;
            let tol = (3.0 * (want * (1.0 - want) / nn).sqrt()).max(0.05);
            let frac_ok = (realized_of_greek - want).abs() <= tol;
            let surv_ok = cs.is_empty() || cs_p10 >= recipe.accent_survival_floor;
            (frac_ok && surv_ok, true)
        } else {
            (lp.is_empty() && lun.is_empty(), false) // disabled ⇒ zero cohort AND zero lunate rows
        };
        checks.push(Check {
            name: "letterpress_cohort".into(),
            ok,
            detail: serde_json::json!({
                "gating": gating,
                "enabled": recipe.ink_transfer.enabled,
                "n_letterpress_rendered": lp.len(),
                "realized_fraction_of_greek": realized_of_greek,
                "target_cohort_fraction": recipe.ink_transfer.cohort_fraction,
                "cohort_accent_survival_p10": cs_p10,
                "accent_survival_floor": recipe.accent_survival_floor,
                "non_historical_font_rows": non_hist,
                "lunate_rows": lun.len(),
                "lunate_fraction_of_greek": lun_of_greek,
                "lunate_target": recipe.ink_transfer.lunate_sigma_fraction,
                "lunate_also_degraded_fraction": lun_also_degraded,
                "note": "letterpress_rendered (synthetic regime, never labeled _real); survival is the poison-probe gate on the ink model; lunate is an INDEPENDENT draw (lunate_also_degraded should ≈ cohort_fraction, not 1.0)"
            }),
        });
    }

    let ok = checks.iter().all(|c| c.ok);
    Ok(AuditReport { ok, n_rows: rows.len(), checks })
}

/// Shared appearance check. Real imports report the result without applying a synthetic marginal gate.
pub fn appearance_check(main: &[&RowMeta], band: Option<&AppearanceBand>) -> Check {
    let dark = 1.0 - frac(&main, |r| r.polarity_light, true);
    let mut cts: Vec<f32> = main.iter().map(|r| r.contrast).collect();
    cts.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let c50 = cts.get(cts.len() / 2).copied().unwrap_or(0.0);
    match band {
        Some(b) => {
            let ok = dark >= b.min_dark_on_light
                && c50 >= b.contrast_p50_range[0]
                && c50 <= b.contrast_p50_range[1];
            Check {
                name: "appearance_band".into(),
                ok,
                detail: serde_json::json!({"band": b, "realized": {"dark_on_light": dark, "contrast_p50": c50}}),
            }
        }
        None => Check {
            name: "appearance_band".into(),
            ok: true,
            detail: serde_json::json!({"gating": false, "realized": {"dark_on_light": dark, "contrast_p50": c50}, "note": "no band file supplied — measure real pages and set recipe.appearance_band before a build of record"}),
        },
    }
}

/// Shared length-distribution report; importer additionally lists per-record length warnings.
pub fn length_check(main: &[&RowMeta], recipe: &Recipe) -> Check {
    let nf: Vec<&&RowMeta> = main.iter().filter(|r| r.script_class != "furniture").collect();
    let long = nf.iter().filter(|r| r.gt_len >= recipe.lengths.long_chars).count() as f64
        / nf.len().max(1) as f64;
    let mut hist: BTreeMap<String, usize> = BTreeMap::new();
    for r in main {
        *hist.entry(format!("{:03}", (r.gt_len / 20) * 20)).or_default() += 1;
    }
    Check {
        name: "length_distribution".into(),
        ok: long >= recipe.lengths.long_min_fraction,
        detail: serde_json::json!({"long_fraction": long, "min": recipe.lengths.long_min_fraction, "hist_by_20": hist}),
    }
}
