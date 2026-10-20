"""RU3T1 offline, one-time evidence-preserving rebind and resume preparation."""
import hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'scripts/secondary'),str(ROOT)]
import ru3t as m
import ru3t_driver as driver
sha=m.sha
def dump(path,obj):m.dump(path,obj)
tests=json.loads((OUT/'tests.json').read_text());assert all(x['ok'] for x in tests.values())
proof=json.loads((OUT/'coverage_proof.json').read_text());assert len(proof)==14 and all(x['identical'] for x in proof.values())
if (OUT/'archived_preflight_failures.json').exists():
    before=json.loads((OUT/'build.before.json').read_text());pack=Path(before['pack'])
    archive=json.loads((OUT/'archived_preflight_failures.json').read_text());moves=archive['files'];failed=archive['contexts']
    info=json.loads((m.ART/'build.json').read_text());changes=[]
    for p,h in before['inputs'].items():
        if info['inputs'][p]!=h:changes.append(dict(path=p,old_sha256=h,new_sha256=info['inputs'][p]))
    assert {x['path'] for x in changes}=={str(m.HERE/'ru2t_coverage.py'),str(m.HERE/'ru3t_driver.py')}
    state=json.loads((OUT/'reading_state.before.json').read_text())
else:
    before=json.loads((OUT/'build.before.json').read_text());assert (m.ART/'build.json').read_bytes()==(OUT/'build.before.json').read_bytes()
    pack=Path(before['pack']);changes=[]
    for p,h in {**before['inputs'],**before['pack_inputs']}.items():
        actual=sha(p)
        if actual!=h:
            assert p in [str(m.HERE/'ru2t_coverage.py'),str(m.HERE/'ru3t_driver.py')],p
            changes.append(dict(path=p,old_sha256=h,new_sha256=actual))
    assert len(changes)==2
    state=json.loads((OUT/'reading_state.before.json').read_text());assert all(sha(p)==h for p,h in state.items())
    # Validate ALL candidates before moving any file. Actual or uncertain reads stay claimed.
    moves=[];failed=[]
    for ctx,r in driver.plan(before):
        stem=m.reader_stem(ctx,r);ans=m.ART/'answers'/stem
        if Path(str(ans)+'.run.json').exists():
            assert ctx+'/'+r in proof
            assert (pack/ctx/r/'answers.jsonl').is_file()
            continue
        attempt=Path(str(ans)+'.attempt.json');log=Path(str(ans)+'.driver.log')
        row=json.loads(attempt.read_text());text=log.read_text()
        assert row['context']==ctx+'/'+r and row['rc']==1 and row['status']=='FAILED'
        assert row['result_line']=='ValueError: bound pack changed'
        assert "if sha(path)!=digest:raise ValueError('bound pack changed')" in text
        assert text.rstrip().endswith('ValueError: bound pack changed')
        assert not (pack/ctx/r/'answers.jsonl').exists()
        for suffix in ['.run.json','.launcher.log','.rollout.jsonl']:
            assert not Path(str(ans)+suffix).exists()
        own=[p for p in ans.parent.glob(stem+'.*') if not any(p.name.startswith(stem+'.'+other+'.') for other in ('r2','r3'))]
        assert set(own)=={attempt,log},own
        failed.append(ctx+'/'+r)
        for p in (attempt,log):
            dest=OUT/'preflight_failures'/p.name
            assert not dest.exists()
            moves.append(dict(source=str(p),archive=str(dest),sha256=sha(p)))
    assert len(failed)==24
    (OUT/'preflight_failures').mkdir()
    for row in moves:Path(row['source']).rename(row['archive']);assert sha(row['archive'])==row['sha256']
    dump(OUT/'archived_preflight_failures.json',dict(contexts=failed,files=moves,reason='Exact launcher binding rejection before account probe or reading; no run, launcher log or answers. Original context_results retained.'))
    info=json.loads((m.ART/'build.json').read_text())
    for row in changes:info['inputs'][row['path']]=row['new_sha256']
    dump(m.ART/'build.json',info)
