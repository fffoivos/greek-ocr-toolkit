"""Read-only CP5 census. Stdout only; native crops unchanged; no reading/OSD."""
import hashlib
import io
import json
import os
from pathlib import Path
import socket
import sys
from collections import Counter
from copy import deepcopy

ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from PIL import Image
import greekocr.pages
from greekocr.glyphs import orientation
from greekocr.harvest import geometry_observations as g
from greekocr.harvest import orientation_screen as s
from greekocr.harvest import separator_inventory as separators
from greekocr.harvest.admission import evaluate, non_segmentation_eligibility, page_medians, _page_key
from greekocr.harvest.seg_qualification import composed_requirements
from test_seg_cp5 import writing
SEG=ROOT/'docs/harvest/collect_v3_admission/seg'
RUN=Path.home()/'Projects/collect-v3-data/run'
HIST=Path.home()/'Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_exclusions/w1_rotated_crop_ids.txt'


def main():
    attempts=[]
    def forbidden(*args,**kwargs):
        attempts.append(str(args));raise AssertionError('detector/reader/network forbidden')
    greekocr.pages.process_page=orientation._osd=orientation.recognizer_polarity=forbidden
    def audit(event,args):
        if event=='open':
            _,mode,flags=args
            if (mode and any(c in mode for c in 'wax+')) or flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
                forbidden('write',args[0])
        if event in ('os.mkdir','os.rename','os.remove','os.rmdir','os.link','os.symlink','os.chmod','os.truncate') or event.startswith('socket.') or event=='subprocess.Popen':
            forbidden(event)
    sys.addaudithook(audit)
    historical=HIST.read_text().split(); assert len(historical)==len(set(historical))==1681
    ledger=json.loads((SEG/'calibration_ledger.json').read_text())
    truth={c['row_id']:c['truth'] for c in ledger['cases']}
    rotated={w['row_id'] for w in ledger['gallery_witnesses'] if w['type']=='rotated_vertical_line'}
    ids=set(historical)|set(truth)|rotated
    fp=Path(os.environ['SEG_FEATURE_SNAPSHOT']);before=g.sha(fp)
    assert fp.resolve().parent == Path.home()/'Projects/collect-v3-data/snapshots'
    features={}
    with fp.open() as stream:
        for raw in stream:
            row=json.loads(raw)
            if row['id'] in ids:
                if row['id'] in features:raise ValueError('duplicate crop')
                features[row['id']]=row
    assert g.sha(fp)==before,'feature drift during snapshot'
    with fp.open() as stream:
        medians=page_medians(json.loads(raw) for raw in stream if raw.strip())
    cases=[]; source_image=None; source_key=None
    region_key=None; page_regions=[]
    for i,rid in enumerate(sorted(ids)):
        record=features.get(rid)
        base=dict(row_id=rid,historical=rid in historical,
                  truth=truth.get(rid),adjudicated_rotated=rid in rotated)
        try:
            if record is None:raise ValueError('missing pre-screen record')
            path=Path(record['crop'])
            if path.exists():
                before_crop=g.sha(path)
                if before_crop!=record['crop_sha256']:raise ValueError('crop hash mismatch')
                with Image.open(path) as opened: im=opened.convert('L')
                origin='existing_png'
            else:
                # Same original source/box/PNG encoder as collector pipeline.py:79.
                # Bytes stay in memory; no PNG is created or altered on disk.
                key=(record['crop_source_image'],record['crop_source_sha256'])
                if key!=source_key:
                    if g.sha(key[0])!=key[1]:raise ValueError('source hash mismatch')
                    with Image.open(key[0]) as opened:
                        if getattr(opened,'n_frames',1)!=1:raise ValueError('ambiguous source frame')
                        source_image=opened.convert('L')
                    source_key=key
                im=source_image.crop(record['crop_bbox'])
                encoded=io.BytesIO();im.save(encoded,format='PNG',compress_level=3)
                before_crop=hashlib.sha256(encoded.getvalue()).hexdigest()
                if before_crop!=record['crop_sha256']:raise ValueError('in-memory original PNG hash mismatch')
                origin='source_bound_byte_identical_in_memory'
            # No isolated-line assumption for suspected multi-row originals.
            m=s.observe_orientation(im)
            if m['decision']['axis']=='unknown':
                key=(record['crop_source_image'],record['crop_source_sha256'])
                if key!=region_key:
                    if g.sha(key[0])!=key[1]:raise ValueError('regional source hash mismatch')
                    with Image.open(key[0]) as opened:
                        if getattr(opened,'n_frames',1)!=1:raise ValueError('ambiguous regional source frame')
                        page_regions=s.measure_page_regions(opened.convert('L'))
                    region_key=key
                m=s.inherit_regional_axis(m,record['crop_bbox'],page_regions,
                    page_binding=dict(source=key[0],source_sha256=key[1],frame=0))
            if path.exists():assert g.sha(path)==before_crop
            text_flags=evaluate(record,page_median_height=medians.get(_page_key(record)))['checks']
            text_rejections=non_segmentation_eligibility(text_flags)['rejections']
            cases.append(dict(base,text_rules=dict(passed=not text_rejections,rejections=text_rejections),crop=str(path),crop_sha256=before_crop,
                primary_class=record['primary_class'],dataset_source=record['source'],
                old_rotated_crop=dict(membership=rid in historical,
                    tall_text=im.height>im.width and len(''.join(record['label'].split()))>=4),
                origin=origin,source=record['crop_source_image'],source_sha256=record['crop_source_sha256'],
                crop_bbox=record['crop_bbox'],orientation=m))
        except (ValueError,OSError,KeyError) as error:
            cases.append(dict(base,orientation=dict(status='unavailable',rotated=None,reason=str(error))))
        if (i+1)%200==0:print(f'CP5 measured {i+1}/{len(ids)}',file=sys.stderr,flush=True)
    by_id={c['row_id']:c for c in cases}
    controls=[]
    for text in ('λόγος','123456','ΟΙ','12'):
        for angle in (0,90,270):
            for unit in ('line','block'):
                m=s.observe_orientation(writing(text,angle),isolated_line=unit=='line',
                    content_kind='numbers' if text.isdigit() else 'unknown')
                controls.append(dict(id=f'{text}-{angle}-{unit}',text=text,primary_class='numerics_tables' if text.isdigit() else 'headings_caps',expected_rotated=angle!=0,
                                     orientation=m))
    for name,im,expected in (
        ('tall_heading',writing('ΟΙ',pad=(2,100,2,100)),False),
        ('tall_numeric',writing('12',pad=(2,100,2,100)),False),
        ('wide_padded_vertical',writing(angle=90,pad=(300,10,300,10)),True),
        ('sloped_horizontal',writing().rotate(8,expand=True,fillcolor=255),False),
        ('uncertain_square',Image.new('L',(70,70),255),None)):
        controls.append(dict(id=name,text='12' if name=='tall_numeric' else 'ΟΙ' if name=='tall_heading' else 'λόγος καὶ λόγος',primary_class='numerics_tables' if name=='tall_numeric' else 'headings_caps' if name=='tall_heading' else 'greek_mono',expected_rotated=expected,
            orientation=s.observe_orientation(im,isolated_line=name!='uncertain_square',
                         content_kind='numbers' if name=='tall_numeric' else 'unknown')))
    keeps=[c for c in cases if c['truth']=='keep']
    positives=[by_id[r] for r in sorted(rotated)]
    hist=[c for c in cases if c['historical']]
    def coverage(rows):
        return dict(required=len(rows),axes=dict(Counter(c['orientation'].get('decision',{}).get('axis','unavailable') for c in rows)),
                    statuses=dict(Counter(c['orientation']['status'] for c in rows)),
                    polarity_known=sum(c['orientation'].get('decision',{}).get('orientation_cw') is not None for c in rows))
    cp4=json.loads(Path(os.environ.get('SEG_CP4_VERIFICATION',str(SEG/'CP5_cp4_verification.json'))).read_text())
    assert cp4['binding']==g.implementation_binding() and cp4['ledger_sha256']==g.sha(SEG/'calibration_ledger.json')
    cp4_by={c['row_id']:c for c in cp4['cases']}
    # Matrix for the selected KEEP/DROP development ledger only. Historical
    # heuristic ids are never labelled positives by their membership alone.
    def matrix(values, labels=truth):
        out=dict(tp=0,fp=0,fn=0,tn=0,unknown=0)
        for rid,expected in labels.items():
            if expected not in ('keep','drop'):continue
            value=values.get(rid)
            out['unknown' if value is None else 'tp' if expected=='drop' and value else
                'fn' if expected=='drop' else 'fp' if value else 'tn']+=1
        def metric(n,d):
            if not d:return dict(numerator=n,denominator=d,value=None,wilson95=None)
            z=1.959963984540054;p=n/d;den=1+z*z/d;c=(p+z*z/(2*d))/den
            r=z*((p*(1-p)/d+z*z/(4*d*d))**.5)/den
            return dict(numerator=n,denominator=d,value=p,wilson95=[max(0,c-r),min(1,c+r)])
        return dict(confusion=out,precision=metric(out['tp'],out['tp']+out['fp']),
            recall=metric(out['tp'],out['tp']+out['fn']),
            keep_false_drop_rate=metric(out['fp'],out['fp']+out['tn']),
            survivor_defect_rate=metric(out['fn'],out['fn']+out['tn']))
    orientation_values={c['row_id']:c['orientation']['rotated'] for c in cases}
    eligible_truth={rid:t for rid,t in truth.items() if by_id[rid]['text_rules']['passed']}
    for c in cases:
        c['orientation_in_composition']=c['orientation']['rotated'] if c.get('text_rules',{}).get('passed') else 'not_reached'
    # Inventory loading never invokes preparation; stale/missing stays unknown.
    composed={}; crossing_pages={}; crossings={}
    for rid,row in sorted(cp4_by.items()):
        st=row.get('observation',dict(status=row['status'],reason=row.get('reason')))
        pid=rid.rsplit('-l',1)[0]
        entry=next((p for p in cp4['page_coverage'] if p.get('binding') and
                    Path(p['binding']['cache_directory']).name==pid),None)
        try:
            if entry is None:raise ValueError('geometry_unavailable')
            if pid not in crossing_pages:
                crossing_pages.clear()  # retain only one native page in memory
                b=entry['binding']
                page=g.load_cached_page(b['source'],b['cache_directory'],b['source_sha256'])
                inventory=separators.load(page,Path(os.environ.get('SEG_SEPARATOR_ROOT',str(SEG/'CP5_separators')))/pid)
                crossing_pages[pid]=(page,inventory)
            page,inventory=crossing_pages[pid]
            crossing=s.column_crossings(page,by_id[rid]['crop_bbox'],inventory['boundaries'])
            crossing['inventory_sha256']=g.sha(Path(os.environ.get('SEG_SEPARATOR_ROOT',str(SEG/'CP5_separators')))/pid/'inventory.json')
        except (OSError,ValueError,KeyError) as error:
            crossing=dict(status='unavailable',drop=None,reason=str(error))
        crossings[rid]=crossing
        composed[rid]=s.compose_cp5(by_id[rid]['orientation'],st,crossing)
    for c in cases:
        if c['row_id'] in composed:
            c['composed']=composed[c['row_id']]
            c['crossing']=crossings[c['row_id']]
    required={rid for rid,t in truth.items() if t in ('keep','drop','challenge')}|rotated
    unresolved=[rid for rid in sorted(required) if
        (composed[rid]['drop'] is None if rid in composed else by_id[rid]['orientation']['rotated'] is None)]
    upright=[c for c in controls if c['expected_rotated'] is False]
    for c in controls:
        flags=evaluate(dict(label=c['text'],source='gazette_modern',primary_class=c['primary_class']))['checks']
        rejections=non_segmentation_eligibility(flags)['rejections']
        c['text_rules']=dict(passed=not rejections,rejections=rejections)
        c['orientation_in_composition']=c['orientation']['rotated'] if not rejections else 'not_reached'
    for c in controls:
        c['composed']=s.compose_cp5(c['orientation'],dict(status='measured',union_drop=False),
                                   dict(status='measured',drop=False))
    upright_composed=[c for c in upright if c['text_rules']['passed']]
    acceptance=dict(
        adjudicated_rotated=dict(caught=sum(c['orientation']['rotated'] is True for c in positives),required=len(positives),unknown=sum(c['orientation']['rotated'] is None for c in positives),
            decision_sources=dict(Counter(c['orientation']['decision_source'] for c in positives))),
        false_drops=dict(keeps=sum(c['orientation']['rotated'] is True for c in keeps),keep_required=len(keeps),
            upright=sum(c['orientation']['rotated'] is True for c in upright),upright_required=len(upright),
            upright_in_composition=sum(c['orientation']['rotated'] is True for c in upright_composed),
            upright_composition_required=len(upright_composed)),
        horizontal_merges=dict(c1=cp4['c1'],gallery=cp4['gallery']),
        unresolved_required=dict(count=len(unresolved),ids=unresolved),
        keep_unknown_after_inheritance=[c['row_id'] for c in keeps if c['orientation']['rotated'] is None],
        union=dict(keep_admitted=sum(composed[c['row_id']]['drop'] is False and not composed[c['row_id']]['geometry_unavailable'] for c in keeps),keep_false_drops=sum(composed[c['row_id']]['drop'] is True for c in keeps),
            keep_verified=sum(composed[c['row_id']]['verified_keep'] for c in keeps),
            rotated_caught=sum(s.compose_cp5(c['orientation'],dict(status='unavailable',union_drop=None),
                dict(status='unavailable',drop=None))['measured_drop'] is True for c in positives),
            rotated_required=len(positives),
            upright_false_drops=sum(c['composed']['drop'] is True for c in upright),
            horizontal_misses=cp4['c1']['required']-cp4['c1']['met']+cp4['gallery']['required']-cp4['gallery']['met']))
    requirements=dict(
        adjudicated_rotated=bool(positives) and acceptance['adjudicated_rotated']['caught']==len(positives),
        no_false_drops=not acceptance['false_drops']['keeps'] and not acceptance['false_drops']['upright'],
        horizontal_merges=cp4['c1']['met']==cp4['c1']['required'] and cp4['gallery']['met']==cp4['gallery']['required'],
        unknowns_explicit=all(c['orientation']['status']=='orientation_unknown' for c in cases
            if c['orientation'].get('decision',{}).get('axis')=='unknown'))
    requirements.update(composed_requirements(truth, composed, crossings))
    protected=json.loads((SEG/'protected_before.json').read_text())
    for path,entry in protected.items():assert g.sha(ROOT/path)==entry['sha256']
    manifest=SEG.parent/'crops_manifest.jsonl'
    pngs=[json.loads(raw) for raw in manifest.read_text().splitlines()]
    for row in pngs:assert g.sha(SEG.parent/row['path'])==row['sha256']
    assert g.sha(fp)==before,'feature drift during run'
    unknowns=[c for c in cases if c['orientation'].get('decision',{}).get('axis')=='unknown']
    hooks=[]
    for source,cls in sorted({(c['dataset_source'],c['primary_class']) for c in unknowns}):
        rows=[c for c in unknowns if (c['dataset_source'],c['primary_class'])==(source,cls)]
        membership=[c['row_id'] for c in rows if c['old_rotated_crop']['membership']]
        tall=[c['row_id'] for c in rows if c['old_rotated_crop']['tall_text']]
        excluded=sorted(set(membership)|set(tall))
        hooks.append(dict(source=source,primary_class=cls,unknown_count=len(rows),
            unknown_ids=[c['row_id'] for c in rows],old_rotated_crop_excluded_count=len(excluded),
            old_rotated_crop_excluded_ids=excluded,membership_ids=membership,tall_text_ids=tall))
    assert sum(h['unknown_count'] for h in hooks)==len(unknowns)
    out=dict(schema='SEG-CP5c-v1',cp7_orientation_unknown_hooks=hooks,gate=False,ledger_sha256=g.sha(SEG/'calibration_ledger.json'),
        verifier_sha256=g.sha(__file__),features_sha256=before,historical_file=str(HIST),historical_sha256=g.sha(HIST),
        historical=coverage(hist),historical_not_vertical=[c['row_id'] for c in hist if c['orientation']['rotated'] is not True],
        keeps=coverage(keeps),adjudicated_rotated=coverage(positives),controls=controls,
        acceptance_values=acceptance,acceptance=dict(met=sum(requirements.values()),required=len(requirements),requirements=requirements,passed=all(requirements.values())),
        text_rule_composition=dict(native_eligible=sum(c.get('text_rules',{}).get('passed',False) for c in cases),
            native_required=len(cases),keeps_eligible=sum(c['text_rules']['passed'] for c in keeps),
            rotated_eligible=sum(c['text_rules']['passed'] for c in positives)),
        screens=dict(orientation=matrix(orientation_values),
                     orientation_in_composition=matrix(orientation_values,eligible_truth),
                     orientation_targeted=matrix(orientation_values,
                         {**{rid:t for rid,t in truth.items() if t=='keep'},
                          **{rid:'drop' for rid in rotated}}),
                     measured_union=matrix({r:None if v['drop'] is False and not v['verified_keep'] else v['measured_drop'] for r,v in composed.items()}),
                     composed_union=matrix({r:None if v['drop'] is False and not v['verified_keep'] else v['drop'] for r,v in composed.items()}),
                     union_in_composition=matrix({r:None if v['drop'] is False and not v['verified_keep'] else v['drop'] for r,v in composed.items()},eligible_truth),cp4=cp4['screens']),
        column_crossing_coverage=dict(prepared_pages=len(list((SEG/'CP5_separators').glob('*/receipt.json'))),
            cases=dict(Counter(c['status'] for c in crossings.values()))),
        runtime_forbidden_attempts=attempts,publish_actions=0,protected_artifacts=len(protected),
        crop_pngs_verified=len(pngs),cases=cases)
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
