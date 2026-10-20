"""Offline R8-GEOM-02-i1 receipt/galleries; never imported by runtime."""
import hashlib,json
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from ..shared.geometry_columns import native_crossings
from .r8_geometry_review import correspond

R=Path('.astra/fast_lines/out/round8');O=R/'R8-GEOM-02-i1';B=R/'R8-04-i1/runtime'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False,default=lambda v:v.tolist() if hasattr(v,'tolist') else float(v))+'\n')
def render_controls(inputs):
    target=O/'controls';target.mkdir(exist_ok=True);records=[]
    for rec in read(R/'R8-04-i1/NATIVE_CONTROLS.json'):
        page=rec['page'];idx=rec['index'];q=read(B/f'{page}.json')['items'][idx];g=cv2.imread(inputs[page]['path'],0)
        a,b,c,d=rec['bounds'];raw=g[b:d,a:c];view=cv2.cvtColor(raw,cv2.COLOR_GRAY2BGR);pp=np.rint(np.asarray(q['polygon'])-[a,b]).astype(int);cv2.polylines(view,[pp],True,(0,150,0),1)
        mask=np.zeros(raw.shape,np.uint8);cv2.fillPoly(mask,[pp],1);cut=np.where(mask,raw,255).astype(np.uint8);stem=f'{page}-{idx}'
        cv2.imwrite(str(target/f'{stem}-context.png'),np.vstack([cv2.cvtColor(raw,cv2.COLOR_GRAY2BGR),view]));cv2.imwrite(str(target/f'{stem}-native.png'),cut)
        cv2.imwrite(str(target/f'{stem}-normalized.png'),cv2.resize(cut,None,fx=min(1,1400/cut.shape[1]),fy=min(1,1400/cut.shape[1]),interpolation=cv2.INTER_AREA))
        records.append(dict(rec,observation=('Accepted polygon and πό support unchanged. The independent check locates the hyphen at the crop edge; this polygon-masked rendering does not show a complete hyphen. No completeness claim or new repair.' if '466cff' in page else rec['observation']),review_scope='Restored checked runtime, fresh rendering; exact accepted polygon/support, inherited defect status',input_sha256=inputs[page]['sha256'],output_sha256=sha(B/f'{page}.json')))
    dump(O/'NATIVE_CONTROLS.json',records)

def c8_comparison(inputs):
    p='an-c8b96a901917-p000036';old=read(B/f'{p}.evidence.json');trial=read(O/'focus-repaired'/f'{p}.json');g=cv2.imread(inputs[p]['path'],0);rule=next(q for q in old['geometry']['columns']['rules'] if q['accepted']);slow=read(O/'c8-p36-slow-reference.json');h=old['geometry']['columns']['height']
    explicit=native_crossings(g,rule['rule'],h,'slow');fast=native_crossings(g,rule['rule'],h,'explicit');assert explicit==fast
    fs=trial['page_field']['proposal']['evidence']['fields'];bs=old['page_field']['proposal']['evidence']['fields'];domains=[]
    crops=[('heading',[450,635,2410,830]),('rule-start',[400,910,2430,1190]),('rule-end',[400,2550,2430,2830])]
    for name,(a,b,c,d) in crops:
        raw=Image.fromarray(g[b:d,a:c]).convert('RGB');panels=[raw.copy() for _ in range(3)]
        for panel,fields in zip(panels[:2],[bs,fs]):
            dr=ImageDraw.Draw(panel)
            for field in fields:
                x,y,z,w=field['region'];poly=field.get('domain',[[x,y],[z,y],[z,w],[x,w],[x,y]])
                dr.line([(xx-a,yy-b) for xx,yy in poly]+[(poly[0][0]-a,poly[0][1]-b)],fill=(0,100,240),width=2)
            dr.line([(x-a,y-b) for x,y in rule['rule']['path']],fill=(225,0,0),width=3)
            for side in ('left','right'):
                for q in rule['endpoints'][side]:
                    x,y=q['point'];dr.ellipse((x-a-3,y-b-3,x-a+3,y-b+3),fill=(200,0,200))
        dr=ImageDraw.Draw(panels[2])
        for row in slow['rows']:
            if row['discounted'] or row['x1']<a or row['x0']>c or max(row['bottom'])<b or min(row['top'])>d:continue
            for key,color in [('top',(0,150,0)),('bottom',(0,150,0)),('baseline',(180,0,180))]:dr.line([(x-a,y-b) for x,y in zip(range(row['x0'],row['x1']),row[key])],fill=color,width=1)
        sheet=Image.new('RGB',(c-a,4*(d-b)+100),'white');draw=ImageDraw.Draw(sheet)
        for i,(label,panel) in enumerate(zip(['Raw native','Accepted: blue field bounds / red finite rule','Rejected repair: finite domains, outside continuation unknown','Pixel-seeded slow rows (conditional guides, not truth)'],[raw,*panels])):
            y=i*(d-b+25);draw.text((3,y+3),label,fill='black');sheet.paste(panel,(0,y+25))
        image=f'c8-{name}.png';sheet.save(O/image);domains.append(dict(name=name,bounds=[a,b,c,d],image=image))
    # Original per-component identities/rough seeds remain in the slow receipt.
    comparison=dict(accepted=correspond(slow['rows'],read(B/f'{p}.json')['items']),rejected_trial=correspond(slow['rows'],trial['items']))
    dump(O/'C8_EXPLICIT.json',dict(page=p,rule=rule,explicit_crossing=explicit,fast_crossing_equal=True,native_images=domains,slow_reference_sha256=sha(O/'c8-p36-slow-reference.json'),slow_reference_seconds=slow['seconds'],slow_rule_boundaries=[q for q in slow['structure']['boundaries'] if q['kind']=='rule'],heading_slow_row=4,heading_slow_extent=[525,683.137,2297,793.793],accepted_heading_index=87,slow_limits='Heading is a single retained pixel-seeded row. The isolated right tick is not included in that slow extent. Slow rule acceptance is independent and can disagree; native M13 path remains the finite witness.',ordered_comparison=comparison,trial_status='Rejected for new glyph losses on other pages; no promoted domain repair'))

