"""R2C saved-data contracts and synthetic independent-reader integration."""
from copy import deepcopy
import json
from pathlib import Path

import pytest
from PIL import Image

from scripts.labelfix import r2_cards_prepare as prep
from scripts.labelfix import r2_cards_resolve as res


def heads(**changes):
    return dict(dict.fromkeys(res.HEADS,'none'),**changes)


def answer(card,form='η',**kw):
    row=dict(card_id=card['card_id'],choice='literal',transcription=form,
             anchor_heads=heads(),letter_heads=[],readability='readable',ownership_ok=True,
             confidence='high',note='',usage={'input_tokens':10,'output_tokens':5})
    row.update(kw)
    return row


@pytest.fixture(autouse=True)
def temporary_output_root(tmp_path, monkeypatch):
    # The production confinement stays enabled; this test owns a separate root.
    monkeypatch.setenv('GREEK_OCR_R2C_TEST_OUTPUT_ROOT', str(tmp_path))


@pytest.fixture
def synthetic(tmp_path):
    deck=tmp_path/'T2';(deck/'blind').mkdir(parents=True);(deck/'private').mkdir()
    image=Image.new('RGB',(40,20),'white');image.save(deck/'blind/pixels.png')
    for name in ('README.md','answer_schema.json'):
        (deck/'blind'/name).write_text('{}')
    cards=[];keys=[];controls=[]
    for ident in ['data1','data2','control1','control2','control3']:
        card=dict(card_id=ident,options={'A':'η','B':'ῃ'},anchor_index=0,
                  word_image='pixels.png',line_image='pixels.png')
        cards.append(card)
        keys.append(dict(card_id=ident,public=card,control=ident.startswith('control'),
                         crop_sha256='samecrop',crop_letter_offset=0 if ident=='data1' else 4,
                         word_index=0 if ident=='data1' else 1,slice='subscript',
                         anchor_index=0,target_head='subscript'))
        if ident.startswith('control'):
            controls.append(dict(card_id=ident,lead_verified=True,expected_form='η',
                                 expected_letter_heads=[dict(index=0,**heads())],
                                 expected_readability='readable',expected_ownership_ok=True))
    res.write(deck/'blind/cards.jsonl',cards);res.write(deck/'private/key.jsonl',keys)
    res.dump(deck/'private/controls_proposed.json',dict(controls=controls))
    r1=[answer(c) for c in cards];r2=[answer(c) for c in reversed(cards)]
    p1=tmp_path/'r1.jsonl';p2=tmp_path/'r2.jsonl'
    res.write(p1,r1);res.write(p2,r2)
    return deck,cards,p1,p2,tmp_path/'resolved'


def test_reservation_disjoint_deterministic_stratified():
    source={f'doc{i}':dict(source='a' if i<50 else 'b',era='1890s',line_count=3) for i in range(100)}
    a=prep.allocate(deepcopy(source));b=prep.allocate(dict(reversed(list(deepcopy(source).items()))))
    assert a==b
    from collections import Counter
    assert Counter(r['role'] for r in a.values())==dict(validation=10,witness=20,calibration=14,supervision=56)
    assert {r['role'] for r in a.values()}=={'validation','witness','calibration','supervision'}


@pytest.mark.parametrize('head,expected',[('breathing',3),('accent',4),('diaeresis',2),('subscript',2)])
def test_options_only_target_head_from_bases(head,expected):
    opts=prep.options('ἀῄ',1,head,'fixed')
    assert len(opts)==expected
    assert {prep.skeleton(v) for v in opts.values()}=={'αη'}
    assert opts==prep.options('αη',1,head,'fixed')
    for form in opts.values():
        cc=prep.clusters(form)
        assert cc[0]=='α'
        assert all(v=='none' for k,v in prep.tuple_heads(cc[1]).items() if k!=head)


def test_two_reader_agreement_complete_slots_and_usage(synthetic):
    deck,cards,p1,p2,out=synthetic
    truth,gates,inv=res.run(deck,p1,p2,out)
    assert all(t['status']=='resolved' for t in truth)
    assert len(truth)==2 and all(g['accepted'] for g in gates.values())
    assert inv['T2:subscript']['complete']==2  # crop-relative indices 0 and 4
    assert inv['T2:subscript']['absent']==2
    assert len(res.read(out/'truth.jsonl'))==2
    assert json.loads((out/'opus_usage.json').read_text())[0]['input_tokens']==50


