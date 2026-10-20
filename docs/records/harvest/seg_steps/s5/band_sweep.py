"""S5 step B: length-band sweep, stability and changed lines. Proposal only.

Input: s5/band_population.jsonl (from build_population.py). Outputs: s5/sweep.json,
s5/changed_lines.jsonl, s5/owner_cases.json and s5/BAND_PROPOSAL.md.

Rule 2 is reproduced exactly as segmentation-policy.js::boxLengthJudgement:
r = (chars+1)/(expected+1); KEEP iff L <= r <= U (r < L too little, r > U too much).
End to end = rule-2 KEEP and rule-3 padding (unchanged, <= 1.5) KEEP; the gate is
already PASS for every population line.

Objective = false drops (owner KEEP not kept) + false keeps (owner DROP kept),
equal weights, over the population minus the owner DROPs whose note says the
output is wrong or the length is correct ("length cannot see this"). Those lines
are counted in their own column and never enter the objective.
Tie rule for a single proposed point: fewest total errors, then nearest to the
current band (|L-0.5|+|U-1.5|), then lower L, then lower U.
"""
import json, hashlib
from pathlib import Path
from collections import Counter
import numpy as np

D = Path(__file__).resolve().parent
LS = [round(.30 + .05 * i, 2) for i in range(11)]
US = [round(1.20 + .05 * i, 2) for i in range(27)]
GRID = [(L, U) for L in LS for U in US]
CUR = (0.5, 1.5)
SEED = 20261019
NBOOT = 1000
GROUPS = {
    'overall': lambda r: True,
    'numeric': lambda r: r['output_type'] == 'numeric',
    'non-numeric': lambda r: r['output_type'] == 'non-numeric',
    'mixed': lambda r: r['output_type'] == 'mixed',
    'small': lambda r: r['small'],
    'non-small': lambda r: not r['small'],
}


def read(p):
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]


def write(p, rows):
    with open(p, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True, allow_nan=False) + '\n')


def in_band(r, L, U):
    return L <= r['r'] <= U


def keep(r, L, U, e2e):
    return in_band(r, L, U) and (not e2e or r['padding_state'] == 'KEEP')


def verdict(r, L, U):
    if r['r'] < L:
        return 'DROP (too little)'
    if r['r'] > U:
        return 'DROP (too much)'
    return {'KEEP': 'KEEP', 'DROP': 'DROP (padding)'}.get(r['padding_state'], 'UNCERTAIN (padding)')


def errors(rows, L, U, e2e):
    obj = [r for r in rows if not r['length_blind']]
    fd = sum(r['owner_mark'] == 'KEEP' and not keep(r, L, U, e2e) for r in obj)
    fk = sum(r['owner_mark'] == 'DROP' and keep(r, L, U, e2e) for r in obj)
    lb = [r for r in rows if r['length_blind']]
    return dict(fd=fd, fk=fk, total=fd + fk, blind_n=len(lb), blind_kept=sum(keep(r, L, U, e2e) for r in lb))


def matrix(rows, e2e):
    """E[g, i] = 1 if grid point g misclassifies objective line i."""
    obj = [r for r in rows if not r['length_blind']]
    rr = np.array([r['r'] for r in obj]); y = np.array([r['owner_mark'] == 'KEEP' for r in obj])
    pad = np.array([(r['padding_state'] == 'KEEP') or not e2e for r in obj])
    E = np.zeros((len(GRID), len(obj)), dtype=np.int64)
    for g, (L, U) in enumerate(GRID):
        k = (rr >= L) & (rr <= U) & pad
        E[g] = (y & ~k) | (~y & k)
    return E, obj


DIST = np.array([abs(L - CUR[0]) + abs(U - CUR[1]) for L, U in GRID])
LARR = np.array([L for L, _ in GRID]); UARR = np.array([U for _, U in GRID])
CUR_G = GRID.index(CUR)


def pick(totals):
    order = np.lexsort((UARR, LARR, np.round(DIST, 6), totals))
    return int(order[0])


def optimum(rows, e2e=True):
    if not [r for r in rows if not r['length_blind']]:
        return None
    E, _ = matrix(rows, e2e); tot = E.sum(1); g = pick(tot)
    ties = [GRID[i] for i in np.flatnonzero(tot == tot.min())]
    return dict(L=GRID[g][0], U=GRID[g][1], total=int(tot[g]), ties=ties)


def sweep_group(rows):
    out = {}
    for mode, e2e in (('length_alone', False), ('end_to_end', True)):
        grid = [dict(L=L, U=U, **errors(rows, L, U, e2e)) for L, U in GRID]
        best = min(g['total'] for g in grid)
        ties = [g for g in grid if g['total'] == best]
        opt = optimum(rows, e2e)
        out[mode] = dict(
            n=len(rows), n_objective=sum(not r['length_blind'] for r in rows),
            owner=dict(Counter(r['owner_mark'] for r in rows)),
            current=dict(L=CUR[0], U=CUR[1], **errors(rows, *CUR, e2e)),
            lower_alone=[dict(L=L, U=CUR[1], **errors(rows, L, CUR[1], e2e)) for L in LS],
            upper_alone=[dict(L=CUR[0], U=U, **errors(rows, CUR[0], U, e2e)) for U in US],
            joint_min_total=best, joint_ties=ties,
            proposed=dict(L=opt['L'], U=opt['U'], **errors(rows, opt['L'], opt['U'], e2e)) if opt else None,
            grid=grid)
    return out


