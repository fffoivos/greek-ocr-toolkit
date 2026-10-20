"""Read-only finite-set final-eligibility comparison; no Pipeline or census runs."""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def analyze():
    from greekocr.harvest import admission as adm
    from greekocr.harvest import line_pipeline as new
    spec = importlib.util.spec_from_file_location('greekocr.harvest._part3_baseline', HERE / 'part3-baseline/greekocr/harvest/line_pipeline.py')
    old = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = old
    spec.loader.exec_module(old)
    inputs = runpy.run_path(str(HERE / 'part2_analysis.py'))
    codec = adm.load_codec()
    summaries = {}; decisions = []
    for name, rows in inputs['sets']().items():
        changed = Counter(); transitions = Counter(); remaining = Counter(); outcome_changes = 0
        for row in rows:
            # Empty heldout policy: a missing edition cannot match an exclusion.
            # This placeholder supplies the final checker contract, not provenance.
            row.setdefault("edition_id", None)
            text = row['raw_text']; inv = new.inventory(text, codec)
            if row.get('crop_bbox') is None:
                assert hashlib.sha256(Path(row['crop_path']).read_bytes()).hexdigest() == row['crop_sha256']
            expected = new.expectations(row, {})
            gate = new.content_gate_exclusion(text, inv, expected, codec, row, {})
            if gate:
                continue
            before = old.final_eligibility(row, text, inv, expected, codec, {})
            after = new.final_eligibility(row, text, inv, expected, codec, {})
            aspect = new.crop_aspect(row); cell = aspect is not None and aspect <= 6
            numeric = new.content_role(row, expected) == 'numerics_tables' or new.numeric_text(text)
            br = [r['reason'] for r in before]; ar = [r['reason'] for r in after]
            def outcome(issues):
                return 'HOLD' if any(i.get('unresolved') for i in issues) else 'DROP' if issues else 'ELIGIBLE'
            if cell:
                assert not set(ar) & {'short_line', 'numeric_shape', 'nonletter_fraction', 'single_character_cell', 'cell_status_unresolved'}
            else:
                assert before == after
            if before != after:
                assert cell
                removed = Counter(br) - Counter(ar)
                changed.update(removed)
                transitions[','.join(br) + ' -> ' + (','.join(ar) or 'none')] += 1
                outcome_changes += outcome(before) != outcome(after)
            if numeric and not cell:
                remaining.update(r for r in ar if r in {'numeric_shape', 'nonletter_fraction'})
            decisions.append(dict(set=name,id=row['id'],text=text,A=aspect,cell=cell,numeric=numeric,
                before=before,after=after,before_outcome=outcome(before),after_outcome=outcome(after)))
        summaries[name] = dict(rows=len(rows),gate_admitted=sum(d['set']==name for d in decisions),
            changed_reason_rows=sum(changed.values()),removed_reasons=dict(changed),reason_transitions=dict(transitions),
            final_outcomes_changed=outcome_changes,remaining_numeric_noncell_exclusions=dict(remaining))
    (HERE / 'part3-counts.json').write_text(json.dumps(summaries,ensure_ascii=False,indent=2)+'\n')
    (HERE / 'part3-row-decisions.jsonl').write_text(''.join(json.dumps(d,ensure_ascii=False)+'\n' for d in decisions))
    paths = [inputs[k] for k in ('INPUTS','SAMPLES','TYPOLOGY','COMMON')]
    (HERE / 'part3-input-hashes.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n')
    print(json.dumps(summaries,indent=2))


if __name__ == '__main__':
    analyze()
