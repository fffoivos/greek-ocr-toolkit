"""Read saved evidence and small release payloads; never decode native crops."""
from collections import Counter
from copy import deepcopy
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys
import unicodedata as ud

ROOT=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck')
OUT=Path(__file__).resolve().parent
from greekocr.labelfix import release_gate as gate
from greekocr.labelfix.text import clusters,nfd
from scripts.labelfix.clariden.l1_common import rows,label_sha,overlay
from scripts.labelfix.clariden.r1_common import sha256
from test_c3_scope import capital_diaeresis,clean


def dump(name,data):
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')


def check_release(path, variants, originals):
    out={}
    for variant in variants:
        m=json.loads((path/f'release_{variant}.json').read_text())
        ctrl=json.loads((path/f'release_ctrl_subset_{variant}.json').read_text())
        for obj,keys in [(m,[('overlay','overlay_sha256'),('kept_line_ids','kept_line_ids_sha256')]),
                         (ctrl,[('labels_file','labels_sha256')])]:
            for name,digest in keys:assert sha256(path/obj[name])==obj[digest]
        overlays=list(rows(path/m['overlay']));controls=list(rows(path/ctrl['labels_file']))
        kept=(path/m['kept_line_ids']).read_text().splitlines()
        accepted=[r['line_id'] for r in overlays if r['status'] in ('corrected','unchanged')]
        assert len(accepted)==len(set(accepted))==len(kept)==m['kept_lines']
        assert set(accepted)==set(kept)=={r['line_id'] for r in controls}
        assert Counter(r['status'] for r in overlays)==Counter(m['counts_by_status'])
        for r in overlays:
            assert r['original_label_sha256']==label_sha(originals[r['line_id']]['label'])
            if r['status'] in ('corrected','unchanged'):
                assert not r['hold_slots']
                assert all(s['label_status']!='HOLD' and not s['hold_reasons'] for s in r['gate_decisions'])
            else:assert 'label' not in r and r['line_id'] not in kept
        for c in controls:
            assert c['label']==originals[c['line_id']]['label']
            assert c['original_label_sha256']==label_sha(c['label'])
        waves={}
        for r in overlays:
            wave=originals[r['line_id']]['wave']
            waves.setdefault(wave,Counter())[r['status']]+=1
        for wave,c in waves.items():
            assert all(m['coverage_per_wave'][wave][k]==c[k] for k in ('corrected','unchanged','hold','out_of_scope'))
        if m['release_policy']!='sf2-release-v1':
            assert m['ensemble_caveat']==ctrl['ensemble_caveat']==gate.ENSEMBLE_CAVEAT
            assert all(len(v)==64 for v in m['checkpoint_sha256'].values())
        out[variant]=dict(policy=m['release_policy'],counts=m['counts_by_status'],kept=len(kept),
            overlay_and_control_hashes_verified=True,original_label_hashes_verified=len(overlays),
            original_control_labels_verified=len(controls),exact_pairing=True,no_HOLD_fallback=True,
            wave_counts_verified=True,exclusions=m['exclusion_receipts'],r0_policy=m['r0_policy'],
            code_commit=m['code_commit'],policy_sha=m['policy_sha'],
            manifest_sha256=sha256(path/f'release_{variant}.json'))
    return out


def release_checks():
    fixture=ROOT/'artifacts/labelfix_l1e/fixture_v4/mock'
    originals={r['id']:r for r in rows(fixture/'selection.jsonl')}
    r={}
    for tag,path in [('L1E_original_mock64',ROOT/'artifacts/labelfix_l1e/mock_run_v4/recomposition'),
                     ('SF3_recomposed_mock64',OUT/'recomposed_mock64')]:
        receipt=json.loads((path/'receipt.json').read_text())
        for name,digest in receipt['inputs'].items():assert sha256(Path(name) if Path(name).is_absolute() else ROOT/name)==digest
        for name,digest in receipt['outputs'].items():assert sha256(path/name)==digest
        r[tag]=dict(inputs_verified=len(receipt['inputs']),outputs_verified=len(receipt['outputs']),
                    historical_apostrophe_boxes_missing=receipt['historical_apostrophe_boxes_missing'],
                    releases=check_release(path/'release',('presence','full','ensemble_ab'),originals))
    sf2=Path('/tmp/SF2-l1r-verified-20261017')
    receipt=json.loads((sf2/'receipt.json').read_text())
    for name,digest in receipt['inputs'].items():assert sha256(Path(name) if Path(name).is_absolute() else ROOT/name)==digest
    for name,digest in receipt['outputs'].items():assert sha256(sf2/name)==digest
    ids={r['line_id'] for r in rows(sf2/'release/overlay_presence.jsonl.gz')}
    originals={r['id']:r for r in rows(ROOT/'docs/harvest/collection/v2/import_real_v2_train.jsonl') if r['id'] in ids}
    assert set(originals)==ids
    r['SF2_original_mock160']=dict(inputs_verified=len(receipt['inputs']),outputs_verified=len(receipt['outputs']),
        releases=check_release(sf2/'release',('presence','full'),originals))
    return r


