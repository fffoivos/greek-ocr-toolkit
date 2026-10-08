//! Real crops enter the same shard/codec contract; every unusable row has a ledger entry.
use crate::audit::{appearance_check, length_check, AppearanceBand, RowMeta};
use crate::codec::{Codec, CODEC_VERSION};
use crate::custody::{hash, shard_hashes};
use crate::recipe::Recipe;
use crate::shard::{Row, ShardSink};
use anyhow::{Context, Result};
use image::{imageops, GrayImage};
use serde::Deserialize;
use serde_json::{json, Value};
use std::collections::{BTreeMap, HashSet};
use std::path::Path;

#[derive(Deserialize)]
struct Record {
    #[serde(alias = "crop")]
    crop_path: String,
    #[serde(alias = "label", alias = "label_text", alias = "gt_nfc")]
    text: String,
    #[serde(alias = "source_doc_id", alias = "doc_id")]
    doc: String,
    #[serde(alias = "line_id")]
    id: String,
    script_class: Option<String>,
    split: Option<String>,
    source_dataset: Option<String>,
    license: Option<String>,
    label_tier: Option<String>,
    licence_evidence: Option<String>,
    source_url: Option<String>,
    attribution: Option<String>,
    admitted: Option<bool>,
    word_tags: Option<Value>,
}

fn strip(img: GrayImage) -> Result<GrayImage> {
    let (w, h) = img.dimensions();
    anyhow::ensure!(w > 0 && h > 0, "empty_crop");
    let mut nw = (w as f64 * 48.0 / h as f64).round().max(1.0) as u32;
    let mut nh = 48;
    if nw > 2560 {
        nh = (h as f64 * 2560.0 / w as f64).round() as u32;
        anyhow::ensure!(nh >= 14, "strip_below_14px_floor");
        nw = 2560;
    }
    let resized = imageops::resize(&img, nw, nh, imageops::FilterType::Lanczos3);
    let mut tail = Vec::new();
    for y in 0..nh { for x in nw.saturating_sub(2)..nw { tail.push(resized.get_pixel(x, y)[0]); } }
    tail.sort_unstable();
    let bg = tail[tail.len()/2];
    let mut canvas = GrayImage::from_pixel(nw.max(64), 48, image::Luma([bg]));
    imageops::replace(&mut canvas, &resized, 0, ((48-nh)/2) as i64);
    Ok(canvas)
}

const CLASSES: &[&str] = &["greek_mono", "greek_poly", "greek_latin_cs", "latin", "cyrillic", "furniture"];

fn contract_class(text: &str) -> Option<String> {
    crate::corpus::classify(text, false).map(|c| {
        if c == "greek_cyrillic_cs" || c == "cyrillic_latin_cs" { "cyrillic".into() } else { c.into() }
    })
}