def h(line_id):
    return int(hashlib.sha256(line_id.encode()).hexdigest(), 16) % 2


def heldout(train, test, label):
    opt = optimum(train)
    if opt is None:
        return dict(held_out=label, n_train=len(train), n_test=len(test), fit=None)
    return dict(held_out=label, n_train=len(train), n_test=len(test), n_test_objective=sum(not r['length_blind'] for r in test),
                fit_L=opt['L'], fit_U=opt['U'], fit_ties=len(opt['ties']),
                test_fitted=errors(test, opt['L'], opt['U'], True), test_current=errors(test, *CUR, True))


def bootstrap(rows, proposed):
    E, obj = matrix(rows, True)
    rng = np.random.default_rng(SEED); n = len(obj)
    Ls, Us, cur_opt, prop_opt, gain = [], [], 0, 0, []
    pg = GRID.index(proposed)
    for _ in range(NBOOT):
        c = np.bincount(rng.integers(0, n, n), minlength=n)
        tot = E @ c; g = pick(tot)
        Ls.append(GRID[g][0]); Us.append(GRID[g][1])
        cur_opt += int(tot[CUR_G] == tot.min()); prop_opt += int(tot[pg] == tot.min())
        gain.append(int(tot[CUR_G] - tot[pg]))
    q = lambda xs: {str(p): float(np.percentile(xs, p)) for p in (2.5, 25, 50, 75, 97.5)}
    return dict(resamples=NBOOT, seed=SEED, n=n, L_quantiles=q(Ls), U_quantiles=q(Us),
                L_freq=dict(sorted(Counter(Ls).items())), U_freq=dict(sorted(Counter(Us).items())),
                current_is_optimal=cur_opt, proposed_is_optimal=prop_opt,
                errors_saved_by_proposed_vs_current=q(gain), saved_le_0=sum(x <= 0 for x in gain))


OWNER_CASES = [
    ('gazette_modern--52ee6226bb7d4834--s000-l0122', 'S2 vertical witness, letter-spaced caps "ΠΟΛΕΩΣ"; owner KEEP, drops on too-little (r≈0.35)'),
    ('gazette_modern--82115ca04c55f5b7--s000-l0005', 'S2 vertical witness; owner KEEP, drops on too-little'),
    ('gazette_modern--80e8a42cbf8e629f--s000-l0120', 'S1 witness; owner DROP: "should have been dropped ... more than 2 full words ... the output length is correct"'),
    ('elstat--0877c813a8512b56--s000-l0037', 'S2 vertical witness; owner KEEP, drops on padding'),
    ('gazette_modern--6d6a6fe53e769b59--s000-l0009', 'S2 vertical witness; owner KEEP, drops on padding'),
    ('ia_poly1850--df8f2267db2b7275--s025-l0037', 'S3 curved-row witness; owner KEEP'),
    ('129cff40-p000009-l0107', 'S1 witness; owner KEEP: "accents of ἔχει are detected as second line"'),
]


def table(head, rows):
    cell = lambda a: str(a).replace('|', '\\|').replace('\n', ' ')
    return '\n'.join(['| ' + ' | '.join(head) + ' |', '| ' + ' | '.join(['---'] * len(head)) + ' |'] +
                     ['| ' + ' | '.join(cell(a) for a in row) + ' |' for row in rows])


def f3(x):
    return f'{x:.3f}' if isinstance(x, float) else x


