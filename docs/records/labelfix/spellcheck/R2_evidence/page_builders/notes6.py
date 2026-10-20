import gzip, json
B='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/'
want={'95a8decfdafb3b75d6549383-p000103-l0015':'τ','1c3c81f346537e276486e9fd-p000032-l0046':'Τ','240e6345063d-p000005-l0042':None,'b963a5d59be557e9eef8498b-p000065-l0055':None,'2d29e5e76d90adc4cc1b093a-p000037-l0038':None,'f77a8c0084022edb7981fb15-p000055-l0044':None}
for l in gzip.open(B+'l1e_20261017/l1r_sf6_3680729/release/overlay_ensemble_ab.jsonl.gz','rt'):
    r=json.loads(l)
    if r['line_id'] not in want: continue
    print('==', r['line_id'], r['status'], r['composed_text'])
    for g in sorted(r['gate_decisions'], key=lambda g:g['start']):
        A=g.get('r1_parts'); Bp=(g.get('peer_prediction') or {}).get('parts'); ev=g['evidence']
        if A or Bp or g.get('detector_parts') or g['hold_reasons']:
            print('  ', g['start'], g['base'], 'A',A,'B',Bp,'det',g.get('detector_parts'),'clipT',ev.get('clipped_top'),'hold',g['hold_reasons'][:3], 'probs', {k:round(v,2) for k,v in ((g.get('peer_prediction') or {}).get('mark_probabilities') or {}).items()})
