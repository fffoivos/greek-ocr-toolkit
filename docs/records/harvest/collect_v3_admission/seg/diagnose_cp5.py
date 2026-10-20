"""Bound native diagnostic context for H1/H2; no detector/preparation/writes."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from PIL import Image
import numpy as np
from greekocr.harvest import geometry_observations as g
from greekocr.glyphs.orientation import discover_directions,measure_orientation
from greekocr.glyphs.orientation_regions import axis_regions
RUN=Path.home()/'Projects/collect-v3-data/run'
SEG=Path(__file__).resolve().parent


def main():
    import os
    def audit(event,args):
        if event.startswith('socket.') or event=='subprocess.Popen':raise AssertionError('network/process forbidden')
        if event=='open':
            _,mode,flags=args
            if (mode and any(c in mode for c in 'wax+')) or flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):raise AssertionError('write forbidden')
        if event in ('os.mkdir','os.rename','os.remove','os.rmdir','os.link','os.symlink','os.chmod','os.truncate'):raise AssertionError('mutation forbidden')
    sys.addaudithook(audit)
    prefixes=('0d0b2233','8213d286','83c3182a','b9f59878','ebdc4d07')
    suffixes=('l0019','l0144','l0259','l0034','l0265')
    records=[]
    for raw in (RUN/'W1/features.jsonl').open():
        r=json.loads(raw)
        if any(p in r['id'] and r['id'].endswith(s) for p,s in zip(prefixes,suffixes)):records.append(r)
    out=[]
    for r in records:
        assert g.sha(r['crop_source_image'])==r['crop_source_sha256']
        with Image.open(r['crop_source_image']) as opened:page_image=opened.convert('L')
        box=r['crop_bbox'];crop=page_image.crop(box)
        proposals=discover_directions(page_image);regions=axis_regions(proposals)
        overlaps=[b for b in regions if b['box'][0]<box[2] and box[0]<b['box'][2] and b['box'][1]<box[3] and box[1]<b['box'][3]]
        pid=r['id'].rsplit('-l',1)[0]
        caches=[SEG/'CP4_geometry'/pid,RUN/'cache/g1b'/pid,SEG/'CP3_geometry'/pid]
        rows=[];binding=None;reason=None
        try:
            cache=next(p for p in caches if (p/'receipt.json').exists())
            page=g.load_cached_page(r['crop_source_image'],cache,r['crop_source_sha256']);binding=page['binding']
            for row in page['rows']:
                hits=page['ownership'].box_hits(row,box)
                if hits.any():
                    rows.append(dict(row_id=row['row_id'],x0=row['x0'],x1=row['x1'],xheight=row['xheight'],
                        meanline_range=[float(np.min(row['meanline'])),float(np.max(row['meanline']))],
                        baseline_range=[float(np.min(row['baseline'])),float(np.max(row['baseline']))],
                        assigned_pixels=int(hits.sum()),target=row['row_id']==r.get('measured_row_id')))
        except (StopIteration,OSError,ValueError) as error:reason=str(error) or 'no_existing_cache'
        out.append(dict(row_id=r['id'],source=r['crop_source_image'],source_sha256=r['crop_source_sha256'],
            crop_bbox=box,crop_sha256=r['crop_sha256'],geometry_binding=binding,geometry_reason=reason,rows=rows,
            crop_measurements={u:measure_orientation(crop,use_osd=False,unit=u).to_record() for u in ('block','line')},
            crop_regions=axis_regions(discover_directions(crop)),page_regions_overlapping_crop=overlaps,
            page_region_measurements=[dict(region=b,measurement=measure_orientation(page_image.crop(b['box']),use_osd=False,unit='block').to_record()) for b in overlaps]))
    print(json.dumps(dict(schema='SEG-CP5b-native-diagnostics-1',cases=out),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
