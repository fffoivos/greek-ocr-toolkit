import json,sys,traceback
from pathlib import Path
import numpy as np
projects=Path(sys.argv[1]);root=Path(sys.argv[2]);sys.path.insert(0,str(projects/'greek-ocr-toolkit-sol-recut'))
from greekocr.harvest import geometry_observations as geo
from greekocr.harvest.line_pipeline_native import NativeSegmenter
from greekocr.harvest.line_pipeline_runtime import validate
manifest=root/'attempts/qual_05/qualify/native-runtime.json';validate(manifest)
original=geo.vendor_ownership

def ownership(*args,**kwargs):
    module=original(*args,**kwargs);prepare=module.prepare_row
    def inspect(record,*args,**kwargs):
        try:return prepare(record,*args,**kwargs)
        except Exception:
            curves={k:np.asarray(record[k],dtype=float) for k in module.CURVES}
            delta=curves['bottom']-curves['top']
            print(json.dumps(dict(probe='invalid row witness',row_id=record['row_id'],x0=record['x0'],x1=record['x1'],xheight=record['xheight'],shapes={k:list(v.shape) for k,v in curves.items()},finite=all(np.isfinite(v).all() for v in curves.values()),minimum_bottom_minus_top=float(delta.min()),nonpositive_columns=int((delta<=0).sum()))),flush=True)
            raise
    module.prepare_row=inspect;return module
geo.vendor_ownership=ownership
row=next(json.loads(s) for s in (root/'attempts/qual_05/qualify/sample.jsonl').open() if json.loads(s)['id']=='lekythos--3bfc4a385d61b883--s004-l0129')
native=NativeSegmenter(json.loads((projects/'greek-ocr-toolkit-sol-recut/docs/harvest/line_pipeline/tool_versions.json').read_text())['tools'],root/'runtime/rust-target/release/greekocr-frozen-font-predict')
try:print(json.dumps(native(row)))
except Exception:traceback.print_exc()
finally:native.close()
