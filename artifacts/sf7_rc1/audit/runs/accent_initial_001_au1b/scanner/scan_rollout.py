#!/usr/bin/env python3
"""Offline rollout audit 4.5.2: image provenance, literal paths, manifest integrity.
Downscales: any non-upscaling common scale, aspect within one pixel, RGB mean absolute
error < 2.0/255 using one of Pillow's standard resampling filters.
Historical reproductions use the same image policy as current views.
This audits recorded inputs/outputs, not OS isolation.
"""
import argparse,ast,base64,hashlib,io,json,re,sys,subprocess,tempfile,shutil,shlex
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
        # view_image may re-encode a PNG without changing mode or pixels.
        for rel,blob,im in candidates:
            if im.size != out.size:continue
            with Image.open(io.BytesIO(blob)) as original:
                if original.mode == out.mode and original.tobytes() == out.tobytes():
                    return dict(path=rel,match='pixels',mad=0)
        observed_mode=out.mode
        opaque=out.mode!='RGBA' or out.getchannel('A').getextrema()==(255,255)
        out=out.convert('RGB');w,h=out.size
        for rel,blob,im in candidates:
            if w>im.width or h>im.height or (w,h)==im.size:continue
            # A single scale must lie in both per-axis one-pixel intervals.
            lo=max(0,(w-1)/im.width,(h-1)/im.height)
            hi=min(1,(w+1)/im.width,(h+1)/im.height)
            if lo>hi:continue
            with Image.open(io.BytesIO(blob)) as original:
                if original.convert('RGBA').getchannel('A').getextrema()!=(255,255):continue
                if observed_mode not in ('RGB','RGBA','L'):continue
            if not opaque:continue
            for filt in (Image.Resampling.LANCZOS,Image.Resampling.BICUBIC,Image.Resampling.BILINEAR,Image.Resampling.NEAREST,Image.Resampling.BOX,Image.Resampling.HAMMING):
                diff=ImageChops.difference(out,im.resize((w,h),filt));mad=sum(ImageStat.Stat(diff).mean)/3
                if mad<2.0:return dict(path=rel,match='downscale',mad=mad,resampling=filt.name)
    return None

# Reproduction writes only into fresh OS temporary directories.
REPLAY_TMP=Path(tempfile.gettempdir())
VERSION='4.5.2'

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
            for ordinal,cmd in replay_history(history):
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
                    if match is None:match=match_image(data,[(str(rel),p.read_bytes(),im.convert('RGB'))])
                    if im.size==observed.size:
                        receipt['same_size_rgb_exact']=ImageChops.difference(im.convert('RGB'),observed.convert('RGB')).getbbox() is None
                        receipt['metadata_differences']={k:dict(observed=observed.info.get(k),reproduced=im.info.get(k)) for k in set(im.info)|set(observed.info) if im.info.get(k)!=observed.info.get(k)}
            if match:
                return dict(match,match='reproduced_pixels' if match['match']=='pixels' else ('reproduced_downscale' if match['match']=='downscale' else 'reproduced'),comparison=match['match'],reproduction=receipt),receipt
            raise ValueError('reproduced file fails image policy')
    except Exception as exc:receipt['error']=str(exc)
    return None,receipt


