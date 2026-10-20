"""Actual final caller and strips on small, original-pixel-bound observations.

Only upstream outputs are frozen. The final ownership/bands/raster and its
transaction execute normally. No ignored capture or absolute path is required.
"""
from pathlib import Path
from types import SimpleNamespace
import copy,hashlib,json
import cv2,numpy as np,pytest
from ..shared import geometry_bands as G,type_completion as R
from ..shared.geometry_final_support import identity
from ..stack import pipeline as P
F=Path(__file__).parent


def fixture(key):
    meta=json.loads((F/'final_bands_native.json').read_text())
    assert hashlib.sha256((F/'final_bands_native.npz').read_bytes()).hexdigest()==meta['fixture_sha256']
    case=next(x for x in meta['cases'] if x['key']==key);z=np.load(F/'final_bands_native.npz');gray=z[key+'_gray'];assert hashlib.sha256(gray.tobytes()).hexdigest()==case['pixels_sha256']
    ctx=dict(image=gray,shape=gray.shape,height=case['height'],scale=1.,threshold=.08,paper_kernel=case['kernel'],ink=z[key+'_ink'],strong=z[key+'_strong'])
    items=copy.deepcopy(case['items'])
    if key=='r4959':
        request_meta=json.loads((F/'request_bands_native.json').read_text());request_arrays=np.load(F/'request_bands_native.npz')
        assert request_meta['input_sha256']==case['input_sha256']
        for q in items:
            native={109:3,107:4,105:5,103:6}.get(q['fixture_parent_index'])
            if native is None:continue
            ids=request_meta['audit'][native]['admitted_components'];yy,xx=np.nonzero(np.isin(request_arrays['labels'],ids))
            points=np.c_[xx,yy]+request_meta['origin']-np.array(case['origin'])
            xs=np.array([xx.min(),xx.max()]);axis=request_meta['axes'][native];path=np.c_[xs,axis[0]+axis[1]*xs]+request_meta['origin']-np.array(case['origin'])
            q['_selected_pixel_support']=dict(points=points,path=path,image=gray,shape=gray.shape,namespace=request_meta['observation'],height=request_meta['height'])
    return gray,items,ctx


def decision_fixture():
    """Known finite R pair for decision-contract tests, not a page gain claim."""
    gray,items,ctx=fixture('r4959')
    return gray,[q for q in items if q['fixture_parent_index'] in [107,105]],ctx


def freeze_upstream(monkeypatch,gray,items,ctx):
    """Compose reaches its real final boundary with hash-bound upstream items."""
    height=ctx['height'];witness=dict(height=height,candidates=[])
    monkeypatch.setattr(P,'scout',lambda *a:(witness,None))
    monkeypatch.setattr(P,'sample_boxes',lambda *a:None)
    ownership=dict(height=height,suppress_indices=[],image_size=gray.shape[::-1])
    ink=dict(items=items,ownership=ownership,removed=[],removal_reasons={},scout_s=0.,ink_s=0.,seal_s=0.,discrete_scout_s=0.,discrete_refinement_s=0.,refinement_s=0.)
    ownership.update(scout_s=0.,seconds=0.)
    monkeypatch.setattr(P,'ink_run',lambda *a,**k:ink)
    monkeypatch.setattr(P,'edge_scout',lambda *a:dict(trigger=False))
    geo=dict(items=items,witness=witness,columns=dict(changes=[],rules=[]),changes=[],curved=None,fragments=dict(joins=[]),joined_reduction=0,**{k:0. for k in ['scout_s','geometry_s','curved_s','fragment_s','column_s']})
    monkeypatch.setattr(P,'geometry_run',lambda *a,**k:geo)
    monkeypatch.setattr(P,'recover',lambda *a,**k:dict(items=items,added=[],scout_s=0.,correction_s=0.))
    monkeypatch.setattr(P,'smooth_envelopes',lambda *a,**k:dict(items=items,changes=[]))
    monkeypatch.setattr(P,'relative_faintness',lambda *a,**k:dict(suppress_indices=[],scout_s=0.))
    monkeypatch.setattr(P,'split_rows',lambda *a,**k:dict(items=items,changes=[],scout_s=0.,native_s=0.))
    def reconcile(gray,items,prepared_output):
        prepared_output.update(ctx)
        return dict(items=items,changes=[],seconds=0.)
    monkeypatch.setattr(P,'reconcile_rows',reconcile)
    monkeypatch.setattr(P,'frame_render',lambda *a:SimpleNamespace(bands=[],units=np.array([]),sides=np.array([])))
    # Source, motifs/rules, final frame and identity refresh remain actual code.