pub fn run(records: &str, crops: &str, out: &str, partition: &str) -> Result<()> {
    anyhow::ensure!(!partition.trim().is_empty(), "partition must be nonempty");
    let root = Path::new(out);
    anyhow::ensure!(!root.exists() || std::fs::read_dir(root)?.next().is_none(), "import output must be new or empty");
    let crop_root = std::fs::canonicalize(crops).context("crop directory")?;
    let bytes = std::fs::read(records).context("records JSONL")?;
    let codec = Codec::v1();
    let recipe = Recipe::example();
    let band_path = Path::new(env!("CARGO_MANIFEST_DIR")).join("appearance_band.json");
    let band: AppearanceBand = serde_json::from_slice(&std::fs::read(&band_path)?)?;
    let mut rows = Vec::new();
    let mut metas = Vec::new();
    let mut ledger = Vec::<Value>::new();
    let mut warnings = Vec::<Value>::new();
    let mut tags = Vec::<Value>::new();
    let mut hashes = BTreeMap::<String, String>::new();
    let mut record_hashes = BTreeMap::<String, String>::new();
    let mut seen = HashSet::new();
    let mut doc_splits = BTreeMap::<String, String>::new();
    let mut label_tiers = BTreeMap::<String, usize>::new();
    let mut n_records = 0;
    for (line, raw) in std::str::from_utf8(&bytes)?.lines().enumerate() {
        if raw.trim().is_empty() { continue; }
        n_records += 1;
        let record: Record = serde_json::from_str(raw).with_context(|| format!("record line {}", line+1))?;
        anyhow::ensure!(!record.id.is_empty() && !record.doc.is_empty(), "record {} needs doc and line id", line+1);
        anyhow::ensure!(seen.insert(record.id.clone()), "duplicate line id {}", record.id);
        record_hashes.insert(record.id.clone(), hash(raw.as_bytes()));
        let drop = |reason: String| json!({"record_line": line+1, "line_id": record.id, "doc": record.doc, "reason": reason});
        if record.admitted == Some(false) { ledger.push(drop("not_admitted".into())); continue; }
        let gt = Codec::normalize_gt(&record.text);
        let Some(ids) = codec.encode(&gt) else { ledger.push(drop("unmapped_codepoint".into())); continue; };
        if ids.is_empty() { ledger.push(drop("empty_label".into())); continue; }
        let class = record.script_class.clone().or_else(|| contract_class(&gt));
        let Some(class) = class else { ledger.push(drop("unmapped_script_class".into())); continue; };
        if !CLASSES.contains(&class.as_str()) { ledger.push(drop(format!("invalid_script_class:{class}"))); continue; }
        let split = record.split.clone().unwrap_or_else(|| "train".into());
        anyhow::ensure!(["train", "val", "reserved"].contains(&split.as_str()), "invalid split for {}", record.id);
        if let Some(previous) = doc_splits.insert(record.doc.clone(), split.clone()) {
            anyhow::ensure!(previous == split, "source document {} crosses split boundary", record.doc);
        }
        let path = crop_root.join(&record.crop_path);
        let path = match std::fs::canonicalize(&path) {
            Ok(p) => p,
            Err(e) => { ledger.push(drop(format!("crop_read_error:{e}"))); continue; }
        };
        anyhow::ensure!(path.starts_with(&crop_root), "crop path outside --crops: {}", path.display());
        let payload = std::fs::read(&path)?;
        hashes.insert(record.id.clone(), hash(&payload));
        let img = match image::load_from_memory(&payload) {
            Ok(i) => i.to_luma8(),
            Err(e) => { ledger.push(drop(format!("crop_decode_error:{e}"))); continue; }
        };
        let img = match strip(img) {
            Ok(i) => i,
            Err(e) => { ledger.push(drop(e.to_string())); continue; }
        };
        let px: Vec<f32> = img.as_raw().iter().map(|v| *v as f32/255.0).collect();
        let contrast = crate::distort::contrast_of(&px);
        let mut sorted = img.as_raw().clone();
        sorted.sort_unstable();
        let light = sorted[sorted.len()/2] < 128;
        let len = gt.chars().count();
        if len < recipe.lengths.min_chars || len > recipe.lengths.max_chars {
            warnings.push(json!({"line_id": record.id, "reason": "length_outside_3_140_nfd", "gt_len": len}));
        }
        if contrast < recipe.ink_contrast_floor {
            warnings.push(json!({"line_id": record.id, "reason": "low_contrast", "contrast": contrast}));
        }
        let source = record.source_dataset.clone().unwrap_or_else(|| "real_import".into());
        if let Some(tier) = &record.label_tier {
            anyhow::ensure!(["gold", "silver", "silver_ocr_layer", "silver_agreed", "gold_aligned"].contains(&tier.as_str()),
                            "invalid admitted label_tier for {}: {tier}", record.id);
            anyhow::ensure!(record.license.as_ref().is_some_and(|s| !s.trim().is_empty()),
                            "tiered real record {} needs license", record.id);
            *label_tiers.entry(tier.clone()).or_default() += 1;
        }
        let nfc = Codec::render_form(&gt);
        let word_tags = record.word_tags.clone().unwrap_or_else(|| Value::Array(gt.split(' ').map(|word| {
            json!({"text_nfd": word, "script_class": contract_class(word), "tagger": "linefactory/corpus::classify"})
        }).collect()));
        tags.push(json!({"line_id": record.id, "source_doc_id": record.doc, "partition_id": partition,
                        "source_dataset": source, "label_tier": record.label_tier,
                        "licence": record.license, "source_url": record.source_url,
                        "licence_evidence": record.licence_evidence, "attribution": record.attribution,
                        "crop_path": path, "script_class_source": if record.script_class.is_some() { "record" } else { "linefactory" },
                        "word_tags": word_tags, "word_tags_source": if record.word_tags.is_some() { "record" } else { "linefactory" }}));
        let mut png = Vec::new();
        img.write_to(&mut std::io::Cursor::new(&mut png), image::ImageFormat::Png)?;
        rows.push(Row {
            image_png: png, width: img.width() as i32, gt_nfd: gt.clone(), gt_nfc: nfc,
            label_ids: ids.iter().map(|i| *i as i32).collect(), script_class: class.clone(), split: split.clone(),
            severity: 0, applied_ops: vec!["import_real:resize_letterbox".into()], font: "real".into(),
            polarity: if light { "light_on_dark".into() } else { "dark_on_light".into() },
            bg_type: "flat".into(), accent_survival: 1.0, reuse_index: 0,
            line_id: record.id.clone(), source_dataset: source.clone(), source_doc_id: record.doc.clone(),
            license: record.license.unwrap_or_else(|| "unspecified".into()),
        });
        metas.push(RowMeta {
            script_class: class, split, severity: 0, polarity_light: light, bg_type: "flat".into(), font: "real".into(),
            accent_survival: 1.0, has_top_marks: gt.chars().any(Codec::is_top_mark), reuse_index: 0,
            gt_len: len, source_dataset: source, source_doc_id: record.doc, contrast, letterpress: false, lunate: false,
        });
    }
    std::fs::create_dir_all(root)?;
    let mut sink = ShardSink::new(out)?;
    let mut counts = BTreeMap::<String, usize>::new();
    for row in rows { *counts.entry(row.script_class.clone()).or_default() += 1; sink.push(row)?; }
    let written = sink.finish()?;
    let main: Vec<&RowMeta> = metas.iter().collect(); // include reserved: a real import reports every crop
    let checks = vec![appearance_check(&main, Some(&band)), length_check(&main, &recipe)];
    let audit_ok = !metas.is_empty() && checks.iter().all(|c| c.ok) && warnings.is_empty();
    let report = json!({"kind": "real", "report_only": true, "ok": audit_ok, "n_rows": metas.len(), "checks": checks, "warnings": warnings,
                       "note": "appearance/length never drop real crops; accent_survival=1 is an unmeasured placeholder; bg_type=flat is the import default, not a measured domain claim"});
    let info = json!({"kind": "real", "codec_version": CODEC_VERSION, "partition_id": partition,
                      "records_sha256": hash(&bytes), "record_sha256": record_hashes, "crop_sha256": hashes,
                      "shard_sha256": shard_hashes(root)?, "counts_per_script_class": counts,
                      "n_records": n_records, "n_written": metas.len(), "written": written,
                      "label_tier_counts": label_tiers,
                      "word_tags_sha256": hash(tags.iter().map(|t| serde_json::to_string(t).unwrap()+"\n").collect::<String>().as_bytes()),
                      "drop_ledger": ledger, "audit_ok": audit_ok,
                      "appearance_band_sha256": hash(&std::fs::read(band_path)?), "doc_splits": doc_splits});
    for (name, obj) in [("build_info.json", info), ("audit_report.json", report), ("select_report.json", json!({"kind": "real", "drop_ledger": ledger}))] {
        std::fs::write(root.join(name), serde_json::to_string_pretty(&obj)?)?;
    }
    let jsonl = tags.iter().map(|t| serde_json::to_string(t).unwrap()+"\n").collect::<String>();
    std::fs::write(root.join("word_tags.jsonl"), jsonl)?;
    eprintln!("[import-real] records={n_records} written={} drops={} (report-only audit_ok={audit_ok})", metas.len(), ledger.len());
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn resize_contract_and_readability_floor() {
        let image = strip(GrayImage::from_pixel(12, 48, image::Luma([211]))).unwrap();
        assert_eq!(image.dimensions(), (64, 48));
        assert_eq!(image.get_pixel(63, 0)[0], 211);
        assert!(strip(GrayImage::new(10000, 20)).is_err());
        assert_eq!(strip(GrayImage::new(3000, 48)).unwrap().dimensions(), (2560, 48));
    }
    #[test]
    fn real_label_normalization_uses_codec() {
        let gt = Codec::normalize_gt("  ἅ  δʼ  ϲ ");
        assert_eq!(gt, "α\u{0314}\u{0301} δ' σ");
        assert!(Codec::v1().encode(&gt).is_some());
        assert_eq!(contract_class(&gt), Some("greek_poly".into()));
    }
}

