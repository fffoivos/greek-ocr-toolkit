"""Offline CQ4 inventory gate. Does not build packs or run any reader."""
import collections
import hashlib
import json
import math
from pathlib import Path
import random
import re
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
    assert HASHES[str(prereg)] == '3b2fdf21169124e0b5e73503860ac299bacc9db5b9aba7917fa65213f65732dc'
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
    excluded = set().union(*groups.values())
    dump(OUT/'excluded_docs.json',dict(canonicalization='strip :human suffix and source namespace; retain all raw group provenance in input hashes',count=len(excluded),documents=sorted(excluded),by_reason={k:sorted(v) for k,v in groups.items()}))
    exbase=P/'greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_exclusions'
    passed={(r['tranche'],r['source'],r['primary_class'],r.get('gazette_stratum')) for r in load(exbase/'unchecked_strata.json')['strata'] if r['status']=='c1_pass'}
    # A document upper bound: no recogniser inference, geometry, or truth read.
    candidates={}
    def add(r,pool):
        d=r['item'] if pool=='W1' else r['doc']
        if alias(d) in excluded:return
        year=str(r.get('year',''));era=str(int(year)//10*10)+'s' if year.isdigit() else 'unknown'
        candidates.setdefault(d,dict(pool=pool,source=r['source'] if pool=='W1' else r['wave']+':'+r['source'],era=era,lines=0,role=roles['documents'].get(d,{}).get('role','unassigned')))['lines']+=1
    for r in w1:
        if (r['tranche'],r['source'],r['primary_class'],r.get('gazette_stratum')) in passed and r['primary_class'] in ('poly1850','poly1900','greek_poly') and r.get('usable_final') is True and r.get('candidate_usable') is True:
            add(r,'W1')
    for r in v2:
        text=r['label'];letters=''.join(c for c in U.normalize('NFD',text) if U.category(c).startswith('L'))
        allcaps=bool(letters) and letters.isupper() and any(c in 'ΑΕΗΙΟΥΩΡ' for c in letters)
        if r.get('split')=='train' and (r['script_class']=='greek_mono' or (r['script_class']=='greek_poly' and allcaps)):
            add(r,'v2')
    cells=collections.Counter((m['pool'],m['source'],m['era']) for m in candidates.values())
    inventory=dict(status='STOP_INVENTORY_SHORTFALL',seed=20261017,preregistration_sha256=HASHES[str(prereg)],excluded_documents=len(excluded),exclusion_group_counts={k:len(v) for k,v in groups.items()},wcap_candidate_documents=candidates,wcap_counts_by_source_era=[dict(pool=p,source=s,era=e,documents=n) for (p,s,e),n in sorted(cells.items())],wcap_document_cap=30,wcap_target=300,wcap_minimum=210,wcap_upper_bound=len(candidates)*30,slot_counts=None,slot_counts_note='Not located: document-cap upper bound fails before slot selection. Likely class counts are unknown.',heldout_note='R1 document_split holds out 16 of the 316 C1 documents; these are already in old_pool_316.',pack_contexts_built=0,controls_built=0,reader_runs=0,training_runs=0,manifest_builds=0,codex_weekly_before=None,codex_weekly_after=None,codex_probe_note='No context was run, so no Sol limit-probe calls were made. Live weekly usage unknown.',estimated_reader_weekly_points_executed=0)
    assert inventory['wcap_upper_bound'] < inventory['wcap_minimum'], 'Inventory no longer proves shortfall: reassess before building.'
    # Keep top-up outside W-CAP candidate docs, conservatively, for an inventory only.
    eligible=rows(R2/'eligible_lines.jsonl')
    topdocs={}
    for r in eligible:
        d=r['document']
        if alias(d) not in excluded and d not in candidates:
            topdocs[d]=roles['documents'][d]
    inventory['topup_remaining_r2c_documents_after_wcap_candidate_reservation']=topdocs
    inventory['topup_note']='No W-CAP selection made. Top-up global inventory not expanded after mandatory W-CAP stop; this field covers saved R2C eligible documents only.'
    dump(OUT/'inventory.json',inventory)
    dump(OUT/'build_receipt.json',dict(inventory,inputs_sha256=HASHES))
    lines=['# CQ4 inventory: STOP', '', 'The mandatory pre-build gate fails. No packs, contexts, controls, runner scripts, readings, training or R2a manifest were built.', '', f'Preregistration SHA-256 verified: `{HASHES[str(prereg)]}`.', '', f'The requested whole-document exclusion union contains **{len(excluded)} documents**. IDs and per-reason membership are in `artifacts/cq4/excluded_docs.json`; input hashes are in `artifacts/cq4/build_receipt.json`.', '', '| Pool | Source | Era | Candidate documents |', '|---|---|---|---:|']
    lines += [f'| {p} | {s} | {e} | {n} |' for (p,s,e),n in sorted(cells.items())]
    lines += ['', 'Candidate documents:']+[f'- `{d}` ({m["role"]}, {m["lines"]} candidate lines)' for d,m in sorted(candidates.items())]
    lines += ['',f'Even before recogniser/case classification, geometry rejection, class balance, page caps, or document alias merging, {len(candidates)} documents × 30 slots/document gives at most **{len(candidates)*30}/300 W-CAP slots**. The minimum is **210/300**. This is a generous upper bound, not a claim of available readable slots. At least seven documents are required even for the 70% threshold; ten are required for 300 slots. Splitting the remaining documents between W-CAP and top-up can only lower this bound.', '', 'The raw W1 c1_pass polytonic rows and collection-v2 training rows were checked directly. V2 eligibility includes monotonic rows and Greek polytonic rows whose letter sequence is ALL-CAPS; none survive the requested exclusions. R2C saved eligibility is not used to restrict this W-CAP document upper bound.', '', inventory['heldout_note'], '', 'Likely-marked / likely-bare slot counts remain unknown: the gate stops before location or selection. Top-up selection is also stopped. The remaining saved R2C top-up inventory after reserving the three W-CAP candidate documents is empty; no wider top-up availability claim is made.', '', 'No reader or limit probe ran. Live Codex percentages are unknown; executed reader cost is 0 points. The requested full initial 1,505 bed items plus 180 controls (18 contexts) would have a HANDOVER §7 upper-bound estimate of 3.37 weekly points before re-reads. No reading is authorized here.', '', 'Reproduce: `python3 -B artifacts/cq4/tools/inventory.py`. The script asserts the shortfall and writes inventory artifacts only. Fresh eligible documents or an owner-approved change to the document exclusions/caps is needed before pack construction.', '', 'CQ4 BUILD STOPPED: W-CAP document-cap upper bound below 70%; no packs or readers built.']
    (R2/'CQ4_REPORT.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(inventory,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
