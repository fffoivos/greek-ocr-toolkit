"""Post-reader custody checks on synthetic packs; no reading or network."""
import importlib.util
import json
import sys
from pathlib import Path
from tests._paths import ADMISSION, relocated

import pytest

BASE=ADMISSION / 'seg/cp7'
sys.path.insert(0,str(BASE))
import runtime_r2 as r2

@pytest.fixture(autouse=True)
def receipt_locations(monkeypatch):
    # Preserve hash values; translate only repository-relative receipt names
    # to compare the same suffix under CLEAN4L's additional records directory.
    read = r2.read
    def located(path):
        value = read(path)
        if path == r2.AMENDMENT:
            value = dict(value, path=str(relocated(value['path'])))
        if path == r2.FREEZE:
            value = dict(value, files={str(relocated(p)): h for p, h in value['files'].items()})
        return value
    monkeypatch.setattr(r2, 'read', located)

@pytest.fixture
def pack(tmp_path):
    originals={'cards.jsonl':b'{"fixture": true}\n','crops/fixture.png':b'fixture crop bytes'}
    for name,data in originals.items():
        p=tmp_path/name;p.parent.mkdir(exist_ok=True);p.write_bytes(data)
    return tmp_path,{name:r2.sha(tmp_path/name) for name in originals}


def test_originals_unchanged(pack):
    directory,expected=pack
    assert r2.post_read_closure(directory,expected)==expected


def test_reader_outputs_allowed(pack):
    directory,expected=pack
    (directory/'answers.jsonl').write_text('{}\n')
    (directory/'zoom/nested').mkdir(parents=True)
    (directory/'zoom/nested/view.png').write_bytes(b'zoom')
    assert r2.post_read_closure(directory,expected)==expected


@pytest.mark.parametrize('name',['cards.jsonl','crops/fixture.png'])
def test_changed_original_fails(pack,name):
    directory,expected=pack
    with (directory/name).open('ab') as f:f.write(b'changed')
    with pytest.raises(AssertionError,match='original changed'):
        r2.post_read_closure(directory,expected)


@pytest.mark.parametrize('name',['cards.jsonl','crops/fixture.png'])
def test_missing_original_fails(pack,name):
    directory,expected=pack;(directory/name).unlink()
    with pytest.raises(AssertionError):r2.post_read_closure(directory,expected)


@pytest.mark.parametrize('name',['unexpected.txt','crops/extra.png','zoomish/view.png'])
def test_unallowed_output_fails(pack,name):
    directory,expected=pack
    p=directory/name;p.parent.mkdir(exist_ok=True);p.write_text('extra')
    with pytest.raises(AssertionError,match='unallowed'):
        r2.post_read_closure(directory,expected)


def test_unallowed_empty_directory_fails(pack):
    directory,expected=pack;(directory/'extra').mkdir()
    with pytest.raises(AssertionError,match='unallowed directory'):
        r2.post_read_closure(directory,expected)


def test_symlink_output_fails(pack):
    directory,expected=pack;(directory/'zoom').symlink_to(directory/'crops',target_is_directory=True)
    with pytest.raises(AssertionError,match='symlink'):
        r2.post_read_closure(directory,expected)


def test_hardlink_output_fails(pack):
    import os
    directory,expected=pack
    (directory/'zoom').mkdir();os.link(directory/'crops/fixture.png',directory/'zoom/copy.png')
    with pytest.raises(AssertionError,match='hardlink'):
        r2.post_read_closure(directory,expected)


def test_manifest_cannot_replace_recorded_closure(pack,monkeypatch):
    directory,expected=pack
    root=directory/'packs';bed='segcp7r2_b'
    (root/bed/'r1').mkdir(parents=True)
    (root/bed/'MANIFEST.r1.json').write_text(json.dumps({'files':{}}))
    (directory/'pack_closure.json').write_text(json.dumps({'contexts':[dict(bed=bed,reader='r1',files=expected)]}))
    monkeypatch.setattr(r2,'R2',directory);monkeypatch.setattr(r2,'PACK_ROOT',root)
    with pytest.raises(AssertionError):r2.verify_packs([bed])


def test_pre_read_still_calls_strict_closure(pack,monkeypatch):
    directory,expected=pack;bed='segcp7r2_b'
    (directory/'keys').mkdir()
    (directory/'keys'/f'{bed}.json').write_text(json.dumps({'readers':{'r1':[]}}))
    (directory/'pack_closure.json').write_text(json.dumps({'contexts':[dict(bed=bed,reader='r1',files=expected)]}))
    (directory/bed).mkdir()
    (directory/bed/'MANIFEST.r1.json').write_text(json.dumps({'files':expected}))
    monkeypatch.setattr(r2,'R2',directory);monkeypatch.setattr(r2,'PACK_ROOT',directory)
    def strict(*args):raise AssertionError('strict pre-read closure called')
    monkeypatch.setattr(r2,'closure',strict)
    with pytest.raises(AssertionError,match='strict pre-read closure called'):
        r2.verify_packs([bed],pre_read=True)


def test_only_runtime_freeze_exception(monkeypatch):
    amendment=r2.read(r2.AMENDMENT)
    original=r2.r2_common.sha
    def verify():
        assert r2.r2_common.sha(Path(r2.__file__))==amendment['original_sha256']
        assert r2.r2_common.sha(BASE/'common.py')==original(BASE/'common.py')
    monkeypatch.setattr(r2,'verify',verify)
    r2.verify_runtime_freeze()
    assert r2.r2_common.sha is original


def test_amendment_drift_fails(monkeypatch):
    read=r2.read
    def altered(path):
        result=read(path)
        if path==r2.AMENDMENT:result['amended_sha256']='0'*64
        return result
    monkeypatch.setattr(r2,'read',altered)
    with pytest.raises(AssertionError,match='runtime amendment drift'):
        r2.verify_runtime_freeze()


def test_b_launcher_prepared_only():
    text=(BASE/'launch_cp7_r2_b.sh').read_text()
    assert 'segcp7r2_a' not in text and 'Refuse rerun' in text
    assert 'pre-read segcp7r2_b' in text
    assert 'run_bed.sh" segcp7r2_b r1' in text


@pytest.mark.parametrize('reader_outputs',[False,True])
def test_original_pre_read_closure_remains_strict(tmp_path,reader_outputs):
    from PIL import Image
    import cp7_common as common
    (tmp_path/'crops').mkdir()
    image=tmp_path/'crops/temp.png'
    Image.new('RGB',(1,1),'white').save(image)
    digest=r2.sha(image);image.rename(tmp_path/'crops'/f'{digest}.png')
    ids=[f'k{i:010x}' for i in range(55)]
    cards=[dict(card_id=card_id,crop=f'crops/{digest}.png',google_text='',word_scripts=[]) for card_id in ids]
    (tmp_path/'cards.jsonl').write_text(''.join(json.dumps(card)+'\n' for card in cards))
    if reader_outputs:
        (tmp_path/'answers.jsonl').write_text('{}\n')
        (tmp_path/'zoom').mkdir();(tmp_path/'zoom/view.png').write_bytes(b'zoom')
        with pytest.raises(AssertionError):common.closure(tmp_path,ids)
    else:
        assert set(common.closure(tmp_path,ids))=={'cards.jsonl',f'crops/{digest}.png'}