def test_control_gate_more_than_one_discards_whole_batch(synthetic):
    deck,cards,p1,p2,out=synthetic
    rows=res.read(p1)
    for r in rows:
        if r['card_id'] in ('control1','control2'):
            r['transcription']='ῃ';r['anchor_heads']=heads(subscript='present')
    res.write(p1,rows)
    truth,gates,inv=res.run(deck,p1,p2,out)
    assert not gates['reader1']['accepted'] and gates['reader1']['control_errors']==2
    assert all(t['status']=='unresolved' for t in truth)
    assert inv['T2:subscript']['complete']==0  # single surviving vote cannot decide truth
    assert inv['T2:subscript']['unknown']==2


def test_one_control_error_is_allowed(synthetic):
    deck,cards,p1,p2,out=synthetic
    rows=res.read(p1);rows[-1]['transcription']='α';res.write(p1,rows)
    truth,gates,_=res.run(deck,p1,p2,out)
    assert gates['reader1']['accepted'] and gates['reader1']['control_errors']==1
    assert all(t['status']=='resolved' for t in truth)


def test_controls_must_be_pixel_verified(synthetic):
    deck,cards,p1,p2,out=synthetic
    cp=json.loads((deck/'private/controls_proposed.json').read_text());cp['controls'][0]['lead_verified']=False
    res.dump(deck/'private/controls_proposed.json',cp)
    with pytest.raises(ValueError,match='pixel-verify'):
        res.run(deck,p1,p2,out)


def test_reverse_order_enforced(synthetic):
    deck,cards,p1,p2,out=synthetic
    res.write(p2,list(reversed(res.read(p2))))
    with pytest.raises(ValueError,match='reverse order'):
        res.run(deck,p1,p2,out)


def test_tiebreak_rekeys_options_and_two_of_three(synthetic):
    deck,cards,p1,p2,out=synthetic
    rows=res.read(p2)
    for r in rows:
        if r['card_id']=='data1':
            r['transcription']='ῃ';r['anchor_heads']=heads(subscript='present')
    res.write(p2,rows)
    truth,_,_=res.run(deck,p1,p2,out)
    assert truth[0]['printed_form'] is None
    tb=res.read(out/'tiebreak/blind/cards.jsonl')
    assert len(tb)==4
    assert all(c['options']!={'A':'η','B':'ῃ'} for c in tb)
    third=[]
    for c in tb:
        a=answer(c)
        a.update(choice=next(k for k,v in c['options'].items() if v=='η'))
        third.append(a)
    p3=out.parent/'r3.jsonl';res.write(p3,third)
    truth,gates,inv=res.run(deck,p1,p2,out,p3)
    assert truth[0]['printed_form']=='η' and truth[0]['status']=='resolved'
    assert gates['reader3']['accepted'] and inv['T2:subscript']['complete']==2


def test_unknown_heads_not_fabricated_from_literal():
    card=dict(card_id='x',options={},anchor_index=0)
    a=res.normalise(answer(card,'η',anchor_heads=heads(subscript='unknown')),card)
    key=dict(card_id='x',slice='subscript',crop_sha256='crop',word_index=0,anchor_index=0,target_head='subscript')
    t=res.resolve_card(key,[a,a])
    assert t['printed_form']=='η' and t['letter_heads'][0]['subscript']=='unknown'
    assert t['status']=='unresolved'


def test_ownership_failure_masks_heads():
    card=dict(card_id='x',options={},anchor_index=0)
    a=res.normalise(answer(card,'ῃ',anchor_heads=heads(subscript='present'),ownership_ok=False),card)
    key=dict(card_id='x',slice='specks',crop_sha256='crop',word_index=0,anchor_index=0,target_head='breathing')
    t=res.resolve_card(key,[a,a])
    assert all(t['letter_heads'][0][h]=='unknown' for h in res.HEADS)


@pytest.mark.parametrize('changes',[{'anchor_heads':{'accent':'acute'}}, {'choice':'Z'},
                                    {'letter_heads':[dict(index=0,**heads())]},
                                    {'usage':{'input_tokens':-1}}, {'choice':'unreadable'}])
def test_malformed_answers_rejected(changes):
    card=dict(card_id='x',options={'A':'η'},anchor_index=0)
    with pytest.raises((ValueError,KeyError)):
        res.normalise(answer(card,**changes),card)


