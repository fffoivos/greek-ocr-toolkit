"""Compare notes against a hash-bound reviewed page and its original slot geometry.

No current analyser, CTC remapping, neighbour widening, or DB absence inference.
"""
import argparse
import hashlib
import json
import re
import unicodedata as ud
from pathlib import Path
from greekocr.labelfix.text import clusters,nfd


def mentioned_slots(note):
    """Only slot-shaped clauses; counts, dates and unrelated integers are not IDs."""
    out=set()
    clauses=re.findall(r'\b(?:at|slots?)\s+(\d+(?:\s*[-–]\s*\d+)?(?:\s*[,/&]\s*\d+(?:\s*[-–]\s*\d+)?)*)',note,re.I)
    clauses+=re.findall(r'(?<![\d-])\b\d{1,3}\s*[-–]\s*\d{1,3}\b(?![\d-])',note)
    for clause in clauses:
        for a,b in re.findall(r'(\d+)(?:\s*[-–]\s*(\d+))?',clause):
            lo,hi=int(a),int(b or a)
            if 0<lo<=hi<=999:out.update(range(lo,hi+1))
    return out


def marks_by_letter(text):
    return [(c.base,''.join(sorted(c.marks))) for c in clusters(nfd(text)) if c.base.isalpha()]


def compare(old,new,notes):
    result=[]
    for note in notes:
        lid=note['line_id'];text=(note.get('note') or '').strip()
        if lid not in old or lid not in new:
            result.append(dict(line=lid,kind='unresolved',reason='missing target line'));continue
        a,b=old[lid],new[lid];ma,mb=marks_by_letter(a['reading']),marks_by_letter(b['reading'])
        slots=a.get('line_reading',{}).get('slots',a.get('slots',[]))
        if len(ma)!=len(mb) or [x[0] for x in ma]!=[x[0] for x in mb]:
            result.append(dict(line=lid,kind='unresolved',reason='letters differ'));continue
        if len(slots)!=len(ma):
            result.append(dict(line=lid,kind='unresolved',reason='old sidecar lacks reviewed slot geometry'));continue
        named=mentioned_slots(text)
        present={s.get('display_slot') for s in slots}
        for missing in sorted(named-present):
            result.append(dict(line=lid,slot=missing,kind='unresolved',reason='missing target slot'))
        for i,(x,y) in enumerate(zip(ma,mb)):
            if x==y:continue
            s=slots[i];sl=s.get('display_slot')
            if sl is None or not s.get('bbox'):
                kind='unresolved'
            elif sl in named:kind='at a slot the note mentions'
            else:kind='REGRESSION? (reviewed snapshot approval)'
            result.append(dict(line=lid,old_slot=sl,new_slot=(b.get('line_reading',{}).get('slots') or [{}]*len(ma))[i].get('display_slot'),
                               old_bbox=s.get('bbox'),before=ud.normalize('NFC',''.join(x)),after=ud.normalize('NFC',''.join(y)),kind=kind,note=text))
    return result


def bound_sidecar(page,sidecar,expected_page_sha256):
    digest=hashlib.sha256(Path(page).read_bytes()).hexdigest()
    if digest!=expected_page_sha256:raise ValueError('reviewed page snapshot hash mismatch')
    data=json.loads(Path(sidecar).read_text())
    if data.get('page_sha256')!=digest:raise ValueError('sidecar not bound to page snapshot')
    return data['lines']


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for flag in ('old-page','new-page','old-boxes','new-boxes','reviewed-page-sha256','new-page-sha256','notes','out'):
        ap.add_argument('--'+flag,required=True)
    ap.add_argument('--review-binding',help='JSON binding exact notes bytes to the reviewed page')
    a=ap.parse_args()
    old=bound_sidecar(a.old_page,a.old_boxes,a.reviewed_page_sha256)
    new=bound_sidecar(a.new_page,a.new_boxes,a.new_page_sha256)
    from scripts.labelfix.box_regression import validate_review_binding
    binding=validate_review_binding(a.review_binding,dict(page_sha256=a.reviewed_page_sha256),[a.notes])
    notes=[json.loads(l) for l in Path(a.notes).read_text().splitlines()]
    data=dict(reviewed_page_sha256=a.reviewed_page_sha256,old_sidecar_sha256=hashlib.sha256(Path(a.old_boxes).read_bytes()).hexdigest(),
              note_set=a.notes,notes_sha256=binding['notes_sha256'],review_binding=binding,
              review_binding_sha256=hashlib.sha256(Path(a.review_binding).read_bytes()).hexdigest(),changes=compare(old,new,notes))
    Path(a.out).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
