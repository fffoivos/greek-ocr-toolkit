"""Wave1c index bytes; no sampling or changes to MIX1B arm arithmetic.

Upstream draw_contract imports the campaign supervisor (sys.path mutation).
Execute its exact SHA check at bench/e4_wave1c.py:218-219 via AST, unchanged.
The writer uses its exact index serialization at lines 207-208 and gzip settings
at lines 182-183. Header is a separate receipt so gzip contains only index rows.
"""
from core import *
import ast, tempfile

def wave1c_check(out,indexed):
    source=Path(__file__).parent/'wave2/bench/e4_wave1c.py'
    tree=ast.parse(source.read_text())
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='draw_contract')
    check=next(n for n in fn.body if isinstance(n,ast.If) and n.lineno==218)
    require(check.end_lineno==219,'wave1c verifier source changed')
    exec(compile(ast.Module(body=[check],type_ignores=[]),str(source),'exec'),dict(out=Path(out),indexed=indexed,sha256=sha))

def write_index(path,epochs,pools):
    with open(path,'wb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as sink:
        for epoch,indexed in enumerate(epochs,1):
            for position,(c,i,ident) in enumerate(indexed):
                require(pools[c][i]['line_id']==ident,'pool identity')
                physical=pools[c][i].get('physical_index',i)
                sink.write((json.dumps([epoch,position,c,physical,ident],separators=(',',':'))+'\n').encode())

def verify_index(path,epochs,pools):
    # Re-serialize the same draw, never sample again. Upstream checks gzip SHA.
    with tempfile.TemporaryDirectory() as tmp:
        write_index(Path(tmp)/'v_c_indices.jsonl.gz',epochs,pools)
        wave1c_check(tmp,path)
