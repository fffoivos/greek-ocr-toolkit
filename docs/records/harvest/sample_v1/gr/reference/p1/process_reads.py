"""Native-frame DocAI admission, crop custody and read-only G1b measurement."""
from __future__ import annotations
import json,math,statistics,sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
from PIL import Image
from pilotlib import *
sys.path.insert(0,str(ROOT))
import greekocr
GEO=ROOT.parent/'greek-ocr-toolkit-sol-labelfix/greekocr'
greekocr.__path__.append(str(GEO))
from greekocr.harvest.page_reads import _response_geometry
from greekocr.harvest.round1_reads import symbol_confidences
from greekocr.labelfix.geometry.io import cache_page
from greekocr.labelfix.geometry.ownership import prepare_row,ownership
from greekocr.labelfix.geometry.magnitude import measure,measured_owner,page_ratios,decision
from prepare_detector import detector_identity
from classify import inspect

THRESHOLDS=GEO/'labelfix/geometry/thresholds.json'

def one(page):
    dest=BASE/'bulk/lines'/(page['id']+'.jsonl');summary=BASE/'receipts/analysis'/(page['id']+'.json')
    parsed=BASE/'google/parsed/docai'/(page['image_sha256']+'.json')
    if not parsed.exists():return page['id'],'no_read'
    if not (BASE/'cache/g1b'/page['id']/'receipt.json').exists():return page['id'],'detector_pending'
    source=json.loads(parsed.read_text())
    if source['status']!='ok':return page['id'],'read_failed'
    signature=sha(pathlib.Path(__file__))+sha(BASE/'classify.py')+sha(THRESHOLDS)
    if summary.exists() and json.loads(summary.read_text()).get('analysis_signature')==signature:return page['id'],'cached'
    try:
        raw_path=pathlib.Path(source['raw_json_path']);raw=json.loads(raw_path.read_text())
        cache=json.loads((raw_path.parent/'cache.json').read_text());assert cache['raw_sha256']==sha(raw_path)
        geometry=_response_geometry('docai',raw,(page['width'],page['height']))
        lines=[r for r in geometry['lines'] if r['source']=='lines'];custody=symbol_confidences(raw['document'])
        if len(lines)!=len(custody):raise ValueError('line_geometry_or_symbol_custody_loss')
        heights=[l['bbox'][3]-l['bbox'][1] for l in lines if sum(c.isalpha() for c in l['text'])>=3]
        median=statistics.median(heights) if heights else None
        data,ink,labels,receipt=cache_page(BASE/page['image'],BASE/'cache/g1b'/page['id'],page['image_sha256'],detector_identity())
        detector_rows=[];invalid=[]
        for r in data['rows']:
            try:detector_rows.append(prepare_row(r,ink,labels))
            except ValueError as e:invalid.append(dict(row_id=r['row_id'],reason=str(e)))
        measured=[]
        with Image.open(BASE/page['image']) as image:
            for i,(line,conf) in enumerate(zip(lines,custody)):
                bbox=line['bbox'];height=bbox[3]-bbox[1];tall=median is not None and height>1.7*median
                result=inspect(line['text'],conf['mean'],tall=tall)
                heading='heading' in result['line_tags'];pad=max(4,math.ceil(height*.12)) if heading else 2
                crop_box=[max(0,math.floor(bbox[0])-pad),max(0,math.floor(bbox[1])-pad),min(image.width,math.ceil(bbox[2])+pad),min(image.height,math.ceil(bbox[3])+pad)]
                ident=page['id']+f'-l{i+1:04d}'
                crop=BASE/'bulk'/('heading_crops' if heading else 'crops')/(ident+'.png');crop.parent.mkdir(parents=True,exist_ok=True);image.crop(crop_box).save(crop,compress_level=3)
                old=dict(id=ident,old_label=result['text'],bbox=bbox,crop_bbox=crop_box,**ownership(bbox,detector_rows))
                owner,failure=measured_owner(old,detector_rows);features=dict(**measure(old,owner,detector_rows),measurement_failure=failure)
                measured.append(dict(id=ident,page_id=page['id'],pilot=page['pilot'],item=page['item'],page=page['page'],docai_index=i,docai_raw_text=line['text'],docai_text_anchors=raw['document']['pages'][0]['lines'][i]['layout'].get('textAnchor'),symbol_indices=conf['symbol_indices'],symbol_count=conf['symbol_count'],bbox=bbox,crop_bbox=crop_box,crop_path=str(crop.relative_to(BASE)),crop_sha256=sha(crop),crop_policy='heading_bbox_pad_max4_12pct' if heading else 'mapped_native_bbox_pad2',tall_box=tall,median_counted_line_height=median,ownership=old,**features,**result))
        page_ratios(measured);thresholds=json.loads(THRESHOLDS.read_text())
        for r in measured:
            r.update(decision(r,thresholds));r['usable_candidate']=r['admitted'] and r['codec_v1_pass'] and r['geometry_positive'] is False
            r['primary_target']=('mixed_greek_latin' if r['mixed_line'] else 'headings_caps' if any(t in r['line_tags'] for t in ['heading','caps']) else 'numerics_tables' if 'numeric' in r['line_tags'] else 'leaders_indices' if 'leaders' in r['line_tags'] else 'dialogue_fiction' if 'dialogue_punctuation' in r['line_tags'] else r['script_class'])
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(''.join(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n' for r in measured))
        report=dict(page_id=page['id'],pilot=page['pilot'],item=page['item'],status='ok',image_sha256=page['image_sha256'],analysis_signature=signature,raw_sha256=sha(raw_path),lines=len(measured),admitted=sum(r['admitted'] for r in measured),codec_admitted=sum(r['admitted'] and r['codec_v1_pass'] for r in measured),usable_candidate=sum(r['usable_candidate'] for r in measured),script_classes=dict(Counter(r['script_class'] for r in measured)),tags=dict(Counter(t for r in measured for t in r['line_tags'])),geometry_positive=sum(r['geometry_positive'] is True for r in measured),geometry_negative=sum(r['geometry_positive'] is False for r in measured),geometry_unresolved=sum(r['geometry_positive'] is None for r in measured),mixed_lines=sum(r['mixed_line'] for r in measured),coordinate_frame=geometry['coordinate_frame'],invalid_detector_rows=invalid,detector_rows=len(detector_rows),thresholds=thresholds,thresholds_sha256=sha(THRESHOLDS),lines_path=str(dest.relative_to(BASE)),lines_sha256=sha(dest),label_status='Google silver candidates; G1b is a calibrated diagnostic, not pixel ground truth or automatic release')
        write(summary,report);return page['id'],len(measured)
    except Exception as e:
        write(summary,dict(page_id=page['id'],pilot=page['pilot'],status='error',error_class=type(e).__name__,error=str(e)[:600]));return page['id'],type(e).__name__

if __name__=='__main__':
    pages=[json.loads(p.read_text()) for p in sorted((BASE/'receipts/pages').glob('*.json'))];pages=[p for p in pages if not p.get('excluded')]
    with ProcessPoolExecutor(max_workers=2) as pool:
        for f in as_completed([pool.submit(one,p) for p in pages]):print(*f.result(),flush=True)