#[cfg(test)]
mod round_trip {
    use super::*;
    use arrow_array::{Array, BinaryArray, StringArray};
    use parquet::arrow::arrow_reader::ParquetRecordBatchReaderBuilder;
    #[test]
    fn twenty_fixture_crops_round_trip() {
        let fixtures = Path::new(env!("CARGO_MANIFEST_DIR")).join("../data/fixtures/real_crops");
        let nonce = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos();
        let out = std::env::temp_dir().join(format!("c0-real-{}-{nonce}", std::process::id()));
        run(fixtures.join("records.jsonl").to_str().unwrap(), fixtures.to_str().unwrap(), out.to_str().unwrap(), "C0-fixture-v1").unwrap();
        let info: Value = serde_json::from_slice(&std::fs::read(out.join("build_info.json")).unwrap()).unwrap();
        assert_eq!(info["n_written"], 20);
        assert_eq!(info["kind"], "real");
        assert_eq!(info["drop_ledger"].as_array().unwrap().len(), 0);
        let mut total = 0;
        for split in ["train", "val"] {
            let file = std::fs::File::open(out.join(split).join("shard-00000.parquet")).unwrap();
            let builder = ParquetRecordBatchReaderBuilder::try_new(file).unwrap();
            assert_eq!(builder.schema().as_ref(), crate::shard::schema().as_ref());
            for batch in builder.build().unwrap() {
                let batch = batch.unwrap();
                total += batch.num_rows();
                let images = batch.column(0).as_any().downcast_ref::<BinaryArray>().unwrap();
                let labels = batch.column(2).as_any().downcast_ref::<StringArray>().unwrap();
                for i in 0..images.len() {
                    let img = image::load_from_memory(images.value(i)).unwrap().to_luma8();
                    assert_eq!(img.height(), 48);
                    assert!((64..=2560).contains(&img.width()));
                    assert_eq!(Codec::normalize_gt(labels.value(i)), labels.value(i));
                }
            }
        }
        assert_eq!(total, 20);
        std::fs::remove_dir_all(out).unwrap();
    }

