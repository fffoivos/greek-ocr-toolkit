import collections,hashlib,importlib.util,json,sys
from pathlib import Path
import pytest
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D));sys.path.insert(0,str(D/'package/projects/greek-ocr-toolkit-pipe032'))
from binding_state import pending,require_bound
from flip_report import report
from bind_sf7 import pairs,load_and_validate
from greekocr.harvest.line_pipeline import canonical,identity,digest
from greekocr.harvest.line_pipeline_census import Ledger
from greekocr.harvest import admission

def write(path,obj):path.write_text(json.dumps(obj)+'\n')
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def publication(root,decisions,trains):
 root.mkdir();g=root/'generations/g1';g.mkdir(parents=True)
 for name,rs in [('decisions',decisions),('admitted_train',trains)]:
  (g/(name+'.jsonl')).write_text(''.join(json.dumps(r)+'\n' for r in rs))
 write(g/'summary.json',dict(complete=True,outputs={n:dict(sha256=hashfile(g/(n+'.jsonl'))) for n in ('decisions','admitted_train')}))
 write(root/'CURRENT.json',dict(status='completed',export_id='g1',summary_sha256=hashfile(g/'summary.json')))
 return g

def d(i,admit,status,edits=None):return dict(binding=dict(parent_id='p',id=str(i)),disposition='ADMIT' if admit else 'HOLD',routes=dict(polytonic=dict(status=status,edits=edits or [],evidence={'reason':'sf7 hold'})))
def test_flips_and_reasons(tmp_path):
 a=tmp_path/'a';b=tmp_path/'b'
 publication(a,[d(1,True,'not_applied_out_of_scope'),d(2,True,'not_applied_out_of_scope'),d(3,False,'not_applied_out_of_scope')],[dict(parent_id='p',id='1')])
 publication(b,[d(1,False,'required_evidence_unresolved'),d(2,True,'kept_unverified'),d(3,True,'applied',[{'x':1}])],[dict(parent_id='p',id='2'),dict(parent_id='p',id='3')])
 r=report(a,b,tmp_path/'out');c=collections.Counter()
 for f in r['flips']:c[f['metric'],f['reason']]+=f['rows']
 assert c=={('ADMIT','polytonic hold'):1,('ADMIT','polytonic edit'):1,('admitted_train','polytonic hold'):1,('admitted_train','polytonic edit'):1,('admitted_train','kept_unverified: sf7 hold'):1}
@pytest.mark.parametrize('case',['missing','duplicate','hash','inside'])
def test_flip_refusals(tmp_path,case):
 a=tmp_path/'a';b=tmp_path/'b';ds=[d(1,True,'kept_unverified')]
 publication(a,ds,[]);g=publication(b,[] if case=='missing' else ds+ds if case=='duplicate' else ds,[])
 if case=='hash':(g/'decisions.jsonl').write_text('changed')
 with pytest.raises((AssertionError,__import__('sqlite3').IntegrityError)):
  report(a,b,b/'out' if case=='inside' else tmp_path/'out')

def test_pending_guard():
 c=dict(corrections=[dict(tool='polytonic',parent_id='p',path='PENDING',sha256=None)])
 assert pending(c)==['p']
 with pytest.raises(ValueError,match='PENDING'):require_bound(c)
 c['corrections'][0].update(path='/real',sha256='a'*64);require_bound(c)

def test_pair_hash_size(tmp_path):
 p=tmp_path/'r';p.write_text('abc')
 assert pairs([str(p),hashfile(p)])[0]['bytes']==3
 with pytest.raises(ValueError):pairs([str(p),'0'*64])
 with pytest.raises(ValueError):pairs([str(p)])

