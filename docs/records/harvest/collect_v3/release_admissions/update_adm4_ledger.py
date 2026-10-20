"""Update the ledger snapshot from ADM4; preserve prior numbers as history. Offline."""
import ast
from collections import Counter
import copy
import json
import math
from pathlib import Path
from build_w1_originals_v3 import BASE, OUT, OWNER_RULE, sha, obj, lines

LP = BASE / 'weak_ledger/ledger.json'
MD = BASE / 'WEAK_CATEGORY_LEDGER.md'
ADMISSION = OUT / 'w1_originals_v3.jsonl'
SUMMARY = OUT / 'w1_originals_v3_summary.json'
NOTE = (OWNER_RULE + ' Original-crop crop_ok rates of 53–82% for gazette, kosmopolis, lekythos and caps '
        'are measurement history, not admission blockers. Masks are the unchanged 1d measurement record; '
        'do not add masked counts to original admissions. W2 receipt counts remain exploratory and separate.')

def main():
    ledger = obj(LP)
    admissions = lines(ADMISSION)
    summary = obj(SUMMARY)
    relative = str(ADMISSION.relative_to(BASE.parents[2]))
    def fact(n, method):
        return {'value': n, 'source': [relative], 'method': method}
    # Reuse only the pure formatting function, never execute the live ledger builder.
    tree = ast.parse((BASE / 'weak_ledger/build_ledger.py').read_text())
    render_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'render')
    ns = {}
    exec(compile(ast.Module(body=[render_node], type_ignores=[]), '<ledger-render>', 'exec'), ns)
    render = ns['render']
    history_keys = ['collected_by_source_status', 'qualified_w1_union_rows', 'excluded_from_qualified_w1_rows',
                    'gap_to_quota_proxy_rows', 'cost_to_fill_proxy_gap']
    if 'adm4_history' not in ledger:
        ledger['adm4_history'] = {'note': 'Pre-ADM4 WCL1 accounting; historical counts and forecasts only.',
                                 'rows': [{k:copy.deepcopy(r[k]) for k in ['category'] + history_keys} for r in ledger['rows']],
                                 'status_policy':ledger['status_policy']}
    ledger['adm4'] = {'owner_rule':OWNER_RULE, 'crop_ok_notes':NOTE, 'admissions':relative,
                      'sha256':sha(ADMISSION), 'rows':len(admissions)}
    ledger['status_policy'] = NOTE
    for r in ledger['rows']:
        selected = [a for a in admissions if a['primary_class'] in r['primary_classes']]
        cnt = Counter(a['source'] for a in selected)
        w2 = [x for x in r['collected_by_source_status'] if x['tranche'] == 'W2 main receipt']
        r['collected_by_source_status'] = [
            {'tranche':'W1 release-v3 original', 'source_name':source,
             'counts':{'admitted':fact(n, 'ADM4 exact source and mapped primary-class count; marks status retained per row')}}
            for source,n in sorted(cnt.items())] + w2
        r['crop_ok_notes'] = NOTE
        r['collected_release_v3_original_rows'] = fact(len(selected), 'Count mapped primary classes in w1_originals_v3; masked record not added')
        r['qualified_w1_union_rows'] = fact(len(selected), 'ADM4 original admissions only; replaces historical C1/masked union')
        removed = sum(sum(v.get('removed_' + reason,0) for reason in summary['removals'])
                      for key,v in summary['counts_per_source_class'].items() if key.split('|')[1] in r['primary_classes'])
        r['excluded_from_qualified_w1_rows'] = fact(removed, 'Disjoint merged, rotated and registered-class removals from ADM4 eligible pool')
        w2n = sum(x['counts']['passed']['value'] for x in w2)
        gap = max(0, r['plan_quota_rows']['value']-len(selected)-w2n)
        r['gap_to_quota_proxy_rows'] = fact(gap, 'max(quota - ADM4 original rows - historical W2 main receipt usable, 0); planning proxy; final assurance pending')
        cost = r['cost_to_fill_proxy_gap']
        yieldn = cost.get('yield_rows_per_page',{}).get('value')
        if yieldn and 'rate_usd_per_page' in cost:
            pages = math.ceil(gap/yieldn)
            cost['pages'] = fact(pages, 'ceil(updated ADM4 proxy gap / historical W1 candidate yield); forecast only')
            cost['usd'] = fact(round(pages*cost['rate_usd_per_page']['value'],4), 'pages times historical plan rate; arithmetic only, no order or spend')
    ledger['input_sha256'][relative] = sha(ADMISSION)
    ledger['input_sha256'][str(SUMMARY.relative_to(BASE.parents[2]))] = sha(SUMMARY)
    legacy = OUT/'w1_masked_1d_summary.json'
    ledger['input_sha256'][str(legacy.relative_to(BASE.parents[2]))] = sha(legacy)
    # Update current registry bindings; historical values remain attached to old facts/history.
    for p,digest in summary['input_sha256'].items():
        p = Path(p)
        try: key = str(p.relative_to(BASE.parents[2]))
        except ValueError: key = str(p).replace(str(Path.home()), '~')
        ledger['input_sha256'][key] = digest
    def count_fields(d):
        if isinstance(d,dict):
            if 'value' in d: return (int(d.get('status') != 'not found'), int(d.get('status') == 'not found'))
            vals = [count_fields(v) for k,v in d.items() if k not in ['accounting','adm4_history']]
        elif isinstance(d,list): vals = [count_fields(v) for v in d]
        else: return (0,0)
        return tuple(sum(v[i] for v in vals) for i in range(2))
    sourced, missing = count_fields(ledger)
    ledger['accounting']['numbers_sourced'] = sourced
    ledger['accounting']['not_found'] = missing
    LP.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
    text = MD.read_text()
    # Existing full table stays in place, with current collection/gap cells replaced.
    updated = []
    for line in text.splitlines():
        if line.startswith('| Weak category / mapping |'):
            line = line.replace('Collected by source: passed / pending check / failed / unchecked','Collected: ADM4 W1 admitted; W2 historical receipt')
        for r in ledger['rows']:
            if line.startswith('| '+r['category']+'<br>'):
                cells = line.split(' | ')
                cells[3] = render(r['collected_by_source_status'])+'<br>crop_ok notes: '+NOTE
                cells[4] = 'Historical 1d measurement only; superseded for admission.<br>'+render(r['masked_by_arm_source'])
                cells[6] = render(r['gap_to_quota_proxy_rows'])+'<br>ADM4 W1 originals: '+render(r['qualified_w1_union_rows'])+'<br>ADM4 disjoint removals: '+render(r['excluded_from_qualified_w1_rows'])
                cells[7] = render(r['source_and_page_band_reads'])+'<br>'+render(r['cost_to_fill_proxy_gap'])
                line = ' | '.join(cells)
                break
        updated.append(line)
    text = '\n'.join(updated)+'\n'
    marker = '\n<!-- ADM4 CURRENT -->'
    if marker in text: text = text.split(marker)[0].rstrip()+'\n'
    # Mark prior prose as historical to avoid conflicting with the current cells.
    text = text.replace('W1 original passed/pending check/failed/unchecked from unchecked_strata.', 'Historical WCL1 policy (superseded for W1 admission by ADM4 below): original passed/pending check/failed/unchecked from unchecked_strata.')
    text = text.replace('combine the named masked arms by original row ID, subtract current W1 line-level exclusions,', 'use ADM4 W1 originals plus the historical W2 receipt,')
    text = text.replace('Original W1 failures remain visible even where a separate masked arm qualifies.', 'Historical W1 check failures remain in JSON history; current collected cells use ADM4 original admissions.')
    text += marker+'\n\nADM4 current admission and crop_ok notes: '+NOTE+'\n\n'
    text += '| Category | Current W1 original admissions | Historical WCL1 W1 qualified union | Historical proxy gap |\n|---|---:|---:|---:|\n'
    for r,old in zip(ledger['rows'],ledger['adm4_history']['rows']):
        text += f"| {r['category']} | {r['qualified_w1_union_rows']['value']} | {old['qualified_w1_union_rows']['value']} | {old['gap_to_quota_proxy_rows']['value']} |\n"
    text += '\nHistory note: all old collected-by-source/status numbers, qualified counts, gaps and cost projections are preserved verbatim in `weak_ledger/ledger.json` → `adm4_history`. '
    text += 'The old masked numbers remain above as measurement history. The historical build_ledger.py predates ADM4; do not use it to overwrite this snapshot. Reapply ADM4 with `python3 -B release_admissions/update_adm4_ledger.py` from this directory.\n'
    text = text.replace('Accounting: 494 numeric fact fields sourced; 39 explicit not-found fields.', 'Historical WCL1 accounting: 494 numeric fact fields sourced; 39 explicit not-found fields.')
    text += f'\nADM4 current accounting: {sourced} sourced numeric fact fields; {missing} explicit not-found fields; historical JSON snapshot excluded from these totals.\n'
    MD.write_text(text)

if __name__ == '__main__': main()
