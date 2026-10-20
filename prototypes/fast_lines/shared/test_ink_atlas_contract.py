"""Native score identity through the atlas factory and the actual B5 consumer."""
from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np
import pytest
from . import ink_ownership as own
from .ink_photometry import GlyphAtlas, GlyphExemplar, glyph_atlas, glyphs, match_glyphs


def native():
    root=Path(__file__).with_name('fixtures')
    meta=json.loads((root/'ink_atlas_native.json').read_text())
    path=root/'ink_atlas_native.png'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['png_sha256']
    gray=cv2.imread(str(path),0);gray.flags.writeable=False
    return gray,meta


def asymmetric():
    gray,meta=native();box=meta['items'][0]['polygon']
    gs=glyphs(gray,[*box[0],*box[2]],meta['height'])
    chosen=[next(g for g in gs if g['bbox']==b) for b in meta['asymmetric_bboxes']]
    for i,g in enumerate(chosen):g['line']=i+17
    return chosen


def test_native_order_replacement_and_owned_metadata():
    raw=asymmetric();query=[dict(g,vector=g['vector'].copy(),bbox=g['bbox'][:]) for g in raw]
    atlas=glyph_atlas(raw);expected=match_glyphs(query,atlas)
    assert [m['direct_id'] for m in expected]==[0,1]
    assert all(m['direct']>.999 and m['margin']<-.2 for m in expected)
    boxes=[tuple(g['bbox']) for g in raw]
    raw[:]=raw[::-1]
    reordered=glyph_atlas(raw)
    assert [m['direct_id'] for m in match_glyphs(query,reordered)]==[1,0]
    assert match_glyphs(query,atlas)==expected
    raw[:]=[dict(query[1],vector=query[1]['vector'].copy(),line=99,bbox=[9,9,19,19]),dict(query[0],vector=query[0]['vector'].copy(),line=98,bbox=[20,20,30,30])]
    assert match_glyphs(query,atlas)==expected
    replacement=glyph_atlas(raw)
    assert replacement.exemplars[0].bbox==(9,9,19,19)
    for g in raw:g['vector'][:]=0;g['aspect']=100;g['bbox'][:]=[0]*4;g['line']=-1
    assert match_glyphs(query,atlas)==expected
    assert [e.bbox for e in atlas.exemplars]==boxes
    assert [e.line for e in atlas.exemplars]==[17,18]
    assert replacement.exemplars[0].line==99
    fresh=glyph_atlas(raw)
    assert np.all(fresh.vectors==0) and np.all(fresh.aspects==100)
    assert not np.shares_memory(atlas.vectors,query[0]['vector'])
    with pytest.raises(ValueError):atlas.vectors[0,0]=0
    with pytest.raises(ValueError):atlas.aspects[0]=0
    with pytest.raises(FrozenInstanceError):atlas.exemplars=()
    with pytest.raises(TypeError):match_glyphs(query,atlas,prepared=(atlas.vectors,atlas.aspects))


def test_native_duplicate_symmetric_ties_reflection_and_empty():
    raw=asymmetric();g=raw[0]
    atlas=glyph_atlas([g,dict(g,bbox=[90,91,92,93],line=90)])
    mirror=dict(g,vector=g['vector'].reshape(22,22)[:,::-1].ravel().copy())
    scores=match_glyphs([mirror,g],atlas)
    assert scores[0]['reflected_id']==scores[1]['direct_id']==0
    assert scores[0]['reflected']>.999 and scores[0]['margin']>.2
    symmetric=(g['vector'].reshape(22,22)+g['vector'].reshape(22,22)[:,::-1])/2
    symmetric=symmetric.ravel()/np.linalg.norm(symmetric)
    s=dict(g,vector=symmetric)
    tied=match_glyphs([s],glyph_atlas([s,dict(s,bbox=[99]*4)]))[0]
    assert tied['direct_id']==tied['reflected_id']==0 and tied['margin']==0
    assert match_glyphs([],atlas)==match_glyphs([g],glyph_atlas([]))==[]


@pytest.mark.parametrize('empty',[False,True])
def test_atlas_sealed_parts_dtypes_and_readonly_views(empty):
    raw=[] if empty else asymmetric();atlas=glyph_atlas(raw)
    assert atlas.vectors.dtype==np.float32 and atlas.aspects.dtype==np.float64
    assert atlas.vectors.shape==((0,) if empty else (2,484))
    assert atlas.aspects.shape==((0,) if empty else (2,))
    for array in [atlas.vectors,atlas.aspects]:
        assert not array.flags.owndata and not array.base.flags.writeable
        with pytest.raises(ValueError):array.setflags(write=True)
    # Ordinary assembly/replacement cannot detach metadata from scored arrays,
    # even with compatible lengths or the current empty representation.
    with pytest.raises(TypeError):GlyphAtlas(atlas.vectors,atlas.aspects,atlas.exemplars)
    with pytest.raises(TypeError):replace(atlas,exemplars=atlas.exemplars[::-1])
    with pytest.raises(TypeError):replace(atlas,vectors=np.zeros((3,484),np.float32))
    with pytest.raises(TypeError):replace(atlas,exemplars=(GlyphExemplar((7,7,8,8),99),)*len(atlas))
    for query in [[],raw]:
        with pytest.raises(TypeError):match_glyphs(query,[])
        with pytest.raises(TypeError):match_glyphs(query,raw)