def _inspect_records(records,directory,skip_manifest=False,path_inputs=None):
    directory=Path(directory).resolve();violations=[];views=[];commands=[];paths=[];matches=[];usage=None;rate_limits=None;tool_calls=0
    candidates=[];history=[];pending={};reproductions=[];legacy_data_call=None
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
        for path in re.findall(r'''(?<![\w:/)])/(?:[^\s"'`;,(){}<>|&\\])+''',value):
            paths.append(path)
            if not (path==str(directory) or path.startswith(str(directory)+'/')):violations.append(dict(record=ordinal,reason='absolute path outside reader_dir',path=path))
    for ordinal,obj in enumerate(records):
        p=obj.get('payload') or {}
        if not isinstance(p,dict):continue
        if p.get('type')=='item_completed' and legacy_data_call is not None:
            item=p.get('item') or {}
            if item.get('type')=='ImageView' and isinstance(item.get('path'),str):
                path=item['path'].removeprefix('file://')
                try:rel=Path(path).relative_to(directory)
                except ValueError:rel=Path('__outside__')
                # Witnessed original-data views confer no zoom replay authority.
                check(path,ordinal)
                pending[legacy_data_call].append((path if str(rel).startswith(('img/','crops/')) else '__unsupported__',[]))
        if p.get('type')=='token_count':
            usage=(p.get('info') or {}).get('total_token_usage') or usage;rate_limits=p.get('rate_limits') or rate_limits
        if p.get('type') in ('custom_tool_call_output','function_call_output'):
            for image_index,block in enumerate(image_blocks(p)):
                try:
                    url=block.get('image_url');url=url.get('url') if isinstance(url,dict) else url
                    if not isinstance(url,str) or not url.startswith('data:image/'):raise ValueError('non-data image')
                    calls=pending.get(p.get('call_id'),[])
                    chosen=candidates
                    if image_index<len(calls):
                        requested=Path(calls[image_index][0])
                        if requested.is_absolute():
                            try:requested=requested.relative_to(directory)
                            except ValueError:requested=Path('__outside__')
                        chosen=[c for c in candidates if c[0]==str(requested)]
                    elif calls:chosen=[]
                    else:chosen=[c for c in candidates if c[0].startswith(("img/","crops/"))]
                    match=match_image(base64.b64decode(url.split(',',1)[1],validate=True),chosen)
                    if match and match['match']=='downscale' and not calls:match=None
                    if match and match['match']=='downscale' and match['path'].startswith('zoom/'):
                        # Preserve v4's established 2048 baseline. New scale
                        # admission requires a manifest-seeded reconstruction.
                        with Image.open(io.BytesIO(base64.b64decode(url.split(',',1)[1],validate=True))) as observed:
                            source=next(c[2] for c in chosen if c[0]==match['path'])
                            legacy=max(source.size)>2048 and max(observed.size)==2048
                        if not legacy:match=None
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
        legacy_data_call=None
        tool_calls+=1;name=p.get('name','local_shell_call');raw=p.get('input',p.get('arguments',p.get('action',{})))
        if name=='exec':
            text=raw if isinstance(raw,str) else json.dumps(raw)
            # Template text is retained, including computed templates; no static path resolution required.
            # Inspect literals erased by loop expansion as well as concrete paths.
            original=(path_inputs or {}).get(ordinal,text)
            current_literals={unquote(m[0]) for m in re.finditer(LITERAL,text)}
            for m in re.finditer(LITERAL,original):
                value=unquote(m[0])
                if value not in current_literals:check(answer_data(value,history),ordinal)
            ops=list(re.finditer(r'tools\.(exec_command|view_image)\s*\(\s*\{\s*(?:[\"\']?(?:cmd|path)[\"\']?)\s*:\s*('+LITERAL+')',text))
            operations={op.start(2):op for op in ops};selected=[]
            for m in re.finditer(LITERAL,text):
                value=unquote(m[0]);check(answer_data(value,history),ordinal)
                op=operations.get(m.start())
                if op:
                    if op[1]=='exec_command':history.append((ordinal,value))
                    else:selected.append((value,list(history)))
            v=quoted_property(text,'path');c=quoted_property(text,'cmd');views.extend(v);commands.extend(c)
            pending[p.get('call_id')]=selected
            if not selected and re.fullmatch(r'\s*for\(const \w+ of load\('+LITERAL+r'\)\.slice\(\d+,\d+\)\)image\(\(await tools\.view_image\(\{path:\w+\.crop\}\)\)\.image_url\);\s*',text):
                legacy_data_call=p.get('call_id')
        else:
            try:args=json.loads(raw) if isinstance(raw,str) else raw
            except ValueError:args=raw
            for value in strings(args):check(answer_data(value,history),ordinal)
            if isinstance(args,dict):
                if 'view_image' in name and isinstance(args.get('path'),str):
                    views.append(args['path']);pending[p.get('call_id')]=[(args['path'],list(history))]
                if 'exec_command' in name or p.get('type')=='local_shell_call':
                    cmd=args.get('cmd',args.get('command'))
                    if isinstance(cmd,list):cmd=' '.join(cmd)
                    if isinstance(cmd,str):commands.append(cmd);history.append((ordinal,cmd))
    errors,skipped=integrity(directory,skip_manifest);violations.extend({'reason':e} for e in errors)
    zoom=[dict(path=str(p.relative_to(directory)),sha256=sha(p),bytes=p.stat().st_size) for p in sorted((directory/'zoom').rglob('*')) if p.is_file()]
    return dict(scanner_version=VERSION,reproductions=reproductions,ok=not violations,violations=violations,image_policy={'reproduction':'same image policy as current views', 'scale':'non-upscaling common scale','aspect_tolerance_px':1,'rgb_mad_strictly_below':2.0},image_matches=matches,returned_images=len(matches)+sum(v['reason'].startswith('image provenance:') for v in violations),zoom=zoom,view_image_calls=len(views),distinct_images_viewed=len(set(m['path'] for m in matches)),images_viewed=sorted(set(m['path'] for m in matches)),exec_commands=len(commands),commands=commands,paths=paths,tool_calls=tool_calls,total_token_usage=usage,rate_limits=rate_limits,manifest_check_skipped=skipped)