def test_four_head_compounds_and_crasis():
    assert prep.tuple_heads('η\u0314\u0342\u0345')==heads(breathing='dasia',accent='circumflex',subscript='present')
    word=dict(mining_key='κἀγώ',script_class='greek_poly',neighbour_body_ink_xh=0,
              accent_ink_cut_fraction=0,token_box=[20,2,80,20],native_size=[100,24])
    assert any(s.get('subtype')=='crasis' for s in prep.slice_candidates(word))


def test_initial_consonant_is_a_capital_candidate():
    word=dict(mining_key='Ν.',script_class='greek_poly',neighbour_body_ink_xh=0,
              accent_ink_cut_fraction=0,token_box=[20,2,40,20],native_size=[100,24])
    assert prep.slice_candidates(word)==[dict(slice='capitals',anchor_index=0,target_head='breathing',mining_marked=False)]


def test_provider_geometry_and_exact_crop_restoration(tmp_path,monkeypatch):
    import io
    from PIL import ImageDraw
    source=Image.new('L',(200,60),255)
    ImageDraw.Draw(source).rectangle((45,20,60,34),fill=0)
    sourcepath=tmp_path/'page.png';source.save(sourcepath)
    bbox=[20,10,180,50];im=source.crop(bbox);stream=io.BytesIO();im.save(stream,format='PNG',compress_level=3)
    crop_hash=prep.hashlib.sha256(stream.getvalue()).hexdigest()
    raw=dict(document=dict(text='αη\n',pages=[dict(dimension=dict(width=200,height=60),
          lines=[dict(layout=dict(textAnchor=dict(textSegments=[dict(endIndex=3)])))],
          tokens=[dict(layout=dict(textAnchor=dict(textSegments=[dict(endIndex=2)]),
                      boundingPoly=dict(vertices=[dict(x=43,y=18),dict(x=63,y=18),dict(x=63,y=36),dict(x=43,y=36)])))])]))
    rawpath=tmp_path/'raw.json';res.dump(rawpath,raw)
    (tmp_path/'W1/pages').mkdir(parents=True)
    res.dump(tmp_path/'W1/pages/p.json',dict(response=str(rawpath),response_sha256=prep.sha(rawpath)))
    monkeypatch.setattr(prep,'ROOT',tmp_path)
    monkeypatch.setattr(prep,'OUT',tmp_path/'out');(tmp_path/'out').mkdir()
    monkeypatch.setattr(prep,'RUN',tmp_path)
    row=dict(pool='W1',page_id='p',docai_line_index=0,crop_bbox=bbox,crop=str(tmp_path/'deleted.png'),
             crop_source_image=str(sourcepath),crop_sha256=crop_hash,id='line',document='doc',source='synthetic',label='αη')
    ww=prep.locate(row,{},{});assert len(ww)==1
    word=ww[0];assert word['crop_letter_offset']==0
    assert prep.sha(Path(word['crop']))==crop_hash
    assert word['token_box']==[23,8,43,26]
    lo,_,hi,h=word['word_box']
    assert lo<=23 and hi>=43 and h==40
    row['label']='αη β'
    with pytest.raises(ValueError,match='line_anchor_text_mismatch'):
        prep.locate(row,{},{})


def test_inconsistent_tuple_and_literal_refused():
    card=dict(card_id='x',options={'A':'η'},anchor_index=0)
    with pytest.raises(ValueError,match='contradicts literal'):
        res.normalise(answer(card,anchor_heads=heads(subscript='present')),card)


def test_literal_base_error_can_be_a_digit_without_invented_anchor():
    card=dict(card_id='x',options={'A':'δ'},anchor_index=0)
    a=res.normalise(answer(card,'8',anchor_heads=dict.fromkeys(res.HEADS,'unknown')),card)
    assert a['form']=='8'
    key=dict(card_id='x',slice='capitals',crop_sha256='c',word_index=0,anchor_index=0,target_head='breathing',crop_letter_offset=0)
    truth=res.resolve_card(key,[a,a])
    assert truth['printed_form']=='8' and truth['letter_heads']==[] and truth['status']=='unresolved'


def test_spacing_diacritics_are_not_copied_to_options():
    assert prep.options('᾿Α',0,'breathing','seed')==prep.options('Α',0,'breathing','seed')