def owner_checks():
    from scripts.labelfix import owner_pages_build_combined as p
    base=Path('/tmp/SF2-verified-20261017/owner')
    conf=json.loads((base/'combined_config.json').read_text())
    side=json.loads((base/'combined_boxes.json').read_text())
    assert side['page_sha256']==sha256(base/'combined.html')
    p.R1={}
    for path,digest in conf['r1_predictions'].items():
        path=ROOT/path;assert sha256(path)==digest
        for r in rows(path):p.R1[r['line_id'],r['start']]=r
    for path,digest in conf['r1_coverage'].items():assert sha256(path)==digest
    p.COVERAGE={r['line_id']:r['coverage'] for r in rows(base/'coverage.jsonl')}
    p.LINE_TEXT={r['line_id']:r['recogniser_text'] for r in rows(base/'S6_scoring_lines.jsonl')}
    outputs={};equal=0
    for lid,s in side['lines'].items():
        predictions={start:v for (key,start),v in p.R1.items() if key==lid}
        raw=s['raw_line_reading']
        expected=gate.compose(p.LINE_TEXT[lid],raw,predictions,p.COVERAGE[lid],'PRESENCE')
        actual,_=p.combine(lid,gate.deserialize(raw),'PRESENCE')
        a=gate.serialize(actual)
        assert a['text']==expected['text'] and a['slots']==expected['slots']
        equal+=1;outputs[lid]=expected
    old=json.loads((ROOT/'docs/reviews/astra_program_review_2026-10-06/ASTRA-SC1c2_evidence/cn1_unheld_coverage.json').read_text())
    checked=[]
    for kind,values in old.items():
        if not isinstance(values,list):continue
        for lid,start,baseletter in values:
            slot=next(s for s in outputs[lid]['slots'] if s['start']==start)
            assert slot['hold'];checked.append(dict(kind=kind,line_id=lid,start=start,reasons=slot['hold_reasons']))
    quotes={lid:outputs[lid]['text'] for lid in ('384c3f89-p000030-l0010','384c3f89-p000030-l0029')}
    assert all(t.startswith('“') for t in quotes.values())
    return dict(saved_page_sha256=sha256(base/'combined.html'),current_presence_exact_lines=equal,
        previous_unheld_witnesses=checked,quote_witnesses=quotes,
        limit='Saved-evidence composition only; no new physical detection or GUI qualification.')


def domain_checks():
    unsupported=0;failures=[]
    for code in [*range(0x370,0x400),*range(0x1f00,0x2000)]:
        char=chr(code);cs=clusters(nfd(char))
        if len(cs)==1 and cs[0].marks and not gate._supported(cs[0]):
            unsupported+=1
            if not gate.edit_guard(char,cs[0].base):failures.append(char)
    cases=0
    marks=['\u0304','\u0306','\u0307','\u0323','\u0301\u0300','\u0313\u0314','\u0308\u0313']
    for base,mark in itertools.product('αεηιουωρΑΕΗΙΟΥΩΡaéδϝ',marks):
        source=base+mark
        if not gate._supported(clusters(nfd(source))[0]):
            cases+=1
            if not gate.edit_guard(source,base):failures.append(source)
    assert not failures
    return dict(greek_unicode_unsupported_precomposed_cases=unsupported,
        unsupported_cluster_deletion_cases=cases,unsafe_deletions=failures,
        scope='Greek and Greek Extended canonical decompositions plus explicit synthetic unsupported classes; not an exhaustive Unicode proof.')


def cli_checks():
    results={}
    for case in ('external_K1_flag','Google_agrees_R1_detector_disagrees'):
        r=clean('α');r['recogniser_text']='ά'
        r['r1_predictions'][0]['parts']=['acute']
        r['detector']['slots'][0]['parts']=['acute' if case=='external_K1_flag' else 'psili']
        path=OUT/(case+'.jsonl');path.write_text(json.dumps(r,ensure_ascii=False)+'\n')
        cmd=[sys.executable,str(ROOT/'scripts/labelfix/agreement_mode.py'),str(path),'--mode','PRESENCE']
        if case=='external_K1_flag':
            flags=OUT/'external_flags.jsonl'
            flags.write_text(json.dumps(dict(id='synthetic',constraint_flags=[dict(start=0,rule='C2',reason='impossible_by_rule')]))+'\n')
            cmd+=['--flags',str(flags)]
        p=subprocess.run(cmd,cwd=ROOT,env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True)
        assert p.returncode==0 and "'HOLD': 1" in p.stdout
        results[case]=p.stdout.strip()
    return results


def new_witnesses():
    out={}
    for base in ('Ι','Υ'):
        r=capital_diaeresis(base);decision=gate.compose_runtime(r,'ENSEMBLE_AB')
        result=overlay(dict(id='synthetic',label=r['recogniser_text'],script_class='greek_poly'),r,
                       'ensemble_ab',dict(detector='s6',r1_sha256='A',policy_sha256='test'))
        out[base]=dict(runtime=r,decision=decision,overlay=result)
    return out


if __name__=='__main__':
    result=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                policy=gate.policy_binding(),network=False,ctc_inference=0,r1_inference=0,native_crops_decoded=0)
    for name,fn in [('releases',release_checks),('owner',owner_checks),('edit_domain',domain_checks),('agreement_cli',cli_checks)]:
        value=fn();dump(name+'_checks.json',value);result[name+'_checks_sha256']=sha256(OUT/(name+'_checks.json'))
        print(name,'verified',flush=True)
    dump('capital_diaeresis_witnesses.json',new_witnesses())
    dump('audit_receipt.json',result)
