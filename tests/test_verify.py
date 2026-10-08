"""T7 offline contracts; every Codex boundary is mocked, never a live test call."""
from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
import subprocess
import unicodedata as ud

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import pytest

from greekocr.verify import (image_checks, readability_profile, render_overlay, text_checks,
                             vlm_annotate, llm_judge, CallBudget)
from greekocr.verify import judges
from greekocr.verify.calibration import calibrate, confusion, fit_distribution
from greekocr.verify.cli import crop_records, reading_records
from greekocr.cli import main

ROOT = Path(__file__).resolve().parents[1]
REGRESSION = ROOT/'tests/fixtures/o4d_lines/regressions/s2-60f24a3d8a2d714767f2-p00003-l00024_old.png'


def letters(*, slope=0., width=500, height=70):
    image=Image.new('L',(width,height),255)
    d=ImageDraw.Draw(image)
    for x in range(25,width-25,20):
        bottom=round(40+slope*x)
        d.rectangle((x,bottom-17,x+6,bottom),fill=15)
        d.rectangle((x+6,bottom-3,x+12,bottom),fill=15)
    return image


def test_profile_shapes_bins_finite_and_json():
    p=readability_profile(letters())
    for name in ('visible_fraction','clip_top','clip_bottom','baseline_offset','local_contrast','blur','obstruction','neighbour'):
        a=getattr(p,name)
        assert len(a)==p.width_px and np.isfinite(a).all()
        assert p.bins[name].shape==(64,)
    assert p.quality_map.shape==(16,64)
    assert (p.quality_map>=0).all() and (p.quality_map<=1).all()
    json.dumps(p.to_dict(),allow_nan=False)


def test_scalar_summaries_same_analysis():
    p=readability_profile(letters())
    assert p.summaries==image_checks(letters())
    assert p.summaries.trail=='flat'
    assert p.summaries.unreadable_fraction == np.mean(p.readability < p.threshold)


@pytest.mark.parametrize('slope,direction',[(.03,'down'),(-.03,'up')])
def test_baseline_sign_and_degrees(slope,direction):
    c=image_checks(letters(slope=slope))
    assert c.trail==direction
    assert abs(c.skew_deg-np.degrees(np.arctan(slope)))<.6
    assert c.trail_amplitude_px>7


def test_required_clipping_fixture_localizes_fragments_and_clear_middle():
    p=readability_profile(REGRESSION)
    w=p.width_px
    # Ignore the unprinted leading margin; the initial fragment train is weak.
    initial=slice(int(.09*w),int(.20*w))
    middle=slice(int(.45*w),int(.70*w))
    assert p.visible_fraction[initial].mean()<.56
    assert (p.readability[initial]<.55).mean()>.75
    assert p.clip_bottom[initial].mean()>.1
    assert p.visible_fraction[middle].mean()>.85
    assert (p.readability[middle]>=.55).mean()>.8
    assert any(s['x0']<.20*w and s['x1']>.15*w for s in p.segments)
    # This specific old raster also visibly clips ink later, at the upper border.
    assert p.clip_top[int(.8*w):int(.9*w)].mean()>.1


def test_local_cropped_letters_without_turning_spaces_into_defects():
    image=letters()
    a=np.array(image)
    a[:38,:110]=255
    # Cut the initial glyph bodies by replacing their upper support with paper.
    p=readability_profile(a)
    assert p.visible_fraction[35:95].mean()<p.visible_fraction[250:400].mean()-.3
    assert np.all(p.readability[:8]>.9)


def test_border_checks_four_sides():
    image=letters()
    d=ImageDraw.Draw(image)
    d.rectangle((0,0,5,5),fill=0);d.rectangle((494,64,499,69),fill=0)
    assert all(image_checks(image).edge_touch.values())


@pytest.mark.parametrize('size',[(1,1),(13,7),(500,70)])
def test_empty_rasters_are_finite_and_not_readable(size):
    p=readability_profile(Image.new('L',size,255))
    assert p.summaries.empty and p.summaries.ink_coverage==0
    assert not p.readability.any() and not p.quality_map.any()
    assert np.isfinite(p.visible_fraction).all()
    assert p.bins['blur'].shape==(64,)


def test_alpha_composited_onto_paper():
    assert image_checks(Image.new('RGBA',(30,20),(0,0,0,0))).empty


