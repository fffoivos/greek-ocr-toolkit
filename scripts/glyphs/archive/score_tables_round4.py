"""Score saved full-pipeline label destinations against provisional pixel cells.

These are failure-finding measurements. Independent panels are not treated as
one rectangular grid, and an unqualified panel is never marked accepted.
"""
from collections import Counter
from pathlib import Path
import json
import math
import sys
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'.astra/out'

def read(p):return json.loads(p.read_text())
def area(b):return max(0,b[2]-b[0])*max(0,b[3]-b[1])
def overlap(a,b):return max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))


def main():
    sys.path.insert(0,str(ROOT))
    from scripts.glyphs.archive.evaluate_tables_round4 import geometry
    integration=read(OUT/'integration/summary.json');acceptance=read(OUT/'acceptance/summary.json')
    summary={}
    for f in sorted((ROOT/'docs/records/tables/annotations').glob('*.json')):
        ann=read(f);key=f.stem
        doc=read(OUT/f'integration/{key}.document.json');run=integration[key]
        records=run['ocr_records'];assert len(records)==1 and records[0]['status']=='replaced'
        width,height=ann['source']['image_size'];size=doc['pages']['1']['size']
        sx,sy=width/size['width'],height/size['height']
        mapping={};ambiguous=[];unmatched=[];table_labels=[]
        for p in records[0]['lines']:
            r=p['rect'];assert r['coord_origin']=='TOPLEFT'
            xs=[r[f'r_x{i}']*sx for i in range(4)];ys=[r[f'r_y{i}']*sy for i in range(4)]
            box=[min(xs),min(ys),max(xs),max(ys)]
            containing=[t for t in ann['tables'] if overlap(box,t['extent'])/area(box)>.8]
            if not containing:continue
            table_labels.append(p['text'])
            owners=[(t,c) for t in containing for c in t['cells'] if any(
                overlap(box,e['box'])/max(1,min(area(box),area(e['box'])))>.2 for e in c['text_elements'])]
            distinct={c['id'] for _,c in owners}
            if len(distinct)>1:ambiguous.append(p['text'])
            elif len(distinct)==1:mapping[p['text']]=owners[0]
            else:unmatched.append(p['text'])
        locations={};mixed=[]
        for ti,t in enumerate(doc['tables']):
            for ci,c in enumerate(t['data']['table_cells']):
                labels=c['text'].split()
                owners={mapping[s][1]['id'] for s in labels if s in mapping}
                if len(owners)>1:mixed.append(dict(table=ti,cell=ci,annotation_cells=sorted(owners)))
                for label in labels:locations.setdefault(label,[]).append((ti,ci,c))
        lost=[s for s in table_labels if not locations.get(s)]
        duplicate=[s for s in table_labels if len(locations.get(s,[]))>1]
        wrong=[];comparable=0
        mixed_slots={(m['table'],m['cell']) for m in mixed}
        for label,(table,cell) in mapping.items():
            loc=locations.get(label,[])
            if len(loc)!=1:continue
            ti,ci,c=loc[0]
            bad=(ti,ci) in mixed_slots
            if list(table['panels'])==['main']:
                comparable+=1
                bad |= ((c['start_row_offset_idx'],c['start_col_offset_idx'],c['row_span'],c['col_span'])!=
                        (cell['row'],cell['column'],cell['row_span'],cell['column_span']))
            if bad:wrong.append(label)
        # Offline emitted pieces have their own layout admission record. Do not
        # conflate those raster-scale results with native-scale integration.
        pieces=read(OUT/f'{key}.cells.json')['cells']
        wanted={f'P{p["index"]:05d}' for p in pieces if p['table_id'] is not None}
        admitted=Counter(s for t in acceptance[key]['retained_tables'] for s in t['tokens'])
        previous=read(ROOT/f'.astra/previous_round3/{key}.lines.json')
        oldpieces=[dict(index=i,box_pixels=[max(0,l['x0']),max(0,math.floor(min(l['top']))),
                         min(width,l['x1']),min(height,math.ceil(max(l['bottom'])))],
                         box_page=[max(0,l['x0'])/3,max(0,min(l['top']))/3,
                                   min(width,l['x1'])/3,min(height,max(l['bottom']))/3],coord_origin='TOPLEFT')
                   for i,l in enumerate(previous) if l['discounted'] is None]
        oldgeometry=geometry(ann,oldpieces,Image.open(ROOT/f'.astra/pages/{key}.png'))
        summary[key]=dict(integration=dict(
            input_pieces_in_annotated_extents=len(table_labels),uniquely_mapped=len(mapping),
            ambiguous_input_pieces=ambiguous,unmatched_input_pieces=unmatched,
            missing_from_final_tables=lost,duplicated_in_final_tables=duplicate,
            wrong_owner_labels=wrong,mixed_owner_cells=mixed,
            exact_grid_comparable_labels=comparable,all_panels_qualified=False,
            accepted=False),
            standalone_admission=dict(detector_table_pieces=len(wanted),
              admitted_exactly_once=sum(admitted[s]==1 for s in wanted),
              excluded_labels=sorted(s for s in wanted if not admitted[s])),
            previous_geometry=oldgeometry)
    (OUT/'acceptance/delivery-audit.json').write_text(json.dumps(summary,indent=2)+'\n')
    controls=[]
    for p in sorted((OUT/'acceptance').glob('*.fused_negative.json')):
        result=read(p);meta=result['annotation_metadata']
        pair=next((a,b) for i,a in enumerate(meta) for b in meta[i+1:] if a['row']==b['row']
                  and a['cell_id']!=b['cell_id'] and abs(a['column']-b['column'])==1)
        landing=[result['landing'].get(m['label'],[]) for m in pair]
        together=all(len(x)==1 for x in landing) and landing[0][0]['cell']==landing[1][0]['cell']
        controls.append(dict(file=p.name,labels=[m['label'] for m in pair],
                             same_output_cell=together,landing=landing))
        # Different annotated owners reaching ONE output cell must fail the
        # ownership gate even though both constituent strings survive intact.
        assert together,(p,landing)
    assert len(controls)==22
    (OUT/'acceptance/fused-controls-audit.json').write_text(json.dumps(controls,indent=2)+'\n')
    print(json.dumps({k:{'input':v['integration']['input_pieces_in_annotated_extents'],
        'lost':len(v['integration']['missing_from_final_tables']),
        'wrong':len(v['integration']['wrong_owner_labels'])} for k,v in summary.items()},indent=2))


if __name__=='__main__':main()