def compose_fixture(monkeypatch,key):
    gray,items,ctx=fixture(key);freeze_upstream(monkeypatch,gray,items,ctx)
    result=P.compose(gray,np.zeros((1,1),np.float32),items,None,use_final_export=True)
    return gray,items,ctx,result


def request():
    meta=json.loads((F/'request_bands_native.json').read_text());file=F/'request_bands_native.npz'
    assert hashlib.sha256(file.read_bytes()).hexdigest()==meta['fixture_sha256'];z=np.load(file)
    assert hashlib.sha256(z['gray'].tobytes()).hexdigest()==meta['pixel_sha256']
    h=meta['height'];paper=cv2.boxFilter(z['gray'],cv2.CV_32F,(max(3,round(4*h)|1),)*2)
    assert np.array_equal(paper-z['gray']>20.4,z['ink']>0)
    audit=copy.deepcopy(meta['audit']);out=R.corridor_hulls(copy.deepcopy(meta['rows']),audit,z['ink'],z['labels'],z['stats'],h,set(meta['target_rows']),axes=meta['axes'])
    return z,meta,audit,out


def slope(q):
    p=np.array(q['polygon']);right=int(np.argmax(p[:,0]));edges=[p[:right+1],np.vstack([p[right:],p[0]])[::-1]]
    return max(float(np.max(abs(np.diff(e[:,1])[np.diff(e[:,0])>0]/np.diff(e[:,0])[np.diff(e[:,0])>0]))) for e in edges)


def assert_seams(gray,items,seams):
    for seam in seams:
        i,j=seam['rows'];a,c=seam['domain_x'];x=np.arange(a,c);p=np.array(seam['path']);y=np.floor(np.interp(x,p[:,0],p[:,1])).astype(int)
        masks=[G.crop_mask(gray.shape,items[k]) for k in [i,j]]
        assert np.all((masks[0]+masks[1])[y,x]==1),'shared separator pixels must be claimed once by actual final masks'
        assert not np.any(masks[0]&masks[1]),'shared final crops overlap'


def test_committed_real_R_gain_and_native_members():
    z,meta,audit,out=request()
    for j in [3,4,5,6]:
        m=G.crop_mask(z['ink'].shape,out[j]);hits=np.bincount(z['labels'][m>0],minlength=len(z['stats']));ids=audit[j]['admitted_components']
        assert set(np.flatnonzero(hits))-{0}==set(ids),'foreign native row ink'
        assert all(hits[k]==z['stats'][k,4] for k in ids),'whole selected native member clipped'
    for j in [4,5]:assert slope(out[j])<=G.MAX_SLOPE+1e-6,'tight per-letter edge restored'
    seam=next(s for s in out[4]['shared_separators'] if s['rows']==[4,5]);assert_seams(z['gray'],out,[seam])
    a,c=seam['domain_x'];x=np.arange(a,c);y=np.arange(z['ink'].shape[0])[:,None];axes=meta['axes'];domain=(y>=axes[4][0]+axes[4][1]*x)&(y<=axes[5][0]+axes[5][1]*x)
    counts=G.crop_mask(z['ink'].shape,out[4])[:,a:c]+G.crop_mask(z['ink'].shape,out[5])[:,a:c]
    assert np.all(counts[domain]==1),'frozen supported middle domain has gap/overlap'


def partition_counts(gray,items):
    return sum((G.crop_mask(gray.shape,q).astype(np.uint16) for q in items),np.zeros(gray.shape,np.uint16))


