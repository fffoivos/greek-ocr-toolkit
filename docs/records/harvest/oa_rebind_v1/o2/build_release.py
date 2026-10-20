"""Apply O1 metadata to copies, preserving all other original JSON tokens."""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
import collections, datetime, hashlib, json, re, shutil
from common import *

META = {'collection','collection_slug','source','source_dataset','title','attribution','year','decade','source_url','external_link','edm_url','metadata_status'}
DEC = json.JSONDecoder()

def book_comparison(proposal):
    totals=collections.Counter();by_split=collections.defaultdict(collections.Counter)
    for p in proposal.values():
        assigned=[s for s,n in p['admitted_lines']['v2'].items() if n]
        assert len(assigned)<=1
        split=assigned[0] if assigned else p['declared_holdout_split']
        assert split in SPLITS
        pairs={k:(p['recorded'][k],p[k]) for k in ['collection_slug','title','year','decade']}
        pairs.update(source=('openarchives_'+p['recorded']['collection_slug'],p['source']),attribution=(p['recorded']['attribution'],p['collection_slug']+'; '+p['title']),source_url=(p['recorded']['source_url'],p['external_link']),edm_url=(None,p['edm_url']))
        for k,(old,new) in pairs.items():
            if old!=new:totals[k]+=1;by_split[k][split]+=1
        if not p['provider_verified']:
            totals['metadata_status_pending']+=1;by_split['metadata_status_pending'][split]+=1
    return dict(baseline_books=89,release_books=89,book_id_set_equal=True,pdf_hashes_equal=True,changed_fields=dict(totals),changed_fields_by_book_split={k:dict(v) for k,v in by_split.items()},split_basis='Current admitted split, or declared split for the single empty holdout; book records are not added training lines.')

def fields(raw):
    """Top-level field spans, with byte-identical JSON spelling available for QA."""
    pos=1; out={}
    while True:
        while raw[pos].isspace() or raw[pos]==',':pos+=1
        if raw[pos]=='}':break
        key, end=DEC.raw_decode(raw,pos);key_start=pos;pos=end
        while raw[pos].isspace():pos+=1
        assert raw[pos]==':';pos+=1
        while raw[pos].isspace():pos+=1
        start=pos;value,end=DEC.raw_decode(raw,pos)
        assert key not in out
        out[key]=(start,end,raw[key_start:start],value)
        pos=end
    return out

def row_identity(r, bycrop, byid):
    if r.get('id'):
        return r['id']
    if r.get('crop') or r.get('crop_path'):
        crop=r.get('crop') or r['crop_path']
        assert crop in bycrop, crop
        return bycrop[crop]
    return None

def patch(raw, r, proposal, idmap):
    line_id=r.get('id')
    if not line_id and (r.get('crop') or r.get('crop_path')):
        line_id=idmap[r.get('crop') or r['crop_path']]
    if not line_id:return raw,{},None
    key=line_id.split('-p',1)[0]
    # Prefix matching is never sufficient: the exact ID/crop was bound to wave 4.
    if key not in proposal:return raw,{},line_id
    p=proposal[key]
    if r.get('wave') is not None:assert r['wave']=='openarchives'
    if r.get('book_key') is not None:assert r['book_key']==key
    if r.get('doc') is not None:assert r['doc']=='openarchives:'+key
    expected=dict(source='openarchives_'+p['recorded']['collection_slug'],source_dataset='openarchives_'+p['recorded']['collection_slug'],
      collection=p['recorded']['collection_slug'],collection_slug=p['recorded']['collection_slug'],
      title=p['recorded']['title'],attribution=p['recorded']['attribution'],year=p['recorded']['year'],decade=p['recorded']['decade'],source_url=p['recorded']['source_url'])
    values=dict(source=p['source'],source_dataset=p['source'],collection=p['collection_slug'],collection_slug=p['collection_slug'],
      title=p['title'],attribution=p['collection_slug']+'; '+p['title'],year=p['year'],decade=p['decade'],source_url=p['external_link'],external_link=p['external_link'],edm_url=p['edm_url'])
    # Decision-only files (e.g. relabel audit) retain their schema and raw bytes.
    has_metadata=any(k in r for k in values)
    changes={}
    for k,v in values.items():
        if k not in r:continue
        if k in expected:assert r[k]==expected[k], (line_id,k,r[k],expected[k])
        if r[k]!=v:changes[k]=v
    if has_metadata and not p['provider_verified']:
        assert p['collection_slug']=='Dione'
        changes['metadata_status']='pending_provider_verification'
    if not changes:return raw,{},line_id
    spans=fields(raw);edits=[]
    for k,v in changes.items():
        encoded=json.dumps(v,ensure_ascii=False,allow_nan=False)
        if k in spans:
            a,b,_,_=spans[k];edits.append((a,b,encoded))
        else:
            assert k=='metadata_status'
            at=raw.rfind('}')
            edits.append((at,at,', '+json.dumps(k)+': '+encoded))
    new=raw
    for a,b,v in sorted(edits,reverse=True):new=new[:a]+v+new[b:]
    nr=json.loads(new)
    assert {k:v for k,v in r.items() if k not in META}=={k:v for k,v in nr.items() if k not in META}
    # Compare lexical key/value tokens for every immutable field, not just values.
    ns=fields(new)
    assert [(k,prefix,raw[a:b]) for k,(a,b,prefix,v) in spans.items() if k not in META]==[(k,prefix,new[a:b]) for k,(a,b,prefix,v) in ns.items() if k not in META]
    return new,changes,line_id

