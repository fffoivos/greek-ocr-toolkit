import json
import os
import subprocess
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/secondary/reading'))
from ru1_map_answers import map_records
W=Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('args,stem,reader', [([], 'ctx01','r1'),(['r1'],'ctx01','r1'),(['r2'],'ctx01.r2','r2')])
def test_launcher_paths(args,stem,reader):
    p=subprocess.run(['bash',str(W/'scripts/secondary/reading/run_bed.sh'),'ctx01',*args],env=dict(os.environ,RU1_DRY_RUN='1'),capture_output=True,text=True,check=True)
    out=dict(l.split('=',1) for l in p.stdout.splitlines())
    for k,suffix in [('answers','.jsonl'),('scan','.scan.json'),('mapped','.mapped.jsonl'),('controls','.controls.json')]:
        assert out[k]==str(W/f'artifacts/ru1/answers/{stem}{suffix}')
    assert out['key']==str(W/f'artifacts/ru1/keys/{stem}.json')
    assert out['pack'].endswith('/ctx01/'+reader)


def test_reader_argument_rejected():
    p=subprocess.run(['bash',str(W/'scripts/secondary/reading/run_bed.sh'),'ctx01','r4'],capture_output=True)
    assert p.returncode==64


def test_r2_mapper():
    iid='k0000000001';item=dict(item_id=iid,slots=1)
    key=dict(context='ctx01',readers={'r2':[iid]},items={iid:dict(row_id='row',source_id='row',control=False,slots=[dict(offset=1,google='ь',kind='final',prior='unknown')])})
    ans=dict(item_id=iid,slots={'1':'ъ'},confidence={'1':'high'},unmarked_final_hard_signs=[],pre1918='yes',note='')
    m,s=map_records([ans],key,[item],reader='r2');assert m[0]['call']=='ъ' and s['status']=='VALID'


def test_reverse_closure_and_fresh_ids(tmp_path,monkeypatch):
    from PIL import Image
    import scan_packs
    from common import sha
    root=tmp_path/'keys';root.mkdir();monkeypatch.setattr(scan_packs,'ROOT',tmp_path)
    ctx=tmp_path/'ctx01';sources={}
    for reader in ['r1','r2']:
        dest=ctx/reader;(dest/'crops').mkdir(parents=True)
        im=Image.new('RGB',(10,10),'white');temp=dest/'crops/temp.png';im.save(temp);h=sha(temp);temp.rename(dest/f'crops/{h}.png')
        ids=['k0000000001','k0000000002'] if reader=='r1' else ['k0000000004','k0000000003']
        texts=['а⟦1⟧','б⟦1⟧'] if reader=='r1' else ['б⟦1⟧','а⟦1⟧']
        items=[dict(item_id=i,crop=f'crops/{h}.png',masked_text=t,slots=1) for i,t in zip(ids,texts)]
        (dest/'items.jsonl').write_text(''.join(json.dumps(i,ensure_ascii=False)+'\n' for i in items))
        key=dict(readers={reader:ids},items={i:dict(source_id='private-source') for i in ids})
        (root/('ctx01'+('.r2' if reader=='r2' else '')+'.json')).write_text(json.dumps(key))
    assert all(scan_packs.scan(ctx/r,'yer')['ok'] for r in ['r1','r2'])
    path=ctx/'r2/items.jsonl';items=[json.loads(l) for l in path.read_text().splitlines()];items[0]['masked_text']='в⟦1⟧'
    path.write_text(''.join(json.dumps(i,ensure_ascii=False)+'\n' for i in items))
    result=scan_packs.scan(ctx/'r2','yer');assert not result['ok'] and 'reader content is not exact reverse' in result['violations']
