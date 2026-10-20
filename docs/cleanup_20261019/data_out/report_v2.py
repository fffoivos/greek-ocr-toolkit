"""Fresh live-reference scan and coordinator-facing CLEAN3B reports."""
import ast,collections,csv,hashlib,json,os,subprocess
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[2]
csv.field_size_limit(100_000_000)
rows=list(csv.DictReader((O/'MOVE_PLAN_v2.tsv').open(),delimiter='\t'))
move={r['path']:r for r in rows if r['decision']=='MOVE'}
names=collections.defaultdict(set)
for p in move:names[Path(p).name].add(p)
pattern=O/'basename_patterns_v2.txt';pattern.write_text('\n'.join(sorted(names,key=lambda s:(-len(s),s)))+'\n')
command=['rg','--only-matching','--with-filename','--null','--no-line-number','--no-heading','--no-ignore','--hidden','--fixed-strings','--file',str(pattern),'--glob','!**/__pycache__/**','--glob','!**/.git/**','--glob','!**/target/**','--glob','!**/node_modules/**','--glob','!**/.venv/**','--glob','!**/.pytest_cache/**',*['greekocr','scripts','tests','worker','prototypes']]
proc=subprocess.Popen(command,cwd=R,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
refs=collections.defaultdict(set);cache={};lengths=sorted({len(n) for n in names});matches=0
for line in proc.stdout:
    if b'\0' not in line:continue
    filename,match=line.rstrip(b'\n').split(b'\0',1);reader=os.fsdecode(filename);literal=os.fsdecode(match)
    if literal not in cache:
        found=set()
        for start in range(len(literal)):
            for length in lengths:
                if start+length>len(literal):break
                sub=literal[start:start+length]
                if sub in names:found.add(sub)
        cache[literal]=set().union(*(names[n] for n in found)) if found else set()
    refs[reader].update(cache[literal]);matches+=1
error=proc.stderr.read().decode();rc=proc.wait()
assert rc in (0,1),(rc,error)
changes=json.loads((O/'reader_changes_v2.json').read_text());changed={x['path'] for x in changes}
details=json.loads((O/'reader_sites_v2.json').read_text());static=collections.defaultdict(set)
for s in details:static[s['reader']].update(s.get('paths',[]))
# Exact read sites are included even if rg's basename overlap strategy hides a
# longer pattern. Every output pair is still a literal current-file reference.
for reader,ps in static.items():
    if (R/reader).is_file():
        text=(R/reader).read_text(errors='replace')
        refs[reader].update(p for p in ps if p in move and (p in text or Path(p).name in text))
# A direct test diff is a handoff only: never applied by this run.
test_diff=(O/'CLEAN4T_READER_HANDOFF_v2.diff').read_text()
test_handoff={line[6:] for line in test_diff.splitlines() if line.startswith('+++ b/')}
# Provider coverage is reported separately from basename identity.
providers=collections.defaultdict(set)
for reader in refs:
    if not reader.endswith('.py'):continue
    try:tree=ast.parse((R/reader).read_text())
    except (SyntaxError,UnicodeError):continue
    for node in tree.body:
        if isinstance(node,ast.ImportFrom) and node.module:
            module=node.module.replace('.','/')+'.py'
            if module in changed:providers[reader].add(module)
            for alias in node.names:
                mod=node.module.replace('.','/')+'/'+alias.name+'.py'
                if mod in changed:providers[reader].add(mod)
        elif isinstance(node,ast.Import):
            for alias in node.names:
                mod=alias.name.replace('.','/')+'.py'
                if mod in changed:providers[reader].add(mod)
header=['live_reader','MOVE_path','reference','proposed_change','status']
counts=collections.Counter();pairs=0
with (O/'LIVE_READERS_v2.tsv').open('w',newline='') as f:
    writer=csv.writer(f,delimiter='\t',lineterminator='\n');writer.writerow(header)
    for reader,paths in sorted(refs.items()):
        try:text=(R/reader).read_text(errors='replace')
        except OSError:continue
        for path in sorted(paths):
            full=path in text
            if Path(path).name in {'docs','artifacts'} and not full:
                status='basename collision';proposed='No path rewrite: generic docs/artifacts text is not a load of this symlink.'
            elif reader in test_handoff and path in static[reader]:
                status='CLEAN4T handoff';proposed='Use input_path(existing_expression), which delegates to greekocr.ops.data_root.resolve(repo_relative_path); staged in CLEAN4T_READER_HANDOFF_v2.diff. Existing tests were not edited.'
            elif reader in changed and path in static[reader]:
                status='applied';proposed='Read/hash via input_path(existing_expression) -> greekocr.ops.data_root.resolve(repo_relative_path); repo first, then GREEK_OCR_DATA_ROOT mirror; missing error names receipt.'
            elif reader in changed:
                status='adapter applied; basename identity ambiguous';proposed='Shared file-input adapter applied in this file; basename match is not proof that this specific MOVE file is consumed. Output writers unchanged.'
            elif providers[reader]:
                status='shared adapter';proposed='Input helper provided by '+', '.join(sorted(providers[reader]))+' resolves missing repo-local paths via greekocr.ops.data_root.resolve; no caller rewrite needed. Basename identity may be ambiguous.'
            elif not reader.endswith(('.py','.sh','.js','.mjs','.rs')):
                status='metadata/record';proposed='Literal reference in data/record; no code edit. Reader of this metadata must call greekocr.ops.data_root.resolve on repo-relative input fields; serialized records retained.'
            else:
                status='lexical reference; no proven MOVE input';proposed='No path-specific substitution: reference is a basename, producer name, command/example, other-root input or source-control identity. If supplied as a repo data input use greekocr.ops.data_root.resolve(repo_relative_path) at its file-open boundary; do not redirect output writes.'
            writer.writerow([reader,path,'full path' if full else 'basename',proposed,status]);counts[status]+=1;pairs+=1
metrics=json.loads((O/'metrics_v2.json').read_text())
conflicts=list(csv.DictReader((O/'RECEIPT_CONFLICTS.tsv').open(),delimiter='\t'))
plan={r['path']:r for r in rows};decisions=[]
for c in conflicts:
    action=plan[c['path']]['decision']
    decision=f'{action} exact HEAD bytes/hash as custody; lead-receipt bytes/hash noted as a distinct source-worktree version, never substitute or overwrite. If destination differs, mover stops.'
    decisions.append([c[k] for k in ('path','HEAD_bytes','HEAD_sha256','lead_bytes','lead_sha256','lead_receipt')]+[action,decision])
with (O/'RECEIPT_CONFLICT_DECISIONS_v2.tsv').open('w',newline='') as f:
    w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['path','HEAD_bytes','HEAD_sha256','lead_bytes','lead_sha256','lead_receipt','v2_decision','custody_decision']);w.writerows(decisions)
