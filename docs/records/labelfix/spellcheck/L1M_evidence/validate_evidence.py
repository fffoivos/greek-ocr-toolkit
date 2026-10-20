"""Independent joins/counts/native-pixel checks for the saved L1M audit."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
def load(p):return list(map(json.loads,gzip.open(p,'rt')))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def validate():
    checks={};total_lines=0;total_flags=0;total_blobs=0;all_lines={}
    for sample in ('200','vouli'):
        root=HERE/sample
        if not (root/'receipt.json').exists():continue
        receipt=json.loads((root/'receipt.json').read_text())
        for filename,digest in receipt['outputs'].items():assert sha(root/filename)==digest
        lines=load(root/'lines.jsonl.gz');details={r['id']:r for r in load(root/'details.jsonl.gz')}
        all_lines.update({r['id']:r for r in lines})
        flags=load(root/'border_flags.jsonl.gz');blobs=load(root/'border_blobs.jsonl.gz')
        suffix='_vouli' if sample=='vouli' else ''
        ids=set((HERE.parent/f'L1M_masking_sample_ids{suffix}.txt').read_text().split())
        assert len(lines)==len(ids)==len(details)==receipt['lines']
        assert {r['id'] for r in lines}==ids==set(details)
        assert all(all(r['saved_original_gate_parity'].values()) for r in lines)
        blobmap={(b['id'],b['key']):b for b in blobs};assert len(blobmap)==len(blobs)
        flagmap={(f['id'],f['start'],f['edge']):f for f in flags};assert len(flagmap)==len(flags)
        for r in lines:
            key=r['id'];d=details[key]
            with np.load(root/'pixels'/f'{key}.npz') as p:
                before=p['original_ink'];after=p['masked_ink'];labels=p['original_labels']
                assert int(p['changed_pixels'].sum())==r['changed_pixels']
                if r['source']['match_status']!='ok':assert not p['changed_pixels'].any()
                for s in d['detector']['original']['slots']:
                    for edge,y in [('top',0),('bottom',before.shape[0]-1)]:
                        flagged=bool(s.get('evidence',{}).get('clipped_'+edge))
                        token=(key,s['start'],edge)
                        assert flagged==(token in flagmap)
                        if not flagged:continue
                        f=flagmap[token];lo,hi=f['window'];xx=np.flatnonzero(before[y,lo:hi])+lo
                        assert xx.tolist()==f['border_ink_x']
                        expected={int(z) for z in labels[y,xx]};assert 0 not in expected
                        assert expected=={blobmap[(key,b)]['label'] for b in f['blob_keys']}
                for b in (b for b in blobs if b['id']==key):
                    xx,yy=np.asarray(b['native_pixels']).T
                    assert (labels[yy,xx]==b['label']).all() and before[yy,xx].all()
                    assert len(xx)==int((labels==b['label']).sum())==b['pixels']
                    assert int((~after[yy,xx]).sum())==b['pixels_no_longer_ink']
            for v in ('original','masked'):
                assert len(d['detector'][v]['slots'])==r['counts'][v]['slots']
                for mode in ('ENSEMBLE_AB','PRESENCE'):
                    o=d['overlays'][v][mode]
                    assert o['status']==r['status'][v][mode]
                    assert bool(o['hold_slots'])==(o['status']=='hold')
                    assert dict(Counter(h['detail'] for h in o['hold_slots']))==r['reasons'][v][mode]
                    gate_entries=Counter((h['start'],h['base'],z) for h in d['modes'][v][mode]['hold_slots'] for z in h['reasons'])
                    overlay_entries=Counter((h['start'],h['letter'],h['detail']) for h in o['hold_slots'] if h['letter'])
                    assert gate_entries==overlay_entries
        for edge in ('top','bottom'):
            original=sum(r['counts']['original']['clipped_'+edge] for r in lines)
            masked=sum(r['counts']['masked']['clipped_'+edge] for r in lines)
            ff=[f for f in flags if f['edge']==edge]
            new=sum(sum(f['edge']==edge for f in r['new_clipping_flags']) for r in lines)
            assert len(ff)==original and sum(f['persists'] for f in ff)+new==masked
        checks[sample]=dict(lines=len(lines),flags=len(flags),blobs=len(blobs),all_native_blob_pixels_checked=True,
            all_flag_to_blob_joins_checked=True,all_original_saved_gate_decisions_match=True,
            all_gate_to_overlay_reason_joins_match=True,failed_matches_included_unchanged=True)
        total_lines+=len(lines);total_flags+=len(flags);total_blobs+=len(blobs)
    for name in ('visual_selection.json','flip_visual_selection.json'):
        selected=json.loads((HERE/name).read_text());assert len(selected)==len({r['id'] for r in selected})==12
        if name.startswith('flip'):
            for r in selected:
                line=all_lines[r['id']]
                assert line['status']['original']['ENSEMBLE_AB']=='hold' and line['status']['masked']['ENSEMBLE_AB']!='hold'
    reviewed=json.loads((HERE/'visual_review.json').read_text())
    for p,digest in reviewed['images'].items():assert sha(HERE/p)==digest
    report=HERE.parent/'L1M_REPORT.md';body=report.read_text()
    assert 'Visual inspection pending' not in body
    for target in re.findall(r'\]\(([^)]+)\)',body):
        if not target.startswith(('https:','http:','#')):assert (report.parent/target).exists(),target
    # Verify the one-command absent-vouli path preserves the completed report.
    vouli=Path('/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/v2_masked/l1e_sample_vouli/receipt.json')
    pending_check=None
    if not vouli.exists():
        old=sha(report)
        p=subprocess.run([sys.executable,str(HERE/'run_pair.py'),'--sample','vouli'],capture_output=True,text=True,check=True)
        assert 'vouli pending' in p.stdout and sha(report)==old
        pending_check=p.stdout.strip()
    receipt=dict(complete=True,paired_analysis_lines=total_lines,all_original_clipping_flags=total_flags,
        all_original_border_blobs=total_blobs,checks=checks,visual_panels_reviewed=24,reviewed_images_including_sheets=len(reviewed['images']),
        vouli_pending_command_check=pending_check,report_sha256=sha(report),ownership='undecidable; saved ownership masks unavailable')
    (HERE/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':validate()