def whole_native(gray,before,after,ctx):
    _,labels,stats,_=cv2.connectedComponentsWithStats(ctx['ink'].astype(np.uint8),8)
    old=partition_counts(gray,before);new=partition_counts(gray,after)
    assert not np.any((old>0)&(new==0)&ctx['ink']),'accepted native text lost'
    def hits(items):return np.array([np.bincount(labels[G.crop_mask(gray.shape,q)>0],minlength=len(stats)) for q in items])
    a,b=hits(before),hits(after);oldwhole=(a==stats[:,4]).any(0);newwhole=(b==stats[:,4]).any(0);oldwhole[0]=False
    assert not np.any(oldwhole&~newwhole),'whole old component newly cut'
    return old,new


@pytest.mark.parametrize('key',['r4959','p44b5','p3229','phase35','interaction','db97'])
def test_real_final_construction_conserves_whole_native_support(monkeypatch,key):
    gray,before,ctx,r=compose_fixture(monkeypatch,key)
    whole_native(gray,before,r['items'],ctx)
    assert r['final_bands']['considered']==len(before)
    assert r['final_bands']['preparation']['labels_builds']==1
    assert r['final_bands']['preparation']['reused']
    assert all('_selected_pixel_support' not in q for q in r['items'])


@pytest.mark.parametrize('key',['r4959','p44b5','db97'])
def test_real_final_caller_reaches_full_lines_beyond_R_B(monkeypatch,key):
    gray,before,ctx,r=compose_fixture(monkeypatch,key)
    old,new=whole_native(gray,before,r['items'],ctx)
    assert r['final_bands']['pairs'],'shared construction bypassed'
    assert any(not q.get('type_residual') and not q.get('row_partition') and q.get('final_band') for q in r['items'])
    assert int((new>1).sum())<int((old>1).sum()) or key=='db97'
    assert any(not np.array_equal(G.crop_mask(gray.shape,a),G.crop_mask(gray.shape,b)) for a,b in zip(before,r['items']))


def test_retained_R_pixels_complete_in_actual_final_crops(monkeypatch):
    gray,items,ctx=fixture('r4959');witnesses={i:q['_selected_pixel_support']['points'].copy() for i,q in enumerate(items) if q.get('_selected_pixel_support')}
    freeze_upstream(monkeypatch,gray,items,ctx);r=P.compose(gray,np.zeros((1,1),np.float32),items,None,use_final_export=True)
    for i,points in witnesses.items():
        m=G.crop_mask(gray.shape,r['items'][i]);assert m[points[:,1],points[:,0]].all(),'original selected R ink clipped'


def ordinary_pair(gray,r):
    for pair in r['final_bands']['pairs']:
        i,j=pair['rows'];a,c=pair['domain_x']
        if c-a<30:continue
        blocked=np.zeros(c-a,bool)
        for q in r['items']:
            for x,z in q.get('legacy_intervals',[]):blocked|=(np.arange(a,c)>=x)&(np.arange(a,c)<z)
        if np.count_nonzero(~blocked)>30:return pair,blocked
    raise AssertionError('no surviving ordinary seam')


def assert_actual_shared_pixels(gray,r,pair,blocked):
    i,j=pair['rows'];a,c=pair['domain_x'];p=np.array(pair['path']);x=np.arange(a,c)[~blocked];y=np.floor(np.interp(x,p[:,0],p[:,1])).astype(int)
    count=partition_counts(gray,r['items'])
    assert np.all(count[y,x]==1),'surviving final separator gap or overlap'


@pytest.mark.parametrize('mutation',['bypass','R_B_only'])
def test_real_final_bypass_loses_ordinary_partition(monkeypatch,mutation):
    gray,before,ctx,r=compose_fixture(monkeypatch,'db97');pair,blocked=ordinary_pair(gray,r);assert_actual_shared_pixels(gray,r,pair,blocked)
    operation=P.tessellate
    def altered(gray,items,**kw):
        if mutation=='R_B_only' and any(q.get('type_residual') or q.get('row_partition') for q in items):return operation(gray,items,**kw)
        return dict(items=items,migrated=[],disabled=True,seconds=0.)
    monkeypatch.setattr(P,'tessellate',altered)
    changed=P.compose(gray,np.zeros((1,1),np.float32),before,None,use_final_export=True)
    with pytest.raises(AssertionError,match='gap or overlap'):assert_actual_shared_pixels(gray,changed,pair,blocked)


