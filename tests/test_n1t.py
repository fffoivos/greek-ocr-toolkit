"""N1-T line completeness, geometry, gates, edit policy and sep2 isolation."""
import importlib.util
import json
from pathlib import Path
from greekocr.ops.data_root import input_path as _data_input
from tests._paths import require_file
import os
import subprocess
import sys
import pytest
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/numerics'))
from greekocr.numerics.tokens import tokenize
from greekocr.numerics.locks import Locks,load_locks
from greekocr.numerics.line_complete import enumerate_line,select_lines
from greekocr.numerics.dash import geometric_type,measure_dash,digit_widths
from greekocr.numerics.combine_v2 import decide,decode_and_gate,MEANINGS,DASHES
from greekocr.numerics.owner_v2 import build as owner_build,GROUPS,named
from n1t_packs import build,typed_controls,rows,sha
from n1_pack_closure import scan
LOCK=Locks(frozenset(),frozenset({'reserved'}),frozenset())
SLOT=dict(slot_id='l:t0:s1',line_id='l',start=1,end=2,glyph='-',grammar_candidates=['range','thousands'],
    geometry={'geom_status':'ok'},dash={'geometric_type':'en dash'})

def vote(reader='r1',meaning='raised dot',gate='VALID',confidence='high'):
    return dict(reader=reader,meaning=meaning,context_status=gate,read_status='ok',confidence=confidence)


def test_complete_enumeration_small_tokens_empty_gaps_and_boundaries():
    row=dict(id='l',text='A -12. X 3, 45–678!');slots=enumerate_line(row,LOCK)
    tokens=tokenize(row['text'])
    assert len(slots)==sum(t.digit_count+1 for t in tokens)
    assert [s['number'] for s in slots]==list(range(1,len(slots)+1))
    assert len({s['slot_id'] for s in slots})==len(slots)
    assert all(row['text'][s['start']:s['end']]==s['glyph'] for s in slots)
    assert any(s['glyph']=='' and not s['boundary'] for s in slots)
    assert [s['boundary'] for s in slots].count('left')==len(tokens)
    assert [s['boundary'] for s in slots].count('right')==len(tokens)


def test_lock_and_label_refusal_before_enumerating():
    with pytest.raises(ValueError,match='reserved'):enumerate_line(dict(id='reserved',text='123'),LOCK)
    with pytest.raises(ValueError,match='mismatch'):enumerate_line(dict(id='l',text='123',label='124'),LOCK)


def test_selection_line_unit_union_and_document_refusal():
    cards=[dict(slot_id='a:t0:s1'),dict(slot_id='a:t0:s2')]
    valid=[dict(line_id='b',glyph='-',digit_count=4),dict(line_id='c',glyph='-',digit_count=3)]
    frame=[dict(document='src:doc',partition='step1')]
    byid={i:dict(source='src',item='doc') for i in 'abc'}
    assert select_lines(cards,valid,frame,byid,LOCK)[0]==['a','b']
    byid['b']['item']='outside'
    with pytest.raises(ValueError,match='outside'):select_lines(cards,valid,frame,byid,LOCK)


@pytest.mark.parametrize('ratio,meaning',[(0,'hyphen'),(.749999,'hyphen'),(.75,'en dash'),(1.44999,'en dash'),(1.45,'em dash'),(3,'em dash')])
def test_fixed_unfitted_thresholds(ratio,meaning):assert geometric_type(ratio)==meaning


def test_stroke_metrics_and_ambiguous_multistroke():
    c=dict(bbox=[1,5,11,7],width=10,height=2,centre_y_relative_band=.6,wholly_inside_gap=True)
    m=dict(digit_height=10,components=[c]);w=dict(status='ok',median_digit_width=8)
    d=measure_dash(m,w);stroke=d['strokes'][0]
    assert d['dash_len_ratio']==1.25 and d['geometric_type']=='en dash' and not d['fitted']
    assert stroke['height_relative_band']==.2 and stroke['centre_y_relative_band']==.6
    assert measure_dash(dict(m,components=[c,c]),w)['geometric_type'] is None
    assert measure_dash(dict(m,components=[dict(c,wholly_inside_gap=False)]),w)['strokes']==[]
    assert measure_dash(m,dict(status='no_symbols',median_digit_width=None))['geometric_type'] is None