# Consume quoted strings/comments atomically: commands and comments cannot
# manufacture bindings. Templates are deliberately opaque and unsupported.
TOKEN = re.compile(r'''//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`|[A-Za-z_$][\w$]*|[^\s]''')

def literal(token):
    if not token or token[0] not in "\"'":
        return None
    try:
        value = json.loads(token) if token[0] == '"' else ast.literal_eval(token)
    except (ValueError, SyntaxError):
        return None
    # Keep decoding conservative across Python and JavaScript string syntax.
    if re.search(r'\\(?![\\\'"/bfnrt]|u[0-9a-fA-F]{4})', token):
        return None
    return value if isinstance(value, str) else None


def resolve(records, call_types):
    bindings = {}; recorded_stores = set(); resolutions = []; failures = []
    for ordinal, obj in enumerate(records):
        p = obj.get('payload', {})
        if p.get('type') not in call_types or p.get('name') != 'exec':
            continue
        field = 'input' if 'input' in p else 'arguments'
        raw = p.get(field)
        if not isinstance(raw, str): continue
        tokens = [m for m in TOKEN.finditer(raw) if not m[0].startswith(('//', '/*'))]
        edits = []
        for i, token in enumerate(tokens):
            t = [m[0] for m in tokens[i:i+8]]
            if i and tokens[i-1][0] in ('.', 'function'): continue
            if len(t) >= 4 and t[:2] == ['store', '('] and t[3] == ',':
                name = literal(t[2])
                if name is not None:
                    recorded_stores.add(name)
                    value = literal(t[4]) if len(t) >= 6 and t[5] == ')' else None
                    bindings.pop(name, None)
                    if value is not None:
                        bindings[name] = dict(value=value, record=ordinal,
                            expression=raw[token.start():tokens[i+5].end()])
            if len(t) >= 4 and t[:2] == ['load', '('] and t[3] == ')':
                name = literal(t[2]); binding = bindings.get(name)
                # Recorded non-concatenated data loads (RU1 rows) retain v4
                # behavior. Missing stores and unresolved concatenations fail.
                concatenated = len(t) >= 5 and t[4] == '+'
                if not concatenated and name in recorded_stores: continue
                suffix = literal(t[5]) if len(t) >= 6 and t[4] == '+' else None
                if binding is None or suffix is None:
                    failures.append(dict(record=ordinal, reason='unresolvable load expression',
                        expression=raw[token.start():tokens[i+3].end()], name=name))
                    continue
                end = tokens[i+5].end(); value = binding['value'] + suffix
                edits.append((token.start(), end, json.dumps(value)))
                resolutions.append(dict(record=ordinal, expression=raw[token.start():end],
                    name=name, literal_suffix=suffix, binding=binding.copy(), resolved=value))
        for start, end, replacement in reversed(edits):
            raw = raw[:start] + replacement + raw[end:]
        p[field] = raw
    return resolutions, failures


