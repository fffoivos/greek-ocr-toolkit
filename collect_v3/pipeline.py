"""P1 + codec v1 + G1b, frozen T4b assembly and flag-only screen."""
from __future__ import annotations
from collections import Counter
import io,json,math,statistics,unicodedata as ud
from pathlib import Path
import numpy as np
from PIL import Image
from greekocr.harvest.page_reads import _response_geometry
from greekocr.harvest.round1_reads import symbol_confidences
from .common import read_json,sha,sha_bytes,atomic_bytes
from .config import POLY,marks
from .vendor.classify import inspect
from .vendor.admission import page_quality
from .vendor.assembly_fix import assemble_line,page_tokens,spans
from .vendor.features import pixel_features,token_features,reject
from .vendor.geometry.io import cache_page,detector_identity
from .vendor.geometry.ownership import prepare_row,ownership
from .vendor.geometry.magnitude import measured_owner,measure,page_ratios,decision
from .vendor.conventions import apply_conventions

MODEL=read_json(Path(__file__).parent/'vendor/screen_model.json')
THRESHOLDS=read_json(Path(__file__).parent/'vendor/geometry/thresholds.json')

def period(year):
    return 'poly1850' if year and 1850<=year<=1890 else 'poly1891_1899_aux' if year and 1891<=year<=1899 else 'poly1900' if year and 1900<=year<=1982 else 'modern' if year and year>=1983 else 'pre1850' if year and year<1850 else 'unknown'

def primary(r,page,physical_gazette=True):
    greek=r['inventory']['greek_letters'];tags=r['line_tags'];track=page.get('track')
    if r['mixed_line']:return 'mixed_greek_latin'
    if 'leaders' in tags:return 'leaders_indices'
    if greek>=3 and any(t in tags for t in ('caps','heading')):return 'headings_caps'
    if 'numeric' in tags:return 'numerics_tables'
    if greek>=3 and 'dialogue_punctuation' in tags:return 'dialogue_fiction'
    s=page['source'];y=page.get('year');p=page.get('period') or period(y)
    if s=='gazette_modern' and physical_gazette:
        # Date is a sampling stratum; the line's script decides monotonicity.
        if r['script_class']=='greek_poly':return 'poly1900'
        if r['script_class']=='greek_mono':return 'modern_scanned'
    if s in ('ia_poly1850','poly1850') and r['script_class']=='greek_poly':return 'poly1850'
    if s=='poly1900' and r['script_class']=='greek_poly':return 'poly1900'
    if s in ('bsb','bsb_poly1850') and r['script_class']=='greek_poly':return 'poly1850' if page.get('census_group','bsb_poly1850')=='bsb_poly1850' else 'poly1900' if page.get('census_group')=='bsb_poly1900' else 'greek_poly'
    if (track=='gr' or s in ('nlg','kosmopolis','lekythos','gazette_poly1900','gazette_modern','elstat')):
        if r['script_class']=='greek_poly' and p in ('poly1850','poly1900') and page.get('target_regime')!='ancient_or_bilingual_edition_auxiliary':return p
        if r['script_class'] in ('greek_mono','greek_poly') and ((s in ('openarchives','elstat') and y and y>=1900) or p=='modern') and page.get('target_regime')!='ancient_or_bilingual_edition_auxiliary':return 'modern_scanned'
    return r['script_class']

def detector(page,cache,fixture_cache=None):
    if fixture_cache:
        import gzip
        p=Path(fixture_cache);rec=read_json(p/'receipt.json')
        if rec['source_sha256']!=page['image_sha256']:raise ValueError('fixture detector source mismatch')
        for name,key in [('detector.json.gz','geometry_sha256'),('ink.png','mask_sha256'),('labels.npz','labels_sha256')]:
            if sha(p/name)!=rec[key]:raise ValueError('fixture detector cache corrupt')
        data=json.loads(gzip.decompress((p/'detector.json.gz').read_bytes()))
        with Image.open(p/'ink.png') as im:ink=np.asarray(im).astype(bool)
        with np.load(p/'labels.npz') as a:labels=a['labels']
    else:data,ink,labels,rec=cache_page(Path(page['image']),Path(cache)/'g1b'/page['id'],page['image_sha256'],detector_identity())
    prepared=[]
    for r in data['rows']:
        try:prepared.append(prepare_row(r,ink,labels))
        except ValueError:pass
    return prepared,rec