validated=m.validate();assert len(driver.plan(validated))==38
cmd=['bash',str(m.HERE/'reading/run_ru3t_all.sh'),'--dry-run']
result=subprocess.run(cmd,capture_output=True,text=True)
(OUT/'driver_dry_run.jsonl').write_text(result.stdout)
(OUT/'driver_dry_run.stderr').write_text(result.stderr)
assert result.returncode==0,result.stderr
pending=[json.loads(line) for line in result.stdout.splitlines()]
identities=[x['context']+'/'+x['reader'] for x in pending]
assert identities==failed
assert all(x['dry_run'] and x['closure']=='ok' and not x['network'] for x in pending)
assert set(driver.done_contexts(m.ART,pack,info))==set(proof)
archived={str(Path(x['source']).resolve()):x for x in moves}
assert all(sha(archived[str(Path(p).resolve())]['archive'] if str(Path(p).resolve()) in archived else p)==h for p,h in state.items())
scans={identity:json.loads((OUT/(m.reader_stem(*identity.split('/'))+'.scan.json')).read_text()) for identity in proof}
receipt=dict(schema='RU3T1-v1',status='READY_TO_RESUME',created_at=datetime.now(timezone.utc).isoformat(),change='behaviour-preserving',
    investigation=dict(working_tree_diff_against_HEAD='empty; current coverage file equals HEAD',commit='69c068b18881a2e2da4a7e527ef946cc25f691c7',commit_time='2026-10-17T23:44:21+03:00',file_mtime='2026-10-17T23:39:01+03:00',timing_note='mtime is filesystem evidence, not a proven exact edit time; file was first added to Git by N1-TR commit, so parent commit has no copy',n1tr_receipt='artifacts/n1/N1TR_RECEIPT.json',n1tr_brief='docs/briefs/N1T2_train_read.md',n1tr_coverage_sha256='84b4b6f90d716910f5c400049d3d3a777aec129e5a5b8651f9a206a66eae8c5b',difference='coverage adds image_fields=(crop,) default, generalizes origins/assigned/dropped_items; singleton crop default is identical for existing callers; N1-TR explicitly passes line and zoom',bound_source_recovery='Reverse only the four image_fields edits; recovered bytes match original binding SHA-256 exactly'),
    rebindings=changes,old_build_sha256=sha(OUT/'build.before.json'),new_build_sha256=sha(m.ART/'build.json'),
    proof=dict(tests=tests,contexts=proof,all_coverage_objects_identical=True,comparison='full dictionary equality including witnesses, replay log, direct/derived/unviewed/dropped lists; sorted JSON bytes also equal',basis='same canonical v4.4 scan and same saved rollout/items for both functions; no production finalize',totals={key:sum(v[key] for v in proof.values()) for key in ['assigned_crops','direct','derived','unviewed']}),
    contexts_done=14,contexts_total=38,remaining=24,done_contexts=list(proof),remaining_contexts=identities,
    resume=dict(archived_preflight_failures=failed,archive_manifest=str((OUT/'archived_preflight_failures.json').relative_to(ROOT)),original_context_results_preserved=True,reading_evidence_preserved_by_hash=True,policy='Dry-run and live driver omit existing reading claims; only these 24 independently verified never-started failures were archived. Revalidate binding before each pending context, before probing.',closure='38/38 ok'),
    dry_run=dict(ok=True,command=cmd,exit_code=result.returncode,contexts=len(pending),output=str((OUT/'driver_dry_run.jsonl').relative_to(ROOT)),probes=0,readings=0),
    existing_scan_findings=dict(unclean_contexts=[k for k,v in scans.items() if not v['ok']],note='Done counts completed reader executions, not admitted votes. Canonical scan failures remain unchanged and fail closed at finalization; no scanner/gate changes or reruns authorized.'),
    production_readings_run=0,account_probes_run=0,production_finalization_run=False,network=False,browser=False,computer_use=False,git_writes=False)
# Confirm serialized before/after byte identity too.
for identity in proof:
    stem=m.reader_stem(*identity.split('/'))
    assert (OUT/(stem+'.before.json')).read_bytes()==(OUT/(stem+'.after.json')).read_bytes()
receipt['artifacts']={str(p.relative_to(ROOT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}
receipt['changed_source_files']={str(p.relative_to(ROOT)):sha(p) for p in [m.HERE/'ru3t_driver.py',ROOT/'tests/test_ru3t.py']}
dump(m.ART/'RU3T1_RECEIPT.json',receipt)
print(json.dumps(dict(done=14,remaining=24,dry_run='ok',unclean_contexts=receipt['existing_scan_findings']['unclean_contexts'])))
