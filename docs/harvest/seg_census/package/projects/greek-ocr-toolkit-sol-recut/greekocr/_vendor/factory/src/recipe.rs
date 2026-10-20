//! Recipe — the single consumed source of truth for a build. Strict schema (unknown keys rejected).

use anyhow::{bail, Context, Result};
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

#[derive(Serialize, Deserialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct Recipe {
    /// Raw recipe bytes, distinct from the historical effective/serialized recipe hash.
    #[serde(skip)]
    pub source_sha256: Option<String>,
    #[serde(skip)]
    pub source_effective_sha256: Option<String>,
    pub target_total: usize,
    /// Versioned eval-only distribution; never eligible for training/validation.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub eval_only: Option<EvalOnly>,
    pub seed: u64,
    /// script_class -> fraction; keys from data_contracts §3. Must sum to 1 (±1e-6).
    pub content_marginals: BTreeMap<String, f64>,
    /// severity 0..=3 -> weight (normalized internally).
    pub severity_weights: [f64; 4],
    pub bg_weights: BgWeights,
    /// fraction of strips rendered light-on-dark (band-checked at audit).
    pub polarity_light_fraction: f64,
    pub fonts: Fonts,
    pub lengths: Lengths,
    /// Pre-IPF diversity caps, applied to the candidate POOL (lesson: never post-draw).
    pub pool_caps: PoolCaps,
    pub reuse: Reuse,
    /// per-codec-atom minimum occurrence count on selected TRAIN rows; deficits FAIL the build
    /// unless --allow-deficit, and are always listed in select_report.
    pub atom_floor: usize,
    /// fraction of greek lines that get letterspaced (gesperrt) rendering, per the 19c. book style.
    pub letterspacing_fraction: f64,
    /// crop-normalized render fit: the ink band targets this many px of the 48px strip (matches
    /// the inference pipeline's detector-crop resize semantics), jittered per strip.
    #[serde(default = "d_ink_target_h")]
    pub ink_target_h: f32,
    #[serde(default = "d_ink_fit_jitter")]
    pub ink_fit_jitter: f32,
    /// mark-ink survival floor; below it the strip is re-rendered one severity lower (REPAIR, never drop).
    pub accent_survival_floor: f32,
    /// minimum ink/bg contrast after distortion; below it → repair (same policy).
    pub ink_contrast_floor: f32,
    /// path to a measured appearance band JSON (from `linefactory measure`); audited against.
    pub appearance_band: Option<String>,
    /// directory of stamp/watermark alpha masks (*.png, 255=ink); None = procedural fallback.
    #[serde(default)]
    pub watermarks_dir: Option<String>,
    /// explicit eval-exclusion manifests (one NFD gt per line); missing file = HARD FAIL (fail-closed).
    pub exclusion_manifests: Vec<String>,
    /// detector-crop augmentation (I7/I8 reframe). Default = DISABLED; skipped on serialize when off so
    /// the recipe SHA (custody/provenance) is byte-identical to a crop-less recipe. See
    /// docs/crop_robustness_design.md.
    #[serde(default, skip_serializing_if = "CropCfg::is_disabled")]
    pub crop: CropCfg,
    /// letterpress ink cohort (`ink_transfer_v2`): a ~20% tail rendered in historical cuts with the
    /// field-driven ink model in place of the ink-amount ops. Default = DISABLED; skipped on serialize
    /// when off so the recipe SHA is byte-identical to a letterpress-less recipe (same guarantee as
    /// `crop`). See docs/reviews/ink_transfer_v2_design.md.
    #[serde(default, skip_serializing_if = "InkTransferCfg::is_disabled")]
    pub ink_transfer: InkTransferCfg,
}

#[derive(Serialize, Deserialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct EvalOnly {
    pub fonts: Vec<String>,
    pub minimum_class_counts: BTreeMap<String, usize>,
    pub max_font_share: f64,
}

fn d_ink_target_h() -> f32 {
    40.0
}
fn d_ink_fit_jitter() -> f32 {
    3.0
}

#[derive(Serialize, Deserialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct BgWeights {
    pub flat: f64,
    pub gradient: f64,
    pub textured: f64,
}

#[derive(Serialize, Deserialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct Fonts {
    pub dir: String,
    /// font file stems NEVER used for training strips (permanent font-OOD eval slice).
    pub held_out: Vec<String>,
}

#[derive(Serialize, Deserialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct Lengths {
    pub min_chars: usize,
    pub max_chars: usize,
    /// minimum fraction of selected lines with >= long_chars characters.
    pub long_chars: usize,
    pub long_min_fraction: f64,
}