def main():
    P = read(D / 'band_population.jsonl'); X = read(D / 'excluded.jsonl')
    conflicts = read(D / 'owner_conflicts.jsonl'); receipt = json.loads((D / 'population_receipt.json').read_text())
    sweep = {name: sweep_group([r for r in P if f(r)]) for name, f in GROUPS.items()}
    prop = {g: (sweep[g]['end_to_end']['proposed']['L'], sweep[g]['end_to_end']['proposed']['U']) for g in ('overall', 'numeric')}
    numeric = [r for r in P if r['output_type'] == 'numeric']
    # Stability
    stab = {}
    for g, rows in (('overall', P), ('numeric', numeric)):
        halves = [[r for r in rows if h(r['line_id']) == k] for k in (0, 1)]
        stab[g] = dict(
            split_half=[heldout(halves[0], halves[1], 'hash half 1 (fit on half 0)'), heldout(halves[1], halves[0], 'hash half 0 (fit on half 1)')],
            loso_source_set=[heldout([r for r in rows if r['source_set'] != s], [r for r in rows if r['source_set'] == s], s) for s in sorted({r['source_set'] for r in rows})],
            loso_cohort=[heldout([r for r in rows if r['cohort'] != s], [r for r in rows if r['cohort'] == s], s) for s in sorted({r['cohort'] for r in rows})],
            bootstrap=bootstrap(rows, prop[g]))
    # Changed lines
    changed, reason_only = [], []
    for scheme, rows in (('overall', P), ('numeric', numeric)):
        L, U = prop[scheme]
        for r in rows:
            a, b = verdict(r, *CUR), verdict(r, L, U)
            if a != b and (a == 'KEEP') == (b == 'KEEP'):
                reason_only.append(dict(scheme=scheme, line_id=r['line_id'], text=r['text'], r=r['r'], owner_mark=r['owner_mark'], current=a, proposed=b))
            if (a == 'KEEP') != (b == 'KEEP'):
                changed.append(dict(scheme=scheme, band=f'{L:.2f}-{U:.2f}', line_id=r['line_id'], text=r['text'], r=r['r'], chars=r['chars'],
                                    owner_mark=r['owner_mark'], owner_note=r['owner_note'], output_type=r['output_type'], small=r['small'],
                                    source_set=r['source_set'], cohort=r['cohort'], padding=r['padding'], current=a, proposed=b,
                                    effect=('fixes' if (b == 'KEEP') == (r['owner_mark'] == 'KEEP') else 'breaks') if not r['length_blind'] else 'length cannot see this',
                                    length_blind=r['length_blind']))
    write(D / 'changed_lines.jsonl', changed)
    neighbours = {g: neighbour_moves([r for r in P if GROUPS[g](r)], prop[g]) for g in ('overall', 'numeric')}
    weights = {g: weight_sensitivity([r for r in P if GROUPS[g](r)]) for g in ('overall', 'numeric')}
    # Owner cases
    byid = {r['line_id']: r for r in P}; xid = {r['line_id']: r for r in X}
    replay = {}
    for l in open(D.parent / 's4/replay.jsonl', encoding='utf-8'):
        z = json.loads(l)
        if z['line_id'] in {c for c, _ in OWNER_CASES}:
            replay[z['line_id']] = z
    cases = []
    for cid, why in OWNER_CASES:
        r = byid.get(cid)
        if r:
            cases.append(dict(line_id=cid, why=why, in_population=True, owner_mark=r['owner_mark'], owner_note=r['owner_note'], r=r['r'], padding=r['padding'],
                              output_type=r['output_type'], small=r['small'], current=verdict(r, *CUR), proposed_overall=verdict(r, *prop['overall']),
                              proposed_numeric=verdict(r, *prop['numeric']) if r['output_type'] == 'numeric' else 'n/a (not numeric)', length_blind=r['length_blind']))
        else:
            z = replay.get(cid); x = xid.get(cid)
            cases.append(dict(line_id=cid, why=why, in_population=False, owner_mark=x['owner_mark'] if x else None,
                              exclusion=x['exclusion'] if x else 'no owner judgement in (a)/(b)/(c)',
                              s4=(z['after']['verdict'] + ': ' + z['after']['reason']) if z else None))
    (D / 'owner_cases.json').write_text(json.dumps(cases, ensure_ascii=False, indent=1))
    # Short false-rejects outside small (NOTES_FOR_LATER_STEPS step-5 note)
    short_out = [r for r in P if r['owner_mark'] == 'KEEP' and not r['small'] and r['chars'] <= 10 and not in_band(r, *CUR)]
    summary = dict(population=receipt, proposed=prop, stability=stab, owner_cases=cases, neighbour_moves=neighbours, fk_weight_sensitivity=weights, reason_only_changes=reason_only,
                   short_owner_keep_outside_small=dict(n=len(short_out), kept_by_proposed_overall=sum(in_band(r, *prop['overall']) for r in short_out),
                                                       ids=[r['line_id'] for r in short_out]))
    (D / 'sweep.json').write_text(json.dumps(dict(grid=dict(L=LS, U=US), tie_rule='min total, then min |L-0.5|+|U-1.5|, then lower L, then lower U',
                                                  objective='false drops + false keeps over the population minus length-blind owner DROPs',
                                                  groups=sweep, **summary), ensure_ascii=False, indent=1))
    report(P, X, conflicts, receipt, sweep, prop, stab, changed, cases, short_out, neighbours, weights, reason_only)


def neighbour_moves(rows, band):
    """Lines whose end-to-end keep/drop differs between the proposed band and each adjacent grid point."""
    L, U = band; out = []
    for dL, dU in ((-.05, 0), (.05, 0), (0, -.05), (0, .05)):
        L2, U2 = round(L + dL, 2), round(U + dU, 2)
        if (L2, U2) not in GRID:
            continue
        diff = [r for r in rows if keep(r, L, U, True) != keep(r, L2, U2, True)]
        out.append(dict(L=L2, U=U2, lines_moved=len(diff), owner=dict(Counter(r['owner_mark'] + (' (length-blind)' if r['length_blind'] else '') for r in diff)),
                        errors=errors(rows, L2, U2, True), ids=[r['line_id'] for r in diff]))
    return out


def weight_sensitivity(rows):
    """Diagnostic only: optimum when a false keep costs w false drops."""
    E_obj = [r for r in rows if not r['length_blind']]
    out = []
    n_keep = sum(r['owner_mark'] == 'KEEP' for r in E_obj); n_drop = sum(r['owner_mark'] == 'DROP' for r in E_obj)
    for w in (1, 2, 3, round(n_keep / n_drop, 2)):
        best = None
        for L, U in GRID:
            e = errors(rows, L, U, True); cost = e['fd'] + w * e['fk']
            key = (round(cost, 6), round(abs(L - CUR[0]) + abs(U - CUR[1]), 6), L, U)
            if best is None or key < best[0]:
                best = (key, L, U, e)
        c = errors(rows, *CUR, True)
        out.append(dict(w=w, L=best[1], U=best[2], fd=best[3]['fd'], fk=best[3]['fk'], current_fd=c['fd'], current_fk=c['fk'], balanced=(w == round(n_keep / n_drop, 2))))
    return out


