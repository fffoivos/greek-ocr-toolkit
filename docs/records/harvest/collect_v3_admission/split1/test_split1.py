"""Offline contract checks requested by SPLIT1; do not admit or assign rows."""
import base64,collections,copy,gzip,hashlib,json,random,re,subprocess,sys
from pathlib import Path
import pytest
from bs4 import BeautifulSoup
import build_split1 as b

@pytest.fixture(scope='module')
def artifacts():
 es=list(b.jsonl(b.HERE/'editions.jsonl'));receipt=json.loads((b.HERE/'input_verification.json').read_text())
 with gzip.open(b.HERE/'row_split_proposal.jsonl.gz','rt') as f:rs=[json.loads(l) for l in f]
 return es,rs,receipt

@pytest.fixture(scope='module')
def sheet():return BeautifulSoup((b.HERE/'OWNER_REVIEW.html').read_text(),'html.parser')

def test_snapshot_checksums(artifacts):
 _,_,r=artifacts
 for w in ('W1','W2'):assert b.digest(r[w]['path'])==r[w]['sha256']

def test_all_snapshot_rows_reconcile(artifacts):
 es,rs,r=artifacts;expected=[]
 for w in ('W1','W2'):
  for row in b.jsonl(r[w]['path']):expected.append((f'collect-v3-{w}-20261018-0524',row['id']))
 assert [(x['parent_id'],x['row_id']) for x in rs]==expected
 assert len(rs)==r['rows']==sum(e['row_count'] for e in es)==320479
 assert r['difference_from_held']==177520

def test_whole_edition_integrity(artifacts):
 es,rs,_=artifacts;by={e['edition_id']:e for e in es};counts=collections.Counter();sides=collections.defaultdict(set)
 for r in rs:
  e=by[r['edition_id']];assert r['proposed_split']==e['proposed_split'];assert r['forced']==e['forced'];sides[r['edition_id']].add(r['proposed_split']);counts[r['edition_id']]+=1
 assert all(len(s)==1 for s in sides.values());assert counts=={e['edition_id']:e['row_count'] for e in es}

def test_edition_ids_and_merges(artifacts):
 es,_,_=artifacts;docs=[]
 for e in es:
  assert e['edition_id']==hashlib.sha256('\n'.join(sorted(e['member_documents'])).encode()).hexdigest()
  assert len(e['merge_evidence'])==len(e['member_documents'])-1
  for m in e['merge_evidence']:assert set(m['documents'])<=set(e['member_documents']) and len(m['evidence'])==2
  docs.extend(e['member_documents'])
 assert len(docs)==len(set(docs))==1370

def test_seeded_allocation_determinism(artifacts):
 es,_,_=artifacts;a=copy.deepcopy(es);c=copy.deepcopy(es);random.Random(36).shuffle(c)
 for x in a+c:
  if not x['forced']:x['proposed_split']=None
 assert b.allocate(a)==b.allocate(c)
 assert {e['edition_id']:e['proposed_split'] for e in a}=={e['edition_id']:e['proposed_split'] for e in es}

def test_class_and_source_counts_reconcile(artifacts):
 es,rs,_=artifacts;summary=json.loads((b.HERE/'summary.json').read_text());totals=collections.Counter();sc=collections.defaultdict(collections.Counter)
 for e in es:
  assert sum(e['rows_per_class'].values())==sum(e['rows_per_source_class'].values())==e['row_count']
  totals[e['proposed_split']]+=e['row_count']
  for k,n in e['rows_per_source_class'].items():sc[k][e['proposed_split']]+=n
 assert dict(totals)==summary['total_rows_by_split']
 assert all({s:sc[k][s] for s in b.SPLITS}==v for k,v in summary['source_class_counts'].items())

def test_locked_and_v2_forcing(artifacts):
 es,rs,r=artifacts;by={e['edition_id']:e for e in es};rowmap={v['row_id']:by[v['edition_id']] for v in rs};reg=json.loads((b.EXDIR/'release_exclusions.json').read_text());witnesses=0
 for name,cl in reg['classes'].items():
  if not ('eval' in name or 'never trains' in str(cl.get('rule','')) or 'never admitted to training' in str(cl.get('rule',''))):continue
  for rid in (b.EXDIR/cl['file']).read_text().splitlines():
   if rid in rowmap:
    e=rowmap[rid];assert e['forced'];assert e['forced_split']==('dev' if name=='eval_only_dev' else 'test');witnesses+=1
 for e in es:
  if e['forced']:assert e['leakage_matches'] and e['proposed_split']==e['forced_split']
  for match in e['leakage_matches']:
   if 'v2_doc' in match:assert e['proposed_split']==match['v2_split']
 assert witnesses>0;assert sum(e['forced'] for e in es)==99;assert not r['forced_side_conflicts']

