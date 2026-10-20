"""Offline actual-magick witnesses; invoke the pinned canonical scanner in place.
A third, unviewed overwrite forces BOTH earlier views through reconstruction.
No scanner imports, patches, substitute image commands, or Codex calls.
"""
import base64,json,shutil,subprocess,os,tempfile
from ss4_common import *
from run_type import PILLOW
DEST=SS/'q3/replay_fixture'

def call(name,args,cid):
    return dict(payload=dict(type='function_call',name=name,call_id=cid,arguments=json.dumps(args)))

def run():
    check_scanner(); DEST.mkdir(parents=True,exist_ok=True)
    # This ImageMagick install has no font registry. Resolve the literal font
    # name for fixture generation only; do not change scanner/replay environment.
    fontconfig=DEST/'fontconfig'; fontconfig.mkdir(exist_ok=True)
    (fontconfig/'type.xml').write_text('<typemap><type name="Helvetica" fullname="Helvetica" family="Helvetica" glyphs="/System/Library/Fonts/Helvetica.ttc"/></typemap>')
    env=dict(os.environ,MAGICK_CONFIGURE_PATH=str(fontconfig))
    source=PACK_ROOT/'type2/t01/r1' 
    pics=[r['crop'] for r in rows(source/'items.jsonl')[:3]]
    results={}
    for case in ('literal_overwrite','pwd_overwrite','absolute_font_overwrite'):
        reader=PACK_ROOT/'type2_fixture_v3'/case/'r1'
        if reader.exists(): raise ValueError('refuse overwrite of fixture')
        shutil.copytree(source,reader)
        shutil.copyfile(source.parent/'MANIFEST.r1.json',reader.parent/'MANIFEST.r1.json')
        records=[]
        records.append(call('exec_command',dict(cmd='mkdir -p zoom'),'mkdir'))
        (reader/'zoom').mkdir()
        for i,operands in enumerate((pics[:2],pics[1:],pics[::2])):
            cmd='magick montage -font Helvetica '+' '.join(operands)+' -geometry +0+0 -tile 1x zoom/g01.png'
            if case=='pwd_overwrite':
                cmd=cmd.replace('img/','"$(pwd)/img/').replace('.png ','.png" ',len(operands))
            if case=='absolute_font_overwrite':
                cmd=cmd.replace('-font Helvetica','-font /System/Library/Fonts/Helvetica.ttc')
            records.append(call('exec_command',dict(cmd=cmd),f'm{i}'))
            proc=subprocess.run(cmd,shell=True,cwd=reader,capture_output=True,text=True,env=env)
            records.append(dict(payload=dict(type='function_call_output',call_id=f'm{i}',output=dict(exit_code=proc.returncode,stdout=proc.stdout,stderr=proc.stderr))))
            if proc.returncode: raise ValueError('fixture command failed: '+proc.stderr)
            if i<2:
                records.append(call('view_image',dict(path='zoom/g01.png'),f'v{i}'))
                blob=(reader/'zoom/g01.png').read_bytes()
                records.append(dict(payload=dict(type='function_call_output',call_id=f'v{i}',output=[dict(type='input_image',image_url='data:image/png;base64,'+base64.b64encode(blob).decode())])))
        rollout=DEST/f'{case}.rollout.jsonl'; jsonl(rollout,records)
        check_scanner()
        proc=subprocess.run(PILLOW+[str(SCANNER),str(rollout),str(reader)],capture_output=True,text=True)
        (DEST/f'{case}.scan.json').write_text(proc.stdout)
        (DEST/f'{case}.stderr.txt').write_text(proc.stderr)
        scan=json.loads(proc.stdout)
        results[case]=dict(returncode=proc.returncode,ok=scan['ok'],image_match_counts=scan['image_match_counts'],violations=scan['violations'],original_files=[r.get('original_files') for r in scan['reproductions']],replay_errors=[r.get('error') for r in scan['reproductions']],rollout=str(rollout),scan=str(DEST/f'{case}.scan.json'),reader=str(reader))
    positive=results['literal_overwrite']
    passed=positive['ok'] and sum(v for k,v in positive['image_match_counts'].items() if k.startswith('reproduced'))==2 and all(not results[c]['ok'] for c in ('pwd_overwrite','absolute_font_overwrite'))
    result=dict(status='PASS' if passed else 'FAIL',scanner=str(SCANNER),scanner_sha256=sha(SCANNER),cases=results,note='Third unviewed overwrite ensures neither recorded view matches the final zoom; both require historical reconstruction.')
    dump(DEST/'RESULT.json',result); print(json.dumps(result,indent=2)); return passed
if __name__=='__main__': sys.exit(0 if run() else 2)
