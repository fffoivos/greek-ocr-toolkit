"""Parameterised L1/C1 -> L1E -> frozen SF7-A -> RB7; never submits."""
from __future__ import annotations
import argparse,json,os,subprocess,sys,time
from pathlib import Path
from collections import Counter
from scripts.labelfix.clariden.l1_common import rows,sha256,write_json,write_rows
from scripts.labelfix.clariden.r1_common import crop_path,canonical_line,canonical_doc
from scripts.labelfix.clariden import tr2_recompose,tr2_convert
from scripts.labelfix import release_gate_sf7 as gate

POLICY='f41e05636d165f1d15edbdb4f2bb6c1aa46721962a96302be8c4dce7ce305047'

def checked(path,wanted):
 if sha256(path)!=wanted:raise ValueError('SHA mismatch '+str(path))

def command(script,*args):
 cmd=[sys.executable,'-B','-u','scripts/labelfix/clariden/'+script+'.py',*map(str,args)]
 print('ENTRYPOINT',json.dumps(cmd),flush=True);subprocess.run(cmd,check=True)

def intake(cfg,out,dry=False):
 from PIL import Image
 from concurrent.futures import ThreadPoolExecutor
 selections={};identities={};summary={}
 for split,c in cfg['splits'].items():
  checked(c['source'],c['sha256']);checked(c['ids'],c['ids_sha256'])
  selected=[r for r in rows(c['source']) if r['script_class']=='greek_poly']
  ids=[r['id'] for r in selected];docs={canonical_doc(r['doc']) for r in selected}
  assert len(selected)==c['lines'] and len(set(ids))==len(ids)
  assert len({canonical_line(i) for i in ids})==len(ids)
  assert len({r['crop'] for r in selected})==len(ids)
  assert sorted(ids)==Path(c['ids']).read_text().splitlines()
  identities[split]=(set(map(canonical_line,ids)),docs)
  selections[split]=selected
  # All crop paths must exist, including Wikisource. Full run hashes/decodes all.
  assert all(crop_path(r['crop'],cfg['crop_root'],'e3').is_file() for r in selected)
  sample=selected[:250] if dry else selected
  def inspect(r):
   p=crop_path(r['crop'],cfg['crop_root'],'e3')
   with Image.open(p) as im:im.load();size=list(im.size)
   return dict(id=r['id'],crop=r['crop'],path=str(p),sha256=sha256(p),bytes=p.stat().st_size,size=size)
  with ThreadPoolExecutor(max_workers=4) as pool:inventory=list(pool.map(inspect,sample))
  dest=out/split;dest.mkdir();write_rows(dest/'selection.jsonl',sample)
  write_rows(dest/'crop_inventory.jsonl',inventory)
  summary[split]=dict(population=len(selected),checked_images=len(inventory),parent_sha256=c['sha256'],
   selection_sha256=sha256(dest/'selection.jsonl'),inventory_sha256=sha256(dest/'crop_inventory.jsonl'))
 a,b=identities.values();assert not a[0]&b[0] and not a[1]&b[1]
 train=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/artifacts/labelfix_l1/binding/selection.jsonl')
 checked(train,'ee6c51bdeb9131fd65361d060fd34b77823c1321d3a77849581cfaa577bd3eec')
 trainrows=list(rows(train));ti={canonical_line(r['id']) for r in trainrows};td={canonical_doc(r['doc']) for r in trainrows}
 for ids,docs in identities.values():assert not ids&ti and not docs&td
 legacy=json.loads(Path('config/tr2_legacy_binding.json').read_text())
 for name,h in legacy['source_sha256'].items():checked(Path('legacy_l1')/name,h)
 for name,h in legacy['assets'].items():checked(name,h)
 for key in ('checkpoint',):checked(cfg[key],cfg[key+'_sha256'])
 checked(Path(cfg['checkpoint']).with_suffix('.safetensors'),cfg['safetensors_sha256'])
 for v in cfg['checkpoints'].values():checked(v['path'],v['sha256'])
 for p,h in cfg['historical_forward_sha256'].items():checked(p,h)
 assert gate.policy_binding()['sha256']==POLICY
 receipt=dict(complete=True,mode='real-input-login-preflight' if dry else 'production-intake',splits=summary,
  lines=sum(s['checked_images'] for s in summary.values()),all_population_crop_paths_exist=True,
  canonical_line_document_split_and_train_disjoint=True,policy_digest=POLICY,checkpoints=cfg['checkpoints'],
  gpu_stages_pending=['C1 fresh alignment/scored frames','S6 detector needs new alignments','reader A/B/E','SF7-A/RB7 need new runtime'] if dry else [],
  model_forward_passes=0,preregistration_sha256=gate.PREREGISTRATION_SHA256)
 write_json(out/'intake_receipt.json',receipt);return selections,receipt