def test_leakage_match_modes_synthetic(monkeypatch):
 # Exercise all three matching paths even though this population has no direct v2 metadata matches.
 monkeypatch.setattr(b,'digest',lambda p:'sha')
 # Registry remains real; only the v2 metadata witness is synthetic and unmistakably distinct.
 for typ,meta,vd in [
  ('identifier',{'id':'archive_item'}, {'identifiers':{'archive_item'},'urls':set(),'title_year':set()}),
  ('url',{'source_url':'https://example.test/book'}, {'identifiers':set(),'urls':{'example.test/book'},'title_year':set()}),
  ('title_year',{'title':'Βιβλίο','year':1902}, {'identifiers':set(),'urls':set(),'title_year':{(b.norm('Βιβλίο'),'1902')}})]:
  # Keep real registry hash assertions active by returning its declared hashes.
  reg=json.loads((b.EXDIR/'release_exclusions.json').read_text());hashes={v['file']:v['sha256'] for v in reg['classes'].values()}
  monkeypatch.setattr(b,'digest',lambda p:hashes.get(p.name,'sha'))
  for side in b.SPLITS:
   e={'edition_id':'synthetic','metadata':[{'document_id':'d','records':[{'metadata':meta,'evidence':'synthetic'}],'year':1902}],'leakage_matches':[]}
   v2={('legacy',side):dict(vd,doc='legacy',split=side,metadata_evidence=set())}
   _,conflicts=b.force_leakage([e],[],v2,{})
   assert e['forced'] and e['proposed_split']==side and not conflicts
   assert any(typ in ev for ev in e['leakage_matches'][0]['evidence'])

def test_bsb_partial_and_gazette_issue_identity(artifacts):
 es,_,_=artifacts;assert sum(d['partial_bsb_w2'] for e in es for d in e['metadata'])==10
 gaz=[e for e in es if e['gazette']];assert len(gaz)==1163;assert all(len(e['member_documents'])==1 for e in gaz)


def test_regenerated_crop_shas():
 records=json.loads((b.HERE/'crop_receipts.json').read_text())
 for r in records:
  assert b.digest(b.HERE/r['path'])==r['crop_sha256']
  rebuilt,_=b.regenerate(r);assert hashlib.sha256(rebuilt).hexdigest()==r['crop_sha256']
 assert len(records)==410

def test_sheet_crops_and_original_google_text(sheet):
 receipts=json.loads((b.HERE/'crop_receipts.json').read_text());by={r['crop_sha256']:r for r in receipts};images=sheet.select('.card .zw img');assert len(images)==410
 for image in images:
  sha=hashlib.sha256(base64.b64decode(image['src'].split(',',1)[1])).hexdigest();assert sha in by
  wrapper=image.find_parent(class_='zw');table=wrapper.find_next_sibling('table');assert table.select_one('td').text==by[sha]['old_label']
 assert len(sheet.select('.card'))==205

def test_sheet_year_issue_ids_and_groups(sheet,artifacts):
 es,_,_=artifacts;script=sheet.find('script').string;payload=json.loads(script.split('const SPLIT1_CARDS = ',1)[1].split(';\n',1)[0]);ids=[e['edition_id'] for c in payload for e in c['entries']]
 assert len(ids)==len(set(ids))==len(es);assert set(ids)=={e['edition_id'] for e in es}
 assert len(sheet.select('.issue-select'))==9
 assert [h.text for h in sheet.select('main>h2')]==['Forced by v2 / registered evaluation — locked','TEST proposals','DEV proposals','TRAIN proposals']

def test_sheet_size_and_self_containment(sheet):
 assert (b.HERE/'OWNER_REVIEW.html').stat().st_size<10_000_000
 assert all(x['src'].startswith('data:image/png;base64,') for x in sheet.select('img'))
 assert not sheet.select('script[src],link[href]')

def test_live_javascript_no_write_on_load_and_events():
 result=subprocess.run(['node',str(b.HERE/'test_sheet_runtime.cjs')],cwd=b.HERE,text=True,capture_output=True)
 assert result.returncode==0,result.stdout+'\n'+result.stderr


def test_edition_identity_determinism(artifacts):
 es,_,_=artifacts;docs={d['document_id']:d for e in es for d in e['metadata']}
 rows=[{'document':d,'source':v['source'],'primary_class':'synthetic_count'} for d,v in docs.items()]
 first,_,merges=b.build_editions(docs,rows)
 second,_,other=b.build_editions(dict(reversed(list(docs.items()))),list(reversed(rows)))
 assert b.canonical(first)==b.canonical(second);assert b.canonical(merges)==b.canonical(other)
 assert {e['edition_id'] for e in first}=={e['edition_id'] for e in es}
