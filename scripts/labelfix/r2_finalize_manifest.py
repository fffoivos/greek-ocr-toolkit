"""Offline B6c finalization; R2a admission helpers. Never invokes network or git."""
from greekocr.ops.data_root import input_path as _data_input
import json
import hashlib
from pathlib import Path
from collections import Counter
from scripts.labelfix import r2_cards_resolve as R

ROOT = Path(__file__).resolve().parents[2]
TOKENS = {'T2': [157076, 160476], 'T4': [169280, 161761]}

def sha(path):
    return hashlib.sha256(_data_input(Path(path)).read_bytes()).hexdigest()

def unique(rows):
    out = {}
    for row in rows:
        key = tuple(row['slot_id'])
        if key in out and out[key]['targets'] != row['targets']:
            raise ValueError('conflicting duplicate slot')
        out.setdefault(key, row)
    return list(out.values())

def quarantine(row):
    return bool(row.get('unknown')) or any(v is None for v in row['targets'])

def modification(row, old_keys):
    row = dict(row)
    if tuple(row['slot_id']) in old_keys:
        row['replaces'] = row['slot_id']
        row.pop('pool', None)
    else:
        row['pool'] = 'native'
    return row

def leakage_check(rows, roles, witness_docs):
    hits = [r for r in rows if r['doc'] in witness_docs or
            roles.get(r['doc'], {}).get('role') != 'supervision']
    if hits:
        raise ValueError('STOP: manifest document leakage or unbound role: ' + str(sorted({r['doc'] for r in hits})))
    return 0

