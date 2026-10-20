"""Finite-set metadata diagnostics only: no Pipeline, native tools, readers or census."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import unicodedata as ud

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
COMMON = ROOT.parent / 'greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/scripts/common.py'
INPUTS = ROOT / 'docs/harvest/seg_steps/s4/inputs.jsonl'
SAMPLES = ROOT / 'docs/harvest/collect_v3_admission/segeval1/cells/samples.jsonl'
TYPOLOGY = ROOT / 'docs/harvest/seg_steps/s4/typology_replay.jsonl'


def sets():
    groups = {name: [] for name in ('segeval1', 'calibration', 'cells', 'typology')}
    samples = {r['row_id']: r for r in map(json.loads, SAMPLES.read_text().splitlines())}
    for line in INPUTS.read_text().splitlines():
        item = json.loads(line)
        row = dict(item['row'])
        if item['cohort'] == 'cells':
            meta = samples[row['id']]
            assert row['raw_text'] == meta['text'] and row['crop_sha256'] == meta['crop_sha256']
            row.update(source=meta['source'], wave=meta['wave'])
        groups[item['cohort']].append(row)
    for line in TYPOLOGY.read_text().splitlines():
        item = json.loads(line)
        if not item['manifest']['control']:
            groups['typology'].append(dict(item['row'], source=item['manifest']['source'], wave=item['manifest']['wave']))
    assert [len(v) for v in groups.values()] == [150, 888, 250, 417]
    for rows in groups.values():
        for row in rows:
            row.setdefault('source', row['id'].split('--', 1)[0])
            row.setdefault('book_id', row['id'].rsplit('--s', 1)[0])
            row.setdefault('page_id', row['id'].rsplit('-l', 1)[0])
    return groups


def analyze():
    from greekocr.harvest import admission as adm
    from greekocr.harvest.line_pipeline import (inventory, expectations, content_gate_exclusion,
        numeric_text, content_role, crop_aspect, final_eligibility)
    output_type = runpy.run_path(str(COMMON))['output_type']
    codec = adm.load_codec()
    result = {}
    details = []
    for name, rows in sets().items():
        counts = Counter(); fields = Counter(); diagnostics = Counter(); examples = {}; admitted = Counter(); numeric_breakdown = Counter(); by_kind = Counter()
        for row in rows:
            text = row['raw_text']; inv = inventory(text, codec)
            if row.get('crop_bbox') is None:
                assert hashlib.sha256(Path(row['crop_path']).read_bytes()).hexdigest() == row['crop_sha256']
            assert numeric_text(text) == (output_type(text) == 'numeric'), (name, row['id'], text)
            fields['crop_bbox' if row.get('crop_bbox') is not None else 'bound crop header size' if crop_aspect(row) is not None else 'unresolved'] += 1
            expected = expectations(row, {})
            exclusion = content_gate_exclusion(text, inv, expected, codec, row, {})
            reason = exclusion[1][0]['reason'] if exclusion else 'gate_admitted'
            counts[reason] += 1
            aspect = crop_aspect(row)
            numeric = content_role(row, expected) == 'numerics_tables' or numeric_text(text)
            cell = aspect is not None and aspect <= 6
            issues = []
            if not exclusion and (cell or numeric):
                admitted['cells' if cell else 'numeric_noncell'] += 1
                issues = final_eligibility(row, text, inv, expected, codec, {})
                assert not any(i['reason'] in {'short_line','single_character_cell','cell_status_unresolved'} or (i['reason']=='numeric_shape' and 'alnum' in i) for i in issues)
                for key in ('nonletter_fraction', 'numeric_shape'):
                    if any(i['reason'] == key for i in issues):
                        diagnostics[key] += 1
                        by_kind[key + (':cell' if cell else ':numeric_noncell')] += 1
                        if key == 'numeric_shape':
                            normalized = ud.normalize('NFC', text)
                            too_few = inv['digits'] < 4
                            bad_shape = sum(ud.category(c) == 'Nd' or c in '.,·-/ ' for c in normalized) < .6 * len(normalized)
                            numeric_breakdown['digits_lt4'] += int(too_few)
                            numeric_breakdown['shape_lt60percent'] += int(bad_shape)
                            numeric_breakdown['both'] += int(too_few and bad_shape)
                        examples.setdefault(key, [])
                        if len(examples[key]) < 5:
                            examples[key].append(dict(id=row['id'],text=text,A=aspect,role=content_role(row,expected),letters=inv['letter_count'],digits=inv['digits'],cell=cell,numeric=numeric))
            details.append(dict(set=name,id=row['id'],text=text,A=aspect,reason=reason,final_diagnostic=[i for i in issues if i['reason'] in {'nonletter_fraction','numeric_shape'}]))
        result[name] = dict(rows=len(rows),counts=dict(counts),dimension_fields=dict(fields),gate_admitted_exempt=dict(admitted),still_excluded=dict(diagnostics),diagnostic_by_kind=dict(by_kind),numeric_shape_breakdown=dict(numeric_breakdown),examples=examples,parity=len(rows))
    (HERE/'part2-counts.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (HERE/'part2-row-decisions.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in details))
    (HERE/'part2-input-hashes.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (INPUTS,TYPOLOGY,SAMPLES,COMMON)},indent=2)+'\n')
    print(json.dumps({k:{x:v[x] for x in ('rows','counts','dimension_fields','still_excluded','parity')} for k,v in result.items()},indent=2))


if __name__ == '__main__':
    analyze()
