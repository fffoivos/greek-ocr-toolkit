"""Inventory saved runtime/score formats without evaluating locked M2 records."""
from collections import Counter
import gzip
import json
from pathlib import Path
import re
import subprocess

import numpy as np
from scripts.labelfix.clariden.r1_common import rows, sha256, write_json
from scripts.labelfix.sf6c_measure import EV
from scripts.labelfix.sf5_measure import baseline
from greekocr.labelfix import release_gate as gate
from scripts.labelfix.clariden import l1_common


def score_summary(records,key):
    counts=Counter();values=[];regional=0;total=0
    for r in records:
        total+=1;v=r.get(key)
        state=('missing' if key not in r else 'null' if v is None else
               'invalid' if not isinstance(v,(float,int)) or isinstance(v,bool) or not np.isfinite(v) else
               'zero' if v==0 else 'below_or_at_floor' if v<=.5 else 'above_floor')
        counts[state]+=1
        if isinstance(v,(float,int)) and not isinstance(v,bool) and np.isfinite(v):values.append(v)
        regional+=bool(r.get('recognition_evidence',{}).get('regions'))
    return dict(records=total,states=dict(counts),regional_scores=regional,
        quantiles=dict(zip(('min','p01','p05','median','p95','max'),np.quantile(values,[0,.01,.05,.5,.95,1]).tolist())) if values else {})


def audit():
    manifest=list(rows('docs/records/labelfix/spellcheck/SF3_evidence/m2_dev_manifest.jsonl'))
    allowed={r['card_id'] for r in manifest}
    dev_records={r['card_id']:dict(id=r['card_id'],label=r['google'],script_class='greek_poly') for r in manifest}
    mock_records={r['id']:r for r in rows('artifacts/labelfix_l1e/mock/source.jsonl')}
    mock_records.update({r['id']:r for r in rows('artifacts/labelfix_l1e/fixture_v4/mock/source.jsonl')})
    oldgate,oldcommon=baseline(Path('artifacts/labelfix_sf6c/before'))
    binding=dict(detector='saved',r1_sha256='saved',policy_sha256=gate.policy_binding()['sha256'])
    def dev_rows(path):
        # Extract the first id string only; never decode an excluded record.
        op=gzip.open if path.suffix=='.gz' else open
        with op(path,'rt') as f:
            for line in f:
                match=re.match(r'\{\s*"id"\s*:\s*("(?:[^"\\]|\\.)*")',line)
                if not match:raise ValueError('id must be first: '+str(path))
                if json.loads(match[1]) in allowed:yield json.loads(line)
    paths=subprocess.check_output(['rg','--files','--hidden','.cache','artifacts','docs/records/labelfix/spellcheck'],text=True).splitlines()
    inventory=[]
    for name in sorted(paths):
        p=Path(name)
        if 'SF6c_evidence' in name:continue
        if not (re.search(r'runtime[^/]*\.jsonl(\.gz)?$',name)
                or re.search(r'/shard-[^/]*-(combined|detector)\.jsonl\.gz$',name)
                or p.name=='witness_inputs.jsonl.gz'):continue
        data=dev_rows(p) if '/m2/' in name or '/m2_' in name else rows(p)
        data=list(data)
        summary=score_summary((r.get('runtime',r) for r in data),'recognition_confidence')
        effects=[];statuses={phase:Counter() for phase in ('before','after')}
        for row in data:
            rt=row.get('runtime',row);record=row.get('record') or dev_records.get(rt['id']) or mock_records.get(rt['id'])
            if rt.get('status')=='skipped':continue
            if record is None:raise ValueError('missing original label: '+rt['id'])
            modes=(row.get('mode','ENSEMBLE_AB'),) if 'runtime' in row else gate.MODES
            for mode in modes:
                a=oldcommon.overlay(record,rt,mode,binding);b=l1_common.overlay(record,rt,mode,binding)
                statuses['before'][a['status']]+=1;statuses['after'][b['status']]+=1
                if (a['status'],a.get('label'))!=(b['status'],b.get('label')):
                    assert a['status']!='hold' and b['status']=='hold'
                    effects.append(dict(id=rt['id'],mode=mode,before=a['status'],after=b['status']))
        inventory.append(dict(path=name,sha256=sha256(p),scope='DEV allowlist before decode' if '/m2/' in name or '/m2_' in name else 'all saved records',
            status_counts={k:dict(v) for k,v in statuses.items()},newly_hold=effects,**summary))
        print(name,'newly HOLD',len(effects),flush=True)
    alignments=[]
    for name in sorted(paths):
        p=Path(name)
        if not re.search(r'/align[^/]*\.jsonl(\.gz)?$|/C1_alignments\.jsonl\.gz$',name):continue
        if 'align_locked' in name:
            alignments.append(dict(path=name,sha256=sha256(p),scope='locked; not decoded'));continue
        data=dev_rows(p) if '/m2/' in name else rows(p)
        alignments.append(dict(path=name,sha256=sha256(p),scope='DEV allowlist before decode' if '/m2/' in name else 'saved alignment metadata',
            **score_summary((r.get('alignment',r) for r in data),'confidence')))
    held={r['crop'].split('/docs/',1)[-1] for r in rows('docs/records/labelfix/spellcheck/R0_evidence/continuity_666.jsonl')}
    held_scores=[]
    for r in rows('.cache/labelfix/align_s0.jsonl'):
        if r['crop'].split('/docs/',1)[-1] in held:held_scores.append(r['alignment'])
    assert len(held_scores)==666
    writers={
        'scripts/labelfix/m2_run.py':'direct Alignment confidence, image width and actual window frame scores; missing stays None',
        'scripts/labelfix/clariden/l1_detect.py':'active builder from immutable L1 reference; same certification fields as M2',
        'scripts/labelfix/clariden/l1_infer.py':'copies original fields; missing confidence becomes None with scored false provenance',
        'scripts/labelfix/clariden/l1e_run.py':'preserves original score/provenance; legacy unknown explicitly scored false',
        'scripts/labelfix/clariden/l1e_measure.py':'passes only saved metadata scores; absent metadata explicitly unknown',
        'scripts/labelfix/sf5_measure.py':'overlay recovery retains no recognition confidence; unavailable, never defaulted',
        'scripts/labelfix/sf6_measure.py':'heldout has no recognition score or B/E coverage; frozen-slot instrument only',
        'scripts/labelfix/sf4_measure.py':'saved predictions only; no recognition confidence synthesized',
        'scripts/labelfix/owner_pages_build_combined.py':'complete runtime copied or partial runtime without score; partial stays unavailable',
        'artifacts/labelfix_l1e/reference/l1_detect.py':'immutable historical builder omits score entirely; safe unavailable',
    }
    write_json(EV/'runtime_audit.json',dict(runtime_sources=inventory,alignment_sources=alignments,
        heldout_alignment_distribution=score_summary(held_scores,'confidence'),
        reviewer_runtime_distribution=score_summary((r['runtime'] for r in json.loads(Path('docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3v3_evidence/unsafe_release_witnesses.json').read_text())),'recognition_confidence'),
        writer_audit={p:dict(sha256=sha256(p),behavior=v) for p,v in writers.items()},
        locked_ii_records_decoded=0,network=False,inference_runs=0))


