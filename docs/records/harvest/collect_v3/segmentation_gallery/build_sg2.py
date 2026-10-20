"""Offline SG2; all writes confined to this script's directory."""
import ast, collections, gzip, hashlib, json, pathlib, random, subprocess
from PIL import Image, ImageDraw
OUT=pathlib.Path(__file__).resolve().parent
REPO=pathlib.Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit')
COMMIT='22dd16e4d35da61816ddde11533a5eb14cc81f4c'
def show(p): return subprocess.check_output(['git','-C',str(REPO),'show',COMMIT+':'+p])
def records(p):return [json.loads(x) for x in show(p).splitlines()]
ns={'random':random,'defaultdict':collections.defaultdict}
tree=ast.parse(show('greekocr/labelfix/geometry/io.py'))
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='sample_pages')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'archived sample_pages','exec'),ns)
pages=records('docs/labelfix/geometry/missed_rows/pages.jsonl')
keys=ns['sample_pages']([(p['wave'],p['page_id']) for p in pages if p['split']=='test' and p['status']=='measured' and p['fitted_detector_rows']>0],50,2026101604)
judgments=records('docs/labelfix/geometry/adjudication_20261016/page_adjudication.jsonl')
def load(i):
 k=keys[i-1];p=next(p for p in pages if (p['wave'],p['page_id'])==k)
 image=REPO/p['image'];assert hashlib.sha256(image.read_bytes()).hexdigest()==p['image_sha256']
 a=pathlib.Path(p['assignment']);a=a if a.exists() else a.with_suffix('.json.gz')
 raw=gzip.open(a,'rb').read() if a.suffix=='.gz' else a.read_bytes()
 d=json.loads(raw);assert d['page']['image_sha256']==p['image_sha256']
 return p,image,a,d

def admitted_ids():
 ids=set()
 for split in ['test','train']:
  for line in (REPO/f'docs/harvest/collection/v2/import_real_v2_{split}.jsonl').open():
   r=json.loads(line);ids.add((r['wave'],r['id']))
 return ids