def test_normalized_raster_contract():
    im=letters()
    assert image_checks(im).skew_deg==image_checks(np.asarray(im)/255.).skew_deg
    for a in (np.empty((0,10)), np.array([[np.nan]]),np.array([[200.]])):
        with pytest.raises(ValueError):image_checks(a)


def test_blur_degradation_increases_local_blur():
    sharp=readability_profile(letters())
    blurred=readability_profile(letters().filter(ImageFilter.GaussianBlur(2)))
    assert blurred.summaries.clarity['laplacian_variance']<sharp.summaries.clarity['laplacian_variance']/4
    assert blurred.blur[50:400].mean()>sharp.blur[50:400].mean()


def test_foreign_rule_is_localized():
    clean=letters()
    dirty=clean.copy()
    ImageDraw.Draw(dirty).rectangle((90,12,330,15),fill=0)
    p=readability_profile(dirty)
    assert p.obstruction[100:320].mean()>.05
    assert p.obstruction[370:440].mean()<.02
    assert p.summaries.obstruction_score>image_checks(clean).obstruction_score


def test_bounded_grid_keeps_native_edge_and_coordinates():
    image=letters(width=3000,height=190)
    ImageDraw.Draw(image).rectangle((2444,0,2450,0),fill=0)
    p=readability_profile(image)
    assert p.summaries.analysis_scale<1
    assert p.width_px==3000 and p.clip_top[2444:2451].all()
    assert p.summaries.edge_touch['top']
    assert p.expected_band.shape==(2,3000)
    assert len(p.readability)==3000


def test_overlay_png_is_viewable_and_size_bound():
    im=letters();p=readability_profile(im)
    encoded=render_overlay(im,p)
    assert encoded.startswith(b'\x89PNG')
    with Image.open(io.BytesIO(encoded)) as result:
        assert result.size==im.size
    with pytest.raises(ValueError):render_overlay(Image.new('L',(10,10)),p)


@pytest.mark.parametrize('text',[
    'ἄνθρωπος καὶ εἰς τὴν χώραν', 'Τρικούπη, ἐμποδιζομένη ἀπὸ τὸν νόμον',
    'ἄνθρωπός μου', 'Ἰωάννης', 'ΟΙ ΑΝΘΡΩΠΟΙ', 'ἑῷος',
])
def test_valid_greek_nfc_nfd_equivalent(text):
    a=text_checks(ud.normalize('NFC',text));b=text_checks(ud.normalize('NFD',text))
    assert a==b and a.is_greek_script==1
    assert a.polytonic_consistency['impossible_mark_stacks']==0
    assert a.lexicon_validity is None


def test_monotonic_not_penalized_for_missing_breathing():
    c=text_checks('άνθρωπος και η πόλη')
    assert c.polytonic_consistency['missing_breathing_ratio'] is None
    assert c.garbage_score==0


@pytest.mark.parametrize('text',['α\u0313\u0314','α\u0301\u0300','κ\u0301','ε\u0342','ο\u0345','α\u0308','\u0301', 'α\u0304\u0306','α\u0342\u0306','ω\u0306'])
def test_impossible_marks_detected(text):
    c=text_checks(text)
    assert c.polytonic_consistency['impossible_mark_stacks']>0
    assert c.problems


def test_garbage_independent_evidence():
    clean=text_checks('ἡ χώρα')
    bad=text_checks('βγδκλμν ΟCR $%\ufffd')
    assert bad.consonant_run_ratio>0 and bad.mixed_script_word_ratio>0 and bad.symbol_density>0
    assert bad.garbage_score>clean.garbage_score+.3
    assert text_checks('').garbage_score==1
    assert text_checks('123 —').is_greek_script==0
    with pytest.raises(TypeError):text_checks(None)


def test_foreign_name_accents_and_symbol_runs():
    assert text_checks('ἡ χώρα καὶ René').polytonic_consistency['impossible_mark_stacks']==0
    assert text_checks('ἡ χώρα #####').symbol_density>.3