def test_inclusive_mutation_duplicates_actual_shared_boundary(monkeypatch):
    gray,before,ctx,r=compose_fixture(monkeypatch,'db97');pair,blocked=ordinary_pair(gray,r);operation=G.polygon_mask
    monkeypatch.setattr(G,'polygon_mask',lambda shape,p,origin=(0,0),**kw:operation(shape,p,origin,half_open=False))
    with pytest.raises(AssertionError,match='gap or overlap'):assert_actual_shared_pixels(gray,r,pair,blocked)


def test_local_fallback_mutation_exposes_real_native_loss(monkeypatch):
    monkeypatch.setattr(G,'local_patch',lambda *a:None)
    gray,before,ctx,r=compose_fixture(monkeypatch,'r4959')
    with pytest.raises(AssertionError,match='native text lost|newly cut'):whole_native(gray,before,r['items'],ctx)


def test_content_callbacks_only_for_changed_native_support():
    gray,items,ctx=decision_fixture();calls=[]
    def refresh(pool,ids):
        calls.append(ids);return dict(input_identities={str(i):identity(pool[i]) for i in ids},refused_indices=[])
    r=G.tessellate(gray,items,prepared=ctx,refresh=refresh)
    assert len(calls)==int(bool(r['changed_content'])),'paper-only change reran content decision'
    assert any(not np.array_equal(G.crop_mask(gray.shape,a),G.crop_mask(gray.shape,b)) for a,b in zip(items,r['items']))


def test_real_changed_content_cannot_reuse_stale_receipt():
    gray,items,ctx=fixture('p44b5')
    with pytest.raises(ValueError,match='stale final decision refresh'):
        G.tessellate(gray,items,prepared=ctx,refresh=lambda pool,ids:dict(input_identities={},refused_indices=[]))


def test_order_permutation_preserves_native_ownership():
    gray,items,ctx=fixture('r4959')
    def run(xs):return G.tessellate(gray,xs,prepared=ctx,refresh=lambda pool,ids:dict(input_identities={str(i):identity(pool[i]) for i in ids},refused_indices=[]))['items']
    a=run(items);b=run(items[::-1])[::-1]
    assert all(np.array_equal(G.crop_mask(gray.shape,x)&ctx['ink'],G.crop_mask(gray.shape,y)&ctx['ink']) for x,y in zip(a,b)),'item order changes physical ink owners'


def test_nonmonotone_half_open_residue_preserves_concavity():
    from shapely.geometry import box
    p=box(1,1,10,10).difference(box(1,4,7,7));q=dict(polygon=list(p.exterior.coords)[:-1],raster_edges=G.EDGE_CONVENTION);m=G.crop_mask((12,12),q)
    assert m[2,2] and m[8,2] and not m[5,2] and m[5,8]


def test_actual_OCR_strip_consumes_all_independent_final_masks(monkeypatch,tmp_path):
    from . import round6_rows_export as E
    gray,before,ctx,r=compose_fixture(monkeypatch,'db97');pair,blocked=ordinary_pair(gray,r);i,j=pair['rows'];seen=[];operation=E.crop_mask
    def capture(shape,item,origin):
        m=operation(shape,item,origin);seen.append(m);return m
    monkeypatch.setattr(E,'crop_mask',capture)
    E.ocr_crop(gray,dict(polygon=[[0,0],[gray.shape[1],0],[gray.shape[1],gray.shape[0]],[0,gray.shape[0]]]),[r['items'][i],r['items'][j]],tmp_path/'real.png','final')
    assert (tmp_path/'real.png').exists()
    assert np.array_equal(seen[1],G.crop_mask(gray.shape,r['items'][i])) and np.array_equal(seen[2],G.crop_mask(gray.shape,r['items'][j]))


def test_restored_tight_R_export_fails_real_smoothness(monkeypatch):
    operation=R.corridor_hulls
    monkeypatch.setattr(R,'corridor_hulls',lambda *a,**kw:operation(*a,**dict(kw,smooth_exports=False)))
    with pytest.raises(AssertionError,match='tight per-letter'):test_committed_real_R_gain_and_native_members()


