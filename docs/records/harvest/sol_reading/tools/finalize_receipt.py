#!/usr/bin/env python3
"""Bind successful validation artifacts into the blocked/ready build receipt."""
import json,re,shutil
from common import *

def main():
    receipt=json.loads((ROOT/'BUILD_RECEIPT_B1.json').read_text());scans=json.loads((ROOT/'PACK_SCAN_B1.json').read_text());assert len(scans)==6 and all(s['ok'] for s in scans)
    tests=(ROOT/'TEST_RESULTS_B1.txt').read_text();match=re.search(r'Ran (\d+) tests',tests);assert match and tests.rstrip().endswith('OK')
    for pack in receipt['packs']:
        directory=Path(pack['path']);manifest=directory.parent/f'MANIFEST.{pack["reader"]}.json'
        pack['manifest']=str(manifest);pack['manifest_sha256']=sha(manifest)
        scan=next(s for s in scans if s['directory']==pack['path']);assert scan['manifest_sha256']==pack['manifest_sha256']
    receipt['validation']={'tests':{'passed':int(match[1]),'total':int(match[1]),'output_sha256':sha(ROOT/'TEST_RESULTS_B1.txt')},'pack_scan':{'folders':6,'passed':6,'output_sha256':sha(ROOT/'PACK_SCAN_B1.json')},'probe_scan':{'expected_exit':2,'canary_flagged':any(v.get('path','').endswith('/canary_outside.txt') for v in json.loads((ROOT/'PROBE_SCAN_B1.json').read_text())['violations']),'manifest_skipped':True,'output_sha256':sha(ROOT/'PROBE_SCAN_B1.json')},'no_readers_launched':True}
    receipt['git']['staging']='blocked: sandbox index.lock Operation not permitted';receipt['git']['after']=receipt['git']['before'];receipt['git']['commit']=None
    receipt['visual_review']={'layout_inspected':['bsb','yer','owner39'],'yer_s003':'suspect: crop appears to include terminal hard signs despite Google soft-sign label; lead pixel adjudication required; expected call retained per brief','lead_review_completed':False}
    receipt['git']['intended_commit_message']='SR-B1: Sol-reading packs, controls, scanners, mapper, ledger\n\nCo-Authored-By: gpt-6.1-sol via Codex'
    receipt['status']='BLOCKED';receipt['blockers']=receipt['choices']['control_shortfall']+['Git fast-forward and commit unavailable: sandbox denies ORIG_HEAD.lock and index.lock']
    review_out=PACK_ROOT/'control_review';review_out.mkdir(parents=True,exist_ok=True)
    receipt['control_review']={}
    for bed in FIELDS:
        for suffix in ('.png','.md'):shutil.copyfile(ROOT/'keys/control_review'/f'{bed}{suffix}',review_out/f'{bed}{suffix}')
        receipt['control_review'][bed]={'path':str(review_out/f'{bed}.png'),'sha256':sha(review_out/f'{bed}.png'),'lead_pixel_check':'pending'}
    receipt['implementation_sha256']={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'tools').glob('*.py'))}
    dump(ROOT/'BUILD_RECEIPT_B1.json',receipt)
    print(json.dumps({'status':receipt['status'],'packs':6,'tests':int(match[1]),'blockers':receipt['blockers']}))
if __name__=='__main__':main()
