"""Render CLEAN3A proposals from the read-only snapshot and basename scan."""
import collections,csv,hashlib,json,os,pathlib,re,subprocess
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];os.chdir(R)
S=json.loads((O/'snapshot.json').read_text());rows=S['rows'];by_path={x['path']:x for x in rows}
refs=json.loads((O/'readers.json').read_text())
LIMIT=5_000_000;DATA='/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-data'
def tsv(name,header,data):
 with (O/name).open('w',newline='') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(header);w.writerows(data)
def code(p):return pathlib.PurePosixPath(p).suffix.lower() in {'.py','.sh','.rs','.js','.mjs','.c','.h','.cpp','.sbatch'}
receipts=['docs/harvest/seg_census/OUT_OF_GIT_RECEIPT.md','docs/labelfix/spellcheck/OUT_OF_GIT_RECEIPT.md','docs/harvest/collect_v3_admission/OUT_OF_GIT_RECEIPT.md','docs/harvest/pilots_v2/RECEIPTS_OUT_OF_GIT.md']
receipt_rows=[];receipt_links=[];receipt_matches=collections.defaultdict(list)
for receipt in receipts:
 for line in (R/receipt).read_text().splitlines():
  if not line.startswith('|'):continue
  cells=[c.strip().strip('`') for c in line.strip('|').split('|')]
  paths=[c for c in cells if '/' in c and not c.startswith('sha') and not ' ' in c]
  hashes=[c for c in cells if re.fullmatch('[0-9a-f]{64}',c)]
  sizes=[int(c.replace(',','')) for c in cells if re.fullmatch('[0-9][0-9,]*',c)]
  if 'symlink' in cells and cells[0] and len(cells)>=3:
   lp=cells[0];target=cells[2].removeprefix('-> ');actual=os.readlink(R/lp) if (R/lp).is_symlink() else ''
   receipt_links.append((receipt,lp,target,str(lp in by_path),actual,'same target' if actual==target else 'not present here or different target; retain source-worktree custody'))
  if not(paths and hashes and sizes):continue
  p=paths[-1];n=sizes[-1];sha=hashes[-1];x=by_path.get(p)
  status='not tracked in this HEAD; receipt is custody input, not a move here'
  if x:
   status='tracked here; bytes and sha256 agree' if (x['bytes'],x['sha256'])==(n,sha) else 'CONFLICT: HEAD bytes/hash differ from lead receipt'
   receipt_matches[p].append((receipt,status))
  receipt_rows.append((receipt,p,n,sha,status))
tsv('RECEIPT_RECONCILIATION.tsv',['receipt','path','bytes','sha256','HEAD_status'],receipt_rows)
tsv('RECEIPT_LINKS.tsv',['receipt','path','recorded_link_target','tracked_in_HEAD','current_target','status'],receipt_links)
source_suffix={'.py','.sh','.rs','.js','.mjs','.css','.toml','.yaml','.yml','.sbatch','.c','.h','.cpp','.patch','.diff','.svg','.mmd','.typed','.ini','.cfg'}
record_words=('receipt','manifest','sha256','sha256sums','initial_hash','initial_scope','scope_guard','input_hash','deploy_files','deploy_sha','files.tsv','checksums','seal','provenance')
small_evidence='docs/harvest/collect_v3_admission/segeval1/keys/census02_segmentation_evidence.jsonl'
def kind(p):
 l=p.lower();name=pathlib.PurePosixPath(l).name
 if l.endswith(('.bundle','.tar','.tar.gz','.tgz','.zip','.whl')):return 'bundle'
 if l.endswith(('.png','.jpg','.jpeg','.webp')):
  return 'montage' if any(s in name for s in ('montage','contact','grid')) else 'crop-set'
 if l.endswith('.html'):return 'sheet'
 if l.endswith(('.log','.codexlog','.xml','.stderr','.stdout','.headers','.body')) or '/pytest_tmp/' in l:return 'log'
 if '/keys/' in l or 'candidate_order' in name:return 'key'
 if any(s in name for s in ('census','population_cells','admission_census')) and l.endswith(('.json','.jsonl','.gz','.csv','.tsv')):return 'census-export'
 if any(s in l for s in ('/output_','/predictions','runtime.jsonl','/rollout','model_output')) or l.endswith(('.npz','.npy','.pt','.pth','.safetensors','.onnx')):return 'model-output'
 if l.endswith(('.jsonl','.jsonl.gz')) or any(s in name for s in ('train_pool','candidates.json','pool.json')):return 'pool'
 return 'other'
