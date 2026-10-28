"""Build summary.csv (one row per trial) and curves.csv (dev loss every 50k drawn lines) from the copied records."""
import csv, glob, json, os, sys

here = sys.argv[1]
INSTR = ('harvest_dev', 'seal04_dev')
rows, curves = [], []
for tpath in sorted(glob.glob(os.path.join(here, 'trials', '*.json'))):
    name = os.path.basename(tpath)[:-5]
    t = json.load(open(tpath))
    p = t['parameters']
    run = os.path.join(here, 'runs', name)
    loss = []
    if os.path.exists(os.path.join(run, 'loss_eval.jsonl')):
        loss = [json.loads(l) for l in open(os.path.join(run, 'loss_eval.jsonl'))]
    for e in loss:
        curves.append(dict(trial=name, width_mult=p['width_mult'], drawn_lines=e['drawn_lines'],
                           **{i + '_ctc_loss': e['instruments'][i]['ctc_loss'] for i in INSTR}))
    ev = sorted(glob.glob(os.path.join(run, 'eval', 'step-*.json')))
    r = dict(trial=name, width_mult=p['width_mult'], lr=p['lr'], beta1=p['beta1'], wd=p['wd'],
             total_updates=t['total_updates'], loss_evals_done=len(loss), loss_evals_planned=26,
             status='failed' if glob.glob(os.path.join(run, 'FAILURE_*.json')) else
                    'complete' if ev else 'running' if loss else 'not_started')
    if loss:
        for i in INSTR:
            r['last_' + i + '_ctc_loss'] = loss[-1]['instruments'][i]['ctc_loss']
        r['last_loss_drawn_lines'] = loss[-1]['drawn_lines']
    if ev:
        ins = json.load(open(ev[-1]))['instruments']
        ed = sum(ins[i]['score']['cer']['nfd_atom']['edits'] for i in INSTR)
        ru = sum(ins[i]['score']['cer']['nfd_atom']['reference_units'] for i in INSTR)
        r['pooled_nfd_cer'] = ed / ru
        for i in INSTR:
            s = ins[i]['score']
            r[i + '_nfd_cer'] = s['cer']['nfd_atom']['rate']
            r[i + '_nfc_cer'] = s['cer']['nfc_char']['rate']
            r[i + '_wer'] = s['wer']['rate']
            r[i + '_exact_line_rate'] = s['exact_line_rate']
    rows.append(r)
keys = []
for r in rows:
    keys += [k for k in r if k not in keys]
with open(os.path.join(here, 'summary.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, keys); w.writeheader(); w.writerows(rows)
with open(os.path.join(here, 'curves.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, ['trial', 'width_mult', 'drawn_lines'] + [i + '_ctc_loss' for i in INSTR])
    w.writeheader(); w.writerows(curves)
done = sum(r['status'] == 'complete' for r in rows)
print('trials', len(rows), 'complete', done, 'curve points', len(curves))