def font_path(path):
    p = Path(path)
    return '..' not in p.parts and any(path.startswith(prefix) and len(path)>len(prefix)
        for prefix in ('/System/Library/Fonts/', '/Library/Fonts/'))


def read_proofs(cmd, path):
    """Return the number of statically proven read operands, or zero."""
    heredoc = re.fullmatch(r"python3 - <<'PY'\n(.*)\nPY", cmd, re.S)
    if heredoc:
        try: tree = ast.parse(heredoc[1])
        except SyntaxError: return 0
        occurrences = [n for n in ast.walk(tree) if isinstance(n, ast.Constant) and n.value == path]
        proved = set()
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name) and node.func.value.id == 'subprocess'
                and node.func.attr == 'run' and node.args and isinstance(node.args[0], ast.List)):
                continue
            args = node.args[0].elts
            if not args or not isinstance(args[0], ast.Constant) or args[0].value != 'magick': continue
            for i, arg in enumerate(args):
                if (i>0 and i<len(args)-1 and isinstance(arg, ast.Constant) and arg.value == path
                    and isinstance(args[i-1], ast.Constant) and args[i-1].value == '-font'):
                    proved.add(id(arg))
        return len(proved) if occurrences and all(id(n) in proved for n in occurrences) else 0
    try: args = shlex.split(cmd)
    except ValueError: return 0
    if args and args[0] in ('cat','stat','ls') and all(
        a == path or (a.startswith('-') and re.fullmatch(r'-[A-Za-z-]+', a)) for a in args[1:]):
        return args.count(path)
    return 0



PWD = '${(await tools.exec_command({cmd:"pwd",max_output_tokens:100})).output.trim()}'


def resolve_templates(records, directory):
    """v4.1 witnessed pwd and literal base templates; never execute tool input.

    v4.3's stricter literal-store resolver handles concatenations first.
    v4.1 templates retain the witnessed const base / store(base, base) idiom.
    """
    evidence = []; resolutions = []; failures = []; base = None; stores = {}
    for ordinal, obj in enumerate(records):
        p = obj.get('payload') or {}
        if not isinstance(p, dict) or p.get('type') not in CALL_TYPES: continue
        field = 'input' if 'input' in p else 'arguments'
        raw = p.get(field)
        if not isinstance(raw, str): continue
        updated = raw
        if PWD in raw:
            outputs = []
            for j in range(ordinal + 1, len(records)):
                q = records[j].get('payload') or {}
                if not isinstance(q, dict): continue
                if q.get('type') in CALL_TYPES: break
                item = q.get('item') or {}
                if item.get('type') == 'CommandExecution' and item.get('command', [])[-1:] == ['pwd']:
                    outputs.append(dict(record=j, pwd=item.get('stdout', '').strip(), exit_code=item.get('exit_code')))
            if not outputs or any(e['pwd'] != str(directory) or e['exit_code'] != 0 for e in outputs):
                failures.append(dict(record=ordinal, reason='pwd output absent or differs from reader_dir', outputs=outputs))
            else:
                updated = updated.replace(PWD, str(directory))
                evidence.append(dict(record=ordinal, expression=PWD, outputs=outputs, resolved_pwd=str(directory)))
        if p.get('name') == 'exec':
            tokens = [m[0] for m in TOKEN.finditer(updated) if not m[0].startswith(('//', '/*'))]
            for i, token in enumerate(tokens):
                t = tokens[i:i+6]
                if len(t) >= 4 and t[:3] == ['const', 'base', '=']:
                    base = literal(t[3])
                if len(t) >= 4 and t[:2] == ['store', '('] and t[3] == ',' and (not i or tokens[i-1] not in ('.', 'function')):
                    name = literal(t[2]); value = literal(t[4]) if len(t) == 6 and t[5] == ')' else None
                    if name is not None:
                        stores.pop(name, None)
                        if value is not None: stores[name] = value
            if base is not None: updated = updated.replace('${base}', base)
            def template_load(m):
                name = literal(m[1])
                if name in stores: return stores[name]
                if name == 'base' and base is not None: return base
                failures.append(dict(record=ordinal, reason='unresolvable load expression', expression=m[0], name=name))
                return m[0]
            updated = re.sub(r'\$\{\s*load\(('+LITERAL+r')\)\s*\}', template_load, updated)
        if updated != raw:
            resolutions.append(dict(record=ordinal, original=raw, resolved=updated))
            p[field] = updated
    return resolutions, evidence, failures