def timing():
    pairs=[]
    for i in (1,2):
        a=read(O/f'paired-base-{i}/receipt.json');b=read(O/f'paired-trial-{i}/receipt.json');aa={q['page']:q for q in a['records']};bb={q['page']:q for q in b['records']};assert aa.keys()==bb.keys();records=[]
        for p,x in aa.items():
            y=bb[p];records.append(dict(page=p,**{k+'_delta_ms':1000*(y[k]-x[k]) for k in ('correction_s','total_s','detector_s','decode_s')},stage_delta_ms={k:1000*(y['stages'].get(k,0)-x['stages'].get(k,0)) for k in set(x['stages'])|set(y['stages'])}))
        pairs.append(dict(order=i,n=len(records),summary={k:dict(total_ms=sum(r[k] for r in records),median_ms=float(np.median([r[k] for r in records]))) for k in ('correction_s_delta_ms','total_s_delta_ms','detector_s_delta_ms','decode_s_delta_ms')},stage_totals_ms={k:sum(r['stage_delta_ms'].get(k,0) for r in records) for k in sorted(set().union(*(r['stage_delta_ms'] for r in records)))},baseline_over1s=a['over1s'],trial_over1s=b['over1s'],baseline_distribution=a['summary'],trial_distribution=b['summary'],records=records,settings={k:a[k] for k in ('opencv','opencv_threads','onnx','model_sha256','timing')},baseline_source=a['source_sha256'],trial_source=b['source_sha256']))
    full=read(B/'receipt.json');dump(O/'TIMING.json',dict(scope='Fresh serial paired80 baseline/rejected trial, both source orders and reversed page order. No concurrent benchmark/profiler. Rejected trial is NOT the recommended runtime.',pairs=pairs,accepted_full208=full,accepted_runtime_delta='zero; source identical, no new full run after restoring',startup='Separate Stack construction, not included in per-page clocks; no startup time separately recorded by this runner'))
    text=['# R8-GEOM-02-i1 timing','', 'These fresh pairs measure the **rejected finite-domain implementation**. The recommended runtime is unchanged 54cc8f9. No speed improvement is claimed.','', '| Order / 80 pages | Correction sum delta ms | Median paired delta ms | Field stage sum delta ms | Detector delta ms | Decode delta ms |','|---|---:|---:|---:|---:|---:|']
    for r in pairs:text.append(f"| {r['order']} | {r['summary']['correction_s_delta_ms']['total_ms']:.3f} | {r['summary']['correction_s_delta_ms']['median_ms']:.3f} | {r['stage_totals_ms'].get('field_proposal_s',0):.3f} | {r['summary']['detector_s_delta_ms']['total_ms']:.3f} | {r['summary']['decode_s_delta_ms']['total_ms']:.3f} |")
    text+=['','The accepted full208 timing is source-bound reuse: correction median/p95/max 199.421/1287.272/2007.555 ms; 22 pages >1s. Full raw per-page/stage records and named lists are in TIMING.json. Nested stages are not summed. Detector drift is not subtracted.','', '## Accepted slow pages','']+['- '+p for p in full['over1s']]
    (O/'TIMING.md').write_text('\n'.join(text)+'\n')

def main():
    rows=read(R/'R8-01b/inputs-208.json')['pages'];inputs={r['page']:r for r in rows};sources=read(B/'source.json');assert len(sources)==190
    assert all(sha(p)==v for p,v in sources.items());dump(O/'runtime-source.json',sources);bindings=[]
    for r in rows:
        assert sha(r['path'])==r['sha256'];p=r['page'];files={str(B/f'{p}{tail}.json'):sha(B/f'{p}{tail}.json') for tail in ('','.evidence','.timing')};bindings.append(dict(page=p,input_sha256=r['sha256'],files=files,items=len(read(B/f'{p}.json')['items'])))
    dump(O/'REUSE_RECEIPT.json',dict(baseline='54cc8f9ead2809d3c7da11f5a8e9a87334d2df24',runtime_files=190,runtime_source_sha256=sha(O/'runtime-source.json'),input_manifest_sha256=sha(R/'R8-01b/inputs-208.json'),reason='All trial runtime edits withdrawn; exact checked runtime retained. User explicitly permits binding checked208 instead of repeating identical OCR.',fresh_full208=False,pages=bindings,items=sum(q['items'] for q in bindings)))
    for name in ('COMMENTS','ROWS','NO_SEED_ROWS'):
        source=R/'R8-03-i2'/f'{name}.json';data=read(source)
        for q in data:q['r8_geom02_i1']=dict(status='inherited accepted-runtime disposition; no promoted geometry fix',runtime='54cc8f9',evidence='REUSE_RECEIPT.json',note='All original fields preserved. Trials rejected. 466 hyphen lies at crop edge per independent check; completeness not established.')
        dump(O/f'{name}.json',data)
    dump(O/'PILOT_REUSE.json',dict(pages=read(R/'R8-04-i1/PILOT_REUSE.json'),status='23/127 inherited native review bound to unchanged final runtime; focused trial reviews are separate, not claimed as fresh all-mark adjudication',source_sha256=sha(R/'R8-04-i1/PILOT_REUSE.json')))
    render_controls(inputs);c8_comparison(inputs);timing()
    print('Bound190 runtime /208 inputs /624 artifacts; native controls, c8 explicit, paired timing and preserved ledgers')

if __name__=='__main__':main()
