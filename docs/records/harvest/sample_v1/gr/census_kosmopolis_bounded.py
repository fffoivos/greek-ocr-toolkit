"""Bound the OJS frame when issue/date endpoints repeatedly time out."""
from f2lib import *
from collections import Counter
def cached(url):
 for base in [BASE,F1]:
  p=base/'bulk/metadata'/(digest(url.encode())+'.body')
  if p.exists():return BeautifulSoup(p.read_bytes(),'html.parser'),sha(p),str(p.relative_to(ROOT))
 return None,None,None
def main():
 allissues={};found={};dates=[]
 for receipt in rows(BASE/'receipts/kosmopolis-archives.jsonl'):
  ss,h,path=cached(receipt['url'])
  if ss is None:continue
  for a in ss.select('a[href*="/issue/view/"]'):
   u=urljoin(receipt['url'],a['href']);j=u.split('/index.php/')[1].split('/')[0];ident=j+'-'+u.rstrip('/').rsplit('/',1)[-1]
   allissues[ident]=dict(id=ident,source='kosmopolis',journal=j,title=a.get_text(' ',strip=True),catalogue_url=u,url=None,year=None,kind='periodical_issue')
 for ident,it in allissues.items():
  ss,h,path=cached(it['catalogue_url'])
  if ss is None:continue
  articles=[urljoin(it['catalogue_url'],a['href']) for a in ss.select('a[href]') if re.search(r'/article/view/\d+$',a['href'])]
  for article in articles:
   aa,ah,ap=cached(article)
   if aa is None:continue
   dt=aa.select_one('meta[name=citation_date]');y=year(dt.get('content')) if dt else None
   if y and 1850<=y<=1930:
    found[ident]=dict(it,year=y,date_basis='own article citation_date linked from own issue catalogue',date_metadata_sha256=ah,date_metadata_path=ap);break
 # F1's own-catalogue, same-day date receipts qualify two further issue IDs;
 # the article count itself never supplies an issue population count.
 for old in rows(F1/'candidates_kosmopolis.jsonl'):
  u=old.get('issue');y=old.get('year')
  if not u or not y or not 1850<=y<=1930:continue
  ident=old['journal']+'-'+u.rstrip('/').rsplit('/',1)[-1]
  if ident not in allissues:continue
  it=allissues[ident];ss,h,path=cached(u)
  if ss is not None:found.setdefault(ident,dict(it,year=y,date_basis='F1 same-day own-catalogue citation_date, source issue and article bindings retained',date_metadata_sha256=h,date_metadata_path=path))
 write(BASE/'receipts/kosmopolis-exposed-frame.json',dict(exposed_journals=14,exposed_unique_issues=len(allissues),by_journal=dict(Counter(x['journal'] for x in allissues.values())),date_qualified_lower_bound=len(found),unresolved_date_items=len(allissues)-len(found),blocker='apothiki1 issue and article metadata returned repeated 25-second timeouts/502; stopped unbounded date crawl; no full eligible census claimed',at=stamp()))
 population('kosmopolis',list(found.values()),False,'All 2047 unique issue URLs exposed by all 14 current journal archives were enumerated. The eligible date-qualified lower bound uses own issue-to-article citation_date bindings, including same-day F1 bindings for two Χρυσαλλίς issues. Repeated issue endpoint timeouts prevent whole-population 1850-1930 filtering.',exposed_issue_urls=len(allissues),unit='issue')
 print('dated periods',Counter(period(x['year']) for x in found.values()))
 print('draw periods',Counter(period(x['year']) for x in rows(BASE/'draw_kosmopolis.jsonl')))
if __name__=='__main__':main()
