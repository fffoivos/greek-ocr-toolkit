"""Create bounded fixtures and execute the exact R2a sbatch entry point offline."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import numpy as np
from PIL import Image
from scripts.labelfix.clariden.r2_mock import prepare as old_prepare
from scripts.labelfix.clariden.r1_common import rows,sha256,write_rows,write_json
from greekocr.labelfix.release_gate import policy_binding


def prepare(out):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
    import torch
    from scripts.labelfix.clariden.r1_model import MarkReader
    torch.manual_seed(20261016)
    checkpoint=out/'mock_teacher.pt';torch.save(dict(arm='A',model=MarkReader(True).state_dict()),checkpoint)
    old=old_prepare(out/'old',checkpoint,Path('tests/labelfix/fixtures/r2/r1_train_3678928.py'))
    cfg=dict(mock=True,source_commit='R2J2-bounded-mock',policy=policy_binding(),data=old['data'],heldout=old['heldout'],
        teacher=old['teacher'],recognizer=old['recognizer'],seeds=[20261016,20261017,20261018],expected_slots=4,expected_dev_lines=1,expected_dev_items=4)
    write_json(out/'roles.json',dict(documents={'native:0':dict(role='supervision'),'witness:0':dict(role='witness')}));cfg['roles']=str(out/'roles.json')
    inventory=list(rows(old['inventory']));cohorts={};aligns={}
    for i,name in enumerate(('native','witness','dev')):
        p=out/f'docs/harvest/mock-r2a/crops/{name}.png';p.parent.mkdir(parents=True,exist_ok=True)
        with Image.open(out/'old/crop-0.png') as im:
            im.putpixel((0,0),100+i);im.save(p)
        h=sha256(p);lid=f'{name}-0';text='α'*8
        row=dict(id=lid,line_id=lid,doc=f'{name}:0',source=name,role='train' if name=='native' else 'witness',crop=str(p),image=str(p),crop_sha256=h,recogniser_text=text)
        cohorts[name]=row;selection=out/f'{name}.jsonl';write_rows(selection,[row]);cfg[name]=str(selection)
        ap=out/f'{name}_alignments.jsonl';write_rows(ap,[dict(crop=str(p),alignment=dict(prediction=text,confidence=.99,spans=[['α',j,j+1,j*18+4,j*18+15] for j in range(8)]))]);cfg[name+'_alignments']=str(ap)
        inventory.append(dict(crop=str(p),sha256=h))
    manifest=[dict(slot_id=[cohorts['native']['crop_sha256'],i],line_id='native-0',doc='native:0',source='native',role='train',provenance='native_print',targets=y,unknown=[],loss_weight=1,pool='native') for i,y in enumerate(([0,0,0,0],[1,1,0,0],[2,3,0,1],[0,1,1,0]))]
    write_rows(out/'manifest.jsonl',manifest);cfg['manifest']=str(out/'manifest.jsonl')
    write_rows(out/'inventory.jsonl',inventory);cfg['inventory']=str(out/'inventory.jsonl')
    w=cohorts['witness'];write_rows(out/'witness_key.jsonl',[dict(card_id='w0',line_id=w['id'],doc=w['doc'],crop_sha256=w['crop_sha256'],crop_letter_offset=0,mining_key='α'*8,slice='subscript',anchor_index=0,target_head='subscript')])
    write_rows(out/'eligible.jsonl',[dict(id=w['id'],label='α'*8)])
    write_rows(out/'witness_truth.jsonl',[dict(card_id='w0',printed_form='α'*8,control=False,letter_heads=[dict(index=i,base='α',breathing='none',accent='none',diaeresis='none',subscript='none') for i in range(8)])])
    write_rows(out/'dev_truth.jsonl',[dict(type='item',id=f'd{i}',line_id='dev-0',wave='mock',control=i==2,status='resolved' if i!=3 else 'unadjudicated',truth='αα' if i!=3 else None,start=2*i,end=2*i+2,weight=2,selection='mock',scoring_policy='ordinary',in_cut=i!=3) for i in range(4)])
    truth=[]
    for r in rows(Path(old['heldout'])/'lines.jsonl.gz'):
        truth.append(dict(line_id=r['id'],doc=r['doc'],dev=False,recogniser_text=r['recogniser_text'],
            slots=[dict(slot=j,base='α',truth=[],bbox=[j*18+4,12,j*18+15,30]) for j in range(8)],
            recogniser_slots=[dict(start=j,base='α',component_slot=j,locator_span=[j*18+4,j*18+15],parts=[],word=0) for j in range(8)]))
    write_rows(out/'heldout_truth.jsonl',truth);write_json(out/'overlay.json',dict(version='mock',entries=[]))
    for k in ('witness_key','eligible','witness_truth','dev_truth','heldout_truth'):cfg[k]=str(out/(k+'.jsonl'))
    cfg['overlay']=str(out/'overlay.json')
    cfg['checkpoints']={name:dict(path=old['teacher'],sha256=sha256(old['teacher'])) for name in ('A16','BASEs17','BASEs18')}
    cfg['sha256']={v:sha256(v) for k,v in cfg.items() if isinstance(v,str) and Path(v).is_file()}
    for k in ('data','heldout'):
        p=str(Path(cfg[k])/'extraction_receipt.json');cfg['sha256'][p]=sha256(p)
    write_json(out/'config.json',cfg);return cfg


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();prepare(a.out/'inputs')
    env={**os.environ,'R2_MOCK':'1','R2_PYTHON':sys.executable,'R2_CONFIG':str((a.out/'inputs/config.json').resolve()),'R2_OUT':str((a.out/'run').resolve())}
    subprocess.run(['bash','scripts/labelfix/clariden/r2a_job.sbatch'],env=env,check=True)
    root=a.out/'run';rr=json.loads((root/'run_receipt.json').read_text());assert rr['complete']
    for stage in 'ABCD':
        receipt=json.loads((root/f'stage_{stage}.json').read_text());assert receipt['complete'] and receipt['binding']==rr['binding']
        for p,h in receipt['sha256'].items():assert sha256(root/p)==h
    write_json(a.out/'mock_receipt.json',dict(complete=True,entrypoint='scripts/labelfix/clariden/r2a_job.sbatch',stages=list('ABCD'),arms=6,network=False,submitted=False))
    print('R2A_MOCK_PASS')

if __name__=='__main__':main()
