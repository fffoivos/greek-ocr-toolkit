#!/usr/bin/env python3
"""S5: bounded probes of NLG, Pergamos, Gallica and Wellcome public interfaces."""
import html,xml.etree.ElementTree as ET
from greekocr._vendor.scripts.fetch.o4c_common import *

def parse_nlg(data,url):
    text=data.decode('utf-8','replace');rows=[];seen=set()
    for m in re.finditer(r'<a\b[^>]*href=["\']([^"\']*/browse/(\d+)[^"\']*)["\'][^>]*>(.*?)</a>',text,re.S|re.I):
        id=m[2]
        if id in seen:continue
        title=html.unescape(re.sub('<[^>]+>',' ',m[3])).strip()
        if not title:continue
        seen.add(id);r=row('other','nlg:'+id,title,urllib.parse.urljoin(url,html.unescape(m[1])),rights=None,library='National Library of Greece',language='el')
        rows.append(r)
    return rows

def parse_wellcome(item):
    r=row('other','wellcome:'+item['id'],item['title'],'https://wellcomecollection.org/works/'+item['id'],
      rights=None,library='Wellcome Collection',language=item.get('languages'))
    r['digitised_locations']=[]
    for child in item.get('items',[]):
        for location in child.get('locations',[]):
            r['digitised_locations'].append(location)
    return r

def main():
    p=parser('other');p.add_argument('--query',default='Εφημερίς');args=p.parse_args();h=HTTP('other',args.offline,args.interval,retry_errors=args.retry_errors)
    path,state=load_state(args);rows={r['document_id']:r for r in read_rows(args.out)}
    attempts=[('Pergamos','https://pergamos.lib.uoa.gr/oai?verb=Identify'),
      ('Gallica',api('https://gallica.bnf.fr/services/engine/search/sru',operation='searchRetrieve',version='1.2',query='dc.language all "gre"',maximumRecords=2)),
      ('NLG homepage','https://digitalcollections.nlg.gr/'),
      ('NLG OAI guess','https://digitalcollections.nlg.gr/nlg-repo/oai?verb=Identify')]
    for name,u in attempts:
        try:
            m,b=h.get(u);h.event(stage='interface',library=name,url=u,status=m['status'],sha256=m['sha256'])
            if name=='NLG homepage':
                for r in parse_nlg(b,u):rows.setdefault(r['document_id'],r)
        except Exception as e:h.event(stage='interface',library=name,url=u,error=str(e))
    offset=state.get('nlg_page',1)
    for _ in range(args.max_pages):
        u=api('https://digitalcollections.nlg.gr/nlg-repo/dl/el/search.html',**{'p.text':args.query,'page':offset})
        try:m,b=h.get(u);new=parse_nlg(b,u);h.event(stage='nlg-search',url=u,returned=len(new),sha256=m['sha256'])
        except Exception as e:h.event(stage='nlg-search',error=str(e));break
        for r in new:rows.setdefault(r['document_id'],r)
        if not new:break
        offset+=1;state['nlg_page']=offset;write_json(path,state)
    # Known public catalogue API. Language filter may have zero matches; do not infer language from query alone.
    page=state.get('wellcome_page',1)
    for _ in range(args.max_pages):
        u=api('https://api.wellcomecollection.org/catalogue/v2/works',query='Greek',availabilities='online',pageSize=10,page=page,include='items')
        try:d=h.json(u);h.event(stage='wellcome-search',url=u,total=d.get('totalResults'),returned=len(d.get('results',[])))
        except Exception as e:h.event(stage='wellcome-search',error=str(e));break
        for item in d.get('results',[]):
            r=parse_wellcome(item);rows.setdefault(r['document_id'],r)
        page+=1;state.update(wellcome_page=page,wellcome_complete=page>d.get('totalPages',0));write_json(path,state)
        if state['wellcome_complete']:break
    save_rows(args.out,rows.values());write_json(path,state)
    print('other documents',len(rows),'bytes',h.transferred)
if __name__=='__main__':main()
