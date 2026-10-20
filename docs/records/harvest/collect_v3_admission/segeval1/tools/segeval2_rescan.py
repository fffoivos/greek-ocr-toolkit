"""Offline SEGEVAL-2 custody audit. No reader launch or network access."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

D = Path(__file__).resolve().parents[1]
CANONICAL = Path.home() / 'Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading'
SCANNER = CANONICAL / 'tools/scan_rollout.py'
EXPECTED = 'e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load(path):
    return json.loads(Path(path).read_text())

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def main():
    assert sha(SCANNER) == EXPECTED
    assert 'Canonical v4.5.5 file sha256 = ' + EXPECTED in (CANONICAL / 'HANDOVER.md').read_text()
    closure = load(D / 'pack_closure.json')
    comparisons = {}
    for bed in ('segeval1_a', 'segeval1_b'):
        original = D / 'scan' / bed
        previous = load(original / 'r1.custody.json')
        old_scan = load(original / 'r1.scan.json')
        answer = D / 'answers' / bed / 'r1.jsonl'
        assert sha(answer) == previous['answers_sha256']
        assert sha(previous['rollout']) == previous['rollout_sha256']
        assert sha(original / 'r1.scan.json') == previous['scan_sha256']
        reader = Path(closure['pack_root']) / bed / 'r1'
        manifest = reader.parent / 'MANIFEST.r1.json'
        assert load(manifest) == closure['manifests'][bed]
        assert sha(reader / 'answers.jsonl') == sha(answer)
        out = D / 'scan/v4.5.5' / bed
        out.mkdir(parents=True, exist_ok=True)
        command = [sys.executable, '-B', str(SCANNER), previous['rollout'], str(reader)]
        with (out / 'r1.scan.json').open('w') as stream:
            result = subprocess.run(command, stdout=stream, stderr=subprocess.PIPE, text=True)
        assert result.returncode in (0, 2), result.stderr
        scan = load(out / 'r1.scan.json')
        assert scan['scanner_version'] == '4.5.5'
        assert scan['rollout_sha256'] == previous['rollout_sha256']
        verdict = 'VALID' if scan['ok'] and not scan['manifest_check_skipped'] else 'VOID'
        old = dict(version=old_scan['scanner_version'], verdict='VALID' if old_scan['ok'] and not old_scan['manifest_check_skipped'] else 'VOID',
                   violations=old_scan['violations'], scan_sha256=previous['scan_sha256'],
                   scanner_sha256=previous['scanner_sha256'], scan_path=str(original / 'r1.scan.json'))
        custody = dict(previous, scan_sha256=sha(out / 'r1.scan.json'), scanner_sha256=EXPECTED,
                       scanner=str(SCANNER), scanner_version='4.5.5', verdict=verdict,
                       reader_dir=str(reader), manifest_sha256=sha(manifest), command=command,
                       timestamp_utc=datetime.now(timezone.utc).isoformat(), previous_scans=[old],
                       scanner_dependencies={name: sha(SCANNER.parent / name) for name in ('common.py', 'replay_literal.py')},
                       handover_sha256=sha(CANONICAL / 'HANDOVER.md'), pack_closure_sha256=sha(D / 'pack_closure.json'))
        write(out / 'r1.custody.json', custody)
        comparisons[bed] = dict(previous_scans=[old], canonical=dict(version='4.5.5', verdict=verdict,
            violations=scan['violations'], scan_sha256=custody['scan_sha256'], scanner_sha256=EXPECTED,
            custody_sha256=sha(out / 'r1.custody.json'), scan_path=str(out / 'r1.scan.json')),
            intermediate_versions='No intermediate v4.5.x SEGEVAL-1 receipts supplied; no verdict inferred.')
        print(bed, verdict, json.dumps(scan['violations']))
    write(D / 'scan/verdicts.json', comparisons)

if __name__ == '__main__':
    main()