def fake_judge(calls):
    def run(prompt,schema,images,model,budget,kind,receipts_dir):
        calls.append((prompt,schema,images,kind))
        count=len(images) if kind=='image' else len(json.loads(prompt.split('Numbered readings:\n')[1]))
        j={'readable':'yes','defects':[],'other_text':'','transcription_attempt':None} if kind=='image' else {'good_greek':'yes','problems':[]}
        return {'results':[{'number':i+1,'judgement':j.copy()} for i in range(count)]}, {'model':model,'call_id':str(len(calls)),'cost':{'usd':None}}
    return run


def test_image_batches_cache_identity_and_no_layer(monkeypatch,tmp_path):
    calls=[];monkeypatch.setattr(judges,'_run_codex',fake_judge(calls))
    paths=[]
    for i in range(5):
        path=tmp_path/f'{i}.png';letters(width=500+i).save(path);paths.append(path)
    rows=vlm_annotate(paths,cache=tmp_path/'cache.jsonl')
    assert [len(c[2]) for c in calls]==[4,1]
    assert len(rows)==5 and all(r['receipt']['model']=='gpt-6-luna' for r in rows)
    assert all('layer' not in p.lower() for p,_,_,_ in calls)
    vlm_annotate(paths,cache=tmp_path/'cache.jsonl')
    assert len(calls)==2
    letters(width=520).save(paths[0])
    vlm_annotate(paths,cache=tmp_path/'cache.jsonl')
    assert len(calls)==3


def test_duplicate_rasters_one_judgement(monkeypatch,tmp_path):
    calls=[];monkeypatch.setattr(judges,'_run_codex',fake_judge(calls))
    a=tmp_path/'a.png';b=tmp_path/'b.png';letters().save(a);b.write_bytes(a.read_bytes())
    r=vlm_annotate([a,b])
    assert len(calls)==1 and len(calls[0][2])==1
    assert [row['crop'] for row in r]==[str(a),str(b)]


def test_text_judge_caches_and_batches_without_layer(monkeypatch,tmp_path):
    calls=[];monkeypatch.setattr(judges,'_run_codex',fake_judge(calls))
    texts=['ἡ χώρα','ὁ δήμος','νόμος','πόλις','κείμενον','ἡ χώρα']
    rows=judges.judge_texts(texts,cache=tmp_path/'cache.jsonl')
    assert len(rows)==6 and len(calls)==2
    assert llm_judge('ἡ χώρα',cache=tmp_path/'cache.jsonl')['good_greek']=='yes'
    assert len(calls)==2


def test_numbered_response_mismatch_not_cached(monkeypatch,tmp_path):
    monkeypatch.setattr(judges,'_run_codex',lambda *a:({'results':[]},{}))
    path=tmp_path/'a.png';letters().save(path)
    with pytest.raises(ValueError,match='count mismatch'):vlm_annotate([path],cache=tmp_path/'cache')
    assert not (tmp_path/'cache').exists()


@pytest.mark.parametrize('size',[0,5])
def test_batch_bounds_before_any_call(size):
    with pytest.raises(ValueError):vlm_annotate([],batch_size=size)
    with pytest.raises(ValueError):judges.judge_texts([],batch_size=size)


def test_budget_failure_reservation_survives(tmp_path):
    b=CallBudget(tmp_path/'calls.jsonl',limit=2)
    b.reserve('image');b.reserve('text')
    assert b.count==2
    with pytest.raises(RuntimeError,match='exhausted'):b.reserve('image')
    assert b.count==2


def test_text_budget_cannot_exceed_200(tmp_path):
    p=tmp_path/'calls.jsonl'
    p.write_text(''.join(json.dumps({'call_id':str(i),'kind':'text'})+'\n' for i in range(200)))
    with pytest.raises(RuntimeError,match='200-call'):CallBudget(p).reserve('text')
    assert CallBudget(p).reserve('image')


