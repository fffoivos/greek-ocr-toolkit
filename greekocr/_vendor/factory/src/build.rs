//! Build orchestrator: jobs -> parallel render/distort with repair-not-drop -> shards + reports.
//! Promotion is explicit: audit ok => PROMOTED marker; else QUARANTINED marker + exit 2.

use crate::audit::{audit, AppearanceBand, RowMeta};
use crate::codec::{Codec, CODEC_VERSION};
use crate::corpus::PoolLine;
use crate::distort;
use crate::recipe::Recipe;
use crate::render::{band_ink, render_ink, FontPool, STRIP_H};
use crate::select::Job;
use crate::shard::{Row, ShardSink};
use anyhow::{Context, Result};
use rand::seq::SliceRandom;
use rand::{Rng, SeedableRng};
use rand_chacha::ChaCha20Rng;
use rayon::prelude::*;
use std::collections::BTreeMap;
use xxhash_rust::xxh3::xxh3_64_with_seed;

/// Count of EMITTED rows whose label the crop auto-repaired (an accent dropped) — distinct from the
/// severity-walkdown `repairs`. Surfaced in build_info.json (F3b: a real build's label-edit count).
static CROP_LABEL_REPAIRS: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);
/// Letterpress cohort rows whose text no historical cut could render, so they fell back to the full
/// eligible font set (still get `ink_transfer_v2`, just not a historical face). Surfaced in build_info.
static LP_FONT_FALLBACK: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);

pub struct Built {
    row: Row,
    meta: RowMeta,
    repairs: u32,
}