def analyse(page,raw,cache,crop_root,serbian=False,fixture_cache=None,baseline_overrides=None,convention_context=None):
    if sha(page['image'])!=page['image_sha256']:raise ValueError('page image hash mismatch')
    geometry=_response_geometry('docai',raw,(page['width'],page['height']))
    lines=[r for r in geometry['lines'] if r['source']=='lines'];custody=symbol_confidences(raw['document'])
    if len(lines)!=len(custody):raise ValueError('line/symbol custody mismatch')
    dr,rec=detector(page,cache,fixture_cache);tokens,inv,returned=page_tokens(raw['document'],(page['width'],page['height']))
    heights=[l['bbox'][3]-l['bbox'][1] for l in lines if sum(c.isalpha() for c in l['text'])>=3];median=statistics.median(heights) if heights else statistics.median([l['bbox'][3]-l['bbox'][1] for l in lines] or [1])
    result=[]
    with Image.open(page['image']) as original:
        image=original.convert('L')
        for i,(line,conf) in enumerate(zip(lines,custody)):
            bbox=line['bbox'];height=bbox[3]-bbox[1];tall=height>1.7*median
            text=inspect(line['text'],conf['mean'],tall=tall,serbian=False)
            heading='heading' in text['line_tags'];pad=max(4,math.ceil(height*.12)) if heading else 2
            cb=[max(0,math.floor(bbox[0])-pad),max(0,math.floor(bbox[1])-pad),min(image.width,math.ceil(bbox[2])+pad),min(image.height,math.ceil(bbox[3])+pad)]
            ident=page['id']+f'-l{i+1:04d}';crop=image.crop(cb);encoded=io.BytesIO();crop.save(encoded,format='PNG',compress_level=3)
            crop_path=Path(crop_root)/(ident+'.png');atomic_bytes(crop_path,encoded.getvalue())
            old=dict(id=ident,old_label=text['text'],bbox=bbox,crop_bbox=cb,**ownership(bbox,dr))
            owner,failure=measured_owner(old,dr);measured=dict(**measure(old,owner,dr),measurement_failure=failure)
            assembly=assemble_line(raw['document'],i,tokens)
            th=[t['bbox'][3]-t['bbox'][1] for t in assembly['kept_tokens'] if t['bbox'] and any(c.isalpha() for c in t['text'])];fallback=statistics.median(th)*.5 if th else median*.5
            pix=pixel_features(crop,fallback);xh=pix['xheight'];tok=token_features(assembly['kept_tokens'],xh)
            ownsp=spans(raw['document']['pages'][0]['lines'][i]);paras=[j for j,q in enumerate(raw['document']['pages'][0].get('paragraphs',[])) if any(max(a,c)<min(z,d) for a,z in ownsp for c,d in spans(q))]
            fixed=assembly['fixed_label'];density=sum(not c.isspace() and not ud.category(c).startswith('M') for c in ud.normalize('NFD',fixed))*xh/max(1,pix['ink_width'])
            r=dict(id=ident,page_id=page['id'],source=page['source'],track=page.get('track','collect_v3'),item=page['item'],page=page['page'],year=page.get('year'),bbox=bbox,crop_bbox=cb,crop_sha256=sha_bytes(encoded.getvalue()),crop=str(crop_path),docai_line_index=i,tall_box=tall,page_median_row_height=median,height_ratio=(cb[3]-cb[1])/median,old_label=assembly['old_label'],fixed_label=fixed,assembly_changed=assembly['changed'],dropped_token_ids=[d['dropped_token_id'] for d in assembly['drops']],label_density=density,google_line_contributors=1,google_paragraph_contributors=len(paras),google_paragraph_ids=paras,**text,**measured,**pix,**tok)
            r['token_drop_trace']=assembly['drops'];r['rollback_label']=assembly['old_label']
            r['exclusion_manifest_sha256']=page.get('exclusion_manifest_sha256')
            result.append(r)
    page_ratios(result)
    quality=page_quality([dict(page_id=page['id'],docai_text=r['text'],confidence=r['confidence'] or 0,flags=['tall_box'] if r['tall_box'] and 'heading' not in r['line_tags'] else []) for r in result]).get(page['id'],dict(bad_page=False))
    density_median=statistics.median([r['label_density'] for r in result if r['label_density']>0] or [1])
    for r in result:
        r.update(decision(r,THRESHOLDS));r['admitted']=r['admitted'] and not quality['bad_page']
        r['original_usable']=bool(r['admitted'] and r['codec_v1_pass'] and r['geometry_positive'] is False)
        r['primary_class']=primary(r,page);r['tags']=list(r['line_tags']);r['density_ratio']=r['label_density']/max(1e-9,density_median)
        # Replay explicit human withholds and prior duplicate/page overrides only;
        # labels, geometry, admission, crop hashes and features are recomputed.
        if baseline_overrides and r['id'] in baseline_overrides:
            saved=baseline_overrides[r['id']]
            r['native_withheld']=saved.get('native_withheld',False);r['duplicate_crop_label']=saved.get('duplicate_crop_label',False)
            if saved.get('native_withheld') or saved.get('duplicate_crop_label'):r['original_usable']=False
            if page.get('visual_excluded'):r['admitted']=False;r['original_usable']=False
        base=''.join(c for c in ud.normalize('NFD',r['fixed_label']) if not ud.category(c).startswith('M'));letters=sum(c.isalpha() for c in base);nonspace=sum(not c.isspace() for c in base);exempt=bool(set(r['tags'])&{'caps','numeric','leaders'})
        r['fixed_text_gate_pass']=not r['assembly_changed'] or (bool(r['fixed_label']) and (exempt or (letters>=10 and 3*(nonspace-letters)<=nonspace)))
        r['fixed_usable']=r['original_usable'] and r['fixed_text_gate_pass'];r['screen_merged']=reject(r,MODEL)
        r['screen_reject']=r['screen_merged'];r['screen_reasons']=[b for b in MODEL['branches'] if all(r[k]>v for k,v in b.items())]
    apply_conventions(result,convention_context)
    for r in result:
        from copy import deepcopy
        r['t4b_compatibility']=deepcopy({k:r.get(k) for k in ('admitted','codec_v1_pass','original_usable','fixed_usable','primary_class','label_after_conventions','roman_fixes','roman_ambiguous','long_s_label_count','text_exclusions','hyphen_test','next_column_line_id','join_evidence','tags')})
        r['t4b_compatibility']['primary_class']=primary(r,page,physical_gazette=False)
        r['t4b_label_after_conventions']=r['label_after_conventions'];r['emdash_label_count']=r['fixed_label'].count('—');r['emdash_to_hyphen_count']=r['label_after_conventions'].count('—')
        r['label_after_conventions']=r['label_after_conventions'].replace('—','-')
        r['tags'].extend(r['text_exclusions'])
        if r['roman_fixes']:r['tags'].append('roman_lookalike_normalized')
        if r['long_s_label_count']:r['tags'].append('long_s_glyph_variant_accepted')
        if page['source'] in POLY:r['tags'].append('marks_correction_required')
        r['tags']=sorted(set(r['tags']));r['source_marks']=marks(page['source']) if page['source'] in __import__('collect_v3.config',fromlist=['SPECS']).SPECS else None
        r['usable_final']=r['fixed_usable'] and not r['text_exclusions']
        r['label']=r['label_after_conventions'];r['codec_serbian_enabled']=serbian
        r['t4b_compatibility']['tags']=list(r['tags'])
    from .rules import apply_rules
    apply_rules(result,convention_context,serbian=serbian)
    return result
