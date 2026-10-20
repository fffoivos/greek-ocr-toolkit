"""Bind lead-supplied population/roles and optional R2a inputs. Does not submit."""
import argparse
import json
import math
from pathlib import Path
from scripts.labelfix.clariden.r1_common import rows, sha256, write_json
from scripts.labelfix.clariden.r2_teacher import TEACHER_SHA, ROLES
from greekocr.labelfix.release_gate import policy_binding

REMOTE=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')

from scripts.labelfix.clariden.r2_util import atomic_json as write_json

def prepare(line_list=None,roles=None,manifest=None,inventory=None,native=None,out=Path('config/r2_job.json'),external_hashes=None):
    old=REMOTE/'labelfix_r1_20261016'
    cfg=dict(schema='r2-first-job-v1',mock=False,source_commit='66e39e76+R2P2-uncommitted',policy=policy_binding(),
        data=str(old/'output_3678928/data'),heldout=str(old/'artifacts/labelfix_r1/heldout_font'),
        teacher=str(old/'output_3678928/A/best.pt'),recognizer=str(REMOTE/'greek-page-ocr/out/e3b/jobA/runs/full_s0/best.pt'),
        line_list=str(line_list) if line_list else None,roles=str(roles) if roles else None,
        manifest=str(manifest) if manifest else None,inventory=str(inventory or old/'.cache/labelfix/clariden/C1_crop_inventory.jsonl.gz'),
        excluded_documents=[],excluded_lines=[],sha256=external_hashes or {},native=native)
    exclusions=Path('artifacts/labelfix_r1/binding/exclusions.json')
    if exclusions.exists():
        groups=json.loads(exclusions.read_text())['sets'].values()
        cfg['excluded_documents']=sorted({d for g in groups for d in g['documents']})
        groups=json.loads(exclusions.read_text())['sets'].values()
        cfg['excluded_lines']=sorted({i for g in groups for i in g['line_ids']})
        cfg['sha256'][str(exclusions)]=sha256(exclusions)
    cfg['sha256'][cfg['teacher']]=TEACHER_SHA
    cfg['sha256'][cfg['recognizer']]='5f300fdac73d7479769c98e27d068039186ac193c6c4002ddfc8be511d363663'
    population=[]
    if line_list:
        if not roles:raise ValueError('R2C roles binding required')
        role_binding=json.loads(Path(roles).read_text());population=list(rows(line_list))
        allowed=role_binding['documents']
        for r in population:
            if r['role'] not in ROLES: raise ValueError('invalid population role')
            d=allowed.get(r['doc'])
            if not d or not d['eligible'] or r['role']!=d['role'] or r['source']!=d['source']: raise ValueError('population outside R2C role binding')
        expected=set(role_binding['eligible_line_ids'])
        if {r['line_id'] for r in population}!=expected or len(population)!=len(expected): raise ValueError('not ALL eligible R2C lines')
        cfg['excluded_documents']=sorted(set(cfg['excluded_documents'])|set(role_binding['excluded_documents']));cfg['excluded_lines']=sorted(set(cfg['excluded_lines'])|set(role_binding['excluded_lines']))
        for p in (line_list,roles): cfg['sha256'][str(p)]=sha256(p)
    if manifest:
        if not roles: raise ValueError('R2a requires document-role firewall')
        cfg['sha256'][str(manifest)]=sha256(manifest)
    if Path(cfg['inventory']).exists():cfg['sha256'][cfg['inventory']]=sha256(cfg['inventory'])
    # Conservative historical teacher upper rate; no GH200 claim from CPU mock.
    n=len(population);teacher_minutes=50*n/124669 if n else 50
    forecast=30+teacher_minutes;cfg['forecast']=dict(population_lines=n or None,teacher_minutes=teacher_minutes,
        train_wall_minutes=30,total_minutes=forecast,requested_minutes=math.ceil(1.5*forecast),status='bound population' if n else 'PENDING population; 124669-line planning reference')
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);write_json(out,cfg);return cfg

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ('line-list','roles','manifest','inventory','out'):ap.add_argument('--'+key,type=Path,required=key=='out')
    ap.add_argument('--external-hashes',type=Path)
    a=vars(ap.parse_args());p=a.pop('external_hashes');a['external_hashes']=json.loads(p.read_text()) if p else None
    print(json.dumps(prepare(**a)['forecast']))
