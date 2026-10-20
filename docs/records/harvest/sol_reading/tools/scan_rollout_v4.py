#!/usr/bin/env python3
"""Offline rollout audit v4: image provenance, literal paths, manifest integrity.
Downscales: long side 2048, aspect within one pixel, RGB mean absolute
error < 2.0/255 using one of Pillow's standard resampling filters.
Reproductions require identical bytes or identical mode, size, and RGB(A) pixels.
This audits recorded inputs/outputs, not OS isolation.
"""
import argparse,base64,io,json,re,sys,subprocess,tempfile,shutil
from replay_literal import parse as parse_replay
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
from common import sha,rows
CALL_TYPES={'custom_tool_call','function_call','local_shell_call'}
LITERAL=r'''(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`)'''

def unquote(value):
    try:return json.loads(value)
    except (ValueError,TypeError):return re.sub(r'\\([\\\'"`])',r'\1',value[1:-1])

def quoted_property(code,name):
    return [unquote(m[1]) for m in re.finditer(r'(?:["\']?'+name+r'["\']?)\s*:\s*('+LITERAL+')',code)]

def integrity(directory,skip=False):
    directory=Path(directory);manifest=directory.parent/f'MANIFEST.{directory.name}.json';errors=[]
    if not manifest.is_file():return ([] if skip else ['missing MANIFEST'],True)
    files=json.loads(manifest.read_text())['files']
    for rel,digest in files.items():
        p=directory/rel
        if Path(rel).is_absolute() or '..' in Path(rel).parts:errors.append('unsafe manifest path: '+rel);continue
        if not p.is_file() or p.is_symlink() or sha(p)!=digest:errors.append('original changed or missing: '+rel)
    for p in directory.rglob('*'):
        rel=str(p.relative_to(directory))
        if p.is_symlink():errors.append('symlink: '+rel);continue
        if p.is_file():
            if p.stat().st_nlink!=1:errors.append('hardlink: '+rel)
            if rel not in files and rel!='answers.jsonl' and not rel.startswith('zoom/'):errors.append('unallowed added file: '+rel)
        elif p.is_dir() and not any(f.startswith(rel+'/') for f in files) and rel!='zoom' and not rel.startswith('zoom/'):errors.append('unallowed added directory: '+rel)
    return errors,False

def strings(obj):
    if isinstance(obj,str):yield obj
    elif isinstance(obj,dict):
        for v in obj.values():yield from strings(v)
    elif isinstance(obj,list):
        for v in obj:yield from strings(v)

def image_blocks(obj):
    if isinstance(obj,dict):
        if obj.get('type')=='input_image':yield obj
        else:
            for v in obj.values():yield from image_blocks(v)
    elif isinstance(obj,list):
        for v in obj:yield from image_blocks(v)
    elif isinstance(obj,str) and obj.lstrip().startswith(('[','{')):
        try:yield from image_blocks(json.loads(obj))
        except ValueError:pass

def match_image(data,candidates):
    for rel,blob,im in candidates:
        if data==blob:return dict(path=rel,match='bytes',mad=0)
    with Image.open(io.BytesIO(data)) as out:
        out=out.convert('RGB');w,h=out.size
        for rel,blob,im in candidates:
            if max(im.size)<=2048 or max(w,h)!=2048:continue
            scale=2048/max(im.size)
            if abs(w-im.width*scale)>1 or abs(h-im.height*scale)>1:continue
            for filt in (Image.Resampling.LANCZOS,Image.Resampling.BICUBIC,Image.Resampling.BILINEAR,Image.Resampling.NEAREST,Image.Resampling.BOX,Image.Resampling.HAMMING):
                diff=ImageChops.difference(out,im.resize((w,h),filt));mad=sum(ImageStat.Stat(diff).mean)/3
                if mad<2.0:return dict(path=rel,match='downscale',mad=mad,resampling=filt.name)
    return None

REPLAY_TMP=Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/d11f6140-6320-42d0-9f21-018ca3512d68/scratchpad/g4_tmp')

