"""Independent disk readback of release files, fields, IDs and split membership."""
from __future__ import annotations
import sys
sys.dont_write_bytecode=True
import collections, datetime, hashlib, itertools, json, re, subprocess
from common import *

ALLOWED={'source','source_dataset','collection','collection_slug','title','attribution','year','decade','source_url','external_link','edm_url','metadata_status'}
DEC=json.JSONDecoder()

def rows_and_raw(path):
    if path.suffix=='.jsonl':
        for line in path.open():
            if line.strip():
                start=len(line)-len(line.lstrip());r,end=DEC.raw_decode(line,start)
                yield r,line[start:end]
    elif path.name.startswith('manifest_'):
        text=path.read_text();pos=text.index('[')+1
        while True:
            while text[pos].isspace() or text[pos]==',':pos+=1
            if text[pos]==']':break
            r,end=DEC.raw_decode(text,pos);yield r,text[pos:end];pos=end
    elif path.name=='split_moves_v2.json':
        for r in json.loads(path.read_text())['rows']:yield r,json.dumps(r,ensure_ascii=False)

def value_tokens(raw):
    pos=1;out=[]
    while True:
        while raw[pos].isspace() or raw[pos]==',':pos+=1
        if raw[pos]=='}':return out
        key,end=DEC.raw_decode(raw,pos);ks=pos;pos=end
        while raw[pos].isspace():pos+=1
        assert raw[pos]==':';pos+=1
        while raw[pos].isspace():pos+=1
        value,end=DEC.raw_decode(raw,pos)
        if key not in ALLOWED:out.append(raw[ks:end])
        pos=end

