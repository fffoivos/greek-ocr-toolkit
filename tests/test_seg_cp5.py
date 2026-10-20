"""CP5 orientation mechanics and independent horizontal structural evidence."""
from copy import deepcopy
from pathlib import Path
from tests._paths import run_record
import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont, ImageOps
from greekocr.harvest import orientation_screen as s
from greekocr.harvest import geometry_observations as g
from greekocr.harvest.neighbour_words import neighbour_word_evidence
from test_seg_cp3 import planted

FONT=Path(__file__).parent/'fixtures/fonts/GFSDidot-Regular.ttf'


def writing(text='λόγος καὶ λόγος', angle=0, pad=(8,8,8,8)):
    font=ImageFont.truetype(str(FONT),32)
    box=font.getbbox(text)
    im=Image.new('L',(box[2]-box[0]+8,box[3]-box[1]+8),255)
    ImageDraw.Draw(im).text((4-box[0],4-box[1]),text,font=font,fill=0)
    return ImageOps.expand(im.rotate(angle,expand=True),pad,255)


@pytest.mark.parametrize('text',['λόγος','123456'])
@pytest.mark.parametrize('angle',[0,90,270])
def test_letters_and_digits_axis_independent_of_polarity(text,angle):
    kind='numbers' if text.isdigit() else 'unknown'
    m=s.observe_orientation(writing(text,angle),isolated_line=True,content_kind=kind)
    assert m['rotated'] == (None if text.isdigit() else angle!=0)
    if kind=='numbers': assert m['decision']['orientation_cw'] is None


def test_wide_padded_vertical():
    im=writing(angle=90,pad=(300,10,300,10))
    assert im.width>im.height
    assert s.observe_orientation(im,isolated_line=True)['rotated']


@pytest.mark.parametrize('text',['ΟΙ','12'])
def test_tall_canvas_upright_controls(text):
    im=writing(text,pad=(2,100,2,100))
    assert im.height>im.width
    assert s.observe_orientation(im,isolated_line=True,
        content_kind='numbers' if text.isdigit() else 'unknown')['rotated'] is None


def test_uncertain_square_abstains():
    m=s.observe_orientation(Image.new('L',(70,70),255))
    assert m['status']=='orientation_unknown' and m['rotated'] is None


def test_sloped_horizontal():
    assert s.observe_orientation(writing().rotate(8,expand=True,fillcolor=255),
                                 isolated_line=True)['rotated'] is False


def test_line_extent_is_diagnostic_in_both_contexts(monkeypatch):
    from greekocr.glyphs.orientation import Orientation
    calls=[]
    def measure(im,**kw):
        calls.append(kw)
        return Orientation(axis='horizontal')
    monkeypatch.setattr(s,'measure_orientation',measure)
    s.observe_orientation(writing());s.observe_orientation(writing(),isolated_line=True)
    assert [c['unit'] for c in calls]==['block','line','block','line']
    assert all(c['use_osd'] is False for c in calls)


def test_saved_local_hashes_and_no_remeasurement(monkeypatch):
    im=writing();m=s.observe_orientation(im)
    monkeypatch.setattr(s,'measure_orientation',lambda *a,**k:pytest.fail('saved hit remeasured'))
    assert s.observe_orientation(im,saved=m)['source']=='saved_local'
    assert s.observe_orientation(writing('ἄλλος λόγος'),saved=m)['status']=='unavailable'
    changed=deepcopy(m);changed['decision']['axis']='vertical'
    assert s.observe_orientation(im,saved=changed)['reason']=='corrupt_local_orientation'
    assert s.observe_orientation(im,saved=m,isolated_line=True)['status']=='unavailable'


@pytest.mark.parametrize('n',[2,3])
def test_horizontal_multiline_not_discharged_by_axis(n):
    p=planted([(f'r{i}','c',10,100,15+35*i,0) for i in range(n)])
    st=neighbour_word_evidence(p,[0,0,160,150])
    assert st['union_drop'] is True
    result=s.compose_cp5(dict(status='measured',rotated=False),st,
                         dict(status='unavailable',drop=None))
    assert result['measured_drop'] and result['drop']


def crossing_page(tmp_path):
    p=planted([('left','c0',10,70,50,0),('right','c1',90,145,50,0)])
    # A long original separator, not a new separator detector.
    p['ink'][5:145,79:81]=True
    path=tmp_path/'page.png';Image.fromarray(np.where(p['ink'],0,255).astype('uint8')).save(path)
    p['source']=path
    return p


