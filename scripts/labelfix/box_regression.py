"""Regression check between two page builds: mark boxes lost / added / moved per line, and reading changes.

Standard step of every detector or reader cycle (owner, 16 Oct 2026): "checking for regression should be standard part of your work
cycle ... test for the presence of different boxes on the line from previous versions."

Inputs are the `--boxes-out` sidecars written by the owner-page builder (line_id -> reading, boxes [{kind, bbox}], letters [[x0, x1]]).
Boxes match when they have the same kind and IoU >= --iou (default 0.3); a matched pair whose IoU < 0.6 is reported as moved.
Each changed box is tied to the page's slot number (letter components sorted by x, from 1) by horizontal centre.
With --notes (owner note files, jsonl with line_id/note), lines are split into: judged correct (empty note), reviewed with a note
(a change at a slot number the note names is 'at a named slot', otherwise 'implicitly approved'), and unreviewed.

Usage: python scripts/labelfix/box_regression.py OLD.json NEW.json [--notes a.jsonl b.jsonl] [--out diff.json]
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import json
import re
from collections import Counter
import numpy as np
from scipy.optimize import linear_sum_assignment
from scripts.labelfix.owner_implicit_changes import mentioned_slots


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0.0


def slot_of(box, letters):
    """Assign only inside an explicit mark zone; ambiguous/outside stays unassigned."""
    cx,cy=(box[0]+box[2])/2,(box[1]+box[3])/2
    hits=[]
    for i,letter in enumerate(letters):
        zone=letter.get('mark_zone') if isinstance(letter,dict) else letter
        if zone is None or len(zone)!=4:continue  # legacy x ranges cannot certify a mark zone
        inside=zone[0]<=box[0] and box[2]<=zone[2] and zone[1]<=box[1] and box[3]<=zone[3]
        if inside:hits.append(letter.get('display_slot',i+1) if isinstance(letter,dict) else i+1)
    return hits[0] if len(hits)==1 else None


def diff_line(old, new, thr):
    lost,added,moved=[],[],[]
    changes={k:[] for k in ('owner_changed','pixels_changed','status_changed','pixels_unknown','owner_unknown','status_unknown')}
    # Canonical order also makes equal-weight choices independent of input order.
    aa=sorted(old['boxes'],key=lambda b:(b['kind'],b['bbox']))
    bb=sorted(new['boxes'],key=lambda b:(b['kind'],b['bbox']))
    n,m=len(aa),len(bb);weight=np.zeros((n+m,n+m))
    for i,a in enumerate(aa):
        for j,b in enumerate(bb):
            ov=iou(a['bbox'],b['bbox'])
            if a['kind']==b['kind'] and ov>=thr:
                weight[i,j]=min(n,m)+1+ov  # maximum cardinality, then total IoU
    ii,jj=linear_sum_assignment(weight,maximize=True)
    matched={i:j for i,j in zip(ii,jj) if i<n and j<m and weight[i,j]>0}
    used=set(matched.values())
    oldzones=old.get('letter_zones',old.get('letters',[]));newzones=new.get('letter_zones',new.get('letters',[]))
    for i,a in enumerate(aa):
        oldslot=slot_of(a['bbox'],oldzones)
        if i not in matched:
            lost.append(dict(a,slot=oldslot,old_slot=oldslot,namespace='old',ownership='assigned' if oldslot else 'unassigned'))
        else:
            b=bb[matched[i]];ov=iou(a['bbox'],b['bbox'])
            newslot=slot_of(b['bbox'],newzones)
            oldowner=a.get('display_slot');newowner=b.get('display_slot')
            delta=dict(kind=a['kind'],old=a,new=b,iou=ov,old_slot=oldslot,new_slot=newslot,
                       old_display_slot=oldowner,new_display_slot=newowner)
            if a['kind']!='quote' and (oldowner is None or newowner is None):changes['owner_unknown'].append(delta)
            elif oldowner!=newowner:changes['owner_changed'].append(delta)
            def pixels(box):
                runs=box.get('pixel_runs')
                if runs is None:return None
                x0,y0=box['bbox'][:2]
                return {(y+y0,x+x0) for y,lo,hi in runs for x in range(lo,hi)}
            ap,bp=pixels(a),pixels(b)
            if ap is None or bp is None:changes['pixels_unknown'].append(delta)
            elif ap!=bp or set(a.get('source_ids') or [])!=set(b.get('source_ids') or []):changes['pixels_changed'].append(delta)
            if a.get('status') is None or b.get('status') is None:changes['status_unknown'].append(delta)
            elif a['status']!=b['status']:changes['status_changed'].append(delta)
            if ov<.6:
                newslot=slot_of(b['bbox'],newzones)
                moved.append(dict(kind=a['kind'],old=a['bbox'],new=b['bbox'],iou=round(ov,2),slot=oldslot,
                                  old_slot=oldslot,new_slot=newslot,namespace='old/new'))
    for j,b in enumerate(bb):
        if j not in used:
            slot=slot_of(b['bbox'],newzones)
            added.append(dict(b,slot=slot,new_slot=slot,namespace='new',ownership='assigned' if slot else 'unassigned'))
    return dict(**changes,lost=lost,added=added,moved=moved,reading_old=old['reading'],reading_new=new['reading'],reading_changed=old['reading']!=new['reading'])


def compare_pages(old,new,thr):
    result={}
    empty=dict(boxes=[],letters=[],reading='')
    for lid in sorted(set(old)|set(new)):
        d=diff_line(old.get(lid,empty),new.get(lid,empty),thr)
        d['line_status']='missing_old' if lid not in old else 'missing_new' if lid not in new else 'both'
        result[lid]=d
    return result


def review_scope(change,kind,oldline,named,status):
    """Notes refer to reviewed OLD slots; a new slot number is never an alias."""
    if status=='unreviewed':return 'unreviewed'
    oldslot=change.get('old_slot')
    if kind=='added':
        oldslot=slot_of(change['bbox'],oldline.get('letter_zones',[]))
    change['reviewed_old_slot']=oldslot
    if oldslot is None:return 'unresolved reviewed owner'
    return 'at a named slot' if status=='reviewed with note' and oldslot in named else 'implicitly approved'


def validate_review_binding(path, old, notes):
    """A caller explicitly binds each exact notes file to the reviewed snapshot."""
    if not path:raise ValueError('notes require --review-binding before approval language')
    binding=json.loads(Path(path).read_text())
    expected={str(p):hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in notes}
    if not old.get('page_sha256') or binding.get('reviewed_page_sha256')!=old['page_sha256']:
        raise ValueError('notes binding does not identify reviewed page')
    if binding.get('notes_sha256')!=expected:raise ValueError('notes binding hash mismatch')
    page=Path(binding['reviewed_page'])
    if hashlib.sha256(page.read_bytes()).hexdigest()!=old['page_sha256']:
        raise ValueError('reviewed page bytes differ')
    return binding


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('old'); ap.add_argument('new')
    ap.add_argument('--notes', nargs='*', default=[]); ap.add_argument('--iou', type=float, default=0.3); ap.add_argument('--out')
    ap.add_argument('--review-binding',help='JSON: reviewed_page, reviewed_page_sha256, notes_sha256 keyed by notes path')
    a = ap.parse_args()
    old, new = json.load(open(a.old)), json.load(open(a.new))
    if a.notes:validate_review_binding(a.review_binding,old,a.notes)
    old=old.get('lines',old);new=new.get('lines',new)
    notes = {}
    for f in a.notes:
        for l in open(f):
            r = json.loads(l); notes[r['line_id']] = (r.get('note') or '').strip()
    out, tot = {}, Counter()
    for lid,d in compare_pages(old,new,a.iou).items():
        if lid not in notes:
            status = 'unreviewed'
        elif not notes[lid]:
            status = 'judged correct'
        else:
            status = 'reviewed with note'
        named = mentioned_slots(notes.get(lid,''))
        for k in ('lost', 'added', 'moved','owner_changed','pixels_changed','status_changed'):
            for b in d[k]:
                b['scope'] = review_scope(b,k,old.get(lid,{}),named,status)
                tot[(status, k, b['scope'])] += 1
        for key in ('owner_unknown','pixels_unknown','status_unknown'):
            tot[('coverage',key,'unresolved')]+=len(d[key])
        d['status'] = status
        if d['line_status']!='both' or d['lost'] or d['added'] or d['moved'] or any(d[k] for k in ('owner_changed','pixels_changed','status_changed')) or d['reading_changed']:
            out[lid] = d
    summary = {' / '.join(k): v for k, v in sorted(tot.items())}
    summary['lines missing old']=len(set(new)-set(old));summary['lines missing new']=len(set(old)-set(new))
    summary['lines compared'] = len(set(old) & set(new)); summary['lines with any change'] = len(out)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    if a.out:
        json.dump(dict(summary=summary, lines=out), open(a.out, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