def reproduce(data,directory,view,history):
    """Only invoked after ordinary v3 provenance fails; never seed from zoom."""
    receipt={'view':view,'commands':[]}
    try:
        errors,skipped=integrity(directory)
        if errors or skipped:raise ValueError('original pack integrity failed: '+str(errors))
        manifest=json.loads((directory.parent/f'MANIFEST.{directory.name}.json').read_text())
        rel=Path(view)
        if rel.is_absolute():rel=rel.relative_to(directory)
        if '..' in rel.parts or not str(rel).startswith('zoom/'):raise ValueError('unsupported view path')
        with tempfile.TemporaryDirectory(prefix='reproduce-',dir=REPLAY_TMP) as tmp:
            root=Path(tmp)
            for name,digest in manifest['files'].items():
                if name!='items.jsonl' and not name.startswith('img/'):continue
                src=directory/name;dst=root/name;dst.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(src,dst)
                if sha(dst)!=digest:raise ValueError('copied original digest mismatch')
            receipt['manifest_verified']=True
            receipt['original_files']=sum(n=='items.jsonl' or n.startswith('img/') for n in manifest['files'])
            for ordinal,cmd in history:
                event=dict(record=ordinal,command=cmd)
                try:parse_replay(cmd)
                except (ValueError,SyntaxError) as exc:
                    event.update(status='skipped',reason=str(exc));receipt['commands'].append(event);continue
                try:
                    run=subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('replay_literal.py')),str(root)],input=cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60,env=dict(PATH='/opt/homebrew/bin:/usr/bin:/bin',PYTHONDONTWRITEBYTECODE='1',MAGICK_TEMPORARY_PATH=str(root),TMPDIR=str(root)))
                    event.update(status='replayed',returncode=run.returncode,stderr=run.stderr[-2000:])
                except subprocess.TimeoutExpired:event.update(status='failed',reason='timeout')
                receipt['commands'].append(event)
            p=root/rel
            if not p.is_file() or p.is_symlink():raise ValueError('reproduced view missing')
            with Image.open(p) as im:
                match=dict(path=str(rel),match='bytes',mad=0) if data==p.read_bytes() else None
                receipt['size']=list(im.size);receipt['sha256']=sha(p)
                with Image.open(io.BytesIO(data)) as observed:
                    receipt['observed_size']=list(observed.size)
                    receipt['mode']=im.mode;receipt['observed_mode']=observed.mode
                    exact=(im.mode==observed.mode and im.size==observed.size and im.convert('RGBA').tobytes()==observed.convert('RGBA').tobytes())
                    receipt['pixels_exact']=exact
                    if match is None and exact:match=dict(path=str(rel),match='pixels',mad=0)
                    if im.size==observed.size:
                        receipt['same_size_rgb_exact']=ImageChops.difference(im.convert('RGB'),observed.convert('RGB')).getbbox() is None
                        receipt['metadata_differences']={k:dict(observed=observed.info.get(k),reproduced=im.info.get(k)) for k in set(im.info)|set(observed.info) if im.info.get(k)!=observed.info.get(k)}
            if match:
                return dict(match,match='reproduced_pixels' if match['match']=='pixels' else 'reproduced',comparison=match['match'],reproduction=receipt),receipt
            raise ValueError('reproduced file fails exact bytes/pixels policy')
    except Exception as exc:receipt['error']=str(exc)
    return None,receipt