def test_historical_incomplete_owner_export_really_loses_six_ink_pixels():
    gray,items,ctx=fixture('phase35');case=next(q for q in json.loads((F/'final_bands_native.json').read_text())['cases'] if q['key']=='phase35');bad={r['row']:r for r in case['failure_export']};old=np.zeros(gray.shape,np.uint16);new=old.copy()
    for q in items:
        old+=G.crop_mask(gray.shape,q)
        r=bad.get(q['fixture_parent_index']);new+=G.crop_mask(gray.shape,r or q)
    loss=(old>0)&(new==0)&ctx['ink']
    assert int(loss.sum())==6,'source-bound historical dependency failure not reproduced'


def test_export_raster_is_independent_of_crop_origin():
    gray,items,ctx=fixture('phase35');case=next(q for q in json.loads((F/'final_bands_native.json').read_text())['cases'] if q['key']=='phase35')
    from ..shared.geometry import roi
    from ..shared.contracts import bbox
    for q in case['failure_export']:
        whole=G.crop_mask(gray.shape,q)
        a,b,c,d=roi(np.array(bbox(q))+[-1,-1,2,2],gray.shape)
        for pad in [0,1,4,11]:
            x,y,z,w=max(0,a-pad),max(0,b-pad),min(gray.shape[1],c+pad),min(gray.shape[0],d+pad)
            actual=G.crop_mask((w-y,z-x),q,(x,y))
            assert np.array_equal(actual,whole[y:w,x:z]),'crop/export phase changes half-open pixels'




def assert_complete_domains(gray,result):
    count=partition_counts(gray,result['items']);bands=result['final_bands']
    for pair in bands['pairs']:
        i,j=pair['rows'];a,c=pair['domain_x'];x=np.arange(a,c);y=np.arange(gray.shape[0])[:,None]
        up=np.polynomial.polynomial.polyval(np.clip(x,*bands['path_extents'][i]),bands['paths'][i]);down=np.polynomial.polynomial.polyval(np.clip(x,*bands['path_extents'][j]),bands['paths'][j]);domain=(y>=np.ceil(up))&(y<np.floor(down))
        assert np.all(count[:,a:c][domain]==1),'whole-column domain still has local legacy gap/overlap'


@pytest.mark.xfail(strict=True,reason='4959 same-row/mixed and interlock intervals remain legacy; complete right column is open')
def test_required_4959_whole_column_is_tiled(monkeypatch):
    gray,before,ctx,result=compose_fixture(monkeypatch,'r4959');assert_complete_domains(gray,result)


@pytest.mark.xfail(strict=True,reason='44b5 mixed/duplicate and interlock intervals remain legacy; complete ordinary column is open')
def test_required_44b5_whole_column_is_tiled(monkeypatch):
    gray,before,ctx,result=compose_fixture(monkeypatch,'p44b5');assert_complete_domains(gray,result)


def test_actual_final_kat_apostrophe_whole_and_unique(monkeypatch):
    from .test_whole_children import actual
    from ..shared import geometry_rows as B
    source,item,record,pieces,prepared=actual(3)
    yy,xx=np.nonzero(prepared['labels']==32);points=np.rint(np.asarray(B.to_page(np.c_[xx,yy],prepared['transform']))+[6,1853]-[7,58]).astype(int)
    gray,before,ctx,r=compose_fixture(monkeypatch,'p3229');row=next(i for i,q in enumerate(before) if q['fixture_parent_index']==15);m=G.crop_mask(gray.shape,r['items'][row])
    assert len(np.unique(points,axis=0))==59 and m[points[:,1],points[:,0]].all(),'mapped apostrophe clipped'
    count=partition_counts(gray,r['items']);assert np.all(count[points[:,1],points[:,0]]==1),'apostrophe has another final claimant'
    ink=cv2.GaussianBlur(gray,(3,3),.6)<prepared['threshold'];_,labels,stats,_=cv2.connectedComponentsWithStats(ink.astype(np.uint8),8)
    label=int(labels[points[0,1],points[0,0]]);component=labels==label
    assert stats[label,4]==60,'original-page component observation changed'
    assert np.all(m[component]>0) and np.all(count[component]==1),'whole original apostrophe must have one final owner'
    yy,xx=np.nonzero(prepared['labels']==1);fragment=np.rint(np.asarray(B.to_page(np.c_[xx,yy],prepared['transform']))+[6,1853]-[7,58]).astype(int)
    assert not m[fragment[:,1],fragment[:,0]].any(),'preceding zero-parent ) fragment restored'