# P1: prompt semantics give breathing n/s/r/u, accent n/a/g/c/u;
# Optional ? denotes low confidence; yes/no pairs and numeric item ids cover
# the other HANDOVER answer formats. Only this audited confined recorder can
# consume shorthand. Its AST pins all IO and mappings, not merely its filename.
RECORD_AST_SHA = 'd7e8022eb608fe49fc3b39ce77c66228f519bc795eac323a1152371b21e47107'
ANSWER_ATOM = re.compile(r'(?:[nsru]\??/[nagcu]\??|[yn]\??/[yn]\??|[0-9]+)')
HEREDOC = re.compile(r"(?m)^(?:(?:python|python3) -|cat > (zoom/[A-Za-z0-9_.-]+\.py)) <<'([A-Za-z_]+)'\n(.*?)\n\2(?=\n|$)",re.S)

def recorded_helpers(history):
    helpers={}
    for _,cmd in history:
        for name in list(helpers):
            if name in cmd and not re.fullmatch(r'(?:python|python3) '+re.escape(name)+r' [^\n;|&<>]+',cmd):helpers.pop(name)
        for m in HEREDOC.finditer(cmd):
            if m[1]:helpers[m[1]]=m[3]
    return helpers

def answer_data(command,history):
    try: args=shlex.split(command)
    except ValueError:return command
    if len(args)!=3 or args[:2] not in (['python','zoom/record.py'],['python3','zoom/record.py']):return command
    atoms=args[2].split()
    if not atoms or not all(ANSWER_ATOM.fullmatch(a) for a in atoms):return command
    code=recorded_helpers(history).get('zoom/record.py','')
    try:digest=hashlib.sha256(ast.dump(ast.parse(code)).encode()).hexdigest()
    except SyntaxError:return command
    if digest!=RECORD_AST_SHA:return command
    return args[0]+' '+args[1]+' ANSWER_DATA'


def independent_units(command):
    """Closed newline-separated shell grammar; never extract from unknown scopes.

    Heredoc bodies are opaque here. Shell conditionals, functions, operators,
    substitutions and unsupported commands reject the entire enclosing command.
    """
    units=[];cursor=0
    while cursor<len(command):
        m=HEREDOC.match(command,cursor)
        if m:
            units.append((m[1],m[3]) if m[1] else "python3 - <<'PY'\n"+m[3]+"\nPY")
            cursor=m.end()
            continue
        # A quoted literal argv may span lines, but cannot contain shell
        # expansions/operators. Consume the complete invocation as one unit.
        invocation=re.match(r'''(?:python|python3) zoom/[A-Za-z0-9_.-]+\.py(?: (?:[A-Za-z0-9_./?,+-]+|'[A-Za-z0-9_./?,+ \n-]*'|"[A-Za-z0-9_./?,+ \n-]*"))*(?=\n|$)''',command[cursor:])
        if invocation:
            units.append(invocation[0]);cursor+=invocation.end();continue
        end=command.find('\n',cursor)
        if end<0:end=len(command)
        line=command[cursor:end];cursor=end+1
        if not line.strip():continue
        if line in ('mkdir zoom','mkdir -p zoom','cat items.jsonl'):
            units.append(line)
        else:raise ValueError('unsupported enclosing shell context')
    return units


