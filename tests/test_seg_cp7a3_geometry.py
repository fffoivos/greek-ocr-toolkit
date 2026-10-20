"""Preparation contracts; synthetic dry payloads never invoke a detector."""
import importlib.util
import json
from pathlib import Path
from tests._paths import ADMISSION
import subprocess
import sys
import pytest

HERE=ADMISSION / 'seg/cp7'
sys.path.insert(0,str(HERE))
import prepare_population_geometry as prep


def page(tmp_path, name='p'):
    source=tmp_path/(name+'.png');source.write_bytes(b'fixture')
    return dict(page_id=name,source=str(source.resolve()),source_sha256=prep.sha(source),frame=0,page_ids=[name])


def isolated(code):
    result=subprocess.run([sys.executable,'-B','-c',"import sys;sys.path.insert(0,"+repr(str(HERE))+");import prepare_population_geometry as p;"+code],capture_output=True,text=True)
    assert result.returncode==0, result.stderr


def test_two_page_dry_resume(tmp_path):
    pages=[page(tmp_path,'one'),page(tmp_path,'two')];out=tmp_path/'out'
    code=f"pages={pages!r};out={str(out)!r};assert p.run(pages,out,2,True,0)==0;assert p.run(pages,out,2,True,0)==0"
    isolated(code)
    progress=prep.read(out/'progress.json')
    assert progress['skipped']==2 and progress['prepared']==0 and progress['failures']==0
    assert all(prep.valid(out,p,True) for p in pages)
    assert all(prep.read(out/'cache'/p['page_id']/'preparation.json')['preparation_calls']==0 for p in pages)


def test_watchdog_submits_nothing(tmp_path):
    pages=[page(tmp_path)];out=tmp_path/'out'
    isolated(f"assert p.run({pages!r},{str(out)!r},1,True,10**30)==2")
    progress=prep.read(out/'progress.json')
    assert progress['stopped_disk'] and progress['completed']==0
    assert not (out/'cache').exists()


def test_skip_valid_never_calls_detector(tmp_path):
    item=page(tmp_path);out=tmp_path/'out'
    isolated(f"item={item!r};out={str(out)!r};assert p.prepare_one(out,item,True)['status']=='prepared';p.io_module=lambda:1/0;assert p.prepare_one(out,item,True)['status']=='skip_valid'")


@pytest.mark.parametrize('mutation',['payload','source','identity','missing'])
def test_invalid_is_not_skipped_or_redetected(tmp_path,mutation):
    item=page(tmp_path);out=tmp_path/'out'
    isolated(f"assert p.prepare_one({str(out)!r},{item!r},True)['status']=='prepared'")
    directory=out/'cache'/'p'
    if mutation=='payload':(directory/'dry_payload.json').write_bytes(b'changed')
    if mutation=='source':Path(item['source']).write_bytes(b'changed')
    if mutation=='identity':
        r=prep.read(directory/'preparation.json');r['identity']['frame']=4
        (directory/'preparation.json').write_text(json.dumps(r))
    if mutation=='missing':(directory/'dry_payload.json').unlink()
    assert not prep.valid(out,item,True)
    isolated(f"assert p.prepare_one({str(out)!r},{item!r},True)['status']=='failed'")


def test_dry_cache_is_never_real_geometry(tmp_path):
    item=page(tmp_path);out=tmp_path/'out'
    isolated(f"assert p.prepare_one({str(out)!r},{item!r},True)['status']=='prepared'")
    assert not prep.valid(out,item,False)


def test_aliases_prepared_once(tmp_path):
    item=page(tmp_path)
    records=[dict(id=pid+'-l001',crop_source_image=item['source'],crop_source_sha256=item['source_sha256']) for pid in ['a','b']]
    result=prep.page_manifest(records)
    assert len(result)==1 and result[0]['page_ids']==['a','b']


def test_network_and_live_writes_forbidden(tmp_path):
    out=tmp_path/'out';out.mkdir()
    isolated(f"p.guard({str(out)!r});import socket\ntry: socket.socket(); raise RuntimeError('network allowed')\nexcept AssertionError: pass\ntry: open({str(tmp_path/'forbidden')!r},'w'); raise RuntimeError('write allowed')\nexcept AssertionError: pass")


def test_watchdog_boundary(monkeypatch,tmp_path):
    from types import SimpleNamespace
    monkeypatch.setattr(prep.shutil,'disk_usage',lambda path:SimpleNamespace(free=10_000_000_000))
    assert prep.enough_disk(tmp_path)
    monkeypatch.setattr(prep.shutil,'disk_usage',lambda path:SimpleNamespace(free=9_999_999_999))
    assert not prep.enough_disk(tmp_path)


def test_launcher_is_detached_nice_and_not_reader():
    text=(HERE/'launch_population_geometry.sh').read_text()
    assert 'nohup bash -c' in text and '/usr/bin/nice -n 10' in text
    assert 'population.pid' in text and 'prepare_population_geometry.py' in text
    assert 'run_bed' not in text and 'launch_cp7.sh' not in text
