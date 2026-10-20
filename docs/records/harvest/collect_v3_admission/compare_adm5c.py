"""Offline, read-only population comparison; writes only ADM5c report artifacts."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def main():
    baseline = json.loads((OUT / 'ADM5b_BASELINE.json').read_text())
    report = {}
    lines = ['# ADM5c admission comparison', '',
             'ADM5b counts were captured from the existing ADM5b decisions and receipts before rerunning. '
             'Input hashes and group sizes are checked against the new outputs. Counts are passing rows.', '']
    for population, prefix in [('w1', OUT / 'w1_originals_v3'),
                                ('v2', ROOT / 'docs/harvest/collection/v2/ADMISSION_CENSUS_20261017')]:
        receipt = json.loads(Path(str(prefix) + '_admission_receipt.json').read_text())
        old = baseline[population]
        assert old['receipt']['tool_version'] == 'ADM5b-20261017.1'
        assert old['receipt']['input_sha256'] == receipt['input_sha256']
        groups = defaultdict(lambda: dict(rows=0, passed=0))
        for line in Path(str(prefix) + '_admission.jsonl').open():
            row = json.loads(line)
            group = groups[row['source'] + '|' + row['class']]
            group['rows'] += 1
            group['passed'] += row['pass']
        assert groups.keys() == old['groups'].keys()
        comparisons = {}
        for key, group in sorted(groups.items()):
            before = old['groups'][key]
            assert before['rows'] == group['rows']
            comparisons[key] = dict(rows=group['rows'], adm5b_pass=before['passed'],
                                    adm5c_pass=group['passed'], delta=group['passed']-before['passed'])
        report[population] = dict(rows=receipt['rows_total'], adm5b_pass=old['receipt']['rows_pass'],
                                 adm5c_pass=receipt['rows_pass'], groups=comparisons,
                                 input_sha256=receipt['input_sha256'], tool_version=receipt['tool_version'],
                                 tool_sha256=receipt['tool_sha256'],
                                 expected_table_sha256=receipt['expected_table_sha256'],
                                 serbian_extension_atoms=receipt['serbian_extension_atoms'],
                                 serbian_extension_sha256=receipt['serbian_extension_sha256'])
        lines += [f'## {population}', '',
                  f"Total: {old['receipt']['rows_pass']:,} → {receipt['rows_pass']:,} / {receipt['rows_total']:,} passing.", '',
                  '| Source | Class | Rows | ADM5b pass | ADM5c pass | Delta |',
                  '|---|---|---:|---:|---:|---:|']
        for key, c in comparisons.items():
            source, cls = key.split('|')
            lines.append(f"| {source} | {cls} | {c['rows']} | {c['adm5b_pass']} | {c['adm5c_pass']} | {c['delta']:+d} |")
        lines.append('')
    (OUT / 'ADM5c_COMPARISON.json').write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    (OUT / 'ADM5c_COMPARISON.md').write_text('\n'.join(lines))
    for population, r in report.items():
        print(population, r['adm5b_pass'], '->', r['adm5c_pass'], '/', r['rows'])
        for key, group in r['groups'].items():
            if population == 'w1' and ('serbia' in key or 'numerics' in key or 'headings' in key):
                print(key, group)


if __name__ == '__main__':
    main()