    #[test]
    fn tiered_source_metadata_survives_import() {
        let fixtures = Path::new(env!("CARGO_MANIFEST_DIR")).join("../data/fixtures/real_crops");
        let nonce = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos();
        let root = std::env::temp_dir().join(format!("o4b-tier-{}-{nonce}", std::process::id()));
        std::fs::create_dir_all(&root).unwrap();
        let bytes = std::fs::read_to_string(fixtures.join("records.jsonl")).unwrap();
        let mut record: Value = serde_json::from_str(bytes.lines().next().unwrap()).unwrap();
        record["label_tier"] = json!("gold");
        record["license"] = json!("CC-BY-4.0");
        record["source_dataset"] = json!("polyton_db");
        record["source_url"] = json!("https://example.org/fixture");
        record["attribution"] = json!("fixture creator");
        std::fs::write(root.join("records.jsonl"), record.to_string()+"\n").unwrap();
        run(root.join("records.jsonl").to_str().unwrap(), fixtures.to_str().unwrap(), root.join("import").to_str().unwrap(), "o4b-documents-v1").unwrap();
        let tags = std::fs::read_to_string(root.join("import/word_tags.jsonl")).unwrap();
        let tag: Value = serde_json::from_str(tags.trim()).unwrap();
        assert_eq!(tag["label_tier"], "gold");
        assert_eq!(tag["licence"], "CC-BY-4.0");
        assert_eq!(tag["source_dataset"], "polyton_db");
        let info: Value = serde_json::from_slice(&std::fs::read(root.join("import/build_info.json")).unwrap()).unwrap();
        assert_eq!(info["label_tier_counts"]["gold"], 1);
        assert_eq!(info["word_tags_sha256"], hash(tags.as_bytes()));
        std::fs::remove_dir_all(root).unwrap();
    }
}
