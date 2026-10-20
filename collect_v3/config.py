"""Plan section 3 allocations. Prices are integer micro-USD, never floats in ledger."""
from pathlib import Path
from .common import read_json

# source: total pages, minimum total items, route, measured marks numerator/denominator, yields/page
SPECS = {
 'bsb_poly1850': (1000,25,'iiif', (37,40), {'poly1850':16.4}),
 'ia_poly1850': (1600,40,'ia',(34,40),{'poly1850':19.7}),
 'ia_greek_latin': (1000,25,'ia',(35,40),{'mixed_greek_latin':22.*.94,'latin':8.}),
 'ia_russian': (400,10,'ia',None,{'cyrillic':30.2}),
 'nlg': (400,10,'iiif',(32,40),{'poly1850':14.1,'poly1900':9.1,'dialogue_fiction':2.0}),
 'kosmopolis': (600,16,'ojs',(34,40),{'poly1900':20.9*560/600,'poly1850':70.7*40/600,'dialogue_fiction':2200/600}),
 'lekythos': (290,13,'pdf',(32,40),{'poly1900':134.1,'dialogue_fiction':11.8,'headings_caps':3.2}),
 'gazette_modern': (1200,1200,'gazette',(39,40),{'modern_scanned':525/12,'numerics_tables':67/12,'headings_caps':57/12,'dialogue_fiction':36/12}),
 'elstat': (60,30,'pdf',None,{'numerics_tables':176.}),
 'serbia': (300,30,'pdf',None,{'cyrillic':614/30}),
}
TARGETS={'modern_scanned':40000,'poly1850':40000,'poly1900':50000,'mixed_greek_latin':20000,'latin':8000,'cyrillic':12000,'numerics_tables':10000,'headings_caps':6000,'dialogue_fiction':12000,'leaders_indices':4000}
POLY={'bsb_poly1850','ia_greek_latin','nlg','kosmopolis','lekythos'}
HOLD={'gazette_modern','kosmopolis','lekythos','ia_greek_latin'}
ITEM_CAPS={'lekythos':24,'gazette_modern':1,'kosmopolis':40}
DEFAULTS = dict(seed=20261016, caps_usd={'W1':2.15,'W2':8.30}, request_per_second=1.0,
                prune_images=False, storage_diet=True, serbian_codec=True, page_micro_usd=1500,
                mdz_daily_image_cap=500, limiter_root=None,
                output_root='docs/harvest/collect_v3', cache='docs/harvest/collect_v3/cache',
                execution_host=None, network_enabled=False)

def config(path=None, **overrides):
    c={**DEFAULTS, **(read_json(path) if path else {})}
    c.update({k:v for k,v in overrides.items() if v is not None})
    if c['prune_images']:raise ValueError('the only crop-source raster must be retained')
    if not 0 < c['request_per_second'] <= 1: raise ValueError('request_per_second must be >0 and <=1')
    for t, hard in [('W1',2.15),('W2',8.30)]:
        if not 0 < c['caps_usd'][t] <= hard: raise ValueError('cap exceeds authorized tranche ceiling')
    if c['page_micro_usd'] != 1500: raise ValueError('pinned F2 page price is 1500 micro-USD')
    if not isinstance(c['mdz_daily_image_cap'],int) or c['mdz_daily_image_cap']<=0:raise ValueError('positive MDZ daily image cap required')
    return c

def marks(source):
    v=SPECS[source][3]
    return {'y':v[0],'n':v[1],'rate':v[0]/v[1],'evidence':'plan section 2 fresh blind sample'} if v else {'y':None,'n':None,'rate':None,'evidence':'not measured / not applicable'}
