"""Refine CLEAN3A's immutable inventory. Writes only new CLEAN3B artifacts."""
import collections,csv,hashlib,io,json,os
from pathlib import Path
from scan_live_v2 import scan
O=Path(__file__).resolve().parent; R=O.parents[2]
csv.field_size_limit(100_000_000)
BULK=set('png jpg jpeg gif webp tif tiff bmp pdf gz tgz tar zip bundle npy npz pt pth onnx bin mp4 mov wav'.split())
TEXT=set('jsonl html htm xml log codexlog txt tsv csv'.split())
LIVE=('greekocr/','scripts/','tests/','worker/','prototypes/')
with (O/'MOVE_PLAN.tsv').open() as f:
    reader=csv.DictReader(f,delimiter='\t'); fields=reader.fieldnames;rows=list(reader)
by={x['path']:x for x in rows}
sites=json.loads((O/'static_inputs_v2.json').read_text()) + json.loads((O/'static_inputs_extra_v2.json').read_text())
# Definite static input sites, plus literal portable inputs and cache-file loads.
exempt={p for s in sites for p in s['paths']}
portable=json.loads((R/'worker/planned_inputs.json').read_text())['sha256']
exempt.update('docs/harvest/collect_v3/'+p for p in portable)
exempt.update(p for p in by if p.endswith('/ink.png') and '/seg/CP' in p)
exempt.add('artifacts/labelfix_r1/binding/owner_extra_lines.jsonl.gz')
# sr1_receipts hashes the tranche6 evidence files by literal name.
exempt.add('docs/labelfix/spellcheck/R2/evidence/tranche6/letter.png')
small=[]; old={x['path']:x['decision'] for x in rows}
for x in rows:
    p=x['path'];n=int(x['bytes']);ext=Path(p).suffix[1:].lower()
    scope=p.startswith(('docs/','artifacts/','out/','legacy_l1/','fixes/')) or (p.startswith('prototypes/') and any(c in {'evidence','outputs','runs'} for c in p.split('/')[1:-1]))
    rule='a' if n>5_000_000 else 'd' if old[p]=='ASK' else 'b' if ext in BULK and scope else 'c' if n>1_000_000 and ext in TEXT and p.startswith(('docs/','artifacts/','out/')) else ''
    if rule=='b' and n<=50_000 and p in exempt:
        rule='';small.append(p);reason='KEEP: <=50,000 bytes; live literal input (see SMALL_INPUTS_v2.tsv).'
    else:reason={'a':'bytes > 5,000,000 (all paths).','b':'Bulk extension in coordinator data scope; no small live-input exception.','c':'Text/table export > 1,000,000 bytes under docs/, artifacts/ or out/.','d':'Former ASK symlink; preserve link text and mirrored parent directories, never dereference.'}.get(rule,'KEEP: no coordinator MOVE rule applies.')
    x.update(decision='MOVE' if rule else 'KEEP',reason=reason,rule=rule)
move=[x for x in rows if x['decision']=='MOVE'];keep=[x for x in rows if x['decision']=='KEEP'];mp={x['path'] for x in move}
def tsv(name,headers,data):
    with (O/name).open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(headers);w.writerows(data)
tsv('MOVE_PLAN_v2.tsv',fields+['rule'],([x[k] for k in fields+['rule']] for x in rows))
site_readers=collections.defaultdict(set)
for site in sites:
    for p in site['paths']:site_readers[p].add(site['reader'])
for p in portable:site_readers['docs/harvest/collect_v3/'+p].update({'worker/prepare.py','worker/planned_inputs.json'})
tsv('SMALL_INPUTS_v2.tsv',['path','bytes','live_readers','basis'],[(p,by[p]['bytes'],'; '.join(sorted(set(r for r in by[p]['readers'].split('; ') if r.startswith(LIVE))|site_readers[p])),'static input / portable manifest input / literal geometry cache filename') for p in sorted(small)])
links=[]
for x in move:
    if x['rule']=='d':
        text=os.readlink(R/x['path']); links.append([x['path'],text,len(os.fsencode(text)),hashlib.sha256(os.fsencode(text)).hexdigest()])
tsv('SYMLINKS_v2.tsv',['path','link_text','bytes','sha256'],links)
all_dirs=collections.defaultdict(set)
for x in rows:
    for parent in Path(x['path']).parents:
        if str(parent)!='.':all_dirs[parent.as_posix()].add(x['path'])
