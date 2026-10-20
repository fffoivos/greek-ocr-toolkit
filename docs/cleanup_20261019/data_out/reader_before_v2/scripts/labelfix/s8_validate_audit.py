"""Validate all 48 S8a2 audit lines against their blind cards and native pixels."""
import ast
from collections import Counter
import gzip
import json
import math
import random
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scripts.labelfix.s8_prepare import (OUT,E,ROOT,SEED,binding,dump,load,rows,sha,nfd,has_mark,MODES)


def main():
    blind=load(OUT/'audit/items_blind.json');key=load(OUT/'private/audit/items_key.json')
    plan=rows(E/'audit_plan.jsonl');census=rows(E/'audit_word_census.jsonl');selection=load(E/'audit_selection.json')
    data=[k for k in key if not k['control']];controls=[k for k in key if k['control']]
    assert len(blind)==len(key)==len(data)+len(controls)
    assert len({b['id'] for b in blind})==len(blind)
    assert all(set(b)=={'id','img','line_img','options','other_options'} for b in blind)
    assert all(b['other_options']==['none of these','unreadable'] for b in blind)
    assert not any(p.name=='items_key.json' for p in (OUT/'audit').rglob('*'))
    assert [b['id'] for b in blind]==[b['id'] for b in key]
    answers=load(OUT/'audit/answers_blank.json')
    assert len(answers)==len(blind) and all(all(v is None for k,v in r.items() if k!='id') for r in answers)
    assert len(data)==len(plan)==114 and len(controls)==math.ceil(len(data)*.08/.92)==10
    assert len(controls)/len(key)>=.08
    wanted={r['id'] for r in selection};assert len(wanted)==48
    assert Counter(r['AB_after'] for r in selection)=={'corrected':14,'unchanged':34}
    assert Counter(r['sample'] for r in selection)=={'200':42,'vouli':6}
    assert {k['line_id'] for k in data}==wanted
    assert not wanted&set((OUT/'S8_DEV_ids.txt').read_text().split())
    assert {k['uid'] for k in data}=={x['uid'] for x in plan}
    assert not {k['uid'] for k in controls}&{k['uid'] for k in data},'duplicate control/data word'
    for r in selection:
        if r['AB_after']!='unchanged':continue
        eligible=[x for x in census if x['line_id']==r['id']]
        assert all(any(has_mark(v) for v in x['forms'].values()) for x in eligible)
        disputed=[x for x in eligible if len(set(x['forms'].values()))>1]
        pool=[x for x in eligible if len(set(x['forms'].values()))==1]
        expected=random.Random(SEED+'audit20'+r['id']).sample(sorted(pool,key=lambda x:x['uid']),math.ceil(.2*len(pool)))
        got=[x for x in data if x['line_id']==r['id']]
        assert {x['uid'] for x in got}=={x['uid'] for x in disputed+expected}
        for x in pool:assert x['inclusion_probability']==len(expected)/len(pool)
    sources=load(E/'sources.json');remote=json.loads(gzip.decompress((E/'audit_remote_selected.json.gz').read_bytes()))
    lookup={b['id']:b for b in blind};bound=load(E/'frozen_binding.json')
    for k in key:
        assert k['options']==lookup[k['id']]['options']
        assert sha(sources[k['line_id']]['original_path'])==k['source_crop_sha256']
        assert nfd(remote['runtime'][k['line_id']]['recogniser_text'])==remote['alignments'][k['line_id']]['alignment']['prediction']
        with Image.open(OUT/'audit'/k['line_img']) as im,Image.open(sources[k['line_id']]['original_path']) as orig:
            assert im.size==orig.size and np.array_equal(np.asarray(im),np.asarray(orig.convert('RGB')))
        box=k['crop_box'];w,h=box[2]-box[0],box[3]-box[1]
        with Image.open(OUT/'audit'/k['img']) as im,Image.open(sources[k['line_id']]['original_path']) as orig:
            assert 0<k['zoom_scale']<=3 and im.width<=3*w and im.height<=3*h
            assert abs(im.width/w-im.height/h)<=1/w+1/h
            expected=orig.crop(box).convert('RGB').resize(im.size,Image.Resampling.LANCZOS)
            assert np.array_equal(np.asarray(im),np.asarray(expected))
        assert set(k['options'].values())=={v or '∅' for v in k['forms'].values()}
        if k['control']:assert k['options'][k['expected_choice']]==k['known_answer'] and k['pixel_verified']
    for name in ('s8_fetch_l1m.py','s8_prepare.py','s8_report.py','s8_validate_audit.py'):ast.parse((ROOT/'scripts/labelfix'/name).read_text())
    # The detector lazily imports extra frozen modules. Recheck every path in
    # the runtime receipt even when validation itself does not run the detector.
    assert binding(bound['sources'])==bound
    parity=load(E/'L1M_original_projection_parity.json');assert parity['all_equal'] and len(parity['lines'])==14
    # Review sheets contain the final rendered images; no expected answer on data cards.
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',15)
    sheets=[]
    for page in range(math.ceil(len(key)/32)):
        canvas=Image.new('RGB',(1800,1280),'#eee');draw=ImageDraw.Draw(canvas)
        for j,k in enumerate(key[page*32:page*32+32]):
            x=(j%4)*450;y=(j//4)*160
            draw.text((x+4,y+2),f'{page*32+j:03d} {k["id"]}',font=font,fill='black')
            with Image.open(OUT/'audit'/k['img']) as im:
                sc=min(1.,440/im.width,112/im.height)
                tile=im.resize((round(im.width*sc),round(im.height*sc)),Image.Resampling.LANCZOS)
                canvas.paste(tile,(x+4,y+25))
        name=f'audit_final_words_QA_{page:02d}.png';canvas.save(E/name);sheets.append(name)
    visual=load(E/'audit_visual_review.json') if (E/'audit_visual_review.json').exists() else None
    dump(E/'audit_validation.json',dict(status='PASS',audit_lines=48,audit_cards=len(data),controls=len(controls),control_fraction=len(controls)/len(key),
        by_wave=dict(Counter(k['wave'] for k in data)),by_selection=dict(Counter(k['selection'] for k in data)),
        exact_seeded_20_percent_selection=True,all_disputed_mark_words_covered=True,all_48_lines_covered=True,
        blind_sources_and_controls_hidden=True,key_outside_blind=True,full_line_native_pixels_match=True,
        word_rasters_match_source_windows=True,zoom_at_most_3x=True,blank_answers=True,
        alignment_reader_identity_lines=48,original_projection_parity_14=parity['all_equal'],
        visual_sheets=sheets,visual_review=visual,controls_review='audit_controls_verified.json',
        frozen_source_files=len(bound['sources']),reader_runs=0,
        DEV_baseline_status='COMPLETE' if (E/'baseline_by_wave.json').exists() else 'PENDING_missing_saved_DEV_evidence'))
    print(f'PASS: {len(data)} audit cards + {len(controls)} controls, all 48 lines; visual review recorded: {visual is not None}')


if __name__=='__main__':main()