def test_validated_cross_column_and_crop_locality(tmp_path):
    p=crossing_page(tmp_path); before=p['ink'].copy()
    # A structural row envelope spans both sides; pixel crossing must prove it.
    row=dict(p['rows'][0]);a,b=10,145
    for key in p['ownership'].CURVES: row[key]=np.full(b-a,float(row[key][0]))
    row.update(x0=a,x1=b,component_ids=p['rows'][0]['component_ids']+p['rows'][1]['component_ids'])
    row=p['ownership'].prepare_row(row,p['ink'],p['labels'])
    p['rows']=[row]
    boundaries=[dict(id='separator',kind='rule',path=[[80,5],[80,144]])]
    m=s.column_crossings(p,[0,0,160,150],boundaries)
    assert len(m['validated'])==1 and m['drop']
    assert not s.column_crossings(p,[0,0,75,150],boundaries)['drop']
    assert np.array_equal(p['ink'],before)
    # No original stroke: an unvalidated proposal cannot cause DROP.
    p['ink'][5:145,79:81]=False
    Image.fromarray(np.where(p['ink'],0,255).astype('uint8')).save(p['source'])
    assert not s.column_crossings(p,[0,0,160,150],boundaries)['drop']


def test_missing_crossing_evidence_not_clean(tmp_path):
    p=crossing_page(tmp_path)
    assert s.column_crossings(p,[0,0,160,150],None)['drop'] is None
    result=s.compose_cp5(dict(status='unresolved',rotated=None),
        dict(status='measured',union_drop=False),dict(status='unavailable',drop=None))
    assert result['drop'] is None


def test_regional_numeric_polarity_does_not_suppress_axis():
    from greekocr.glyphs.orientation import Orientation
    rows=s.regional_context([], [dict(id='numeric',content_kind='numbers',
        decision=Orientation(axis='vertical',orientation_cw=90))])['resolved']
    assert rows[0]['decision'].axis=='vertical' and rows[0]['decision'].orientation_cw is None


@pytest.mark.parametrize('angle',[0,90,270])
def test_compact_heading_abstains_in_every_orientation(angle):
    m=s.observe_orientation(writing('ΟΙ',angle),isolated_line=True)
    assert m['rotated'] is None
    assert m['reason']=='compact_ink'


def test_actual_line_extent_override_cannot_resolve_block_abstention():
    im=writing('123456')
    line=s.observe_orientation(im,isolated_line=True,content_kind='numbers')
    block=s.observe_orientation(im,content_kind='numbers')
    for result in (line,block):
        evidence=result['decision']['evidence']
        assert evidence['line_diagnostic']['evidence']['axis_source']=='isolated-ink-chain-extent'
        assert evidence['block_diagnostic']['axis']=='unknown'
        assert result['rotated'] is None
        assert evidence['regional_context']==[]


def test_saved_options_adapter_and_dependency_identity(monkeypatch):
    im=writing();m=s.observe_orientation(im)
    assert m['binding']['adapter_sha256']==g.sha(s.__file__)
    assert m['binding']['dependencies']==g.implementation_binding()['dependencies']
    changed=deepcopy(m);changed['binding']['dependencies']['numpy']='stale'
    assert s.observe_orientation(im,saved=changed)['status']=='unavailable'


@pytest.mark.parametrize('case',['head','scope'])
def test_cp5_guard_rejects_head_and_scope(case,monkeypatch):
    import runpy
    guard=run_record(str(Path(__file__).parents[1]/'docs/records/harvest/collect_v3_admission/seg/guard_cp5_commit.py'))
    monkeypatch.setattr(guard['subprocess'],'check_output',lambda *a,**kw:'current\n')
    manifest=dict(base_HEAD='old' if case=='head' else 'current',files=[],read_only_dependencies=[])
    with pytest.raises(ValueError,match='base HEAD moved' if case=='head' else 'exact review scope'):
        guard['verify'](manifest)


@pytest.mark.parametrize('block,line',[('vertical','horizontal'),('horizontal','vertical')])
def test_disagreement_never_excludes(monkeypatch,block,line):
    from greekocr.glyphs.orientation import Orientation
    monkeypatch.setattr(s,'measure_orientation',lambda im,**kw:Orientation(axis=block if kw['unit']=='block' else line))
    monkeypatch.setattr(s,'discover_directions',lambda im:[])
    result=s.observe_orientation(writing())
    assert result['rotated'] is None and result['reason']=='line_block_disagreement'