empty=sorted(d for d,ps in all_dirs.items() if ps<=mp)
actual=[]
for d in empty:
    # Include existing untracked files and ignored files. Never follow symlinks.
    leftovers=[]
    for base,dirs,files in os.walk(R/d,followlinks=False):
        for name in files+[n for n in dirs if (Path(base)/n).is_symlink()]:
            rel=(Path(base)/name).relative_to(R).as_posix()
            if rel not in mp:leftovers.append(rel)
    if not leftovers:actual.append(d)
tsv('EMPTY_DIRECTORIES_v2.tsv',['directory','HEAD_becomes_empty','working_tree_becomes_empty'],[[d,'yes','yes' if d in set(actual) else 'no: untracked/ignored content remains'] for d in empty])
# Receipt shards are UTF-8 byte bounded, including the header.
receipts=O/'RECEIPTS';receipts.mkdir(exist_ok=True)
header='path\tbytes\tsha256\tproducing_commit\tkind\n';chunks=[];buf=header;count=0;total=0
for x in move:
    s=io.StringIO();csv.writer(s,delimiter='\t',lineterminator='\n').writerow([x[k] for k in ('path','bytes','sha256','producing_commit','kind')]);line=s.getvalue()
    if len((buf+line).encode())>4_000_000:
        chunks.append((buf,count,total));buf=header;count=0;total=0
    buf+=line;count+=1;total+=int(x['bytes'])
if count:chunks.append((buf,count,total))
shards=[]
for i,(content,count,total) in enumerate(chunks,1):
    name=f'receipt_{i:02d}.tsv';(receipts/name).write_text(content);shards.append((name,count,total,len(content.encode()),hashlib.sha256(content.encode()).hexdigest()))
special='''SEGEVAL1.bundle is preserved as a file (147,025,055 bytes; sha256 `25c38794aacb89d083b461175471735575551f0acc4d1f612214b3e43fee1e1a`). Its header names bundled head `b3b5aaa19835ac626af6576da37e008386b26879 refs/heads/segeval1-artifacts`. Custody is the bundle bytes, not assumed availability in local history.

`candidate_order_KEEP.jsonl` and `SEGEVAL1.bundle` are referenced by historical scope guards s1–s4 / gate_rereport / gate03. Those records and scripts under docs/ remain unchanged. Historical replay needs a new receipt-backed adapter or a deliberate restored mirror; current scope-guard execution is not qualified by this plan.'''
(receipts/'INDEX.md').write_text('# CLEAN3B receipts\n\nOne row per MOVE entry, including 19 symlinks whose size/hash describe link text. Producing commits are inherited exactly from CLEAN3A (abbreviated commit IDs). HEAD bytes have custody; no lead-receipt replacement.\n\n| Shard | Entries | Payload bytes | TSV bytes | SHA256 |\n|---|---:|---:|---:|---|\n'+''.join(f'| [{n}]({n}) | {c:,} | {b:,} | {z:,} | `{h}` |\n' for n,c,b,z,h in shards)+f'\nTotal: {len(move):,} entries, {sum(int(x["bytes"]) for x in move):,} bytes. Every shard is <=4,000,000 bytes.\n\n'+special+'\n')
def totals(xs,key):
    d=collections.defaultdict(lambda:[0,0])
    for x in xs:d[key(x)][0]+=1;d[key(x)][1]+=int(x['bytes'])
    return d
