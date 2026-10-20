"""Local v4.1 wrapper: resolve pwd/template paths before the absolute-path test.

No rollout code is evaluated. Only the witnessed pwd expression and literal
base/store/load bindings are substituted. Image provenance uses ordinary v4:
exact match or an accepted downscale
(long side 2048, aspect within 1 px, RGB MAD < 2). All other v4 checks
are unchanged.
"""
import sys
sys.dont_write_bytecode = True
import argparse, json, re, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reference_adapter import rollout_scanner
from build import dump, sha, io_guard
RULE = 'resolve pwd/template paths before the absolute-path test; ordinary v4 image provenance (exact or v4 downscale)'
PWD = '${(await tools.exec_command({cmd:"pwd",max_output_tokens:100})).output.trim()}'


def inspect(rollout, directory, scanner_factory=None):
    io_guard()
    scanner = (scanner_factory or rollout_scanner)()
    directory = Path(directory).resolve()
    records = [json.loads(l) for l in Path(rollout).read_text().splitlines()]
    original = scanner.inspect(rollout, directory)
    resolved = []; evidence = []; failures = []; base = None
    for ordinal, obj in enumerate(records):
        p = obj.get('payload', {})
        if p.get('type') not in scanner.CALL_TYPES:
            continue
        raw = p.get('input', p.get('arguments'))
        if not isinstance(raw, str):
            continue
        updated = raw
        if PWD in raw:
            outputs = []
            for j in range(ordinal + 1, len(records)):
                q = records[j].get('payload', {})
                if q.get('type') in scanner.CALL_TYPES:
                    break
                item = q.get('item', {})
                if item.get('type') == 'CommandExecution' and item.get('command', [])[-1:] == ['pwd']:
                    outputs.append(dict(record=j, pwd=item['stdout'].strip(), exit_code=item.get('exit_code')))
            if not outputs or any(e['pwd'] != str(directory) or e['exit_code'] != 0 for e in outputs):
                failures.append(dict(record=ordinal, reason='pwd output absent or differs from reader_dir', outputs=outputs))
            else:
                updated = updated.replace(PWD, str(directory))
                evidence.append(dict(record=ordinal, expression=PWD, outputs=outputs, resolved_pwd=str(directory)))
        binding = re.search(r'const base=("[^"\n]*");', raw)
        if binding:
            base = json.loads(binding[1])
        if base is not None:
            updated = updated.replace('${base}', base).replace('${load("base")}', base)
        if updated != raw:
            resolved.append(dict(record=ordinal, original=raw, resolved=updated))
            p['input' if 'input' in p else 'arguments'] = updated
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl') as f:
        for obj in records: f.write(json.dumps(obj)+'\n')
        f.flush()
        result = scanner.inspect(f.name, directory)
    result.update(scanner_version='4.1', rule=RULE, rollout=str(rollout), rollout_sha256=sha(rollout),
                  v4_violations=original['violations'], template_resolutions=resolved, pwd_evidence=evidence)
    result['violations'].extend(failures)
    result['image_match_counts'] = {
        kind: sum(m['match'] == kind for m in result['image_matches'])
        for kind in sorted({m['match'] for m in result['image_matches']})}
    result['v41_path_witness_ok'] = not failures and not [
        v for v in result['violations'] if not v['reason'].startswith('image provenance:')]
    result['ok'] = not result['violations']
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rollout', type=Path); parser.add_argument('reader_dir', type=Path); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); result = inspect(args.rollout, args.reader_dir); dump(args.output, result)
    print(json.dumps(dict(ok=result['ok'], path_witness=result['v41_path_witness_ok'], returned_images=result['returned_images'], violations=result['violations']), indent=2))
    raise SystemExit(0 if result['ok'] else 2)
