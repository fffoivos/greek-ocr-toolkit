"""Offline, read-only input gallery builder. Writes only beside this script."""
import json, hashlib, collections, re, html
from pathlib import Path
from PIL import Image, ImageDraw
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
P=Path('/Users/foivoskarounos-zamparloukos/Projects')
W=P/'collect-v3-data/run/W1'
T=P/'greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked'
C=ROOT/'docs/harvest/collect_v3/c1'
EX=ROOT/'docs/harvest/collect_v3/release_exclusions'
def read(p):return json.loads(p.read_text())
def rows(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputs={}
def bind(p):inputs[str(p)]=sha(p)
verdicts=[]
for p in sorted((C/'verdicts').glob('*.jsonl')):
 bed=p.stem.rsplit('__',1)[0]; kp=W/'c1'/f'{bed}_key.json'; key=read(kp);bind(p);bind(kp)
 for r in rows(p):verdicts.append(dict(r,bed=bed,stage='C1',verdict_path=str(p),key_path=str(kp),line_id=key[r['card_id']]['line_id']))
for p in sorted((T/'checks/verdicts').glob('*.jsonl')):
 bed=p.stem.rsplit('__',1)[0]; kp=T/('cards_probe_supplement_key.json' if bed=='gazette_probe_supplement' else f'cards/{bed}_key.json');key=read(kp);bind(p);bind(kp)
 for r in rows(p):verdicts.append(dict(r,bed=bed,stage='T6b',verdict_path=str(p),key_path=str(kp),line_id=key[r['card_id']]['line_id']))
srk=T/'checks/kosmo_poly1850_sol/answers_mapped.jsonl';bind(srk)
for r in rows(srk):verdicts.append(dict(r,bed='kosmopolis_poly1850',stage='SRK',verdict_path=str(srk),key_path=str(T/'cards_kosmo_poly1850_sol_key.json')))
selected=[]
def pick(stage,bed,card,typ):
 r=next(x for x in verdicts if x['stage']==stage and x['bed']==bed and x['card_id']==card);selected.append(dict(r,type=typ))
probe='gazette_modern__modern_scanned__probe_1982_1985'
for c in ['c011','c015','c020','c025','c027']:pick('C1',probe,c,'merged_multi_line')
pick('T6b','gazette_probe_supplement','p025','merged_multi_line')
for stage,bed,c in [('C1','kosmopolis__poly1900','c052'),('C1','bsb_poly1850__poly1850','c057'),('C1','ia_poly1850__latin','c056'),('C1',probe,'c024'),('T6b','lekythos','c027'),('T6b','kosmopolis','c086')]:pick(stage,bed,c,'readable_half_line_overrun')
for bed,c in [('ia_poly1850__latin','c097'),('lekythos__poly1900','c094'),('nlg__greek_poly','c006'),('nlg__poly1850','c088')]:pick('C1',bed,c,'box_fragment')
for stage,bed,c in [('C1','ia_russian__cyrillic','c027'),('C1','nlg__poly1900','c031'),('T6b','kosmopolis','c056'),('SRK','kosmopolis_poly1850','c062')]:pick(stage,bed,c,'clipped_edge')
rot=set((EX/'w1_rotated_crop_ids.txt').read_text().splitlines()); bind(EX/'w1_rotated_crop_ids.txt')
# Card-linked rotated examples: release exclusion is the type authority even if crop_ok=y.
rotcards=[r for r in verdicts if r['line_id'] in rot and r['stage']=='T6b' and r['bed']=='gazette_modern']
selected.extend(dict(r,type='rotated_vertical_line') for r in rotcards[:3])
pick('C1','gazette_modern__modern_scanned__measured_1986_1990','c074','rotated_vertical_line')
needed={r['line_id'] for r in selected}; features={}; totals=collections.defaultdict(collections.Counter)
fp=W/'features.jsonl'
with fp.open() as f:
 for line in f:
  r=json.loads(line);s=r['source'];totals[s]['feature_rows']+=1;totals[s]['candidate_rows']+=bool(r.get('candidate_usable'));totals[s]['screen_merged']+=bool(r.get('screen_merged'));totals[s]['rotated_crop']+=r['id'] in rot
  if r['id'] in needed:features[r['id']]=r
bind(fp)
assert len(selected)==24 and len(features)==24,(len(selected),len(features))
examples=[]
for i,v in enumerate(selected,1):
 r=features[v['line_id']]; eid=f'sg1-{i:02}';crop_file=Path(r['crop']); im=(Image.open(crop_file).convert('RGB') if crop_file.is_file() else Image.open(r['crop_source_image']).convert('RGB').crop(r['crop_bbox']));h=im.height
 # Preserve exact Google-derived crop extent; no masking, recut, deskew or text reader.
 scale=min(2.,1000/im.width,64/im.height);size=tuple(max(1,round(x*scale)) for x in im.size)
 dest=OUT/f'{eid}-crop.png';im.resize(size,Image.Resampling.LANCZOS).save(dest,optimize=True)
 page=Path(r.get('crop_source_image',''));strip_path=None;strip_bounds=None
 if page.is_file():
  pageim=Image.open(page).convert('RGB');x0,y0,x1,y1=r['crop_bbox'];pad=max(h,round(r.get('page_median_row_height',h)*1.5));strip_bounds=[max(0,x0-pad),max(0,y0-pad),min(pageim.width,x1+pad),min(pageim.height,y1+pad)]
  a,b,c,d=strip_bounds;strip=pageim.crop(strip_bounds);draw=ImageDraw.Draw(strip);draw.rectangle([x0-a,y0-b,x1-a-1,y1-b-1],outline=(255,40,30),width=2)
  strip_scale=min(scale,1000/strip.width,260/strip.height);strip=strip.resize(tuple(max(1,round(z*strip_scale)) for z in strip.size),Image.Resampling.LANCZOS);strip_path=f'{eid}-strip.png';strip.save(OUT/strip_path,optimize=True)
 e=dict(id=eid,source=r['source'],**{'class':r['primary_class']},type=v['type'],line_id=r['id'],crop_height=h,label_text=r.get('literal_label',r['text']),card_verdict_detail=v['detail'],errors=v['errors'],crop_ok=v['crop_ok'],card_id=v['card_id'],verdict_stage=v['stage'],verdict_path=v['verdict_path'],key_path=v['key_path'],original_crop_path=r['crop'],original_crop_sha256=sha(crop_file) if crop_file.is_file() else None,expected_crop_sha256=r['crop_sha256'],crop_reconstructed_from_page=not crop_file.is_file(),crop_bbox=r['crop_bbox'],google_bbox=r['bbox'],page_raster=str(page),image_paths={'crop':dest.name,'page_strip':strip_path},scale=scale,strip_scale=strip_scale if strip_path else None,strip_bounds=strip_bounds,screen_merged=r['screen_merged'],rotated_release_excluded=r['id'] in rot,type_basis='release_exclusions rotated_crop plus card association' if v['type']=='rotated_vertical_line' else 'verdict error tags and detail',classification_note='crop_clipped witness; full printed-row extent is not independently annotated' if v['type']=='box_fragment' else None)
 examples.append(e)
(OUT/'examples.jsonl').write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in examples))
c1res=C/'c1_results.json';t6res=T/'checks/t6b_results.json';pop=T/'population.json'
for p in [c1res,t6res,pop,EX/'release_exclusions.json']:bind(p)
def score(vs):
 n=len(vs);tags=collections.Counter(t for v in vs for t in set(v['errors']));return dict(n=n,crop_ok_y=sum(v['crop_ok']=='y' for v in vs),error_counts=dict(tags),overrun_per_100=100*tags['crop_overrun']/n if n else None,clipped_per_100=100*tags['crop_clipped']/n if n else None)
