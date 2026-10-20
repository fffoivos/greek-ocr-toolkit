"""Offline identity, split and field comparison; does not apply any corrections."""
from __future__ import annotations
import collections, html, json, random, re, sys
sys.dont_write_bytecode=True
from audit import *
from fetch_catalogues import parse
from bs4 import BeautifulSoup

def download_chains(books):
    p=MAIN/'docs/harvest/harvest_big/openarchives/http/requests.jsonl'
    log=list(rows(p));out=[]
    for b in books:
        d=json.loads((MAIN/b['download_receipt']).read_text())
        tail=next(r for r in log if r.get('started')==d['started'] and r.get('sha256')==d['sha256'])
        chain=[tail]
        for _ in range(8):
            if canonical_url(chain[0]['url'])==b['canonical_pdf_url']:break
            previous=[r for r in log if r.get('location') and canonical_url(r['location'])==canonical_url(chain[0]['url']) and 0<=chain[0]['started']-r['finished']<60]
            assert previous,(b['book_key'],chain)
            chain.insert(0,max(previous,key=lambda r:r['finished']))
        assert canonical_url(chain[0]['url'])==b['canonical_pdf_url']
        out.append(dict(book_key=b['book_key'],source_http_log=str(p),chain=chain,complete=True))
    write('receipts/download-chains.json',out)
    return input_receipt(p)

def enrich(b):
    path=OUT/'receipts/catalogues'/f"{b['book_key']}.json";old=json.loads(path.read_text())
    if not old.get('http_receipt'):return old
    rec=old['http_receipt'];body=(OUT/rec['body']).read_bytes();assert sha(body)==rec['sha256']
    d=parse(b,rec,body);s=BeautifulSoup(body,'html.parser');state=s.select_one('#dspace-angular-state')
    if b['link_table']['collection_slug']=='elstat':
        cells={}
        for row in s.select('tr'):
            tds=row.find_all('td',recursive=False)
            if len(tds)==2:cells[tds[0].get_text(' ',strip=True)]=tds[1].get_text(' ',strip=True)
        title=s.select_one('td[colspan="2"] > strong')
        assert title and cells.get('Year of publication')
        d.update(title=title.get_text(' ',strip=True),title_evidence=[dict(field='catalogue title cell',value=title.get_text(' ',strip=True))],date_raw=cells['Year of publication'],date_evidence=[dict(field='Year of publication',value=cells['Year of publication'])],year=int(cells['Year of publication']),reference_year=cells.get('Reference year'),repository_page_count=cells.get('Number of PDF pages'),type_evidence=[dict(field='File type',value=cells.get('File type'))])
    if b['link_table']['collection_slug']=='apothesis':
        date=s.select_one('li.Date [property="dc:date"]');assert date
        value=date.get_text(' ',strip=True);year=re.findall(r'(?<!\d)(?:1[5-9]\d{2}|20[0-2]\d)(?!\d)',value)
        assert len(year)==1
        d.update(date_raw=value,date_evidence=[dict(field='Ημερομηνία έργου / dc:date',value=value)],year=int(year[0]))
        for item in s.select('li'):
            label=item.select_one('label');v=item.select_one('.fldval')
            if label and v and label.get_text(strip=True)=='Άδεια':d['rights_evidence']=[dict(field='Άδεια',value=v.get_text(' ',strip=True))]
            if label and v and label.get_text(strip=True)=='Είδος οντότητας':d['type_evidence']=[dict(field='Είδος οντότητας',value=v.get_text(' ',strip=True))]
    objects=[]
    if state:
        obj=json.loads(state.get_text().replace('&q;','"').replace('&s;',"'"))
        def visit(x):
            if isinstance(x,dict):
                if x.get('handle') and x.get('metadata'):objects.append(x)
                for v in x.values():visit(v)
            elif isinstance(x,list):
                for v in x:visit(v)
        visit(obj)
    expected=b['link_table']['external_link'].split('/handle/')[-1]
    selected=[o for o in objects if o['handle']==expected]
    if selected:
        assert len(selected)==1
        item=selected[0];md=item['metadata']
        d['repository_item_handle']=item['handle'];d['repository_item_uuid']=item.get('uuid') or item.get('id')
        d['repository_item_metadata']={k:v for k,v in md.items() if k.startswith(('dc.title','dc.date.issued','dc.type','dc.rights'))}
        for target,prefix in [('type_evidence','dc.type'),('rights_evidence','dc.rights')]:
            d[target]=[dict(field=k,value=v['value'],basis='embedded DSpace item metadata') for k,vs in md.items() if k.startswith(prefix) for v in vs]
    chain=json.loads((OUT/'receipts/download-chains.json').read_text())
    cb=next(c for c in chain if c['book_key']==b['book_key'])
    # Only published link/meta attachment URLs count, not arbitrary embedded UUIDs.
    links=[a['href'] for a in s.select('a[href],link[rel="item"][href]')]+[el['content'] for el in s.select('meta[name="citation_pdf_url"][content]')]
    chainurls={canonical_url(r['url']) for r in cb['chain']}
    d['attachment_download_chain_matches']=[u for u in links if u.startswith(('https://','http://')) and canonical_url(u) in chainurls]
    d['verified']=bool(d.get('title') and (d['attachment_download_chain_matches'] or d['attachment_exact_matches']))
    d['verification_basis']='Exact canonical offered attachment URL in original hash-bound HTTP download chain' if d['verified'] else 'Repository title/date and pinned item-to-PDF table; attachment not independently confirmed'
    write('receipts/catalogues/'+b['book_key']+'.json',d)
    return d