@pytest.mark.parametrize('field,value',[('vector',np.zeros(483)),('vector',np.zeros((22,22))),
    ('aspect',[1.]),('bbox',[1,2,3]),('bbox',[[],2,3,4]),('line',[])])
def test_factory_rejects_structurally_invalid_census(field,value):
    raw=asymmetric()
    for g in raw:g[field]=value
    with pytest.raises(ValueError):glyph_atlas(raw)


def test_dtype_conversion_and_reopen_attempt_at_native_detail_consumer(monkeypatch):
    raw=asymmetric()
    for g in raw:
        g['vector']=g['vector'].astype(np.float64)
        g['aspect']=np.float32(g['aspect'])
    atlas=glyph_atlas(raw)
    assert atlas.vectors.dtype==np.float32 and atlas.aspects.dtype==np.float64
    assert atlas.aspects[0]==float(raw[0]['aspect'])
    gray,meta=native();factory=own.glyph_atlas;observations=[]
    def prepare(gs):
        snapshot=factory(gs);observations.append(snapshot)
        for array in [snapshot.vectors,snapshot.aspects]:
            with pytest.raises(ValueError):array.setflags(write=True)
        with pytest.raises(TypeError):replace(snapshot,exemplars=snapshot.exemplars[::-1])
        return snapshot
    monkeypatch.setattr(own,'glyph_atlas',prepare)
    result=own.analyze(gray,meta['items'],regions=meta['regions'],height=meta['height'],detail=True)
    result.pop('seconds');result.pop('scout_s')
    assert result==meta['expected_legacy'] and len(observations)==1
    for row in result['regions']:
        for witness in row['witnesses']:
            i=witness['reflected_id'] if witness['margin']>0 else witness['direct_id']
            assert witness['exemplar']==list(observations[0].exemplars[i].bbox)


@pytest.mark.parametrize('mutation',['none','replace','reorder','vector_aspect','bbox_line','clear'])
def test_b5_native_witnesses_use_the_scored_snapshot(monkeypatch,mutation):
    gray,meta=native();factory=own.glyph_atlas;matcher=own.match_glyphs
    observations=[];requests=[]
    def prepare(raw):
        before=[(tuple(g['bbox']),g['line']) for g in raw]
        snapshot=factory(raw);observations.append(snapshot)
        assert [(e.bbox,e.line) for e in snapshot.exemplars]==before
        if mutation=='replace':raw[:]=[dict(g,vector=np.zeros(484),bbox=[7]*4,line=999) for g in raw]
        elif mutation=='reorder':raw.reverse()
        elif mutation=='vector_aspect':
            for g in raw:g['vector'][:]=0;g['aspect']=100
        elif mutation=='bbox_line':
            for g in raw:g['bbox'][:]=[7]*4;g['line']=999
        elif mutation=='clear':raw.clear()
        return snapshot
    def match(query,atlas):
        assert atlas is observations[0]
        result=matcher(query,atlas);requests.append(result);return result
    monkeypatch.setattr(own,'glyph_atlas',prepare);monkeypatch.setattr(own,'match_glyphs',match)
    result=own.analyze(gray,meta['items'],regions=meta['regions'],height=meta['height'],detail=True)
    result.pop('seconds');result.pop('scout_s')
    # Frozen by the independent pre-refactor consumer on these exact native ROIs.
    assert result==meta['expected_legacy']
    assert len(observations)==1 and len(requests)==3
    assert sum(len(r['witnesses']) for r in result['regions'])==13
    for row in result['regions']:
        for witness in row['witnesses']:
            i=witness['reflected_id'] if witness['margin']>0 else witness['direct_id']
            assert witness['exemplar']==list(observations[0].exemplars[i].bbox)


def test_b5_builds_once_for_multiple_requested_regions_and_refreshes(monkeypatch):
    gray,meta=native();factory=own.glyph_atlas;observations=[]
    def prepare(raw):
        snapshot=factory(raw);observations.append(snapshot);return snapshot
    monkeypatch.setattr(own,'glyph_atlas',prepare)
    a=own.analyze(gray,meta['items'],regions=meta['regions']*2,height=meta['height'],detail=True)
    assert len(observations)==1 and len(a['regions'])==6
    b=own.analyze(gray,meta['items'][::-1],regions=meta['regions'],height=meta['height'],detail=True)
    assert len(observations)==2 and observations[0] is not observations[1]
    before={e.bbox:e.line for e in observations[0].exemplars}
    after={e.bbox:e.line for e in observations[1].exemplars}
    assert before.keys()==after.keys() and all(before[b]!=after[b] for b in before)
    empty=own.analyze(gray,[],regions=[],height=meta['height'],detail=True)
    assert empty['regions']==[] and empty['atlas_glyphs']==0 and len(observations)==2