per={}
for s,t in sorted(totals.items()):
 cv=[v for v in verdicts if v['stage']=='C1' and v['line_id'].startswith(s+'--')];tv=[v for v in verdicts if v['stage']=='T6b' and v['line_id'].startswith(s+'--') and v['bed']!='gazette_probe_supplement'];per[s]=dict(t,C1=score(cv),T6b=score(tv),T6b_population=read(pop).get(s,'not measured'),screen_merged_fraction_of_feature_rows=t['screen_merged']/t['feature_rows'],rotated_fraction_of_feature_rows=t['rotated_crop']/t['feature_rows'])
searched=[str(P/'greek-page-ocr/docs/ocr_program_2026-10-06'),str(P/'greek-ocr-toolkit/docs/labelfix'),str(P/'greek-ocr-toolkit/docs/harvest/analysis/C_geometry_quality'),str(ROOT/'docs/O4D_GEOMETRY.md'),str(P/'greek-ocr-toolkit/tests/fixtures/o4d_sample400')]
e3=P/'greek-page-ocr/docs/ocr_program_2026-10-06/E3_RESULTS.md';bind(e3)
counts=dict(schema='SG1-v1',denominators={'feature_rows':'All W1 features, including screened rows.','candidate_rows':'W1 candidate_usable=true; screen_merged/rotated counts use all feature rows, not this filtered denominator.','rates':'Unique cards per source/stage, per 100; verdict tags authoritative. C1 strata pooled; T6b main cards only. Probe supplement kept separately.','comparison':'Unpaired, different source/class/date and screening mixes; no causal masking-fixed fraction can be estimated.'},per_source=per,per_bed={stage:{bed:score([v for v in verdicts if v['stage']==stage and v['bed']==bed]) for bed in sorted({v['bed'] for v in verdicts if v['stage']==stage})} for stage in ['C1','T6b','SRK']},T6b_population_snapshot=read(pop),release_rotated_crop=read(EX/'release_exclusions.json')['classes']['rotated_crop'],v2_wide={'length_mismatch':{'test_line_percent':2.8,'edit_percent':44,'lines':1188,'edits':15011,'threshold':'prediction versus label length differs by >=3 NFD atoms','provenance_path':str(e3),'provenance_line':27},'printed_rows_without_google_box':{'value':'not found','requested_figure_percent':19,'searched_paths':searched}},no_box_examples={'status':'none available','count':0,'searched_paths':searched,'reason':'No locally traced annotated missing-row witness with page/region and absent Google box established; no new reading performed.'},masking_fixed_fraction_by_type={t:'not identifiable from unpaired C1 and T6b crop_ok samples' for t in ['merged_multi_line','readable_half_line_overrun','box_fragment','rotated_vertical_line','clipped_edge','missing_row']},auxiliary_results={'CAPS1':'keys/build/scan exist; no scored verdict/results found under caps1','SRK':str(T/'checks/kosmo_poly1850_sol/results.json')},gallery={'examples':len(examples),'per_type':dict(collections.Counter(e['type'] for e in examples)),'page_strips':sum(bool(e['image_paths']['page_strip']) for e in examples),'png_bytes':sum(p.stat().st_size for p in OUT.glob('*.png'))},input_sha256=inputs)
# Retain reported summary numbers without confusing truncated top_errors with all errors.
counts['reported_results']={'C1':read(c1res),'T6b':read(t6res)}
(OUT/'counts.json').write_text(json.dumps(counts,ensure_ascii=False,indent=2)+'\n')
parts=[]
for s in ['gazette_modern','kosmopolis','lekythos']:
 d=per[s];a=d['C1'];b=d['T6b'];parts.append(f"{s}: crop_ok {a['crop_ok_y']}/{a['n']} → {b['crop_ok_y']}/{b['n']}, overrun {a['overrun_per_100']:g} → {b['overrun_per_100']:g} per 100, clipped {a['clipped_per_100']:g} → {b['clipped_per_100']:g} per 100; screen_merged {d['screen_merged']}/{d['feature_rows']}, current rotated_crop {d['rotated_crop']}/{d['feature_rows']}")
