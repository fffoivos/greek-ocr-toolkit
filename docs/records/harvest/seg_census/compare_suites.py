"""Compare completed pytest JUnit receipts by test ID; no failure reclassification."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def read(path):
    root = ET.parse(path).getroot()
    states = {}
    for case in root.iter('testcase'):
        key = case.attrib.get('classname', '') + '::' + case.attrib['name']
        state = 'passed'
        for kind in ('failure', 'error', 'skipped'):
            if case.find(kind) is not None:
                state = kind
                break
        states[key] = state
    return states


def compare(directory):
    current = read(directory / 'full_current.xml')
    baseline = read(directory / 'full_baseline.xml')
    bad = {'failure', 'error'}
    failures = {k for k, v in current.items() if v in bad}
    baseline_failures = {k for k, v in baseline.items() if v in bad}
    result = dict(
        current_counts={v: list(current.values()).count(v) for v in sorted(set(current.values()))},
        baseline_counts={v: list(baseline.values()).count(v) for v in sorted(set(baseline.values()))},
        identical_failure_ids=sorted(failures & baseline_failures),
        regressions=sorted(k for k in failures if baseline.get(k) == 'passed'),
        unresolved=sorted(k for k in failures if baseline.get(k) not in bad | {'passed'}),
        baseline_only_failures=sorted(baseline_failures - failures),
        deselected_files=['tests/test_seg_cp7c.py'])
    result['gate'] = 'PASS' if not result['regressions'] and not result['unresolved'] else 'STOP'
    (directory / 'suite_comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    result = compare(Path(__file__).resolve().parent)
    print(json.dumps(result, indent=2))
    raise SystemExit(result['gate'] != 'PASS')