#[derive(Serialize, Deserialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct PoolCaps {
    /// max fraction of the candidate pool any one source_dataset may hold (0 disables).
    pub per_source_max_fraction: f64,
    /// max lines any one source_doc_id may contribute to the pool (0 disables).
    pub per_doc_max_lines: usize,
}

#[derive(Serialize, Deserialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct Reuse {
    /// HARD cap on renders per distinct line. No bypass path exists (lesson D-B).
    pub max_per_line: usize,
}

// ============================ detector-crop augmentation config ============================
// All fields carry named serde defaults so the crop block can be tuned PARTIALLY (owner: "decide max/mix
// later"). Disabled ⇒ the whole crop path is skipped in build.rs ⇒ byte-identical shards + recipe SHA.
#[derive(Serialize, Deserialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct CropCfg {
    /// master switch. false ⇒ no crop op runs (current factory behavior).
    #[serde(default)]
    pub enabled: bool,
    /// severity-INDEPENDENT fire rate for the op when a strip is eligible (like neighbor_spill's flat 0.18).
    #[serde(default = "d_crop_activation")]
    pub activation_prob: f64,
    /// canonical / tight / loose stratum weights (normalized internally).
    #[serde(default)]
    pub mix: CropMix,
    /// tight-crop cut maxima (fraction of the ink-band height, per edge).
    #[serde(default)]
    pub tight: TightCfg,
    /// loose-crop extra-headroom padding (fraction of band height, per side).
    #[serde(default)]
    pub loose: LooseCfg,
    /// probability a LEFT / RIGHT white margin is added (EXPAND only — side-contraction stays OFF).
    #[serde(default = "d_l_margin")]
    pub l_margin_prob: f64,
    #[serde(default = "d_r_margin")]
    pub r_margin_prob: f64,
    /// max added side margin as a fraction of strip height.
    #[serde(default = "d_margin_max")]
    pub margin_max: f64,
    /// AUTOMATIC per-mark GT label-repair (always on when cropping). The crop depth is set by `tight`/
    /// `loose` ALONE — never bounded by accent legibility. Repair is the auto-detector: a mark the crop
    /// pushes below `noise_floor` is dropped from the label, so raising the max is self-correcting. At a
    /// survivable max it fires ~never (accents stay > noise_floor); it exists for when the max is raised.
    #[serde(default)]
    pub repair: RepairCfg,
}

#[derive(Serialize, Deserialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct CropMix {
    #[serde(default = "d_mix_canonical")]
    pub canonical: f64,
    #[serde(default = "d_mix_tight")]
    pub tight: f64,
    #[serde(default = "d_mix_loose")]
    pub loose: f64,
}

#[derive(Serialize, Deserialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct TightCfg {
    #[serde(default = "d_tight_t")]
    pub t_max: f32,
    #[serde(default = "d_tight_b")]
    pub b_max: f32,
}

#[derive(Serialize, Deserialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct LooseCfg {
    #[serde(default = "d_loose_min")]
    pub pad_min: f32,
    #[serde(default = "d_loose_max")]
    pub pad_max: f32,
}

#[derive(Serialize, Deserialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct RepairCfg {
    /// mark surviving-ink fraction below which the mark is DROPPED from gt_nfd (the ~noise floor).
    #[serde(default = "d_noise_floor")]
    pub noise_floor: f32,
}

fn d_crop_activation() -> f64 { 0.35 }
fn d_l_margin() -> f64 { 0.12 }
fn d_r_margin() -> f64 { 0.22 }
fn d_margin_max() -> f64 { 1.8 }
fn d_mix_canonical() -> f64 { 0.50 }
fn d_mix_tight() -> f64 { 0.30 }
fn d_mix_loose() -> f64 { 0.20 }
fn d_tight_t() -> f32 { 0.60 }
fn d_tight_b() -> f32 { 0.55 }
fn d_loose_min() -> f32 { 0.15 }
fn d_loose_max() -> f32 { 0.60 }
fn d_noise_floor() -> f32 { 0.03 }