for x in rows:
 p=x['path'];name=pathlib.PurePosixPath(p).name;l=p.lower();ext=pathlib.PurePosixPath(l).suffix
 x['readers']=[r for r in refs.get(name,[]) if r!=p]
 x['kind']=kind(p)
 code_refs=[r for r in x['readers'] if code(r)]
 if x['bytes']>LIMIT:
  decision='MOVE';reason='Exceeds 5,000,000-byte tracked-file limit; preserve exact bytes at mirrored data-root path.'
 elif x['mode']=='120000':
  decision='ASK';reason='Tracked symlink (hash/bytes are link-target text); resolve dangling/external target and reader behavior before deciding relocation.'
 elif p==small_evidence:
  decision='KEEP: source';reason='Explicit small frozen-evidence retention in segmentation lead receipt (3889741f3); this is a documented exception to general bulk-data placement, not new source code.'
 elif (p.startswith('scripts/') and ext=='.html') or (p.startswith('tests/') and ext=='.html'):
  decision='KEEP: source';reason='Small application HTML source or offline HTML test fixture, rather than a generated review sheet.'
 elif ext in source_suffix or name in {'Cargo.lock','LICENSE','LICENSE.txt','Makefile','Dockerfile','.gitignore','pyproject.toml','AGENTS.md'}:
  decision='KEEP: source';reason='Source/configuration/build or reviewable code patch; size within limit, including archived source copies.'
 elif ext=='.md':
  decision='KEEP: source';reason='Human-readable documentation, historical report, or custody receipt; size within limit.'
 elif any(word in name.lower() for word in record_words) and ext in {'.json','.txt','.tsv','.sha256','.gz'}:
  decision='KEEP: source';reason='Small receipt, manifest, hash/scope record or deploy index kept for provenance/retrieval; source-record category.'
 elif p.split('/')[0] in {'greekocr','scripts','config','seed','worker','collect_v3','legacy_l1','prototypes'} and x['kind']=='other':
  decision='KEEP: source';reason='Small runtime asset/configuration or vendored source input; not a bulk output.'
 elif p.startswith('tests/') and x['kind']=='other':
  decision='KEEP: source';reason='Small test fixture/configuration; preserve the offline test input.'
 elif p.startswith('tests/') and code_refs and x['kind'] in {'crop-set','pool','key'}:
  decision='KEEP: ≤ 5 MB and referenced by code/tests';reason='Small test fixture with literal basename reference in code/tests; explicit KEEP exception available in owner decision vocabulary.'
 elif x['kind']!='other' or p.startswith(('docs/','artifacts/','out/','fixes/')):
  decision='MOVE';reason='Generated artifact or bulk evidence; move even below size limit and retain receipt in git.'
 elif code_refs:
  decision='KEEP: ≤ 5 MB and referenced by code/tests';reason='Small referenced input; retain pending any later source-layout change.'
 else:
  decision='ASK';reason='Unclassified small non-source file; preserve in place until purpose/custody is resolved.'
 if p in receipt_matches:
  reason+=' Lead receipt: '+ '; '.join(r+' ('+s+')' for r,s in receipt_matches[p])+'.'
 if p.endswith('SEGEVAL1.bundle'):
  reason+=' PRESERVE THE FILE: bundled head b3b5aaa19835ac626af6576da37e008386b26879 is absent from local object database; copy, hash-verify and record durable custody before untracking; never infer recoverability from history.'
 if p.endswith('candidate_order_KEEP.jsonl'):
  reason+=' Sampling key; historical initial-hash/scope rechecks will report missing after move, as acknowledged by lead.'
 if decision=='KEEP: source' and (ext in source_suffix or (ext=='.html' and p.startswith(('scripts/','tests/')))):x['kind']='other'
 x['decision']=decision;x['reason']=reason
