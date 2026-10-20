"""Offline SPLIT1 proposal. No release assignment, OCR, remote access or live writes."""
from __future__ import annotations
import base64, collections, gzip, hashlib, html, io, json, os, random, re, subprocess, sys, unicodedata
from pathlib import Path
from PIL import Image

HERE=Path(__file__).resolve().parent
PROJECTS=Path.home()/'Projects'
DATA=PROJECTS/'collect-v3-data'; RUN=DATA/'run'; SNAP=DATA/'snapshots'
TOOLKIT=PROJECTS/'greek-ocr-toolkit'; REVIEW=PROJECTS/'greek-ocr-toolkit-review'
COLLECT=PROJECTS/'greek-ocr-toolkit-sol-collect'
PYTHON=COLLECT/'.venv/bin/python'
PLAN=PROJECTS/'greek-page-ocr/docs/ocr_program_2026-10-06/DATA_PLAN_v2_20261016.md'
EXDIR=COLLECT/'docs/harvest/collect_v3/release_exclusions'
SPLITS=('train','dev','test'); RATIOS=(.85,.05,.10)
QUOTAS={'poly1850':40000,'poly1900':50000,'modern_scanned':40000,'mixed_greek_latin':20000,'latin':8000,'cyrillic':12000,'headings_caps':6000,'numerics_tables':10000,'leaders_indices':4000,'dialogue_fiction':12000}

def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def dump(name,x): (HERE/name).write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def jsonl(p):
 with open(p) as f:
  for l in f:
   if l.strip():yield json.loads(l)
def norm(x):
 s=unicodedata.normalize('NFKD',str(x or '')).casefold()
 return ' '.join(''.join(c if c.isalnum() else ' ' for c in s if not unicodedata.combining(c)).split())
def urlnorm(s):
 from urllib.parse import urlsplit,unquote
 if not s:return ''
 p=urlsplit(unquote(str(s)));return (p.netloc.casefold().removeprefix('www.')+p.path.rstrip('/')+('?' + p.query if p.query else ''))
def identifiers(r):
 out=set()
 for k in ('id','identifier','item','doi','urn','isbn','official_catalogue_id'):
  v=r.get(k)
  if v:
   for x in v if isinstance(v,list) else [v]:out.add(str(x).casefold())
 for k,v in r.items():
  if ('url' in k or k=='page_access_route') and isinstance(v,str):
   for pat in (r'archive\.org/(?:details|download)/([^/?]+)',r'(bsb\d+)',r'(GRESYE_[A-Za-z0-9_]+)',r'(URN:NB:RS:[^/?]+)'):
    out.update(x.casefold() for x in re.findall(pat,v,re.I))
 return out
def urls(r):return {urlnorm(v) for k,v in r.items() if 'url' in k and isinstance(v,str) and v.startswith(('http:','https:'))}
def title(r):
 t=r.get('edition_title') or r.get('title') or ''
 # OJS titles are local issue names; journal is part of the publication title.
 return (str(r['journal'])+' — '+t) if r.get('journal') else t

def read_rows():
 rows=[];counts=collections.Counter();seen=collections.Counter();receipt={}
 checks={l.split()[1]:l.split()[0] for l in (SNAP/'SHA256_20261018_0524.txt').read_text().splitlines()}
 keep=('id','page_id','source','item','year','primary_class','crop_sha256','crop_source_image','crop_source_sha256','crop_bbox','bbox','old_label','text')
 for w in ('W1','W2'):
  p=SNAP/f'{w}_features_20261018_0524.jsonl';sha=digest(p);assert sha==checks[p.name]
  for r in jsonl(p):
   q={k:r.get(k) for k in keep};q['wave']=w;q['document']=r['page_id'].rsplit('--s',1)[0]
   rows.append(q);counts[w]+=1;seen[q['id']]+=1
  receipt[w]={'path':str(p),'sha256':sha,'rows':counts[w]}
 receipt['duplicate_row_ids']={k:v for k,v in seen.items() if v>1}
 receipt['selection']='Every nonempty JSONL row, in W1 then W2 input order; no admission or usability filter.'
 receipt['census_held']=142959;receipt['rows']=len(rows);receipt['difference_from_held']=len(rows)-142959
 return rows,receipt

