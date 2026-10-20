from copy import deepcopy
import json
from pathlib import Path
import pytest
from PIL import Image, PngImagePlugin
from greekocr.adjudicate.deck import build_deck, crop_image, leak_scan
from greekocr.adjudicate.protocol import (adapt_answer, deal, tiebreak_deck,
    controls_gate, resolve, write_truth)


def make_deck(tmp_path, n=12):
    native=tmp_path/'private-source.png'
    image=Image.new('RGB',(180,40),'white')
    for x in range(30,70): image.putpixel((x,15),(0,0,0))
    metadata=PngImagePlugin.PngInfo();metadata.add_text('source','secret-book')
    image.save(native,pnginfo=metadata)
    records=[dict(image=str(native),bbox=[30,0,80,40],options=['ἅλφα','άλφα'],
                  private=dict(line_id=f'secret-line-{i}')) for i in range(n)]
    control=dict(records[0],pixel_verified=True,known_answer='ἅλφα')
    receipt=build_deck(dict(blind_dir=str(tmp_path/'run/blind'),items=records,controls=[control],seed=43,control_fraction=.07))
    cards=json.loads((Path(receipt['blind_dir'])/'items_blind.json').read_text())
    keys=json.loads(Path(receipt['private_key']).read_text())
    return cards,keys,receipt


def answers(cards, forms=None):
    return [dict(id=c['id'], answer=next(k for k,v in c['options'].items() if v==(forms or {}).get(c['id'],'ἅλφα')),
                 confidence='high',note='') for c in cards]


def test_deck_shuffles_controls_hashes_and_separates_key(tmp_path):
    cards,keys,receipt=make_deck(tmp_path)
    assert receipt['leak_scan']['passed']
    assert 0 < next(i for i,k in enumerate(keys) if k['control']) < len(keys)-1
    root=Path(receipt['blind_dir']);private=Path(receipt['private_key'])
    assert private.parent.parent==root.parent and not private.is_relative_to(root)
    for c in cards:
        assert set(c)=={'id','img','line_img','options','other_options'}
        for field in ('img','line_img'):
            import hashlib
            p=root/c[field]
            assert p.stem==hashlib.sha256(p.read_bytes()).hexdigest()
            with Image.open(p) as im: assert not im.info
    assert json.loads((root/'reader_2.json').read_text())==list(reversed(cards))
    assert deal(cards,2)==list(reversed(cards))
    old=private.read_bytes()
    import shutil
    shutil.rmtree(root)
    with pytest.raises(FileExistsError):
        build_deck(dict(blind_dir=root,items=[],controls=[]))
    assert private.read_bytes()==old


@pytest.mark.parametrize('profile',['letter','word','mark','line','page'])
def test_profiles_cap_and_geometry(profile):
    image=Image.new('RGB',(100,30),'white')
    cropped,receipt=crop_image(image,profile,bbox=[30,10,50,20] if profile not in ('line','page') else None)
    assert receipt['zoom_scale']<=3
    assert cropped.height in (30,90)
    assert receipt['crop_box'][1::2]==[0,30]
    with pytest.raises(ValueError):crop_image(image,profile,zoom_cap=4)
    with pytest.raises(ValueError):crop_image(image,profile,crop_box=[-1,0,5,20])


def test_leak_scan_and_failed_build_leaves_no_key(tmp_path):
    cards,keys,receipt=make_deck(tmp_path)
    root=Path(receipt['blind_dir'])
    (root/'oops.txt').write_text('source_crop /Users/someone/book')
    assert not leak_scan(root)['passed']
    (root/'oops.txt').unlink()
    (root/'redirect.png').symlink_to(tmp_path/'private-source.png')
    assert any(r['reason']=='symlink' for r in leak_scan(root)['findings'])
    bad=dict(image=str(tmp_path/'private-source.png'),options=['Google','other'],profile='line',pixel_verified=True,known_answer='Google')
    with pytest.raises(ValueError,match='leak scan'):
        build_deck(dict(blind_dir=tmp_path/'bad/blind',items=[],controls=[bad]))
    assert not (tmp_path/'bad/private/items_key.json').exists()
    assert not (tmp_path/'bad/blind').exists()
    with pytest.raises(ValueError,match='sibling'):
        build_deck(dict(blind_dir=tmp_path/'x',private_dir=tmp_path/'x/private',items=[]))
    with pytest.raises(ValueError,match='two readers'):
        build_deck(dict(blind_dir=tmp_path/'x',items=[],readers=1))
    with pytest.raises(ValueError,match='historical'):
        build_deck(dict(blind_dir=tmp_path/'x',items=[],preserve_order=True))


