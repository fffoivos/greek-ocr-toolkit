"""Build unified per-row tables for the 150 blind check and the 888 calibration crops."""
import gzip, json, sys
from pathlib import Path
from common import nchars, output_type, reason_code
sys.path.insert(0, str(Path(__file__).resolve().parents[6]))
from greekocr.harvest.line_pipeline_native import character_count  # pure function, used as in replay_calibration.py

SEG = Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1')
SITE = Path('/Users/foivoskarounos-zamparloukos/Projects/ocr-review-sites-20261018')
OUT = Path(sys.argv[1])
census = {}
with gzip.open(sys.argv[2], 'rt') as f:
    next(f)
    for line in f:
        p = line.rstrip('\n').split('\t')
        census[p[0]] = p
rows = []
owners = {r['line_id']: r for r in map(json.loads, (SEG / 'scored/owner_rows.jsonl').read_text().splitlines())}
for r in map(json.loads, (SEG / 'gate2/replay_segeval1.jsonl').read_text().splitlines()):
    o = owners[r['line_id']]; fr = r['after']['frame']; t = o['google_text']; c = census.get(r['line_id'])
    rows.append(dict(population='150', line_id=r['line_id'], crop_path=str(SEG / o['crop']), text=t,
        width=fr['source_width'], height=fr['source_height'], chars=nchars(t), filter_chars=r['after']['evidence']['characters'],
        output_type=output_type(t), verdict_05=r['verdict_05'], reason_05=reason_code(r['verdict_05'], o['reason']) if r['verdict_05'] else None,
        verdict_08=r['verdict_08'], reason_08=r['after']['reason'],
        owner=r['owner_standard_state'], owner_faults=r.get('owner_faults'), sealed_decision=r.get('sealed_decision'),
        source=c[2] if c else r['line_id'].split('--')[0], primary_class=c[3] if c else None, in_census=bool(c)))
# 888: text lookup copied from deskew/replay_calibration.py
report = json.loads((SITE / 'review-data/box-length-experiment.json').read_text())['rows']
natives = {r['id']: r for r in json.loads(gzip.decompress((SITE / 'review-data/font-normalized/predicted-rows.json.gz').read_bytes()))}
population = json.loads((SITE / 'review-data/population.json').read_text())
cache = {}
texts = {}
for old in report:
    meta = natives[old['id']]
    if meta.get('google_text') is None or 'content_class' not in meta:
        chunk = old['index'] // population['detail_chunk_size']
        if chunk not in cache:
            cache[chunk] = json.loads(gzip.decompress((SITE / f'population-data/details/{chunk:05d}.json.gz').read_bytes()))
        detail = cache[chunk][old['index'] % population['detail_chunk_size']]
        assert detail[0] == old['id'] and detail[4] == old['image_sha256']
        codes = dict(part.split(':') for part in detail[8].split('|'))
        meta['google_text'] = detail[2]
        meta['content_class'] = population['codebooks']['classes'][int(codes['class'])]
    assert character_count(meta['google_text']) == old['characters']
    texts[old['id']] = (meta['google_text'], meta['content_class'], old)
for r in map(json.loads, (SEG / 'gate2/replay_calibration.jsonl').read_text().splitlines()):
    t, cls, old = texts[r['line_id']]; fr = r['after']['frame']; c = census.get(r['line_id'])
    rating = (r['owner_rating'] or {}).get('decision')
    reason_05 = None
    rows.append(dict(population='888', line_id=r['line_id'], crop_path=str(SITE / 'population-images' / (r['after']['binding']['crop_sha256'] + '.png')),
        text=t, width=fr['source_width'], height=fr['source_height'], chars=nchars(t), filter_chars=r['after']['evidence']['characters'],
        output_type=output_type(t), verdict_05=r['verdict_05'],
        reason_05=(c[11] if c and c[10] == r['verdict_05'] else None),
        verdict_08=r['verdict_08'], reason_08=r['after']['reason'], owner=rating,
        source=c[2] if c else r['line_id'].split('--')[0], primary_class=c[3] if c else cls, in_census=bool(c)))
with OUT.open('w') as o:
    for r in rows:
        assert Path(r['crop_path']).is_file(), r['crop_path']
        o.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(rows), 'rows;', sum(r['in_census'] for r in rows if r['population'] == '150'), '150 in census;',
      sum(r['in_census'] for r in rows if r['population'] == '888'), '888 in census')