@pytest.mark.parametrize('meaning',MEANINGS[:8])
def test_two_high_valid_votes_and_dash_crosscheck(meaning):
    slot=dict(SLOT,dash={'geometric_type':meaning})
    d=decide(slot,[vote(meaning=meaning),vote('r2',meaning)])
    assert d['truth_candidate']==meaning and d['status']=='truth_candidate'
    assert d['edit'] is None and d['apply_edit'] is False
    assert bool(d['edit_candidate'])==(meaning=='raised dot')
    if meaning in DASHES:assert d['tags']==[meaning]


@pytest.mark.parametrize('a,b,gate,confidence',[
 ('raised dot','raised dot','VOID','high'),('raised dot','raised dot','MISSING','high'),
 ('raised dot','raised dot','VALID','low'),('raised dot','baseline dot','VALID','high'),
 ('other','other','VALID','high'),('unreadable','unreadable','VALID','high')])
def test_uncertainty_and_void_cannot_supply_primary_truth(a,b,gate,confidence):
    d=decide(SLOT,[vote(meaning=a),vote('r2',b,gate,confidence)])
    assert d['truth_candidate'] is None and d['status']=='lead_review'
    assert d['edit_candidate'] is None


def test_duplicate_reader_dash_disagreement_and_geometry_failure():
    with pytest.raises(ValueError,match='duplicate'):decide(SLOT,[vote(),vote()])
    assert decide(SLOT,[vote(meaning='hyphen'),vote('r2','hyphen')])['reason'].startswith('dash_geometry')
    assert decide(dict(SLOT,geometry={'geom_status':'no_symbols'}),[vote(),vote('r2')])['truth_candidate'] is None


@pytest.mark.parametrize('glyph,grammar,allowed',[('-',['thousands'],True),('.',['thousands'],True),
 ('-',['range','thousands'],True),('-',['range'],False),('–',['thousands'],False),
 (' - ',['thousands'],False),(',',['thousands'],False)])
def test_edit_exact_direction_grammar_and_tags_only(glyph,grammar,allowed):
    d=decide(dict(SLOT,glyph=glyph,grammar_candidates=grammar),[vote(),vote('r2')])
    assert bool(d['edit_candidate'])==allowed


def key_fixture(meanings):
    ids=[f'k{i:010x}' for i in range(len(meanings))];options=dict(zip('ABCDEFGHIJ',MEANINGS))
    key=dict(readers={'r1':ids},items={i:dict(slot_id=i,option_map=options,control_truth=m) for i,m in zip(ids,meanings)})
    answers=[dict(item_id=i,answer=next(k for k,v in options.items() if v==m),confidence='high') for i,m in zip(ids,meanings)]
    return key,answers


def test_gate_dash_types_abstention_and_malformed_fail_closed():
    key,answers=key_fixture(['hyphen','en dash','em dash'])
    assert decode_and_gate(key,answers)[0]['status']=='VALID'
    answers[0]['answer']='J';assert decode_and_gate(key,answers)[0]['abstentions']==1
    answers[0]['answer']='A';answers[1]['answer']='A'
    assert decode_and_gate(key,answers)[0]['status']=='VOID'
    for bad in (answers[:-1],answers+[answers[0]],list(reversed(answers))):
        with pytest.raises(ValueError):decode_and_gate(key,bad)
    answers[0]['confidence']='maybe'
    with pytest.raises(ValueError):decode_and_gate(key,answers)


def fixture_records(tmp_path,count=3):
    img=tmp_path/'source.png';Image.new('RGB',(50,20),'white').save(img)
    base=dict(geometry={'geom_status':'ok'},line=str(img),zoom=str(img),line_sha256=sha(img),zoom_sha256=sha(img),google_glyph='-')
    bed=[dict(base,slot_id=f'b{i}',line_id=f'l{i}') for i in range(count)]
    controls=[dict(base,slot_id=f'c{i}',line_id=f'cl{i}',truth='raised dot' if i==0 else ['baseline dot','comma','nothing'][i%3]) for i in range(9)]
    return bed,controls