def test_cli_receipt_flags_model_rollout_and_unknown_currency(monkeypatch,tmp_path):
    calls=[]
    def run(command,**kwargs):
        calls.append((command,kwargs))
        if command==['codex','--version']:
            return subprocess.CompletedProcess(command,0,'codex-cli 0.159.2\n','')
        answer={'results':[{'number':1,'judgement':{'readable':'yes','defects':[],'other_text':'','transcription_attempt':None}}]}
        Path(command[command.index('--output-last-message')+1]).write_text(json.dumps(answer))
        return subprocess.CompletedProcess(command,0,json.dumps(answer),'model: gpt-6-luna\ntokens used\n123\n')
    monkeypatch.setattr(subprocess,'run',run)
    path=tmp_path/'a.png';letters().save(path)
    result=vlm_annotate([path],budget=CallBudget(tmp_path/'calls'),receipts_dir=tmp_path/'receipts')[0]
    command,kwargs=calls[1]
    for flag in ('--ephemeral','--output-schema','-i'):
        assert flag in command
    for setting in ('features.remote_plugin=false','features.apps=false','project_doc_max_bytes=0'):
        assert setting in command
    assert not kwargs.get('shell')
    assert result['receipt']['model_source']=='rollout header'
    assert result['receipt']['cost']['tokens_used']==123
    assert result['receipt']['cost']['usd'] is None


def test_failed_cli_keeps_receipt_and_no_fake_labels(monkeypatch,tmp_path):
    def run(command,**kwargs):
        return subprocess.CompletedProcess(command,0,'codex-cli 0.159.2\n','') if command==['codex','--version'] else subprocess.CompletedProcess(command,1,'','recorded initialization failure')
    monkeypatch.setattr(subprocess,'run',run)
    path=tmp_path/'a.png';letters().save(path)
    budget=CallBudget(tmp_path/'calls')
    with pytest.raises(RuntimeError,match='failed'):
        vlm_annotate([path],budget=budget,receipts_dir=tmp_path/'receipts',cache=tmp_path/'cache')
    receipt=json.loads(next((tmp_path/'receipts').glob('*.receipt.json')).read_text())
    assert receipt['status']=='failed' and receipt['model'] is None and budget.count==1
    assert not (tmp_path/'cache').exists()


def test_model_mismatch_rejected(monkeypatch,tmp_path):
    def run(command,**kwargs):
        return subprocess.CompletedProcess(command,0,'codex-cli 0.159.2\n','') if command==['codex','--version'] else subprocess.CompletedProcess(command,0,'','model: another-model\n')
    monkeypatch.setattr(subprocess,'run',run)
    path=tmp_path/'a.png';letters().save(path)
    with pytest.raises(RuntimeError,match='model mismatch'):
        vlm_annotate([path],budget=CallBudget(tmp_path/'calls'),receipts_dir=tmp_path/'receipts')


def test_confusion_undefined_and_exact_counts():
    c=confusion([True,False,True,False],[True,True,False,False])
    assert (c['tp'],c['fp'],c['fn'],c['tn'])==(1,1,1,1)
    assert c['precision']==c['recall']==.5
    assert confusion([],[])['precision'] is None
    with pytest.raises(ValueError):confusion([True],[])


def test_calibration_no_labels_never_fabricates_negatives(tmp_path):
    check={'crop':'x','crop_sha256':'abc','checks':image_checks(letters()).to_dict()}
    r=calibrate([check],[{'crop_sha256':'abc','judgement':None}],owner_notes={},output=tmp_path/'CALIBRATION.md')
    assert r['labelled_images']==0 and r['unlabelled_images']==1
    assert all(d['default_all']['n']==0 for d in r['defects'].values())
    assert r['owner_notes_available']==0
    assert 'No empirical calibration' in (tmp_path/'CALIBRATION.md').read_text()


def test_calibration_thresholds_confusion_other_and_owner(tmp_path):
    base=image_checks(letters()).to_dict()
    cheap=[];labels=[]
    for i in range(20):
        c=base | {'skew_deg':3. if i%2 else 0.}
        cheap.append({'crop':f'{i}.png','crop_sha256':str(i),'line_id':f's2-source{i}-p00001-l00001','checks':c})
        labels.append({'crop_sha256':str(i),'judgement':{'readable':'partly','defects':['skew','other'] if i%2 else [],'other_text':'damaged character identities' if i%2 else ''}})
    r=calibrate(cheap,labels,owner_notes={'1.png':{'defects':['skew']}},output=tmp_path/'C.md')
    assert r['defects']['skew']['default_all']['tp']==10
    assert r['defects']['skew']['default_all']['tn']==10
    assert r['defects']['skew']['held_out']['n']>0
    assert r['unsupported_defects']==['other']
    assert r['other_features_not_detected']==['damaged character identities']
    assert r['owner_notes_comparable']==1
    assert r['owner_confusion']['skew']['tp']==1