enum Outcome {
    Ok(Box<Built>),
    Drop(&'static str, String), // reason, script_class
}

fn png_encode(bytes: &[u8], w: usize) -> Result<Vec<u8>> {
    let img = image::GrayImage::from_raw(w as u32, STRIP_H as u32, bytes.to_vec())
        .context("gray image")?;
    let mut out = Vec::new();
    img.write_to(&mut std::io::Cursor::new(&mut out), image::ImageFormat::Png)?;
    Ok(out)
}

/// Load stamp/watermark alpha masks (255 = ink) from recipe.watermarks_dir.
pub fn load_op_ctx(recipe: &Recipe) -> distort::OpCtx {
    let mut ctx = distort::OpCtx::default();
    if let Some(dir) = &recipe.watermarks_dir {
        if let Ok(rd) = std::fs::read_dir(dir) {
            let mut paths: Vec<_> = rd.filter_map(|e| e.ok().map(|e| e.path()))
                .filter(|p| p.extension().is_some_and(|x| x == "png"))
                .collect();
            paths.sort();
            for p in paths {
                if let Ok(img) = image::open(&p) {
                    let g = img.to_luma8();
                    let (w, h) = (g.width() as usize, g.height() as usize);
                    let alpha: Vec<f32> = g.into_raw().iter().map(|v| *v as f32 / 255.0).collect();
                    let name = p.file_stem().and_then(|s| s.to_str()).unwrap_or("wm").to_string();
                    ctx.watermarks.push((name, alpha, w, h));
                }
            }
        }
    }
    ctx
}

/// Drop the combining marks at the given `gt_nfd` byte offsets (automatic label repair). Removing a
/// trailing combining mark preserves NFD canonical order (remaining marks keep their ccc order) and
/// codec-encodability (only atoms remain).
fn drop_marks(gt_nfd: &str, byte_idxs: &[usize]) -> String {
    let set: std::collections::HashSet<usize> = byte_idxs.iter().copied().collect();
    gt_nfd.char_indices().filter(|(i, _)| !set.contains(i)).map(|(_, c)| c).collect()
}

fn build_one(job: &Job, recipe: &Recipe, codec: &Codec, fonts: &FontPool, ctx: &distort::OpCtx) -> Outcome {
    let class = job.line.script_class.clone();
    let nfc = Codec::render_form(&job.line.gt_nfd);
    let elig = fonts.eligible(&nfc);
    if elig.is_empty() {
        return Outcome::Drop("no_eligible_font", class);
    }
    let seed = xxh3_64_with_seed(
        job.line.line_id.as_bytes(),
        recipe.seed ^ ((job.reuse_index as u64) << 32),
    );
    let mut rng = ChaCha20Rng::seed_from_u64(seed);
    // Old-form rows route to the historical cuts only — BOTH the degradation cohort (`letterpress`) and
    // the INDEPENDENT lunate set (`lunate`) need the old glyphs. If none is eligible for this text (e.g. a
    // code-switch line no historical font covers), fall back to the full eligible set (counted). The
    // neither-flag path is byte-identical: `pool == &elig`, so the rng draw is unchanged.
    let lp_pool: Vec<usize>;
    let pool: &[usize] = if job.letterpress || job.lunate {
        let hist: Vec<usize> = elig
            .iter()
            .copied()
            .filter(|&i| recipe.ink_transfer.historical_fonts.iter().any(|s| s == &fonts.fonts[i].stem))
            .collect();
        if hist.is_empty() {
            LP_FONT_FALLBACK.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
            &elig
        } else {
            lp_pool = hist;
            &lp_pool
        }
    } else {
        &elig
    };
    let fi = pool[rng.gen_range(0..pool.len())];
    let font = &fonts.fonts[fi];
    // OLD-FORM: lunate-sigma treatment (owner: "use final sigma"). Applied to a row minted `lunate`
    // (INDEPENDENT of the degradation cohort) — rewrite medial σ→ς in the GT ITSELF, so the render string
    // AND the label both use ς (image == label — a faithful old-orthography variant, NOT a swap; ς is a
    // codec atom). Two guards: the chosen font is a historical cut (else the fallback fired → wrong glyph),
    // and TRAIN-ONLY (mirror `crop_this`, Fable F1) — the LABEL rewrite must never touch eval splits, so
    // val/reserved stay a clean frozen-eval instrument (data_contracts §eval-cleanliness). No rng here: the
    // `lunate` decision was the independent select-time draw.
    let apply_lunate = job.lunate
        && recipe.ink_transfer.historical_fonts.iter().any(|s| s == &font.stem)
        && job.line.split == "train";
    let (gt_nfd, nfc): (std::borrow::Cow<str>, std::borrow::Cow<str>) = if apply_lunate {
        let g = job.line.gt_nfd.replace('σ', "ς");
        let n = Codec::render_form(&g);
        (std::borrow::Cow::Owned(g), std::borrow::Cow::Owned(n))
    } else {
        (std::borrow::Cow::Borrowed(job.line.gt_nfd.as_str()), std::borrow::Cow::Borrowed(nfc.as_str()))
    };
    let tracking = if job.letterspaced { rng.gen_range(0.08f32..0.18) } else { 0.0 };
    let j = recipe.ink_fit_jitter;
    let target_h = recipe.ink_target_h + if j > 0.0 { rng.gen_range(-j..=j) } else { 0.0 };
    let y_jit = if j > 0.0 { rng.gen_range(-2.0f32..2.0) } else { 0.0 };

    // crop augmentation is TRAIN-ONLY: eval splits (val/reserved, incl. transfer-dev) render clean so the
    // retrain-vs-baseline CER comparison is on a consistent clean instrument (F2). want_marks follows.
    let crop_this = recipe.crop.enabled && job.line.split == "train";
    let rendered = match render_ink(font, &nfc, tracking, target_h, y_jit, &gt_nfd, crop_this) {
        Ok(r) => r,
        Err(e) => {
            let msg = e.to_string();
            let reason = if msg.contains("too wide") {
                "too_wide"
            } else if msg.contains("notdef") {
                "notdef_after_cmap_gate"
            } else {
                "render_error"
            };
            return Outcome::Drop(reason, class);
        }
    };
    let w = rendered.w;
    // segmentation-spill stratum: crop includes a full-ink slice of the adjacent line (before
    // d0 so the survival ratio semantics include the spill ink). Fires ~18% of neighbor-carrying
    // jobs, all severities (real segmentation failures are severity-independent).
    let mut base_ink = rendered.ink.clone();
    let mut spill_ops: Vec<String> = Vec::new();
    {
        let mut srng = ChaCha20Rng::seed_from_u64(seed ^ 0x5B111);
        if srng.gen_bool(0.18) {
            if let Some(nb) = job.neighbor_nfc.as_deref() {
                if let Ok(nr) = render_ink(font, nb, 0.0, recipe.ink_target_h, 0.0, "", false) {
                    distort::neighbor_spill(&mut srng, &mut base_ink, w, STRIP_H, (&nr.ink, nr.w, STRIP_H), &mut spill_ops);
                }
            }
        }
    }
    let d0 = band_ink(&base_ink, w, rendered.mark_band_y).max(1e-3);

    // repair-not-drop: try at scheduled severity, walk down on probe failure.
    let mut repairs = 0u32;
    let mut sev = job.severity;
    loop {
        let mut applied: Vec<String> = spill_ops.clone();
        if job.cs_synthetic {
            applied.push("synth:cs".into());
        }
        if job.letterspaced {
            applied.push("letterspaced".into());
        }
        let mut sub = ChaCha20Rng::seed_from_u64(seed ^ (0xA5A5 + sev as u64));
        let mut ink = base_ink.clone();
        distort::ink_ops(&mut sub, &mut ink, w, STRIP_H, sev, &mut applied, false, None, None, job.letterpress);
        let style = distort::Style {
            bg_type: job.bg_type.clone(),
            polarity_light: job.polarity_light,
            severity: sev,
        };
        let (mut img, bg_level, ink_level) = distort::compose(&mut sub, &ink, w, STRIP_H, &style);
        // PHOTO phase first (every mark-killer incl. binarize) → measure survival on the STATIC
        // band → GEO phase (displacement ops) after. Sibling-bug lesson 2026-07-06.
        distort::image_ops(&mut sub, &mut img, w, STRIP_H, sev, &mut applied, distort::Phase::Photo, false, None, None, ctx);
        let survival = if rendered.has_top_marks {
            let band = rendered.mark_band_y.min(STRIP_H);
            let bg_est = {
                let mut v = img.clone();
                v.sort_by(|a, b| a.partial_cmp(b).unwrap());
                v[(v.len() as f32 * 0.85) as usize]
            };
            let d1: f32 = img[..band * w].iter().map(|p| (bg_est - p).max(0.0)).sum();
            (d1 / (d0 * (bg_level - ink_level).max(0.05))).min(1.0)
        } else {
            1.0
        };
        // verso show-through: fires by severity; adds ink only (after the survival probe)
        let bleed_p = [0.0, 0.12, 0.25, 0.40][sev as usize];
        if sub.gen_bool(bleed_p) {
            let vr = job
                .verso_nfc
                .as_deref()
                .and_then(|v| render_ink(font, v, 0.0, recipe.ink_target_h, 0.0, "", false).ok());
            match &vr {
                Some(r) => distort::verso_bleed(&mut sub, &mut img, w, STRIP_H, sev, Some((&r.ink, r.w, STRIP_H)), &mut applied, None),
                None => distort::verso_bleed(&mut sub, &mut img, w, STRIP_H, sev, None, &mut applied, None),
            }
        }
        distort::image_ops(&mut sub, &mut img, w, STRIP_H, sev, &mut applied, distort::Phase::Geo, false, None, None, ctx);
        let contrast = distort::contrast_of(&img);
        let pass = contrast >= recipe.ink_contrast_floor
            && (!rendered.has_top_marks || survival >= recipe.accent_survival_floor);
        if pass || sev == 0 {
            if !pass {
                return Outcome::Drop("unrenderable_at_sev0", class);
            }
            // ---- detector crop: FINAL op, after Geo (docs/crop_robustness_design.md) ----
            // Crop depth is set by the recipe alone (never bounded by accent legibility). The AUTOMATIC
            // label-repair drops any accent the crop actually destroys, so the (cropped image, label) pair
            // stays consistent — at a survivable max it drops nothing. (A repaired label equal to an eval
            // line is NOT contamination — different images — so there is no leak guard; owner ruling.)
            let mut out_img = img; // move (img unused after this point)
            let mut out_w = w;
            let mut out_gt = gt_nfd.clone().into_owned();
            let mut out_nfc = nfc.clone().into_owned();
            let mut out_has_top = rendered.has_top_marks;
            let mut out_surv = survival;
            if crop_this && sub.gen_bool(recipe.crop.activation_prob) {
                let (ni, nw, drops, band_surv) = distort::detector_crop(
                    &mut sub, &out_img, out_w, rendered.mark_band_y, rendered.bot_band_y,
                    rendered.has_top_marks, rendered.has_bottom_marks, &rendered.marks,
                    &recipe.crop, &mut applied,
                );
                out_img = ni;
                out_w = nw;
                if !drops.is_empty() {
                    CROP_LABEL_REPAIRS.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
                    // AUTO-REPAIR: a repaired label equal to an eval line is NOT contamination (different
                    // images — unique crop — and a rare corner case; owner ruling). So the repair ALWAYS
                    // applies; the (cropped image, repaired label) pair just stays consistent.
                    out_gt = drop_marks(&out_gt, &drops);
                    out_nfc = Codec::render_form(&out_gt);
                    out_has_top = out_gt.chars().any(Codec::is_top_mark);
                }
                // F5: emitted accent_survival = pre-crop Photo survival × geometric top-band retention, so
                // the audit p10 gate measures the EMITTED image (markless-after-repair rows ⇒ 1.0).
                out_surv = if out_has_top { survival * band_surv } else { 1.0 };
            }
            let bytes = distort::finalize(&mut sub, &out_img, out_w, STRIP_H, sev, job.polarity_light, &mut applied);
            let png = match png_encode(&bytes, out_w) {
                Ok(p) => p,
                Err(_) => return Outcome::Drop("png_encode", class),
            };
            let ids = match codec.encode(&out_gt) {
                Some(v) => v.into_iter().map(|i| i as i32).collect(),
                None => return Outcome::Drop("repair_unencodable", class), // defensive; repair keeps atoms
            };
            let row = Row {
                image_png: png,
                width: out_w as i32,
                gt_nfd: out_gt.clone(),
                gt_nfc: out_nfc,
                label_ids: ids,
                script_class: class.clone(),
                split: job.line.split.clone(),
                severity: sev as i32,
                applied_ops: applied.clone(),
                font: font.stem.clone(),
                polarity: if job.polarity_light { "light_on_dark".into() } else { "dark_on_light".into() },
                bg_type: job.bg_type.clone(),
                accent_survival: out_surv,
                reuse_index: job.reuse_index as i32,
                line_id: job.line.line_id.clone(),
                source_dataset: job.line.source_dataset.clone(),
                source_doc_id: job.line.source_doc_id.clone(),
                license: job.line.license.clone(),
            };
            let meta = RowMeta {
                script_class: class,
                split: job.line.split.clone(),
                severity: sev,
                polarity_light: job.polarity_light,
                bg_type: job.bg_type.clone(),
                font: font.stem.clone(),
                accent_survival: out_surv,
                has_top_marks: out_has_top,
                reuse_index: job.reuse_index,
                gt_len: out_gt.chars().count(),
                source_dataset: job.line.source_dataset.clone(),
                source_doc_id: job.line.source_doc_id.clone(),
                contrast,
                letterpress: job.letterpress,
                lunate: apply_lunate,
            };
            return Outcome::Ok(Box::new(Built { row, meta, repairs }));
        }
        sev -= 1;
        repairs += 1;
    }
}

pub fn run(
    recipe: &Recipe,
    jobs: Vec<Job>,
    codec: &Codec,
    out: &str,
    select_report: serde_json::Value,
    ingest_meta: Option<serde_json::Value>,
    allow_deficit: bool,
) -> Result<bool> {
    anyhow::ensure!(!std::path::Path::new(out).exists() || std::fs::read_dir(out)?.next().is_none(),
                    "build output must be new or empty (custody forbids stale shards)");
    anyhow::ensure!(recipe.source_sha256.is_some()
        && recipe.source_effective_sha256.as_deref() == Some(recipe.sha256().as_str()),
        "effective recipe changed after loading: commit a new recipe file instead of an in-memory override");
    std::fs::create_dir_all(out)?;
    let excluded = if let Some(eval) = &recipe.eval_only {
        anyhow::ensure!(!eval.fonts.is_empty(), "eval-only fonts must be nonempty");
        FontPool::stems_in(&recipe.fonts.dir)?.into_iter()
            .filter(|s| !eval.fonts.contains(s)).collect()
    } else { recipe.fonts.held_out.clone() };
    let fonts = FontPool::load(&recipe.fonts.dir, &excluded)?;
    let ctx = load_op_ctx(recipe);
    eprintln!("[build] fonts loaded: {} | watermarks: {}", fonts.fonts.len(), ctx.watermarks.len());
    crate::render::MARK_SKIPS.store(0, std::sync::atomic::Ordering::Relaxed); // F9: fresh per build
    CROP_LABEL_REPAIRS.store(0, std::sync::atomic::Ordering::Relaxed);
    LP_FONT_FALLBACK.store(0, std::sync::atomic::Ordering::Relaxed);
    // emitted-label atom census (the crop-repair drops marks at BUILD time, after select-time atom-floor
    // accounting — this recounts the ACTUALLY-emitted labels to surface any silent mark-atom underrun).
    let mut atom_census: BTreeMap<i32, u64> = BTreeMap::new();
    let census_on = recipe.crop.enabled; // repair is intrinsic to cropping ⇒ census whenever cropping runs
    let band: Option<AppearanceBand> = match &recipe.appearance_band {
        Some(p) => Some(serde_json::from_str(
            &std::fs::read_to_string(p).with_context(|| format!("appearance band {p}"))?,
        )?),
        None => None,
    };

    // interleave classes so --smoke prefixes and progress are representative
    let mut jobs = jobs;
    let mut rng = ChaCha20Rng::seed_from_u64(recipe.seed ^ 0xC0FFEE);
    jobs.shuffle(&mut rng);

    let mut sink = ShardSink::new(out)?;
    let mut metas: Vec<RowMeta> = Vec::with_capacity(jobs.len());
    let mut drops: BTreeMap<String, usize> = BTreeMap::new();
    let mut repairs: BTreeMap<String, usize> = BTreeMap::new();
    let samples_dir = std::path::Path::new(out).join("samples");
    std::fs::create_dir_all(&samples_dir)?;
    let mut n_samples = 0usize;

    let t0 = std::time::Instant::now();
    for (ci, chunk) in jobs.chunks(2048).enumerate() {
        let outcomes: Vec<Outcome> = chunk
            .par_iter()
            .map(|j| build_one(j, recipe, codec, &fonts, &ctx))
            .collect();
        for o in outcomes {
            match o {
                Outcome::Ok(b) => {
                    if census_on && b.row.split == "train" {
                        // atom_floor is a TRAIN-split guarantee (select.rs counts train rows), so the
                        // emitted recount must be train-only or val/reserved marks would mask a deficit.
                        for id in &b.row.label_ids {
                            *atom_census.entry(*id).or_default() += 1;
                        }
                    }
                    if b.repairs > 0 {
                        *repairs.entry(format!("sev_walkdown:{}", b.meta.script_class)).or_default() += b.repairs as usize;
                    }
                    if n_samples < 64 {
                        let name = format!(
                            "{:03}_{}_sev{}.png",
                            n_samples, b.meta.script_class, b.meta.severity
                        );
                        std::fs::write(samples_dir.join(name), &b.row.image_png)?;
                        n_samples += 1;
                    }
                    metas.push(b.meta);
                    sink.push(b.row)?;
                }
                Outcome::Drop(reason, class) => {
                    *drops.entry(format!("{reason}:{class}")).or_default() += 1;
                }
            }
        }
        eprintln!(
            "[build] chunk {}/{} done ({} rows, {:.1}s)",
            ci + 1,
            jobs.len().div_ceil(2048),
            metas.len(),
            t0.elapsed().as_secs_f32()
        );
    }
    let written = sink.finish()?;
    eprintln!("[build] written: {written:?} drops: {drops:?}");

    let mut census_ok = true;
    if census_on {
        // recount mark atoms on the EMITTED train labels (post-repair) vs the floor the pool satisfied at
        // select — the crop-repair drops marks at BUILD time, so this is the only place a silent underrun shows.
        let mut marks: Vec<serde_json::Value> = Vec::new();
        let mut deficits: Vec<(char, u64)> = Vec::new();
        for a in &codec.atoms {
            if matches!(a.kind, crate::codec::Kind::Mark) {
                let c = atom_census.get(&(a.id as i32)).copied().unwrap_or(0);
                marks.push(serde_json::json!({"cp": a.cp, "ch": a.ch.to_string(), "id": a.id, "emitted": c}));
                if (c as usize) < recipe.atom_floor {
                    deficits.push((a.ch, c));
                }
            }
        }
        census_ok = deficits.is_empty();
        std::fs::write(
            std::path::Path::new(out).join("crop_atom_census.json"),
            serde_json::to_string_pretty(&serde_json::json!({
                "note": "emitted TRAIN-split mark-atom counts after the crop-repair; a deficit vs atom_floor \
                    that select-time accounting did not show means repair pushed a mark below its floor.",
                "atom_floor": recipe.atom_floor,
                "allow_deficit": allow_deficit,
                "ok": census_ok,
                "deficits": deficits.iter().map(|(c, n)| serde_json::json!({"ch": c.to_string(), "emitted": n})).collect::<Vec<_>>(),
                "marks": marks,
            }))?,
        )?;
        let skips = crate::render::MARK_SKIPS.load(std::sync::atomic::Ordering::Relaxed);
        if skips > 0 {
            eprintln!("[build] WARN compute_marks could not isolate {skips} cluster(s) → undropable under the crop-repair (font-pool drift?)");
        }
        if census_ok {
            eprintln!("[build] crop census: all mark atoms >= atom_floor ({})", recipe.atom_floor);
        } else if allow_deficit {
            eprintln!("[build] crop census: {} mark atom(s) below atom_floor (ALLOWED via --allow-deficit): {:?}", deficits.len(), deficits);
        } else {
            // F3: hard-fail (like the select-time floor) — a real crop-repair build must not silently ship a
            // mark-atom underrun. Use --allow-deficit to proceed on a known/subset build.
            eprintln!("[build] FAIL crop census: {} mark atom(s) below atom_floor after repair: {:?}", deficits.len(), deficits);
        }
    }

    let report = audit(&metas, recipe, band.as_ref(), &drops, &repairs)?;
    std::fs::write(
        std::path::Path::new(out).join("audit_report.json"),
        serde_json::to_string_pretty(&report)?,
    )?;
    std::fs::write(
        std::path::Path::new(out).join("select_report.json"),
        serde_json::to_string_pretty(&select_report)?,
    )?;
    let font_meta: Vec<serde_json::Value> = fonts
        .fonts
        .iter()
        .map(|f| serde_json::json!({"stem": f.stem, "sha16": f.sha16}))
        .collect();
    let build_info = serde_json::json!({
        "codec_version": CODEC_VERSION,
        "kind": "synthetic",
        "recipe_sha256": recipe.source_sha256.as_ref().context("build requires a loaded recipe file")?,
        "recipe_effective_sha256": recipe.sha256(),
        "shard_sha256": crate::custody::shard_hashes(std::path::Path::new(out))?,
        "recipe": recipe,
        "n_jobs": jobs.len(),
        "written": written,
        "drops": drops,
        "repairs": repairs,
        "crop_label_repairs": CROP_LABEL_REPAIRS.load(std::sync::atomic::Ordering::Relaxed),
        "letterpress_font_fallbacks": LP_FONT_FALLBACK.load(std::sync::atomic::Ordering::Relaxed),
        "fonts": font_meta,
        "held_out_fonts": recipe.fonts.held_out,
        "ingest": ingest_meta,
        "audit_ok": report.ok && (allow_deficit || census_ok),
        "eval_only": recipe.eval_only.is_some(),
        "strip_contract": {"height": STRIP_H, "timesteps": "ceil(width/4)", "polarity": "u8, 255=white"},
    });
    std::fs::write(
        std::path::Path::new(out).join("build_info.json"),
        serde_json::to_string_pretty(&build_info)?,
    )?;
    let promoted = report.ok && (allow_deficit || census_ok);
    let marker = if promoted { "PROMOTED" } else { "QUARANTINED" };
    std::fs::write(std::path::Path::new(out).join(marker), format!("audit ok: {} census_ok: {}\n", report.ok, census_ok))?;
    eprintln!("[build] {marker} ({} rows, audit_ok={} census_ok={})", report.n_rows, report.ok, census_ok);
    Ok(promoted)
}

/// Readability-ceiling stress probe (standing, after the sibling program's 2026-07-06 finding
/// that its dataset never stacked >2 ops and its 'hardest' strata never probed the real limit):
/// force EVERY ink + photo + geo op at max severity on a mixed sample and emit samples + stats
/// for eyeball/auto review. If the extreme stack is legible, the per-op probabilities have
/// headroom; if not, the audit floors are doing real work.
pub fn stress_run(recipe: &Recipe, pool: &[PoolLine], out: &str, n: usize) -> Result<()> {
    std::fs::create_dir_all(out)?;
    let fonts = FontPool::load(&recipe.fonts.dir, &recipe.fonts.held_out)?;
    let ctx = load_op_ctx(recipe);
    let mut lines: Vec<&PoolLine> = pool.iter().collect();
    lines.sort_by_key(|l| std::cmp::Reverse(l.gt_nfd.chars().count()));
    let mut picked: Vec<&PoolLine> = lines.iter().take(n / 2).copied().collect(); // longest half
    let mut rng = ChaCha20Rng::seed_from_u64(recipe.seed ^ 0x57E55);
    for _ in 0..(n - picked.len()) {
        picked.push(lines[rng.gen_range(0..lines.len())]);
    }
    let mut survs: Vec<f32> = Vec::new();
    let mut cons: Vec<f32> = Vec::new();
    for (i, l) in picked.iter().enumerate() {
        let nfc = Codec::render_form(&l.gt_nfd);
        let elig = fonts.eligible(&nfc);
        if elig.is_empty() {
            continue;
        }
        let font = &fonts.fonts[elig[rng.gen_range(0..elig.len())]];
        let Ok(r) = render_ink(font, &nfc, 0.0, recipe.ink_target_h, 0.0, "", false) else { continue };
        let w = r.w;
        let d0 = band_ink(&r.ink, w, r.mark_band_y).max(1e-3);
        let mut applied = Vec::new();
        let mut ink = r.ink.clone();
        distort::ink_ops(&mut rng, &mut ink, w, STRIP_H, 3, &mut applied, true, None, None, false);
        let style = distort::Style { bg_type: "flat".into(), polarity_light: false, severity: 3 };
        let (mut img, bg_level, ink_level) = distort::compose(&mut rng, &ink, w, STRIP_H, &style);
        distort::image_ops(&mut rng, &mut img, w, STRIP_H, 3, &mut applied, distort::Phase::Photo, true, None, None, &ctx);
        let surv = if r.has_top_marks {
            let band = r.mark_band_y.min(STRIP_H);
            let mut v = img.clone();
            v.sort_by(|a, b| a.partial_cmp(b).unwrap());
            let bg_est = v[(v.len() as f32 * 0.85) as usize];
            let d1: f32 = img[..band * w].iter().map(|p| (bg_est - p).max(0.0)).sum();
            (d1 / (d0 * (bg_level - ink_level).max(0.05))).min(1.0)
        } else {
            1.0
        };
        distort::verso_bleed(&mut rng, &mut img, w, STRIP_H, 3, None, &mut applied, None);
        distort::image_ops(&mut rng, &mut img, w, STRIP_H, 3, &mut applied, distort::Phase::Geo, true, None, None, &ctx);
        let con = distort::contrast_of(&img);
        survs.push(surv);
        cons.push(con);
        let bytes = distort::finalize(&mut rng, &img, w, STRIP_H, 3, false, &mut applied);
        if let Ok(png) = png_encode(&bytes, w) {
            std::fs::write(
                std::path::Path::new(out).join(format!("stress_{i:03}_len{}.png", l.gt_nfd.chars().count())),
                png,
            )?;
        }
    }
    let q = |v: &mut Vec<f32>, f: f32| -> f32 {
        if v.is_empty() {
            return f32::NAN;
        }
        v.sort_by(|a, b| a.partial_cmp(b).unwrap());
        v[((v.len() - 1) as f32 * f) as usize]
    };
    eprintln!(
        "[stress] n={} ALL ops @ sev3 | accent_survival p10={:.3} p50={:.3} | contrast p10={:.3} p50={:.3} | floors: surv {} contrast {}",
        survs.len(),
        q(&mut survs.clone(), 0.10),
        q(&mut survs.clone(), 0.50),
        q(&mut cons.clone(), 0.10),
        q(&mut cons.clone(), 0.50),
        recipe.accent_survival_floor,
        recipe.ink_contrast_floor,
    );
    eprintln!("[stress] samples -> {out} (eyeball or auto-review the ceiling)");
    Ok(())
}

/// Load a pool written by `ingest`.
pub fn load_pool(path: &str) -> Result<Vec<PoolLine>> {
    use std::io::BufRead;
    let f = std::fs::File::open(path).with_context(|| format!("pool {path}"))?;
    let mut out = Vec::new();
    for l in std::io::BufReader::new(f).lines() {
        let l = l?;
        if !l.trim().is_empty() {
            out.push(serde_json::from_str(&l)?);
        }
    }
    Ok(out)
}

/// Distortion LADDER (owner protocol 2026-07-06): every op in ISOLATION at escalating strength
/// multipliers of its sev-3 max, plus the combined stack at the same rungs — climb down from the
/// extreme to find each op's readability cliff and any needed caps. Emits strips + stats.json;
/// review sheets/presentation are assembled downstream.
pub fn ladder_run(recipe: &Recipe, out: &str) -> Result<()> {
    std::fs::create_dir_all(out)?;
    let fonts = FontPool::load(&recipe.fonts.dir, &recipe.fonts.held_out)?;
    let ctx = load_op_ctx(recipe);
    // probes: polytonic (fragile marks — the binding constraint), modern Greek w/ digits, latin
    const PROBES: &[(&str, &str)] = &[
        ("poly", "Θὰ τελειώσω τὰς ἁπλᾶς ταύτας γραμμάς, τὰς ὁποίας θὰ κρίνῃ ὁ ἀναγνώστης ἐπιεικῶς"),
        ("mono", "Τόμος 12, τεύχος 3, σελίδες 217–248, Αθήνα 1998 — βιβλιογραφία καὶ εὑρετήρια"),
        ("latn", "Homerische Untersuchungen, Berlin 1884, pp. 145–212 (zweite Auflage)"),
    ];
    const RUNGS: &[(&str, f32)] = &[("m100", 3.0), ("m150", 4.5), ("m225", 6.75), ("m300", 9.0)];
    let mut stats: Vec<serde_json::Value> = Vec::new();

    let render_probe = |name: &str| -> Result<(crate::render::RenderedStrip, String)> {
        let (_, text) = PROBES.iter().find(|(n, _)| *n == name).expect("probe");
        let nfc = Codec::render_form(&Codec::normalize_gt(text));
        let elig = fonts.eligible(&nfc);
        anyhow::ensure!(!elig.is_empty(), "no font for probe {name}");
        let f = &fonts.fonts[elig[0]];
        Ok((render_ink(f, &nfc, 0.0, recipe.ink_target_h, 0.0, "", false)?, f.stem.clone()))
    };

    // per-op ladders on the polytonic probe (isolation; fixed compose for comparability)
    let (probe, _font) = render_probe("poly")?;
    let w = probe.w;
    let d0 = band_ink(&probe.ink, w, probe.mark_band_y).max(1e-3);
    let ink_op_names = ["ink_bleed", "ink_starve", "edge_noise", "ink_transfer_v2", "verso_ghost_self"];
    let all_ops: Vec<&str> = distort::OP_NAMES.iter().copied().chain(ink_op_names).collect();
    for op in &all_ops {
        for (rname, s_ov) in RUNGS {
            let mut rng = ChaCha20Rng::seed_from_u64(0xD15707 ^ (*s_ov as u64) << 8);
            let mut applied = Vec::new();
            let mut ink = probe.ink.clone();
            if *op == "ink_transfer_v2" {
                // isolated: ink_transfer_v2 is driven by the letterpress flag, not `only`; map the rung
                // multiplier to a severity so the ladder still sweeps s0..s3.
                let lp_sev = (*s_ov).round().clamp(0.0, 3.0) as u8;
                distort::ink_transfer_v2(&mut rng, &mut ink, w, STRIP_H, lp_sev, &mut applied);
            } else if ink_op_names.contains(op) && *op != "verso_ghost_self" {
                distort::ink_ops(&mut rng, &mut ink, w, STRIP_H, 3, &mut applied, false, Some(*s_ov), Some(op), false);
            }
            let style = distort::Style { bg_type: "flat".into(), polarity_light: false, severity: 3 };
            let (mut img, bg_level, ink_level) = distort::compose(&mut rng, &ink, w, STRIP_H, &style);
            if *op == "verso_ghost_self" {
                distort::verso_bleed(&mut rng, &mut img, w, STRIP_H, 3, None, &mut applied, Some(*s_ov));
            } else if !ink_op_names.contains(op) {
                for phase in [distort::Phase::Photo, distort::Phase::Geo] {
                    distort::image_ops(&mut rng, &mut img, w, STRIP_H, 3, &mut applied, phase, false, Some(op), Some(*s_ov), &ctx);
                }
            }
            let surv = {
                let band = probe.mark_band_y.min(STRIP_H);
                let mut v = img.clone();
                v.sort_by(|a, b| a.partial_cmp(b).unwrap());
                let bg_est = v[(v.len() as f32 * 0.85) as usize];
                let d1: f32 = img[..band * w].iter().map(|p| (bg_est - p).max(0.0)).sum();
                (d1 / (d0 * (bg_level - ink_level).max(0.05))).min(1.0)
            };
            let con = distort::contrast_of(&img);
            let bytes = distort::finalize(&mut rng, &img, w, STRIP_H, 3, false, &mut applied);
            if let Ok(png) = png_encode(&bytes, w) {
                std::fs::write(std::path::Path::new(out).join(format!("op_{op}_{rname}.png")), png)?;
            }
            stats.push(serde_json::json!({"kind":"per_op","op":op,"rung":rname,"mult":s_ov/3.0,
                "survival":surv,"contrast":con,"applied":applied}));
        }
    }
    // combined stack ladders, all three probes
    for (pname, _) in PROBES {
        let (pr, _) = render_probe(pname)?;
        let w = pr.w;
        let d0 = band_ink(&pr.ink, w, pr.mark_band_y).max(1e-3);
        for (rname, s_ov) in RUNGS {
            let mut rng = ChaCha20Rng::seed_from_u64(0xC0B1E ^ (*s_ov as u64) << 8);
            let mut applied = Vec::new();
            let mut ink = pr.ink.clone();
            distort::ink_ops(&mut rng, &mut ink, w, STRIP_H, 3, &mut applied, true, Some(*s_ov), None, false);
            let style = distort::Style { bg_type: "textured".into(), polarity_light: false, severity: 3 };
            let (mut img, bg_level, ink_level) = distort::compose(&mut rng, &ink, w, STRIP_H, &style);
            distort::image_ops(&mut rng, &mut img, w, STRIP_H, 3, &mut applied, distort::Phase::Photo, true, None, Some(*s_ov), &ctx);
            let surv = {
                let band = pr.mark_band_y.min(STRIP_H);
                let mut v = img.clone();
                v.sort_by(|a, b| a.partial_cmp(b).unwrap());
                let bg_est = v[(v.len() as f32 * 0.85) as usize];
                let d1: f32 = img[..band * w].iter().map(|p| (bg_est - p).max(0.0)).sum();
                (d1 / (d0 * (bg_level - ink_level).max(0.05))).min(1.0)
            };
            distort::verso_bleed(&mut rng, &mut img, w, STRIP_H, 3, None, &mut applied, Some(*s_ov));
            distort::image_ops(&mut rng, &mut img, w, STRIP_H, 3, &mut applied, distort::Phase::Geo, true, None, Some(*s_ov), &ctx);
            let con = distort::contrast_of(&img);
            let bytes = distort::finalize(&mut rng, &img, w, STRIP_H, 3, false, &mut applied);
            if let Ok(png) = png_encode(&bytes, w) {
                std::fs::write(std::path::Path::new(out).join(format!("combined_{pname}_{rname}.png")), png)?;
            }
            stats.push(serde_json::json!({"kind":"combined","probe":pname,"rung":rname,
                "mult":s_ov/3.0,"survival":surv,"contrast":con}));
        }
    }
    std::fs::write(
        std::path::Path::new(out).join("ladder_stats.json"),
        serde_json::to_string_pretty(&stats)?,
    )?;
    eprintln!("[ladder] {} strips + ladder_stats.json -> {out}", all_ops.len() * 4 + 12);
    Ok(())
}

/// Stage-by-stage composition demo: replay REAL build jobs (same seeds/draws as `build`) for a
/// handful of lines, saving the image after every stage — render, ink ops, paper compose,
/// photometric, verso, geometry, finalize. Owner-facing "how a strip is made" evidence.
pub fn stages_run(recipe: &Recipe, pool: &[PoolLine], codec: &Codec, out: &str) -> Result<()> {
    std::fs::create_dir_all(out)?;
    let fonts = FontPool::load(&recipe.fonts.dir, &recipe.fonts.held_out)?;
    let ctx = load_op_ctx(recipe);
    let (jobs, _) = crate::select::select(pool, recipe, codec, true)?;
    let spill_fires = |j: &crate::select::Job| -> bool {
        let seed = xxh3_64_with_seed(j.line.line_id.as_bytes(), recipe.seed ^ ((j.reuse_index as u64) << 32));
        j.neighbor_nfc.is_some() && ChaCha20Rng::seed_from_u64(seed ^ 0x5B111).gen_bool(0.18)
    };
    let mut picks: Vec<&crate::select::Job> = Vec::new();
    for (class, sev) in [("greek_poly", 3u8), ("greek_mono", 2), ("greek_latin_cs", 3), ("cyrillic", 1)] {
        if let Some(j) = jobs
            .iter()
            .find(|j| j.line.script_class == class && j.severity == sev && spill_fires(j)
                && (30..110).contains(&j.line.gt_nfd.chars().count()))
            .or_else(|| jobs.iter().find(|j| {
                j.line.script_class == class && j.severity == sev && j.verso_nfc.is_some()
                    && (30..110).contains(&j.line.gt_nfd.chars().count())
            }))
            .or_else(|| jobs.iter().find(|j| j.line.script_class == class && j.severity == sev))
        {
            picks.push(j);
        }
    }
    let mut meta: Vec<serde_json::Value> = Vec::new();
    for (li, job) in picks.iter().enumerate() {
        let nfc = Codec::render_form(&job.line.gt_nfd);
        let elig = fonts.eligible(&nfc);
        if elig.is_empty() {
            continue;
        }
        let seed = xxh3_64_with_seed(job.line.line_id.as_bytes(), recipe.seed ^ ((job.reuse_index as u64) << 32));
        let mut rng = ChaCha20Rng::seed_from_u64(seed);
        let fi = elig[rng.gen_range(0..elig.len())];
        let font = &fonts.fonts[fi];
        let tracking = if job.letterspaced { rng.gen_range(0.08f32..0.18) } else { 0.0 };
        let j = recipe.ink_fit_jitter;
        let target_h = recipe.ink_target_h + if j > 0.0 { rng.gen_range(-j..=j) } else { 0.0 };
        let y_jit = if j > 0.0 { rng.gen_range(-2.0f32..2.0) } else { 0.0 };
        let Ok(rendered) = render_ink(font, &nfc, tracking, target_h, y_jit, "", false) else { continue };
        let w = rendered.w;
        let save = |tag: &str, img: &[f32]| -> Result<()> {
            let bytes: Vec<u8> = img.iter().map(|p| (p.clamp(0.0, 1.0) * 255.0) as u8).collect();
            std::fs::write(
                std::path::Path::new(out).join(format!("line{li}_{tag}.png")),
                png_encode(&bytes, w)?,
            )?;
            Ok(())
        };
        let sev = job.severity; // demo shows the SCHEDULED severity pass (repair walk-down rare now)
        let mut applied: Vec<String> = Vec::new();
        let mut sub = ChaCha20Rng::seed_from_u64(seed ^ (0xA5A5 + sev as u64));
        let white_ink: Vec<f32> = rendered.ink.iter().map(|a| 1.0 - a).collect();
        save("0_render", &white_ink)?;
        // replicate build_one's segmentation-spill stage (same seed/draw)
        let mut base_ink = rendered.ink.clone();
        let mut spill_desc = "not fired".to_string();
        {
            let mut srng = ChaCha20Rng::seed_from_u64(seed ^ 0x5B111);
            if srng.gen_bool(0.18) {
                if let Some(nb) = job.neighbor_nfc.as_deref() {
                    if let Ok(nr) = render_ink(font, nb, 0.0, recipe.ink_target_h, 0.0, "", false) {
                        let mut sp = Vec::new();
                        distort::neighbor_spill(&mut srng, &mut base_ink, w, STRIP_H, (&nr.ink, nr.w, STRIP_H), &mut sp);
                        spill_desc = sp.join(", ");
                        let wi: Vec<f32> = base_ink.iter().map(|a| 1.0 - a).collect();
                        save("0b_spill", &wi)?;
                    }
                }
            }
        }
        let mut ink = base_ink.clone();
        distort::ink_ops(&mut sub, &mut ink, w, STRIP_H, sev, &mut applied, false, None, None, job.letterpress);
        let ink_stage_ops = applied.clone();
        let white_ink2: Vec<f32> = ink.iter().map(|a| 1.0 - a).collect();
        save("1_inkops", &white_ink2)?;
        let style = distort::Style { bg_type: job.bg_type.clone(), polarity_light: job.polarity_light, severity: sev };
        let (mut img, _bg, _il) = distort::compose(&mut sub, &ink, w, STRIP_H, &style);
        save("2_paper", &img)?;
        distort::image_ops(&mut sub, &mut img, w, STRIP_H, sev, &mut applied, distort::Phase::Photo, false, None, None, &ctx);
        let photo_ops: Vec<String> = applied[ink_stage_ops.len()..].to_vec();
        save("3_photo", &img)?;
        let bleed_p = [0.0, 0.12, 0.25, 0.40][sev as usize];
        let mut verso_fired = false;
        if sub.gen_bool(bleed_p) {
            verso_fired = true;
            let vr = job.verso_nfc.as_deref().and_then(|v| render_ink(font, v, 0.0, recipe.ink_target_h, 0.0, "", false).ok());
            match &vr {
                Some(r) => distort::verso_bleed(&mut sub, &mut img, w, STRIP_H, sev, Some((&r.ink, r.w, STRIP_H)), &mut applied, None),
                None => distort::verso_bleed(&mut sub, &mut img, w, STRIP_H, sev, None, &mut applied, None),
            }
        }
        save("4_verso", &img)?;
        let pre_geo = applied.len();
        distort::image_ops(&mut sub, &mut img, w, STRIP_H, sev, &mut applied, distort::Phase::Geo, false, None, None, &ctx);
        let geo_ops: Vec<String> = applied[pre_geo..].to_vec();
        save("5_geo", &img)?;
        let bytes = distort::finalize(&mut sub, &img, w, STRIP_H, sev, job.polarity_light, &mut applied);
        std::fs::write(
            std::path::Path::new(out).join(format!("line{li}_6_final.png")),
            png_encode(&bytes, w)?,
        )?;
        meta.push(serde_json::json!({
            "line": li, "gt": job.line.gt_nfd, "class": job.line.script_class,
            "severity": sev, "font": font.stem, "bg": job.bg_type,
            "letterspaced": job.letterspaced,
            "ink_ops": ink_stage_ops, "photo_ops": photo_ops,
            "spill": spill_desc,
            "verso": if verso_fired { if job.verso_nfc.is_some() { "real-text ghost" } else { "self ghost" } } else { "not fired" },
            "geo_ops": geo_ops,
        }));
    }
    std::fs::write(std::path::Path::new(out).join("stages.json"), serde_json::to_string_pretty(&meta)?)?;
    eprintln!("[stages] {} lines -> {out}", meta.len());
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn drop_marks_removes_only_targeted_marks() {
        // ό = ο(U+03BF, 2 bytes) + U+0301(2 bytes) ; ς at byte 4. Drop the acute at byte 2.
        let gt = "\u{03BF}\u{0301}\u{03C2}";
        let out = drop_marks(gt, &[2]);
        assert_eq!(out, "\u{03BF}\u{03C2}", "acute dropped, letters kept");
        assert!(!out.chars().any(|c| c == '\u{0301}'));
    }

    #[test]
    fn drop_marks_stacked_keeps_the_others() {
        // ᾧ NFD = ω(2b) U+0314(@2) U+0342(@4) U+0345(@6). Drop ONLY the perispomeni (U+0342 @ byte 4).
        let gt = "\u{03C9}\u{0314}\u{0342}\u{0345}";
        let out = drop_marks(gt, &[4]);
        assert_eq!(out, "\u{03C9}\u{0314}\u{0345}", "dasia + ypogegrammeni kept, perispomeni gone");
    }

    #[test]
    fn drop_marks_noop_when_empty() {
        let gt = "\u{03BF}\u{0301}\u{03C2}";
        assert_eq!(drop_marks(gt, &[]), gt);
    }

}
