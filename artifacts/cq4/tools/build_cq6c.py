"""Assemble a new CQ6C attempt. Never mutate CQ6, CQ4 truth, or remote state."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
CQ = ROOT / 'artifacts/cq4'
P = CQ / 'cq6c_package'
FROZEN = CQ / 'cq6_package'
PREREG = '7cb5a6fb53a4b5c35a55e85cce9a14961570b4a880cc79a6e4f227b9149f6964'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(p):
    return json.loads(p.read_text())

def rows(p):
    return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]

def dump(p, x):
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n')

def write_rows(p, rr):
    p.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rr))

def sid(r):
    return tuple(r['slot_id'])

def polarity(r):
    assert r['breathing'] in ('none', 'smooth', 'rough')
    assert r['accent'] in ('none', 'acute', 'grave', 'circumflex')
    return 'negative' if (r['breathing'], r['accent']) == ('none', 'none') else 'positive'

def snapshot():
    pp = list(FROZEN.rglob('*')) + [CQ/'CQ6_HANDOFF.md', CQ/'CQ6_STOPPED_BUNDLE.tar', CQ/'CQ6_STOPPED_BUNDLE.sha256']
    return {str(p.relative_to(CQ)): sha(p) for p in pp if p.is_file()}

def main():
    frozen_before = snapshot()
    assert not (P/'assembly_receipt.json').exists(), 'new attempt only; refuse overwrite'
    for d in ('data', 'evidence', 'slurm'):
        (P/d).mkdir(parents=True, exist_ok=True)
    assert sha(CQ/'R2A2_PREREGISTRATION.md') == PREREG
    # Copy only explicitly named parent evidence, not obsolete CQ6 receipts or stubs.
    for name in ('config.json', 'r1_train.py', 'r1_common.py', 'r1_extract.py',
                 'r1_model.py', 'r2_manifest.py', 'r2a_run.py', 'r2a_job.sbatch',
                 'r2_score.py', 'r2a_digest.py', 'source_provenance.json',
                 'old_extraction_receipt.json', 'old_overlap.json',
                 *(f'run_binding_{s}.json' for s in (20261016, 20261017, 20261018))):
        shutil.copyfile(FROZEN/'evidence'/name, P/'evidence'/name)
    sources = {'R2A2_PREREGISTRATION.md':'R2A2_PREREGISTRATION.md',
        'aggregate_receipt.json':'evidence/aggregate_receipt.json',
        'cq7/import_receipt.json':'evidence/cq7_import_receipt.json',
        'cq6_preregistration_binding.json':'data/preregistration_binding.json',
        'build_hashes.json':'evidence/build_hashes.json',
        'keys/topup_selected.jsonl':'data/topup_frozen_order.jsonl',
        'keys/wcap_selected.jsonl':'data/wcap_frozen_selection.jsonl',
        'truth/topup.jsonl':'data/topup_all_resolved.jsonl',
        'truth/wcap.jsonl':'data/wcap_truth.jsonl'}
    for src, dst in sources.items():
        shutil.copyfile(CQ/src, P/dst)
    for src, dst in (('data/r2a_slots_v2.jsonl','data/r2a_slots_v2.jsonl'),
                     ('data/old_pool_reference.json','data/old_pool_reference.json'),
                     ('evaluate.py','evaluate.py'), ('test_instrument.py','test_instrument.py'),
                     ('EVALUATION.md','EVALUATION.md')):
        shutil.copyfile(FROZEN/src, P/dst)
    (P/'EVALUATION.md').write_text((P/'EVALUATION.md').read_text().replace('CQ6 training','CQ6C training').replace('this stopped\npackage','this assembly\npackage'))
    build_hashes = load(P/'evidence/build_hashes.json')
    for name in ('topup', 'wcap'):
        copied = P/'data'/('topup_frozen_order.jsonl' if name=='topup' else 'wcap_frozen_selection.jsonl')
        assert sha(copied) == build_hashes[f'keys/{name}_selected.jsonl']
    ag = load(P/'evidence/aggregate_receipt.json')
    imp = load(P/'evidence/cq7_import_receipt.json')
    assert imp['accepted'] == imp['positives'] == ag['cq7']['accepted'] == 98
    assert ag['cq6_amendment1a_binding']['current_preregistration_sha256'] == PREREG
    tt = rows(P/'data/topup_all_resolved.jsonl')
    ww = rows(P/'data/wcap_truth.jsonl')
    vv = rows(P/'data/r2a_slots_v2.jsonl')
    ss = rows(P/'data/topup_frozen_order.jsonl')
    assert len(tt) == len({sid(r) for r in tt}) == 1107
    assert len(ww) == 281 and len(vv) == 1572 and len(ss) == 1205
    assert len({sid(r) for r in ss}) == len(ss)
    assert sha(P/'data/r2a_slots_v2.jsonl') == '20b24e0fa6831487568d3bf00bac928e0fcd94831db566c520535a8216a855e1'
    assert sum(r['truth_tier']=='C_sol_two_independent_CQ7_agreed' for r in tt)==98
    assert all(polarity(r)=='positive' for r in tt if r['truth_tier']=='C_sol_two_independent_CQ7_agreed')
    assert Counter(polarity(r) for r in tt) == {'negative':720, 'positive':387}
    assert not {sid(r) for r in tt} & {sid(r) for r in vv}
    assert not {r['doc'] for r in tt} & {r['doc'] for r in ww}
    alias = lambda d: d.removesuffix(':human').split(':')[-1]
    witness_docs={alias(r['doc']) for r in ww}
    assert not witness_docs & {alias(r['doc']) for r in vv}
    assert not witness_docs & {alias(d) for d in load(P/'evidence/old_extraction_receipt.json')['document_split']['train']}
    truth={sid(r):r for r in tt}
    assert set(truth) <= {sid(r) for r in ss}
    caps=Counter(r['polarity'] for r in vv if r['slice']=='capitals')
    assert caps == {'negative':214,'positive':127}
    needs={'negative':800-caps['negative'], 'positive':500-caps['positive']}
    chosen=[]; selected_counts=Counter()
    for order, x in enumerate(ss):
        if sid(x) not in truth:
            continue
        r=truth[sid(x)]; pol=polarity(r)
        if selected_counts[pol] >= needs[pol]:
            continue
        assert x['role']==r['role']=='train'
        assert all(x[k]==r[k] for k in ('line_id','doc','source'))
        selected_counts[pol]+=1
        chosen.append(dict(slot_id=r['slot_id'],line_id=r['line_id'],doc=r['doc'],source=r['source'],
            role='train',provenance='native_print',targets=[('none','smooth','rough').index(r['breathing']),
            ('none','acute','grave','circumflex').index(r['accent']),None,None],
            unknown=['diaeresis','subscript'],loss_weight=1,pool='native',slice='capitals',polarity=pol,
            teacher_seen_document=r['teacher_seen_document'],truth_tier=r['truth_tier'],
            truth_scope='CQ4 breathing/accent only',overlay_action=r['overlay_action'],
            page=x['page'],frozen_selection_rank=order))
    total={k:caps[k]+selected_counts[k] for k in needs}
    status='ready' if total=={'negative':800,'positive':500} else 'stopped'
    write_rows(P/'data/topup_assembled.jsonl',chosen)
    write_rows(P/'data/overlay_assembled.jsonl',vv+chosen)
    chosen_ids={sid(r) for r in chosen}
    write_rows(P/'data/topup_unused_resolved.jsonl',[r for r in tt if sid(r) not in chosen_ids])
    guard=[dict(arm='R2a-2',set='W-CAP',slot_id=r['slot_id'],line_id=r['line_id'],doc=r['doc'],
        reason='exposed_to_witness_selection',trained_on=False,exclude_from_fresh_final_capitals_readout=True,
        resolved=sid(r) in {sid(x) for x in ww}) for r in rows(P/'data/wcap_frozen_selection.jsonl')]
    write_rows(P/'data/lqb_in_sample_guard.jsonl',guard)
    guard += [dict(arm='R2a-2',set='planned_training_overlay',slot_id=r['slot_id'],line_id=r['line_id'],doc=r['doc'],
        reason='planned_training_identity',trained_on=False,planned_training=True,
        exclude_from_fresh_final_capitals_readout=True) for r in vv+chosen]
    write_rows(P/'data/lqb_guard.jsonl',guard)
    bindings=[load(P/f'evidence/run_binding_{s}.json') for s in (20261016,20261017,20261018)]
    remote=(P/'evidence/clariden_readonly_20261019.txt').read_text()
    assert '3683130|labelfix_R2a|normal|01:21:00|' in remote
    assert 'MaxTime=01:30:00' in remote
    for name in ('r1_train.py','r1_common.py','r1_model.py','r1_extract.py'):
        for b in bindings:
            assert sha(P/'evidence'/name)==b['file_sha256']['scripts/labelfix/clariden/'+name]
        assert sha(P/'evidence'/name)+'  scripts/labelfix/clariden/'+name in remote
    for name in ('r2_manifest.py','r2a_run.py'):
        assert sha(P/'evidence'/name)+'  scripts/labelfix/clariden/'+name in remote
    assert sha(P/'evidence/config.json')+'  config/r2a_job.json' in remote
    for seed,b in zip((20261016,20261017,20261018),bindings):
        assert b['runtime']['job_id']=='3683130'
        assert sha(P/f'evidence/run_binding_{seed}.json')+f'  output_3683130/C/{seed}/run_binding.json' in remote
    recipe=load(FROZEN/'recipe_equivalence.json')
    assert recipe['parameter_fields']==19 and recipe['changed']==0
    recipe['scope']='intended CQ6C recipe only; no training executed; admission pending'
    recipe['actual_parameters_by_seed']={str(s):b['parameters'] for s,b in zip((20261016,20261017,20261018),bindings)}
    for b in bindings:
        assert len(b['parameters'])==19
        assert {k:v for k,v in b['parameters'].items() if k not in ('seed','sampler_seed')} == {k:v for k,v in bindings[0]['parameters'].items() if k not in ('seed','sampler_seed')}
    dump(P/'recipe_equivalence.json',recipe)
    table=['# CQ6C parameters versus actual R2a job 3683130','',
        '19 bound parameters, 0 intended changes. Three seeds: 20261016/17/18. No new training measurement.',
        '', '| Parameter | Actual R2a | Intended CQ6C | Changes |','|---|---|---|---|']
    for k,v in bindings[0]['parameters'].items():
        value={str(s):b['parameters'][k] for s,b in zip((20261016,20261017,20261018),bindings)} if k in ('seed','sampler_seed') else v
        text=json.dumps(value).replace('|','\\|')
        table.append(f'| {k} | `{text}` | same | 0 |')
    table+=['','## Effective settings','', '| Setting | Actual R2a | Intended CQ6C |','|---|---|---|']
    for k,v in recipe['effective_settings'].items():
        table.append(f'| {k} | `{json.dumps(v)}` | same |')
    table+=['','The pool intervention changes sampler exposure and steps per epoch naturally. No partial-head loss or teacher-label fill is authorized. See HEADS_AND_ADMISSION.md.',
        '', '| Data/resource surface | R2a | CQ6C |','|---|---|---|',
        '| Old pool | 1,935,016 rows, 5 excess duplicates | identical reference, order and duplicates |',
        '| v2 overlay | 1,572 | byte-identical |',
        f'| Capital slice | 214 negative / 127 positive | {total["negative"]} / {total["positive"]} assembled |',
        f'| Top-up | absent | {len(chosen)} proposals; UNKNOWN heads retained |',
        '| W-CAP | absent | 281/300, witness only |',
        '| Job kinds | combined normal / 01:21:00 | prepare/train/evaluate explicitly normal / 01:21:00; combined limit inherited, not separately measured |',
        '| Smoke | no parent debug job | debug / 01:21:00; semantic only, explicit partition override |',
        '', '## Every parent config leaf','', '| Parent config field | Actual value | CQ6C disposition |','|---|---|---|']
    def leaves(d,prefix=''):
        if isinstance(d,dict):
            for k,v in d.items():
                yield from leaves(v,f'{prefix}.{k}' if prefix else k)
        else:
            yield prefix,d
    for k,v in leaves(load(P/'evidence/config.json')):
        disposition='frozen reference; no new runtime config claimed'
        if k=='seeds': disposition='unchanged'
        if k=='manifest': disposition='data/overlay_assembled.jsonl is a proposal, not admitted training input'
        table.append(f'| {k} | `{json.dumps(v)}` | {disposition} |')
    (P/'PARAMETERS_VS_R2A.md').write_text('\n'.join(table)+'\n')
    receipt=dict(attempt='CQ6C',status=status,status_scope='assembly and coordinator review only; NOT training admission',
        reason='frozen 800/500 assembly met; R2a four-head admission remains pending' if status=='ready' else 'frozen capital quota unmet',
        capital_slice=total,v2_capitals=dict(caps),v2_slots=1572,
        resolved_topup=dict(Counter(polarity(r) for r in tt)),selected_topup=dict(selected_counts,total=len(chosen)),
        unused_topup=dict(Counter(polarity(r) for r in tt if sid(r) not in chosen_ids)),
        selected_cq7=sum(r['truth_tier']=='C_sol_two_independent_CQ7_agreed' for r in chosen),
        shortfall={k:max(0,{'negative':800,'positive':500}[k]-total[k]) for k in total},
        wcap=dict(resolved=281,total=300,marked=133,bare=148,quarantined=19,witness_only=True),
        seeds=[20261016,20261017,20261018],preregistration_sha256=PREREG,amendment='1a',
        training_ready=False,deployable=False,commands=dict(smoke='ready: semantic only',verify='ready',
        prepare='ready: admission audit only',train='missing admitted runtime',evaluate='ready: offline ledgers required',submit='missing production runtime'),
        deployed=False,submitted=False,training_smoke_executed=False,real_input_dry_run_executed=False)
    dump(P/'assembly_receipt.json',receipt)
    dump(P/'data/HEAD_ADMISSION.json',dict(policy_source='evidence/r2_manifest.py ManifestPool.__init__; evidence/r2a_run.py validate',
        known_heads=['breathing','accent'],unknown_heads=['diaeresis','subscript'],
        row_policy='unknown tuple quarantined whole; parent validate rejects unknown overlay',
        assumed_zero_heads=[],masked_loss_added=False,teacher_fill_added=False,
        assembled_topup=len(chosen),admitted_topup=0,assembled_overlay=len(vv)+len(chosen),
        full_candidate_training_ready=False))
    dump(P/'evidence/source_inputs.json',dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        inputs={src:sha(CQ/src) for src in sources},frozen_cq6_hashes=frozen_before,
        remote_read_only=True,remote_command='sacct; scontrol show partition debug; sha256sum parent sources, config and three run bindings'))
    assert snapshot()==frozen_before, 'frozen CQ6 changed'
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':
    main()
