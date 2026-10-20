import json
from urllib.parse import urlencode
from pilotlib import *
from concurrent.futures import ThreadPoolExecutor

def job(source,label,url,limit=8_000_000):
    try:
        p=fetch(client(source),url,BASE/'bulk/discovery'/(label+'.dat'),limit);print(label,'ok',p.stat().st_size,flush=True)
    except Exception as e:print(label,type(e).__name__,str(e)[:180],flush=True)

if __name__=='__main__':
    tasks=[
      ('ia','ia-historical','https://archive.org/advancedsearch.php?'+urlencode(dict(q='mediatype:texts AND (language:gre OR language:grc OR language:ell) AND year:[1850 TO 1890]',output='json',rows=100,**{'fl[]':['identifier','title','year','publisher','creator']}),doseq=True)),
      ('kosmopolis','kosmopolis-issue','https://kosmopolis.library.upatras.gr/index.php/xrysallis/issue/view/4162'),
      ('elstat','elstat-record','https://www.openarchives.gr/aggregator-openarchives/edm/elstat/000056-book_p_id%3D10095331?language=el'),
      ('perseus','perseus-ggm','https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/03776b39f4047c5cff06f5296fae4b2bae4b08fb/data/ggm0001/ggm001/ggm0001.ggm001.1st1K-grc1.xml'),
    ]
    with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(lambda x:job(*x),tasks))