def err_s(e):
    return f"{e['fd']}/{e['fk']} (total {e['total']}; length-blind kept {e['blind_kept']}/{e['blind_n']})"


def report(P, X, conflicts, receipt, sweep, prop, stab, changed, cases, short_out, neighbours, weights, reason_only):
    o, nm = prop['overall'], prop['numeric']
    so, sn = sweep['overall'], sweep['numeric']
    lines = ['# SEG step 5 — length-band proposal from the owner marks (0.9-s4 measurement)', '',
             '**Proposal only. Not an adoption.** No tool, rule, test or existing file changed. The only free parameters are the lower bound L and the upper bound U of rule 2, fitted separately for all lines ("overall") and for numeric lines. Non-numeric, small, non-small and mixed are diagnostics.', '',
             'Rule 2 as in `segmentation-policy.js::boxLengthJudgement`: r = (Google chars + 1) / (predicted chars + 1); KEEP iff L ≤ r ≤ U. "End to end" adds rule 3 (padding ≤ 1.5, unchanged); every population line already passed rule 1. **fd** = false drops (owner KEEP, tool does not keep). **fk** = false keeps (owner DROP, tool keeps). The objective is fd + fk, equally weighted. Owner KEEP outnumbers owner DROP 434 : 66 in the population, so an equal-weight total favours keeping; every table shows fd and fk separately so another weighting can be read off.', '',
             '## 1. Population and exclusions', '',
             f"Owner judgements: (a) owner_marks_20261019 (240 entries / 235 IDs), (b) the 135 explicit 888 ratings, (c) 185 typology marks. Joined exactly as `s4/validate_report.py`: explicit marks beat ratings; among explicit marks the latest `updated` wins (Athens-local strings → UTC, `Z` strings as UTC), then list order. Result: **{receipt['judged_ids']} judged IDs**. Row data come from `s4/replay.jsonl` (1,288 rows), then `s4/typology_replay.jsonl` for IDs not in the main replay; typology controls carry no marks.", '',
             table(['Set', 'n'], [['Judged IDs', receipt['judged_ids']], ['Excluded: gate DROP', receipt['exclusion_reasons'].get('gate DROP', 0)], ['Excluded: gate UNCERTAIN', receipt['exclusion_reasons'].get('gate UNCERTAIN', 0)], ['Excluded: gate PASS but no usable box/prediction', receipt['exclusion_reasons'].get('no usable box/prediction', 0)], ['**Band population**', receipt['population']], ['… of which owner DROPs that length cannot see (not in the objective)', sum(receipt['length_blind'].values())], ['Objective population', receipt['population'] - sum(receipt['length_blind'].values())]]), '',
             'Readback: on every population line, the current 0.5–1.5 band plus padding 1.5 reproduces the saved 0.9-s4 verdict.', '',
             table(['Population breakdown', 'Counts'], [['Owner mark', receipt['owner_marks']], ['Judgement source (source set)', receipt['source_sets']], ['Line cohort', receipt['cohorts']], ['Output type', receipt['output_types']], ['Small (chars ≤ 8 and A ≤ 6)', receipt['small']], ['Padding (rule 3) state', dict(Counter(r['padding_state'] for r in P))]]), '',
             '### Excluded owner-judged lines (not the band\'s job)', '',
             table(['ID', 'Cohort', 'Exclusion', 'Owner', 'Owner note', 'S4 reason'], [[x['line_id'], x['cohort'], x['exclusion'], x['owner_mark'], x['owner_note'], x['gate_reason_s4']] for x in sorted(X, key=lambda x: (x['exclusion'], x['owner_mark'], x['line_id']))]), '',
             f"Excluded by mark: {receipt['excluded_by_reason_and_mark']}.", '',
             '### Owner DROPs that length cannot see', '',
             'Selected on the literal owner note only: the note says the Google output is wrong ("wrong output", "actual output is …", "wrong reading", "bad output") or that the length is correct ("length is correct", "correct char count", "evenly matched per chars"). They are counted in a separate "length-blind kept" column and never enter the objective. Typology DROPs with Sol `final_text=wrong` but no owner note (HARIAZ, IIIXX, БАЦИМА) are **not** in this set; they stay in the objective.', '',
             table(['ID', 'Text', 'r', 'Category', 'Owner note', 'Current'], [[r['line_id'], r['text'], f3(r['r']), r['length_blind'], r['owner_note'], verdict(r, *CUR)] for r in P if r['length_blind']]), '',
             '### Owner judgement conflicts', '',
             table(['ID', 'Chosen', 'All judgements'], [[c['line_id'], f"{c['chosen']['owner_mark']} ({c['chosen'].get('sheet') or c['chosen']['source']}, {c['chosen']['updated']})", '; '.join(f"{j['owner_mark']} ({j.get('sheet') or j['source']}, {j['updated']})" for j in c['judgments'])] for c in conflicts]), '',
             '## 2. Sweep', '',
             f"Grid: L = {LS[0]}…{LS[-1]} step 0.05; U = {US[0]}…{US[-1]} step 0.05 (inclusive). Cells read fd/fk (total; length-blind kept). Full grids for every group and both modes are in [sweep.json](sweep.json).", '']
    for g in ('overall', 'numeric', 'non-numeric', 'small', 'non-small', 'mixed'):
        s = sweep[g]; e, a = s['end_to_end'], s['length_alone']
        flag = ' — **too few lines; indicative only**' if g == 'mixed' else (' — diagnostic' if g not in ('overall', 'numeric') else '')
        lines += [f"### {g} (n = {e['n']}, objective n = {e['n_objective']}, owner {e['owner']}){flag}", '',
                  table(['Band', 'Length alone fd/fk', 'End to end fd/fk'], [['current 0.50–1.50', err_s(a['current']), err_s(e['current'])],
                        [f"joint optimum (tie rule) {e['proposed']['L']:.2f}–{e['proposed']['U']:.2f}", err_s(dict(**errors([r for r in P if GROUPS[g](r)], e['proposed']['L'], e['proposed']['U'], False))), err_s(e['proposed'])]]), '',
                  f"Joint minimum end-to-end total {e['joint_min_total']}; every tie (L–U fd/fk): " + ', '.join(f"{t['L']:.2f}–{t['U']:.2f} {t['fd']}/{t['fk']}" for t in e['joint_ties']) + '.', '',
                  f"Length alone: joint minimum total {a['joint_min_total']}; ties: " + ', '.join(f"{t['L']:.2f}–{t['U']:.2f} {t['fd']}/{t['fk']}" for t in a['joint_ties']) + '.', '']
        if g in ('overall', 'numeric'):
            lines += ['Lower bound alone (U = 1.50):', '', table(['L', 'Length alone fd/fk (total)', 'End to end fd/fk (total)', 'Length-blind kept'], [[f"{x['L']:.2f}", f"{x['fd']}/{x['fk']} ({x['total']})", f"{y['fd']}/{y['fk']} ({y['total']})", y['blind_kept']] for x, y in zip(a['lower_alone'], e['lower_alone'])]), '',
                      'Upper bound alone (L = 0.50):', '', table(['U', 'Length alone fd/fk (total)', 'End to end fd/fk (total)', 'Length-blind kept'], [[f"{x['U']:.2f}", f"{x['fd']}/{x['fk']} ({x['total']})", f"{y['fd']}/{y['fk']} ({y['total']})", y['blind_kept']] for x, y in zip(a['upper_alone'], e['upper_alone'])]), '']
    # r distribution near the floor
    obj = [r for r in P if not r['length_blind']]
    below = lambda lo, hi, m: sum(lo <= r['r'] < hi and r['owner_mark'] == m for r in obj)
    lines += ['### Owner marks by r interval (objective population, all types)', '',
              table(['r interval', 'owner KEEP', 'owner DROP'], [[f'[{lo}, {hi})', below(lo, hi, 'KEEP'), below(lo, hi, 'DROP')] for lo, hi in [(0, .2), (.2, .25), (.25, .30), (.30, .35), (.35, .40), (.40, .45), (.45, .50), (.50, .55), (.55, .60), (.6, 1.4), (1.4, 1.5), (1.5, 1.6), (1.6, 1.8), (1.8, 2.0), (2.0, 2.25), (2.25, 2.5), (2.5, 99)]]), '',
              f"L = 0.30 is the floor of the requested grid. Below it the objective population has {sum(r['r'] < .30 and r['owner_mark'] == 'KEEP' for r in obj)} owner KEEP and {sum(r['r'] < .30 and r['owner_mark'] == 'DROP' for r in obj)} owner DROP lines, so extending the grid lower adds owner DROPs faster than owner KEEPs: [0.25, 0.30) holds {below(.25, .30, 'KEEP')} KEEP / {below(.25, .30, 'DROP')} DROP.", '']
    # Proposal
    co, po = so['end_to_end']['current'], so['end_to_end']['proposed']
    cn, pn = sn['end_to_end']['current'], sn['end_to_end']['proposed']
    cla, pla = so['length_alone']['current'], errors(P, *o, False)
    cnla, pnla = sn['length_alone']['current'], errors(numeric_rows(P), *nm, False)
    lines += ['## 3. Proposed bounds (from the end-to-end joint optimum and the tie rule)', '',
              'Tie rule: fewest total errors, then nearest to the current band (|L − 0.5| + |U − 1.5|), then lower L, then lower U.', '',
              table(['Scheme', 'Band', 'Length alone fd/fk', 'End to end fd/fk (padding 1.5 unchanged)'],
                    [['overall, current', '0.50–1.50', err_s(cla), err_s(co)], [f'**overall, proposed**', f'**{o[0]:.2f}–{o[1]:.2f}**', err_s(pla), err_s(po)],
                     ['numeric, current', '0.50–1.50', err_s(cnla), err_s(cn)], [f'**numeric, proposed**', f'**{nm[0]:.2f}–{nm[1]:.2f}**', err_s(pnla), err_s(pn)],
                     ['numeric lines under the overall proposal', f'{o[0]:.2f}–{o[1]:.2f}', err_s(errors(numeric_rows(P), *o, False)), err_s(errors(numeric_rows(P), *o, True))]]), '',
              f"Overall: fd {co['fd']} → {po['fd']} ({po['fd'] - co['fd']:+d}), fk {co['fk']} → {po['fk']} ({po['fk'] - co['fk']:+d}); length-blind kept {co['blind_kept']} → {po['blind_kept']} of {po['blind_n']}.", '',
              f"Numeric: fd {cn['fd']} → {pn['fd']} ({pn['fd'] - cn['fd']:+d}), fk {cn['fk']} → {pn['fk']} ({pn['fk'] - cn['fk']:+d}); length-blind kept {cn['blind_kept']} → {pn['blind_kept']} of {pn['blind_n']}. A separate numeric band would be an output-type switch in the tool. On these {len(numeric_rows(P))} numeric lines the overall proposal {o[0]:.2f}–{o[1]:.2f} gives the same keep/drop as the numeric proposal {nm[0]:.2f}–{nm[1]:.2f} on {sum(keep(r, *o, True) == keep(r, *nm, True) for r in numeric_rows(P))} of {len(numeric_rows(P))} lines (row 'numeric lines under the overall proposal').", '',
              '### How many lines each bound move rests on', '',
              f"From current to proposed (overall): the lower bound 0.50 → {o[0]:.2f} changes {sum(o[0] <= r['r'] < .5 for r in P)} lines (owner KEEP {sum(o[0] <= r['r'] < .5 and r['owner_mark'] == 'KEEP' for r in P)}, owner DROP {sum(o[0] <= r['r'] < .5 and r['owner_mark'] == 'DROP' for r in P)}); the upper bound 1.50 → {o[1]:.2f} changes {sum(1.5 < r['r'] <= o[1] for r in P)} lines (owner KEEP {sum(1.5 < r['r'] <= o[1] and r['owner_mark'] == 'KEEP' for r in P)}, owner DROP {sum(1.5 < r['r'] <= o[1] and r['owner_mark'] == 'DROP' for r in P)}). Counts include length-blind and padding-dropped lines.", '',
              'One grid step away from each proposed point (end to end):', '',
              table(['Scheme', 'Neighbour band', 'Lines whose keep/drop differs from the proposal', 'Their owner marks', 'Neighbour fd/fk (total)'], [[g, f"{x['L']:.2f}–{x['U']:.2f}", x['lines_moved'], x['owner'], f"{x['errors']['fd']}/{x['errors']['fk']} ({x['errors']['total']})"] for g in ('overall', 'numeric') for x in neighbours[g]]), '',
              '### Diagnostic: unequal costs', '',
              'Not part of the proposal. If a false keep is counted as w false drops, the end-to-end optimum (same tie rule) is:', '',
              table(['Scheme', 'w', 'Optimum', 'fd/fk', 'Current fd/fk'], [[g, str(x['w']) + (' (class-balanced: KEEP n / DROP n)' if x['balanced'] else ''), f"{x['L']:.2f}–{x['U']:.2f}", f"{x['fd']}/{x['fk']}", f"{x['current_fd']}/{x['current_fk']}"] for g in ('overall', 'numeric') for x in weights[g]]), '',
              'The judged sets are not a random sample of the census (the typology sheet holds small crops; the deskew sheet holds verdict flips; the cells sheet holds census samples), so all counts in this report are counts of owner-judged lines, not census error rates.', '']
    lines += stability_md(stab, o, nm)
    # Changed lines
    lines += ['## 5. Lines whose verdict changes (proposed vs current 0.50–1.50, end to end)', '',
              f"[changed_lines.jsonl](changed_lines.jsonl). Overall scheme: {sum(c['scheme'] == 'overall' for c in changed)} lines ({dict(Counter(c['effect'] for c in changed if c['scheme'] == 'overall'))}). Numeric scheme (numeric lines only): {sum(c['scheme'] == 'numeric' for c in changed)} lines ({dict(Counter(c['effect'] for c in changed if c['scheme'] == 'numeric'))}). 'fixes' = new keep/drop agrees with the owner; 'breaks' = it now disagrees. Lines that stay DROP but change reason are not counted: " + ('; '.join(f"{x['scheme']}: {x['line_id']} ({x['text']}, r {x['r']:.3f}, owner {x['owner_mark']}) {x['current']} → {x['proposed']}" for x in reason_only) or 'none') + '.', '']
    for scheme in ('overall', 'numeric'):
        cs = sorted([c for c in changed if c['scheme'] == scheme], key=lambda c: c['r'])
        lines += [f'### {scheme} scheme ({cs[0]["band"] if cs else ""})', '',
                  table(['ID', 'Text', 'r', 'Owner', 'Type', 'Small', 'Current', 'Proposed', 'Effect', 'Owner note'],
                        [[c['line_id'], c['text'][:40], f3(c['r']), c['owner_mark'], c['output_type'], c['small'], c['current'], c['proposed'], c['effect'], c['owner_note']] for c in cs]), '']
    # Owner cases
    lines += ['## 6. Owner cases from steps 1–3', '',
              table(['ID', 'Case', 'In population', 'Owner', 'r', 'Padding', 'Current', f'Proposed overall {o[0]:.2f}–{o[1]:.2f}', 'Proposed numeric'],
                    [[c['line_id'], c['why'], c['in_population'], c.get('owner_mark'), f3(c.get('r', '')), f3(c.get('padding', '')), c.get('current', c.get('exclusion')), c.get('proposed_overall', c.get('s4', '')), c.get('proposed_numeric', '')] for c in cases]), '',
              owner_case_notes(cases, o),
              '',
              f"Short owner-KEEP lines outside small (chars ≤ 10, non-small, currently dropped by length; the step-5 note in NOTES_FOR_LATER_STEPS.md): {len(short_out)} in this population; the overall proposal keeps {sum(in_band(r, *o) for r in short_out)} of them by length.", '',
              table(['ID', 'Text', 'Chars', 'r', f'Proposed {o[0]:.2f}–{o[1]:.2f}'], [[r['line_id'], r['text'], r['chars'], f3(r['r']), verdict(r, *o)] for r in sorted(short_out, key=lambda r: r['r'])]), '']
    lines += ['## Files and reproduction', '',
              '- [band_population.jsonl](band_population.jsonl): one row per population line (id, source set, cohort, chars, output type, small, r, padding, owner mark/note/source, 0.9-s4 verdict and reason, length_blind).',
              '- [excluded.jsonl](excluded.jsonl), [owner_conflicts.jsonl](owner_conflicts.jsonl), [population_receipt.json](population_receipt.json) (input SHA-256s).',
              '- [sweep.json](sweep.json): full grids per group and mode, stability, bootstrap, owner cases. [changed_lines.jsonl](changed_lines.jsonl). [owner_cases.json](owner_cases.json).',
              '- Reproduce: `python3 -B s5/build_population.py && python3 -B s5/band_sweep.py` (sol-recut .venv; numpy). Read-only over s4 and the owner files; no tool, OCR, reader, network or git write.', '']
    co, po = sweep['overall']['end_to_end']['current'], sweep['overall']['end_to_end']['proposed']
    cn, pn = sweep['numeric']['end_to_end']['current'], sweep['numeric']['end_to_end']['proposed']
    sh = [x['test_current']['total'] - x['test_fitted']['total'] for x in stab['overall']['split_half']]
    lo = [x['test_current']['total'] - x['test_fitted']['total'] for k in ('loso_source_set', 'loso_cohort') for x in stab['overall'][k]]
    bo, bn = stab['overall']['bootstrap'], stab['numeric']['bootstrap']
    nb = {(x['L'], x['U']): x['lines_moved'] for x in neighbours['overall']}
    n_changed = len({c['line_id'] for c in changed})
    summary = ['## Summary', '',
               table(['Item', 'Value'], [
                   ['Population (excluded)', f"{receipt['population']} ({receipt['excluded']}: gate DROP {receipt['exclusion_reasons'].get('gate DROP', 0)}, gate UNCERTAIN {receipt['exclusion_reasons'].get('gate UNCERTAIN', 0)}, no box 0)"],
                   ['Owner DROPs length cannot see (outside the objective)', sum(receipt['length_blind'].values())],
                   ['Overall, current 0.50–1.50, end to end fd/fk', f"{co['fd']}/{co['fk']}"],
                   [f"Overall, proposed {o[0]:.2f}–{o[1]:.2f}, end to end fd/fk", f"{po['fd']}/{po['fk']}"],
                   ['Numeric, current, end to end fd/fk', f"{cn['fd']}/{cn['fk']}"],
                   [f"Numeric, proposed {nm[0]:.2f}–{nm[1]:.2f}, end to end fd/fk", f"{pn['fd']}/{pn['fk']} (the overall proposal gives the same verdicts on all numeric lines)"],
                   ['Held-out errors saved, split half (both ways)', sh],
                   ['Held-out errors saved, leave-one-set-out (source sets, then cohorts)', lo],
                   ['Bootstrap optimal L, 2.5–97.5 % (0.30 is the grid floor)', f"{bo['L_quantiles']['2.5']:.2f}–{bo['L_quantiles']['97.5']:.2f}"],
                   ['Bootstrap optimal U, 2.5–97.5 %', f"{bo['U_quantiles']['2.5']:.2f}–{bo['U_quantiles']['97.5']:.2f}"],
                   ['Bootstrap resamples where proposed saves ≤ 0 errors vs current', f"{bo['saved_le_0']}/{bo['resamples']} (numeric {bn['saved_le_0']}/{bn['resamples']})"],
                   ['Lines separating the proposal from its grid neighbours', f"L {o[0]:.2f} vs {o[0]+.05:.2f}: {nb.get((round(o[0]+.05, 2), o[1]))}; U {o[1]:.2f} vs {o[1]-.05:.2f}: {nb.get((o[0], round(o[1]-.05, 2)))}; U {o[1]:.2f} vs {o[1]+.05:.2f}: {nb.get((o[0], round(o[1]+.05, 2)))}"],
                   ['Changed lines (overall scheme; numeric-scheme changes are a subset)', n_changed],
                   ['Class-balanced cost (diagnostic, not proposed)', 'optimum ' + next(f"{x['L']:.2f}–{x['U']:.2f} fd/fk {x['fd']}/{x['fk']}" for x in weights['overall'] if x['balanced'])]]), '',
               f"Reading of the table: moving both bounds outward reduces owner-KEEP false drops by {co['fd'] - po['fd']} and adds {po['fk'] - co['fk']} owner-DROP false keeps on these judged lines; the overall gain holds on every held-out split (numeric held-out gains are 0–6 lines). The exact point is not pinned down: {o[0]:.2f} vs {o[0]+.05:.2f} and {o[1]:.2f} vs its neighbours each rest on 1–3 lines, and the bootstrap U spans {bo['U_quantiles']['2.5']:.2f}–{bo['U_quantiles']['97.5']:.2f}. With equal costs the optimum widens the band; with class-balanced costs it narrows it (section 3).", '']
    i = lines.index('## 1. Population and exclusions'); lines[i:i] = summary
    sl = sweep['overall']['end_to_end']
    ready = (f"SEG S5 READY: population {receipt['population']} (excluded {receipt['excluded']}); current 0.5–1.5 errors overall {co['fd']}/{co['fk']}; proposed overall {o[0]:.2f}–{o[1]:.2f} errors {po['fd']}/{po['fk']}; "
             f"numeric current {cn['fd']}/{cn['fk']} → proposed {nm[0]:.2f}–{nm[1]:.2f} {pn['fd']}/{pn['fk']}; stability held-out gain on every overall split (numeric 0–6 lines), gain ≤ 0 in 0/1000 bootstraps, exact bounds rest on 1–3 lines (bootstrap U {bo['U_quantiles']['2.5']:.2f}–{bo['U_quantiles']['97.5']:.2f}); changed lines {n_changed}")
    lines += [ready, '']
    (D / 'ready_line.txt').write_text(ready + '\n', encoding='utf-8')
    (D / 'BAND_PROPOSAL.md').write_text('\n'.join(lines), encoding='utf-8')