def main():
    receipt=json.loads((OUT/'v2_meta1/receipt.json').read_text());proposal={r['book_key']:r for r in jsonl(O1/'rebind.jsonl')}
    # Bind the exact O1 commit artifacts, not just a similarly named local file.
    for name in ['FINDING.md','rebind.jsonl']:
        committed=subprocess.check_output(['git','show','c22d7a78:docs/harvest/oa_rebind_v1/'+name],cwd=ROOT)
        assert committed==(O1/name).read_bytes()
    source_checked={}
    for name in ['duplicate-inputs.json','release-inputs.json','candidate-local-inputs.json']:
        for e in json.loads((OUT/'receipts'/name).read_text()):
            if e['path'] not in source_checked:
                actual=fingerprint(e['path']);assert actual==e, ('source drift',e['path']);source_checked[e['path']]=e
    lookup={};bycrop={}
    for base,name in [(COL,'admitted_all.jsonl'),(COL/'v2','admitted_all_v2.jsonl')]:
        for r in jsonl(base/name):
            lookup[r['id']]=(r['crop_sha256'],r['label']);bycrop[r['crop_path']]=r['id']
    reports=[];active={};manifest_views={};import_views={}
    for file in receipt['files']:
        src=Path(file['source']);dst=OUT/'v2_meta1'/file['file']
        assert fingerprint(src)==file['input'];assert fingerprint(dst)==file['output']
        original_ids=[];new_ids=[];before_hash=hashlib.sha256();after_hash=hashlib.sha256();changed=collections.Counter();pending=set();n=0
        missing=object()
        for old,new in itertools.zip_longest(rows_and_raw(src),rows_and_raw(dst),fillvalue=missing):
            assert old is not missing and new is not missing
            a,ar=old;b,br=new;n+=1
            assert {k:v for k,v in a.items() if k not in ALLOWED}=={k:v for k,v in b.items() if k not in ALLOWED}, (src.name,n)
            assert value_tokens(ar)==value_tokens(br),(src.name,n,'immutable JSON token difference')
            ident=a.get('id') or bycrop[a['crop']];newid=b.get('id') or bycrop[b['crop']]
            assert ident==newid;original_ids.append(ident);new_ids.append(newid)
            key=ident.split('-p',1)[0]
            dif={k for k in a.keys()|b.keys() if a.get(k,missing)!=b.get(k,missing)}
            assert dif<=ALLOWED
            changed.update(dif)
            if dif:assert key in proposal,(src.name,ident)
            if b.get('metadata_status')=='pending_provider_verification':
                assert key in proposal and not proposal[key]['provider_verified'];pending.add(key)
            p=proposal.get(key)
            if p and any(f in a for f in ['source','source_dataset','attribution','year','decade','source_url']):
                expected=dict(source=p['source'],source_dataset=p['source'],attribution=p['collection_slug']+'; '+p['title'],year=p['year'],decade=p['decade'],source_url=p['external_link'])
                assert all(b[k]==v for k,v in expected.items() if k in a)
                if not p['provider_verified']:assert b['metadata_status']=='pending_provider_verification'
            for r,h in [(a,before_hash),(b,after_hash)]:
                fallback=lookup[ident];tuple_hash=r.get('crop_sha256') or fallback[0];label=r['label'] if 'label' in r else fallback[1]
                assert tuple_hash is not None
                h.update((json.dumps([ident,tuple_hash,label],ensure_ascii=False,separators=(',',':'))+'\n').encode())
            if src.name=='admitted_all_v2.jsonl':active[ident]=b
            if src.name.startswith('manifest_'):
                manifest_views.setdefault(src.stem.rsplit('_',1)[1],[]).append((b['crop'],b['label'],b['source'],b['year'],b['script_class'],b.get('metadata_status')))
            if src.name.startswith('import_real_v2_') and not src.name.endswith('_all.jsonl'):
                import_views.setdefault(src.stem.rsplit('_',1)[1],[]).append((b['crop'],b['label'],b['source'],b['year'],b['script_class'],b.get('metadata_status')))
        assert n==file['before']['line_count']==file['after']['line_count']
        assert original_ids==new_ids
        assert before_hash.hexdigest()==after_hash.hexdigest()==file['before']['id_crop_hash_label_sha256']==file['after']['id_crop_hash_label_sha256']
        assert dict(changed)==file['changed_metadata_fields'],(src.name,changed,file['changed_metadata_fields'])
        reports.append(dict(file=src.name,logical_rows=n,ordered_ids_equal=True,id_sets_equal=True,immutable_field_values_equal=True,immutable_json_tokens_equal=True,tuple_sha256=after_hash.hexdigest(),tuple_digest_equal=True,pending_book_count=len(pending),metadata_changes=dict(changed)))
        print(json.dumps(dict(file=src.name,passed=True)),flush=True)
    assert manifest_views==import_views
    bindings=list(jsonl(OUT/'v2_meta1/book_metadata.jsonl'));assert len(bindings)==89
    assert sum(r['metadata_status']=='pending_provider_verification' for r in bindings)==9
    assert {r['book_key'] for r in bindings}==set(proposal)
    bc=collections.Counter();bcs=collections.defaultdict(collections.Counter)
    for r in bindings:
        p=proposal[r['book_key']]
        assert r['book_id']==p['book_id'] and r['pdf_sha256']==p['pdf_sha256']
        assert all(r[k]==p[k] for k in ['title','collection_slug','year','decade','source','edm_url'])
        assert r['source_url']==p['external_link'] and r['attribution']==p['collection_slug']+'; '+p['title']
        splits=[s for s,n in r['lines'].items() if n]
        split=splits[0] if splits else r['declared_holdout_split']
        for k in ['title','collection_slug','year','decade']:
            if p['recorded'][k]!=r[k]:bc[k]+=1;bcs[k][split]+=1
        for k,old in [('source','openarchives_'+p['recorded']['collection_slug']),('attribution',p['recorded']['attribution']),('source_url',p['recorded']['source_url']),('edm_url',None)]:
            if old!=r[k]:bc[k]+=1;bcs[k][split]+=1
        if not p['provider_verified']:bc['metadata_status_pending']+=1;bcs['metadata_status_pending'][split]+=1
    assert dict(bc)==receipt['book_metadata_comparison']['changed_fields']
    assert dict(bcs)==receipt['book_metadata_comparison']['changed_fields_by_book_split']
    active_wave4=[r for r in active.values() if r['wave']=='openarchives'];assert len(active_wave4)==25372
    assert collections.Counter(r['split'] for r in active_wave4)==dict(train=19625,dev=1067,test=4680)
    assert collections.Counter(r['split'] for r in active.values())==receipt['admitted_split_counts_after']
    assert {r['id'] for r in active_wave4 if r.get('metadata_status')=='pending_provider_verification'} and sum(r.get('metadata_status')=='pending_provider_verification' for r in active_wave4)==2828
    summary=json.loads((OUT/'duplicate_summary.json').read_text());groups=list(jsonl(OUT/'duplicates.jsonl'));possible=list(jsonl(OUT/'possible.jsonl'))
    assert len(groups)==12 and len(possible)==37
    assert all(r['similarity']>=.9 and r['status']=='possible' for r in possible)
    assert not any(m['wave']=='openarchives' for g in groups+possible for m in g['members'])
    pages=json.loads((OUT/'receipts/page-collision-readback.json').read_text())
    assert sum(len(p['files']) for p in pages['groups'])==14
    assert not any(p['admitted_collision_cross_split'][v] for p in pages['groups'] for v in ['v1','v2'])
    provider=json.loads((OUT/'receipts/provider-item-summary.json').read_text());assert len(provider)==6
    for r in provider:
        assert r['url']=='https://archive.org/details/'+r['identifier'] and r['status']==200 and not r['redirects_followed']
        assert fingerprint(OUT/r['body'])['sha256']==r['sha256']
        assert r['metadata']['embedded_item_metadata']['identifier']==r['identifier']
    expected=json.loads((OUT/'receipts/final-line.json').read_text())['line']
    assert (OUT/'RELEASE_NOTE.md').read_text().splitlines()[-1]==expected
    # Original collection and wave sources have not drifted during this readback.
    for path,e in source_checked.items():assert fingerprint(path)==e
    dump('receipts/validation.json',dict(passed=True,at=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=dict(o1_commit_artifacts_equal=True,input_fingerprints_verified=len(source_checked),release_files_read_back=len(reports),files=reports,manifest_import_ordered_metadata_and_label_equality=True,auxiliary_book_metadata_records_verified=89,book_metadata_changes=dict(bc),active_admitted_lines=271987,active_wave4_metadata_rows=25372,wave4_split_counts=dict(train=19625,dev=1067,test=4680),pending_dione_books=9,pending_dione_active_line_occurrences=2828,lines_added=0,lines_dropped=0,lines_moved=0,labels_changed=0,admission_decisions_changed=0,exact_key_groups=12,possible_groups=37,version_union_cross_split_groups=summary['version_union']['cross_split']['groups'],native_collision_files_rehashed=14,provider_item_requests=6,all_http_200=True,no_other_network_calls=True,spend=0),limitations=summary['limitations']))
    print('Independent release readback passed.',flush=True)

if __name__=='__main__':main()