moves=[x for x in rows if x['decision']=='MOVE'];move_paths={x['path'] for x in moves}
# These are literal reference candidates, not proof a same-named file is opened.
reader_targets=collections.defaultdict(list)
for x in moves:
 for reader in x['readers']:
  if code(reader):reader_targets[reader].append(x['path'])

def fix(reader):
 if reader.startswith(('docs/','artifacts/')):
  return 'Preserve historical source; add a replay/receipt resolver mapping each original input to Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path, and write regenerated outputs outside git.'
 if reader.endswith('.rs'):
  return 'Resolve each relocated input as PathBuf::from(std::env::var("GREEK_OCR_DATA_ROOT")?) .join(repo_relative_path), checking the retained receipt.'
 if reader.endswith(('.sh','.sbatch')):
  return 'Resolve relocated inputs/outputs under "${GREEK_OCR_DATA_ROOT:?}/<repo-relative-path>"; verify input receipt hashes before running.'
 if reader.endswith(('.js','.mjs')):
  return 'Resolve moved inputs through GREEK_OCR_DATA_ROOT or a receipt-backed staging resolver; emit generated sheets/assets under that root.'
 return 'Resolve relocated inputs using Path(os.environ["GREEK_OCR_DATA_ROOT"]) / repo_relative_path (or a hash-checked receipt lookup); route generated bulk outputs there too.'

tsv('READERS_TO_UPDATE.tsv',['reader','MOVE_path_basename_matched','reference_evidence','one_line_fix'],[(r,p,'literal basename match; same-name collisions and producer-only mentions need line review',fix(r)) for r,ps in sorted(reader_targets.items()) for p in sorted(ps)])
# Empty means no current nonmoving leaf remains, including symlinks and untracked files.
children=collections.defaultdict(set)
for x in rows:
 for d in pathlib.PurePosixPath(x['path']).parents:
  if str(d)!='.':children[str(d)].add(x['path'])
nontracked=[]
for root,dirs,files in os.walk(R,followlinks=False):
 dirs[:]=[d for d in dirs if d!='.git']
 for name in files+[d for d in dirs if (pathlib.Path(root)/d).is_symlink()]:
  p=(pathlib.Path(root)/name).relative_to(R).as_posix()
  if p not in by_path:
   nontracked.append(p)
   for d in pathlib.PurePosixPath(p).parents:
    if str(d)!='.':children[str(d)].add(p)
empty=sorted(d for d,ps in children.items() if ps and ps<=move_paths)
emptyset=set(empty);empty_roots=[d for d in empty if not any(str(p) in emptyset for p in pathlib.PurePosixPath(d).parents)]
tsv('EMPTY_DIRECTORIES.tsv',['directory','tracked_MOVE_files','tracked_MOVE_bytes'],[(d,len(children[d]),sum(by_path[p]['bytes'] for p in children[d])) for d in empty])
# Directory ignores only where every current descendant is moved; exact anchored paths
# elsewhere prevent ignoring retained scripts/receipts in mixed directories.
covered={p for d in empty_roots for p in children[d]}
ignore=['/'+d+'/' for d in empty_roots]+['/'+p for p in sorted(move_paths-covered)]
def escape(s):return ''.join('\\'+c if c in '\\*?[]!#' else c for c in s)
(O/'.gitignore.proposed').write_text('# CLEAN3A proposal only: append after verified relocation and untracking.\n# Exact paths/move-only directories; retained source and receipts stay addable.\n'+'\n'.join(escape(p) for p in ignore)+'\n')
tsv('MOVE_PLAN.tsv',['path','bytes','sha256','kind','producing_commit','readers','decision','reason'],[(x['path'],x['bytes'],x['sha256'],x['kind'],x['producing_commit'],'; '.join(x['readers']) or 'none',x['decision'],x['reason']) for x in rows])
def totals(key):
 out=collections.defaultdict(lambda:[0,0,0,0])
 for x in rows:
  a=out[key(x)];a[0]+=1;a[1]+=x['bytes']
  if x['decision']=='MOVE':a[2]+=1;a[3]+=x['bytes']
 return out
