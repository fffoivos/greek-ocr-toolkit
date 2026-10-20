"""Stage, but never apply, a reader patch against current concurrent tests."""
import ast,collections,csv,difflib,hashlib,json,subprocess
from pathlib import Path
import scan_live_v2 as scan
O=Path(__file__).resolve().parent;R=O.parents[2]
csv.field_size_limit(100_000_000)
move={r['path'] for r in csv.DictReader((O/'MOVE_PLAN_v2.tsv').open(),delimiter='\t') if r['decision']=='MOVE'}
scan.LIVE=('tests',);sites=scan.scan(move)
(O/'test_current_sites_v2.json').write_text(json.dumps(sites,indent=2)+'\n')
details=json.loads((O/'reader_sites_v2.json').read_text());loaders={(d['reader'],d['function']) for d in details if d['mode']=='shared input loader'}
groups=collections.defaultdict(list)
for s in sites:
    name=s['reader'];text,tree,_,imports=scan.parsed(name)
    node=next((n for n in ast.walk(tree) if isinstance(n,ast.Call) and n.lineno==s['line'] and scan.input_arg(n) is not None and [scan.input_arg(n).lineno,scan.input_arg(n).col_offset]==s['start'] and [scan.input_arg(n).end_lineno,scan.input_arg(n).end_col_offset]==s['end']),None)
    provider=None
    if node:
        f=node.func
        if isinstance(f,ast.Name):provider=imports.get(f.id,(name,f.id))
        elif isinstance(f,ast.Attribute) and isinstance(f.value,ast.Name) and f.value.id in imports:
            mod,var=imports[f.value.id]
            if var is None:provider=(mod,f.attr)
    if provider not in loaders:groups[name].append(s)
diffs=[];hashes=[]
for name,ss in sorted(groups.items()):
    original=(R/name).read_text();lines=original.splitlines(True);data=original.encode();ranges=set()
    def off(a,b):return sum(len(l.encode()) for l in lines[:a-1])+b
    for s in ss:
        a,b=off(*s['start']),off(*s['end']);assert data[a:b].decode()==s['expression'];ranges.add((a,b))
    ranges=[(a,b) for a,b in ranges if not any(c<=a and b<=d and (a,b)!=(c,d) for c,d in ranges)]
    for a,b in sorted(ranges,reverse=True):data=data[:a]+b'_data_input('+data[a:b]+b')'+data[b:]
    new=data.decode();tree=ast.parse(new);insert=0
    if tree.body and isinstance(tree.body[0],ast.Expr) and isinstance(tree.body[0].value,ast.Constant) and isinstance(tree.body[0].value.value,str):insert=tree.body[0].end_lineno
    for n in tree.body:
        if isinstance(n,ast.ImportFrom) and n.module=='__future__':insert=n.end_lineno
    lines=new.splitlines(True);lines.insert(insert,'from greekocr.ops.data_root import input_path as _data_input\n');new=''.join(lines);ast.parse(new)
    diffs.append(''.join(difflib.unified_diff(original.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name)))
    hashes.append((name,hashlib.sha256(original.encode()).hexdigest(),len(ranges)))
    details.extend(dict(reader=name,line=s['line'],mode='current tests handoff',paths=s['paths']) for s in ss)
(O/'CLEAN4T_READER_HANDOFF_v2.diff').write_text(''.join(diffs));(O/'reader_sites_v2.json').write_text(json.dumps(details,indent=2)+'\n')
with (O/'HANDOFF_TEST_HASHES_v2.tsv').open('w',newline='') as f:
    w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['test_file','current_sha256','staged_input_sites']);w.writerows(hashes)
subprocess.run(['git','apply','--check',str(O/'CLEAN4T_READER_HANDOFF_v2.diff')],cwd=R,check=True)
print('Read-only git apply --check passed;',len(groups),'test files staged, no test file edited')
