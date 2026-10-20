"""Local classification and census only; no existing decision is modified."""
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import sys

D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[4]))
from greekocr.harvest.numeric_cells import classify_cell, _character_count


def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def evaluate():
    base = D.parent
    owners = {r['line_id']: r for r in map(json.loads, (base / 'scored/owner_rows.jsonl').read_text().splitlines())}
    result = []
    for r in map(json.loads, (base / 'gate2/replay_segeval1.jsonl').read_text().splitlines()):
        frame = r['after']['frame']
        text = owners[r['line_id']]['google_text']
        row = dict(row_id=r['line_id'], text=text, width_px=frame['source_width'],
                   height_px=frame['source_height'], characters=r['after']['evidence']['characters'],
                   owner_standard_state=r['owner_standard_state'], verdict_05=r['verdict_05'],
                   verdict_08=r['verdict_08'], reason_08=r['after']['reason'],
                   false_reject_08=r['owner_standard_state'] == 'fine' and r['verdict_08'] == 'DROP')
        row.update(classify_cell(text, row['width_px'], row['height_px']))
        result.append(row)
    assert len(result) == 150 and sum(r['false_reject_08'] for r in result) == 18
    (D / 'evaluation_150_cells.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in result))
    ordinary = sorted((r for r in result if r['owner_standard_state'] == 'fine'
                       and not r['is_numeric_output'] and r['characters'] >= 20), key=lambda r: r['row_id'])[:20]
    assert len(ordinary) == 20 and all(not r['is_cell'] for r in ordinary)
    fixtures = dict(numeric_evaluation=[r for r in result if r['is_numeric_output']],
                    false_rejects=[r for r in result if r['false_reject_08']], ordinary=ordinary,
                    source_hashes={str(p.relative_to(base)): sha(p) for p in
                                   (base / 'scored/owner_rows.jsonl', base / 'gate2/replay_segeval1.jsonl')})
    dump(D / 'evaluation_fixtures.json', fixtures)
    return dict(rows=150, numeric_output=sum(r['is_numeric_output'] for r in result),
                cells=sum(r['is_cell'] for r in result), false_rejects=18,
                cells_among_false_rejects=sum(r['is_cell'] and r['false_reject_08'] for r in result))


def main():
    path = D / 'population_cells.jsonl.gz'
    original_sha = sha(path)
    axes = {a: defaultdict(Counter) for a in ('source', 'primary_class', 'script_class', 'wave', 'parent_id')}
    total, pipeline, verdicts, reasons, cross, missing = Counter(), defaultdict(Counter), defaultdict(Counter), defaultdict(Counter), Counter(), defaultdict(Counter)
    tmp = path.with_suffix('.gz.classified.tmp')
    with gzip.open(path, 'rt') as stream, gzip.GzipFile(filename=str(tmp), mode='wb', mtime=0, compresslevel=6) as out:
        for line in stream:
            r = json.loads(line)
            if r['characters'] is not None:
                assert r['characters'] == _character_count(r['raw_text']), r['row_id']
            flags = classify_cell(r['raw_text'], r['width_px'], r['height_px'], r['xheight_px'])
            r.update(flags)
            groups = ['all']
            if r['is_numeric_output']:
                groups.append('numeric')
            if r['is_cell']:
                groups.append('cells')
            if r['is_numeric_output'] and not r['is_small_image']:
                groups.append('numeric_not_small')
            if r['is_small_image'] and not r['is_numeric_output']:
                groups.append('small_not_numeric')
            for group in groups:
                total[group] += 1
                pipeline[group][r['pipeline_disposition']] += 1
                verdicts[group][r['verdict_05'] or 'NOT_EVALUATED'] += 1
                reasons[group][(r['verdict_05'] or 'NOT_EVALUATED') + ' | ' + (r['reason_05'] or 'no segmentation evidence')] += 1
                for k in ('width_px', 'height_px', 'xheight_px', 'characters'):
                    if r[k] is None:
                        missing[group][k] += 1
                for axis in axes:
                    axes[axis][r[axis]][group] += 1
            if r['is_cell']:
                cross[(r['pipeline_disposition'], r['verdict_05'] or 'NOT_EVALUATED')] += 1
            out.write((json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n').encode())
    assert total['all'] == 592466
    receipt = json.loads((D / 'export_receipt.json').read_text())
    assert dict(pipeline['all']) == {k: v for k, v in receipt['provenance']['summary_dispositions'].items() if v}
    tmp.replace(path)
    dump(D / 'population_summary.json', dict(total=dict(total),
        by={a: {k: dict(v) for k, v in sorted(rows.items())} for a, rows in axes.items()},
        pipeline_dispositions={k: dict(v) for k, v in pipeline.items()},
        segmentation_verdicts={k: dict(v) for k, v in verdicts.items()},
        segmentation_reasons={k: dict(v) for k, v in reasons.items()},
        cells_pipeline_by_segmentation={' | '.join(k): v for k, v in cross.items()},
        missing={k: dict(v) for k, v in missing.items()}, evaluation=evaluate()))
    receipt = json.loads((D / 'export_receipt.json').read_text())
    receipt.update(pre_classification_reduced_sha256=original_sha, reduced_sha256=sha(path),
                   reduced_bytes=path.stat().st_size, classifier_sha256=sha(D.parents[4] / 'greekocr/harvest/numeric_cells.py'))
    dump(D / 'export_receipt.json', receipt)
    print(json.dumps(total, indent=2))


if __name__ == '__main__':
    main()