def invalidate_helpers(command,helpers):
    """Retain source only when all possible replay writes exclude its path."""
    try:_,code=parse_replay(command)
    except (ValueError,SyntaxError):
        helpers.clear();return
    if code is None:return # literal mkdir/read-only command
    for node in ast.walk(ast.parse(code)):
        if not isinstance(node,ast.Call):continue
        f=node.func
        if isinstance(f,ast.Attribute) and f.attr=='run':
            helpers.clear();return
        if isinstance(f,ast.Attribute) and f.attr=='save':
            target=node.args[0] if node.args else next((k.value for k in node.keywords if k.arg=='fp'),None)
        elif isinstance(f,ast.Name) and f.id=='open':
            mode=node.args[1] if len(node.args)>1 else next((k.value for k in node.keywords if k.arg=='mode'),ast.Constant('r'))
            if isinstance(mode,ast.Constant) and isinstance(mode.value,str) and not any(c in mode.value for c in 'wax+'):continue
            target=node.args[0] if node.args else next((k.value for k in node.keywords if k.arg=='file'),None)
        else:continue
        if not isinstance(target,ast.Constant) or not isinstance(target.value,str):
            helpers.clear();return
        # Normalize './zoom/...' too; unknown computed writes invalidate all.
        helpers.pop(str(Path(target.value)),None)


def replay_history(history):
    """Replay independent units in order, retaining only historical helper source."""
    helpers={}
    for ordinal,cmd in history:
        try:units=independent_units(cmd)
        except ValueError:
            # An uncertain command may mutate helpers, even through aliases.
            helpers.clear()
            yield ordinal,cmd
            continue
        # Preserve whole-command receipts for the original restricted grammar,
        # but invalidate helper source before every successful fast-path exit.
        try:_,code=parse_replay(cmd)
        except (ValueError,SyntaxError):pass
        else:
            invalidate_helpers(cmd,helpers)
            yield ordinal,cmd
            continue
        emitted=False
        for unit in units:
            if isinstance(unit,tuple):
                helpers[unit[0]]=unit[1];continue
            if unit in ('mkdir zoom','mkdir -p zoom'):
                yield ordinal,'mkdir -p zoom';emitted=True;continue
            if unit.startswith("python3 - <<'PY'\n") or unit=='cat items.jsonl':
                # Invalidate before admission: accepted image code can overwrite
                # a helper too. Never let successful replay bypass this step.
                invalidate_helpers(unit,helpers)
                try:parse_replay(unit)
                except (ValueError,SyntaxError):continue
                yield ordinal,unit;emitted=True;continue
            try:argv=shlex.split(unit)
            except ValueError:continue
            if len(argv)<2 or argv[0] not in ('python','python3') or argv[1] not in helpers:
                for name in list(helpers):
                    if name in unit:helpers.pop(name)
                continue
            if not all(re.fullmatch(r'-?\d+',v) for v in argv[2:]):continue
            # sys.argv is data, never an API made available to the worker.
            try:
                tree=ast.parse(helpers[argv[1]])
                class Argv(ast.NodeTransformer):
                    def visit_Import(self,node):
                        node.names=[a for a in node.names if a.name!='sys']
                        return node if node.names else None
                    def visit_Attribute(self,node):
                        if isinstance(node.value,ast.Name) and node.value.id=='sys' and node.attr=='argv':
                            return ast.copy_location(ast.List(elts=[ast.Constant(v) for v in argv[1:]],ctx=ast.Load()),node)
                        return self.generic_visit(node)
                tree=ast.fix_missing_locations(Argv().visit(tree))
                replay="python3 - <<'PY'\n"+ast.unparse(tree)+"\nPY"
                parse_replay(replay)
            except (ValueError,SyntaxError):continue
            # Literal argv expansion must obey the same write barrier as
            # inline replay, including writes to this helper's own source.
            invalidate_helpers(replay,helpers)
            yield ordinal,replay;emitted=True
        if not emitted:yield ordinal,cmd # retain explicit skipped receipt