def test_distribution_is_diagnostic_no_text_and_deduplicated(tmp_path):
    c={'crop_sha256':'x','checks':image_checks(letters()).to_dict()}
    r=fit_distribution([c,c],tmp_path/'sample.json')
    assert r['n']==1 and min(r['scale'])>0
    assert 'text' not in r and 'readings' not in r


def test_manifest_excludes_unindexed_regressions_and_layer(tmp_path):
    assert len(crop_records(ROOT/'tests/fixtures/o4d_lines'))==44
    assert len(crop_records(ROOT/'tests/fixtures/o4d_sample400'))==400
    p=tmp_path/'readings.json'
    p.write_text(json.dumps({'lines':[{'cllg_text':'ἡ χώρα','layer_text':'diagnostic-only'}]}))
    assert reading_records(p)[0]['text']=='ἡ χώρα'
    p.write_text(json.dumps({'lines':[{'layer_text':'must not be read'}]}))
    with pytest.raises(ValueError,match='layer'):reading_records(p)


def test_cli_images_text_and_calibrate_offline(tmp_path,capsys,monkeypatch):
    monkeypatch.setattr(subprocess,'run',lambda *a,**k:pytest.fail('offline CLI called a subprocess'))
    directory=tmp_path/'images';directory.mkdir();letters().save(directory/'a.png')
    out=tmp_path/'checks.jsonl'
    assert main(['verify','images',str(directory),'--out',str(out),'--profiles','--overlays',str(tmp_path/'overlays')])==0
    assert json.loads(out.read_text())['profile']['width_px']==500
    text=tmp_path/'reading.txt';text.write_text('ἡ χώρα\n')
    assert main(['verify','text',str(text)])==0
    labels=tmp_path/'labels.jsonl';labels.write_text('')
    assert main(['verify','calibrate','--checks',str(out),'--labels',str(labels),'--out',str(tmp_path/'C.md')])==0
    assert 'lexicon_validity' in capsys.readouterr().out


def test_extra_spatial_metrics_anomaly_and_neighbour_tracks():
    image=letters()
    d=ImageDraw.Draw(image)
    for x in range(25,475,20):
        d.rectangle((x,2,x+7,11),fill=0)
    p=readability_profile(image)
    assert p.summaries.baseline_count>=2
    assert p.neighbour.mean()>.02
    for name in ('stroke_width_px','stroke_width_cv','laplacian_variance','skew_deg','bleed_through_proxy','residual_anomaly_score'):
        assert p.spatial_features[name].shape==(500,)
        assert p.bins[name].shape==(64,) and np.isfinite(p.bins[name]).all()


def test_online_cli_boundaries_are_mocked(monkeypatch,tmp_path,capsys):
    calls=[];monkeypatch.setattr(judges,'_run_codex',fake_judge(calls))
    directory=tmp_path/'images';directory.mkdir();letters().save(directory/'a.png')
    common=['--ledger',str(tmp_path/'ledger'),'--receipts-dir',str(tmp_path/'receipts')]
    assert main(['verify','vlm',str(directory),'--cache',str(tmp_path/'image_cache')]+common)==0
    assert json.loads(capsys.readouterr().out)['rows'][0]['judgement']['readable']=='yes'
    reading=tmp_path/'text.txt';reading.write_text('ἡ χώρα\n')
    assert main(['verify','text',str(reading),'--judge','--cache',str(tmp_path/'text_cache')]+common)==0
    assert json.loads(capsys.readouterr().out)['rows'][0]['judgement']['good_greek']=='yes'
    assert [c[3] for c in calls]==['image','text']


def test_verify_public_api_integrates_repository_inventory():
    import ast
    from scripts.generate_api_docs import api_entries,CALLS
    docs=(ROOT/'docs/API.md').read_text()
    entries=[e for e in api_entries() if e[0].startswith('greekocr.verify')]
    assert len(entries)>=10
    for module,name,node,owner in entries:
        qualified=module+'.'+(owner+'.' if owner else '')+name
        assert '### `'+qualified+'`' in docs and name in CALLS
        if isinstance(node,ast.FunctionDef):
            assert node.returns is not None
            assert all(a.annotation is not None for a in node.args.args+node.args.kwonlyargs if a.arg!='self')
