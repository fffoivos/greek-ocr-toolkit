"""Read-only SSH reducer, following ../tools/export_remote.py. Writes stdout only.

Run with ``ssh clariden python3 -B - < export_remote.py``. No imports from the
pipeline, databases, readers, image libraries or scheduler. No remote files made.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
from statistics import median
import sys

BASE = Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_02/census')
EXPORT = BASE / 'generations/g1-1c775230225d4bbea5871d4fae2475da/decisions.jsonl'
EXPECTED_SHA = '568d4759257787086ee8c0780cd0d4cf633c5ebf7b355d519d6053ff8c42764a'
current = json.loads((BASE / 'CURRENT.json').read_text())
assert (BASE / 'decisions.jsonl').resolve() == EXPORT
summary_path = Path(current['summary_path'])
summary_bytes = summary_path.read_bytes()
assert hashlib.sha256(summary_bytes).hexdigest() == current['summary_sha256']
summary = json.loads(summary_bytes)
assert summary['outputs']['decisions']['sha256'] == EXPECTED_SHA
out = gzip.GzipFile(fileobj=sys.stdout.buffer, mode='wb', mtime=0, compresslevel=1)


def emit(r):
    out.write((json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n').encode())


emit({'_provenance': dict(current=current, resolved_export=str(EXPORT),
                         summary_dispositions=summary['dispositions'])})
h = hashlib.sha256()
count = 0
with EXPORT.open('rb') as stream:
    before = os.fstat(stream.fileno())
    for line in stream:
        h.update(line)
        r = json.loads(line)
        count += 1
        stages = [s['result'] for s in r.get('stages', []) if s['stage'] == 'segmentation']
        assert len(stages) <= 1
        s = stages[0] if stages else {}
        if s:
            assert s['tool_version'] == '0.5'
        e, frame = s.get('evidence', {}), s.get('frame', {})
        xh = e.get('xheight_px', e.get('xheight'))
        method = 'explicit_evidence' if xh is not None else None
        # Existing native curve evidence: x-height is base minus mean on MAIN.
        # Do not use ascender/descender height or infer it from the crop height.
        mains = [d for d in e.get('detected_rows', []) if d.get('side') == 'main']
        if xh is None and len(mains) == 1:
            curves = mains[0].get('curves', {})
            mean = dict(curves.get('mean', []))
            diffs = [y - mean[x] for x, y in curves.get('base', []) if x in mean and y > mean[x]]
            if diffs:
                xh, method = median(diffs), 'median_main_curve_base_minus_mean'
        emit(dict(row_id=r['binding']['id'], parent_id=r['binding']['parent_id'],
                  crop_sha256=r['binding']['crop_sha256'], raw_text_sha256=r.get('raw_text_sha256'),
                  width_px=frame.get('source_width'), height_px=frame.get('source_height'),
                  characters=e.get('characters'), xheight_px=xh, xheight_method=method,
                  verdict_05=s.get('verdict'), reason_05=s.get('reason'),
                  segmentation_version=s.get('tool_version'),
                  pipeline_disposition=r['disposition'], pipeline_reasons=r.get('reasons', [])))
    after = os.fstat(stream.fileno())
assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
assert json.loads((BASE / 'CURRENT.json').read_text()) == current
assert (BASE / 'decisions.jsonl').resolve() == EXPORT
assert count == 592466 and h.hexdigest() == EXPECTED_SHA
emit({'_receipt': dict(export_sha256=h.hexdigest(), rows=count, bytes=before.st_size,
                      mtime_ns=before.st_mtime_ns, stat_unchanged=True, current_unchanged=True)})
out.close()