def expand_view_loops(records):
    """Finite view-only JavaScript grammar; no JS evaluation or dynamic bounds."""
    evidence=[];failures=[]
    for ordinal,obj in enumerate(records):
        p=obj.get('payload') or {}
        if p.get('type') not in CALL_TYPES or p.get('name')!='exec':continue
        field='input' if 'input' in p else 'arguments';raw=p.get(field)
        if not isinstance(raw,str):continue
        tokens=[m for m in TOKEN.finditer(raw) if not m[0].startswith(('//','/*'))]
        edits=[];i=0
        while i<len(tokens):
            if tokens[i][0]!='for':i+=1;continue
            start=i;j=i+1;depth=0
            if j>=len(tokens) or tokens[j][0]!='(':i+=1;continue
            while j<len(tokens):
                t=tokens[j][0]
                if t=='(':depth+=1
                if t==')':
                    depth-=1
                    if depth==0:break
                j+=1
            if j+1>=len(tokens):
                failures.append(dict(record=ordinal,reason='unsupported view loop'));break
            header=raw[tokens[i+1].end():tokens[j].start()]
            a=re.fullmatch(r'\s*(?:const|let)\s+(\w+)\s+of\s+\[([^\[\]]*)\]\s*',header)
            r=re.fullmatch(r'\s*let\s+(\w+)\s*=\s*(\d+)\s*;\s*\1\s*(<=|<)\s*(\d+)\s*;\s*\1\+\+\s*',header)
            values=None;var=None
            if a:
                var=a[1]
                try:
                    values=ast.literal_eval('['+a[2]+']')
                    if not all(type(v) in (str,int) for v in values):values=None
                except (ValueError,SyntaxError):pass
            elif r:
                var=r[1];lo=int(r[2]);hi=int(r[4])+(r[3]=='<=')
                if 0<=hi-lo<=1000:values=list(range(lo,hi))
            k=j+1;body_start=k;braced=tokens[k][0]=='{'
            if braced:
                depth=1;k+=1;body_start=k
                while k<len(tokens) and depth:
                    if tokens[k][0]=='{':depth+=1
                    elif tokens[k][0]=='}':depth-=1
                    if depth:k+=1
                if depth:
                    failures.append(dict(record=ordinal,reason='unterminated view loop'));break
                body_end=k;end=k+1
            else:
                # The only admitted body is image(...), with balanced parens.
                depth=0;k=body_start
                while k<len(tokens):
                    if tokens[k][0]=='(':depth+=1
                    elif tokens[k][0]==')':
                        depth-=1
                        if depth==0: k+=1;break
                    k+=1
                body_end=k;end=k
            body=raw[tokens[body_start].start():tokens[body_end-1].end()] if body_end>body_start else ''
            # Exact image wrapper: no extra statements, hidden calls, or side effects.
            if var:body=re.sub(r'^text\(\s*'+re.escape(var)+r'\s*\);\s*','',body)
            view=re.fullmatch(r'image\s*\(\s*\(\s*await\s+tools\.view_image\s*\(\s*\{\s*path\s*:\s*('+LITERAL+r')\s*\}\s*\)\s*\)\.image_url\s*\)\s*;?',body)
            if not view and re.fullmatch(r'\s*(?:const|let)\s+\w+\s+of\s+load\('+LITERAL+r'\)\.slice\(\d+,\d+\)\s*',header) and re.fullmatch(r'image\(\(await tools\.view_image\(\{path:\w+\.crop\}\)\)\.image_url\);?',body):
                # Legacy data views gain no expansion/replay authority. Only
                # manifest original images and recorded ImageView events prove outputs.
                i=max(end,i+1);continue
            if values is None or len(values)>1000 or not view:
                failures.append(dict(record=ordinal,reason='unsupported view loop',expression=header))
            else:
                template=unquote(view[1]);expanded=[]
                template=re.sub(r'\$\{\s*('+LITERAL+r')\s*\}',lambda m:unquote(m[1]),template)
                for value in values:
                    path=template.replace('${'+var+'}',str(value))
                    path=re.sub(r'\$\{String\('+re.escape(var)+r'\)\.padStart\(([1-9]\d?),[\"\']0[\"\']\)\}',lambda m:str(value).zfill(int(m[1])),path)
                    if '${' in path:
                        failures.append(dict(record=ordinal,reason='unresolved view loop path'));break
                    expanded.append('image((await tools.view_image({path:'+json.dumps(path)+'})).image_url);')
                else:
                    edits.append((tokens[start].start(),tokens[end-1].end(),''.join(expanded)))
                    evidence.append(dict(record=ordinal,variable=var,values=values,views=len(expanded)))
            i=max(end,i+1)
        for a,b,replacement in reversed(edits):raw=raw[:a]+replacement+raw[b:]
        p[field]=raw
    return evidence,failures


