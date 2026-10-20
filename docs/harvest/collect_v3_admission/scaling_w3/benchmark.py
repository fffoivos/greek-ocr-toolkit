"""Bounded local synthetic throughput; no production data access."""
import json
import tempfile
import time
from pathlib import Path
import scale as s

def sample(i):
    text='δοκιμή συνθετικού κειμένου '*3
    d=dict(binding=dict(parent_id=s.VC,id=str(i),split='train',crop_sha256='0'*64),admitted=True,disposition='ADMIT',final_text=text,expectations=dict(orthography='monotonic',scripts=['greek']),final_inventory=dict(greek_letters=66,latin_letters=0,cyrillic_letters=0,letter_count=66),stages=[dict(stage='segmentation',result=dict(frame=dict(normalization_cw=0,source_height=40,source_width=800),evidence=dict(xheight_px=20,baseline_angle_deg=0,curve_deviation_px=0)))])
    return dict(parent_id=s.VC,id=str(i),split='train',admitted=True,decision=d,final_text=text,crop_sha256='0'*64,crop_path='/tmp/synthetic-crop',edition_id='doc',doc='doc',source='source',crop_bbox=None,confidence=.9,synthetic_padding='x'*20000)

def main():
    m=s.classifier();n=1000;r=sample(0);r.pop('synthetic_padding')
    r['decision']['stages'][0]['result']['evidence']['detected_rows']=[dict(side='main',curves={name:[[x,round(10+offset+x*.001,3)] for x in range(250)] for name,offset in [('base',20),('mean',0),('ascender',-10),('descender',30)]})]
    line=json.dumps(r,ensure_ascii=False);encoded=line.encode();start=time.perf_counter()
    for i in range(n):
        r=json.loads(line);slim=s.census_row(r,m);m.tag(slim,relative_flag=False)
    seconds=time.perf_counter()-start
    with tempfile.TemporaryDirectory() as t:
        p=Path(t)/'synthetic';p.write_bytes(encoded*n);t0=time.perf_counter();s.sha(p);hash_seconds=time.perf_counter()-t0
    result=dict(rows=n,bytes_per_row=len(encoded),seconds=seconds,MB_per_second=n*len(encoded)/seconds/1e6,hash_MB_per_second=n*len(encoded)/hash_seconds/1e6,production_input_bytes=7870677512)
    s.dump(s.HERE/'SYNTHETIC_THROUGHPUT.json',result);print(json.dumps(result))
if __name__=='__main__':main()