impl Default for CropCfg {
    fn default() -> Self {
        CropCfg {
            enabled: false,
            activation_prob: d_crop_activation(),
            mix: CropMix::default(),
            tight: TightCfg::default(),
            loose: LooseCfg::default(),
            l_margin_prob: d_l_margin(),
            r_margin_prob: d_r_margin(),
            margin_max: d_margin_max(),
            repair: RepairCfg::default(),
        }
    }
}
impl Default for CropMix {
    fn default() -> Self { CropMix { canonical: d_mix_canonical(), tight: d_mix_tight(), loose: d_mix_loose() } }
}
impl Default for TightCfg {
    fn default() -> Self { TightCfg { t_max: d_tight_t(), b_max: d_tight_b() } }
}
impl Default for LooseCfg {
    fn default() -> Self { LooseCfg { pad_min: d_loose_min(), pad_max: d_loose_max() } }
}
impl Default for RepairCfg {
    fn default() -> Self { RepairCfg { noise_floor: d_noise_floor() } }
}
impl CropCfg {
    /// used by skip_serializing_if — a disabled crop is inert, so we omit it entirely (SHA stability).
    pub fn is_disabled(&self) -> bool { !self.enabled }
}

/// Letterpress ink cohort. The severity→defect bands (absent/faint/spillage/type-height/roller/
/// pressure per s0..s3) are FROZEN inside `distort::ink_transfer_v2` (owner-eyeball-approved,
/// `~/letterpress_lab/regimes/ink_transfer_v2.json`) — the config exposes only the build-level knobs:
/// the master switch, the cohort size, and which font stems count as historical cuts to route to.
#[derive(Serialize, Deserialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct InkTransferCfg {
    /// master switch. false ⇒ no letterpress cohort, `ink_transfer_v2` never runs (current behavior).
    #[serde(default)]
    pub enabled: bool,
    /// fraction of rows minted into the letterpress tail at select time (rendering regime, not a
    /// source property). Met by supply — no extra reuse.
    #[serde(default = "d_lp_cohort")]
    pub cohort_fraction: f64,
    /// font stems the cohort is routed to (historical cuts only). A cohort row with none of these
    /// eligible for its text falls back to a normal render (logged), never a notdef.
    #[serde(default = "d_lp_fonts")]
    pub historical_fonts: Vec<String>,
    /// OLD-FORM KNOB (owner-decided 2026-07-14): fraction of GREEK rows rendered with LUNATE sigma — an
    /// INDEPENDENT draw from `cohort_fraction` (lunate ⊥ degradation; a lunate row may be clean or
    /// degraded). Medial σ is rewritten to ς (final sigma, the only lunate glyph our fonts have) in BOTH
    /// the image render AND the GT label, so image == label (a faithful old-orthography variant, NOT a
    /// character swap; ς is codec atom id 100). Routed to a historical cut for the right glyph; the LABEL
    /// rewrite is TRAIN-ONLY (eval splits stay clean). Default 0.0 = off. See
    /// docs/recognizer_real_page_issues.md I9 + docs/reviews/ink_transfer_v2_design.md §10.
    #[serde(default = "d_lunate")]
    pub lunate_sigma_fraction: f64,
}

fn d_lp_cohort() -> f64 { 0.20 }
fn d_lunate() -> f64 { 0.0 }
fn d_lp_fonts() -> Vec<String> {
    vec!["GFSDidot_Classic".into(), "OldStandard-Regular".into()]
}

impl Default for InkTransferCfg {
    fn default() -> Self {
        InkTransferCfg {
            enabled: false,
            cohort_fraction: d_lp_cohort(),
            historical_fonts: d_lp_fonts(),
            lunate_sigma_fraction: d_lunate(),
        }
    }
}
impl InkTransferCfg {
    /// skip_serializing_if — a disabled cohort is inert, omitted entirely (SHA stability, like crop).
    pub fn is_disabled(&self) -> bool { !self.enabled }
}

impl Recipe {
    pub fn load(path: &str) -> Result<Recipe> {
        let s = std::fs::read_to_string(path).with_context(|| format!("read recipe {path}"))?;
        let mut r: Recipe = serde_json::from_str(&s).context("recipe schema")?;
        r.source_sha256 = Some(crate::custody::hash(s.as_bytes()));
        r.validate()?;
        r.source_effective_sha256 = Some(r.sha256());
        Ok(r)
    }

