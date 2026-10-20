"""Offline CQ4b amended inventory gate. Does not build packs or run any reader."""
import collections
import hashlib
import json
import math
from pathlib import Path
import random
import re
import shutil
import unicodedata as U

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'artifacts/cq4'
P = ROOT.parent
R2 = ROOT / 'docs/labelfix/spellcheck/R2'
SPELL = P / 'greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck'
S8 = P / 'greek-ocr-toolkit-spellcheck-s8'
HASHES = {}


def read(p):
    p = Path(p)
    data = p.read_bytes()
    HASHES[str(p)] = hashlib.sha256(data).hexdigest()
    return data.decode()


def load(p):
    return json.loads(read(p))


def rows(p):
    return [json.loads(s) for s in read(p).splitlines() if s.strip()]


def alias(d):
    return d.removesuffix(':human').split(':')[-1]


def line_doc(s):
    return alias(re.split(r'--n\d+|-p\d+|-l\d+', s)[0])


def dump(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n')


def main():
    prereg = P/'greek-ocr-toolkit-spellcheck-r2prep/docs/labelfix/spellcheck/R2/R2A2_PREREGISTRATION.md'
    read(prereg)
    assert HASHES[str(prereg)] == 'dbac559fe9792a4f7c879f1fc7b08d03c6a82611bbb42ecce1ffd4ae31ccbebc'
    roles = load(R2/'doc_roles.json')
    base = P/'greek-ocr-toolkit/docs/harvest/collection/v2'
    v2 = rows(base/'import_real_v2_train.jsonl')
    other = rows(base/'import_real_v2_dev.jsonl') + rows(base/'import_real_v2_test.jsonl')
    w1 = rows(P/'collect-v3-data/run/W1/candidates.jsonl')
    lookup = {r['id']:alias(r['doc']) for r in v2+other}
    lookup.update({r['id']:alias(r['item']) for r in w1})
    def docs(ids):
        return {lookup.get(i,line_doc(i)) for i in ids}
    groups = {}
    for t in ('T2','T4'):
        groups[t] = {alias(r['doc']) for r in rows(R2/f'decks/{t}/private/key.jsonl')}
    for role in ('validation','calibration'):
        groups[role] = {alias(d) for d,m in roles['documents'].items() if m['role']==role}
    c1 = rows(S8/'.cache/labelfix/clariden/C1_selection.jsonl')
    c1docs = sorted({r['doc'] for r in c1})
    assert len(c1docs)==316
    groups['old_pool_316'] = {alias(d) for d in c1docs}
    # R1 document_split: the 16 held-out documents are INSIDE the 316.
    groups['old_pool_heldout16'] = {alias(d) for d in random.Random(20261016).sample(c1docs,16)}
    groups['S8_DEV'] = docs(read(S8/'docs/labelfix/spellcheck/S8_DEV/S8_DEV_ids.txt').split())
    read(SPELL/'LQB_MARKS_INPUTS.md')
    groups['print_truth'] = docs(r['line_id'] for r in load(SPELL/'print_truth/key_SEALED.json').values())
    groups['owner39'] = docs(r['line_id'] for r in load(SPELL/'R2_evidence/reader_errors_39_card_inputs.json'))
    sub = load(SPELL/'R2_evidence/substitution_sample_60.json')
    groups['substitution60'] = docs(r['line_id'] for rs in sub['sample'].values() for r in rs)
    groups['audit100'] = docs(r['line_id'] for r in rows(S8/'docs/labelfix/spellcheck/clariden/L1R3_evidence/production_3680729_3680730/audit100_ids.jsonl'))
    groups['CQ1'] = {alias(r['doc']) for r in load(ROOT/'artifacts/cq1/keys/cap1.json')['items'].values()}
    # Amendment 1 removes only the validation reason, and only for W-CAP.
    topup_excluded = set().union(*groups.values())
    wcap_excluded = set().union(*(v for k,v in groups.items() if k!='validation'))
    validation = groups['validation']
    assert len(validation)==17
    prior=load(OUT/'prior_cq4/inventory.json')
    unused={alias(d) for d in prior['wcap_candidate_documents']}
    assert len(unused)==3
    wcap_allowed=validation|unused
    assert not (wcap_allowed & wcap_excluded)
    source=P/'greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/tools'
    scanner_sha='dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547'
    read(source/'scan_rollout.py')
    assert HASHES[str(source/'scan_rollout.py')]==scanner_sha
    shutil.copyfile(source/'scan_rollout.py',OUT/'tools/scan_rollout.py')
    assert hashlib.sha256((OUT/'tools/scan_rollout.py').read_bytes()).hexdigest()==scanner_sha
    read(source/'scan_rollout.py')
    assert HASHES[str(source/'scan_rollout.py')]==scanner_sha
    for name in ('common.py','replay_literal.py'):
        read(source/name)
        shutil.copyfile(source/name,OUT/'tools'/name)
        assert hashlib.sha256((OUT/'tools'/name).read_bytes()).hexdigest()==HASHES[str(source/name)]
    # Fresh canonical v4.4 audits, using each original manifest and rollout.
    import scan_rollout
    regression={}
    for entry in load(ROOT/'artifacts/cq1/usage_ledger.json'):
        reader=entry['reader'];assert reader in ('r1','r1b')
        closure=load(ROOT/('artifacts/cq1/closure'+('_r1b' if reader=='r1b' else '')+'.json'))
        if isinstance(closure,list):closure=closure[0]
        rd=Path(closure['directory']);rollout=Path(entry['run']['rollout'])
        read(rollout);read(rd.parent/f'MANIFEST.{rd.name}.json')
        result=scan_rollout.inspect(rollout,rd)
        result['scanner_sha256']=scanner_sha
        dump(OUT/'regression'/f'cq1_{reader}.scan_v44.json',result)
        assert result['ok']==(reader=='r1b'),result['violations']
        if reader=='r1':
            assert any(v.get('record')==24 and v.get('path')=='/zoom/batch1.png' for v in result['violations'])
        regression[reader]=dict(status='clean' if result['ok'] else 'VOID',violations=result['violations'],image_match_counts=result['image_match_counts'])
    assert set(regression)=={'r1','r1b'}
    dump(OUT/'excluded_docs.json',dict(scanner_sha256=scanner_sha,
        canonicalization='strip :human suffix and source namespace',
        count=len(topup_excluded),documents=sorted(topup_excluded),
        by_reason={k:sorted(v) for k,v in groups.items()},
        wcap=dict(count=len(wcap_excluded),documents=sorted(wcap_excluded),eligible_documents=sorted(wcap_allowed),removed_reason='validation only'),
        topup=dict(count=len(topup_excluded),documents=sorted(topup_excluded))))
    exbase=P/'greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_exclusions'
    passed={(r['tranche'],r['source'],r['primary_class'],r.get('gazette_stratum')) for r in load(exbase/'unchecked_strata.json')['strata'] if r['status']=='c1_pass'}
    eligible=rows(R2/'eligible_lines.jsonl')
    candidates={}
    # Validation documents are explicitly eligible, including v2 documents that
    # are not wholly ALL-CAPS. No change to their frozen R2 role is made.
    for d in sorted(wcap_allowed):
        meta=next((m for raw,m in roles['documents'].items() if alias(raw)==d),{})
        candidates[d]=dict(pool=meta.get('pool','W1'),source=meta.get('source','unknown'),era=meta.get('era','unknown'),role=meta.get('role','unassigned'),lines=0,slot_upper_bound=30)
    for r in eligible:
        d=alias(r['document'])
        if d in candidates:candidates[d]['lines']+=1
    # Broad top-up scan: all Greek mono AND poly train lines, rather than
    # restricting it to the W-CAP all-caps v2 stratum or saved R2C words.
    # This is a conservative document upper bound, before geometry, v2-slot
    # removal, page caps, class balance, or W-CAP document reservation.
    topdocs={}
    def add_top(r,pool):
        d=alias(r['item'] if pool=='W1' else r['doc'])
        if d in topup_excluded:return
        year=str(r.get('year',''));era=str(int(year)//10*10)+'s' if year.isdigit() else 'unknown'
        meta=next((m for raw,m in roles['documents'].items() if alias(raw)==d),{})
        x=topdocs.setdefault(d,dict(pool=pool,source=r['source'] if pool=='W1' else r['wave']+':'+r['source'],era=era,role=meta.get('role','unassigned'),lines=0,slot_upper_bound=120))
        x['lines']+=1
    for r in w1:
        if (r['tranche'],r['source'],r['primary_class'],r.get('gazette_stratum')) in passed and r['primary_class'] in ('poly1850','poly1900','greek_poly','greek_mono') and r.get('usable_final') is True and r.get('candidate_usable') is True:
            add_top(r,'W1')
    for r in v2:
        if r.get('split')=='train' and r['script_class'] in ('greek_mono','greek_poly'):
            add_top(r,'v2')
    cells=collections.Counter((m['pool'],m['source'],m['era']) for m in candidates.values())
    target=735+470;minimum=math.ceil(.7*target);upper=len(topdocs)*math.floor(.1*target)
    assert upper<minimum,'Top-up no longer proves shortfall: reassess slot inventory before building.'
    inventory=dict(status='STOP_TOPUP_INVENTORY_SHORTFALL',amendment=1,seed=20261017,
        preregistration_sha256=HASHES[str(prereg)],scanner_version='v4.4-canonical',scanner_sha256=scanner_sha,
        scanner_copy_before_and_after_verified=True,scanner_copy=dict(source=str(source/'scan_rollout.py'),source_before_sha256=scanner_sha,source_after_sha256=HASHES[str(source/'scan_rollout.py')],destination_sha256=hashlib.sha256((OUT/'tools/scan_rollout.py').read_bytes()).hexdigest()),cq1_rescan=regression,
        excluded_documents=len(topup_excluded),wcap_excluded_documents=len(wcap_excluded),
        exclusion_group_counts={k:len(v) for k,v in groups.items()},
        wcap_candidate_documents=candidates,wcap_counts_by_source_era=[dict(pool=p,source=s,era=e,documents=n) for (p,s,e),n in sorted(cells.items())],
        wcap_document_cap=30,wcap_target=300,wcap_minimum=210,wcap_upper_bound=len(candidates)*30,
        wcap_gate='document upper bound passes; located-slot gate not assessed because top-up already fails',
        topup_candidate_documents=topdocs,topup_document_cap=120,topup_target=target,topup_minimum=minimum,topup_upper_bound=upper,
        topup_cap_note='floor(10% of 1205)=120; generous bound before any W-CAP reservation. Minimum deficits without oversampling are 586 bare + 373 marked = 959; even their 70% minimum 672 exceeds 360.',
        slot_counts=None,slot_counts_note='Not located or selected: mandatory top-up document upper bound already fails. Per-document slot counts are upper bounds, not located/readable counts.',
        heldout_note='R1 document_split holds out 16 of the 316 C1 documents; these are already in old_pool_316.',
        pack_contexts_built=0,controls_built=0,reader_runs=0,training_runs=0,manifest_builds=0,
        codex_weekly_before=None,codex_weekly_after=None,codex_probe_note='Build only. No reader or limit probe ran; live weekly usage unknown.',estimated_reader_weekly_points_executed=0)
    dump(OUT/'inventory.json',inventory)
    dump(OUT/'build_receipt.json',dict(inventory,inputs_sha256=HASHES))
    lines=['# CQ4b amended inventory: STOP','',
        'Amendment 1 enlarges W-CAP to 20 candidate documents, but the unchanged top-up exclusions fail the mandatory 70% gate. No packs, control pool, run scripts, readings, training or R2a manifest were built.','',
        f'Preregistration SHA-256 verified: `{HASHES[str(prereg)]}`.',
        f'Canonical scanner v4.4 copied without modification; source before/after and destination SHA-256: `{scanner_sha}`. Dependencies copied from the same canonical directory with hashes in the receipt. CQ4 does not import or invoke a CQ1 v4.3 wrapper.',
        'CQ1 canonical re-scan: **r1 VOID**, `/zoom/batch1.png` at record **24**; **r1b clean**, with manifest integrity enabled. Full audits: `artifacts/cq4/regression/`.','',
        'The exclusion union remains 495 documents for top-up. Removing only the validation reason for W-CAP gives 478 excluded documents; the 17 validation-role documents have no other exclusion reason. Calibration remains excluded from both sets. Original CQ4 inventory/report artifacts are preserved in `artifacts/cq4/prior_cq4/`.','',
        '## Inventory gate','',
        '| Set | Candidate documents | Per-document slot cap | Generous slot upper bound | 70% minimum | Result |',
        '|---|---:|---:|---:|---:|---|',
        f'| W-CAP | {len(candidates)} | 30 | {len(candidates)*30} | 210 | Document bound passes; actual slot availability not located |',
        f'| Top-up, before reserving any W-CAP document | {len(topdocs)} | 120 | {upper} | {minimum} | **STOP** |','',
        'Top-up requires about 735 likely-bare + 470 likely-marked slots (1,205). Even granting all three unused documents exclusively to top-up gives at most 360 slots. Choosing any for W-CAP reduces that bound. The 97 other supervision-role and 29 other witness-role documents are already excluded; validation and calibration remain excluded for top-up. At least eight eligible top-up documents are necessary for the 844-slot gate under the generous 120-slot cap.','',
        'The broader raw top-up scan includes all Greek monotonic and polytonic v2 train lines, not only ALL-CAPS lines or saved R2C eligibility; **zero v2 documents survive**. W1 c1_pass Greek candidates leave the same three unused documents. The impossibility holds even without the 25% oversampling: 70% of the 959-slot repair deficit is 672, above 360. No marked/bare, geometry, page-cap or manifest-overlap assumption is needed.','',
        '## Counts per candidate document','',
        'Line counts are saved eligible lines for W-CAP and broad admitted source lines for top-up. Slot columns are optimistic document-cap upper bounds; actual located, marked-likely and bare-likely counts remain unknown. Documents appearing in both columns are alternatives, never selected for both.','',
        '| Canonical document | Pool / source | Era | Role | W-CAP lines | W-CAP slot cap | Top-up lines | Top-up slot cap |',
        '|---|---|---|---|---:|---:|---:|---:|']
    for d in sorted(set(candidates)|set(topdocs)):
        w=candidates.get(d,{});t=topdocs.get(d,{});m=w or t
        lines.append(f'| `{d}` | {m["pool"]} / {m["source"]} | {m["era"]} | {m["role"]} | {w.get("lines",0)} | {w.get("slot_upper_bound",0)} | {t.get("lines",0)} | {t.get("slot_upper_bound",0)} |')
    lines += ['', '## W-CAP candidates by source and era','', '| Pool | Source | Era | Documents |','|---|---|---|---:|']
    lines += [f'| {p} | {s} | {e} | {n} |' for (p,s,e),n in sorted(cells.items())]
    lines += ['', '## Reproduction and limits','',
        'Run `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B artifacts/cq4/tools/inventory.py`, then the same interpreter with `-m unittest discover -s artifacts/cq4/tools -p "test_*.py"`. Input hashes and scanner identity are recorded in the build receipt; validation results are in `artifacts/cq4/validation.json`.',
        'No network calls, `.git` writes, reader calls, model inference or limit probes were made. Executed reader cost is **0 weekly points**; live weekly usage is unknown. The requested full 18-context initial read remains an upper-bound estimate of **3.37 weekly points**, before re-reads. This inventory does not qualify located W-CAP slots or printed truth.',
        'Continuation requires a coordinator amendment to top-up document eligibility or additional eligible documents. The present instruction explicitly keeps validation documents excluded from top-up, so they were not repurposed.','',
        f'CQ4b BUILD STOPPED: W-CAP candidate docs {len(candidates)} (slot upper bound {len(candidates)*30}, located counts unknown); top-up candidate docs {len(topdocs)} (slot upper bound {upper} < {minimum}); contexts 0; controls pool 0; scanner v4.4 sha ok; CQ1 rescan r1 VOID / r1b clean; executed reader Codex 0 pts.']
    (R2/'CQ4_REPORT.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in inventory.items() if k not in ('wcap_candidate_documents','topup_candidate_documents','cq1_rescan')},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
