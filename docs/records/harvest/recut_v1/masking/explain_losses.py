"""Capture unchanged _voronoi_keep inputs for three inspected native failures."""
from pathlib import Path
import sys,gzip,json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
sys.path.insert(0,str(OUT));sys.path.insert(0,str(ROOT))
import run as current
from greekocr.glyphs import foreign_ink as cutter
from greekocr.glyphs.components import EIGHT
prior=current.prior


def main():
    rr=prior.rows(OUT/'dev/records.jsonl');observed=[]
    original=cutter._voronoi_keep
    for card,label in [('c023',3136),('c040',1886),('c019',1503)]:
        r=next(r for r in rr if r['stratum']=='ia_greek_latin' and r['dev']['card_id']==card)
        native=Image.open(r['original_page']).copy();lines=current.runtime_lines(native,r['page_id'])
        target=lines[r['runtime_index']];own=cutter._centre_fit(target)
        cache=Path(next(p['cache'] for p in prior.rows(OUT/'dev/provenance.jsonl') if p['page_id']==r['page_id']))
        with np.load(cache/'labels.npz') as archive:old_labels=archive['labels']
        capture={}
        def traced(ink,miss,c0,c_up,c_dn,rise):
            keep=original(ink,miss,c0,c_up,c_dn,rise)
            capture.update(ink=ink,miss=miss,c0=c0,c_up=c_up,c_dn=c_dn,rise=rise,keep=keep)
            return keep
        cutter._voronoi_keep=traced
        result=cutter.mask_foreign_ink(native,target,lines,r['old_box'])
        cutter._voronoi_keep=original
        assert result.record['mask_sha256']==r['mask_sha256']
        x0,y0,x1,y1=r['old_box'];a=max(0,min(x0,own.x0));b=min(native.width,max(x1,own.x1))
        centre=own.base_at(np.arange(a,b,dtype=float));rounded=np.rint(centre).astype(int)
        lab,_=ndi.label(capture['ink'],structure=EIGHT)
        yy,xx=np.nonzero((old_labels[y0:y1,x0:x1]==label)&result.mask)
        sr=yy+y0-rounded[xx+x0-a]+int(capture['c0']);sc=xx+x0-a
        ids=np.unique(lab[sr,sc]);ids=ids[ids!=0];groups=[]
        for ident in ids:
            sy,sx=np.nonzero(lab==ident);cy=float(sy.mean());c0=capture['c0'];half=capture['rise']/2
            up=capture['c_up'][sx];dn=capture['c_dn'][sx]
            def finite(v):return float(v) if np.isfinite(v) else None
            groups.append(dict(straightened_component=int(ident),pixels=len(sy),centroid_y=cy,
                own_centre=c0,own_distance=abs(cy-c0),up_distance=finite(abs(cy-up.mean())),down_distance=finite(abs(cy-dn.mean())),
                own_body_touched=bool(((sy>=c0-half)&(sy<=c0+half)).any()),
                neighbour_body_band_touched=bool(((sy<=up+half)|(sy>=dn-half)).any()),
                kept_pixels=int(capture['keep'][sy,sx].sum()),removed_pixels=int((~capture['keep'][sy,sx]).sum())))
        observed.append(dict(card_id=card,id=r['id'],cached_component_id=label,
            full_output_mask_matches_frozen_record=True,target_lost_pixels=len(yy),components=groups))
    prior.write_json(OUT/'dev/confirmed_loss_mechanisms.json',dict(cases=observed,
        method='captured arguments to original _voronoi_keep; no replacement ownership scoring or output change',
        library_sha256=prior.file_sha256(ROOT/'greekocr/glyphs/foreign_ink.py')))
    print(json.dumps(observed,indent=2))

if __name__=='__main__':main()