def test_resolution_gate_before_any_truth_and_unknown(tmp_path):
    cards,keys,_=make_deck(tmp_path)
    r1=answers(cards);r2=answers(deal(cards,2))
    result=resolve(cards,keys,r1,r2)
    assert result['status']=='RESOLVED' and len(result['truth'])==12
    assert all(t['status']=='AGREED' for t in result['truth'])
    control=next(k['id'] for k in keys if k['control'])
    broken=deepcopy(r2)
    a=next(a for a in broken if a['id']==control)
    card=next(c for c in cards if c['id']==control)
    a['answer']=next(k for k,v in card['options'].items() if v=='άλφα')
    failed=resolve(cards,keys,r1,broken)
    assert failed['status']=='CONTROLS_FAILED' and failed['truth']==[]
    with pytest.raises(ValueError,match='gate'):write_truth(tmp_path/'failed.jsonl',failed)
    data=next(k['id'] for k in keys if not k['control'])
    for reader in (r1,r2): next(a for a in reader if a['id']==data)['answer']='unreadable'
    unknown=resolve(cards,keys,r1,r2)
    assert next(t for t in unknown['truth'] if t['id']==data)['status']=='UNKNOWN'
    path=tmp_path/'truth.jsonl.gz';write_truth(path,unknown)
    with pytest.raises(FileExistsError):write_truth(path,unknown)
    with pytest.raises(ValueError,match='order'):resolve(cards,keys,r1,list(reversed(r2)))


def test_fresh_tiebreak_map_two_of_three_and_gate(tmp_path):
    cards,keys,receipt=make_deck(tmp_path)
    ident=next(k['id'] for k in keys if not k['control'])
    r1=answers(cards);r2=answers(deal(cards,2),{ident:'άλφα'})
    initial=resolve(cards,keys,r1,r2)
    assert initial['disagreements']==[ident] and initial['status']=='PENDING'
    tb=tiebreak_deck(cards,keys,[ident],image_root=receipt['blind_dir'],blind_dir=tmp_path/'tb/blind')
    tb_cards=json.loads((Path(tb['blind_dir'])/'items_blind.json').read_text())
    tb_keys=json.loads(Path(tb['private_key']).read_text())
    for key in tb_keys:
        assert list(key['public']['options'].values())!=list(key['provenance']['original_options'].values())
    third=answers(tb_cards)
    result=resolve(cards,keys,r1,r2,reader3=third,tiebreak_keys=tb_keys)
    row=next(t for t in result['truth'] if t['id']==ident)
    assert row['printed']=='ἅλφα' and row['status']=='MAJORITY_OF_3'
    ctl=next(k['id'] for k in tb_keys if k['control'])
    next(a for a in third if a['id']==ctl)['answer']='unreadable'
    result=resolve(cards,keys,r1,r2,reader3=third,tiebreak_keys=tb_keys)
    assert not result['third_gate']['passed']
    assert next(t for t in result['truth'] if t['id']==ident)['status']=='UNKNOWN'


@pytest.mark.parametrize('adapter',['canonical','r0','s8','r2c'])
def test_answer_adapters(adapter):
    card=dict(id='one',options={'A':'ἅ','B':'ά'},anchor_index=0)
    answer=dict(id='one',choice='A',transcription='ἅ',confidence='high',note='')
    if adapter=='s8':answer.pop('confidence');answer['uncertain']=False
    if adapter=='r2c':
        answer.pop('id');answer['card_id']='one'
        answer.update(readability='readable',ownership_ok=True,anchor_heads=dict(breathing='dasia',accent='acute',diaeresis='none',subscript='none'))
    out=adapt_answer(answer,card,adapter=adapter)
    assert out['printed']=='ἅ'
    if adapter=='r2c':
        answer['anchor_heads']['breathing']='unknown'
        assert adapt_answer(answer,card,adapter=adapter)['heads'][0]['breathing']=='unknown'
        answer['anchor_heads']['breathing']='psili'
        with pytest.raises(ValueError,match='contradicts'):adapt_answer(answer,card,adapter=adapter)
    else:
        answer['transcription']='ά'
        with pytest.raises(ValueError,match='contradicts'):adapt_answer(answer,card,adapter=adapter)


def test_historical_c1_gate_descriptions_and_shared_misses():
    assert controls_gate([{}],[],dict(readers=1,allow_no_controls=True,n=100,exact_n=100,minimum_rates={'letters':.9,'crop':.9},rates={'letters':.91,'crop':.95}))['passed']
    assert not controls_gate([{}],[],dict(readers=1,allow_no_controls=True,n=99,exact_n=100))['passed']
    assert controls_gate([{}],[],dict(readers=1,allow_no_controls=True,n=40,min_n=40))['passed']
    keys=[dict(id='c',control=True,known_answer='x')]
    batch={'c':dict(printed='bad')}
    assert not controls_gate([batch,batch],keys,dict(readers=2,max_errors=1,no_shared_misses=True))['passed']
    controls=[dict(id=f'c{i}',control=True,known_answer='x') for i in range(84)]
    first={k['id']:dict(printed='bad' if i<2 else 'x') for i,k in enumerate(controls)}
    second={k['id']:dict(printed='bad' if 2<=i<4 else 'x') for i,k in enumerate(controls)}
    assert controls_gate([first,second],controls,dict(readers=2,min_correct=82,expected_controls=84))['passed']
    second['c2']['printed']='x'
    second['c0']['printed']='bad'
    assert not controls_gate([first,second],controls,dict(readers=2,min_correct=82))['passed']


