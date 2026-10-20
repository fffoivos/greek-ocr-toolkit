"""Resolve sampled OJS issue dates through linked catalogue citation metadata."""
from f2lib import *
def main(source):
 c=HTTP(source);bindings={}
 for v in rows(BASE/f'verification_{source}.jsonl'):
  if not v.get('resolved_item'):continue
  r=v['resolved_item'];ys=[];evidence=[]
  galleys=[x['galley'] for x in r.get('issue_page_spans',[])]+r.get('galleys',[])
  for galley in galleys:
   u=galley.rsplit('/',1)[0];p=BASE/'bulk/metadata'/(digest(u.encode())+'.body')
   if not p.exists():continue
   ss=BeautifulSoup(p.read_bytes(),'html.parser');dt=ss.select_one('meta[name=citation_date]');y=year(dt.get('content')) if dt else None
   if y:ys.append(y);evidence.append(dict(url=u,sha256=sha(p),year=y))
  if not ys and galleys:
   u=galleys[0].rsplit('/',1)[0]
   try:
    ss,m,b=soup(c,u);dt=ss.select_one('meta[name=citation_date]');y=year(dt.get('content')) if dt else None
    if y:ys.append(y);evidence.append(dict(url=u,sha256=m['sha256'],year=y))
   except Exception as e:evidence.append(dict(url=u,error=type(e).__name__))
  bindings[r['id']]=dict(year=ys[0] if len(set(ys))==1 else r.get('year'),evidence=evidence,conflicting_dates=len(set(ys))>1)
 pp=rows(BASE/f'pages_{source}.jsonl')
 for p in pp:
  d=bindings.get(p['item'],{})
  if d.get('year'):
   p.update(year=d['year'],period=period(d['year']),date_binding='receipts/'+source+'-issue-dates.json')
   for folder in ['pages','machine']:
    dest=BASE/'receipts'/folder/(p['id']+'.json')
    if dest.exists():
     old=json.loads(dest.read_text());old.update(year=p['year'],period=p['period'],date_binding=p['date_binding']);write(dest,old)
 jsonl(BASE/f'pages_{source}.jsonl',pp);write(BASE/'receipts'/(source+'-issue-dates.json'),bindings)
 vv=rows(BASE/f'verification_{source}.jsonl')
 for v in vv:
  if v.get('resolved_item') and bindings.get(v['item'],{}).get('year'):v['resolved_item']['year']=bindings[v['item']]['year']
 jsonl(BASE/f'verification_{source}.jsonl',vv)
 print(source,'bound',sum(bool(v.get('year')) for v in bindings.values()),'/',len(bindings))
if __name__=='__main__':main(sys.argv[1])