class Check:
    def __init__(self,name,lookup,bycrop,assignment):
        self.name=name;self.lookup=lookup;self.bycrop=bycrop;self.assignment=assignment
        self.n=0;self.ids=[];self.splits=collections.Counter();self.raw_splits=collections.Counter();self.tuples=hashlib.sha256();self.immutable=hashlib.sha256();self.hash_missing=0;self.joined_hash=0;self.joined_label=0
    def add(self,r,raw):
        self.n+=1
        ident=row_identity(r,self.bycrop,self.lookup)
        assert ident is not None, (self.name,r)
        self.ids.append(ident)
        fallback=self.lookup.get(ident,{})
        crop_hash=r.get('crop_sha256') or fallback.get('crop_sha256')
        if not r.get('crop_sha256') and crop_hash:self.joined_hash+=1
        if not crop_hash:self.hash_missing+=1
        label=r.get('label',fallback.get('label'))
        if 'label' not in r:self.joined_label+=1
        self.tuples.update((json.dumps([ident,crop_hash,label],ensure_ascii=False,separators=(',',':'))+'\n').encode())
        for k,(a,b,prefix,v) in fields(raw).items():
            if k not in META:
                self.immutable.update((k+'\0'+prefix+raw[a:b]+'\0').encode())
        self.immutable.update(b'\n')
        if 'split' in r:self.raw_splits[str(r['split'])]+=1
        # The split-specific file is authoritative for export views. Historical
        # dropped/relabel/move logs use their original or joined split explicitly.
        m=re.search(r'(?:manifest_v2_|import_real_v2_)(train|dev|test)\.',self.name)
        split=m[1] if m else r.get('split')
        if split is None:split=self.assignment.get(ident, fallback.get('split'))
        split={'reserved':'test','val':'dev'}.get(split,split)
        self.splits[str(split)]+=1
    def result(self):
        return dict(line_count=self.n,unique_line_ids=len(set(self.ids)),per_split_counts=dict(self.splits),recorded_split_values=dict(self.raw_splits),id_crop_hash_label_sha256=self.tuples.hexdigest(),immutable_json_tokens_sha256=self.immutable.hexdigest(),missing_crop_hashes=self.hash_missing,joined_crop_hashes=self.joined_hash,joined_labels=self.joined_label)