def test_compact_agreement_is_still_abstention(monkeypatch):
    from greekocr.glyphs.orientation import Orientation
    monkeypatch.setattr(s,'measure_orientation',lambda *a,**kw:Orientation(axis='vertical'))
    result=s.observe_orientation(writing('ΟΙ'))
    assert result['rotated'] is None and result['reason']=='compact_ink'


def test_separator_cache_identity_and_corruption(tmp_path):
    import json
    from greekocr.harvest import separator_inventory as inventory
    page=dict(binding=dict(source_sha256='source',frame=0))
    data=dict(binding=inventory.binding(page),boundaries=[])
    path=tmp_path/'inventory.json';path.write_text(json.dumps(data))
    receipt=dict(binding=data['binding'],inventory_sha256=g.sha(path))
    (tmp_path/'receipt.json').write_text(json.dumps(receipt))
    assert inventory.load(page,tmp_path)['boundaries']==[]
    with pytest.raises(ValueError,match='stale'):
        inventory.load(dict(binding=dict(source_sha256='other',frame=0)),tmp_path)
    path.write_text('{}')
    with pytest.raises(ValueError,match='corrupt'):inventory.load(page,tmp_path)


def test_once_only_separator_claim_binds_source_alias(tmp_path):
    import runpy
    module=run_record(str(Path(__file__).parents[1]/'docs/records/harvest/collect_v3_admission/seg/prepare_cp4_geometry.py'))
    claim=module['claim_attempt']
    metadata=dict(id='first',image=str(tmp_path/'source.png'),image_sha256='sha')
    assert claim(tmp_path,metadata,'detector',dict(options='bound'))
    assert not claim(tmp_path,dict(metadata,id='alias'),'detector',dict(options='bound'))
    with pytest.raises(ValueError,match='identity_changed'):
        claim(tmp_path,metadata,'changed',{})


@pytest.mark.parametrize('text,cls,flag',[
    ('ΟΙ','headings_caps','short_line'),('12','numerics_tables','numeric_shape'),
    ('λόγος','greek_mono','short_line')])
def test_text_rules_precede_screen_for_short_controls(text,cls,flag):
    from greekocr.harvest.admission import evaluate
    result=evaluate(dict(source='gazette_modern',label=text,primary_class=cls))
    assert result['checks'][flag]=='fail'


@pytest.mark.parametrize('local,axes,expected,source', [
    ('unknown',['vertical'],'vertical','regional'),
    ('unknown',['vertical','horizontal'],'unknown','unknown'),
    ('horizontal',['vertical'],'horizontal','measured'),
    ('unknown',['unknown'],'unknown','unknown'),
])
def test_coordinator_regional_inheritance(local,axes,expected,source):
    from greekocr.glyphs.orientation import Orientation
    observation=dict(status='orientation_unknown' if local=='unknown' else 'measured',
        rotated=None if local=='unknown' else False, decision_source='unknown' if local=='unknown' else 'measured',
        decision=Orientation(axis=local).to_record())
    regions=[dict(id=str(i),box=[0,0,100,100],axis=a,decision=Orientation(axis=a).to_record()) for i,a in enumerate(axes)]
    original=deepcopy(observation)
    out=s.inherit_regional_axis(observation,[10,10,90,90],regions,page_binding=dict(source_sha256='test'))
    assert out['decision']['axis']==expected and out['decision_source']==source
    assert observation==original
    if expected=='unknown':
        union=s.compose_cp5(out,dict(status='measured',union_drop=False),dict(status='measured',drop=False))
        assert union['drop'] is False and not union['verified_keep']
        assert union['measured_drop'] is None
        assert union['orientation_status']=='orientation_unknown'


def test_regional_overlap_without_membership_does_not_inherit():
    from greekocr.glyphs.orientation import Orientation
    m=dict(status='orientation_unknown',rotated=None,decision_source='unknown',decision=Orientation().to_record())
    r=dict(id='edge',box=[0,0,20,100],axis='vertical',decision=Orientation(axis='vertical').to_record())
    assert s.inherit_regional_axis(m,[10,10,90,90],[r],page_binding={})['rotated'] is None


def test_saved_regional_evidence_requires_page_revalidation():
    im=writing('123456');m=s.observe_orientation(im)
    m['decision']['evidence']['page_regional_inheritance']={}
    m['decision_sha256']=s.decision_sha(m['decision'])
    assert s.observe_orientation(im,saved=m)['reason']=='regional_context_requires_revalidation'


def test_orientation_unknown_does_not_cancel_structural_positive():
    m=dict(status='orientation_unknown',rotated=None)
    assert s.compose_cp5(m,dict(status='measured',union_drop=True),dict(status='measured',drop=False))['drop'] is True