    pub fn validate(&self) -> Result<()> {
        if let Some(eval) = &self.eval_only {
            if eval.fonts.is_empty() || eval.fonts.iter().any(|f| !self.fonts.held_out.contains(f))
                || !(0.0..=1.0).contains(&eval.max_font_share)
                || self.atom_floor != 0 || self.crop.enabled || self.ink_transfer.enabled {
                bail!("eval-only recipe requires declared held-out fonts, valid font-share cap, atom_floor0, crop/ink disabled");
            }
            if eval.minimum_class_counts.iter().any(|(c,n)| !self.content_marginals.contains_key(c) || *n == 0) {
                bail!("invalid eval-only minimum class counts");
            }
        }
        let known = [
            "greek_mono", "greek_poly", "greek_latin_cs", "greek_cyrillic_cs", "cyrillic_latin_cs",
            "latin", "cyrillic", "furniture",
        ];
        let mut sum = 0.0;
        for (k, v) in &self.content_marginals {
            if !known.contains(&k.as_str()) {
                bail!("unknown script_class in content_marginals: {k}");
            }
            if *v < 0.0 {
                bail!("negative marginal {k}");
            }
            sum += v;
        }
        if (sum - 1.0).abs() > 1e-6 {
            bail!("content_marginals sum {sum}, want 1.0");
        }
        if self.severity_weights.iter().any(|w| *w < 0.0) {
            bail!("negative severity weight");
        }
        if !(0.0..=0.10).contains(&self.polarity_light_fraction) {
            bail!("polarity_light_fraction {} outside [0, 0.10] — inverted text is a small stratum by design; widen deliberately if the deployment surface demands it", self.polarity_light_fraction);
        }
        if self.reuse.max_per_line == 0 {
            bail!("reuse.max_per_line must be >= 1");
        }
        if self.reuse.max_per_line > 4 {
            bail!("reuse.max_per_line {} > 4: floors are met by SUPPLY, not reuse", self.reuse.max_per_line);
        }
        if !(0.0..=1.0).contains(&(self.accent_survival_floor as f64)) {
            bail!("accent_survival_floor out of range");
        }
        if self.lengths.min_chars < 1 || self.lengths.max_chars <= self.lengths.min_chars {
            bail!("bad lengths");
        }
        if self.crop.enabled {
            let c = &self.crop;
            if !(0.0..=1.0).contains(&c.activation_prob) {
                bail!("crop.activation_prob out of [0,1]");
            }
            let msum = c.mix.canonical + c.mix.tight + c.mix.loose;
            if c.mix.canonical < 0.0 || c.mix.tight < 0.0 || c.mix.loose < 0.0 || msum <= 0.0 {
                bail!("crop.mix weights must be >=0 and sum to >0");
            }
            if !(0.0..=1.0).contains(&c.tight.t_max) || !(0.0..=1.0).contains(&c.tight.b_max) {
                bail!("crop.tight.{{t_max,b_max}} must be in [0,1]: it is the fraction of the ABOVE-x-height \
                    (top) / BELOW-baseline (bottom) mark zone that may be cut — 1.0 removes the whole accent \
                    zone (aggressive-max extreme) but never reaches the x-height body, so letters stay protected");
            }
            if c.loose.pad_min < 0.0 || c.loose.pad_max < c.loose.pad_min {
                bail!("crop.loose pad range invalid");
            }
            if !(0.0..=1.0).contains(&c.l_margin_prob) || !(0.0..=1.0).contains(&c.r_margin_prob) || c.margin_max < 0.0 {
                bail!("crop margin params out of range");
            }
            if !(0.0..=1.0).contains(&(c.repair.noise_floor as f64)) {
                bail!("crop.repair.noise_floor out of [0,1]");
            }
            // NB: crop depth is set by `tight`/`loose` ALONE — never bounded by accent legibility. The
            // automatic label-repair (drop marks below noise_floor) is the safety net that makes raising
            // the max self-correcting.
        }
        if self.ink_transfer.enabled {
            let lp = &self.ink_transfer;
            if !(0.0..=1.0).contains(&lp.cohort_fraction) {
                bail!("ink_transfer.cohort_fraction {} out of [0,1]", lp.cohort_fraction);
            }
            if lp.historical_fonts.is_empty() {
                bail!("ink_transfer.historical_fonts is empty: the cohort must route to at least one historical cut");
            }
            if !(0.0..=1.0).contains(&lp.lunate_sigma_fraction) {
                bail!("ink_transfer.lunate_sigma_fraction {} out of [0,1]", lp.lunate_sigma_fraction);
            }
        }
        Ok(())
    }

    pub fn sha256(&self) -> String {
        use sha2::{Digest, Sha256};
        let mut h = Sha256::new();
        h.update(serde_json::to_vec(self).expect("recipe serializes"));
        format!("{:x}", h.finalize())
    }