(OUT/'NOTE.md').write_text('Masking comparisons are unpaired observations across different screened populations, so the fraction fixed for each failure type is not identifiable from crop_ok: '+'; '.join(parts)+'. Screening counts overlap and must not be added; T6b population records an older rotation rule separately in counts.json. Merged multi-line crops missed by screen_merged, box fragments and missing printed rows remain open; crop_clipped tags alone do not establish whole-row fragment extent. No-box examples: none available in the searched evidence, and the requested missing-row prevalence was not found. All quoted numbers are in counts.json.\n')
# Reviewable local HTML, no scripts, external assets or network.
body=''.join(f"<article><h2>{e['id']} · {e['type']}</h2><p>{html.escape(e['source'])} · {html.escape(e['class'])} · {e['verdict_stage']} {e['card_id']} · scale {e['scale']:.3f}×</p><img src='{e['image_paths']['crop']}'><p>{html.escape(e['label_text'])}</p><p>{html.escape(e['card_verdict_detail'])}</p>"+(f"<img src='{e['image_paths']['page_strip']}'>" if e['image_paths']['page_strip'] else '')+'</article>' for e in examples)
(OUT/'index.html').write_text("<!doctype html><meta charset='utf-8'><title>SG1 segmentation gallery</title><style>body{font:16px system-ui;max-width:1250px;margin:30px auto;background:#eee}article{background:white;padding:20px;margin:24px 0}img{max-width:100%;display:block;border:1px solid #aaa}p{overflow-wrap:anywhere}</style><h1>Google line-segmentation failures</h1><p>Original cached Google-derived crop extent, resized only (up to 2×; per-image scale in examples.jsonl). Red rectangle in page strips is crop_bbox, including cached crop padding. No new OCR or transcription. Fragment witnesses are provisional where full-row extent lacks annotation. Rotated cards use release-exclusion evidence even when crop_ok was scored yes. No missing-row witness was available.</p>"+body)
assert counts['gallery']['png_bytes']<6_000_000
print(json.dumps(counts['gallery']))
