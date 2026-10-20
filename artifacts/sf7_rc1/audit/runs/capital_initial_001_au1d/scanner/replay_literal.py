"""Conservative literal-command replay. No shell evaluation; unknown syntax is skipped.
Python heredocs run in a separate, restricted interpreter with a small AST/API
allowlist and an audit hook confining Python IO to the fresh reproduction root.
The only child program is magick, with parsed options and confined PNG operands.
"""
import ast, builtins, json, os, re, subprocess, sys
from pathlib import Path
from types import SimpleNamespace
from PIL import Image, ImageDraw

ATTRS = {'loads','open','convert','height','width','new','Draw','text','paste','append','save','run','size','resize','Resampling','NEAREST','LANCZOS','BICUBIC','BILINEAR','BOX','HAMMING','read','splitlines'}
BUILTINS = {'open','range','len','enumerate','max','min','sum','str','int','print','list','dict','zip','round'}
OPTIONS = {'-background':1,'-gravity':1,'-extent':1,'+append':0,'-append':0,'-splice':1,'-font':1,'-pointsize':1,'-annotate':2,'-bordercolor':1,'-border':1,'-resize':1,'-filter':1,'-crop':1,'+repage':0}

def relative(value):
    p=Path(value)
    if p.is_absolute() or '..' in p.parts or '~' in str(p) or '\\' in str(p): raise ValueError('nonrelative path')
    return p

def parse(command):
    if 'answers.jsonl' in command: raise ValueError('answers writes/read skipped')
    # Exact shell grammar, deliberately no expansion, substitutions, pipes or redirection.
    lines=command.splitlines(); pre=[]
    while lines and lines[0].startswith('mkdir -p '):
        line=lines.pop(0); p=line[len('mkdir -p '):]
        if not re.fullmatch(r'[a-zA-Z0-9_./-]+',p): raise ValueError('nonliteral mkdir')
        pre.append(str(relative(p)))
    rest='\n'.join(lines)
    if not rest: return pre,None
    if rest=='cat items.jsonl': return pre,None
    m=re.fullmatch(r"(?:python|python3) - <<'([A-Za-z_]+)'\n(.*)\n\1\s*",rest,re.S)
    if not m: raise ValueError('unsupported/nonliteral shell command')
    code=m[2]; tree=ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node,(ast.Import,ast.ImportFrom)):
            if isinstance(node,ast.Import):
                if any(a.name not in ('json','subprocess') or a.asname for a in node.names): raise ValueError('unsupported import')
            elif node.module!='PIL' or any(a.name not in ('Image','ImageDraw') or a.asname for a in node.names): raise ValueError('unsupported import')
        if isinstance(node,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef,ast.Lambda,ast.With,ast.Try,ast.Raise,ast.Delete,ast.Global,ast.Nonlocal,ast.While)):
            raise ValueError('unsupported Python statement')
        if isinstance(node,ast.Attribute) and node.attr not in ATTRS: raise ValueError('unsupported attribute: '+node.attr)
        if isinstance(node,ast.Name) and node.id.startswith('__'): raise ValueError('dunder name')
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id not in BUILTINS: raise ValueError('unsupported call: '+node.func.id)
        if isinstance(node,ast.Constant) and isinstance(node.value,str):
            # Literal path attempts rejected even if unreachable.
            if node.value.startswith(('/', '~')) or '..' in node.value.split('/') or '://' in node.value: raise ValueError('nonrelative literal')
    return pre,code

def worker(root,command):
    pre,code=parse(command); root=Path(root).resolve(); os.chdir(root)
    for p in pre: (root/p).mkdir(parents=True,exist_ok=True)
    if code is None:return
    def confined(path):
        if isinstance(path,int):return
        p=Path(os.fsdecode(path)); resolved=(root/p).resolve()
        if not resolved.is_relative_to(root):raise ValueError('path escape')
    def magick(args,**kw):
        if not isinstance(args,list) or not args or args[0]!='magick' or set(kw)-{'check'}:raise ValueError('unsupported subprocess')
        i=1
        while i<len(args):
            a=args[i]
            if not isinstance(a,str):raise ValueError('nonstring magick arg')
            if a in ('(',')'):i+=1;continue
            if a in OPTIONS:
                n=OPTIONS[a]
                for v in args[i+1:i+1+n]:
                    if not isinstance(v,str) or any(c in v for c in ('/','\\',':','@','`','$','\n')):raise ValueError('unsafe magick option')
                if len(args[i+1:i+1+n])!=n:raise ValueError('missing magick option')
                i+=1+n;continue
            confined(a)
            if not re.fullmatch(r'(?:img|zoom)/[A-Za-z0-9_.-]+\.png',a):raise ValueError('unsupported magick operand')
            i+=1
        return subprocess.run(args,check=kw.get('check',False),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
    def audit(event,args):
        if event=='open':confined(args[0])
        elif event in ('os.mkdir','os.remove','os.rmdir','os.chdir','os.chmod','os.utime'):confined(args[0])
        elif event.startswith(('socket.','os.system','os.exec','os.spawn','os.link','os.symlink','os.rename','ctypes.')):raise ValueError('forbidden audit event '+event)
        elif event=='subprocess.Popen':
            if args[0]!='magick':raise ValueError('forbidden program')
    def imports(name,*args,**kw):
        if name=='json':return json
        if name=='subprocess':return SimpleNamespace(run=magick)
        if name=='PIL':return SimpleNamespace(Image=Image,ImageDraw=ImageDraw)
        raise ValueError('forbidden import')
    safe={k:getattr(builtins,k) for k in BUILTINS};safe['__import__']=imports
    Image.init()
    ImageDraw.Draw(Image.new('RGB',(1,1))).text((0,0),'x')
    compiled=compile(code,'<literal-replay>','exec')
    sys.addaudithook(audit)
    exec(compiled,{'__builtins__':safe})

if __name__=='__main__':
    worker(sys.argv[1],sys.stdin.read())