    pub fn example() -> Recipe {
        Recipe {
            source_sha256: None,
            source_effective_sha256: None,
            target_total: 200_000,
            eval_only: None,
            seed: 20260706,
            // NOTE: these are THIS example()'s own marginals (gm .27 / gp .22), NOT the v1-final
            // recipe of record (recipe.v1.json: gm .30 / gp .24 → cs/greek-block = 0.18/0.72 = 25.0%).
            // For this example: cs/(greek block) = 0.18/(0.27+0.22+0.18) = 0.18/0.67 = 26.9%
            // — both are inside the owner's 25–30% code-switch pin.
            content_marginals: [
                ("greek_mono", 0.27),
                ("greek_poly", 0.22),
                ("greek_latin_cs", 0.18),
                ("latin", 0.20),
                ("cyrillic", 0.08),
                ("furniture", 0.05),
            ]
            .into_iter()
            .map(|(k, v)| (k.to_string(), v))
            .collect(),
            severity_weights: [0.16, 0.20, 0.28, 0.36],
            bg_weights: BgWeights { flat: 0.35, gradient: 0.15, textured: 0.50 },
            polarity_light_fraction: 0.02,
            fonts: Fonts { dir: "assets/fonts".into(), held_out: vec![] },
            lengths: Lengths { min_chars: 3, max_chars: 140, long_chars: 100, long_min_fraction: 0.06 },
            pool_caps: PoolCaps { per_source_max_fraction: 0.25, per_doc_max_lines: 400 },
            reuse: Reuse { max_per_line: 2 },
            atom_floor: 300,
            letterspacing_fraction: 0.03,
            ink_target_h: 40.0,
            ink_fit_jitter: 3.0,
            accent_survival_floor: 0.5,
            ink_contrast_floor: 0.18,
            appearance_band: None,
            watermarks_dir: Some("assets/watermarks".into()),
            exclusion_manifests: vec![],
            crop: CropCfg::default(),
            ink_transfer: InkTransferCfg::default(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn disabled_ink_transfer_is_omitted_and_sha_stable() {
        let r = Recipe::example();
        assert!(r.ink_transfer.is_disabled(), "example() cohort is disabled by default");
        let js = serde_json::to_string(&r).unwrap();
        assert!(!js.contains("ink_transfer"), "a disabled cohort must serialize to nothing (SHA byte-stability)");
        // enabling it must both appear and move the SHA (provenance actually tracks the change)
        let mut r2 = Recipe::example();
        r2.ink_transfer.enabled = true;
        let js2 = serde_json::to_string(&r2).unwrap();
        assert!(js2.contains("ink_transfer"), "an enabled cohort must serialize");
        assert_ne!(r.sha256(), r2.sha256(), "enabling the cohort must change the recipe SHA");
    }

    #[test]
    fn round_trips_without_ink_transfer_key() {
        // a recipe JSON with NO ink_transfer key deserializes to a disabled cohort and re-serializes
        // to the SAME bytes — the on-disk recipes of record stay byte-identical after this change.
        let r = Recipe::example();
        let js = serde_json::to_string(&r).unwrap();
        let back: Recipe = serde_json::from_str(&js).unwrap();
        assert!(back.ink_transfer.is_disabled());
        assert_eq!(js, serde_json::to_string(&back).unwrap());
    }

    #[test]
    fn enabled_cohort_validation_catches_bad_fields() {
        let mut r = Recipe::example();
        r.ink_transfer.enabled = true;
        r.ink_transfer.cohort_fraction = 1.4;
        assert!(r.validate().is_err(), "cohort_fraction > 1 must fail validation");
        r.ink_transfer.cohort_fraction = 0.2;
        r.ink_transfer.historical_fonts = vec![];
        assert!(r.validate().is_err(), "empty historical_fonts must fail validation");
        r.ink_transfer.historical_fonts = vec!["GFSDidot_Classic".into()];
        assert!(r.validate().is_ok(), "a valid enabled cohort passes");
        r.ink_transfer.lunate_sigma_fraction = 1.5;
        assert!(r.validate().is_err(), "lunate_sigma_fraction > 1 must fail validation");
        r.ink_transfer.lunate_sigma_fraction = 0.5;
        assert!(r.validate().is_ok(), "a valid lunate fraction passes");
    }

    #[test]
    fn lunate_default_is_off_and_omitted_when_disabled() {
        let r = Recipe::example();
        assert_eq!(r.ink_transfer.lunate_sigma_fraction, 0.0, "lunate defaults OFF");
        // disabled cohort still serializes to nothing (the knob does not leak into a disabled recipe)
        assert!(!serde_json::to_string(&r).unwrap().contains("lunate"));
    }
}
