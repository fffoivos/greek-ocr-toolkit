"""Image tests: run with x86 Python -B -s (system SciPy), never default arm64."""
import sys
from pathlib import Path
import json
import pytest
from PIL import Image,ImageDraw,PngImagePlugin
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/numerics'))
from n1_render import render
from n1_build_packs import build,MEANINGS,rows
from n1_pack_closure import scan
from greekocr.numerics.locks import Locks


def fixture(tmp_path):
    im=Image.new('RGB',(100,40),'white');d=ImageDraw.Draw(im)
    d.rectangle([20,10,30,29],fill='black');d.rectangle([45,10,55,29],fill='black')
    metadata=PngImagePlugin.PngInfo();metadata.add_text('source_id','private')
    source=tmp_path/'source.png';im.save(source,pnginfo=metadata)
    geom=dict(geom_status='ok',gap_center=37.5,gap=[31,45],gap_width=14,digit_height=20,digit_top=10,baseline=30,zoom_bbox=[14,4,62,36])
    result=render(source,geom,tmp_path/'rendered')
    records={f's{i}':dict(result,geometry=geom,slot_id=f's{i}',line_id=f'line{i}',google_glyph='.',geometry_record_ref='fixture') for i in range(36)}
    return source,result,records


def test_triangles_never_cover_ink(tmp_path):
    source,result,_=fixture(tmp_path)
    with Image.open(source) as original,Image.open(result['line']) as line:
        assert line.crop((0,12,100,52)).tobytes()==original.convert('RGB').tobytes()
        assert line.getpixel((38,2))==(128,128,128)
    with Image.open(source) as original, Image.open(result['zoom']) as zoom:
        expected=original.convert('RGB').crop((14,4,62,36)).resize((144,96),Image.Resampling.LANCZOS)
        assert zoom.size==(144,120)
        assert zoom.crop((0,12,144,108)).tobytes()==expected.tobytes()
        assert zoom.getpixel((70,2))==(128,128,128)
        assert zoom.getpixel((70,117))==(128,128,128)
        assert all(zoom.getpixel((x,y)) in [(255,255,255),(128,128,128)]
                   for y in list(range(12))+list(range(108,120)) for x in range(144))


@pytest.mark.parametrize('bbox,center',[([-8,-5,62,45],0),([14,-5,108,45],99)])
def test_zoom_boundary_padding_and_marker_alignment(tmp_path,bbox,center):
    source,_,records=fixture(tmp_path)
    geom=dict(records['s0']['geometry'],zoom_bbox=bbox,gap_center=center)
    result=render(source,geom,tmp_path/'boundary')
    with Image.open(source) as original,Image.open(result['zoom']) as marked:
        padded=Image.new('RGB',(bbox[2]-bbox[0],bbox[3]-bbox[1]),'white')
        padded.paste(original.convert('RGB'),(-bbox[0],-bbox[1]))
        expected=padded.resize((padded.width*3,padded.height*3),Image.Resampling.LANCZOS)
        assert marked.crop((0,12,expected.width,12+expected.height)).tobytes()==expected.tobytes()
        x=round((center-bbox[0])*3)
        assert marked.getpixel((x,8))==(128,128,128)
        assert marked.getpixel((x,12+expected.height+3))==(128,128,128)


def test_fixture_30_closure(tmp_path):
    _,_,records=fixture(tmp_path)
    bed=[dict(slot_id=f's{i}') for i in range(30)]
    controls=[dict(slot_id=f's{i}',truth='comma') for i in range(30,36)]
    locks=Locks(frozenset(),frozenset(),frozenset())
    result=build(bed,controls,records,tmp_path/'packs',tmp_path/'private',locks)
    assert result[0]['closure']['ok'];assert result[0]['items']==33
    directory=tmp_path/'packs/ctx01/r1'
    public=rows(directory/'items.jsonl')
    assert all(set(r)=={'item_id','line','zoom','options'} and set(r['options'].values())==set(MEANINGS) for r in public)
    assert all(not p.is_symlink() for p in directory.rglob('*'))
    for p in (directory/'img').glob('*.png'):
        with Image.open(p) as im:assert not im.info
    assert (directory.parent/'MANIFEST.r1.json').is_file()
    (directory/'leak.txt').write_text('private')
    assert not scan(directory,tmp_path/'private')['ok']


def test_calibration(tmp_path):
    _,_,records=fixture(tmp_path)
    controls=[dict(slot_id=f's{i}',truth='comma') for i in range(30,36)]
    result=build([],controls,records,tmp_path/'cal',tmp_path/'private',Locks(frozenset(),frozenset(),frozenset()),True)
    assert len(result)==1;assert result[0]['items']==result[0]['controls']==6;assert result[0]['closure']['ok']


def test_reserved_builder_refuses(tmp_path):
    _,_,records=fixture(tmp_path)
    with pytest.raises(ValueError,match='reserved'):
        build([], [dict(slot_id='s30',truth='comma')], records,tmp_path/'packs',tmp_path/'private',Locks(frozenset(),frozenset({'line30'}),frozenset()),True)


def test_hash_mismatch_no_substitute(tmp_path,monkeypatch):
    import n1_render
    monkeypatch.setattr(n1_render,'SCRATCH',tmp_path)
    source=tmp_path/'page.png';Image.new('L',(30,30),255).save(source)
    import hashlib
    row=dict(crop='/read-only/run/crop.png',crop_sha256='0'*64,crop_source_image=str(source),
             crop_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),crop_bbox=[0,0,20,20])
    with pytest.raises(ValueError,match='regenerated crop hash mismatch'):n1_render.cached_crop(row)
    assert row['crop']=='/read-only/run/crop.png'
    assert not (tmp_path/'n1_cache/crops'/('0'*64+'.png')).exists()


def test_missing_render_refused(tmp_path):
    _,_,records=fixture(tmp_path);records['s30']['zoom']=None
    with pytest.raises(ValueError,match='unrenderable'):
        build([], [dict(slot_id='s30',truth='comma')], records,tmp_path/'packs',tmp_path/'private',Locks(frozenset(),frozenset(),frozenset()),True)