def run_file(src,dst,proposal,lookup,bycrop,assign):
    name=src.name;before=Check(name,lookup,bycrop,assign);after=Check(name,lookup,bycrop,assign)
    changed=collections.Counter();changed_splits=collections.defaultdict(collections.Counter);changed_ids=set();new_pending=set()
    def convert(raw):
        r=json.loads(raw);before.add(r,raw)
        new,ch,ident=patch(raw,r,proposal,bycrop)
        nr=json.loads(new);after.add(nr,new)
        if ch:
            changed_ids.add(ident)
            s=assign.get(ident,lookup.get(ident,{}).get('split'))
            for k in ch:changed[k]+=1;changed_splits[k][str(s)]+=1
            if 'metadata_status' in ch:new_pending.add(ident)
        return new
    if src.suffix=='.jsonl':
        with src.open() as fi, dst.open('w') as fo:
            for line in fi:
                if not line.strip():fo.write(line);continue
                # Keep each line's whitespace and original newline spelling.
                start=len(line)-len(line.lstrip());obj,end=DEC.raw_decode(line,start)
                fo.write(line[:start]+convert(line[start:end])+line[end:])
    elif name.startswith('manifest_'):
        raw=src.read_text();out=[];pos=0
        assert raw.lstrip().startswith('[')
        pos=raw.index('[')+1;last=0
        while True:
            while raw[pos].isspace() or raw[pos]==',':pos+=1
            if raw[pos]==']':break
            r,end=DEC.raw_decode(raw,pos)
            out.append(raw[last:pos]);out.append(convert(raw[pos:end]));pos=end;last=end
        out.append(raw[last:]);dst.write_text(''.join(out))
    elif name=='split_moves_v2.json':
        # This is an immutable historical decision log, not a current split map.
        raw=src.read_text();obj=json.loads(raw)
        for r in obj['rows']:
            rr=json.dumps(r,ensure_ascii=False);before.add(r,rr);after.add(r,rr)
        shutil.copyfile(src,dst)
    else:
        shutil.copyfile(src,dst)
    a,b=before.result(),after.result()
    assert a==b, (name,a,b)
    assert before.ids==after.ids
    def physical_lines(path):
        with path.open('rb') as f:return sum(1 for _ in f)
    return dict(file=name,source=str(src),input=fingerprint(src),output=fingerprint(dst),before=a,after=b,physical_lines_before=physical_lines(src),physical_lines_after=physical_lines(dst),line_id_set_equal=set(before.ids)==set(after.ids),line_id_order_equal=before.ids==after.ids,line_id_multiset_equal=collections.Counter(before.ids)==collections.Counter(after.ids),lines_added=0,lines_dropped=0,lines_moved=0,changed_metadata_rows=len(changed_ids),changed_metadata_fields=dict(changed),changed_metadata_fields_by_split={k:dict(v) for k,v in changed_splits.items()},pending_line_occurrences=len(new_pending),historical_unchanged=name in ['CLEAN_REPORT.md','validation_v2.json','split_moves_v2.json'])