def test_real_B_lower_row_keeps_all_57_selected_members(monkeypatch):
    from .test_whole_children import actual
    from ..shared import geometry_rows as B
    gray,item,record,pieces,prepared=actual(3);prepared['retain_support']=True
    polygons,receipt=B.whole_children(gray,item,record,pieces,prepared)
    assert len(receipt['admitted_components'][1])==57
    meta=json.loads((F/'final_B_native_context.json').read_text());pack=F/'final_B_native_context.npz'
    assert hashlib.sha256(pack.read_bytes()).hexdigest()==meta['pack_sha256'] and hashlib.sha256(gray.tobytes()).hexdigest()==meta['gray_sha256']
    z=np.load(pack);ctx=dict(image=gray,shape=gray.shape,height=meta['height'],paper_kernel=meta['kernel'],threshold=.08,scale=1,ink=z['ink'],strong=z['strong']);items=copy.deepcopy(meta['items']);i=next(i for i,q in enumerate(items) if q['fixture_parent_index']==2)
    items[i]['_selected_pixel_support']=prepared['whole_page_supports'][1]
    points=prepared['whole_page_supports'][1]['points'].copy();freeze_upstream(monkeypatch,gray,items,ctx)
    result=P.compose(gray,np.zeros((1,1),np.float32),items,None,use_final_export=True)
    assert G.crop_mask(gray.shape,result['items'][i])[points[:,1],points[:,0]].all(),'clean lower B support lost'


def test_paper_only_actual_final_call_reuses_source_motif_and_frame(monkeypatch):
    from ..shared import ink_ownership as source,type_residual_recovery as recovery,ink_frame_field as frame
    gray,items,ctx=decision_fixture();freeze_upstream(monkeypatch,gray,items,ctx);calls=dict(source=0,motif=0,frame=0)
    for module,name,key in [(source,'analyze','source'),(recovery,'candidate_motif','motif'),(P,'frame_exclude','frame')]:
        operation=getattr(module,name)
        def wrapper(*a,_op=operation,_key=key,**kw):calls[_key]+=1;return _op(*a,**kw)
        monkeypatch.setattr(module,name,wrapper)
    r=P.compose(gray,np.zeros((1,1),np.float32),items,None,use_final_export=True)
    assert not r['final_bands']['changed_content']
    assert calls==dict(source=0,motif=0,frame=1),'paper envelope reran content classifiers'
    assert any(not np.array_equal(G.crop_mask(gray.shape,a),G.crop_mask(gray.shape,b)) for a,b in zip(items,r['items']))


def test_bypassing_construction_restores_duplicate_kat_claim(monkeypatch):
    monkeypatch.setattr(P,'tessellate',lambda gray,items,**kw:dict(items=items,migrated=[],disabled=True,seconds=0.))
    with pytest.raises(AssertionError,match='another final claimant|one final owner'):
        test_actual_final_kat_apostrophe_whole_and_unique(monkeypatch)


@pytest.mark.parametrize('case',range(3))
def test_real_page_join_witnesses_close_without_pixel_waivers(monkeypatch,case):
    meta=json.loads((F/'final_join_native.json').read_text());pack=F/'final_join_native.npz'
    assert hashlib.sha256(pack.read_bytes()).hexdigest()==meta['pack_sha256'];m=meta['cases'][case];z=np.load(pack);gray=z[f'gray{case}']
    assert hashlib.sha256(gray.tobytes()).hexdigest()==m['gray_sha256']
    ctx=dict(image=gray,shape=gray.shape,height=m['height'],paper_kernel=m['kernel'],threshold=.08,scale=1,ink=z[f'ink{case}'],strong=z[f'strong{case}']);items=copy.deepcopy(m['items']);freeze_upstream(monkeypatch,gray,items,ctx)
    r=P.compose(gray,np.zeros((1,1),np.float32),items,None,use_final_export=True)
    whole_native(gray,items,r['items'],ctx)
    points=np.array(m['lost_original_points']);assert partition_counts(gray,r['items'])[points[:,1],points[:,0]].all(),'historical native loss restored'