def metadata(rows):
 docs={}; evidence=[]; files={}
 for r in rows:
  d=docs.setdefault(r['document'],{'document_id':r['document'],'source':r['source'],'item':r['item'],'year':r['year'],'records':{},'pages':set(),'waves':set()})
  d['pages'].add((r['wave'],r['page_id']));d['waves'].add(r['wave'])
 for w in ('W1','W2'):
  for p in sorted(RUN.glob(w+'_manifest*.jsonl')):
   files[str(p)]=digest(p)
   for n,r in enumerate(jsonl(p),1):
    did=r['id'].rsplit('--s',1)[0]
    if did in docs:
     v=r.get('item_record',{});key=canonical(v)
     docs[did]['records'].setdefault(key,{'metadata':v,'evidence':f'{p}:{n}#item_record'})
 # Read only pages represented by the frozen inputs. Never select later feature rows.
 for d in docs.values():
  for w,pid in sorted(d['pages']):
   p=RUN/w/'pages'/f'{pid}.json'
   if p.exists():
    r=json.loads(p.read_text());a=r.get('analysis_page',{});v=a.get('item_record',{})
    if v: d['records'].setdefault(canonical(v),{'metadata':v,'evidence':f'{p}#analysis_page.item_record'})
    d.setdefault('page_urls',set()).update(urls(a))
  d['records']=sorted(d['records'].values(),key=lambda r:r['evidence']);d['waves']=sorted(d['waves'])
  d['page_count_in_snapshot']=len(d.pop('pages'));d['page_urls']=sorted(d.get('page_urls',[]))
  d['partial_bsb_w2']=d['source']=='bsb_poly1850' and 'W2' in d['waves']
  d['title']=next((title(v['metadata']) for v in d['records'] if title(v['metadata'])),d['item'])
 return docs,files

def identity_keys(d):
 result=[]
 for rec in d['records']:
  r=rec['metadata'];src=r.get('provider') or r.get('source') or d['source'].split('_')[0]
  # Namespaced record identity; shared DOI/URN/ISBN also works across providers.
  for ident in sorted(identifiers(r)):
   namespace='global' if ident.startswith(('urn:','10.','isbn')) else str(src)
   result.append((('identifier',namespace,ident),rec['evidence']))
  t=norm(title(r));y=r.get('year',d['year']);v=norm(r.get('volume'))
  if t and y:result.append((('title_year_volume',t,str(y),v),rec['evidence']))
 return result