def archives():
    """Check packed runtime snapshots too; never extract or modify an archive."""
    import hashlib
    import tarfile
    receipt=json.loads((EV/'runtime_audit.json').read_text());packed=[]
    oldgate,oldcommon=baseline(Path('artifacts/labelfix_sf6c/before'))
    binding=dict(detector='saved',r1_sha256='saved',policy_sha256=gate.policy_binding()['sha256'])
    for name in subprocess.check_output(['rg','--files','artifacts'],text=True).splitlines():
        if not name.endswith(('.tar','.tar.gz','.tgz')):continue
        members=[]
        with tarfile.open(name,'r:*') as archive:
            files={m.name:m for m in archive.getmembers() if m.isfile()}
            originals={}
            for member,m in files.items():
                if member.endswith('/source.jsonl'):
                    for line in archive.extractfile(m).read().decode().splitlines():
                        r=json.loads(line);originals[r['id']]=r
            for member,m in files.items():
                if not re.search(r'(runtime[^/]*\.jsonl(\.gz)?$|shard-[^/]*-(combined|detector)\.jsonl\.gz$)',member):continue
                data=archive.extractfile(m).read()
                if member.endswith('.gz'):data=gzip.decompress(data)
                records=[json.loads(line) for line in data.decode().splitlines() if line.strip()]
                effects=[]
                for rt in records:
                    if rt.get('status')=='skipped':continue
                    record=originals[rt['id']]
                    for mode in gate.MODES:
                        a=oldcommon.overlay(record,rt,mode,binding);b=l1_common.overlay(record,rt,mode,binding)
                        if (a['status'],a.get('label'))!=(b['status'],b.get('label')):
                            assert a['status']!='hold' and b['status']=='hold'
                            effects.append(dict(id=rt['id'],mode=mode))
                members.append(dict(member=member,decoded_sha256=hashlib.sha256(data).hexdigest(),
                    newly_hold=effects,**score_summary(records,'recognition_confidence')))
        packed.append(dict(path=name,sha256=sha256(name),runtime_members=members))
    receipt['archive_sources']=packed
    receipt['label_sources']={p:sha256(p) for p in ('docs/records/labelfix/spellcheck/SF3_evidence/m2_dev_manifest.jsonl',
        'artifacts/labelfix_l1e/mock/source.jsonl','artifacts/labelfix_l1e/fixture_v4/mock/source.jsonl')}
    write_json(EV/'runtime_audit.json',receipt)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--archives-only',action='store_true')
    args=parser.parse_args()
    if not args.archives_only:audit()
    archives()
