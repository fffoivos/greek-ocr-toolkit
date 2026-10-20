"""Offline synthetic boundary checks; never starts a reader or writes pack answers."""
import base64,copy,importlib.util,json,shutil,sys,tempfile
from pathlib import Path
from common import ROOT,PACK_ROOT,dump,rows
from scan_rollout_v42 import inspect
from reference_adapter import rollout_scanner
rd=PACK_ROOT/'cap1/r1'
checks=[]
with tempfile.TemporaryDirectory(prefix='cq1-validation-') as temp:
 t=Path(temp);fixture=t/'project/artifacts/cq1';fixture.mkdir(parents=True)
 (t/'project/docs/labelfix/spellcheck/R2').mkdir(parents=True)
 shutil.copytree(ROOT/'keys',fixture/'keys')
 import score_cq1 as scorer
 old=scorer.ROOT;scorer.ROOT=fixture
 key=json.loads((fixture/'keys/cap1.json').read_text());ids=key['readers']['r1']
 answers=[]
 for i in ids:
  k=key['items'][i];p=k['public'];e=k['expected']
  answers.append(dict(item_id=i,breathing=next(a for a,v in p['breathing_options'].items() if v==e['breathing']),accent=next(a for a,v in p['accent_options'].items() if v==e['accent']),confidence='high',note=''))
 ap=t/'synthetic_answers.jsonl';sp=t/'synthetic_scan.json';dump(sp,dict(ok=True,scanner_version='4.2',manifest_check_skipped=False))
 def run(a):
  ap.write_text(''.join(json.dumps(x)+'\n' for x in a));return scorer.score(ap,sp,'synthetic only','synthetic only')
 r=run(answers);assert r['qualifies'] and r['bed']['exact']==60;checks.append('60/60 exact qualifies')
 bed=[j for j,i in enumerate(ids) if not key['items'][i]['control']]
 def corrupt(a,j):
  p=key['items'][ids[j]]['public'];a[j]['accent']=next(c for c,v in p['accent_options'].items() if v=='unreadable')
 a=copy.deepcopy(answers)
 for j in bed[:3]:corrupt(a,j)
 r=run(a);assert r['qualifies'] and r['bed']['exact']==57;checks.append('57/60 qualifies')
 corrupt(a,bed[3]);r=run(a);assert not r['qualifies'];checks.append('56/60 fails')
 j=next(j for j in bed if key['items'][ids[j]]['expected']['breathing']=='none');a=copy.deepcopy(answers);a[j]['breathing']=next(c for c,v in key['items'][ids[j]]['public']['breathing_options'].items() if v=='smooth')
 r=run(a);assert not r['qualifies'] and r['bed']['invented_breathings']==1;checks.append('one invented breathing fails at 59/60')
 a=copy.deepcopy(answers)
 for j in [j for j,i in enumerate(ids) if key['items'][i]['control']][:2]:corrupt(a,j)
 assert not run(a)['valid'];checks.append('two control errors flag context and prevent qualification')
 try:run(answers[::-1]);raise RuntimeError('order not rejected')
 except AssertionError:checks.append('answer order rejected')
 scorer.ROOT=old
 # Audit fixtures test byte provenance and forbidden reads with manifest checking enabled.
 item=rows(rd/'items.jsonl')[0];blob=(rd/item['word_image']).read_bytes()
 records=[dict(payload=dict(type='function_call',name='view_image',call_id='v',arguments=json.dumps(dict(path=item['word_image'])))),dict(payload=dict(type='function_call_output',call_id='v',output=[dict(type='input_image',image_url='data:image/png;base64,'+base64.b64encode(blob).decode())]))]
 rp=t/'synthetic_rollout.jsonl'
 def scan(recs):
  rp.write_text(''.join(json.dumps(r)+'\n' for r in recs));return inspect(rp,rd)
 assert scan(records)['ok'];checks.append('v4.2 exact returned image accepted with manifest')
 bad=records+[dict(payload=dict(type='function_call',name='exec_command',arguments=json.dumps(dict(cmd='cat /private/tmp/elsewhere.json'))))]
 assert not scan(bad)['ok'];checks.append('v4.2 outside absolute read rejected')
 bad=records+[dict(payload=dict(type='function_call',name='exec',input='await tools.exec_command({cmd:"cat /System/Library/Fonts/Helvetica.ttc"})'))]
 r=scan(bad);assert r['ok'] and r['os_resource_allowances'];checks.append('v4.2 proven read-only font allowed')
 bad[-1]['payload']['input']='await tools.exec_command({cmd:"touch /System/Library/Fonts/Helvetica.ttc"})'
 assert not scan(bad)['ok'];checks.append('v4.2 font write rejected')
 dump(ROOT/'validation.json',dict(ok=True,synthetic_only=True,reader_started=False,checks=checks))
print(json.dumps(checks,indent=2))