def inspect(rollout, directory, skip_manifest=False):
    directory = Path(directory).resolve()
    records = rows(rollout) if Path(rollout).is_file() else []
    bindings, failures = resolve(records, CALL_TYPES)
    templates, pwd_evidence, template_failures = resolve_templates(records, directory)
    path_inputs={i:p.get('input',p.get('arguments','')) for i,obj in enumerate(records)
        if isinstance((p:=obj.get('payload')),dict) and p.get('name')=='exec'}
    loop_expansions, loop_failures = expand_view_loops(records)
    result = _inspect_records(records, directory, skip_manifest, path_inputs)
    allowed = []; keep = []
    for violation in result['violations']:
        path = violation.get('path', '')
        if violation['reason'] != 'absolute path outside reader_dir' or not font_path(path):
            keep.append(violation); continue
        payload = records[violation['record']]['payload']
        raw = payload.get('input', payload.get('arguments', ''))
        commands = quoted_property(raw, 'cmd') if payload.get('name') == 'exec' else []
        proofs = sum(read_proofs(cmd, path) for cmd in commands)
        if proofs and isinstance(raw, str) and raw.count(path) == proofs:
            allowed.append(dict(violation, access='read-only', proof='statically checked command operand'))
        else: keep.append(violation)
    keep.extend(failures + template_failures + loop_failures)
    if not Path(rollout).is_file(): keep.append(dict(reason='missing rollout: '+str(rollout)))
    result.update(loop_expansions=loop_expansions, violations=keep, ok=not keep, rollout=str(rollout),
        rollout_sha256=sha(rollout) if Path(rollout).is_file() else None,
        template_resolutions=bindings, v41_template_resolutions=templates,
        pwd_evidence=pwd_evidence, unresolved_loads=failures + template_failures,
        os_resource_allowances=allowed)
    result['image_match_counts'] = {kind: sum(m['match'] == kind for m in result['image_matches'])
        for kind in sorted({m['match'] for m in result['image_matches']})}
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('rollout',type=Path);p.add_argument('reader_dir',type=Path);p.add_argument('--skip-manifest',action='store_true');a=p.parse_args()
    result=inspect(a.rollout,a.reader_dir,a.skip_manifest);print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['ok'] else 2
if __name__=='__main__':sys.exit(main())
