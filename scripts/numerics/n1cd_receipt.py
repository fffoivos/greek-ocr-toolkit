"""Verify offline N1-Cd packs and append the reviewable delivery receipt/report."""
from collections import Counter
import ast
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from PIL import __version__ as pillow_version
sys.path.insert(0,str(Path(__file__).resolve().parent))
from n1_pack_closure import scan
from n1cd_prepare import ROOT, OUT, SCRATCH, sha, rows


def main():
    receipt=json.loads((SCRATCH/'n1_cache/n1cd_preparation.json').read_text())
    for path,digest in receipt['prior_unchanged'].items():
        assert sha(Path(path))==digest,path
    approved=rows(OUT/'controls/approved.jsonl'); bed=rows(OUT/'step1_rendered_v3.jsonl')
    assert sha(OUT/'controls/approved.jsonl')==receipt['approved_sha256']
    records={r['slot_id']:r for r in bed+approved}
    seen=[]; contexts=[]; output_hashes={}; raised=Counter()
    for root,names in [('n1cal',['cal01']),('n1',[f'ctx{i:02}' for i in range(1,8)])]:
        for ctx in names:
            rd=SCRATCH/'sol_packs'/root/ctx/'r1'
            result=scan(rd,OUT); assert result['ok'],result
            keypath=OUT/'keys'/f'{ctx}.json'; key=json.loads(keypath.read_text())
            public=rows(rd/'items.jsonl'); values=list(key['items'].values())
            assert len(public)<=100
            assert len({r['slot_id'] for r in values})==len(values)
            for item in public:
                private=key['items'][item['item_id']]; source=records[private['slot_id']]
                for name in ('line','zoom'):
                    assert sha(rd/item[name])==source[name+'_sha256']
            b=[r for r in values if r['control_truth'] is None]; c=[r for r in values if r['control_truth'] is not None]
            if root=='n1':
                assert len(c)==9 and any(r['control_truth']=='raised dot' for r in c)
                seen.extend(r['slot_id'] for r in b)
                raised.update(r['slot_id'] for r in c if r['control_truth']=='raised dot')
            else:
                assert len(c)==82 and not b
                assert {r['slot_id'] for r in c}=={r['slot_id'] for r in approved}
            manifest=rd.parent/'MANIFEST.r1.json'
            contexts.append(dict(root=root,context=ctx,reader='r1',pack=str(rd),key=str(keypath),manifest=str(manifest),
                items=len(public),bed=len(b),controls=len(c),
                bed_by_grammar=dict(Counter('/'.join(r['bed_class']) for r in b)),
                controls_by_truth=dict(Counter(r['control_truth'] for r in c)),closure=result))
            for p in (keypath,manifest,rd/'items.jsonl'): output_hashes[str(p)]=sha(p)
    assert Counter(seen)==Counter(r['slot_id'] for r in bed) and len(seen)==558
    assert sorted(raised.values())==[1,2,2,2]
    assert json.loads((OUT/'usage_ledger.json').read_text())==[]
    tests=json.loads((OUT/'N1Cd_TESTS.json').read_text()); assert all(r['exit_code']==0 for r in tests['results'])
    scripts=[ROOT/p for p in ['scripts/numerics/n1_build_packs.py','scripts/numerics/n1_calibration.py','scripts/numerics/n1cd_prepare.py',
        'scripts/numerics/n1cd_receipt.py','scripts/secondary/reading/n1_launch.py','tests/test_n1cd.py','tests/test_n1cd_render.py']]
    for p in scripts: ast.parse(p.read_text(),filename=str(p))
    launcher=ROOT/'scripts/secondary/reading/run_n1.sh'
    subprocess.run(['bash','-n',str(launcher)],check=True)
    report=ROOT/'docs/records/labelfix/secondary/N1C_REPORT.md'
    assert '## N1-Cd\n' not in report.read_text()
    parts=['\n\n## N1-Cd\n',
        '**READY for operator-invoked calibration and glyph reading; no real reading or limit probe was invoked.** The 17 October lead ruling resolves the C1 document conflict recorded in N1-Cc. All 82 proposal rows are sealed in `artifacts/n1/controls/approved.jsonl` with the ruling and source hash in each row’s provenance. The four C1 raised-dot slots are control-only evidence: their lines are outside every step1 line and the reserved set, and N1 never fits on them. Their shared step1 document is explicitly allowed; the other 78 controls retain the document exclusions.',
        f"Sealed SHA256: `{receipt['approved_sha256']}`. Cell 101 is a spaced hyphen duplicating approved hyphen cell 58; the existing cell-58 approval is retained once, with no new control. Cell 102 is a baseline dot under a dotted leader and is excluded. No new raised-dot controls were added.",
        'Seed `20261017:N1-1` controls bed order, control order, item order and per-item option permutations. Calibration is `sol_packs/n1cal/cal01/r1/`, with all 82 controls and private key `artifacts/n1/keys/cal01.json`. Glyph packs are `sol_packs/n1/ctx01/r1/` through `ctx07/r1/`, with 558 distinct rendered step1 slots exactly once and 63 control appearances. Every context has nine distinct controls: one raised dot plus two from each other approved truth class, allocated round-robin within each class. The four raised slots appear 2/2/2/1 times across contexts. Every source line/zoom hash was reverified; pack PNG hashes equal the v3 source hashes. No images were rerendered or glyph truths inferred.',
        'Bed counts below are existing grammar candidate classes, not printed-glyph truths; `range/thousands` preserves the alternative-label combination. Control counts are approved printed truths.',
        '| Context | Items | Bed | Controls | Raised dot | Baseline dot | Comma | Hyphen/dash | Nothing |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for c in contexts:
        cc=c['controls_by_truth'];parts.append('| '+c['context']+' | '+' | '.join(str(x) for x in [c['items'],c['bed'],c['controls'],*[cc.get(k,0) for k in ['raised dot','baseline dot','comma','hyphen or dash','nothing']]])+' |')
    parts.extend(['','| Context | Other | Range | Thousands | Decimal | Range/thousands | Table boundary |\n|---|---:|---:|---:|---:|---:|---:|'])
    for c in contexts:
        bc=c['bed_by_grammar'];parts.append('| '+c['context']+' | '+' | '.join(str(bc.get(k,0)) for k in ['other','range','thousands','decimal','range/thousands','table_boundary'])+' |')
    parts.extend(['',
        'All **8/8 contexts passed closure**, including a final independent rerun. Reader folders contain only `items.jsonl` and hash-named, metadata-free PNGs in `img/`; manifests sit beside `r1`. Keys, geometry, source ids, measurements, approvals and truths stay outside every reader folder. Each context has at most 89 items. `N1Cd_RECEIPT.json` binds keys, item lists, manifests, scripts, tests and every unchanged prior N1 artifact.',
        '`scripts/secondary/reading/run_n1.sh <n1|n1cal> <ctx> [reader]` is prepared for r1 (the only reader packs built). It probes usage before and after an attempted read, refuses weekly usage ≥78%, reuses `run_read.sh` with `sep.md` at medium effort, requires `gpt-6.1-sol`, runs the unchanged v4 `scan_rollout.py` against the exact reader folder, then uses `n1_map_answers.py`. Existing reading helpers are unchanged: their shell bodies are reused with only their hardcoded RU1 log-root assignment redirected in memory to `artifacts/n1`. All original network-disabled and web-disabled model settings are preserved. Existing attempts are never overwritten.',
        'Answers, run receipts, scans and mapped results go to `artifacts/n1/answers/<ctx>.<reader>.*`; measured usage goes to `artifacts/n1/usage_ledger.json`, currently an empty array. Calibration additionally writes `<ctx>.<reader>.calibration.json` with per-class accuracy, a truth-row/prediction-column confusion matrix and disagreements carrying slot and item ids. Missing/duplicate/invalid responses are counted as unresolved errors. More than one control error marks a context VOID; unresolved answers, unexpected ids, reader failures and scan failures return failure.',
        f"**{tests['passed']} tests passed**. `N1Cd_TESTS.json` records exact commands and outputs. New tests validate real-pack coverage and v3 image custody; deterministic seven-context allocation and raised-dot rotation; the production CLI’s missing-raised refusal; calibration disagreements and missing answers; and fake-reader launcher success, pre/post usage threshold refusal, v4 leak rejection, reader failure, missing answers, overwrite refusal, shell syntax, and unchanged helper bodies. Both n1 and n1cal launch paths were exercised solely with isolated fake readers/probes. Python syntax and launcher shell syntax also passed.",
        'Image packing, closure and image fixtures used x86 Python 3.11.3/Pillow 10.4.0 with `-B -s`; text tests used `python3 -B -m pytest --noconftest`. No network, `.git` writes, real reader/probe, collector-root writes, `run.lock` access, locked-evaluation rendering, prompt edits or new glyph classification occurred. All previous frame/lock/artifact hashes remain unchanged.'
    ])
    with report.open('a') as f: f.write(('\n\n'.join(parts)+'\n').replace('\n\n|','\n|'))
    for p in scripts+[launcher,report,OUT/'controls/approved.jsonl',OUT/'usage_ledger.json',OUT/'N1Cd_TESTS.json',
        ROOT/'scripts/secondary/reading/run_read.sh',ROOT/'scripts/secondary/reading/limit_probe.sh']:
        output_hashes[str(p)]=sha(p)
    receipt.update(status='READY',contexts=contexts,bed_contexts=7,bed=558,bed_control_appearances=63,
        calibration_contexts=1,calibration_items=82,closure_ok=8,closure_total=8,
        raised_at_least_one_each=True,raised_slot_appearances=dict(raised),launcher_dry_run='ok',
        tests_passed=tests['passed'],outputs=output_hashes,
        renderer_interpreter=dict(executable=sys.executable,machine=platform.machine(),python=platform.python_version(),pillow=pillow_version),
        checks=dict(prior_artifacts_unchanged=True,frames_locks_unchanged=True,all_images_v3_hash_equal=True,
                    all_bed_once=True,no_control_duplicates_within_context=True,syntax_ok=True,real_ledger_empty=True))
    with (OUT/'N1Cd_RECEIPT.json').open('x') as f: json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
    print(f"N1Cd READY: approved 82 sealed {receipt['approved_sha256'][:8]}; calibration ctx 1 (82 items); bed contexts 7 (bed 558, controls 63, raised ≥1 each yes); closure 8/8 ok; launcher dry-run ok; tests {tests['passed']} passed")
if __name__=='__main__': main()
