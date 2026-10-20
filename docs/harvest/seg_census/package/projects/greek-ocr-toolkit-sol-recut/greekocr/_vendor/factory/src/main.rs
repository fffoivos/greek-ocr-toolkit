//! linefactory — parallel synthetic line-strip factory for greek-page-ocr.
//! recipe -> ingest(pool) -> select -> render/distort (repair-not-drop) -> audit -> parquet shards.

mod audit;
mod build;
mod codec;
mod composer;
mod corpus;
mod custody;
mod import_real;
mod distort;
mod measure;
mod recipe;
mod render;
mod select;
mod shard;

use anyhow::{Context, Result};
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "linefactory", version, about)]
struct Cli {
    #[command(subcommand)]
    cmd: Cmd,
}

#[derive(Subcommand)]
enum Cmd {
    /// Emit the versioned codec artifact (codec/v1.json).
    CodecEmit {
        #[arg(long, default_value = "codec/v1.json")]
        out: String,
    },
    /// Write an example recipe to edit.
    ExampleRecipe {
        #[arg(long, default_value = "factory/recipe.example.json")]
        out: String,
    },
    /// Ingest corpus JSONL ({"text","source_dataset","source_doc_id","license"}) into a
    /// quality-gated candidate pool (+ ingest_report.json next to it).
    Ingest {
        #[arg(long)]
        corpus: String,
        #[arg(long)]
        recipe: String,
        #[arg(long)]
        out: String,
    },
    /// Import real line crops through the factory contract, normalization and report-only audit.
    ImportReal {
        #[arg(long)]
        records: String,
        #[arg(long)]
        crops: String,
        #[arg(long)]
        out: String,
        #[arg(long)]
        partition: String,
    },
    /// Select + render + audit + write shards. Exit 2 if the audit quarantines the build.
    Build {
        #[arg(long)]
        recipe: String,
        #[arg(long)]
        pool: String,
        #[arg(long)]
        out: String,
        /// cap the number of rendered strips (representative prefix — jobs are interleaved)
        #[arg(long)]
        smoke: Option<usize>,
        /// proceed with DISCLOSED class/atom supply deficits instead of failing
        #[arg(long, default_value_t = false)]
        allow_deficit: bool,
    },
    /// Render the RESERVED band with the HELD-OUT fonts only -> font-OOD transfer-dev eval set
    /// Requires a versioned eval_only recipe; bind reserved shards with --transfer-mix.
    TransferDev {
        #[arg(long)]
        recipe: String,
        #[arg(long)]
        pool: String,
        #[arg(long)]
        out: String,
        /// Optional assertion of recipe target; never overrides recipe bytes.
        #[arg(long)]
        cap: Option<usize>,
    },
    /// Measure an appearance band from REAL page crops (feeds recipe.appearance_band).
    Measure {
        #[arg(long)]
        images: String,
        #[arg(long, default_value = "factory/appearance_band.json")]
        out: String,
    },
    /// Compose synthetic PAGES with free GT (line boxes, block classes, order) — parser training data.
    ComposePages {
        #[arg(long)]
        recipe: String,
        #[arg(long)]
        pool: String,
        #[arg(long)]
        out: String,
        #[arg(long, default_value_t = 8)]
        n: usize,
        /// force a single grammar for all pages (eyeball sheets); default = weighted sampling.
        #[arg(long)]
        grammar: Option<String>,
    },
    /// Stage-by-stage composition demo for a few REAL build jobs (owner-facing).
    Stages {
        #[arg(long)]
        recipe: String,
        #[arg(long)]
        pool: String,
        #[arg(long)]
        out: String,
    },
    /// Per-op + combined distortion LADDER at escalating extremes (owner review protocol).
    Ladder {
        #[arg(long)]
        recipe: String,
        #[arg(long)]
        out: String,
    },
    /// Readability-ceiling probe: ALL ops forced at max severity on a mixed sample.
    Stress {
        #[arg(long)]
        recipe: String,
        #[arg(long)]
        pool: String,
        #[arg(long)]
        out: String,
        #[arg(long, default_value_t = 24)]
        n: usize,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    match cli.cmd {
        Cmd::CodecEmit { out } => {
            let c = codec::Codec::v1();
            if let Some(dir) = std::path::Path::new(&out).parent() {
                std::fs::create_dir_all(dir)?;
            }
            std::fs::write(&out, c.emit_json()).with_context(|| format!("write {out}"))?;
            eprintln!("[codec] {} atoms (+blank) -> {out}", c.atoms.len());
        }
        Cmd::ExampleRecipe { out } => {
            std::fs::write(&out, serde_json::to_string_pretty(&recipe::Recipe::example())?)?;
            eprintln!("[recipe] example -> {out}");
        }
        Cmd::Ingest { corpus, recipe, out } => {
            let r = recipe::Recipe::load(&recipe)?;
            let c = codec::Codec::v1();
            let (pool, rep) = corpus::ingest(&corpus, &r, &c)?;
            let mut w = String::with_capacity(pool.len() * 128);
            for l in &pool {
                w.push_str(&serde_json::to_string(l)?);
                w.push('\n');
            }
            std::fs::write(&out, w)?;
            let rep_path = format!("{out}.ingest_report.json");
            std::fs::write(&rep_path, serde_json::to_string_pretty(&rep)?)?;
            eprintln!(
                "[ingest] read {} kept {} -> {out} (report {rep_path})",
                rep.read, rep.kept
            );
        }
        Cmd::ImportReal { records, crops, out, partition } => {
            import_real::run(&records, &crops, &out, &partition)?;
        }
        Cmd::Build { recipe, pool, out, smoke, allow_deficit } => {
            let r = recipe::Recipe::load(&recipe)?;
            let c = codec::Codec::v1();
            let pool = build::load_pool(&pool)?;
            let (mut jobs, sel_rep) = if r.eval_only.is_some() {
                (select::eval_jobs(&pool, &r)?, serde_json::json!({"mode": "eval_only", "target_total": r.target_total}))
            } else {
                let (jobs, rep) = select::select(&pool, &r, &c, allow_deficit)?;
                (jobs, serde_json::to_value(rep)?)
            };
            if let Some(n) = smoke {
                use rand::seq::SliceRandom;
                use rand::SeedableRng;
                let mut rng = rand_chacha::ChaCha20Rng::seed_from_u64(r.seed ^ 0x5710CE);
                jobs.shuffle(&mut rng);
                jobs.truncate(n);
                eprintln!("[build] SMOKE: {n} jobs");
            }
            let ok = build::run(&r, jobs, &c, &out, serde_json::to_value(&sel_rep)?, None, allow_deficit)?;
            if !ok {
                std::process::exit(2);
            }
        }
        Cmd::TransferDev { recipe, pool, out, cap } => {
            let r = recipe::Recipe::load(&recipe)?;
            let eval = r.eval_only.as_ref().context(
                "transfer-dev requires a versioned eval_only recipe (fixtures: factory/recipe.transfer-smoke.v1.json)")?;
            anyhow::ensure!(cap.is_none() || cap == Some(r.target_total),
                "--cap must equal recipe.target_total; use a new versioned recipe to change it");
            let c = codec::Codec::v1();
            let pool = build::load_pool(&pool)?;
            let jobs = select::eval_jobs(&pool, &r)?;
            let rep = serde_json::json!({
                "mode": "transfer_dev", "held_in_fonts": eval.fonts, "n_reserved_jobs": jobs.len(),
            });
            // Preserve recipe identity and enforce the evaluation audit.
            let ok = build::run(&r, jobs, &c, &out, rep, None, false)?;
            if !ok {
                std::process::exit(2);
            }
            eprintln!("[transfer-dev] done -> {out}/reserved/ (bind a mix; load with --transfer-mix)");
        }
        Cmd::Measure { images, out } => measure::measure(&images, &out)?,
        Cmd::ComposePages { recipe, pool, out, n, grammar } => {
            let r = recipe::Recipe::load(&recipe)?;
            let pool = build::load_pool(&pool)?;
            let streams = composer::pool_streams(&pool);
            anyhow::ensure!(!streams.is_empty(), "pool has no usable text streams");
            composer::compose_run(&r, &streams, &out, n, grammar.as_deref())?;
        }
        Cmd::Stages { recipe, pool, out } => {
            let r = recipe::Recipe::load(&recipe)?;
            let c = codec::Codec::v1();
            let pool = build::load_pool(&pool)?;
            build::stages_run(&r, &pool, &c, &out)?;
        }
        Cmd::Ladder { recipe, out } => {
            let r = recipe::Recipe::load(&recipe)?;
            build::ladder_run(&r, &out)?;
        }
        Cmd::Stress { recipe, pool, out, n } => {
            let r = recipe::Recipe::load(&recipe)?;
            let pool = build::load_pool(&pool)?;
            build::stress_run(&r, &pool, &out, n)?;
        }
    }
    Ok(())
}