@pytest.mark.parametrize('case',['valid','missing','extra','duplicate','wrong_digest'])
def test_sf7_coverage_loader(tmp_path,case):
 from test_pipeline_033 import row,answer
 r=row();r['parent_id']='p';versions=json.loads((D/'package/projects/greek-ocr-toolkit-pipe032/docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
 result=answer(r,'polytonic',status='kept_unverified');result.update(tool_version=versions['polytonic']['version'],tool_digest=versions['polytonic']['digest'],evidence=dict(kept_unverified=True,reason='fixture cannot verify'))
 baseline=tmp_path/'baseline';publication(baseline,[d(r['id'],True,'not_applied_out_of_scope')],[])
 ledger=Ledger(baseline/'ledger.sqlite',{})
 codec=admission.load_codec(D/'package/projects/greek-ocr-toolkit-pipe032/greekocr/_vendor/codec/v2.json')
 ledger.register(r,codec)
 if case=='extra':
  extra=dict(r,id='extra');ledger.register(extra,codec)
 ledger.db.commit();ledger.db.close()
 config=dict(parents=[dict(id='p',sha256='a'*64)])
 records=[] if case=='missing' else [result,result] if case=='duplicate' else [result]
 if case=='extra':records.append(dict(result,binding=identity(extra)))
 if case=='wrong_digest':result['tool_digest']='b'*64
 path=tmp_path/'sf7.jsonl';path.write_text(''.join(canonical(x)+'\n' for x in records))
 entries=pairs([str(path),hashfile(path)])
 if case=='valid':
  report,_=load_and_validate(entries,config,baseline,tmp_path/'work');assert report['coverage']=={'p':1};assert report['parents'][0]['status_counts']=={'kept_unverified':1}
 else:
  with pytest.raises((ValueError,__import__('sqlite3').IntegrityError)):load_and_validate(entries,config,baseline,tmp_path/'work')

def test_readout_invariant_catches_hidden_edit():
 # Exercise the exact reconstruction helper on another tool's valid edit and a hidden polytonic edit.
 spec=importlib.util.spec_from_file_location('r06',D/'readout/census_readout.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 assert m.kept_unverified_edit_violation('α x','α y',dict(status='kept_unverified',edits=[]),[dict(start=2,end=3,before='x',after='y',tools=['numerics'])]) is False
 assert m.kept_unverified_edit_violation('α x','ἀ x',dict(status='kept_unverified',edits=[]),[]) is True
 assert m.kept_unverified_edit_violation('α x','ἀ x',dict(status='kept_unverified',edits=[]),[dict(start=0,end=1,before='α',after='ἀ',tools=['polytonic'])]) is True

def test_mock_polytonic_witnesses():
 for tag in ('smoke-mode-i','smoke-mode-ii','full-mode-ii'):
  root=D/'mock_batch/W/census_06_20261020/attempts'/tag
  ds=[json.loads(s) for s in (root/'decisions.jsonl').read_text().splitlines()]
  poly=[x for x in ds if x.get('routes',{}).get('polytonic',{}).get('status')=='applied']
  assert any(x['disposition']=='ADMIT' and any('polytonic' in e['tools'] for e in x['edits']) for x in poly)
  assert any(x['disposition']=='HOLD' and x['routes']['polytonic'].get('reason')=='missing qualified tool result' for x in ds)
  assert any(x['disposition']=='HOLD' and x['routes']['polytonic'].get('evidence',{}).get('reason')=='mock detected unresolved fault' for x in ds)
  assert any(x['routes']['polytonic']['status']=='kept_unverified' for x in ds)
  rd=json.loads(Path(str(root)+'.readout/readout.json').read_text());assert all(v['status']=='PASS' for v in rd['invariants'].values());assert rd['pending']['polytonic']>0

@pytest.mark.parametrize('reason',['sf7 hold','sf7 out_of_scope','  unknown SF7 reason α  '])
@pytest.mark.parametrize('direction',[(False,True),(True,False)])
def test_exact_reason_flips_both_directions(tmp_path,reason,direction):
 before,after=direction;a=tmp_path/'a';b=tmp_path/'b'
 old=[];new=[];old_train=[];new_train=[]
 for parent in ('p','q'):
  x=d(1,before,'not_applied_out_of_scope');y=d(1,after,'kept_unverified')
  x['binding']['parent_id']=y['binding']['parent_id']=parent
  y['routes']['polytonic']['evidence']['reason']=reason
  old.append(x);new.append(y)
  member=dict(parent_id=parent,id='1')
  if before:old_train.append(member)
  if after:new_train.append(member)
 publication(a,old,old_train);publication(b,new,new_train)
 result=report(a,b,tmp_path/'out')
 assert result['flips']==[dict(parent=p,metric=m,transition=f'{int(before)} -> {int(after)}',reason='kept_unverified: '+reason,rows=1) for p in ('p','q') for m in ('ADMIT','admitted_train')]


def test_binder_exact_reason_counts_and_prior_exclusion(tmp_path):
 from test_pipeline_033 import row,answer
 versions=json.loads((D/'package/projects/greek-ocr-toolkit-pipe032/docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
 reasons=['sf7 hold','sf7 out_of_scope','  unknown SF7 reason α  ','sf7 hold']
 baseline=tmp_path/'baseline'
 ds=[d(i,True,'not_applied_out_of_scope') for i in range(len(reasons))]+[d('excluded',False,'not_run_due_to_prior_exclusion')]
 publication(baseline,ds,[]);ledger=Ledger(baseline/'ledger.sqlite',{})
 codec=admission.load_codec(D/'package/projects/greek-ocr-toolkit-pipe032/greekocr/_vendor/codec/v2.json')
 results=[]
 for i,reason in enumerate(reasons):
  r=dict(row(),parent_id='p',id=str(i));ledger.register(r,codec)
  x=answer(r,'polytonic',status='kept_unverified')
  x.update(tool_version=versions['polytonic']['version'],tool_digest=versions['polytonic']['digest'],evidence=dict(kept_unverified=True,reason=reason));results.append(x)
 ledger.register(dict(row(),parent_id='p',id='excluded'),codec)
 ledger.db.commit();ledger.db.close()
 path=tmp_path/'sf7.jsonl';path.write_text(''.join(canonical(x)+'\n' for x in results))
 result,_=load_and_validate(pairs([str(path),hashfile(path)]),dict(parents=[dict(id='p',sha256='a'*64)]),baseline,tmp_path/'work')
 assert result['coverage']=={'p':4}
 assert result['parents'][0]['status_counts']=={'kept_unverified':4}
 assert result['parents'][0]['kept_unverified_reason_counts']==dict(collections.Counter(reasons))


def test_c2a_mock_batch_both_reasons(tmp_path):
 import mock_batch
 mock_batch.main(tmp_path/'batch')
 result=json.loads((tmp_path/'batch/mock_batch_results.json').read_text())
 for tag in ('smoke-mode-i','smoke-mode-ii','full-mode-ii'):
  assert set(result[tag]['kept_unverified_reason_counts'])=={'sf7 hold','sf7 out_of_scope'}
  assert result[tag]['rows']==200 and result[tag]['complete']
 assert result['full-mode-i']['refused']


def test_real_pending_guards_refuse_without_sbatch(tmp_path):
 import os,subprocess
 env=dict(os.environ,CENSUS06_BUNDLE=str(D),W=str(tmp_path/'W'),CENSUS06_ATTEMPT='pending-test',E4_SMOKE='1',CENSUS06_PYTHON=sys.executable)
 for argv in ([sys.executable,'-B',str(D/'binding_state.py'),'--submit'],['bash',str(D/'submit_chain.sh')]):
  p=subprocess.run(argv,env=env,text=True,capture_output=True)
  assert p.returncode!=0 and 'sf7-binding PENDING' in p.stdout+p.stderr
 assert not (tmp_path/'W').exists()

@pytest.mark.parametrize('status',['failed','required_evidence_unresolved','unresolved','proposal_only','applied'])
def test_flip_existing_attribution_preserved(tmp_path,status):
 a=tmp_path/'a';b=tmp_path/'b'
 publication(a,[d(1,True,'not_applied_out_of_scope')],[dict(parent_id='p',id='1')])
 publication(b,[d(1,False,status,[{'x':1}] if status=='applied' else [])],[])
 result=report(a,b,tmp_path/'out')
 assert len(result['flips'])==2
 assert all(f['reason']==('polytonic edit' if status=='applied' else 'polytonic hold') for f in result['flips'])