@pytest.mark.parametrize('keraia',['\u0374','\u0384'])
def test_numeral_adjacent_capital_keeps_keraia_outside_heads(keraia):
    form='Α'+keraia
    assert prep.skeleton(form)=='Α' and res.letters(form)==['Α']
    opts=prep.options(form,0,'breathing','seed')
    assert all(v.endswith(keraia) for v in opts.values())
    card=dict(card_id='x',options=opts,anchor_index=0)
    a=res.normalise(answer(card,form),card)
    assert a['form']==form and a['heads'][0]==heads()


@pytest.mark.parametrize('ident,document',[
    ('acopiusphraseol00fraegoog--n230-l0019','acopiusphraseol00fraegoog'),
    ('13dcc39a-p000016-l0100','13dcc39a'),
])
def test_locked_document_alias_strips_page_and_line(ident,document):
    assert prep.line_doc(ident)==document


@pytest.mark.parametrize('value',[True,False,None])
def test_unmarked_ownership_is_na_in_normalisation_and_signature(value):
    card=dict(card_id='x',options={},anchor_index=0)
    a=res.normalise(answer(card,ownership_ok=value),card)
    assert a['ownership_ok'] is None
    b=deepcopy(a);b['ownership_ok']=True
    assert res.signature(a)==res.signature(b)


@pytest.mark.parametrize('expected_value',[True,None])
def test_unmarked_control_accepts_null_or_true(synthetic,expected_value):
    deck,cards,p1,p2,out=synthetic
    cp=json.loads((deck/'private/controls_proposed.json').read_text())
    for c in cp['controls']:
        c['expected_ownership_ok']=expected_value
    res.dump(deck/'private/controls_proposed.json',cp)
    rows=res.read(p1)
    for r in rows:
        r['ownership_ok']=None
    res.write(p1,rows)
    truth,gates,inv=res.run(deck,p1,p2,out)
    assert gates['reader1']['control_errors']==0
    assert all(t['status']=='resolved' and t['ownership_ok'] is None for t in truth)
    assert inv['T2:subscript']['complete']==2
    assert not (out/'tiebreak').exists()


def test_marked_ownership_still_distinguishes_votes():
    card=dict(card_id='x',options={},anchor_index=0)
    a=res.normalise(answer(card,'ῃ',anchor_heads=heads(subscript='present')),card)
    b=res.normalise(answer(card,'ῃ',anchor_heads=heads(subscript='present'),ownership_ok=None),card)
    assert a['ownership_ok'] is True and b['ownership_ok'] is None
    assert res.signature(a)!=res.signature(b)


@pytest.mark.parametrize('changes,reason',[
    ({'anchor_heads':heads(subscript='present')},'contradicts literal'),
    ({'letter_heads':[dict(index=2,**heads())]},'outside transcription'),
    ({'confidence':'bad'},'invalid confidence'),
    ({'note':None},'invalid confidence'),
])
def test_invalid_data_vote_survives_to_tiebreak_and_usage(synthetic,changes,reason):
    deck,cards,p1,p2,out=synthetic
    rows=res.read(p1);rows[0].update(changes);res.write(p1,rows)
    truth,gates,_=res.run(deck,p1,p2,out)
    g=gates['reader1']
    assert g['accepted'] and g['control_errors']==0
    assert g['invalid_answer_count']==1 and g['valid_answers']==4
    assert g['invalid_answers'][0]['card_id']=='data1'
    assert reason in g['invalid_answers'][0]['reason']
    assert truth[0]['votes']==1 and truth[0]['status']=='unresolved'
    assert truth[1]['status']=='resolved'
    third=res.read(out/'tiebreak/blind/cards.jsonl')
    assert {c['card_id'] for c in third}=={'data1','control1','control2','control3'}
    usage=json.loads((out/'opus_usage.json').read_text())[0]
    assert usage['invalid_answers']==1 and usage['input_tokens']==50
    receipt=json.loads((out/'resolution_receipt.json').read_text())
    assert receipt['invalid_answer_count']==1
    p3=out.parent/'r3.jsonl';res.write(p3,[answer(c) for c in third])
    truth,_,_=res.run(deck,p1,p2,out,p3)
    assert truth[0]['votes']==2 and truth[0]['status']=='resolved'


