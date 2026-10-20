"""Render the complete descriptive census and exact evaluation membership."""
from collections import Counter
import inspect
import json
from pathlib import Path
import re
import sys

D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[4]))
from greekocr.harvest.numeric_cells import classify_cell, MAX_CELL_WIDTH_PX, MAX_CELL_HEIGHT_PX, MAX_CELL_CHARACTERS


def read(name):
    return json.loads((D / name).read_text())


def mdcell(value):
    return str(value).replace('|', '\\|').replace('\n', '<br>')


def table(headers, rows):
    return '| ' + ' | '.join(headers) + ' |\n| ' + ' | '.join(['---'] * len(headers)) + ' |\n' + ''.join(
        '| ' + ' | '.join(mdcell(x) for x in row) + ' |\n' for row in rows) + '\n'


def main(commit):
    s, d, receipt, sample = (read(x) for x in ('population_summary.json', 'distributions.json', 'export_receipt.json', 'sample_receipt.json'))
    tests = int(re.search(r'(\d+) passed', (D / 'tests.log').read_text())[1])
    evaluation = [json.loads(line) for line in (D / 'evaluation_150_cells.jsonl').read_text().splitlines()]
    grammar = inspect.getdoc(classify_cell)
    totals = s['total']
    done = sample['fetched'] == 250
    status = 'done' if done else 'blocked'
    lines = ['# SEG-CELLS-1 — descriptive classification, census and crop samples\n',
             ('**Status: classification, complete census and tests finished; numeric crop samples blocked under the SCP-only constraint. Only 50/250 crops fetched.** No `done` claim is made. The pending fallback below requires an explicit owner scope change.\n' if not done else '**Status: complete.**\n'),
             'No segmentation verdict, policy, detector, version file, reader output or pipeline disposition was changed. The new pure function has no consumer in the pipeline. No Slurm, OCR reader or image regeneration ran. Clariden operations were read-only Python/stdout metadata reduction and path checks, plus SCP reads of existing crops. Nothing was pushed.\n',
             '## Frozen population and receipts\n',
             f"The pinned generation is `{receipt['provenance']['current']['export_id']}`: **592,466 rows**, **8,168,706,501 bytes**, SHA256 `{receipt['export_receipt']['export_sha256']}`. The full export stayed on Clariden. Before/after size+mtime and CURRENT equality, resolved path, summary hash and exact export hash/count all passed. Every raw-text hash was rebound to verified frozen parent metadata; W1/W2 crop hashes also match their parent metadata. The original-v2 parent metadata is the earlier frozen read-only export, with its parent receipts checked against the census configuration. See [export_receipt.json](export_receipt.json), [export_remote.py](export_remote.py), [reduce_population.py](reduce_population.py).\n",
             'The reduced [population_cells.jsonl.gz](population_cells.jsonl.gz) has exactly one record per population row: row and parent IDs; source, primary and script classes, wave; literal raw Google text; original crop width/height from the 0.5 segmentation frame; saved character count; raw trimmed codepoint count; x-height and method; unchanged 0.5 verdict/reason and pipeline disposition/reasons; crop path/hash binding; and the four descriptive classifier fields. There are no missing dimensions, saved character counts or curve-derived x-heights in this export.\n',
             '## Exact classifier grammar and chosen limits\n',
             '```text\n' + grammar + '\n```\n',
             'The named constants are `MAX_CELL_WIDTH_PX=200`, `MAX_CELL_HEIGHT_PX=40`, `MAX_CELL_CHARACTERS=10`. The width proposal rounds numeric P95=169 up to the next 50 px; height rounds numeric P75=35 up to the next 10 px; the character limit is numeric P90=10 without rounding. This selects the compact numeric population for review. It is a descriptive choice, not an inferred ground-truth boundary or an optimum. All distributions and the grid were computed before the crop sample was drawn.\n',
             'The width distribution is strongly separated: numeric median/P95 are 59/169 px, versus 765/2040 px for other outputs. Height alone is weaker: numeric median/P75/P90 are 22/35/81 px, versus 44/67/93 px for other outputs. The height cut deliberately leaves the tall numeric tail for boundary review. Saved visible-character median/P90 are 6/10 for numeric outputs, versus 44/57 for other outputs. The joint cut retains ' + f"{totals['cells']:,}/{totals['numeric']:,} numeric outputs ({100*totals['cells']/totals['numeric']:.2f}%) and also describes {totals['small_not_numeric']:,} small non-numeric rows. No cell accuracy is asserted.\n",
             'X-height is recovered only from saved evidence: median positive `base(x)-mean(x)` on the unique main detected row, at shared saved x coordinates (all 592,466 rows). These are the detector’s saved, rounded curve estimates, not independently measured font truth. Tiny numeric curves have substantial tails (numeric height P95=8.0 x-heights; all rows P95=4.57), supporting the decision to keep x-height out of this proposed pixel cut. No image was opened to derive thresholds.\n',
             '### Sensitivity of the proposed joint cut\n']
    cuts = [x for x in d['candidate_cuts'] if
            (x['height'] == 40 and x['chars'] == 10 and x['width'] in (100, 150, 200, 250, 300)) or
            (x['width'] == 200 and x['chars'] == 10 and x['height'] in (30, 50, 60, 80, 100)) or
            (x['width'] == 200 and x['height'] == 40 and x['chars'] in (8, 9, 12, 16))]
    lines.append(table(['Width ≤ px', 'Height ≤ px', 'Visible chars ≤', 'Numeric rows included'],
                       [[x['width'], x['height'], x['chars'], x['numeric_rows']] for x in cuts]))
    lines += ['## Census totals and composition\n', table(['Population', 'Rows'], [[k, v] for k, v in totals.items()])]
    for axis in ('source', 'primary_class', 'script_class', 'wave', 'parent_id'):
        lines.append('### By ' + axis + '\n')
        lines.append(table([axis, 'All', 'Numeric output', 'Cells'], [[k, v.get('all', 0), v.get('numeric', 0), v.get('cells', 0)] for k, v in s['by'][axis].items()]))
    lines += ['## What the unchanged 0.5 filter and pipeline did\n',
              '**Receipt discrepancy in the brief:** the exact requested hash contains **17,036 segmentation DROP / 151,931 UNCERTAIN / 423,499 KEEP**, rather than 16,736 / 151,645. The previous SEGEVAL draw receipt independently records these same actual totals. Pipeline disposition is a different field: **17,036 DROP / 575,430 HOLD**, with zero ADMIT/KEEP dispositions. Split/edition holds include segmentation KEEP rows. Counts below use the sealed export, without altering a verdict to match the brief.\n',
              table(['0.5 segmentation verdict', 'All', 'Numeric output', 'Cells'], [[k, s['segmentation_verdicts']['all'].get(k, 0), s['segmentation_verdicts']['numeric'].get(k, 0), s['segmentation_verdicts']['cells'].get(k, 0)] for k in ('DROP', 'UNCERTAIN', 'KEEP')]),
              table(['Pipeline disposition', 'All', 'Numeric output', 'Cells'], [[k, s['pipeline_dispositions']['all'].get(k, 0), s['pipeline_dispositions']['numeric'].get(k, 0), s['pipeline_dispositions']['cells'].get(k, 0)] for k in ('DROP', 'HOLD', 'ADMIT')]),
              'The cells among pipeline HOLD are 36,595 = 31,527 segmentation KEEP + 5,068 segmentation UNCERTAIN. Every one of the 2,419 pipeline-DROP cells has segmentation DROP. The required status line uses **HOLD as an alias for 0.5 segmentation UNCERTAIN (5,068)**; it does not substitute the larger pipeline-HOLD count. The table stores the literal verdict `UNCERTAIN`.\n',
              table(['0.5 verdict and literal reason', 'All', 'Numeric output', 'Cells'], [[reason, s['segmentation_reasons']['all'].get(reason, 0), s['segmentation_reasons']['numeric'].get(reason, 0), s['segmentation_reasons']['cells'].get(reason, 0)] for reason in sorted(s['segmentation_reasons']['all'])]),
              '## Dimension distributions\n',
              'Nearest-rank empirical quantiles, using all rows in each cohort. Width and height refer to original source pixels. Character counts use saved segmentation evidence (NFC visible characters); the additional raw-length distribution is available in [distributions.json](distributions.json). No missing measurements were imputed.\n']
    for field in ('width_px', 'height_px', 'characters', 'width_xh', 'height_xh'):
        lines.append('### ' + field + ': quantiles\n')
        qs = ('0', '0.1', '0.25', '0.5', '0.75', '0.9', '0.95', '0.99', '1')
        lines.append(table(['Cohort', 'N', 'Min', 'P10', 'P25', 'P50', 'P75', 'P90', 'P95', 'P99', 'Max'],
                           [[g, d['quantiles'][g][field]['n'], *[f"{d['quantiles'][g][field][q]:.3f}".rstrip('0').rstrip('.') for q in qs]] for g in ('numeric', 'rest', 'all')]))
    for field in ('width_px', 'height_px', 'characters'):
        lines.append('### ' + field + ': histogram\n')
        labels = set(d['histograms']['all'][field])
        def order(label):
            return (label.startswith('>'), float(label.split()[-1])) if label != 'missing' else (2, 0)
        previous, histogram = None, []
        for label in sorted(labels, key=order):
            display = label if previous is None or label.startswith('>') else f'> {previous}, {label}'
            histogram.append([display, *[d['histograms'][g][field].get(label, 0) for g in ('numeric', 'rest', 'all')]])
            previous = label.split()[-1]
        lines.append(table(['Non-overlapping interval', 'Numeric output', 'Rest', 'All'], histogram))
    lines += ['## Seeded samples and observed segment types\n',
              'The draw uses **seed 20261019**, equal probability per row over the full pool across sources (no source quotas), separately for 150 cells, 50 numeric outputs above at least one size limit and 50 small non-numeric rows. Each pool is sorted by `(parent_id,row_id)` before a full `random.Random(seed).sample` permutation, in that category order. The first fetchable rows in each fixed permutation are retained. [sample_order.jsonl.gz](sample_order.jsonl.gz) seals the complete replacement order. [samples.jsonl](samples.jsonl) is the coordinator input, with all requested fields plus group, parent/wave, script class and pipeline disposition.\n',
              f"**{sample['fetched']}/250** crops fetched with read-only SCP; every crop’s SHA256 matches the census binding, every PNG decodes, and its physical dimensions match the saved source frame. There were **{sample['failed_or_unavailable']:,}** unavailable/failed candidate paths before replacements. See [sample_failures.jsonl](sample_failures.jsonl) and [sample_receipt.json](sample_receipt.json). No missing crop was reconstructed, and no new source page was fetched.\n",
              ('**Exhausted numeric pools:** all **39,014 cell paths** and **15,426 numeric-not-small paths** are unavailable. Every numeric row is W1/W2, and both recorded W1/W2 crop directories are absent. The source-page hashes and crop boxes are present in the frozen metadata. [crop_availability_probe.txt](crop_availability_probe.txt) verifies the missing directories and the actual exported crop/source binding. Replacement cannot supply even one numeric crop under the literal SCP-only instruction.\n' if not done else ''),
              ('**Prepared, not executed:** [pending_reconstruction.jsonl](pending_reconstruction.jsonl) binds the first 150 cell and 50 numeric-boundary rows from the original seeded orders to **156** existing source-page identities and frozen boxes. [pending_reconstruction_receipt.json](pending_reconstruction_receipt.json) records the proposed exact action; [stream_missing_crops_remote.py](stream_missing_crops_remote.py) implements the existing L-mode crop / PNG compress_level=3 contract in memory, with source and output SHA256 checks. It has not been run. Proceeding requires owner authorization to change SCP-only fetching to in-memory reconstruction over read-only SSH. No remote file, reader, detector, policy or Slurm action is proposed. The already fetched 50 controls remain available.\n' if not done else ''),
              'The fetchable sample is conditional on archived crop availability. W1/W2 runtime crops can be reconstructed in memory by the existing pipeline without being saved at their declared crop paths; this task deliberately does not run that reconstruction. Missing-source coverage must therefore not be read as absence of those segment types. The source counts below expose this limitation.\n',
              table(['Sample group', 'Pool size', 'Fetched', 'Fetched by source'], [[k, sample['pool_sizes'][k], sample['fetched_counts'].get(k, 0), json.dumps(sample['source_counts'][k], ensure_ascii=False)] for k in sample['targets']]),
              '[sample_observations.md](sample_observations.md) records visual observations from six identified fetched control crops: short Greek/Latin words, capital headers and fragments. These are review material, not accuracy labels. There are no fetched numeric crops and no observed numeric segment-type claim. The classifier does not assign semantic classes such as page number, amount or date.\n',
              '## Exact membership on the 150 evaluation lines\n',
              '**15/150 cells**, **17/150 numeric outputs**. The two numeric non-cells are `330` (103×46 px) and `6 10 6` (63×60 px), both above the 40 px height cut. All 150 rows and their unchanged 0.5/0.8 verdicts are in [evaluation_150_cells.jsonl](evaluation_150_cells.jsonl).\n',
              '**Brief discrepancy:** the base-commit replay and scored Google-text file contain **five numeric cells among the 18 false rejects**, not thirteen. `ΙΙ` is not present in these 150 texts. The 18 false rejects include eleven outputs with 1–9 saved visible characters, of which only five meet the requested numeric grammar; the others contain words or punctuation alone. Both source files were read back equal to commit `410f4566`. No extra numeric class or altered label was introduced to force thirteen witnesses. The synthetic `ΙΙ` grammar case is tested separately.\n',
              table(['False reject row ID', 'Google text', 'Width', 'Height', 'Chars', 'Numeric', 'Cell', '0.8 reason'], [[r['row_id'], r['text'], r['width_px'], r['height_px'], r['characters'], r['is_numeric_output'], r['is_cell'], r['reason_08']] for r in evaluation if r['false_reject_08']]),
              '### All cell members among the 150\n',
              table(['Row ID', 'Google text', 'Width', 'Height', 'Chars', '0.8 verdict', 'Owner state'], [[r['row_id'], r['text'], r['width_px'], r['height_px'], r['characters'], r['verdict_08'], r['owner_standard_state']] for r in evaluation if r['is_cell']]),
              '## Tests, scope and delivery\n',
              f"**{tests} tests passed** with `.venv/`: exact lexical grammar, all 17 actual numeric evaluation outputs, all 18 actual false rejects (five cells), 20 fixed ordinary evaluation lines (no cells), inclusive size/character boundaries, invalid dimensions and x-height independence. The requested thirteen numeric false-reject witnesses cannot be sourced from the exact supplied artifacts; the expanded real-witness coverage and discrepancy above are explicit. [tests.log](tests.log), [evaluation_fixtures.json](evaluation_fixtures.json).\n",
              '```sh\nPYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests/test_numeric_cells.py -q\n```\n',
              f"Implementation commit **`{commit}`**, exact parent **`410f4566db26a9acefb541a5af12312c661fb918`**. The sandbox cannot write the shared Git directory. The authorised [SEGCELLS1.bundle](SEGCELLS1.bundle) contains branch **`sol/seg-cells`** in a separate writable Git directory, followed by a hand-off-only commit. [bundle_receipt.json](bundle_receipt.json) verifies ancestry, independent local import and committed-file bytes. The shared checkout stays on `sol/recut-v1`; shared refs/index and all five pre-existing edited files remain unchanged. No existing production file was staged or changed; production addition is only `numeric_cells.py`. Nothing was pushed.\n",
              f"SEGCELLS1: {status} | numeric-output rows {totals['numeric']}/{totals['all']} | cells {totals['cells']} (thresholds: width<=200px, height<=40px, chars<=10) | cells among 0.5 DROP {s['segmentation_verdicts']['cells']['DROP']}, HOLD {s['segmentation_verdicts']['cells']['UNCERTAIN']}, KEEP {s['segmentation_verdicts']['cells']['KEEP']} | samples fetched {sample['fetched']}/250 | tests {tests} passed | commit {commit}\n"]
    (D / 'HANDOFF.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    main(sys.argv[1])
