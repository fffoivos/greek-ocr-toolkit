import sys,pathlib,json,re
sys.path.insert(0,str(pathlib.Path('docs/harvest/funnel_v1/gr').resolve()))
import funnellib as f
f.BASE=pathlib.Path('docs/harvest/sample_v1/gr').resolve()
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
urls={
'kosmopolis':'https://kosmopolis.library.upatras.gr/',
'pleias':'https://pleias.library.upatras.gr/',
'nlg-digital':'https://digitalcollections.nlg.gr/nlg-repo/dl/el/search.html?p.proto=%2Fbutterfly%2Fbackie%2Fmonograph&p.collabKinds=NLG_ONLY&p.languages=%2Flib%2Fdefault%2Fdata%2F100091&p.start=0&p.count=100',
'lekythos':'https://lekythos.library.ucy.ac.cy/archive/item/14018',
'elstat':'http://dlib.statistics.gr/portal/page/portal/ESYE/categoryyears?p_cat=10007369&p_topic=10007369',
'government-gazette':'https://search.et.gr/el/search-legislation/',
}
def one(t):
 s,u=t
 try:
  r,b=f.HTTP(s).get(u);p=BeautifulSoup(b,'html.parser');txt=p.get_text(' ',strip=True)
  f.write(f.BASE/'receipts'/('inspect-'+s+'.json'),dict(url=u,text=txt[:18000],links=[dict(href=a['href'],text=a.get_text(' ',strip=True)) for a in p.select('a[href]')],forms=[str(a) for a in p.select('form')]))
  print(s,'OK',len(b),txt[:1300],flush=True)
 except Exception as e:print(s,type(e).__name__,str(e)[:200],flush=True)
with ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(one,urls.items()))