def infer_split(cfg,c,base,selected,dry=False):
 from scripts.labelfix.clariden import tr2_l1_detect,l1e_windows,l1e_run
 selection=base/'selection.jsonl';n=len(selected);historical=base/'l1';historical.mkdir()
 binding_dir=base/'binding';binding_dir.mkdir()
 binding=dict(detector='s6',detector_commit='efdf5756',code_commit='TR2-source-bound',r1_sha256=cfg['checkpoints']['A']['sha256'],
  source_sha256=c['sha256'],ctc_sha256=cfg['checkpoint_sha256'],ctc_safetensors_sha256=cfg['safetensors_sha256'])
 write_json(binding_dir/'binding.json',binding)
 inp=dict(source_sha256=c['sha256'],exclusions={'purpose':'heldout correction only; no training; split/train disjoint'},
  out_of_scope='script_class != greek_poly',r0_policy='all raw greek_poly including wikisource',input_documents_sha256=__import__('hashlib').sha256(json.dumps(sorted({r['doc'] for r in selected})).encode()).hexdigest())
 write_json(historical/'input_receipt.json',inp)
 saved=cfg.get('dry_saved_alignments',{}).get(base.name) if dry else None
 if saved:
  ap=Path(saved);summary=json.loads((ap/'summary.json').read_text());b=summary['binding']
  assert b['selection_sha256']==sha256(selection) and b['checkpoint_sha256']==cfg['checkpoint_sha256']
  assert b['checkpoint_safetensors_sha256']==cfg['safetensors_sha256'] and b['lines']==n
  assert summary['counts']['aligned']==n and not summary['counts'].get('failed',0)
  checked(ap/'C1_alignments.jsonl.gz',summary['output_sha256'])
  alpath=ap/'C1_alignments.jsonl.gz'
 else:
  command('tr2_c1_run','--selection',selection,'--checkpoint',cfg['checkpoint'],'--crop-root',cfg['crop_root'],
   '--crop-layout','e3','--out',historical/'alignment','--device','cpu' if dry else 'cuda','--workers',1 if dry else 4,'--threads',4 if dry else 8,'--batch-size',16,'--chunk-size',512,*(['--dry-run'] if dry else []))
  alpath=historical/'alignment/C1_alignments.jsonl.gz'
 if not saved:assert json.loads((historical/'alignment/summary.json').read_text())['counts']['aligned']==n
 command('tr2_legacy_detect','--selection',selection,'--alignments',alpath,'--out',historical/'detector','--crop-root',cfg['crop_root'],'--workers',2 if dry else 64)
 # Archived L1 detector deliberately omits confidence/image-width fields.
 # Fresh C1 scored alignments stay separate; never upgrade the SF7 train contract.
 from scripts.labelfix.clariden import tr2_l1_infer
 tr2_l1_infer.run(historical/'detector',cfg['checkpoints']['A']['path'],historical/'combined','cpu' if dry else 'cuda:0')
 write_json(historical/'run_receipt.json',dict(complete=True,lines=n,binding_sha256=sha256(binding_dir/'binding.json'),
  step_receipts={str(p.relative_to(historical)):sha256(p) for p in historical.rglob('*receipt.json')}))
 windows=l1e_windows.audit(historical/'detector',selection,base/'windows_receipt.json',workers=4)
 code={str(p):sha256(p) for p in Path('scripts/labelfix/clariden').glob('tr2_*.py')}
 l1e_run.infer(historical,windows,cfg['checkpoints'],base/'ensemble',code,device='cpu' if dry else 'cuda:0')
 # Reuse L1F's exact scored-record constructor on C1's already scored forward.
 from greekocr.labelfix.ctc_align import Alignment
 from scripts.labelfix.clariden.l1f_run import make_record
 from scripts.labelfix.clariden.c1_common import crop_key
 bycrop={crop_key(r['crop']):r['alignment'] for r in rows(alpath)};byid={r['id']:r for r in selected}
 counts=Counter(); alignment_sha=sha256(alpath)
 image_widths={r['id']:r['size'][0] for r in rows(base/'crop_inventory.jsonl')}
 def scores():
  for path in sorted((historical/'detector').glob('*-detector.jsonl.gz')):
   for runtime in rows(path):
    r=byid[runtime['id']];saved=bycrop[crop_key(r['crop'])];al=Alignment.from_record(saved)
    record,cc,rr=make_record(r['id'],saved,runtime,al,image_widths[r['id']],dict(schema='l1f-frame-evidence-v1',
     checkpoint_sha256=cfg['checkpoint_sha256'],safetensors_sha256=cfg['safetensors_sha256'],source_alignment_sha256=alignment_sha))
    assert record['provenance']['alignment_identity_match'] and al.frame_confidences is not None
    counts.update(cc);yield record
 write_rows(base/'recogniser_scores.jsonl.gz',scores())
 assert counts['lines']==n
 write_json(base/'scores_receipt.json',dict(complete=True,lines=n,counts=dict(counts),
  sha256=sha256(base/'recogniser_scores.jsonl.gz'),separate_from_composer=True,reused_C1_scored_forward=True))
 config=dict(lines=n,input_run=str(historical),selection=str(selection),binding_dir=str(binding_dir),source=c['source'],ensemble_run=str(base/'ensemble'),verification_only=False)
 cp=base/'recompose.json';write_json(cp,config)
 tr2_recompose.recompose(cp,base/'sf7',workers=2 if dry else 32)
 return tr2_convert.release(c['source'],selection,base/'sf7/release/overlay_A.jsonl.gz',base,base.name,'LOGIN_DRYRUN' if dry else os.environ['SLURM_JOB_ID'])

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--config',default='config/tr2_job.json');ap.add_argument('--out',type=Path,required=True)
 ap.add_argument('--mock',action='store_true');ap.add_argument('--dry-run',action='store_true')
 ap.add_argument('--saved-test-alignment',type=Path);ap.add_argument('--saved-dev-alignment',type=Path);a=ap.parse_args()
 a.out=a.out.resolve();a.out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
 if a.mock:
  c=json.loads(Path('config/sf7_mock.json').read_text());tr2_recompose.recompose('config/sf7_mock.json',a.out/'sf7',workers=1)
  r=tr2_convert.release(c['source'],c['selection'],a.out/'sf7/release/overlay_A.jsonl.gz',a.out,'test','MOCK')
  result=dict(complete=True,mock=True,scope='saved inference fixture -> exact SF7-A and RB7; inference code not executed',conversion=r)
 else:
  cfg=json.loads(Path(a.config).read_text())
  if a.saved_test_alignment or a.saved_dev_alignment:
   assert a.dry_run
   cfg['dry_saved_alignments']={s:str(p) for s,p in (('test',a.saved_test_alignment),('dev',a.saved_dev_alignment)) if p}
  if not a.dry_run:
   import torch
   assert os.environ.get('SLURM_JOB_ID') and torch.cuda.device_count()==4
  selections,receipt=intake(cfg,a.out,a.dry_run)
  releases={split:infer_split(cfg,c,a.out/split,list(rows(a.out/split/'selection.jsonl')),dry=a.dry_run) for split,c in cfg['splits'].items()}
  result=dict(complete=True,dry_run=a.dry_run,intake=receipt,inference_executed=True,
   release_id='sf7_rc1_test_edits_A',releases=releases,status='candidate_pre_audit',bound=False)
 result.update(elapsed_seconds=time.monotonic()-started,submitted=False)
 write_json(a.out/'receipt.json',result);print(json.dumps(result,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
