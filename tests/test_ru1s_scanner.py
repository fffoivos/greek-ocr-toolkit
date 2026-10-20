"""Scanner regressions discovered while validating the existing RU1 r2 runs."""
import io
import json
import sys
from pathlib import Path
import pytest
from PIL import Image, PngImagePlugin
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/secondary/reading'))
import scan_rollout as scanner


def png(mode='L', changed=False, metadata=False):
    im=Image.new(mode,(24,12),128 if mode=='L' else (128,128,128,255))
    if changed:im.putpixel((0,0),127 if mode=='L' else (128,128,128,254))
    b=io.BytesIO();meta=PngImagePlugin.PngInfo()
    if metadata:meta.add_text('timestamp','changed')
    im.save(b,format='PNG',pnginfo=meta);return b.getvalue(),im.convert('RGB')


@pytest.mark.parametrize('mode',['L','RGBA'])
def test_exact_reencoded_png(mode):
    original,im=png(mode);observed,_=png(mode,metadata=True)
    assert original!=observed
    assert scanner.match_image(observed,[('zoom/panel.png',original,im)])['match']=='pixels'


@pytest.mark.parametrize('mode',['L','RGBA'])
def test_pixel_or_alpha_difference_fails(mode):
    original,im=png(mode);changed,_=png(mode,changed=True)
    assert scanner.match_image(changed,[('zoom/panel.png',original,im)]) is None


def test_mode_difference_fails():
    original,im=png();changed,_=png('RGBA')
    assert scanner.match_image(changed,[('zoom/panel.png',original,im)]) is None


@pytest.mark.parametrize('code,ok',[
    ('for(let i=1;i<=6;i++) {image((await tools.view_image({path:`${(await tools.exec_command({cmd:"pwd",max_output_tokens:100})).output.trim()}/zoom/${String(i).padStart(3,\'0\')}.png`})).image_url)}',True),
    ('text(await tools.exec_command({cmd:"x=w*(j+1)//4"}))',True),
    ('text(await tools.exec_command({cmd:"cat /etc/passwd"}))',False),
    ('image((await tools.view_image({path:`${(await tools.exec_command({cmd:"pwd",max_output_tokens:100})).output.trim()}/../keys.json`})).image_url)',False),
])
def test_paths_keep_fail_closed(tmp_path,code,ok):
    rd=tmp_path/'r2';(rd/'crops').mkdir(parents=True)
    original,_=png();(rd/'crops/source.png').write_bytes(original)
    (rd/'items.jsonl').write_text('{}\n')
    (tmp_path/'MANIFEST.r2.json').write_text(json.dumps(dict(files={p:scanner.sha(rd/p) for p in ['items.jsonl','crops/source.png']})))
    rollout=tmp_path/'rollout.jsonl'
    records=[dict(payload=dict(type='custom_tool_call',name='exec',input=code))]
    if scanner.PWD in code:
        # Canonical v4.4 requires the recorded pwd output, not just its expression.
        records.append(dict(payload=dict(item=dict(type='CommandExecution',command=['pwd'],stdout=str(rd),exit_code=0))))
    rollout.write_text(''.join(json.dumps(r)+'\n' for r in records))
    result=scanner.inspect(rollout,rd)
    assert result['ok']==ok,result['violations']