stats={'MOVE':{'count':len(move),'bytes':sum(int(x['bytes']) for x in move)},'KEEP':{'count':len(keep),'bytes':sum(int(x['bytes']) for x in keep)}}
delta=[x for x in keep if old[x['path']]=='MOVE']
lines=['# CLEAN3B MOVE plan v2','', 'Authoritative input: CLEAN3A MOVE_PLAN.tsv, HEAD `ac1c38cf6ebab49ef694fffb2a8b3dc757012f33`. Decimal thresholds: 5,000,000 / 1,000,000 / 50,000 bytes. Rules are evaluated a, d, b (with exception), c. The rule column records the first applicable MOVE rule; KEEP has an empty rule. All original columns are retained verbatim except decision/reason.','', '| Decision | Count | Bytes |','|---|---:|---:|']
for decision,t in stats.items():lines.append(f'| {decision} | {t["count"]:,} | {t["bytes"]:,} |')
lines+=['',f'Small literal inputs retained by b exception: {len(small)} (SMALL_INPUTS_v2.tsv). Rule d moves only the 19 symlink entries with their mirrored parent paths; sibling files follow a/b/c. External or dangling targets are never traversed. Exact link text: SYMLINKS_v2.tsv.','']
for title,key in [('Kind',lambda x:x['kind']),('Top-level directory',lambda x:x['path'].split('/')[0]),('MOVE rule',lambda x:x['rule'] or 'KEEP')]:
    a,b=totals(move,key),totals(keep,key);lines += [f'## {title}','', '| Group | MOVE count | MOVE bytes | KEEP count | KEEP bytes |','|---|---:|---:|---:|---:|']
    for k in sorted(a.keys()|b.keys()):lines.append(f'| {k} | {a[k][0]:,} | {a[k][1]:,} | {b[k][0]:,} | {b[k][1]:,} |')
lines+=['','## Delta versus v1','',f'{len(delta):,} v1 MOVE files ({sum(int(x["bytes"]) for x in delta):,} bytes) now KEEP. All 19 v1 ASK links now MOVE.','', '| Kind | v1 MOVE -> v2 KEEP count | Bytes |','|---|---:|---:|']
for k,(c,b) in sorted(totals(delta,lambda x:x['kind']).items()):lines.append(f'| {k} | {c:,} | {b:,} |')
lines+=['','## Directories becoming empty','',f'{len(empty):,} directories lose all HEAD entries; {len(actual):,} are also empty in the current working tree after the planned removals. EMPTY_DIRECTORIES_v2.tsv records both. Actual deletion uses rmdir only and never removes untracked content.','']
lines.extend(f'- `{d}`'+(' (untracked/ignored content remains)' if d not in set(actual) else '') for d in empty)
lines+=['','## Special custody cases','',special,'']
(O/'MOVE_PLAN_v2.md').write_text('\n'.join(lines))
# Ignore cannot encode byte thresholds. Use scoped bulk/export extensions for
# new/untracked data, preserve small live bulk inputs with exact negations, and
# name oversized source/JSON files individually. All retained tracked files stay
# tracked; no .md/.py/.sh/.js/.css/.toml/.mmd pattern is introduced.
patterns=[];covered=set()
for top in sorted({p.split('/')[0] for p in mp}):
    for ext in sorted({Path(p).suffix for p in mp if p.startswith(top+'/')}):
        eligible=ext[1:].lower() in BULK or (top in {'docs','artifacts','out'} and ext[1:].lower() in TEXT)
        if not eligible:continue
        if top in {'greekocr','scripts','tests','worker','config','collect_v3','seed'}:continue
        paths={p for p in mp if p.startswith(top+'/') and Path(p).suffix==ext}
        if not paths:continue
        if top=='prototypes':
            # Only the three coordinator data scopes, not prototype source data.
            for folder in ('evidence','outputs','runs'):
                group={p for p in paths if folder in p.split('/')[1:-1]}
                if group:patterns.append('/prototypes/**/'+folder+'/**/*'+ext);covered.update(group)
        else:patterns.append('/'+top+'/**/*'+ext);covered.update(paths)
patterns.extend('/'+p for p in sorted(mp-covered))
patterns.extend('!/'+p for p in sorted(small))
patterns.append('/docs/cleanup_20261019/data_out/MOVE_PLAN_v2.tsv')
assert len(patterns)<=299,len(patterns)
(O/'gitignore_additions_v2.txt').write_text('# CLEAN3B additions: scoped data extensions; byte thresholds are not expressible in gitignore.\n# KEEP files remain tracked. Small live bulk inputs are explicitly excepted below.\n'+'\n'.join(patterns)+'\n')
(O/'metrics_v2.json').write_text(json.dumps(dict(stats=stats,rules={k:v for k,v in totals(move,lambda x:x['rule']).items()},small=small,empty_HEAD=len(empty),empty_working_tree=len(actual),delta_count=len(delta),delta_bytes=sum(int(x['bytes']) for x in delta),delta_kind=totals(delta,lambda x:x['kind']),shards=shards,ignore_patterns=len(patterns)),indent=2)+'\n')
print(json.dumps(stats));print('small',len(small),'shards',len(shards),'patterns',len(patterns))