def build_editions(docs,rows):
 parent={d:d for d in docs};merges=[];index={}
 def root(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 for d in sorted(docs):
  for key,ev in identity_keys(docs[d]):
   if key in index:
    other,oev=index[key]
    if root(d)!=root(other):
     # Gazette identity is an issue, never just the annual title.
     parent[root(d)]=root(other);merges.append({'documents':[other,d],'match_key':key,'evidence':[oev,ev]})
   else:index[key]=(d,ev)
 groups=collections.defaultdict(list)
 for d in sorted(docs):groups[root(d)].append(d)
 editions=[];doc2ed={}
 for members in groups.values():
  eid=hashlib.sha256('\n'.join(sorted(members)).encode()).hexdigest()
  e={'edition_id':eid,'member_documents':members,'metadata':[docs[d] for d in members],
    'merge_evidence':[m for m in merges if set(m['documents'])<=set(members)],'rows_per_class':{},'rows_per_source_class':{},
    'row_count':0,'forced':False,'forced_split':None,'proposed_split':None,'leakage_matches':[]}
  e['gazette']=all(docs[d]['source']=='gazette_modern' for d in members)
  e['year']=docs[members[0]]['year'];e['title']=docs[members[0]]['title'];e['partial_bsb_w2']=any(docs[d]['partial_bsb_w2'] for d in members)
  editions.append(e)
  for d in members:doc2ed[d]=e
 for r in rows:
  e=doc2ed[r['document']];e['row_count']+=1;c=r['primary_class'] or 'unclassified';sc=r['source']+' × '+c
  e['rows_per_class'][c]=e['rows_per_class'].get(c,0)+1;e['rows_per_source_class'][sc]=e['rows_per_source_class'].get(sc,0)+1
 for e in editions:
  e['primary_class']=min(e['rows_per_class'],key=lambda c:(-e['rows_per_class'][c],c))
  e['source']=min({d['source'] for d in e['metadata']})
 return sorted(editions,key=lambda e:e['edition_id']),doc2ed,merges

def load_v2():
 docs={};rowdoc={};files={}
 for side in SPLITS:
  p=TOOLKIT/f'docs/harvest/collection/v2/import_real_v2_{side}.jsonl';files[str(p)]=digest(p)
  for r in jsonl(p):
   key=(r['doc'],side);d=docs.setdefault(key,{'doc':r['doc'],'split':side,'urls':set(),'identifiers':set(),'title_year':set(),'metadata_evidence':set(),'rows':0})
   d['rows']+=1;rowdoc[r['id']]=key;d['urls'].update(urls(r));d['identifiers'].update(identifiers({k:v for k,v in r.items() if k not in ('id',)}))
   if r.get('title') and r.get('year'):d['title_year'].add((norm(r['title']),str(r['year'])))
   d['year']=r.get('year')
 # Supplement missing titles with local collection acquisition manifests, bound by URL or document key.
 manifests=[]
 for pattern in ('*/manifest.json','round1/manifest_all.json','mixed/archive_metadata.json'):
  manifests.extend((TOOLKIT/'docs/harvest').glob(pattern))
 byurl=collections.defaultdict(set);bykey=collections.defaultdict(set)
 for k,d in docs.items():
  for u in d['urls']:byurl[u].add(k)
  bykey[d['doc'].split(':')[-1]].add(k)
 for p in sorted(set(manifests)):
  r=json.loads(p.read_text()); records=r if isinstance(r,list) else r.get('pages',[])
  if not isinstance(records,list):continue
  bound=0
  for v in records:
   if not isinstance(v,dict):continue
   matches=set()
   for u in urls(v):matches.update(byurl[u])
   for field in ('key','volume','book','doc'):
    if isinstance(v.get(field),str):matches.update(bykey[v[field]])
   for k in matches:
    d=docs[k];d['identifiers'].update(identifiers({k:v for k,v in v.items() if k not in ('id',)}))
    if v.get('title') and v.get('year'):
     d['title_year'].add((norm(v['title']),str(v['year'])));d['metadata_evidence'].add(str(p));bound+=1
  if bound:files[str(p)]=digest(p)
 return docs,rowdoc,files

def force_leakage(editions,rows,v2,rowdoc):
 ex=json.loads((EXDIR/'release_exclusions.json').read_text());files={str(EXDIR/'release_exclusions.json'):digest(EXDIR/'release_exclusions.json')};locks=collections.defaultdict(list);uncovered=[]
 for name,v in ex['classes'].items():
  is_eval=('eval' in name or 'never trains' in str(v.get('rule','')) or 'never admitted to training' in str(v.get('rule','')))
  if not is_eval:continue
  p=EXDIR/v['file'];actual=digest(p);assert actual==v['sha256'];files[str(p)]=actual
  side='dev' if name=='eval_only_dev' else 'test'
  for rid in p.read_text().splitlines():
   if rid in rowdoc:locks[('v2',rowdoc[rid])].append((name,side,rid))
   locks[('row',rid)].append((name,side,rid))
 iu=collections.defaultdict(set);ii=collections.defaultdict(set);it=collections.defaultdict(set)
 for k,d in v2.items():
  for u in d['urls']:iu[u].add(k)
  for i in d['identifiers']:ii[i].add(k)
  for t in d['title_year']:it[t].add(k)
 rows_by_doc=collections.defaultdict(list)
 for r in rows:rows_by_doc[r['document']].append(r['id'])
 conflicts=[]
 for e in editions:
  found={}; direct=[]
  for d in e['metadata']:
   for rec in d['records']:
    r=rec['metadata']
    for typ,values,idx in [('url',urls(r),iu),('identifier',identifiers(r),ii),('title_year',{(norm(title(r)),str(r.get('year',d['year'])))} if title(r) else set(),it)]:
     for val in values:
      for k in idx.get(val,[]):
       found.setdefault(k,[]).append({'type':typ,'value':val,'w_document':d['document_id'],'w_evidence':rec['evidence']})
   for rid in rows_by_doc[d['document_id']]:
    direct.extend(locks.get(('row',rid),[]))
  sides=set()
  for k,evidence in sorted(found.items()):
   vd=v2[k];ls=locks.get(('v2',k),[]);side=vd['split'];sides.add(side)
   for cl,locked,rid in ls:sides.add(locked)
   e['leakage_matches'].append({'v2_doc':vd['doc'],'v2_split':side,'evidence':sorted({canonical(x) for x in evidence}),
     'v2_metadata_evidence':sorted(vd['metadata_evidence']),'locked_classes':[{'class':x,'side':y,'row_id':z} for x,y,z in ls]})
  if direct:
   # Deduplicate class witnesses; preserve every row witness in the machine ledger.
   direct=sorted(set(direct));sides.update(s for _,s,_ in direct)
   e['leakage_matches'].append({'release_exclusion_matches':[{'class':c,'side':s,'row_id':r} for c,s,r in direct]})
  if sides:
   # A conflict is evidence for the owner, never a silent train inheritance.
   chosen='test' if 'test' in sides else 'dev' if 'dev' in sides else 'train'
   if len(sides)>1:conflicts.append({'edition_id':e['edition_id'],'sides':sorted(sides),'display_side':chosen,'status':'owner resolution required; no final assignment'})
   e.update(forced=True,forced_split=chosen,proposed_split=chosen,reason='forced by v2 / registered locked-eval evidence' if direct else 'forced by v2')
   if len(sides)>1:e['reason']+='; conflicting evidence, owner resolution required'
  else:e['reason']='85/5/10 row-share greedy proposal; whole edition; owner decides'
 return files,conflicts

def allocate(editions):
 totals=collections.Counter();counts=collections.defaultdict(collections.Counter)
 for e in editions:
  totals.update(e['rows_per_source_class'])
  if e['forced']:counts[e['proposed_split']].update(e['rows_per_source_class'])
 strata=collections.defaultdict(list)
 for e in editions:
  if not e['forced']:strata[(e['source'],e['primary_class'])].append(e)
 for (source,cl),es in sorted(strata.items()):
  seed=f'split1:{source}:{cl}';rng=random.Random(seed);es=sorted(es,key=lambda e:e['edition_id']);rng.shuffle(es);es.sort(key=lambda e:-e['row_count'])
  for e in es:
   def score(s):
    # Change in total squared row deviation, over each affected source × class.
    return sum((counts[s][k]+n-totals[k]*RATIOS[SPLITS.index(s)])**2-(counts[s][k]-totals[k]*RATIOS[SPLITS.index(s)])**2 for k,n in e['rows_per_source_class'].items())
   side=min(SPLITS,key=lambda s:(score(s),SPLITS.index(s)));e['proposed_split']=side;e['seed']=seed;counts[side].update(e['rows_per_source_class'])
 return {k:{s:counts[s][k] for s in SPLITS} for k in sorted(totals)}

def write_proposals(rows,editions,doc2ed):
 with open(HERE/'editions.jsonl','w') as f:
  for e in editions:f.write(canonical(e)+'\n')
 with open(HERE/'row_split_proposal.jsonl.gz','wb') as raw:
  with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as z:
   for r in rows:
    e=doc2ed[r['document']];z.write((canonical({'row_id':r['id'],'parent_id':f"collect-v3-{r['wave']}-20261018-0524",'edition_id':e['edition_id'],'proposed_split':e['proposed_split'],'forced':e['forced']})+'\n').encode())

def regenerate(r):
 assert Path(sys.executable).samefile(PYTHON),sys.executable
 source=Path(r['crop_source_image']);assert digest(source)==r['crop_source_sha256']
 with Image.open(source) as im:
  im=im.convert('L');crop=im.crop(tuple(r['crop_bbox']));b=io.BytesIO();crop.save(b,'PNG',compress_level=3)
 data=b.getvalue();sha=hashlib.sha256(data).hexdigest()
 assert sha==r['crop_sha256'],(r['id'],sha,r['crop_sha256'])
 return data,crop.size

def samples(rows,editions,doc2ed):
 groups=collections.defaultdict(list)
 for r in rows:groups[doc2ed[r['document']]['edition_id']].append(r)
 cards=[];gaz=collections.defaultdict(list)
 for e in editions:
  if e['gazette']:gaz[str(e['year'])].append(e)
  else:cards.append({'id':e['edition_id'],'editions':[e]})
 for y,es in sorted(gaz.items()):cards.append({'id':'gazette-year-'+y,'editions':sorted(es,key=lambda e:(not e['forced'],SPLITS.index(e['proposed_split']),e['title'])),'year':y})
 # Card samples are two saved Google rows; edition cards use their own rows, year cards use two different issues.
 receipts=[]
 for card in cards:
  pool=[]
  for e in card['editions']:
   # Deterministic, size-conscious examples: pick 15th- and 35th-percentile-area rows from each edition.
   rs=groups[e['edition_id']];rs=sorted(rs,key=lambda r:((r['crop_bbox'][2]-r['crop_bbox'][0])*(r['crop_bbox'][3]-r['crop_bbox'][1]),r['id']))
   for idx in (15*len(rs)//100,35*len(rs)//100):pool.append(rs[idx])
  chosen=pool[:2] if len(card['editions'])==1 else [pool[0],pool[len(pool)//2]]
  card['samples']=[]
  for r in chosen:
   data,size=regenerate(r);path=HERE/'crops'/f"{r['wave']}--{r['id']}.png";path.parent.mkdir(exist_ok=True);path.write_bytes(data)
   rec={k:r[k] for k in ('id','wave','crop_sha256','crop_source_image','crop_source_sha256','crop_bbox','bbox','old_label')};rec.update(path=str(path.relative_to(HERE)),edition_id=doc2ed[r['document']]['edition_id'],size=size)
   receipts.append(rec);card['samples'].append(rec)
  forced=any(e['forced'] for e in card['editions']);ss={e['proposed_split'] for e in card['editions']}
  card['group']='forced' if forced else next(s for s in ('test','dev','train') if s in ss)
 dump('crop_receipts.json',receipts)
 dump('sheet_cards.json',[{'id':c['id'],'edition_ids':[e['edition_id'] for e in c['editions']],'samples':c['samples'],'group':c['group'],**({'year':c['year']} if 'year' in c else {})} for c in cards])
 return sorted(cards,key=lambda c:(('forced','test','dev','train').index(c['group']),c.get('year',''),c['id']))

def tables(counts):
 lines=['| Source × primary class | Train | Dev | Test | Total | 85/5/10 target rows | Plan class train quota (global) |','|---|---:|---:|---:|---:|---|---:|']
 for k,c in counts.items():
  n=sum(c.values());cl=k.split(' × ')[1];lines.append(f"| {k} | {c['train']:,} | {c['dev']:,} | {c['test']:,} | {n:,} | {n*.85:.1f}/{n*.05:.1f}/{n*.10:.1f} | {QUOTAS.get(cl,'not specified')} |")
 return '\n'.join(lines)

def report(editions,receipt,counts,conflicts,merges,stamp,cards):
 totals=collections.Counter();proposed=collections.Counter();forced=collections.Counter();classes=collections.defaultdict(collections.Counter)
 for e in editions:
  totals[e['proposed_split']]+=e['row_count'];(forced if e['forced'] else proposed)[e['proposed_split']]+=e['row_count']
  for k,n in e['rows_per_class'].items():classes[k][e['proposed_split']]+=n
 quota_table=['| Primary class | Proposed+forced train | Plan usable-train target | Difference (raw rows, not admission) |','|---|---:|---:|---:|']
 for k in sorted(set(classes)|set(QUOTAS)):
  n=classes[k]['train'];q=QUOTAS.get(k);quota_table.append(f'| {k} | {n:,} | {q if q is not None else "unspecified"} | {n-q if q is not None else "n/a"} |')
 leaks=[]
 for e in editions:
  if e['forced']:leaks.append(f"- `{e['edition_id']}` → **{e['proposed_split']}**, {e['row_count']:,} rows, {e['title']}: `"+canonical(e['leakage_matches'])+'`')
 partial=[d for e in editions for d in e['metadata'] if d['partial_bsb_w2']]
 text=f'''# SPLIT1 — edition split proposal, owner review pending

Built {stamp}. Network OFF, no OCR calls, no spend. This is a proposal; no final split, release manifest, live collector file, review database or remote branch was changed.

## Population and identity

Use **all {receipt['rows']:,} snapshot rows**: W1 {receipt['W1']['rows']:,}; W2 {receipt['W2']['rows']:,}. SHA256 files match the supplied checksum list. This exactly reproduces the census parent populations (see `split-repair-config.json` and `ASTRA_CSCS_REVIEW_20261018.json`), not the downstream **142,959 held** disposition subset. Difference {receipt['difference_from_held']:,}: other rows can receive other pipeline dispositions before that hold. We cannot reproduce which held rows without the census_03 row disposition output; no substitute admission filter was invented. Parent-qualified row IDs are retained, including any duplicate raw row IDs across parents ({len(receipt['duplicate_row_ids'])}).

Default unit = `<source>--<dochash>`. Edition ID = full SHA256 of newline-joined sorted member document IDs, no trailing newline. Merge by a shared metadata identifier (provider namespace, global DOI/URN) or normalized title + year + volume. Normalization: NFKD, casefold, remove combining marks and punctuation, collapse whitespace; no transliteration or fuzzy inference. Missing volumes remain empty under the owner's equality rule and are diagnostic questions. Gazette title includes issue number/type and its identifier is issue-specific; issues are never merged merely by year. OJS title includes the journal name. All member metadata, provenance and every merge edge are in `editions.jsonl`.

{len(editions):,} editions; {len(merges)} merge edges ({sum(len(e['member_documents'])-1 for e in editions)} scanned documents collapsed); {len([c for c in cards if 'year' in c])} Gazette year cards. Gazette issues retain independent edition IDs and proposals.

## Quotas and deterministic allocation

Source: `{PLAN}` **§3, “Stream B — targeted collection”, primary allocations table**, read with `DATA_PLAN_v2_CORRECTION_OA_20261016.md` (§1/§3 modern scanned provenance correction). §3 gives **202,000 usable train rows** across ten primary classes; it gives no train/dev/test ratio or per-source split quotas. Use the owner's fallback **85/5/10 by raw snapshot rows**. These raw rows are not an admission forecast; `greek_mono`, `greek_poly`, `nonletter` and unclassified have no separate plan quota. `poly1850` is a collector class and includes years outside 1850–1890: its 40,000 comparison is a class proxy, not proof of date-qualified quota coverage.

For each source × edition modal primary class (lexical tie-break), sort edition IDs, shuffle with Python Random seeded by `split1:<source>:<class>`, then stable sort by descending edition row count. Forced editions initialize counts. Greedily choose the split minimizing the change in squared deviation from 85/5/10 targets over every affected **source × row primary class**. Ties: TRAIN, DEV, TEST. No rows of an edition are split. Cross-source merges contribute their full class vector. Forced allocations may prevent target ratios; whole-edition rounding is reported, not repaired by row-level assignment.

| Rows | Train | Dev | Test |
|---|---:|---:|---:|
| Remaining editions proposed | {proposed['train']:,} | {proposed['dev']:,} | {proposed['test']:,} |
| Forced by v2 / registered eval | {forced['train']:,} | {forced['dev']:,} | {forced['test']:,} |
| Total proposal | {totals['train']:,} | {totals['dev']:,} | {totals['test']:,} |

'''+ '\n'.join(quota_table)+'\n\n'+tables(counts)+f'''

## Leakage and locked sides

{sum(e['forced'] for e in editions)} forced editions. URL comparison removes scheme and www, decodes escapes and strips trailing slash; identifiers are extracted from metadata and known IA/BSB/ELSTAT/Serbian URLs. Title+year uses the normalization above. V2 titles absent from row records are supplemented from local acquisition manifests bound by URL or document key; provenance is recorded. Every matched v2 document and match witness is listed below and in the machine ledger. V2 parent splits normalize val→dev and reserved→test. Registered `eval_only_dev` stays dev; locked evaluation and never-trains benchmark classes display on test, with the original class and witnesses retained. No other exclusion class forces a split. This sheet's “forced by v2” label includes the explicitly requested registered locked/eval evidence.

Conflicting forced-side evidence: {len(conflicts)}. Any conflict is listed in `input_verification.json`; displayed TEST > DEV > TRAIN is only an owner-review placeholder, never a final resolution.

'''+ ('\n'.join(leaks) or 'No exact metadata matches.')+'''

## Partial BSB and owner questions

The **10 BSB W2 documents are partial**. The 436 BSB pages read after 05:24 are absent from these snapshots and were not added. Listed documents:

'''+ '\n'.join(f"- `{d['document_id']}` — {d['item']}: {d['title']}" for d in partial)+'''

- The nine ELSTAT merged groups use annual generic bulletin titles with missing volume/month metadata and distinct provider IDs. They may be different monthly issues; inspect these proposed merges before accepting edition identity.
- Approve edition merges and missing-volume equalities; metadata matching does not certify transliterated or semantically equivalent titles. Missing v2 titles cannot be matched by title+year and are counted in verification.
- Resolve any conflicting locked/v2 sides shown above. Locked test display preserves the lock class; it does not authorize general test use.
- DROP of DEV/TEST proposes TRAIN; DROP of TRAIN proposes held-out, with DEV versus TEST left to the owner. No split is applied by this page.
- Gazette is grouped once per year. The issue selector changes the active edition; each issue has its own mark/note, split pill and stable persistence ID. Samples on a year card are two representative year rows, identified by issue/edition, rather than independent samples for every issue. This grouping keeps the requested page compact; the complete issue list shows every split and lock.
- Forced editions show the lock; marks cannot override their forced side. Notes remain editable. KEEP/DROP still records owner feedback on forced proposals.

## Owner sheet variant (local, unpublished)

| Kind | Owner decision | Mark | Inner frame | Changed rows |
|---|---|---|---|---|
| Edition split proposal (SPLIT1) | Accept split or move edition across train/held-out | KEEP accept; DROP other side | TRAIN green / DEV amber / TEST blue; forced label | Edition metadata, class counts, issue list; two crops with original Google text |

Rendered through the read-only reference `greekocr.adjudicate.owner_sheet.render`; frames, second crop and edition issue selector are post-processing. No invented previous tool version. Outer border = owner KEEP green / DROP red. Keys ↑↓, SPACE, z, b, Esc; lens 3×. Collection `notes`, IDs `split1:<edition_id>`, fields note/verdict/updated/line_id. Never writes on load, focus, hydration or blur without edit. No localStorage fallback and no publishing. The lead must dump notes before any republish and verify reloaded marks afterwards. `OWNER_REVIEW.html` is self-contained and requires the signed-in artifact db capability for persistence.
'''
 (HERE/'SPLIT_PROPOSAL.md').write_text(text)
 summary={'rows':receipt['rows'],'editions':len(editions),'merged':len(merges),'gazette_years':len([c for c in cards if 'year' in c]),'cards':len(cards),'forced':sum(e['forced'] for e in editions),'proposed_rows':dict(proposed),'forced_rows':dict(forced),'total_rows_by_split':dict(totals),'partial_bsb_w2_documents':len(partial),'stamp':stamp,'quotas_source':PLAN.name,'source_class_counts':counts}
 dump('summary.json',summary)
 return text,summary

if __name__=='__main__':
 stamp=subprocess.check_output(['date','+%Y-%m-%d %H:%M:%S %Z'],env={**os.environ,'TZ':'Europe/Athens'},text=True).strip()
 print('Reading snapshots',flush=True);rows,receipt=read_rows()
 print('Metadata',len(rows),flush=True);docs,files=metadata(rows);editions,doc2ed,merges=build_editions(docs,rows)
 print('Leakage',len(editions),flush=True);v2,rowdoc,vfiles=load_v2();efiles,conflicts=force_leakage(editions,rows,v2,rowdoc)
 counts=allocate(editions);write_proposals(rows,editions,doc2ed)
 receipt.update(metadata_files=files,v2_files=vfiles,exclusion_files=efiles,forced_side_conflicts=conflicts,v2_documents=len(v2),v2_documents_without_title=sum(not d['title_year'] for d in v2.values()))
 dump('input_verification.json',receipt)
 print('Crops',flush=True);cards=samples(rows,editions,doc2ed)
 report_text,summary=report(editions,receipt,counts,conflicts,merges,stamp,cards)
 from build_sheet import build_sheet
 build_sheet(cards,summary,counts)
 print(canonical(summary),flush=True)