def test_palette_pixels_survive_metadata_removal(tmp_path):
    import numpy as np
    native=tmp_path/'palette.png'
    image=Image.new('P',(50,30),1)
    image.putpalette([0,0,0,10,100,200]+[0]*762)
    image.save(native)
    receipt=build_deck(dict(blind_dir=tmp_path/'palette/blind',items=[],controls=[dict(
        image=str(native),profile='line',options=['yes','no'],pixel_verified=True,known_answer='yes')]))
    cards=json.loads((Path(receipt['blind_dir'])/'items_blind.json').read_text())
    with Image.open(Path(receipt['blind_dir'])/cards[0]['line_img']) as emitted:
        assert np.array_equal(np.array(image.convert('RGB')),np.array(emitted.convert('RGB')))
        assert not emitted.info


def test_r2c_head_unknown_resolution_and_control_evidence_gate(tmp_path):
    cards,keys,_=make_deck(tmp_path)
    for card in cards:card['anchor_index']=0
    heads=dict(breathing='dasia',accent='acute',diaeresis='none',subscript='none')
    def structured(order):
        return [dict(a,readability='readable',ownership_ok=True,anchor_heads=deepcopy(heads)) for a in answers(order)]
    r1=structured(cards);r2=structured(deal(cards,2))
    control=next(k for k in keys if k['control'])
    # JSON key round-trip converts head index keys to strings in sealed evidence.
    control['expected_fields']=json.loads(json.dumps(dict(ownership_ok=True,readability='readable',heads={0:heads})))
    result=resolve(cards,keys,r1,r2,adapter='r2c')
    assert result['status']=='RESOLVED'
    ident=next(k['id'] for k in keys if not k['control'])
    for rows in (r1,r2):
        next(a for a in rows if a['id']==ident)['anchor_heads']['accent']='unknown'
    result=resolve(cards,keys,r1,r2,adapter='r2c')
    row=next(t for t in result['truth'] if t['id']==ident)
    assert row['heads'][0]['accent']=='unknown' and row['status']=='UNKNOWN'
    next(a for a in r1 if a['id']==control['id'])['anchor_heads']['accent']='unknown'
    assert resolve(cards,keys,r1,r2,adapter='r2c')['status']=='CONTROLS_FAILED'


def test_free_transcription_controls_and_tiebreak(tmp_path):
    native=tmp_path/'native.png';Image.new('L',(80,40),255).save(native)
    base=dict(image=str(native),profile='line',free_text=True)
    receipt=build_deck(dict(blind_dir=tmp_path/'free/blind',items=[base],controls=[dict(base,pixel_verified=True,known_answer='ἅ')]))
    cards=json.loads((Path(receipt['blind_dir'])/'items_blind.json').read_text())
    keys=json.loads(Path(receipt['private_key']).read_text())
    def literal(card,text):return dict(id=card['id'],answer='literal',printed=text,confidence='medium',note='')
    r1=[literal(c,'ἅ') for c in cards]
    ident=next(k['id'] for k in keys if not k['control'])
    r2=[literal(c,'ά' if c['id']==ident else 'ἅ') for c in deal(cards,2)]
    assert resolve(cards,keys,r1,r2)['disagreements']==[ident]
    tb=tiebreak_deck(cards,keys,[ident],image_root=receipt['blind_dir'],blind_dir=tmp_path/'free_tb/blind')
    tb_cards=json.loads((Path(tb['blind_dir'])/'items_blind.json').read_text())
    tb_keys=json.loads(Path(tb['private_key']).read_text())
    result=resolve(cards,keys,r1,r2,reader3=[literal(c,'ἅ') for c in tb_cards],tiebreak_keys=tb_keys)
    assert result['status']=='RESOLVED' and result['truth'][0]['verdict']=='ἅ'
    nested=build_deck(dict(blind_dir=tmp_path/'tagged/blind',private_dir=tmp_path/'tagged/sealed/ib',
        items=[base],controls=[dict(base,pixel_verified=True,known_answer='ἅ')]))
    assert Path(nested['private_key'])==tmp_path/'tagged/sealed/ib/items_key.json'