assert len(conflicts)==23
m,k=metrics['stats']['MOVE'],metrics['stats']['KEEP']
summary=['# CLEAN3B summary v2','',f'MOVE **{m["count"]:,} entries / {m["bytes"]:,} bytes**; KEEP **{k["count"]:,} entries / {k["bytes"]:,} bytes**. All 61,533 CLEAN3A HEAD inventory paths are covered once. {metrics["delta_count"]:,} v1 MOVE entries ({metrics["delta_bytes"]:,} bytes) now KEEP. All 19 ASK symlinks now MOVE, hashed as stored link text. No file moves, untracking, commits, ignore installation or history changes were executed.','',f'Rules: {metrics["rules"]["a"][0]} a; {metrics["rules"]["b"][0]} b; {metrics["rules"]["c"][0]} c; {metrics["rules"]["d"][0]} d. Small literal inputs exempted: {len(metrics["small"])}. Directories becoming empty: {metrics["empty_HEAD"]} in HEAD and {metrics["empty_working_tree"]} in the observed working tree. See MOVE_PLAN_v2.md and EMPTY_DIRECTORIES_v2.tsv.','', '## Reader changes','',f'{len(changed)} existing source files patched at file input/hash boundaries, plus greekocr/ops/data_root.py and tests/test_data_root.py added. Full source changes: LIVE_READER_PATCHES_v2.diff; per-file hashes: reader_changes_v2.json; every path and final byte count: FILES_WRITTEN_v2.tsv. ops/__init__.py lazily loads receipt/rate helpers to avoid a resolver -> receipt -> vendor -> resolver import cycle and importing OCR dependencies merely to resolve a path. Public helper exports are preserved.','',f'Fresh literal scan: {len(refs):,} live files, {pairs:,} reader/MOVE pairs; {matches:,} rg matches. LIVE_READERS_v2.tsv includes full-path references, basename collisions, producer/example mentions and metadata. A lexical match is not a claim that a specific file is loaded. Code changes resolve at existing input boundaries; output writes and historical docs/ scripts are unchanged.','',f'Existing tests were not edited. {len(test_handoff)} test files have direct input-site changes staged in CLEAN4T_READER_HANDOFF_v2.diff; coordinator/CLEAN4T must reconcile and apply that patch after concurrent edits. Other test readers inherit patched shared input helpers.','', '## Receipt conflicts: HEAD has custody','', 'Each of the 23 lead conflicts is decided below. Complete HEAD and lead sizes, hashes and lead receipt paths remain in RECEIPT_CONFLICT_DECISIONS_v2.tsv; the original CLEAN3A conflict file is unchanged. A lead version is noted, not transferred by this checkout.','', '| Path | v2 | Decision |','|---|---|---|']
for d in decisions:summary.append(f'| `{d[0]}` | {d[-2]} | HEAD bytes/hash have custody; distinct lead version noted; never replace HEAD with lead bytes. |')
summary+=['','## Mover and execution boundaries','', 'The coordinator command is:','', '```sh','python3 docs/cleanup_20261019/data_out/move_data.py --execute --dest /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-data','```','', 'The mover first verifies every source and existing destination. Same-hash destinations are skipped, leaving any repository source intact. Different bytes or file/link types stop execution before transfers. Cross-filesystem transfers use exclusive destination creation, hash verification and fsync, with a durable manifest entry before source unlink. MOVE_MANIFEST.tsv and rollback.sh are created only by execution. Interrupted partial destination copies cause a mismatch stop; they are never overwritten automatically. A complete copied destination with its source still present is skipped safely. Rollback restores journaled source losses without overwriting differing repository paths; already-present identical paths are left intact.','', f'RECEIPTS/INDEX.md indexes {len(metrics["shards"])} shard(s), each <=4,000,000 bytes, covering every MOVE entry. SYMLINKS_v2.tsv records the 19 exact link texts; mirrored directories are preserved and external link targets are never copied. SEGEVAL1.bundle and candidate_order_KEEP historical guard notes are in the index.','',f'gitignore_additions_v2.txt has {metrics["ignore_patterns"]} patterns plus comments (<=300 lines). Scoped extension patterns also match some retained small exports: ignore rules cannot express size thresholds. Those KEEP files remain tracked; no source-extension blanket rule is introduced. Small live bulk exceptions are negated explicitly. The oversized generated MOVE_PLAN_v2.tsv is excluded as a local planning artifact. Install additions and untrack only after custody is verified. The size guard checks indexed blob sizes, so missing working files cannot hide tracked large blobs.','', '## Validation and open questions','', '- Inventory scope is frozen to CLEAN3A HEAD ac1c38cf6ebab49ef694fffb2a8b3dc757012f33. At the first successful CLEAN3B baseline, HEAD was already 70a3a4de6b7eb5da72292b7d9bbb6ad52a3a59e5, with 44 added CLEAN3A report/draft paths outside that input inventory. Original inventory index modes/blob IDs are unchanged. Those later additions were not folded into the requested v1-based plan; review their disposition separately (notably the generated basename_patterns.txt). The recorded CLEAN3B HEAD/index baseline remains unchanged. INDEX_DELTA_v2.json lists the additions.', '- Full dry-run source hashes, receipt coverage, classification, ignore coverage, immutable CLEAN3A files and indexed object identities are checked by validate_v2.py; results are in VALIDATION_v2.json.','- New resolver + read-only mover checks: 24 passed under the x86_64 Python interpreter. No transfer/execute/rollback was exercised on real data.','- Broader pre-move selection: 96 passed, 17 failed. Failures involve incompatible SciPy architecture, missing historical budget ledgers and SHEETS.md. Verify-suite collection also hits the incompatible SciPy installation. These are not evidence of post-move reader qualification; this run did not modify those tests or supply missing external inputs.','- Reconcile the staged existing-test reader edits with CLEAN4T before relocation. Directory enumeration, generated HTML relative assets, command examples and caller-supplied data fields need post-move integration checks; literal references alone cannot certify dynamic consumers.','- Set GREEK_OCR_DATA_ROOT for actual jobs and confirm destination capacity/durability. No destination data or external-worktree custody has been acquired here. A mirror holding a conflicting lead version must be versioned separately; the mover stops on a conflict.','- The 19 stored symlink targets can remain dangling after relocation. This preserves their exact custody, not availability of their external targets.','- Historical s1–s4/gate_rereport/gate03 guards and source-hash-bound records remain unchanged. Replay requires a new receipt-backed adapter or deliberately restored mirror; do not edit old records to make a check pass.','', '## Files changed by this run','']
summary.extend('- `'+p+'`' for p in sorted(changed|{'greekocr/ops/data_root.py','tests/test_data_root.py'}))
(O/'SUMMARY_v2.md').write_text('\n'.join(summary)+'\n')
(O/'reader_scan_v2.json').write_text(json.dumps(dict(command=command,matches=matches,live_files=len(refs),pairs=pairs,status_counts=counts,test_handoff_files=sorted(test_handoff),source_files_changed=len(changed),stderr=error),indent=2)+'\n')
print(json.dumps(dict(live_files=len(refs),pairs=pairs,status_counts=counts,test_handoff_files=len(test_handoff)),indent=2))