def owner_case_notes(cases, o):
    c = {x['line_id']: x for x in cases}
    a, b, g = c['gazette_modern--52ee6226bb7d4834--s000-l0122'], c['gazette_modern--82115ca04c55f5b7--s000-l0005'], c['gazette_modern--80e8a42cbf8e629f--s000-l0120']
    return (f"ΠΟΛΕΩΣ (r {a['r']:.3f}) and l0005 (r {b['r']:.3f}): owner KEEP; current {a['current']} / {b['current']}; under {o[0]:.2f}–{o[1]:.2f} they become {a['proposed_overall']} / {b['proposed_overall']}. "
            f"Gazette l0120 (owner DROP, note: the output length is correct; the line should drop on >2 whole neighbour words): r {g['r']:.3f}; current {g['current']}, i.e. it drops on length today; under {o[0]:.2f}–{o[1]:.2f} length keeps it and the 0.9-s4 gate passes it, so end to end it becomes {g['proposed_overall']} against the owner DROP. "
            "It is in the 'length cannot see this' column, not in the objective. The two padding witnesses (elstat l0037, gazette l0009) stay DROP (padding) under the proposal.")


def numeric_rows(P):
    return [r for r in P if r['output_type'] == 'numeric']


def stability_md(stab, o, nm):
    out = ['## 4. Stability', '',
           'Every fit uses the same tie rule on the training part and counts end-to-end errors (fd/fk, length-blind excluded) on the held-out part, for the fitted band and for the current 0.50–1.50.', '']
    for g, band in (('overall', o), ('numeric', nm)):
        s = stab[g]
        rows = []
        for kind in ('split_half', 'loso_source_set', 'loso_cohort'):
            for x in s[kind]:
                if x.get('fit_L') is None:
                    rows.append([kind, x['held_out'], x['n_train'], x['n_test'], 'no objective lines', '', '', '']); continue
                tf, tc = x['test_fitted'], x['test_current']
                rows.append([kind, x['held_out'], x['n_train'], x['n_test'], f"{x['fit_L']:.2f}–{x['fit_U']:.2f}", f"{tc['fd']}/{tc['fk']} ({tc['total']})", f"{tf['fd']}/{tf['fk']} ({tf['total']})", tc['total'] - tf['total']])
        b = s['bootstrap']
        out += [f'### {g} (proposed {band[0]:.2f}–{band[1]:.2f})', '',
                table(['Check', 'Held out', 'n train', 'n held out', 'Fitted band', 'Held-out current fd/fk (total)', 'Held-out fitted fd/fk (total)', 'Errors saved'], rows), '',
                f"Bootstrap ({b['resamples']} resamples of the {b['n']} objective lines, seed {b['seed']}): optimal L quantiles 2.5/25/50/75/97.5 % = {', '.join(f'{v:.2f}' for v in b['L_quantiles'].values())}; optimal U = {', '.join(f'{v:.2f}' for v in b['U_quantiles'].values())}.", '',
                f"L frequency: {b['L_freq']}. U frequency: {b['U_freq']}.", '',
                f"Current 0.50–1.50 is a tied optimum in {b['current_is_optimal']}/{b['resamples']} resamples; the proposed band in {b['proposed_is_optimal']}/{b['resamples']}. Errors saved by the proposed band over current, per resample, quantiles 2.5/25/50/75/97.5 % = {', '.join(f'{v:g}' for v in b['errors_saved_by_proposed_vs_current'].values())}; ≤ 0 in {b['saved_le_0']}/{b['resamples']}.", '']
    return out


if __name__ == '__main__':
    main()
