"""Offline F2 tag projection after the sealed n1tr_finalize.sh --apply-lead.

Keep the sealed reading decisions intact; distinguish resolved nonraised slots
from unresolved HOLDs in the release. No images are opened or reads launched.
"""
import json
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from greekocr.ops.data_root import input_path as _data_input
from greekocr.labelfix.lqb import run, sha256

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'artifacts/n1/n1tr'
OUTPUT = ROOT / 'artifacts/n1/n1_v1_train.jsonl'


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    manifest_path = OUTPUT.with_name(OUTPUT.stem + '_manifest.json')
    manifest = json.loads(manifest_path.read_text())
    assert manifest['edits'] == 0
    assert sha256(OUTPUT) == manifest['output']['sha256']
    temporary = OUTPUT.with_suffix('.jsonl.tmp')
    counts = Counter()
    meanings = Counter()
    holds = Counter()
    with _data_input(OUTPUT).open() as source, temporary.open('w') as target:
        for line in source:
            row = json.loads(line)
            assert row['label'] == row['parent_label'] == row['new_label']
            assert not row['edits']
            tags = []
            unresolved = []
            for decision in row['slot_provenance']:
                decision.setdefault('pre_f2_decision', decision['decision'])
                decision.setdefault('pre_f2_reason', decision['reason'])
                lead = decision.get('lead')
                valid = [r for r in decision['reads']
                         if r['context_status'] == 'VALID' and r['read_status'] == 'ok']
                meaning = None
                basis = None
                if lead and lead['pixel_checked'] is True:
                    meaning, basis = lead['printed'], 'lead_pixel_ruling'
                elif (len(valid) == 2 and {r['reader'] for r in valid} == {'r1', 'r2'}
                      and valid[0]['meaning'] == valid[1]['meaning']):
                    meaning, basis = valid[0]['meaning'], 'two_valid_agreed_reads'
                if meaning in ('hyphen', 'en dash', 'em dash'):
                    decision.update(decision='tag', reason=basis, tags=[meaning])
                    tags.append(dict(slot_id=decision['slot_id'], tag=meaning))
                    meanings[meaning] += 1
                elif meaning == 'baseline dot':
                    decision.update(decision='unchanged', reason=basis, tags=[])
                    meanings[meaning] += 1
                else:
                    decision['tags'] = []
                    unresolved.append(decision)
                    holds[decision['reason']] += 1
            row.update(tags=tags, holds=unresolved)
            counts.update(rows=1, tags=len(tags), holds=len(unresolved),
                          slots=len(row['slot_provenance']))
            target.write(json.dumps(row, ensure_ascii=False) + '\n')
    assert counts == Counter(rows=214436, tags=85, holds=2623, slots=2923), counts
    assert meanings == Counter({'baseline dot': 215, 'hyphen': 55, 'em dash': 24, 'en dash': 6})
    temporary.replace(OUTPUT)
    digest = sha256(OUTPUT)
    OUTPUT.with_suffix('.sha256').write_text(digest + '  ' + OUTPUT.name + '\n')
    manifest['output']['sha256'] = digest
    manifest.update(tags=counts['tags'], holds=counts['holds'],
                    resolved_unchanged=215,
                    tag_types={k: v for k, v in meanings.items() if k != 'baseline dot'},
                    resolved_meanings=dict(meanings),
                    hold_reasons=dict(holds),
                    f2_projection=dict(path=str(Path(__file__).resolve()),
                                       sha256=sha256(__file__),
                                       policy='Lead rulings override reads; two VALID agreeing nonraised reads resolve; all other positions HOLD.'))
    registry_path = ROOT / 'docs/records/labelfix/lqb/versions.json'
    registry = json.loads(registry_path.read_text())
    registry['versions']['n1_v1_train']['sha256'] = digest
    score_path = ART / 'lqb_rescore.json'
    dump(score_path, run(ROOT / 'docs/records/labelfix/lqb/truth_v1_1.jsonl', registry,
                         ['collection_v2_train', 'n1_v1_train']))
    manifest['lqb'] = dict(path=str(score_path), sha256=sha256(score_path))
    dump(registry_path, registry)
    dump(manifest_path, manifest)
    dump(ART / 'FINALIZED_RECEIPT.json', manifest)
    print(json.dumps(dict(counts, sha256=digest, meanings=dict(meanings),
                          hold_reasons=dict(holds)), indent=2))


if __name__ == '__main__':
    main()