if __name__=='__main__':
 import html
 ids=admitted_ids()
 origin='0dc29bf2163d26ce9ff6788b0861e70eb77d7150'
 report='docs/labelfix/geometry/REPORT.md'
 snapshots={
  'sg2-source-REPORT.md':(origin,report),
  'sg2-source-page_adjudication.jsonl':(origin,'docs/labelfix/geometry/adjudication_20261016/page_adjudication.jsonl'),
  'sg2-source-CENSUS.md':(COMMIT,'docs/labelfix/geometry/missed_rows/CENSUS.md'),
 }
 bindings=[]
 for dest,(commit,path) in snapshots.items():
  data=subprocess.check_output(['git','-C',str(REPO),'show',commit+':'+path]);(OUT/dest).write_bytes(data)
  bindings.append(dict(commit=commit,path=path,local_copy=dest,sha256=hashlib.sha256(data).hexdigest()))
 specs=[
  (2,[205,520,1505,850],['-l0010','-l0013'],[], 'Short paragraph endings D-9. and εισόδου. have no admitted box. Both have archived raw Google boxes (cyan); this is admission loss, not proof of a Google detector omission.'),
  (7,[285,1565,1785,2600],['-l0028'],['-l0056','-l0058'], 'ΝΟΜΟΣΧΕΔΙΟΝ has no admitted box. The two blue merged-box witnesses have identical extents [328,2374,1743,2484] over two printed rows, but different labels. The heading has a raw Google box.'),
  (15,[65,1510,1605,3000],['-l0050','-l0052','-l0054','-l0055','-l0056'],['-l0031','-l0033'], 'Ἄρθρ. 5 and the final α–γ list have no admitted boxes. Raw boxes exist. The identical blue box pair at [105,1761,1519,1914] spans slanted rows; labels differ. Red marks use raw extents as locators, not independently fitted row truth.'),
 ]
 examples=[];inputs=[]
 for j,(i,bounds,miss,merged,note) in enumerate(specs,1):
  p,path,assignment,d=load(i);raw=d['docai_lines'];records=d['records'];admitted=[r for r in records if (p['wave'],r['id']) in ids]
  missing=[r for r in records if any(r['id'].endswith(z) for z in miss)]
  assert len(missing)==len(miss) and all((p['wave'],r['id']) not in ids for r in missing)
  merges=[r for r in admitted if any(r['id'].endswith(z) for z in merged)]
  if merges:assert len(merges)==2 and merges[0]['bbox']==merges[1]['bbox']
  im=Image.open(path).convert('RGB').crop(bounds);scale=min(1,950/im.width)
  im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
  dr=ImageDraw.Draw(im)
  def box(b):return [(b[0]-bounds[0])*scale,(b[1]-bounds[1])*scale,(b[2]-bounds[0])*scale,(b[3]-bounds[1])*scale]
  admitted_boxes={tuple(r['bbox']) for r in admitted}
  for r in raw:
   if tuple(r['bbox']) not in admitted_boxes:dr.rectangle(box(r['bbox']),outline='#65bfc5',width=1)
  for r in admitted:dr.rectangle(box(r['bbox']),outline='#005dcc',width=2)
  for r in missing:
   b=box(r['bbox']);dr.rectangle([b[0]-4,b[1]-4,b[2]+4,b[3]+4],outline='#cf163e',width=2)
  for r in merges:dr.text((box(r['bbox'])[0]+5,box(r['bbox'])[1]+3),'MERGED x2',fill='#005dcc',stroke_width=1,stroke_fill='white')
  eid=f'sg2-{j:02}';dest=OUT/f'{eid}-strip.png';im.quantize(colors=64,method=Image.Quantize.MEDIANCUT).save(dest,optimize=True)
  jdg=judgments[i-1];assert jdg['page_id']==f'P{i:03}'
  e=dict(id=eid,type='no_google_box',box_scope='no admitted Google box; raw Google boxes retained in cyan',page_id=p['page_id'],pilot_page_id=f'P{i:03}',source=p['wave'],page_raster=str(path),page_raster_sha256=p['image_sha256'],assignment_path=str(assignment),assignment_sha256=hashlib.sha256(assignment.read_bytes()).hexdigest(),image_paths={'page_strip':dest.name},strip_bounds=bounds,strip_scale=scale,google_boxes=[dict(id=r['id'],bbox=r['bbox']) for r in admitted],archived_google_boxes=[r['bbox'] for r in raw],missed_rows=[dict(id=r['id'],locator_bbox=r['bbox'],raw_google_box_present=True) for r in missing],merged_boxes=[dict(id=r['id'],bbox=r['bbox'],label=r.get('label')) for r in merges],classification_note=note,adjudication=jdg,provenance=dict(commit=origin,path='docs/labelfix/geometry/adjudication_20261016/page_adjudication.jsonl',line=i),png_bytes=dest.stat().st_size)
  examples.append(e);inputs.extend([dict(path=str(path),sha256=p['image_sha256']),dict(path=str(assignment),sha256=e['assignment_sha256'])])
 exfile=OUT/'examples.jsonl';old=[json.loads(x) for x in exfile.read_text().splitlines() if json.loads(x)['type']!='no_google_box'];exfile.write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in old+examples))
 counts=json.loads((OUT/'counts.json').read_text());counts['v2_wide']['printed_rows_without_google_box']=dict(value=100*501/2624,unit='percent',requested_figure_percent=19,status='found',commit=origin,path=report,line=398,provenance_commit=origin,provenance_path=report,provenance_line=398,pages=50,printed_rows=2624,boxed_rows=2123,missed_rows=501,merged_rows=27,split_rows=6,headings_table_cells_unboxed=138,boxed_percent=100*2123/2624,evidence_kind='archived AI visual adjudication; not independent human truth',box_scope='admitted Google boxes in G1c pilot; not all archived raw Google boxes',raw_box_counterexample='P002 D-9., εισόδου. and page number 23 have raw Google boxes but no admitted boxes',census=dict(commit=COMMIT,path='docs/labelfix/geometry/missed_rows/CENSUS.md',lines=[3,15],detector_rows=76154,missed=6514,percent=8.55,criterion='at least 30% of occupied ink columns outside all archived Google boxes; partial overlap allowed',comparable_to_pilot=False),supporting_records=dict(commit=origin,path='docs/labelfix/geometry/adjudication_20261016/page_adjudication.jsonl',lines=[1,50]))
 total=sum(f.stat().st_size for f in OUT.glob('*.png'));assert total<6000000,total
 counts['sg2']=dict(no_google_box_strips=len(examples),box_scope='admitted pilot boxes',png_bytes_total=total,all_archived_google_box_absence_claimed=False)
 (OUT/'counts.json').write_text(json.dumps(counts,ensure_ascii=False,indent=2)+'\n')
 index=(OUT/'index.html').read_text().split('<!-- SG2 -->')[0].replace('SG1 segmentation gallery','SG1 + SG2 segmentation gallery').replace('No missing-row witness was available.','SG2 adds three page-strip witnesses below, with the admitted/raw-box distinction made explicit.')
 section='''<!-- SG2 --><section id="sg2"><h1>SG2 · missing admitted boxes</h1><p><strong>Scope correction:</strong> the archived 81% result is coverage by admitted Google boxes, not every raw Google box. On these strips, blue = admitted Google boxes; thin cyan = other archived Google boxes; red = printed rows absent from the admitted set. A red-marked row can still have a cyan raw box. These are admission-loss witnesses, not evidence of zero raw Google overlap.</p><p>The 16 Oct pilot counted 2,624 printed rows on 50 pages: 2,123 boxed (80.9%), 501 missed (19.1%), 27 merged and 6 split. Source: 0dc29bf21, REPORT.md:398. The later G1d 8.55% detector-row census uses all raw boxes and a different definition. AI visual judgments; no new OCR or dataset changes.</p><p><a href="sg2-source-REPORT.md">Archived report</a> · <a href="sg2-source-page_adjudication.jsonl">50 page judgments</a> · <a href="sg2-source-CENSUS.md">G1d census definition</a> · <a href="sg2_validation.json">SG2 receipt</a></p>'''
 for e in examples:section+=f'<article><h2>{e["id"]} · {e["pilot_page_id"]} · no_google_box (admitted scope)</h2><p>{html.escape(e["page_id"])}</p><p>{html.escape(e["classification_note"])}</p><img src="{e["image_paths"]["page_strip"]}" alt="{html.escape(e["classification_note"],quote=True)}"><p>Native bounds: {e["strip_bounds"]}; scale {e["strip_scale"]:.3f}×. Archived page judgment: {html.escape(e["adjudication"]["notes"])}</p></article>'
 (OUT/'index.html').write_text(index+section+'</section>\n')
 # Preserve selection reconstruction separately: archived sampler and frozen census input, no detector rerun.
 by_page=collections.defaultdict(list)
 for split in ['test','train']:
  for line in (REPO/f'docs/harvest/collection/v2/import_real_v2_{split}.jsonl').open():
   r=json.loads(line);by_page[(r['wave'],r['id'].rsplit('-l',1)[0])].append(r['id'])
 recovered=[]
 for i,k in enumerate(keys,1):
  p=next(p for p in pages if (p['wave'],p['page_id'])==k)
  recovered.append(dict(blind_id=f'P{i:03}',wave=k[0],page_id=k[1],source=p['image'],source_sha256=p['image_sha256'],line_ids=by_page[k]))
 recovered_bytes=''.join(json.dumps(r,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n' for r in recovered).encode()
 inventory=show('docs/labelfix/geometry/FILES.tsv').decode().splitlines()
 entry=next(l for l in inventory if l.startswith('docs/labelfix/geometry/artifacts-repairs/sealed/page_index.jsonl\t'))
 _,_,expected_size,expected_sha=entry.split('\t')
 assert len(recovered_bytes)==int(expected_size) and hashlib.sha256(recovered_bytes).hexdigest()==expected_sha
 (OUT/'sg2-recovered-page_index.jsonl').write_bytes(recovered_bytes)
 (OUT/'sg2-source-page_index-files-receipt.tsv').write_text(entry+'\n')
 selection=[dict(pilot_page_id=f'P{i+1:03}',wave=k[0],page_id=k[1]) for i,k in enumerate(keys)]
 (OUT/'sg2_pilot_selection.json').write_text(json.dumps(dict(method='Archived sample_pages, seed 2026101604, measured fitted test pages from G1d page census; reconstructed because ignored sealed/page_index.jsonl is unavailable',commit=COMMIT,pages=selection),indent=2)+'\n')
 validation=dict(schema='SG2-v1',network_used=False,detector_or_ocr_run=False,writes_scope=str(OUT),source_snapshots=bindings,inputs=inputs,selection_reconstructed=True,selection_crosschecks='Reconstructed full sealed page index matches archived FILES.tsv SHA-256 and size exactly',examples=len(examples),merged_box_pairs=2,png_bytes_total=total,png_limit_bytes=6000000,recovered_page_index_sha256=expected_sha,recovered_page_index_matches_archived_receipt=True,raw_absence_verified=False,limitation='The requested 19% provenance is found, but its no-box meaning is admitted scope. These strips do not claim raw Google detection failures.',visual_review='pending')
 (OUT/'sg2_validation.json').write_text(json.dumps(validation,indent=2)+'\n')
 (OUT/'SG2.md').write_text('''# SG2 provenance and page strips\n\nThe original result is in `0dc29bf2163d26ce9ff6788b0861e70eb77d7150:docs/labelfix/geometry/REPORT.md:398`, supported by 50 page judgments. It was introduced in G1c on 16 Oct and retained in G1d. 501/2624 = 19.09%; 2123/2624 = 80.91%.\n\nThe pilot overlays contain admitted boxes. P002 is a concrete counterexample to reading the 19% as absence of a raw Google detection: both short final rows and the page number have raw boxes. The strips preserve this distinction visibly: blue admitted, cyan other raw boxes, red no admitted box. Two merged pairs are also shown. The later G1d census uses all raw boxes, detector rows rather than printed rows, and permits partial coverage; its 8.55% is a separate measurement. No OCR, detector, checkout, network access or input mutation.\n\nThe original ignored sealed page index was unavailable. Membership was reconstructed with the archived sampler and seed, using frozen measured test-page census records. The complete reconstructed sealed page index matches the archived FILES.tsv SHA-256 and size exactly (78,707 bytes). The selected source rasters match their archived SHA-256 hashes. JSON records retain native coordinates and box lists. `sg2_validation.json` records custody and limitations.\n\nRebuild offline with the existing workspace Python: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/harvest/collect_v3/segmentation_gallery/build_sg2.py`. Run after the SG1 builder, which rebuilds its own files.\n''')
 for f in OUT.glob('sg2-preview-*.jpg'):f.unlink()
 print(json.dumps(dict(provenance=origin+':'+report,no_box_strips=len(examples),png_bytes_total=total)))