def test_pack_reverse_fresh_permutations_closure_dryrun_and_tamper(tmp_path):
    bed,controls=fixture_records(tmp_path);root=tmp_path/'packs/n1t';out=tmp_path/'data'
    result=build(bed,controls,root,out,LOCK)
    assert len(result['contexts'])==1 and all(r['ok'] for r in result['closure'])
    a,b=[rows(root/'ctx01'/r/'items.jsonl') for r in ('r1','r2')]
    assert set(r['item_id'] for r in a).isdisjoint(r['item_id'] for r in b)
    for x,y in zip(a,reversed(b)):
        assert x['line']==y['line'] and x['zoom']==y['zoom']
        assert all(x['options'][k]!=y['options'][k] for k in x['options'])
    env=dict(os.environ,PATH=str(Path(sys.executable).parent)+':/usr/bin:/bin:/usr/sbin:/sbin',N1_TEST_MODE='1',N1_TEST_PACKS=str(tmp_path/'packs'),N1_TEST_DATA=str(out),N1_TEST_READER='/does/not/exist',N1_TEST_PROBE='/does/not/exist')
    r=subprocess.run(['bash',str(ROOT/'scripts/secondary/reading/run_n1.sh'),'n1t','ctx01','r2','--dry-run'],env=env,capture_output=True,text=True)
    assert r.returncode==0,r.stdout+r.stderr
    assert not (out/'answers').exists()
    with pytest.raises(ValueError,match='overwrite'):build(bed,controls,root,out,LOCK)
    (root/'ctx01/r2/private.json').write_text('{}')
    assert not scan(root/'ctx01/r2',out,completed=True,meanings=MEANINGS)['ok']


def test_calibration_refuses_unassigned_dash_and_wrong_set():
    controls=[dict(slot_id='dash',truth='hyphen or dash'),dict(slot_id='dot',truth='raised dot')]
    with pytest.raises(ValueError,match='Lead dash types pending'):typed_controls(controls,[dict(slot_id='dash',truth=None)])
    with pytest.raises(ValueError,match='exactly'):typed_controls(controls,[])
    sealed=typed_controls(controls,[dict(slot_id='dash',truth='em dash')])
    assert sealed[0]['truth']=='em dash' and controls[0]['truth']=='hyphen or dash'


def test_calibration_82_fixture_pack_and_launcher_dry_run(tmp_path):
    bed,controls=fixture_records(tmp_path);base=controls[0]
    controls=[dict(base,slot_id=f'c{i}',line_id=f'cl{i}',truth=MEANINGS[i%8]) for i in range(82)]
    root=tmp_path/'packs/n1cal2';out=tmp_path/'data'
    r=build([],controls,root,out,LOCK,calibration=True)
    assert r['contexts'][0]['readers']=={'r1':82}
    env=dict(os.environ,PATH=str(Path(sys.executable).parent)+':/usr/bin:/bin:/usr/sbin:/sbin',N1_TEST_MODE='1',N1_TEST_PACKS=str(tmp_path/'packs'),N1_TEST_DATA=str(out),N1_TEST_READER='/does/not/exist',N1_TEST_PROBE='/does/not/exist')
    r=subprocess.run(['bash',str(ROOT/'scripts/secondary/reading/run_n1.sh'),'n1cal2','cal01','r1','--dry-run'],env=env,capture_output=True,text=True)
    assert r.returncode==0,r.stdout+r.stderr


def owner_fixture(tmp_path):
    line=dict(line_id='l',text='1-234 5-678',source_era='elstat',crop=str(tmp_path/'line.png'))
    Image.new('RGB',(180,30),'white').save(line['crop'])
    slots=enumerate_line(dict(id='l',text=line['text']),LOCK)
    ds=[]
    for s in slots:
        s['geometry']=dict(geom_status='ok',gap=[s['start']*10,s['end']*10],digit_top=5,baseline=25)
        s['zoom']=line['crop'];s['dash']={'geometric_type':'en dash'}
        meaning='raised dot' if s['glyph']=='-' else 'space' if s['glyph']==' ' else 'nothing'
        ds.append(decide(s,[vote(meaning=meaning),vote('r2',meaning)]))
    return line,slots,ds


