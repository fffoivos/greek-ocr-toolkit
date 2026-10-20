"""Offline codec-only replay, bound to the emitted ADM5b per-row decisions."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import unicodedata as ud

from greekocr.harvest.admission import load_codec, normalize_label

ROOT = Path(__file__).resolve().parents[3]
TRAINING = Path.home() / 'Projects/greek-page-ocr'


def audit(prefix):
    receipt = json.loads(Path(str(prefix) + '_admission_receipt.json').read_text())
    inputs = json.loads(receipt['input_path']) if receipt['input_path'].startswith('[') else [receipt['input_path']]
    codecs = {v: load_codec(ROOT / f'greekocr/_vendor/codec/{v}.json') for v in ('v1', 'v2')}
    counts = {v: Counter() for v in codecs}
    fails = Counter()
    rows = 0
    source_hashes = []
    newly_supported = codecs['v2']['atoms'] - codecs['v1']['atoms']
    with Path(str(prefix) + '_admission.jsonl').open() as decisions:
        for path in inputs:
            raw = Path(path).read_bytes()
            source_hashes.append(dict(path=path, sha256=hashlib.sha256(raw).hexdigest()))
            for line in raw.splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                decision = json.loads(next(decisions))
                assert decision['row_id'] == str(row.get('row_id', row.get('id')))
                text = ud.normalize('NFD', normalize_label(row.get('docai_text', row.get('label'))))
                other_failure = bool(set(decision['rules_failed']) - {'foreign_char'})
                for version, codec in codecs.items():
                    outside = [c for c in text if c not in codec['atoms']]
                    counts[version].update(outside)
                    fails[version + '_codec_rows'] += bool(outside)
                    fails[version + '_all_rule_rows'] += bool(outside) or other_failure
                    if version == 'v2':
                        assert bool(outside) == ('foreign_char' in decision['rules_failed'])
                rows += 1
        assert next(decisions, None) is None
    top = lambda c: [dict(char=ch, codepoint=f'U+{ord(ch):04X}', name=ud.name(ch, 'UNNAMED'),
                          count=n, in_v2=ch in codecs['v2']['atoms']) for ch, n in c.most_common(20)]
    return dict(rows_total=rows, **fails, input_hashes=source_hashes,
                v1_foreign_occurrences=sum(counts['v1'].values()),
                v1_foreign_occurrences_supported_in_v2=sum(n for c, n in counts['v1'].items() if c in newly_supported),
                v1_top20=top(counts['v1']), v2_top20=top(counts['v2']))


def main():
    training = TRAINING / 'codec/v2.json'
    local = ROOT / 'greekocr/_vendor/codec/v2.json'
    release = TRAINING / 'out/e4/wave1b/v2-codec/release.json'
    release_value = json.loads(release.read_text())
    sha = hashlib.sha256(local.read_bytes()).hexdigest()
    assert sha == hashlib.sha256(training.read_bytes()).hexdigest() == release_value['assets']['codec_v2']['sha256']
    result = dict(codec_v2=dict(path=str(local.relative_to(ROOT)), version='v2', sha256=sha,
                               training_origin=str(training), frozen_release=str(release)),
                  codec_v1={k: v for k, v in load_codec(ROOT / 'greekocr/_vendor/codec/v1.json').items()
                            if k in ('path', 'version', 'sha256')})
    for name, prefix in [('w1_originals_v3', ROOT / 'docs/harvest/collect_v3_admission/w1_originals_v3'),
                         ('v2_census', ROOT / 'docs/harvest/collection/v2/ADMISSION_CENSUS_20261017')]:
        result[name] = audit(prefix)
    (Path(__file__).parent / 'ADM5b_CODEC_AUDIT.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    for name in ('w1_originals_v3', 'v2_census'):
        r = result[name]
        print(name, {k: v for k, v in r.items() if not isinstance(v, list)})
        print('v1 top20:', [(r['char'], r['count']) for r in r['v1_top20']])
        print('v2 top20:', [(r['char'], r['count']) for r in r['v2_top20']])


if __name__ == '__main__':
    main()
