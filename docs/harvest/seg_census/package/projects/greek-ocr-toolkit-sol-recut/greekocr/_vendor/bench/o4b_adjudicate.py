"""Blind offline rereading. silver_agreed requires E1 AND an independent teacher.

Teacher is a local module:factory(model_path) returning a crop reader. It receives
no proposed text. Its pinned model SHA and supported scripts must be supplied.
Kalchas typically supports Greek only; absence/ineligible script stays flagged.
"""
from __future__ import annotations
import argparse
import importlib
import json
from collections import Counter
from pathlib import Path
from greekocr._vendor.bench.common import read_rows, write_rows, write_json, sha256
from greekocr._vendor.bench.o4b_common import nfc, fresh


def adjudicate(rows, e1, teacher=None, supported=('greek_poly', 'greek_mono'), teacher_binding=None):
    for original in rows:
        row = dict(original); readings = {}; errors = []
        # Reread EVERY crop, even geometric rejects. Never catch a failure as agreement.
        try: readings['e1'] = nfc(e1(Path(row['crop_path'])))
        except Exception as error: errors.append('e1:'+str(error))
        if teacher is not None and row.get('script_class') in supported:
            try: readings['kalchas'] = nfc(teacher(Path(row['crop_path'])))
            except Exception as error: errors.append('kalchas:'+str(error))
        else:
            errors.append('independent_teacher_unavailable_for_script')
        expected = nfc(row['text'])
        agreed = (not errors and bool(expected) and readings.get('e1') == expected and
                  readings.get('kalchas') == expected)
        row.update(label_tier='silver_agreed' if agreed else 'flagged',
                   admitted=agreed and row.get('admitted', False),
                   adjudication=dict(readings=readings, errors=errors, comparison='NFC + whitespace collapse',
                                     teacher=teacher_binding, exact_agreement=agreed),
                   label_status='machine_agreement' if agreed else 'flagged')
        yield row


def run(records, out, e1, teacher=None, supported=('greek_poly', 'greek_mono'), teacher_binding=None, binding=None):
    fresh(out); out = Path(out)
    results = list(adjudicate(read_rows(records), e1, teacher, supported, teacher_binding))
    write_rows(out/'all.jsonl', results)
    write_rows(out/'records.jsonl', [r for r in results if r['admitted']])
    write_rows(out/'flagged.jsonl', [r for r in results if not r['admitted']])
    receipt = dict(records_sha256=sha256(records), e1=binding, teacher=teacher_binding,
                   tiers=dict(Counter(r['label_tier'] for r in results)),
                   admitted=sum(r['admitted'] for r in results), total=len(results), training=False)
    write_json(out/'report.json', receipt)
    return receipt


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--records', type=Path, required=True); p.add_argument('--out', type=Path, required=True)
    p.add_argument('--e1', type=Path, required=True); p.add_argument('--codec', type=Path, default=Path('codec/v1.json'))
    p.add_argument('--device', default='cpu'); p.add_argument('--kalchas', help='local module:factory(model_path) -> reader(crop_path); no network')
    p.add_argument('--kalchas-model', type=Path, help='model bytes for the attribution/custody receipt')
    p.add_argument('--kalchas-scripts', nargs='+', default=['greek_poly', 'greek_mono'])
    a = p.parse_args(argv)
    if bool(a.kalchas) != bool(a.kalchas_model): p.error('--kalchas and --kalchas-model are required together')
    from greekocr._vendor.bench.o4b_models import E1
    e1 = E1(a.e1, a.codec, a.device)
    teacher = None; binding = None
    if a.kalchas:
        module, function = a.kalchas.rsplit(':', 1); mod = importlib.import_module(module)
        teacher = getattr(mod, function)(a.kalchas_model)
        binding = dict(adapter=a.kalchas, adapter_sha256=sha256(mod.__file__), model_sha256=sha256(a.kalchas_model),
                       supported_scripts=a.kalchas_scripts, native_adapter_binding=getattr(teacher, 'binding', None))
    print(json.dumps(run(a.records, a.out, e1.read, teacher, a.kalchas_scripts, binding, e1.binding), indent=2))


if __name__ == '__main__': main()