def test_owner_complete_full_line_prefill_names_and_actual_renderer(tmp_path):
    line,slots,decisions=owner_fixture(tmp_path)
    cards,spec=owner_build([line],slots,decisions);c=cards[0]
    assert c['printed']=='1·234 5·678' and c['rows'][1]['text']==c['printed']
    assert c['doc_id']==c['line_id']=='l' and c['data']['printed-source']=='ours-proposal'
    assert len(c['slots'])==len(slots)
    assert sum(bool(s['evidence']) for s in c['slots'])==len(slots)  # every gap, per N1-T section 6
    assert len(c['zooms'])==sum(d['truth_candidate']!='nothing' for d in decisions) and all(z['alt'].startswith('gap ') for z in c['zooms'])
    assert 'hyphen (-) → raised dot (·)' in c['rows'][2]['text']
    assert [g['id'] for g in spec['groups']]==list(GROUPS)
    cleanup=Path.home()/'Projects/greek-ocr-toolkit-cleanup/greekocr/adjudicate'
    modspec=importlib.util.spec_from_file_location('n1t_test_renderer',cleanup/'owner_sheet.py',submodule_search_locations=[str(cleanup)])
    module=importlib.util.module_from_spec(modspec);sys.modules[modspec.name]=module;modspec.loader.exec_module(module)
    html=module.render(cards,spec)
    assert 'data-printed-source="ours-proposal"' in html and 'value="1·234 5·678"' in html
    assert 'data-line="l"' in html and 'gap 2' in html
    (tmp_path/'fixture.html').write_text(html)


def test_owner_unsure_keeps_google_dash_typed_no_label_edit(tmp_path):
    line,slots,ds=owner_fixture(tmp_path)
    dash=next(i for i,s in enumerate(slots) if s['glyph']=='-')
    ds[dash]=decide(slots[dash],[vote(meaning='en dash'),vote('r2','en dash')])
    c=owner_build([line],slots,ds)[0][0]
    assert c['printed'].startswith('1–234') and ds[dash]['edit_candidate'] is None
    ds[dash]=decide(slots[dash],[vote(meaning='hyphen'),vote('r2','en dash')])
    c=owner_build([line],slots,ds)[0][0];assert c['printed'].startswith('1-234')
    with pytest.raises(ValueError,match='complete'):owner_build([line],slots,ds[:-1])
    assert named('−')=='minus (−)'


def test_real_phase_a_scope_and_one_explicit_failure():
    require_file('artifacts/n1/n1t/slots.jsonl')
    base=ROOT/'artifacts/n1';records=rows(base/'n1t/slots.jsonl');lines=rows(base/'n1t/lines.jsonl')
    selection=json.loads((_data_input(base/'n1t/selection.json')).read_text());valid=json.loads((_data_input(base/'N1S_VALID_SLOTS.json')).read_text())
    expected=set(selection['owner_sheet_lines'])|{s['line_id'] for s in valid if s['glyph']=='-' and s['digit_count']>=4}
    assert {l['line_id'] for l in lines}==expected
    locks=load_locks(base);locks.assert_fit_rows(expected)
    byline={l['line_id']:l for l in lines}
    assert len(records)==sum(sum(len(t.slots) for t in tokenize(l['text'])) for l in lines)
    failures=[s for s in records if s['geometry']['geom_status']!='ok']
    assert len(failures)==1 and failures[0]['geometry']['reason']=='reversed digit boxes'
    assert 'zoom' not in failures[0] and 'dash' not in failures[0]
    for s in records: assert byline[s['line_id']]['text'][s['start']:s['end']]==s['glyph']