def table(t):
 return '\n'.join(['| Group | Inventoried count | Inventoried bytes | MOVE count | MOVE bytes |','|---|---:|---:|---:|---:|']+['| '+k+' | '+' | '.join(f'{n:,}' for n in v)+' |' for k,v in sorted(t.items())])
counts=collections.Counter(x['decision'] for x in rows);movebytes=sum(x['bytes'] for x in moves);large=[x for x in rows if x['bytes']>LIMIT]
conflicts=[r for r in receipt_rows if r[-1].startswith('CONFLICT')]
tsv('RECEIPT_CONFLICTS.tsv',['path','HEAD_bytes','HEAD_sha256','lead_bytes','lead_sha256','lead_receipt','required_resolution'],[(r[1],by_path[r[1]]['bytes'],by_path[r[1]]['sha256'],r[2],r[3],r[0],'Preserve both versions; HEAD inventory is authoritative for this checkout, lead receipt remains authoritative for its source-worktree version. Do not overwrite either at a shared mirrored destination; settle versioned custody first.') for r in conflicts])
bydec={d:dict(count=sum(x['decision']==d for x in rows),bytes=sum(x['bytes'] for x in rows if x['decision']==d)) for d in counts}
audit=dict(head=S['head'],tracked_count=len(rows),tracked_bytes=sum(x['bytes'] for x in rows),large_count=len(large),large_bytes=sum(x['bytes'] for x in large),move_count=len(moves),move_bytes=movebytes,decisions=bydec,empty_directories=len(empty),empty_roots=len(empty_roots),code_reference_files=len(reader_targets),code_reference_pairs=sum(map(len,reader_targets.values())),receipt_rows=len(receipt_rows),receipt_tracked_matches=sum('tracked here' in r[-1] for r in receipt_rows),receipt_conflicts=conflicts,source_bytes_match_HEAD=True,threshold_bytes=LIMIT)
(O/'AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
plan=f'''# CLEAN3A — proposed data relocation; no moves performed

Snapshot: `{S['head']}`. Data root: `{DATA}/`; destination for each MOVE is `$GREEK_OCR_DATA_ROOT/<path>` with the repository-relative path unchanged. MB is decimal: 5,000,000 bytes; directory byte threshold is strictly >20,000,000, and extension threshold is ≥50 combined PNG/JPG/JSONL/JSONL.GZ/HTML files (case-insensitive). Nothing is removed from history.

`MOVE_PLAN.tsv` inventories **all {len(rows):,} HEAD paths**, a conservative superset of the requested >5 MB and bulk-directory union. This avoids treating a recursive threshold on `docs/` or the repo root as permission to move source. `BULK_DIRECTORIES.tsv` lists direct and recursive metrics for every qualifying non-root directory; the repository root also qualifies recursively. Every descendant is covered, including source/configuration/record siblings. Decisions classify individual files, not whole qualifying directories. HEAD blob lengths come from `git cat-file`; every working regular file and symlink target was SHA256-hashed and its Git blob identity checked against HEAD. An independent recursive HEAD tree traversal (3,360 tree objects) confirmed that the index path set and object IDs exactly match all 61,533 HEAD blobs. Symlinks are measured as stored target text, not followed. Every producing commit is the exact result of `git log -1 --format=%h -- <path>`; it means last path touch, not necessarily original generation.

## Totals by kind

{table(totals(lambda x:x['kind']))}

## Totals by top-level directory

{table(totals(lambda x:x['path'].split('/')[0] if '/' in x['path'] else '(root files)'))}

Decisions: {', '.join(f'{k}: {v:,}' for k,v in sorted(counts.items()))}. Proposed MOVE: **{len(moves):,} files / {movebytes:,} bytes**. Oversized subset: **{len(large):,} / {sum(x['bytes'] for x in large):,} bytes**. Counts are unique paths, not distinct hashes; no hardlink/dedup or filesystem-allocation savings are assumed. Moving files and untracking them will not shrink existing `.git` history.

## Lead receipt reconciliation and custody

Inputs (preserved, never edited):

'''+''.join(f'- `{p}`\n' for p in receipts)+f'''
`RECEIPT_RECONCILIATION.tsv` checks every parseable per-file receipt row against this HEAD: {len(receipt_rows):,} rows; {sum('tracked here' in r[-1] for r in receipt_rows):,} tracked byte/hash matches; {len(conflicts):,} conflicts. “OUT of git” in the spellcheck, small-segment and pilot receipts describes their source worktrees at receipt time, not proof those bytes were moved into the new data root. Paths absent from this HEAD are custody follow-ups, not added to MOVE totals. The spellcheck summary additionally covers 988 files / 2,250,088,199 bytes at `artifacts/sf7_rc1/output_3687228/`, with 985 hashes in its tracked READBACK_RECEIPT; the three remaining files are individually tabled. Do not double-count those 988 with table rows. The pilots receipt covers 3,460 files / 7,273,359 bytes in the inventory worktree; its committed RECEIPTS_MANIFEST.tsv remains authoritative. The six small-segment files listed by the sourcing lead remain custody obligations outside this HEAD. Symlink rows are recorded separately in RECEIPT_LINKS.tsv; their target strings are not mistaken for SHA256s.

**Receipt contradictions requiring reconciliation:** `RECEIPT_CONFLICTS.tsv` lists both HEAD and lead bytes/hashes for every conflict. These are different versions at the same relative paths. The HEAD hash in MOVE_PLAN.tsv is the version inventoried here; it does not invalidate the source-worktree version in the lead receipt. Preserve both and settle versioned custody before copying to a shared mirrored destination; never overwrite or call the older receipt wrong. Conflicting paths:

{chr(10).join('- `'+r[1]+'`' for r in conflicts)}

The segmentation lead explicitly keeps `artifacts/n1/n1_v1_train.sha256`, `docs/labelfix/lqb/truth_v1_1.sha256` and the 1.7 MB `segeval1/keys/census02_segmentation_evidence.jsonl` in git. This plan keeps them. The small frozen evidence is a documented lead exception to general bulk placement; `KEEP: source` includes retained provenance records and does not claim the JSONL is executable source. Literal references alone do not make a bulk artifact source. Small directly referenced test fixtures use the explicitly allowed ≤5 MB KEEP decision; audit that exception before enforcing a zero-bulk interpretation.

**SEGEVAL1.bundle must be preserved as a file.** Its on-disk bundle header names `b3b5aaa19835ac626af6576da37e008386b26879 refs/heads/segeval1-artifacts`; read-only `git cat-file -t` returns 128 (object unavailable). The lead also states that head is not in history. Required receipt: 147,025,055 bytes, SHA256 `25c38794aacb89d083b461175471735575551f0acc4d1f612214b3e43fee1e1a`. Before any future untracking, copy without overwrite to the mirrored data-root path, hash-read it back, retain the bundle header/ref plus producing commit and readers in the git receipt, and establish durable custody. Do not substitute a pointer to repository history or regenerate this bundle in place.

`candidate_order_KEEP.jsonl`: 476,509,196 bytes, SHA256 `08b1b5a054bd5161534ac637c81b4155be6d4d6c843ab41421f584b0c285dd07`. The lead says no semantic code reader opens this sampling key by name. It is still a protected path in historical guards. Moving this key and the bundle makes the following stored checks report missing if rerun unchanged:

- `docs/harvest/seg_steps/s1/initial_hashes.json`
- `docs/harvest/seg_steps/s2/initial_hashes.json`
- `docs/harvest/seg_steps/s3/initial_hashes.json`
- `docs/harvest/seg_steps/s4/initial_hashes.json`
- `docs/harvest/seg_steps/gate_rereport/initial_scope.json`
- `docs/harvest/line_pipeline/gate03/part3-initial-hashes.json`

Preserve those historical records unchanged. A new replay wrapper must look up moved protected paths by their original names in the relocation receipt, resolve through GREEK_OCR_DATA_ROOT, and verify the original recorded hash. Report relocation separately from an altered or missing artifact; do not silently drop guards or rewrite their historical success claims. Other moved historical inputs need the same treatment.

## Reader changes required before relocation

`readers` is a case-sensitive literal-basename grep over all regular text files in the working tree, with hidden/ignored files included; `.git/` and these generated planning outputs are excluded, and symlink directories are not followed. Each cell lists distinct referencing files (self-reference excluded), or `none`; it is not a semantic dependency claim. Binary/compressed content is not decoded. Short names and shared basenames produce intentional false positives. `READERS_TO_UPDATE.tsv` provides every MOVE/code-or-test basename pair with a one-line fix; {len(reader_targets):,} unique source readers / {sum(map(len,reader_targets.values())):,} pairs. It includes archived code, producers and documentation strings inside code, so review literal access sites before changing them. A basename match alone cannot establish that every same-named MOVE path will break that reader. Actual direct accesses will fail after relocation unless resolved or staged; historical reports should stay historical.

Use a resolver requiring `GREEK_OCR_DATA_ROOT`, accepting an original repository-relative receipt key, rejecting absolute/`..` escapes, and checking expected bytes/hash. Existing code roots must continue locating source and small retained assets inside the repository. Resolve only the relocated data paths; do not replace a general repository ROOT wholesale. For offline fixtures, provision bytes by receipt before tests, and fail with a retrieval instruction when missing; do not skip coverage. HTML sheet relative image/JSON links need the whole mirrored asset subtree or a receipt-backed staging tree; file:// browser access cannot directly read a shell env var. Package/build scripts and generated outputs need the data-root destination as well as input lookup.

Direct access sites checked in source (separate from the broad basename candidates):

| Source site | Behavior after the proposed move | One-line fix |
|---|---|---|
| `scripts/numerics/n1g.py:310` | Passes the moved frozen `truth_v1_1.jsonl` to `lqb.run`. | Resolve `docs/labelfix/lqb/truth_v1_1.jsonl` under GREEK_OCR_DATA_ROOT before calling the scorer. |
| `scripts/secondary/ru2t_apply_lead.py:78` | Supplies the moved truth path as the scorer's `--truth` argument. | Pass the receipt-resolved external truth path to `--truth`, keeping the code/registry paths in the repo. |
| `scripts/secondary/ru2t_delivery.py:127` | Binds the moved frozen truth to its scoring input. | Bind the original truth receipt key to GREEK_OCR_DATA_ROOT and verify its frozen SHA256. |
| `tests/test_lqb5.py:14,23` | Opens and hashes the moved truth directly under `lqb.DEFAULT`. | Resolve only the truth file through its external receipt; retain manifest/sidecar lookup in the repo and provision the truth before the test. |
| `docs/harvest/collect_v3_admission/segeval1/cells/classify_population.py:53–54` | Hashes the moved census gzip before processing it. | Replay through a wrapper resolving `docs/harvest/collect_v3_admission/segeval1/cells/population_cells.jsonl.gz` at the data root without rewriting historical source. |
| `docs/harvest/seg_steps/gate_rereport/analyze.py:262–264` | Tracks and opens that moved census gzip. | Use a receipt-backed replay input resolver preserving the historical original-path/hash key. |
| `tests/glyphs/test_initial_batches.py:13–14` | Globs fixture crop directories; moving most PNGs leaves an incomplete pool even though no moved basename is literal here. | Build a receipt-backed fixture view combining retained repo fixtures and moved data-root crops under their original relative names before globbing. |

Producer-only examples: `scripts/numerics/n1_apply_train.py:133` names `n1_v1_train.jsonl` as an output default; route the new output to the data root. `scripts/numerics/n1r_receipt.py:96` mentions it in report prose, so that mention alone needs no data-reader patch. Tests that construct same-named files in `tmp_path` are independent fixtures and should keep doing so.

One-line fix for every literal source-reference candidate (full target list is in `READERS_TO_UPDATE.tsv`):

| Reader | MOVE basename pairs | One-line fix |
|---|---:|---|
'''+''.join(f'| `{r}` | {len(ps):,} | {fix(r)} |\n' for r,ps in sorted(reader_targets.items()))+'''
The basename scan does not detect computed filenames, directory globbing, or strings inside compressed manifests. A relocation execution gate must additionally audit directory consumers and relative HTML assets (especially tests/fixtures, crop/zoom directories, sheet img/src links, package manifests, census/pool loaders, and deploy scripts), provision their receipt-backed inputs, and run affected offline tests. This is an analysis limitation, not evidence that unlisted consumers cannot break.

## Directories becoming empty

These are current directories whose every leaf is a MOVE path; retained files, tracked symlinks and untracked files prevent an empty classification. Git does not track empty directories. These counts describe the proposed decisions with ASK paths left in place. Complete list (also machine-readable in `EMPTY_DIRECTORIES.tsv`):

'''+''.join(f'- `{d}/`\n' for d in empty)+f'''
There are {len(empty):,} such directories, covered by {len(empty_roots):,} maximal empty subtrees. No directory is removed by this run.

## Proposed guard and ignore rules

`size_guard_test.py` is a proposed pytest, not installed into `tests/`. It reads `git ls-files -z`, measures regular files and stored symlink target text, fails on unavailable tracked paths, and rejects sizes strictly greater than 5,000,000 bytes. It neither reads artifact contents nor writes git. Its callable was checked on this unmodified inventory and failed as expected with exactly 232 oversized paths; no test was installed and no artifact was changed. It intentionally does not prove receipt completeness, validate historical blob size, or prevent force-add; review staged content separately at execution time.

Append `.gitignore.proposed` only in the later approved move change. Its {len(ignore):,} anchored rules cover every MOVE path and no retained/ASK HEAD path: whole directories only when every current descendant moves, exact paths otherwise. This protects mixed source/receipt directories and avoids global *.jsonl/*.png/*.html exclusions that would hide legitimate source/test fixtures. Git ignore rules do not affect already tracked paths; relocation/untracking must precede enforcement. Git can override ignore with force-add; the guard supplies the tracked-size backstop. Future ≤5 MB artifact names in mixed directories still require review, rather than a broad unreviewed ignore.

## Future execution gates — not performed here

1. Resolve ASK paths and the small evidence/test fixture exceptions; approve the exact MOVE path list and consumer fixes.
2. Confirm GREEK_OCR_DATA_ROOT points to the designated external root, and check available capacity (no assumption about cross-volume renames or immediate freed bytes).
3. Copy each artifact without overwrite; verify destination bytes and SHA256 against this plan, reconcile lead-only custody items without claiming new transfers, and retain a receipt in git with original path, destination, bytes, SHA256, producing commit, readers and copy verification.
4. Exercise the resolver and affected offline tests, historical guard adapters, deploy/package readers and sheet assets against the external copies. Preserve SEGEVAL1.bundle independently of history.
5. Only after coordinator/owner path-list approval, perform the separately authorized source removals/untracking, append ignores, and install the guard. Never rewrite history. Keep rollback/retrieval receipts; do not regenerate or discard frozen benchmark truths.

The full TSV is deliberately exhaustive and may itself exceed 5 MB. This analysis artifact must stay untracked until it is split into ≤5 MB receipt shards or compressed below the limit, with an index/hash receipt retained. Applying the new guard while force-adding an oversized plan would violate the owner rule. This run does not add any planning output to git.
'''
(O/'MOVE_PLAN.md').write_text(plan)
asks=[x for x in rows if x['decision']=='ASK']
summary=f'''# CLEAN3A summary — analysis only

HEAD `{S['head']}`; no files moved, no git writes, no history rewrite. All outputs are under `docs/cleanup_20261019/data_out/`.

| Measure | Files | Bytes |
|---|---:|---:|
| HEAD inventory (complete conservative scope) | {len(rows):,} | {sum(x['bytes'] for x in rows):,} |
| >5,000,000-byte files (all MOVE) | {len(large):,} | {sum(x['bytes'] for x in large):,} |
| Proposed MOVE (includes oversized subset) | {len(moves):,} | {movebytes:,} |
| KEEP | {sum(v for k,v in counts.items() if k.startswith('KEEP')):,} | {sum(x['bytes'] for x in rows if x['decision'].startswith('KEEP')):,} |
| ASK | {len(asks):,} | {sum(x['bytes'] for x in asks):,} |

Destination: `{DATA}/<original repo-relative path>`, accessed using `GREEK_OCR_DATA_ROOT` or hash-checked receipt lookup. {len(empty):,} directories become empty in the proposed plan. {len(reader_targets):,} code/test source files have literal basename references to MOVE candidates; pair-level fixes are in READERS_TO_UPDATE.tsv. Basename collisions, producer-only references and dynamic directory consumers need execution-time review; these are not all proven read failures.

Lead receipts: {len(receipt_rows):,} per-file rows reconciled, {sum('tracked here' in r[-1] for r in receipt_rows):,} current HEAD matches, {len(conflicts):,} byte/hash conflicts. Other-worktree custody items are not included in MOVE totals. Segmentation's five tracked large artifacts retain their exact required hashes. The bundle header was read; its bundled head is absent from the local Git object database. Preserve the bundle itself. candidate_order_KEEP and SEGEVAL1.bundle will be missing to unchanged historical s1–s4/gate_rereport/gate03 part-3 scope guards; use a new receipt-backed replay adapter without altering those records.

Open questions before any move:

- Decide the following ASK paths (stored symlink text is hashed; external/dangling targets are not copied):
'''+''.join(f'  - `{x["path"]}` — {x["reason"]}\n' for x in asks)+f'''
- Reconcile the {len(conflicts):,} same-path HEAD/lead-receipt byte/hash conflicts listed in RECEIPT_CONFLICTS.tsv. Preserve both versions and settle versioned custody before copying to a shared destination.
- Confirm retention of the lead-mandated 1.7 MB census evidence and the explicitly marked small referenced test fixtures versus a stricter no-bulk-in-git reading. The plan declares these exceptions rather than silently contradicting the lead.
- Confirm retrievable custody at the new root for lead-only paths: spellcheck outputs/READBACK_RECEIPT, six small-segment outputs, and 3,460 pilot receipts. Their source-worktree receipts are inputs, not proof of a completed transfer.
- Review literal-reference candidates and dynamic directory/relative HTML consumers; implement receipt/data-root resolution before relocation. No consumer patch was made here.
- Choose ≤5 MB receipt shards or compression for oversized planning outputs before tracking them. Keep the proposed guard outside tests until the approved execution change; preserve historical evidence unchanged.
- Establish durable external custody and rollback before untracking SEGEVAL1.bundle, frozen LQB truth and sampling/census keys. No destination capacity, copy, move or durability check has been performed.

Deliverables: MOVE_PLAN.tsv, MOVE_PLAN.md, size_guard_test.py, .gitignore.proposed and this SUMMARY.md. Supporting tables record bulk-directory metrics, empty directories, reader fixes and receipt reconciliation. Collector scripts and snapshot/grep caches make the analysis reproducible; they are analysis outputs, not installed repository behavior.
'''
(O/'SUMMARY.md').write_text(summary)
print(json.dumps(audit,indent=2))

# Validation is performed by validate_plan.py after rendering.
