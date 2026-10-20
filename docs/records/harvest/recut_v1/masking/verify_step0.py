"""Public masker identity on native process_page results, including ring fill."""
from pathlib import Path
import json,sys,time,warnings
import numpy as np
from PIL import Image
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
sys.path.insert(0,str(OUT));sys.path.insert(0,str(ROOT))
import run as current
from greekocr.glyphs.foreign_ink import prepare_mask_page,mask_foreign_ink,mask_detected_line
from greekocr.pages import process_page
from greekocr.pages.tables import line_piece
from greekocr.pages.lines import extract_line_image,CURVES
from probe import match,runtime_fit
prior=current.prior
warnings.filterwarnings('ignore',category=np.exceptions.RankWarning)


def main():
    rr,_=prior.bind();base=prior.read_json(OUT/'step0/agreement.json');out=[]
    for page in base['pages']:
        group=[r for r in rr if r['page_id']==page['page_id']]
        native=Image.open(group[0]['crop_page_path']).copy();runtime=process_page(native)
        lines=[l for l in runtime.segmentation.lines if l.discounted is None]
        exact=[]
        for l in lines:
            r=l.to_record();r.update({key:getattr(l,key).tolist() for key in CURVES});exact.append(r)
        # A JSON roundtrip models the exact full-precision training adapter.
        exact=json.loads(json.dumps(exact));fits=[runtime_fit(l) for l in lines];prepared=prepare_mask_page(native)
        count=piece_count=0;pixels=0;unrolled_identical=0
        for r in group:
            i=match(r['crop_bbox'],fits)
            if i is None:continue
            training=mask_foreign_ink(prepared,exact[i],exact,r['crop_bbox'])
            inference=mask_detected_line(prepared,lines[i],lines,r['crop_bbox'])
            assert np.array_equal(training.mask,inference.mask)
            assert np.array_equal(np.asarray(training.image),np.asarray(inference.image))
            assert training.record==inference.record
            count+=1;pixels+=training.record['masked_pixel_count']
            # Execute the precise proposed deployment hook before its unchanged
            # extraction, for the detector's own original rectangle as well.
            box=line_piece(lines[i],i,native.size).box
            a=mask_foreign_ink(prepared,exact[i],exact,box)
            b=mask_detected_line(prepared,lines[i],lines)
            assert np.array_equal(a.mask,b.mask) and a.record==b.record
            aa=native.copy();bb=native.copy();aa.paste(a.image,box[:2]);bb.paste(b.image,box[:2])
            assert np.array_equal(np.asarray(extract_line_image(aa,lines[i])),np.asarray(extract_line_image(bb,lines[i])))
            piece_count+=1;unrolled_identical+=1
        out.append(dict(source=page['source'],page_id=page['page_id'],training_rectangles_equal=count,
                        runtime_rectangles_equal=piece_count,actual_extraction_equal=unrolled_identical,
                        training_masked_pixels=pixels))
        print(out[-1],flush=True)
    prior.write_json(OUT/'step0/public_function_identity.json',dict(inference_applicable=True,pages=out,
        library_sha256=prior.file_sha256(ROOT/'greekocr/glyphs/foreign_ink.py'),
        source_hashes=current.source_hashes(),training_and_runtime_crops_and_records_identical=True,
        deployment_consumer_unmodified=True,network='OFF'))

if __name__=='__main__':main()