def main():
    assert (OUT/'duplicate_summary.json').is_file(), 'Part 1 must finish before release construction.'
    inputs=Inputs();proposal={r['book_key']:r for r in inputs.rows(O1/'rebind.jsonl')}
    # Recheck every fingerprint used in the completed duplicate audit.
    for e in inputs.load(OUT/'receipts/duplicate-inputs.json'):
        assert fingerprint(inputs.add(e['path']))==e
    lookup={};bycrop={};assign={};v2ids=set();v2changed=set()
    for base,name in [(COL,'admitted_all.jsonl'),(COL/'v2','admitted_all_v2.jsonl')]:
        for r in inputs.rows(base/name):
            lookup[r['id']]={k:r[k] for k in ['crop_sha256','label','split','wave','book_key']}
            bycrop[r['crop_path']]=r['id']
            if base.name=='v2':
                v2ids.add(r['id']);assign[r['id']]=r['split']
                if r['wave']=='openarchives':v2changed.add(r['id'])
    # Bind legacy book id/key, old acquisition URL, metadata and actual PDF hash.
    original=inputs.load(HARVEST/'openarchives/books.json')
    assert len(original)==len(proposal)==89
    for b in original:
        p=proposal[b['key']]
        assert b['book']==p['book_id'] and b['pdf_sha256']==p['pdf_sha256'] and b['pdf_url']==p['pdf_url']
        assert all(b.get(k)==v for k,v in p['recorded'].items()), b['key']
        receipt=inputs.load(MAIN/b['download_receipt'])
        assert receipt['sha256']==p['pdf_sha256'] and receipt['bytes']==p['pdf_bytes']
    destination=OUT/'v2_meta1';destination.mkdir(exist_ok=True)
    receipts=[]
    files=sorted(p for p in (COL/'v2').iterdir() if p.is_file())
    assert len(files)==14
    for src in files:
        inputs.add(src)
        result=run_file(src,destination/src.name,proposal,lookup,bycrop,assign)
        receipts.append(result)
        print(json.dumps(dict(file=src.name,rows=result['after']['line_count'],changed=result['changed_metadata_rows'],passed=True)),flush=True)
    # Existing line schemas do not contain title/EDM fields. Publish those complete
    # book metadata bindings separately instead of expanding the trainer schema.
    binding=[]
    for p in sorted(proposal.values(),key=lambda x:x['book_key']):
        binding.append(dict(schema='o2-book-metadata-1',book_id=p['book_id'],book_key=p['book_key'],wave='openarchives',pdf_sha256=p['pdf_sha256'],collection_slug=p['collection_slug'],source=p['source'],title=p['title'],attribution=p['collection_slug']+'; '+p['title'],year=p['year'],decade=p['decade'],source_url=p['external_link'],edm_url=p['edm_url'],metadata_status='repository_verified' if p['provider_verified'] else 'pending_provider_verification',lines=p['admitted_lines']['v2'],declared_holdout_split=p['declared_holdout_split'],evidence='../../rebind.jsonl#'+p['book_key']))
    write_jsonl('v2_meta1/book_metadata.jsonl',binding)
    active=next(r for r in receipts if r['file']=='admitted_all_v2.jsonl')
    receipt=dict(schema='collection-v2-meta1-receipt-1',created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_version='collection v2 strict',release='collection v2-meta1',source_directory=str(COL/'v2'),copied_source_files=14,files=receipts,
      tuple_encoding='Concatenated compact UTF-8 JSON arrays [legacy line id,crop SHA256,label] followed by LF in original row order. Missing fields in views join by exact line ID or crop path to admitted_all_v2, falling back to admitted_all v1 for historical drop/relabel/move logs.',
      empty_log_encoding='Files with no line rows (historical summary/report) have zero logical rows and SHA256 of empty bytes; physical file hashes remain recorded.',
      invariant='All original non-metadata JSON key/value token spellings and order are preserved, including ID, crop path/hash, every label, admission and split decisions.',
      schema_policy='All existing field sets retained; only pending Dione line metadata adds metadata_status. Complete true titles, collection and EDM links are in book_metadata.jsonl, since the trainer row schema omits these fields.',
      unique_admitted_rows_changed=active['changed_metadata_rows'],admitted_rows_changed_by_field=active['changed_metadata_fields'],admitted_rows_changed_by_field_and_split=active['changed_metadata_fields_by_split'],admitted_split_counts_before=active['before']['per_split_counts'],admitted_split_counts_after=active['after']['per_split_counts'],
      lines_added=0,lines_dropped=0,lines_moved=0,labels_changed=0,crop_paths_changed=0,crop_hashes_changed=0,ids_changed=0,admission_decisions_changed=0,
      pending_provider_books=[p['book_key'] for p in binding if p['metadata_status']=='pending_provider_verification'],
      book_metadata=dict(path='book_metadata.jsonl',books=len(binding),pending_provider_verification=sum(p['metadata_status']=='pending_provider_verification' for p in binding),sha256=fingerprint(destination/'book_metadata.jsonl')['sha256']),
      book_metadata_comparison=book_comparison(proposal),
      original_pipeline_metadata_promoted=False,rights_changed=False,source_caps_reapplied=False,network_requests=0,spend=0,passed=True)
    assert len(receipt['pending_provider_books'])==9
    assert receipt['unique_admitted_rows_changed']==25372
    assert active['after']['missing_crop_hashes']==0
    dump('v2_meta1/receipt.json',receipt)
    inputs.finish('receipts/release-inputs.json')

if __name__=='__main__':main()