def test_real_bed_coverage_controls_reverse_and_source_image_hashes():
    require_file('artifacts/n1/n1t/slots.jsonl')
    from collections import Counter
    from n1_render import SCRATCH
    out=ROOT/'artifacts/n1/n1t';packroot=SCRATCH/'sol_packs/n1t'
    slots={s['slot_id']:s for s in rows(out/'slots.jsonl') if s['geometry']['geom_status']=='ok'}
    seen={r:[] for r in ('r1','r2')};opaque=set()
    for ctx in sorted(packroot.glob('ctx*')):
        keys=[json.loads((_data_input(out/'keys'/(ctx.name+suffix+'.json'))).read_text()) for suffix in ('','.r2')]
        for reader,key in zip(('r1','r2'),keys):
            public=rows(ctx/reader/'items.jsonl');assert len(public)<=100
            assert len(public)==len(key['readers'][reader])
            controls=[r for r in key['items'].values() if r['control_truth'] is not None]
            assert len(controls)==9 and any(r['control_truth']=='raised dot' for r in controls)
            assert all(r['control_truth'] not in DASHES for r in controls)
            assert not opaque.intersection(key['items']);opaque.update(key['items'])
            for p in public:
                k=key['items'][p['item_id']]
                if k['control_truth'] is None:
                    seen[reader].append(k['slot_id'])
                    for name in ('line','zoom'):assert sha(ctx/reader/p[name])==slots[k['slot_id']][name+'_sha256']
        a=[keys[0]['items'][i] for i in keys[0]['readers']['r1']]
        b=[keys[1]['items'][i] for i in reversed(keys[1]['readers']['r2'])]
        for x,y in zip(a,b):
            assert x['slot_id']==y['slot_id'] and x['control_truth']==y['control_truth']
            assert all(x['option_map'][k]!=y['option_map'][k] for k in x['option_map'])
    for reader in seen:assert Counter(seen[reader])==Counter({s:1 for s in slots})


