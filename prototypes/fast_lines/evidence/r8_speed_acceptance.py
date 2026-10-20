"""Offline source-bound speed comparison; no runtime imports or inference."""
import hashlib
import json
from pathlib import Path


ROOT=Path('.astra/fast_lines/out/round8')
OUT=ROOT/'R8-04-i1'
BASE=ROOT/'R8-03-i1'
PRIOR=ROOT/'R8-03-i2'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path,value):
    Path(path).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')


def strip_times(value):
    if isinstance(value,dict):
        return {k:strip_times(v) for k,v in value.items()
                if not k.endswith('_s') and k not in ('seconds','elapsed','timing','stages')}
    if isinstance(value,list):return [strip_times(v) for v in value]
    return value


def run():
    manifest=ROOT/'R8-01b/inputs-208.json'
    pages=json.loads(manifest.read_text())['pages']
    pilots_path=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-model/.astra/fast_lines/out/round8/R8-01/inputs.json')
    pilots={p['page'] for p in json.loads(pilots_path.read_text())['pages']}
    records=[]
    for row in pages:
        p=row['page'];a=BASE/'runtime'/f'{p}.json';b=OUT/'runtime'/f'{p}.json'
        aa=BASE/'runtime'/f'{p}.evidence.json';bb=OUT/'runtime'/f'{p}.evidence.json'
        old=json.loads(a.read_text());new=json.loads(b.read_text())
        oe=json.loads(aa.read_text());ne=json.loads(bb.read_text())
        differences=[k for k in set(oe)|set(ne) if k not in ('timing','stages','seconds') and not k.endswith('_s') and strip_times(oe.get(k))!=strip_times(ne.get(k))]
        records.append(dict(page=p,input_sha256=row['sha256'],input_verified=sha(row['path'])==row['sha256'],
            baseline_sha256=sha(a),candidate_sha256=sha(b),baseline_evidence_sha256=sha(aa),candidate_evidence_sha256=sha(bb),
            items=len(new['items']),items_equal=old['items']==new['items'],exclusions_equal=oe.get('removed')==ne.get('removed'),
            nonclock_differences=differences,pilot=p in pilots))
    assert len(records)==208 and all(r['input_verified'] and r['items_equal'] and r['exclusions_equal'] and not r['nonclock_differences'] for r in records)
    dump(OUT/'ACCEPTANCE.json',dict(baseline_commit='5961754bde92badddc14e8d403fd2a6a791eec65',baseline_runtime_equivalent='23ee49c813a02209bee144d8baedefe860bfbdf3',
        baseline_source_sha256=sha(BASE/'runtime/source.json'),candidate_source_sha256=sha(OUT/'runtime/source.json'),
        input_manifest_sha256=sha(manifest),pages=records,items=sum(r['items'] for r in records),pilots=len(pilots),
        interpretation='Every final item, exclusion and recorded non-clock feature decision is exact. This preserves inherited failures; it does not certify physical row/source correctness.'))
    for name,n in [('COMMENTS',104),('ROWS',256)]:
        records=json.loads((PRIOR/f'{name}.json').read_text());assert len(records)==n
        for r in records:
            r['r8_04_i1']=dict(prior=str((PRIOR/f'{name}.json').resolve()),prior_sha256=sha(PRIOR/f'{name}.json'),
                output=f"runtime/{r['page']}.json",items_equal=True,nonclock_evidence_equal=True,
                status='Inherited disposition; no speed-related physical change or new owner fix claimed')
        dump(OUT/f'{name}.json',records)
        lines=[f'# R8-04-i1 {name.lower()}', '',
            f'All {n} original records and prior fields are preserved verbatim in [{name}.json]({name}.json). This iteration appends equality/source lineage; prior physical verdicts are inherited. No owner fix is claimed.', '',
            f'[Prior readable ledger](../R8-03-i2/{name}.md). Exact quotes and complete status lineage remain in JSON.', '']
        for r in records:
            identity=r.get('id',r.get('segment'))
            lines += [f'## {r["page"]} / {identity}', '',
                str(r.get('owner_comment',r.get('mark',''))), '',
                'Inherited status: '+str(r.get('status','see prior record'))+'. Current export and non-clock evidence unchanged.', '']
        (OUT/f'{name}.md').write_text('\n'.join(lines))
    print('208 exports/exclusions/non-clock evidence exact; 104 comments/256 marks preserved')


if __name__=='__main__':run()