def inspect(rollout,directory,skip_manifest=False):
    directory=Path(directory).resolve();violations=[];views=[];commands=[];paths=[];matches=[];usage=None;rate_limits=None;tool_calls=0
    candidates=[];history=[];pending={};reproductions=[]
    for p in directory.rglob('*.png'):
        if p.is_symlink():continue
        rel=str(p.relative_to(directory))
        if not (rel.startswith(('img/','crops/','zoom/')) or skip_manifest):continue
        try:
            with Image.open(p) as im:candidates.append((rel,p.read_bytes(),im.convert('RGB')))
        except OSError:pass
    def check(value,ordinal):
        # Resolve only literal interpolations, never execute rollout code.
        value=re.sub(r"\$\{\s*("+LITERAL+r")\s*\}",lambda m:unquote(m[1]),value)
        # A computed interpolation owns its suffix, e.g. ${base}/zoom/${i}.
        # Mask the slash after it so it cannot become a standalone absolute path.
        value=re.sub(r'(\$\{[^{}]*\})/',r'\1RELATIVE_SLASH',value)
        # Own absolute folder is allowed, including forbidden-looking ancestors.
        value=re.sub(re.escape(str(directory))+r'(?=$|[\s/"\'`;,)}])','READER_DIR',value)
        # Components/names only: code identifiers such as x.keys() are harmless.
        bad=re.search(r'(?i)(?:\$HOME|/Users/|(?:^|[\s/"\'`])(?:\.\.|~)(?=$|[\s/"\'`])|(?:^|[^\w])(?:keys(?=/)|[^\s/"\'`]*key[^\s/"\'`]*\.json\b|truth\b|verdict\b|opus_reference\b|MANIFEST\b|sol_reading_packs\b))',value)
        if bad:violations.append(dict(record=ordinal,reason='forbidden literal path/name',input=value,matched=bad.group()))
        for other in ('r1','r2','r3'):
            if other!=directory.name and re.search(r'(?:^|[\s/"\'`])'+other+r'(?:$|[\s/"\'`])',value):violations.append(dict(record=ordinal,reason='other reader folder',input=value))
        for path in re.findall(r'''(?<![\w:/])/(?:[^\s"'`;,(){}<>|&\\])+''',value):
            paths.append(path)
            if not (path==str(directory) or path.startswith(str(directory)+'/')):violations.append(dict(record=ordinal,reason='absolute path outside reader_dir',path=path))
    if not Path(rollout).is_file():violations.append({'reason':'missing rollout: '+str(rollout)})
    for ordinal,obj in enumerate(rows(rollout) if Path(rollout).is_file() else []):
        p=obj.get('payload') or {}
        if not isinstance(p,dict):continue
        if p.get('type')=='token_count':
            usage=(p.get('info') or {}).get('total_token_usage') or usage;rate_limits=p.get('rate_limits') or rate_limits
        if p.get('type') in ('custom_tool_call_output','function_call_output'):
            for image_index,block in enumerate(image_blocks(p)):
                try:
                    url=block.get('image_url');url=url.get('url') if isinstance(url,dict) else url
                    if not isinstance(url,str) or not url.startswith('data:image/'):raise ValueError('non-data image')
                    match=match_image(base64.b64decode(url.split(',',1)[1],validate=True),candidates)
                    if match is None:
                        calls=pending.get(p.get('call_id'),[])
                        if image_index<len(calls):
                            view,prior=calls[image_index]
                            match,receipt=reproduce(base64.b64decode(url.split(',',1)[1],validate=True),directory,view,prior)
                            reproductions.append(dict(record=ordinal,**receipt))
                        if match is None:raise ValueError('unmatched image provenance')
                    matches.append(dict(record=ordinal,**match))
                except Exception as exc:violations.append(dict(record=ordinal,reason='image provenance: '+str(exc)))
        if p.get('type') not in CALL_TYPES:continue
        tool_calls+=1;name=p.get('name','local_shell_call');raw=p.get('input',p.get('arguments',p.get('action',{})))
        if name=='exec':
            text=raw if isinstance(raw,str) else json.dumps(raw)
            # Template text is retained, including computed templates; no static path resolution required.
            for m in re.finditer(LITERAL,text):check(unquote(m[0]),ordinal)
            v=quoted_property(text,'path');c=quoted_property(text,'cmd');views.extend(v);commands.extend(c)
            for cmd in c:check(cmd,ordinal)
            selected=[]
            for op in re.finditer(r'tools\.(exec_command|view_image)\s*\(\s*\{\s*(?:[\"\']?(?:cmd|path)[\"\']?)\s*:\s*('+LITERAL+')',text):
                value=unquote(op[2])
                if op[1]=='exec_command':history.append((ordinal,value))
                else:selected.append((value,list(history)))
            pending[p.get('call_id')]=selected
        else:
            try:args=json.loads(raw) if isinstance(raw,str) else raw
            except ValueError:args=raw
            for value in strings(args):check(value,ordinal)
            if isinstance(args,dict):
                if 'view_image' in name and isinstance(args.get('path'),str):
                    views.append(args['path']);pending[p.get('call_id')]=[(args['path'],list(history))]
                if 'exec_command' in name or p.get('type')=='local_shell_call':
                    cmd=args.get('cmd',args.get('command'))
                    if isinstance(cmd,list):cmd=' '.join(cmd)
                    if isinstance(cmd,str):commands.append(cmd);check(cmd,ordinal);history.append((ordinal,cmd))
    errors,skipped=integrity(directory,skip_manifest);violations.extend({'reason':e} for e in errors)
    zoom=[dict(path=str(p.relative_to(directory)),sha256=sha(p),bytes=p.stat().st_size) for p in sorted((directory/'zoom').rglob('*')) if p.is_file()]
    return dict(scanner_version=4,reproductions=reproductions,ok=not violations,violations=violations,image_policy={'reproduction':'exact bytes or same mode, size, RGB(A) pixels', 'long_side':2048,'aspect_tolerance_px':1,'rgb_mad_strictly_below':2.0},image_matches=matches,returned_images=len(matches)+sum(v['reason'].startswith('image provenance:') for v in violations),zoom=zoom,view_image_calls=len(views),distinct_images_viewed=len(set(m['path'] for m in matches)),images_viewed=sorted(set(m['path'] for m in matches)),exec_commands=len(commands),commands=commands,paths=paths,tool_calls=tool_calls,total_token_usage=usage,rate_limits=rate_limits,manifest_check_skipped=skipped)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rollout',type=Path);p.add_argument('reader_dir',type=Path);p.add_argument('--skip-manifest',action='store_true');a=p.parse_args()
    result=inspect(a.rollout,a.reader_dir,a.skip_manifest);print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['ok'] else 2
if __name__=='__main__':sys.exit(main())
