//! Parquet shard writer — schema per docs/data_contracts.md §3 (exact names/types).

use anyhow::{Context, Result};
use arrow_array::builder::{
    BinaryBuilder, Float32Builder, Int32Builder, ListBuilder, StringBuilder,
};
use arrow_array::RecordBatch;
use arrow_schema::{DataType, Field, Schema};
use parquet::arrow::ArrowWriter;
use parquet::basic::{Compression, ZstdLevel};
use parquet::file::properties::WriterProperties;
use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::Arc;

pub const SHARD_ROWS: usize = 4096;

#[derive(Clone)]
pub struct Row {
    pub image_png: Vec<u8>,
    pub width: i32,
    pub gt_nfd: String,
    pub gt_nfc: String,
    pub label_ids: Vec<i32>,
    pub script_class: String,
    pub split: String,
    pub severity: i32,
    pub applied_ops: Vec<String>,
    pub font: String,
    pub polarity: String,
    pub bg_type: String,
    pub accent_survival: f32,
    pub reuse_index: i32,
    pub line_id: String,
    pub source_dataset: String,
    pub source_doc_id: String,
    pub license: String,
}

pub fn schema() -> Arc<Schema> {
    let item_i32 = Arc::new(Field::new("item", DataType::Int32, true));
    let item_utf8 = Arc::new(Field::new("item", DataType::Utf8, true));
    Arc::new(Schema::new(vec![
        Field::new("image_png", DataType::Binary, false),
        Field::new("width", DataType::Int32, false),
        Field::new("gt_nfd", DataType::Utf8, false),
        Field::new("gt_nfc", DataType::Utf8, false),
        Field::new("label_ids", DataType::List(item_i32), false),
        Field::new("codec_version", DataType::Utf8, false),
        Field::new("script_class", DataType::Utf8, false),
        Field::new("split", DataType::Utf8, false),
        Field::new("severity", DataType::Int32, false),
        Field::new("applied_ops", DataType::List(item_utf8), false),
        Field::new("font", DataType::Utf8, false),
        Field::new("polarity", DataType::Utf8, false),
        Field::new("bg_type", DataType::Utf8, false),
        Field::new("accent_survival", DataType::Float32, false),
        Field::new("reuse_index", DataType::Int32, false),
        Field::new("line_id", DataType::Utf8, false),
        Field::new("source_dataset", DataType::Utf8, false),
        Field::new("source_doc_id", DataType::Utf8, false),
        Field::new("license", DataType::Utf8, false),
    ]))
}

fn to_batch(rows: &[Row]) -> Result<RecordBatch> {
    let mut image_png = BinaryBuilder::new();
    let mut width = Int32Builder::new();
    let mut gt_nfd = StringBuilder::new();
    let mut gt_nfc = StringBuilder::new();
    let mut label_ids = ListBuilder::new(Int32Builder::new());
    let mut codec_version = StringBuilder::new();
    let mut script_class = StringBuilder::new();
    let mut split = StringBuilder::new();
    let mut severity = Int32Builder::new();
    let mut applied_ops = ListBuilder::new(StringBuilder::new());
    let mut font = StringBuilder::new();
    let mut polarity = StringBuilder::new();
    let mut bg_type = StringBuilder::new();
    let mut accent_survival = Float32Builder::new();
    let mut reuse_index = Int32Builder::new();
    let mut line_id = StringBuilder::new();
    let mut source_dataset = StringBuilder::new();
    let mut source_doc_id = StringBuilder::new();
    let mut license = StringBuilder::new();
    for r in rows {
        image_png.append_value(&r.image_png);
        width.append_value(r.width);
        gt_nfd.append_value(&r.gt_nfd);
        gt_nfc.append_value(&r.gt_nfc);
        for id in &r.label_ids {
            label_ids.values().append_value(*id);
        }
        label_ids.append(true);
        codec_version.append_value(crate::codec::CODEC_VERSION);
        script_class.append_value(&r.script_class);
        split.append_value(&r.split);
        severity.append_value(r.severity);
        for op in &r.applied_ops {
            applied_ops.values().append_value(op);
        }
        applied_ops.append(true);
        font.append_value(&r.font);
        polarity.append_value(&r.polarity);
        bg_type.append_value(&r.bg_type);
        accent_survival.append_value(r.accent_survival);
        reuse_index.append_value(r.reuse_index);
        line_id.append_value(&r.line_id);
        source_dataset.append_value(&r.source_dataset);
        source_doc_id.append_value(&r.source_doc_id);
        license.append_value(&r.license);
    }
    RecordBatch::try_new(
        schema(),
        vec![
            Arc::new(image_png.finish()),
            Arc::new(width.finish()),
            Arc::new(gt_nfd.finish()),
            Arc::new(gt_nfc.finish()),
            Arc::new(label_ids.finish()),
            Arc::new(codec_version.finish()),
            Arc::new(script_class.finish()),
            Arc::new(split.finish()),
            Arc::new(severity.finish()),
            Arc::new(applied_ops.finish()),
            Arc::new(font.finish()),
            Arc::new(polarity.finish()),
            Arc::new(bg_type.finish()),
            Arc::new(accent_survival.finish()),
            Arc::new(reuse_index.finish()),
            Arc::new(line_id.finish()),
            Arc::new(source_dataset.finish()),
            Arc::new(source_doc_id.finish()),
            Arc::new(license.finish()),
        ],
    )
    .context("record batch")
}

/// Rolling per-split writer: out/{split}/shard-NNNNN.parquet, flushed every SHARD_ROWS.
pub struct ShardSink {
    out: PathBuf,
    buf: HashMap<String, Vec<Row>>,
    n_file: HashMap<String, usize>,
    pub written: HashMap<String, usize>,
}

impl ShardSink {
    pub fn new(out: &str) -> Result<ShardSink> {
        Ok(ShardSink { out: PathBuf::from(out), buf: HashMap::new(), n_file: HashMap::new(), written: HashMap::new() })
    }

    pub fn push(&mut self, row: Row) -> Result<()> {
        let split = row.split.clone();
        let v = self.buf.entry(split.clone()).or_default();
        v.push(row);
        if v.len() >= SHARD_ROWS {
            self.flush_split(&split)?;
        }
        Ok(())
    }

    fn flush_split(&mut self, split: &str) -> Result<()> {
        let rows = match self.buf.get_mut(split) {
            Some(v) if !v.is_empty() => std::mem::take(v),
            _ => return Ok(()),
        };
        let dir = self.out.join(split);
        std::fs::create_dir_all(&dir)?;
        let n = self.n_file.entry(split.into()).or_default();
        let path = dir.join(format!("shard-{n:05}.parquet"));
        *n += 1;
        let props = WriterProperties::builder()
            .set_compression(Compression::ZSTD(ZstdLevel::try_new(3)?))
            .build();
        let file = std::fs::File::create(&path).with_context(|| format!("create {path:?}"))?;
        let batch = to_batch(&rows)?;
        let mut w = ArrowWriter::try_new(file, schema(), Some(props))?;
        w.write(&batch)?;
        w.close()?;
        *self.written.entry(split.into()).or_default() += rows.len();
        Ok(())
    }

    pub fn finish(mut self) -> Result<HashMap<String, usize>> {
        let splits: Vec<String> = self.buf.keys().cloned().collect();
        for s in splits {
            self.flush_split(&s)?;
        }
        Ok(self.written)
    }
}
