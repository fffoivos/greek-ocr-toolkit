"""Execute the actual agreement_mode loop with tiny in-memory serialized inputs."""
import ast
import io
import json
from pathlib import Path
from types import SimpleNamespace
from collections import Counter

root=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck')
source=root/'scripts/labelfix/agreement_mode.py'
tree=ast.parse(source.read_text())
loop=next(x for x in tree.body if isinstance(x,ast.For))
# This is the first TOP-LEVEL for, the R1 scoring loop, not the optional flags loop.
code=compile(ast.Module(body=[loop],type_ignores=[]),str(source),'exec')
output={}
for case,flagged,detector in [('external_K1_flag',True,'acute'),('Google_agrees_R1_detector_disagrees',False,'psili')]:
    slot=dict(slot=1,recogniser_start=0,base='α',detected=[['accent','acute']],truth=[['accent','acute']])
    row=dict(line_id='synthetic',recogniser_text='ά',slots=[slot])
    env=dict(gzip=SimpleNamespace(open=lambda *a:io.StringIO(json.dumps(row)+'\n')),R1='unused',MODE='presence',
        FLAGS={('synthetic',0)} if flagged else set(),G={'synthetic':'ά'},nfd=lambda x:x,
        google_marks=lambda *a:{0:{('accent','acute')}},atomic=lambda x:set(map(tuple,x)),
        kinds=lambda m:{k for k,v in m},Counter=Counter,json=json,
        s6={'synthetic':dict(slots=[dict(slot=1,detected=[['accent' if detector=='acute' else 'breathing',detector]])])},
        c=Counter(),lines=Counter(),by_type=Counter(),rows=[])
    exec(code,env)
    output[case]={' / '.join(k):v for k,v in env['c'].items()}
dest=Path(__file__).resolve().parent/'agreement_probe.json'
dest.write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps(output,indent=2))