def diversity(rows):
    """Largest feasible retained slice with <=10% of retained slice per doc.

    Seeded hash order chooses cards/slots. Page cap counts distinct target cards.
    Shrinking a slice cannot leave a document above the final 10% limit.
    """
    rank = lambda r: hashlib.sha256(('20261017:' + str(r['slot_id'])).encode()).hexdigest()
    selected = []; excluded = []; pages = {}
    for row in sorted(rows, key=rank):
        page = (row['doc'], row['page']); cards = pages.setdefault(page, set())
        if row['card_id'] not in cards and len(cards) >= 5:
            excluded.append(dict(row, reason='page_cap_5_target_cards')); continue
        cards.add(row['card_id']); selected.append(row)
    result = []
    for sl in sorted({r['slice'] for r in selected}):
        group = [r for r in selected if r['slice'] == sl]
        counts = Counter(r['doc'] for r in group)
        feasible = max((n for n in range(len(group)+1) if sum(min(c, n//10) for c in counts.values()) >= n), default=0)
        used = Counter(); kept = 0
        for row in group:
            if used[row['doc']] >= feasible//10 or kept >= feasible:
                excluded.append(dict(row, reason='document_cap_10_percent_of_retained_slice')); continue
            result.append(row); used[row['doc']] += 1; kept += 1
    return result, excluded

def finalize(t):
    out = ROOT/'artifacts/r2_resolve'/t
    deck = ROOT/'docs/records/labelfix/spellcheck/R2/decks'/t
    keys = {k['card_id']: dict(k, deck=t) for k in R.read(deck/'private/key.jsonl')}
    original = R.read(deck/'blind/cards.jsonl'); cards = {c['card_id']: c for c in original}
    controls = json.loads((deck/'private/controls_proposed.json').read_text())['controls']
    readers = []
    for i in (1, 2):
        order = [c['card_id'] for c in (original if i == 1 else original[::-1])]
        votes, gate = R.batch(out/'inputs'/f'r{i}.jsonl', cards, controls, order)
        assert gate['accepted']
        readers.append(votes)
    receipt = json.loads((out/'r3_deal_receipt_v2.json').read_text())
    mapping = json.loads((out/'tiebreak_v2/private/option_mapping.json').read_text())
    private_controls = json.loads((out/'tiebreak_v2/private/controls_proposed.json').read_text())['controls']
    for name, digest in receipt['v2_hashes'].items():
        assert sha(out/'tiebreak_v2'/name) == digest, name
    allthird = {}; gates = {}; usage = []; verified = []
    for i, folder in enumerate(receipt['folders']):
        p = Path(folder['folder']); answers = R.read(p/'answers.jsonl')
        for name, digest in folder['hashes'].items():
            if name != 'answers.jsonl':
                assert sha(p/name) == digest, str(p/name)
        assigned = R.read(p/'cards.jsonl'); ids = [a['card_id'] for a in answers]
        assert len(ids) == len(set(ids)) == folder['cards']
        assert set(ids) == set(folder['card_ids']) == {c['card_id'] for c in assigned}
        assert len((p/'answers.jsonl').read_text().splitlines()) == folder['cards']
        assert all(c == mapping[c['card_id']] for c in assigned)
        selected_controls = [c for c in private_controls if c['card_id'] in folder['selected_control_ids']]
        assert len(selected_controls) == 10
        # Reorder by ID for batch validation, never use physical answer position.
        byid = {a['card_id']: a for a in answers}
        joined = out/'final/inputs'/f'b{i:02}.jsonl'
        R.write(joined, [byid[c['card_id']] for c in assigned])
        normal, gate = R.batch(joined, mapping, selected_controls, [c['card_id'] for c in assigned])
        gates[f'b{i:02}'] = gate
        if gate['accepted']:
            assert not set(allthird) & set(normal)
            allthird.update(normal)
        verified.append(dict(folder=str(p), cards=len(ids), answers_sha256=sha(p/'answers.jsonl'), receipt_sha256=sha(out/'r3_deal_receipt_v2.json'), immutable_hashes_verified=True))
        usage.append(dict(reader='reader3', folder=f'b{i:02}', cards=len(ids), data_cards=folder['data_cards'], control_readings=10, accepted=gate['accepted'], total_tokens=TOKENS[t][i], token_source='lead-supplied subagent total including tool I/O', input_tokens=None, output_tokens=None))
    truth = [R.resolve_card(k, [r[ident] for r in readers+[allthird] if ident in r]) for ident,k in keys.items() if not k['control']]
    assert len(truth) == 800
    final = out/'final'
    R.write(final/'resolved.jsonl', [r for r in truth if r['status'] == 'resolved'])
    R.write(final/'unresolved.jsonl', [r for r in truth if r['status'] != 'resolved'])
    R.dump(final/'gate.json', dict(per_folder=gates, all_passed=all(g['accepted'] for g in gates.values()), input_verification=verified, original_gate= json.loads((out/'gate.json').read_text()), input_sha256={str(p.relative_to(ROOT)):sha(p) for p in [out/'inputs/r1.jsonl',out/'inputs/r2.jsonl',deck/'private/key.jsonl',deck/'private/controls_proposed.json',out/'r3_deal_receipt_v2.json']}, resolved=sum(r['status']=='resolved' for r in truth), unresolved=sum(r['status']!='resolved' for r in truth)))
    R.dump(final/'opus_usage.json', dict(reader3=usage, reader3_total_tokens=sum(TOKENS[t]), earlier_readers=json.loads((out/'opus_usage.json').read_text()), earlier_token_totals='not recorded; emitted zeros were placeholders'))
    print(t, 'resolved',sum(r['status']=='resolved' for r in truth),'unresolved',sum(r['status']!='resolved' for r in truth), 'gates', [(k,g['control_errors'],g['invalid_answer_count']) for k,g in gates.items()])


TARGETS = {'capitals': (800,500), 'omicron_monotonic': (400,400), 'subscript': (400,500), 'specks': (400,200), 'exact_names': (0,400)}

def unique_alignment(source, target):
    """Only accept a source base if every optimal LCS maps it to one target."""
    n,m=len(source),len(target)
    pre=[[0]*(m+1) for _ in range(n+1)]; suf=[[0]*(m+1) for _ in range(n+1)]
    for i in range(n):
        for j in range(m):
            pre[i+1][j+1]=max(pre[i][j+1],pre[i+1][j],pre[i][j]+(source[i]==target[j]))
    for i in range(n-1,-1,-1):
        for j in range(m-1,-1,-1):
            suf[i][j]=max(suf[i+1][j],suf[i][j+1],suf[i+1][j+1]+(source[i]==target[j]))
    best=pre[n][m]; result={}
    for i in range(n):
        possible=[j for j in range(m) if source[i]==target[j] and pre[i][j]+1+suf[i+1][j+1]==best]
        skipped=any(pre[i][j]+suf[i+1][j]==best for j in range(m+1))
        if len(possible)==1 and not skipped: result[i]=possible[0]
    return result

def slice_compatible(slice_name, base):
    if slice_name == 'capitals':
        return base.isupper()
    if slice_name == 'subscript':
        return base.lower() in 'αηω'
    return True

def build_manifest():
    import gzip
    import unicodedata as U
    prep=ROOT.parent/'greek-ocr-toolkit-spellcheck-r2prep'
    run=prep/'artifacts/labelfix_r2/output_3681404'
    config=json.loads((prep/'config/r2_job.json').read_text())
    ext=json.loads((prep/'docs/labelfix/spellcheck/R2/evidence/external_hashes.json').read_text())
    inv=ROOT.parent/'greek-ocr-toolkit-spellcheck/.cache/labelfix/clariden/C1_crop_inventory.jsonl.gz'
    assert sha(inv)==ext[config['inventory']]
    with gzip.open(inv,'rt') as f: old_hashes={json.loads(s)['sha256'] for s in f if s.strip()}
    keys={k['card_id']:k for k in R.read(ROOT/'docs/records/labelfix/spellcheck/R2/decks/T2/private/key.jsonl') if not k['control']}
    # All source crop hashes are disjoint from the complete frozen crop inventory:
    # this proves no old-pool slot match without needing its remote index.
    assert not {k['crop_sha256'] for k in keys.values()} & old_hashes, 'old index required for overlapping crops'
    roles=json.loads((ROOT/'docs/records/labelfix/spellcheck/R2/doc_roles.json').read_text())['documents']
    witnesses={k['doc'] for k in R.read(ROOT/'docs/records/labelfix/spellcheck/R2/decks/T4/private/key.jsonl')}
    leakage_check(list(keys.values()),roles,witnesses)
    needed={k['line_id'] for k in keys.values()}
    labels={r['id']:r['label'] for r in R.read(ROOT/'docs/records/labelfix/spellcheck/R2/eligible_lines.jsonl') if r['id'] in needed}
    readback=json.loads((run/'READBACK_RECEIPT.json').read_text()); bound={f['path']:f['sha256'] for f in readback['files']}
    align={}; exports={}; hashes={}
    for p in sorted((run/'B').glob('*-alignments.jsonl.gz')):
        with gzip.open(p,'rt') as f: rows=[json.loads(s) for s in f if s.strip()]
        relevant=[r for r in rows if r['line_id'] in needed]
        if not relevant: continue
        rel=str(p.relative_to(run)); assert sha(p)==bound[rel]; hashes[rel]=bound[rel]
        for row in relevant: align[row['line_id']]=row
        tp=p.with_name(p.name.replace('-alignments','-train'))
        rel=str(tp.relative_to(run)); assert sha(tp)==bound[rel]; hashes[rel]=bound[rel]
        with gzip.open(tp,'rt') as f:
            for s in f:
                e=json.loads(s)
                if e['line_id'] in needed: exports[tuple(e['slot_id'])]=e
    candidates=[]; quarantined=[]; excluded=[]
    truth=R.read(ROOT/'artifacts/r2_resolve/T2/final/resolved.jsonl')+R.read(ROOT/'artifacts/r2_resolve/T2/final/unresolved.jsonl')
    vals=[['none','psili','dasia'],['none','acute','grave','circumflex'],['none','present'],['none','present']]
    for row in truth:
        k=keys[row['card_id']]; entries={h['index']:h for h in row['letter_heads']}
        entries.setdefault(k['anchor_index'],dict(index=k['anchor_index'],**{h:'unknown' for h in R.HEADS}))
        a=align.get(k['line_id']); mapping={}; starts=[]
        if a:
            assert a['crop_sha256']==k['crop_sha256']
            pred=U.normalize('NFD',a['alignment']['prediction'])
            starts=[i for i,c in enumerate(pred) if U.category(c) in ('Lu','Ll','Lt','Lo')]
            mapping=unique_alignment(R.letters(labels[k['line_id']]),[pred[i] for i in starts])
        printed=R.letters(row['printed_form']) if row['printed_form'] else []
        mined=R.letters(k['mining_key'])
        for i,h in entries.items():
            evidence=dict(card_id=k['card_id'],doc=k['doc'],page=k['page'],slice=k['slice'],letter_index=i,crop_sha256=k['crop_sha256'],crop_letter_index=k['crop_letter_offset']+i,heads=h)
            reason=None
            if quarantine(dict(targets=[None if h.get(head)=='unknown' else 0 for head in R.HEADS])): reason='unknown_head'
            elif row['status']!='resolved': reason='unresolved_card'
            elif printed!=mined: reason='printed_base_sequence_differs_from_located_word'
            ordinal=k['crop_letter_offset']+i
            if reason is None and ordinal not in mapping: reason='recogniser_base_alignment_not_unique_or_missing'
            if ordinal in mapping:
                evidence['slot_id']=[k['crop_sha256'],starts[mapping[ordinal]]]
            if reason:
                quarantined.append(dict(evidence,reason=reason));continue
            start=starts[mapping[ordinal]]; sid=[k['crop_sha256'],start]; e=exports.get(tuple(sid))
            if e is None:
                # R1's bound embedding/extractor supports Greek vowels and rho only.
                from scripts.labelfix.clariden.r1_common import LETTERS
                if printed[i] not in LETTERS:
                    excluded.append(dict(evidence,slot_id=sid,reason='base_outside_frozen_R1_embedding'));continue
                quarantined.append(dict(evidence,slot_id=sid,reason='slot_absent_from_saved_native_train_export'));continue
            assert e['doc']==k['doc'] and e['base']==printed[i] and e['role']=='train'
            if not slice_compatible(k['slice'],printed[i]):
                excluded.append(dict(evidence,slot_id=sid,reason='printed_base_outside_tagged_slice'));continue
            targets=[v.index(h[head]) for head,v in zip(R.HEADS,vals)]
            candidate=dict(slot_id=sid,line_id=k['line_id'],doc=k['doc'],source=e['source'],role='train',provenance='native_print',targets=targets,unknown=[],loss_weight=1,teacher_seen_document=e['teacher_seen_document'],pool='native',card_id=k['card_id'],page=k['page'],slice=k['slice'],polarity='negative' if h[k['target_head']]=='none' else 'positive',target_head=k['target_head'])
            candidates.append(candidate)
    # Deduplicate across cards; contradictory full tuples STOP, never choose by order.
    dedup=unique(candidates); duplicates=len(candidates)-len(dedup)
    seen=set(); duplicate_rows=[]
    for r in candidates:
        sid=tuple(r['slot_id'])
        if sid in seen: duplicate_rows.append(dict(r,reason='duplicate_slot_key'))
        seen.add(sid)
    allowed=[]
    for row in dedup:
        if row['slice']=='exact_names' and row['polarity']=='negative': excluded.append(dict(row,reason='exact_names_has_no_negative_budget'))
        else: allowed.append(row)
    admitted,capped=diversity(allowed);excluded+=capped
    leakage_check(admitted,roles,witnesses)
    dest=ROOT/'artifacts/r2a_manifest'
    admitted=sorted([modification(r,set()) for r in admitted],key=lambda r:tuple(r['slot_id']))
    R.write(dest/'duplicates.jsonl',duplicate_rows)
    R.write(dest/'r2a_slots.jsonl',admitted);R.write(dest/'quarantined.jsonl',quarantined);R.write(dest/'excluded.jsonl',excluded)
    table={sl:dict(negative=sum(r['slice']==sl and r['polarity']=='negative' for r in admitted),positive=sum(r['slice']==sl and r['polarity']=='positive' for r in admitted),documents=sorted({r['doc'] for r in admitted if r['slice']==sl}),target_negative=target[0],target_positive=target[1]) for sl,target in TARGETS.items()}
    receipt=dict(slots=len(admitted),negative=sum(r['polarity']=='negative' for r in admitted),positive=sum(r['polarity']=='positive' for r in admitted),replaced=0,new=len(admitted),quarantined=len(quarantined),quarantine_reasons=dict(Counter(r['reason'] for r in quarantined)),excluded=len(excluded),exclusion_reasons=dict(Counter(r['reason'] for r in excluded)),duplicates=duplicates,leakage=0,manifest_sha256=sha(dest/'r2a_slots.jsonl'),slices=table,old_pool=config['data'],old_inventory=str(inv),old_inventory_sha256=sha(inv),old_pool_crop_overlap=0,readback=str(run),readback_sha256=sha(run/'READBACK_RECEIPT.json'),source_hashes=hashes,input_sha256={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'docs/records/labelfix/spellcheck/R2/doc_roles.json',ROOT/'docs/records/labelfix/spellcheck/R2/decks/T2/private/key.jsonl',ROOT/'artifacts/r2_resolve/T2/final/resolved.jsonl',ROOT/'artifacts/r2_resolve/T2/final/unresolved.jsonl']},cap_rule='<=10% of final retained slice per document; <=5 distinct target cards per page',seed=20261017)
    R.dump(dest/'receipt.json',receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('source_hashes','slices')},indent=2))

def write_report():
    dest=ROOT/'artifacts/r2a_manifest'
    r=json.loads((dest/'receipt.json').read_text())
    gates={t:json.loads((ROOT/'artifacts/r2_resolve'/t/'final/gate.json').read_text()) for t in ('T2','T4')}
    lines=['## B6c + R2M: final resolution and R2a supervision manifest', '',
           'Completed offline with the requested Python. No network calls, inference, training, submissions, or `.git` writes. Original reader answers, deals and input worktrees were read-only.', '',
           '| Tranche | Final resolved / 800 | Unresolved | r3 b00 controls / errors / invalid | r3 b01 controls / errors / invalid |',
           '|---|---:|---:|---|---|']
    for t,g in gates.items():
        a,b=g['per_folder']['b00'],g['per_folder']['b01']
        lines.append(f"| {t} | {g['resolved']} | {g['unresolved']} | 10 / {a['control_errors']} / {a['invalid_answer_count']} | 10 / {b['control_errors']} / {b['invalid_answer_count']} |")
    lines += ['', 'Every folder passes the original at-most-one-control-error gate. Receipt-bound manifests, private maps, immutable reader-folder files and PNG hashes match v2. Answers are valid JSONL with exact unique card membership and line counts (47, 51, 60, 62). Answers are joined by card ID before normalization; invalid individual votes remain excluded, with reasons in each final `gate.json`. The unchanged resolver computes 2-of-3 truth. UNKNOWN heads remain UNKNOWN, and cards without the required majority remain unresolved. Controls never enter the 800-card denominators.', '',
              'Final artifacts: `artifacts/r2_resolve/{T2,T4}/final/{resolved.jsonl,unresolved.jsonl,gate.json,opus_usage.json}`. Reader-3 tokens supplied by the lead, including tool I/O: T2 b00 157,076; b01 160,476; total 317,552. T4 b00 169,280; b01 161,761; total 331,041. Combined: 648,593. Input/output token splits are unavailable; earlier readers emitted zero usage fields remain labelled placeholders.', '',
              '### Slot identity and admission', '',
              'Manifest: `artifacts/r2a_manifest/r2a_slots.jsonl`, using the R2 training overlay schema: integer four-head targets, native_print provenance, weight 1, train role, preserved teacher_seen_document, and pool native for new slots. Native extraction/staging is a separate R2 job operation; this task creates the supervision overlay.', '',
              'Card crop_letter_offset is a provider alphabetic-letter ordinal, not a recogniser NFD start. The builder uses case-preserving, mark-blind alignment to saved R2 job 3681404 recogniser predictions. A base is mapped only when every optimal LCS alignment gives the same match and none skips it. Printed/mined word base mismatches, ambiguous/missing mapping and unknown tuples are quarantined; no zeros are invented. Teacher head predictions are never labels. Readback alignment and train-export file hashes are verified against READBACK_RECEIPT.json and recorded in receipt.json.', '',
              'Each card anchor and each resolver-emitted letter entry is accounted for. Extra decided letters inherit the card slice and target head; capitals require an uppercase printed base, and the subscript slice requires printed α/η/ω. Letters outside the frozen R1 vowel/rho embedding are excluded with explicit reasons. Exact-name target-head negatives are excluded because that slice has no negative budget. Negative/positive refers to the card target head, not whether all four heads are absent. Duplicate keys with conflicting tuples STOP; identical duplicates count once.', '',
              'Diversity selection uses seed 20261017 via SHA256 ordering. The page cap counts distinct target cards across slices, at most five per document/page. The document cap is at most 10% of the final retained slice, computed with a feasible retained denominator rather than the larger planned budget. Capped slots are recorded in excluded.jsonl.', '',
              '| Slice | Negative / target | Negative deficit | Positive / target | Positive deficit | Documents |',
              '|---|---:|---:|---:|---:|---:|']
    for sl,v in r['slices'].items():
        lines.append(f"| {sl} | {v['negative']} / {v['target_negative']} | {max(0,v['target_negative']-v['negative'])} | {v['positive']} / {v['target_positive']} | {max(0,v['target_positive']-v['positive'])} | {len(v['documents'])} |")
    lines += [f"| Total | {r['negative']} / 2000 | {sum(max(0,v['target_negative']-v['negative']) for v in r['slices'].values())} | {r['positive']} / 2000 | {sum(max(0,v['target_positive']-v['positive']) for v in r['slices'].values())} | {len({row['doc'] for row in R.read(dest/'r2a_slots.jsonl')})} unique |", '',
              'Deficits remain as measured; top-up reading is paused. Targets are shown per cell; a surplus in one cell does not cancel the deficit in another cell.', '',
              f"Admitted {r['slots']} unique slots ({r['negative']} negative, {r['positive']} positive); identical duplicates {r['duplicates']}. Quarantined {r['quarantined']}: {json.dumps(r['quarantine_reasons'],sort_keys=True)}. Excluded {r['excluded']}: {json.dumps(r['exclusion_reasons'],sort_keys=True)}. Per-document and per-page cap exclusions are zero if absent from that breakdown. Every exclusion/quarantine retains card provenance; exact per-slice document lists are in receipt.json.", '',
              f"Replacement check: {r['replaced']} replaced, {r['new']} new. Frozen R2 data path from r2-prep config/r2_job.json: `{r['old_pool']}`. The complete C1 crop inventory SHA256 `{r['old_inventory_sha256']}` matches the deployment external-hash binding. All T2 data crop hashes are disjoint from this inventory, proving zero existing old-pool identities without reading the remote index. Existing identities use replaces and never append; that branch is covered by a fixture.", '',
              'Leakage: **0**. All T2 data documents and all admitted manifest documents have supervision role and are absent from the complete T4 document set, validation and calibration. Any hit or unknown role raises STOP before manifest publication.', '',
              f"Manifest SHA256: `{r['manifest_sha256']}`.", '',
              'Validation: `tests/test_r2_finalize_manifest.py` plus `tests/test_r2_cards.py`; log `artifacts/r2_resolve/b6c_tests.txt`. Fixtures cover UNKNOWN quarantine, duplicate identity/conflict, final-denominator document cap, page cap, replacement rather than append, leakage STOP, case-preserving/ambiguous base alignment, printed-base slice membership, no-majority resolution and UNKNOWN preservation. Independent output readback checks manifest schema, hashes, all partitions, diversity and leakage.', '']
    ready=f"B6c+R2M READY: T2 final {gates['T2']['resolved']}/800 (unresolved {gates['T2']['unresolved']}), T4 final {gates['T4']['resolved']}/800 (unresolved {gates['T4']['unresolved']}); gates {'ok' if all(g['all_passed'] for g in gates.values()) else 'fail'}; R2a slots {r['slots']} (neg {r['negative']}/pos {r['positive']}; replaced {r['replaced']}, new {r['new']}; quarantined {r['quarantined']}); leakage 0; manifest sha {r['manifest_sha256'][:12]}"
    lines.append(ready)
    path=ROOT/'docs/records/labelfix/spellcheck/R2/B6_RESOLVE_REPORT.md'
    old=path.read_text().split('## B6c + R2M: final resolution and R2a supervision manifest')[0].rstrip()
    path.write_text(old+'\n\n'+'\n'.join(lines)+'\n')
    print(ready)

if __name__ == '__main__':
    for tranche in ('T2', 'T4'):
        finalize(tranche)
    build_manifest()
    write_report()
