"""Independent cached-component measurements and native loss witnesses."""
from __future__ import annotations
import sys,json,gzip
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]


def component_audit(prepared, labels, box, mask, owner_row, box_hits):
    """Measure actual native changes against detector-assigned components.

    Shared by the original dev audit and T6d. Unknown owners stay unknown;
    unassigned foreground is never silently called foreign text.
    """
    x0,y0,x1,y1=box
    own=prepared.get(owner_row)
    own_ids_before=set();own_ids_lost=set();lost=own_pixels=0
    if own is not None:
        before=box_hits(own,box)
        yy,xx=own['_y'][before],own['_x'][before];hit=mask[yy-y0,xx-x0]
        own_ids_before=set(labels[yy,xx]);own_ids_lost=set(labels[yy[hit],xx[hit]])
        own_ids_before.discard(0);own_ids_lost.discard(0)
        own_pixels=int(before.sum());lost=int(hit.sum())
    foreign_ids_before=set();foreign_ids_removed=set();foreign_ids_touched=set()
    foreign_before=foreign_removed=0
    for row in prepared.values():
        if own is None or row['row_id']==own['row_id']:continue
        before=box_hits(row,box);yy,xx=row['_y'][before],row['_x'][before]
        if not len(yy):continue
        ids=labels[yy,xx];hit=mask[yy-y0,xx-x0]
        foreign_before+=len(yy);foreign_removed+=int(hit.sum())
        for ident in np.unique(ids):
            if ident==0:continue
            sel=ids==ident;foreign_ids_before.add(int(ident))
            if hit[sel].any():foreign_ids_touched.add(int(ident))
            if hit[sel].all():foreign_ids_removed.add(int(ident))
    known=own is not None
    counts=dict(own_component_pixels_lost=lost if known else None,
        own_pixels=own_pixels if known else None,
        own_components_before=len(own_ids_before) if known else None,
        own_components_touched=len(own_ids_lost) if known else None,
        foreign_pixels_before=foreign_before if known else None,
        foreign_pixels_removed=foreign_removed if known else None,
        foreign_components_before=len(foreign_ids_before) if known else None,
        foreign_components_touched=len(foreign_ids_touched) if known else None,
        foreign_components_removed_from_crop=len(foreign_ids_removed) if known else None)
    return counts,own_ids_lost


def main():
    # Keep F2-specific imports out of the reusable measurement function.
    sys.path.insert(0,str(OUT));import run as current
    prior=current.prior
    records=prior.rows(OUT/'dev/records.jsonl');groups=defaultdict(list)
    for r in records:groups[r['page_id']].append(r)
    features,_=prior.bind();byid={r['id']:r for r in features};audits=[];witnesses=[]
    font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',14)
    directory=OUT/'dev/witnesses';directory.mkdir(parents=True,exist_ok=True)
    for group in groups.values():
        native,prepared,original,_,_,prov=prior.page_bundle([byid[r['id']] for r in group])
        with np.load(Path(prov['cache'])/'labels.npz') as archive:labels=archive['labels']
        for r in group:
            x0,y0,x1,y1=r['old_box']
            with Image.open(OUT/r['original_path']) as image:a=np.array(image)
            with Image.open(OUT/r['masked_path']) as image:b=np.array(image)
            mask=np.any(a!=b,axis=2) if a.ndim==3 else a!=b
            counts,own_ids_lost=component_audit(prepared,labels,r['old_box'],mask,
                                               r['cached_owner_row'],prior.OWN.box_hits)
            lost=counts['own_component_pixels_lost']
            assert lost==r['own_pixels_lost']
            audit=dict(id=r['id'],source=r['stratum'],card=r['dev']['card_id'],crop_ok=r['dev']['crop_ok'],
                changed=r['changed'],**counts)
            audits.append(audit)
            if r['dev']['crop_ok']=='y' and lost:
                # Every affected native region, grouped by observed label, with
                # untouched context. These are witnesses, not a semantic relabel.
                for label in sorted(own_ids_lost):
                    yy,xx=np.nonzero((labels[y0:y1,x0:x1]==label)&mask)
                    left=max(0,int(xx.min())-10);right=min(x1-x0,int(xx.max())+11)
                    top=max(0,int(yy.min())-14);bottom=min(y1-y0,int(yy.max())+15)
                    old=Image.fromarray(a[top:bottom,left:right]).convert('RGB')
                    new=Image.fromarray(b[top:bottom,left:right]).convert('RGB')
                    scale=min(3.,650/max(1,old.width),180/max(1,old.height))
                    size=(max(1,round(old.width*scale)),max(1,round(old.height*scale)))
                    tile=Image.new('RGB',(1400,220),'#e3e3e3');draw=ImageDraw.Draw(tile)
                    draw.text((5,3),f"{r['stratum']} {r['dev']['card_id']} component {label} lost {len(yy)} | native crop x={left}:{right} y={top}:{bottom}",font=font,fill='black')
                    tile.paste(old.resize(size),(10,30));tile.paste(new.resize(size),(710,30))
                    name=f"{r['stratum']}_{r['dev']['card_id']}_label{label}.png";tile.save(directory/name)
                    witnesses.append(dict(id=r['id'],card=r['dev']['card_id'],source=r['stratum'],component_id=int(label),lost_pixels=len(yy),path=f'dev/witnesses/{name}'))
    prior.write_rows(OUT/'dev/component_audit.jsonl',audits);prior.write_rows(OUT/'dev/loss_witnesses.jsonl',witnesses)
    summary={}
    for source in (*prior.SOURCES,'overall'):
        rr=[r for r in audits if source=='overall' or r['source']==source];n=[r for r in rr if r['crop_ok']=='n'];y=[r for r in rr if r['crop_ok']=='y']
        summary[source]=dict(own_y_components=sum(r['own_components_before'] or 0 for r in y),
            own_y_components_touched=sum(r['own_components_touched'] or 0 for r in y),
            n_foreign_components=sum(r['foreign_components_before'] or 0 for r in n),
            n_foreign_components_removed=sum(r['foreign_components_removed_from_crop'] or 0 for r in n),
            n_foreign_components_touched=sum(r['foreign_components_touched'] or 0 for r in n))
    prior.write_json(OUT/'dev/component_summary.json',summary);print(summary,flush=True)

if __name__=='__main__':main()
