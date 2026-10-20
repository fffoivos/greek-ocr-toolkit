"""Actual ImageMagick heredoc fixtures; canonical scanner invoked unchanged in place."""
import base64, json, os, shutil, subprocess, tempfile
from ss4_common import *
from run_type import PILLOW
from ss4b_replay_fixture import call
DEST=SS/'q3/replay_fixture_ss4c'

def run():
    check_scanner(); DEST.mkdir(exist_ok=True)
    witness=json.loads((SS/'q3/answers/t01.run2_VOID.scan.json').read_text())
    # Read the recorded shell command, not the reader's answers or image judgments.
    recorded=[]
    for line in Path(witness['rollout']).open():
        obj=json.loads(line)
        def walk(x):
            if isinstance(x,dict):
                for k,v in x.items():
                    if k=='cmd' and isinstance(v,str) and "for c in cards[start:start+8]:" in v and 'answers.jsonl' not in v: recorded.append(v)
                    elif isinstance(v,(dict,list)): walk(v)
                    elif k=='arguments' and isinstance(v,str):
                        try: walk(json.loads(v))
                        except ValueError: pass
            elif isinstance(x,list):
                for v in x: walk(v)
        walk(obj)
    if not recorded: raise ValueError('recorded unlabelled montage heredoc not found')
    original=recorded[0]
    base=original.replace('cards.jsonl','items.jsonl').replace('crops/','img/')
    # Bound the fixture to one group; preserve the reader's JSON/subprocess idiom.
    base=base.replace('range(0,len(cards),8)','range(0,8,8)').replace("['magick','montage']","['magick','montage','-font','Helvetica']")
    env=dict(os.environ,MAGICK_CONFIGURE_PATH=str(SS/'q3/replay_fixture/fontconfig'))
    dump(DEST/'SOURCE.json',dict(rollout=witness['rollout'],sha256=sha(witness['rollout']),original_command=original,adaptations=['items.jsonl + img/', 'one group only', 'second montage uses 300% rather than 400%', 'fresh second01 name in c', 'literal Helvetica font with fixture-generation-only registry from SS4b; scanner environment unchanged']))
    results={}
    for case in ('a','b','c','pwd','absolute_font'):
        parent=Path(tempfile.mkdtemp(prefix='ss4c_'+case+'_',dir=PACK_ROOT)); reader=parent/'r1'
        source=PACK_ROOT/'type2/t01/r1'; shutil.copytree(source,reader)
        shutil.copyfile(source.parent/'MANIFEST.r1.json',parent/'MANIFEST.r1.json')
        records=[]
        def execute(cmd,cid):
            records.append(call('exec_command',dict(cmd=cmd),cid))
            p=subprocess.run(cmd,shell=True,cwd=reader,capture_output=True,text=True,env=env)
            records.append(dict(payload=dict(type='function_call_output',call_id=cid,output=dict(exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))))
            if p.returncode: raise ValueError(p.stderr)
        execute('mkdir -p zoom','mkdir')
        commands=[base]
        if case in ('b','c'):
            second=base.replace('400%','300%')
            if case=='c': second=second.replace('zoom/group','zoom/second')
            commands.append(second)
        if case=='absolute_font':
            commands[0]=base.replace("'Helvetica'", "'/System/Library/Fonts/Helvetica.ttc'")
        for i,cmd in enumerate(commands):
            execute(cmd,f'm{i}')
            path='zoom/second01.png' if case=='c' and i==1 else 'zoom/group01.png'
            records.append(call('view_image',dict(path='$(pwd)/'+path if case=='pwd' else path),f'v{i}'))
            records.append(dict(payload=dict(type='function_call_output',call_id=f'v{i}',output=[dict(type='input_image',image_url='data:image/png;base64,'+base64.b64encode((reader/path).read_bytes()).decode())])))
        rollout=DEST/f'{case}.rollout.jsonl'; jsonl(rollout,records)
        check_scanner()
        p=subprocess.run(PILLOW+[str(SCANNER),str(rollout),str(reader)],capture_output=True,text=True)
        scanpath=DEST/f'{case}.scan.json'; scanpath.write_text(p.stdout); (DEST/f'{case}.stderr.txt').write_text(p.stderr)
        scan=json.loads(p.stdout)
        results[case]=dict(ok=scan['ok'],outcome='ok' if scan['ok'] else 'VOID',returncode=p.returncode,image_match_counts=scan['image_match_counts'],violations=scan['violations'],reproductions=scan['reproductions'],rollout=str(rollout),scan=str(scanpath),reader=str(reader))
        print(case,results[case]['outcome'],scan['image_match_counts'],flush=True)
    result=dict(status='PASS' if results['c']['ok'] and all(not results[n]['ok'] for n in ('pwd','absolute_font')) else 'FAIL',scanner=str(SCANNER),scanner_sha256=sha(SCANNER),cases=results)
    dump(DEST/'RESULT.json',result)
    return result
if __name__=='__main__': sys.exit(0 if run()['status']=='PASS' else 2)