@pytest.mark.parametrize('n,accepted',[(1,True),(2,False)])
def test_invalid_control_vote_is_strict_gate_failure(synthetic,n,accepted):
    deck,cards,p1,p2,out=synthetic
    rows=res.read(p1)
    for r in rows[2:2+n]:
        r['anchor_heads']=heads(accent='acute')
    res.write(p1,rows)
    _,gates,_=res.run(deck,p1,p2,out)
    assert gates['reader1']['control_errors']==n
    assert gates['reader1']['invalid_answer_count']==n
    assert gates['reader1']['accepted'] is accepted


def test_dry_run_writes_validation_only_and_preserves_inputs(synthetic):
    deck,cards,p1,p2,out=synthetic
    inputs=[p for p in deck.rglob('*') if p.is_file()]+[p1,p2]
    before={p:p.read_bytes() for p in inputs}
    reader=p1.parent/'reader/answers.jsonl';res.write(reader,res.read(p1))
    g=res.validate_batch(deck,reader,deck/'blind/cards.jsonl',out)
    assert g['accepted']
    assert {p.name for p in out.iterdir()}=={'controls_gate.json','validation_receipt.json','opus_usage.json'}
    assert all(p.read_bytes()==content for p,content in before.items())
    with pytest.raises(ValueError,match='outside deck and reader'):
        res.validate_batch(deck,reader,deck/'blind/cards.jsonl',deck/'blind/forbidden')


def test_unmarked_anchor_keeps_other_explicitly_voted_heads():
    card=dict(card_id='x',options={},anchor_index=0)
    a=res.normalise(answer(card,'ηά',letter_heads=[dict(index=1,**heads(accent='acute'))],ownership_ok=None),card)
    key=dict(card_id='x',slice='specks',crop_sha256='c',word_index=0,anchor_index=0,target_head='breathing')
    t=res.resolve_card(key,[a,a])
    assert t['letter_heads'][0]['accent']=='none'
    assert t['letter_heads'][1]['accent']=='acute'


def test_marked_control_null_ownership_remains_a_failure(synthetic):
    deck,cards,p1,p2,out=synthetic
    cp=json.loads((deck/'private/controls_proposed.json').read_text())
    c=cp['controls'][0]
    c.update(expected_form='ῃ',expected_letter_heads=[dict(index=0,**heads(subscript='present'))])
    rows=res.read(p1)
    rows[2].update(transcription='ῃ',anchor_heads=heads(subscript='present'),ownership_ok=None)
    res.write(p1,rows)
    _,gate=res.batch(p1,{c['card_id']:c for c in cards},cp['controls'],[c['card_id'] for c in cards])
    assert gate['control_failures']==['control1']


def test_multiple_invalid_data_votes_do_not_reject_batch_or_agree(synthetic):
    deck,cards,p1,p2,out=synthetic
    for path in (p1,p2):
        rows=res.read(path)
        for r in rows:
            if r['card_id'].startswith('data'):
                r['anchor_heads']=heads(accent='acute')
        res.write(path,rows)
    truth,gates,_=res.run(deck,p1,p2,out)
    assert all(g['accepted'] and g['invalid_answer_count']==2 for g in gates.values())
    assert all(t['votes']==0 and t['status']=='unresolved' for t in truth)
    assert {c['card_id'] for c in res.read(out/'tiebreak/blind/cards.jsonl')}=={c['card_id'] for c in cards}


def test_dry_run_partial_assignment_remains_incomplete(synthetic):
    deck,cards,p1,p2,out=synthetic
    reader=p1.parent/'reader/answers.jsonl';res.write(reader,res.read(p1)[:-1])
    with pytest.raises(ValueError,match='IDs/order'):
        res.validate_batch(deck,reader,deck/'blind/cards.jsonl',out)
    assert not out.exists()


def test_offline_guard_is_scoped_and_restored():
    import socket
    connect, create = socket.socket.connect, socket.create_connection
    with pytest.raises(RuntimeError, match='saved geometry only'):
        with prep.offline_network():
            socket.create_connection(('localhost', 1))
    assert socket.socket.connect is connect
    assert socket.create_connection is create


def test_output_override_is_required_outside_worktree(synthetic, monkeypatch):
    deck, cards, p1, p2, out = synthetic
    monkeypatch.delenv('GREEK_OCR_R2C_TEST_OUTPUT_ROOT')
    with pytest.raises(ValueError, match='inside this worktree'):
        res.run(deck, p1, p2, out)
    assert not out.exists()
