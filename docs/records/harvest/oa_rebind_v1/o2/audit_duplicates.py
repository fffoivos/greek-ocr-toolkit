"""First phase: inventory corrected book identities and exact/possible duplicate keys."""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
import collections, datetime, difflib, html, itertools, json, re, unicodedata
from urllib.parse import unquote, urlsplit
from common import *

def normal_title(s):
    s = unicodedata.normalize('NFC', html.unescape(s or '')).casefold()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if not unicodedata.combining(c))
    return ' '.join(''.join(c if c.isalnum() else ' ' for c in s).split())

def canonical_url(s):
    s = unicodedata.normalize('NFC', html.unescape(s or '')).strip()
    return re.sub(r'%[0-9a-fA-F]{2}', lambda m: unquote(m[0]) if unquote(m[0]) in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~' else m[0].upper(), s)

def provider_key(s):
    """Only item-level aliases; handles have global namespaces. No PDF basenames."""
    if not s:
        return None
    if s.startswith('/metadata/'):
        s = 'https://anemi.lib.uoc.gr'+s
    u = urlsplit(html.unescape(s))
    if not u.netloc:
        return None
    host = u.hostname.lower()
    path = unicodedata.normalize('NFC', unquote(u.path)).rstrip('/')
    if host == 'hdl.handle.net':
        return 'handle:'+path.lstrip('/')
    m = re.search(r'/(?:bitstream/)?handle/([^/]+/[^/]+)', path)
    if m:
        if m[1].startswith('123456789/'):
            return 'repository-handle:'+host+':'+m[1]
        return 'handle:'+m[1]
    if host.endswith('archive.org'):
        m = re.search(r'/(?:details|download)/([^/]+)', path)
        if m: return 'ia:'+m[1]
    if host == 'anemi.lib.uoc.gr' and path.startswith('/metadata/') and path.endswith('.tkl'):
        return 'anemi:'+path
    if host == 'pergamos.lib.uoa.gr':
        m = re.search(r'/uoa/dl/object/(?:uoadl:)?(\d+)', path)
        if m: return 'pergamos:'+m[1]
    if host.endswith('wikisource.org') and '/wiki/' in path:
        # Pages are never used as book keys; use index_url/book instead.
        if re.search(r'/wiki/(?:Σελίδα|Page|Страница):', path, re.I):return None
        return 'item:'+host+path.replace(' ', '_')
    if host == 'www.openarchives.gr' and '/edm/' in path:
        return 'edm:'+path.split('/edm/',1)[1]
    if path and not re.search(r'\.(?:pdf|png|jpe?g|djvu)$', path, re.I):
        # Preserve the full query; unrelated repository IDs are never equated.
        return 'item:'+host+path+('?' + u.query if u.query else '')
    return None

def main():
    inputs = Inputs()
    rb = {r['book_key']:r for r in inputs.rows(O1/'rebind.jsonl')}
    assert len(rb)==89
    # Revalidate every O1 source fingerprint and the pinned HF table before use.
    old_checks=[]
    for name in ['input-files.json','collection-input-files.json','original-retention-inputs.json','policy-code-inputs.json']:
        for e in inputs.load(O1/'receipts'/name):
            got = fingerprint(inputs.add(e['path']))
            assert got['sha256']==e['sha256'] and got['bytes']==e['bytes'], e['path']
            old_checks.append(e['path'])
    hf = inputs.load(O1/'receipts/hf-link-table.json')
    assert fingerprint(inputs.add(hf['verified_local_path']))['sha256']==hf['sha256']
    dump('receipts/o1-input-verification.json', dict(passed=True, fingerprints_verified=len(set(old_checks)), pinned_hf_table_rehashed=True))
    books={}
    def get(w,k):
        return books.setdefault((w,k), dict(book_key=k,wave=w,book_id=None,title=None,year=None,
          title_trust='unavailable',pdf_hashes=set(),provider_keys=set(),pages=[],
          lines={v:collections.Counter() for v in ['v1','v2']},declared_holdout_split=None,metadata_evidence=[]))
    for v, base, infix in [('v1',COL,''),('v2',COL/'v2','v2_')]:
        for s in SPLITS:
            for r in inputs.rows(base/f'import_real_{infix}{s}.jsonl'):
                w,k=identity(r);b=get(w,k);b['lines'][v][s]+=1
                p=provider_key(r.get('source_url'))
                if p and w!='wikisource':b['provider_keys'].add(p)
    represented=set(books)
    for w in WAVES:
        paths=['selection.json','books.json','source_books.json']
        for name in paths:
            p=HARVEST/w/name
            if not p.exists():continue
            obj=inputs.load(p);rows=obj.get('books',[]) if isinstance(obj,dict) else obj
            for r in rows:
                k=r['key'];ident=(w,k)
                if ident not in represented and not(w=='openarchives' and k in rb):continue
                b=get(w,k);b['book_id']=r.get('book') or r.get('index_url') or b['book_id']
                b['title']=r.get('title') or b['title'];b['year']=r.get('year')
                b['title_trust']='unverified_oa_join_excluded' if r.get('origin')=='openarchives' or w=='openarchives' else 'provider_catalogue_recorded'
                b['origin']=r.get('origin',w)
                b['metadata_evidence'].append(str(p))
                if r.get('pdf_sha256'):b['pdf_hashes'].add(('full_pdf',r['pdf_sha256']))
                for field in ['source_url','index_url','book']:
                    key=provider_key(r.get(field))
                    if key:b['provider_keys'].add(key)
        for h in inputs.load(HARVEST/w/'holdout_books.json'):
            if (w,h['book_key']) in books:books[w,h['book_key']]['declared_holdout_split']=h['split']
        p=HARVEST/w/('manifest_all.json' if w=='round1' else 'manifest.json')
        for r in inputs.load(p):
            k=r.get('key') or Path(r['image']).stem.rsplit('-',1)[0]
            if (w,k) not in books:continue
            b=books[w,k]
            b['book_id']=b['book_id'] or r.get('book')
            pageid=r.get('id') or f"{k}-p{r['page']:06d}"
            ih=r.get('image_sha256') or r.get('gate',{}).get('image_sha256')
            scope='page_pdf' if r.get('fetch_receipt',{}).get('derivative')=='page_pdf' else 'full_pdf'
            ph=r.get('pdf_sha256')
            if ph:b['pdf_hashes'].add((scope,ph))
            b['pages'].append(dict(id=pageid,page=r['page'],image_sha256=ih,pdf_sha256=ph,pdf_scope=scope,image=r.get('image')))
            if w=='wikisource':
                for val in [r.get('index_url'),r.get('book')]:
                    key=provider_key(val)
                    if key:b['provider_keys'].add(key)
                if r.get('scan_file'):b['provider_keys'].add('commons-file:'+unicodedata.normalize('NFC',r['scan_file']).replace(' ','_'))
    # All 89 corrected wave-4 identities, including the empty test holdout.
    for k,r in rb.items():
        b=get('openarchives',k)
        assert b['book_id']==r['book_id']
        assert ('full_pdf',r['pdf_sha256']) in b['pdf_hashes']
        b.update(title=r['title'],year=r['year'],title_trust='repository_verified' if r['provider_verified'] else 'aggregator_provider_pending',metadata_status=r['status'])
        b['provider_keys']=set(filter(None,[provider_key(r['external_link']),provider_key(r['edm_url'])]))
        cat=inputs.load(O1/r['evidence']['provider_catalogue'])
        if cat.get('repository_item_uuid'):
            # Retain UUID only on the exact repository host as an evidence-bound alias.
            host=urlsplit(r['external_link']).hostname
            b['provider_keys'].add('item:'+host+'/items/'+cat['repository_item_uuid'])
        b['metadata_evidence']=[str(O1/'rebind.jsonl'),str(O1/r['evidence']['provider_catalogue'])]
    # Wave-5 OA rows have the same suspect join. Only hash-identical O1 books inherit
    # corrected title/year; provider IDs come from the pinned exact PDF-to-item table.
    targets={canonical_url(r['pdf_url']):(w,r['key']) for w in ['mixed'] for r in inputs.load(HARVEST/w/'books.json') if r.get('origin')=='openarchives' and (w,r['key']) in books}
    if targets:
        import pyarrow.parquet as pq
        matches=collections.defaultdict(set)
        for batch in pq.ParquetFile(hf['verified_local_path']).iter_batches(batch_size=8192,columns=['collection_slug','external_link','edm_url','pdf_links_json','refined_pdf_links_json']):
            for r in batch.to_pylist():
                for f in ['pdf_links_json','refined_pdf_links_json']:
                    try:links=json.loads(r[f]) if r[f] else []
                    except (ValueError,TypeError):links=[]
                    if not isinstance(links,list):continue
                    for u in links:
                        if isinstance(u,str) and canonical_url(u) in targets:
                            matches[targets[canonical_url(u)]].add((r['external_link'],r['edm_url']))
        byhash=collections.defaultdict(list)
        for r in rb.values():byhash[r['pdf_sha256']].append(r)
        mreceipt=[]
        for ident in sorted(targets.values()):
            b=books[ident];pairs=matches[ident]
            assert len(pairs)<=1, (ident,pairs)
            if pairs:b['provider_keys']=set(filter(None,(provider_key(u) for pair in pairs for u in pair)))
            candidates=[r for scope,h in b['pdf_hashes'] for r in byhash.get(h,[]) if scope=='full_pdf']
            if candidates:
                assert len({(r['title'],r['year']) for r in candidates})==1
                r=candidates[0];b.update(title=r['title'],year=r['year'],title_trust='hash_identical_to_o1_corrected_book')
            mreceipt.append(dict(wave=ident[0],book_key=ident[1],pinned_item_matches=[list(x) for x in pairs],title_trust=b['title_trust']))
        dump('receipts/mixed-oa-identity.json',mreceipt)
    # Count only collection exports, never repeated rows as extra books.
    version_page_lines={v:collections.defaultdict(lambda:collections.Counter()) for v in ['v1','v2']}
    for v,base,name in [('v1',COL,'admitted_all.jsonl'),('v2',COL/'v2','admitted_all_v2.jsonl')]:
        for r in inputs.rows(base/name):
            version_page_lines[v][(r['wave'],r['page_id'])][r['split']]+=1
    for ident,b in books.items():
        assert b['book_id'] is not None, ident
        b['split']={v:sorted(s for s,n in b['lines'][v].items() if n) for v in ['v1','v2']}
        for p in b['pages']:
            p['lines']={v:dict(version_page_lines[v][b['wave'],p['id']]) for v in ['v1','v2']}
    index=collections.defaultdict(set);page_occurrences=collections.defaultdict(list)
    for ident,b in books.items():
        for scope,h in b['pdf_hashes']:index['pdf_sha256',scope,h].add(ident)
        for key in b['provider_keys']:index['provider_id','item',key].add(ident)
        if b['title_trust']!='unverified_oa_join_excluded' and b['title'] and isinstance(b['year'],int):
            index['title_year','title_year',normal_title(b['title'])+' | '+str(b['year'])].add(ident)
        for p in b['pages']:
            if p['image_sha256']:
                key=('page_image_sha256','page_image',p['image_sha256'])
                index[key].add(ident)
                page_occurrences[key].append(dict(wave=b['wave'],book_key=b['book_key'],**p))
    def member(ident):
        b=books[ident]
        return {k:b[k] for k in ['book_id','book_key','wave','title','year','title_trust','split','lines','declared_holdout_split']}
    def stats(ids,version):
        ns={s:sum(books[i]['lines'][version][s]>0 for i in ids) for s in SPLITS}
        counts={s:sum(books[i]['lines'][version][s] for i in ids) for s in SPLITS}
        present={s for s in SPLITS if ns[s]}
        return dict(cross_split=len(present)>1,train_test={'train','test'}<=present,train_dev={'train','dev'}<=present,dev_test={'dev','test'}<=present,within_train=ns['train']>1,within_dev=ns['dev']>1,within_test=ns['test']>1,lines=counts,test_books=[f'{w}:{k}' for w,k in sorted(ids) if books[w,k]['lines'][version]['test']])
    groups=[]
    for key,ids in sorted(index.items()):
        kt,scope,value=key
        # Page hashes compare pages across books, not non-overlapping pages within
        # one intentionally page-split book. Item/full-PDF/title detect that book.
        if len(ids)<2 and (scope in ['page_image','page_pdf'] or not any(len(books[i]['split'][v])>1 for i in ids for v in ['v1','v2'])):continue
        st={v:stats(ids,v) for v in ['v1','v2']}
        if not any(s['cross_split'] or any(s['within_'+x] for x in SPLITS) for s in st.values()):continue
        groups.append(dict(group='D'+str(len(groups)+1).zfill(5),key_type=kt,key_scope=scope,key=value,status='exact_key_candidate',members=[member(i) for i in sorted(ids)],versions=st,wave4_only=all(i[0]=='openarchives' for i in ids),contains_wave4=any(i[0]=='openarchives' for i in ids),cross_wave=len({i[0] for i in ids})>1,**({'page_occurrences':page_occurrences[key]} if kt=='page_image_sha256' else {})))
    write_jsonl('duplicates.jsonl',groups)
    # Possible editions use SequenceMatcher on the complete normalized title/year
    # string (autojunk disabled), with the title-only score and year equality shown.
    eligible=[(i,b,normal_title(b['title'])) for i,b in sorted(books.items()) if b['title_trust']!='unverified_oa_join_excluded' and b['title'] and isinstance(b['year'],int)]
    possible=[]
    for (i,a,ta),(j,b,tb) in itertools.combinations(eligible,2):
        xa=ta+' | '+str(a['year']);xb=tb+' | '+str(b['year'])
        if xa==xb:continue
        if min(len(xa),len(xb))/max(len(xa),len(xb)) < .9/1.1:continue
        sm=difflib.SequenceMatcher(None,xa,xb,autojunk=False)
        if sm.quick_ratio()<.9:continue
        ratio=sm.ratio()
        if ratio<.9:continue
        possible.append(dict(group='P'+str(len(possible)+1).zfill(5),status='possible',key_type='near_title_year',similarity=ratio,title_similarity=difflib.SequenceMatcher(None,ta,tb,autojunk=False).ratio(),same_year=a['year']==b['year'],members=[member(i),member(j)],versions={v:stats({i,j},v) for v in ['v1','v2']},edition_identity='unverified; similar catalogue titles alone do not prove the same scan'))
    write_jsonl('possible.jsonl',possible)
    def coverage(ids):
        total=len(ids)
        counts=dict(pdf=sum(bool(books[i]['pdf_hashes']) for i in ids),full_pdf=sum(any(s=='full_pdf' for s,h in books[i]['pdf_hashes']) for i in ids),provider=sum(bool(books[i]['provider_keys']) for i in ids),title=sum(books[i]['title_trust']!='unverified_oa_join_excluded' and bool(books[i]['title']) and isinstance(books[i]['year'],int) for i in ids),page_image=sum(any(p['image_sha256'] for p in books[i]['pages']) for i in ids))
        return dict(books=total,counts=counts,percent={k:round(n/total*100,4) for k,n in counts.items()})
    summaries={}
    for v in ['v1','v2']:
        summaries[v]={}
        for typ in ['all','pdf_sha256','provider_id','title_year','page_image_sha256']:
            gs=[g for g in groups if typ=='all' or g['key_type']==typ]
            result={}
            for flag in ['cross_split','train_test','train_dev','dev_test','within_train','within_dev','within_test']:
                selected=[g for g in gs if g['versions'][v][flag]]
                ids={(m['wave'],m['book_key']) for g in selected for m in g['members']}
                result[flag]=dict(groups=len(selected),**stats(ids,v))
            summaries[v][typ]=result
    serial=[]
    for i,b in sorted(books.items()):
        r=dict(b);r['pdf_hashes']=[dict(scope=s,sha256=h) for s,h in sorted(b['pdf_hashes'])];r['provider_keys']=sorted(b['provider_keys']);r['lines']={v:dict(b['lines'][v]) for v in ['v1','v2']};serial.append(r)
    write_jsonl('books.jsonl',serial)
    summary=dict(schema='o2-duplicate-audit-1',created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),book_identity='wave plus legacy book_key; v1/v2 exports are not extra books',group_definition='one exact key; overlapping keys are not independent leakages',versions=summaries,coverage={'collection_union':coverage(represented),'wave4_89':coverage({('openarchives',k) for k in rb}),'all_including_empty_wave4_holdout':coverage(set(books)),**{v:coverage({i for i in represented if books[i]['split'][v]}) for v in ['v1','v2']}},possible_groups=len(possible),wave4_possible_groups=sum(any(m['wave']=='openarchives' for m in p['members']) for p in possible),wave4_exact_groups=sum(g['wave4_only'] for g in groups),cross_wave_groups=sum(g['cross_wave'] for g in groups),network_requests=0,spend=0,limitations=['Recorded exact file hashes only; differently encoded or cropped scans can evade hash matching.','Anemi hashes are per-page PDFs, not whole-book PDFs, and are explicitly scoped.','Mixed-wave OA titles remain excluded unless the PDF is hash-identical to a corrected O1 book.','Catalogue title/year equality and provider equality identify candidates; multi-volume or catalogue duplication needs edition adjudication.','Possible near matches are reported separately and never counted as exact groups.'])
    dump('duplicate_summary.json',summary)
    inputs.finish('receipts/duplicate-inputs.json')
    print(json.dumps(dict(books=len(books),represented=len(represented),exact_groups=len(groups),possible=len(possible),v1=summaries['v1']['all']['cross_split']['groups'],v2=summaries['v2']['all']['cross_split']['groups'],coverage=summary['coverage']),ensure_ascii=False))

if __name__=='__main__':main()