def exposure(books):
    by={b['book_key']:b for b in books};counts={k:{v:collections.Counter() for v in ['v1','v2','wave_admitted','records']} for k in by};inputs=[];allids={};manchecks=[]
    for name,field in [('admitted.jsonl','wave_admitted'),('records.jsonl','records')]:
        p=OA/name
        for r in rows(p):
            k=r['book_key'];assert k in by
            counts[k][field][r.get('split','unsplit')]+=1
    for version,base,part in [('v1',COL,''),('v2',COL/'v2','v2_')]:
        for split in ['train','dev','test']:
            p=base/f'import_real_{part}{split}.jsonl';inputs.append(input_receipt(p));selected=[]
            for r in rows(p):
                if r['wave']!='openarchives':continue
                key=r['doc'].split(':',1)[1];assert key in by
                counts[key][version][split]+=1
                selected.append((r['crop'],r['label'],r['source'],r['year'],r['script_class']))
                ent=allids.setdefault(r['id'],dict(id=r['id'],book_key=key))
                assert version not in ent
                ent[version]=dict(split=split,script_class=r['script_class'])
            mp=base/f'manifest_{part}{split}.json';inputs.append(input_receipt(mp))
            actual=[(r['crop'],r['label'],r['source'],r['year'],r['script_class']) for r in json.loads(mp.read_text()) if r['wave']=='openarchives']
            assert selected==actual,(version,split)
            manchecks.append(dict(version=version,split=split,wave4_lines=len(selected),ordered_manifest_import_equality=True,selected_content_sha256=sha(json.dumps(selected,ensure_ascii=False).encode())))
    with (OUT/'receipts/line-exposure.jsonl').open('w') as f:
        for r in sorted(allids.values(),key=lambda r:r['id']):f.write(json.dumps(r,ensure_ascii=False)+'\n')
    write('receipts/split-membership.json',counts);write('receipts/manifest-import-checks.json',manchecks)
    write('receipts/collection-input-files.json',inputs+[input_receipt(COL/'data_provenance.json'),input_receipt(COL/'v2/CLEAN_REPORT.md')])
    return counts

if __name__=='__main__':
    books=json.loads((OUT/'receipts/initial-bindings.json').read_text())
    write('receipts/http-source-input.json',download_chains(books))
    result=[enrich(b) for b in books]
    counts=exposure(books)
    print(json.dumps(dict(catalogue_titles=sum(bool(d.get('title')) for d in result),verified=sum(d.get('verified',False) for d in result),v1={s:sum(c['v1'][s] for c in counts.values()) for s in ['train','dev','test']},v2={s:sum(c['v2'][s] for c in counts.values()) for s in ['train','dev','test']})))