@pytest.mark.skip(reason="historical binding; green at opus/secondary-corrections@c5f864222; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_real_dash_sheet_assignments_original_cells_and_custody():
    base=ROOT/'artifacts/n1';approved=rows(base/'controls/approved.jsonl');dash=[r for r in approved if r['truth']=='hyphen or dash']
    template=rows(base/'controls/dash_types_template.jsonl');index=json.loads((_data_input(base/'n1t/dash_controls_index.json')).read_text())
    assert len(template)==len(index['cells'])==len(dash)==27
    assert [(r['slot_id'],r['cell_number']) for r in template]==[(r['slot_id'],r['approval_cell_number']) for r in dash]
    assert min(r['cell_number'] for r in template)==49 and max(r['cell_number'] for r in template)==81
    assert all(r['truth'] is None for r in template) and not index['ratio_printed']
    assert sha(index['sheet'])==index['sha256']
    assert all(r['digit_width']['status']=='ok' for r in index['cells'])
    prior=json.loads(_data_input(Path(json.loads((_data_input(base/'n1t/build.json')).read_text())['prior_snapshot'])).read_text())
    # Phase 2 explicitly replaces owner products; all other custody remains sealed.
    for p,h in prior.items():
        if Path(p).parent==base/'owner_sheet':continue
        archive=Path(p).with_suffix('.pre_v44.json')
        assert sha(archive if p.endswith('.scan.json') and archive.exists() else p)==h


def test_post_read_builders_require_explicit_lead_go():
    from n1t_combine import load_reads
    reads,gates=load_reads()
    assert len(reads)==1059 and len(gates)==28
    result=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/numerics/n1t_owner_sheet.py')],capture_output=True,text=True)
    assert result.returncode!=0 and 'phase 2 requires lead go' in result.stderr


def test_exact_token_digit_median_and_missing_anchor_refusal():
    from test_n1_slots_geom import fixture
    row,doc=fixture('1234');token=tokenize(row['text'])[0]
    # Vary exact symbol widths: 2,4,6,8 => median 5, not flank-only width.
    for i,symbol in enumerate(doc['pages'][0]['symbols']):
        vertices=symbol['layout']['boundingPoly']['vertices'];vertices[1]['x']=vertices[0]['x']+2*(i+1)
    width=digit_widths(row,token,doc)
    assert width['widths']==[2,4,6,8] and width['median_digit_width']==5
    doc['pages'][0]['symbols'].pop(1)
    assert digit_widths(row,token,doc)['status']=='no_symbols'


def test_boundary_window_uses_known_crop_edge_not_estimated_width():
    from test_n1_slots_geom import fixture
    from greekocr.numerics.slots_geom import locate_slot
    row,doc=fixture('12')
    g=locate_slot(row,dict(start=2,end=2,glyph='',boundary='right'),doc,exact_boundary=True)
    assert g['gap']==[18,100]


def test_owner_agreement_sample_is_12_whole_lines_deterministic(tmp_path):
    from copy import deepcopy
    line,slots,ds=owner_fixture(tmp_path);lines=[];allslots=[];alld=[]
    for i in range(15):
        l=dict(line,line_id=f'l{i}');lines.append(l)
        for s,d in zip(slots,ds):
            s=deepcopy(s);s['line_id']=l['line_id'];s['slot_id']=l['line_id']+':'+s['slot_id'].split(':',1)[1]
            meaning='hyphen' if s['glyph']=='-' else 'space' if s['glyph']==' ' else 'nothing'
            s['dash']={'geometric_type':'hyphen'};allslots.append(s)
            alld.append(decide(s,[vote(meaning=meaning),vote('r2',meaning)]))
    cards,spec=owner_build(lines,allslots,alld)
    assert len(cards)==12 and all(c['group']==GROUPS[4] for c in cards)
    assert len(spec['omitted_agreement_line_ids'])==3
    assert spec==owner_build(lines,allslots,alld)[1]


@pytest.mark.parametrize('root',['n1t','n1t2','n1cal2'])
def test_modern_fake_launch_uses_sep2_and_isolates_outputs(tmp_path,root):
    from test_n1cd import fake_setup
    data,rd,ctx,env=fake_setup(tmp_path,root='n1')
    ctxnew='ctx01' if root in ('n1t','n1t2') else 'cal01'
    target=tmp_path/'packs'/root/ctxnew/'r1';target.parent.mkdir(parents=True)
    rd.rename(target)
    key=json.loads((_data_input(data/'keys/ctx01.json')).read_text());key['calibration']=root=='n1cal2'
    public=rows(target/'items.jsonl')
    for item in public:
        truth=key['items'][item['item_id']]['control_truth']
        options=dict(zip('ABCDEFGHIJ',[truth]+[m for m in MEANINGS if m!=truth]))
        item['options']=options;key['items'][item['item_id']]['option_map']=options
    (target/'items.jsonl').write_text('\n'.join(map(json.dumps,public))+'\n')
    (data/'keys'/(ctxnew+'.json')).write_text(json.dumps(key))
    (target.parent/'MANIFEST.r1.json').write_text(json.dumps(dict(files={str(p.relative_to(target)):sha(p) for p in target.rglob('*') if p.is_file()})))
    fake=Path(env['N1_TEST_READER']);body=_data_input(fake).read_text().replace("Path(prompt).name=='sep.md'","Path(prompt).name=='sep2.md'").replace("answer='A')","answer='A',confidence='high')")
    fake.write_text(body)
    env['PATH']=str(Path(sys.executable).parent)+':/usr/bin:/bin:/usr/sbin:/sbin'
    r=subprocess.run(['bash',str(ROOT/'scripts/secondary/reading/run_n1.sh'),root,ctxnew],env=env,capture_output=True,text=True)
    assert r.returncode==0,r.stdout+r.stderr
    stem=data/'answers'/root/f'{ctxnew}.r1'
    assert _data_input(Path(str(stem)+'.prompt.md')).read_bytes()==(_data_input(ROOT/'docs/records/labelfix/secondary/prompts/sep2.md')).read_bytes()
    mapped=json.loads(_data_input(Path(str(stem)+'.mapped.json')).read_text())
    assert mapped['context_status']=='VALID'
    if root=='n1cal2':assert json.loads(_data_input(Path(str(stem)+'.calibration.json')).read_text())['correct']==2
