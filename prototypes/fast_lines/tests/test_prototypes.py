import importlib
import cv2,numpy as np,pytest
from prototypes.fast_lines.shared.context import Context
from prototypes.fast_lines.shared.contracts import rect
from prototypes.fast_lines.shared.detector import postprocess

@pytest.fixture
def ctx():
    im=np.full((240,400),245,np.uint8); pm=np.zeros((240,400),np.float32)
    for y in (45,85,125,165):
        for x in range(25,375,14): cv2.rectangle(im,(x,y),(x+7,y+10),40,-1)
        pm[y+2:y+9,25:380]=.9
    items=postprocess(pm,(400,240))
    c=Context(im,pm,items); c.products['residual_ledger']={'requests':[{'id':'test','bbox':[0,0,400,240],'derivation':['test']}]}
    return c

@pytest.mark.parametrize('name',['native_contours','layout_barriers','local_ribbons','sheet_lattice','foreground_profiles','residual_ledger','font_guides','image_motifs','ink_condition','map_graph','classical_residual'])
def test_prototype_contract(ctx,name):
    result=importlib.import_module('prototypes.fast_lines.'+name+'.run').run(ctx,2)
    assert 'status' in result and isinstance(result['items'],list)
    for item in result['items']:
        assert 'baseline' in item and np.isfinite(np.asarray(item['polygon'])).all()
        assert not item.get('discounted')

def test_selective_remap_has_no_invented_score(ctx):
    from prototypes.fast_lines.selective_rerun.run import run
    class FakeDetector:
        def infer(self,image,long_side=960):
            h,w=image.shape; p=np.zeros((h,w),np.float32); p[h//3:h//3+8,w//4:3*w//4]=.9
            return p,{'tensor':[1,3,h,w],'map_shape':[h,w],'preprocess_s':0.,'inference_s':0.}
    ctx.detector=FakeDetector(); r=run(ctx)
    assert len(r['calls'])==3 and {q['variant'] for q in r['calls']}=={'scale','unbend','combined'}
    assert all(q['baseline'] is None for q in r['items'])

def test_foreground_ambiguity_preserves_pale_text(ctx):
    from prototypes.fast_lines.foreground_profiles.run import run
    r=run(ctx); assert r['items']==ctx.items
    assert all(q['ownership']=='unknown' for q in r['lines'])

def test_table_preservation(ctx):
    from prototypes.fast_lines.layout_barriers.run import run
    for x in (20,200,380): cv2.line(ctx.gray,(x,20),(x,210),0,2)
    for y in (20,80,140,210): cv2.line(ctx.gray,(20,y),(380,y),0,2)
    r=run(ctx); assert r['table'] and not r['changes']

def test_null_score_json_roundtrip(tmp_path,ctx):
    import json
    from prototypes.fast_lines.shared.review import write_result
    q={'polygon':rect([-5,2,450,20]),'baseline':None,'score':None}
    write_result(tmp_path,{'page':'synthetic','image_size':list(ctx.size),'group':'test'},ctx.gray,{'items':[q]},0.)
    data=json.loads((tmp_path/'synthetic.json').read_text())
    assert data['items'][0]['score'] is None
    assert np.asarray(data['items'][0]['polygon'])[:,0].min()==0
    assert np.asarray(data['items'][0]['polygon'])[:,0].max()==400

def test_map_graph_barrier_never_crossed(ctx):
    from prototypes.fast_lines.map_graph.run import run
    ctx.products['layout_barriers']={'barriers':[{'bbox':[198,0,202,240]}]}
    r=run(ctx)
    for q in r['candidates']:
        p=np.asarray(q['polygon']); assert not (p[:,0].min()<200<p[:,0].max())

def test_sloped_separator_splits_prose_not_table():
    from prototypes.fast_lines.layout_barriers.run import run
    image=np.full((600,600),245,np.uint8); items=[]
    cv2.line(image,(290,30),(305,570),20,2)
    for y in range(70,550,35):
        for x in list(range(50,275,14))+list(range(325,555,14)):
            cv2.rectangle(image,(x,y),(x+7,y+14),30,-1)
        items.append({'polygon':rect([45,y-3,565,y+20]),'baseline':None,'score':.8})
    ctx=Context(image,np.zeros((600,600),np.float32),items)
    r=run(ctx); assert not r['table'] and len(r['changes'])>=10
    assert any(q['kind']=='sloped rule' for q in r['barriers'])
