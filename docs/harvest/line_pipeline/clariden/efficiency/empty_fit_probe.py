import sys,json,traceback
from pathlib import Path
projects=Path(sys.argv[1]);root=Path(sys.argv[2]);sys.path.insert(0,str(projects/'greek-ocr-toolkit-sol-recut'))
from greekocr.harvest.line_pipeline_native import NativeSegmenter
from greekocr.harvest.line_pipeline_runtime import validate
q=root/'attempts/scale_01/qualify';validate(q/'native-runtime.json')
row=next(json.loads(s) for s in (q/'sample.jsonl').open() if json.loads(s)['id']=='lekythos--dcfa99599048d352--s002-l0114')
native=NativeSegmenter(json.loads((projects/'greek-ocr-toolkit-sol-recut/docs/harvest/line_pipeline/tool_versions.json').read_text())['tools'],root/'runtime/rust-target/release/greekocr-frozen-font-predict')
try:print(json.dumps(native(row)))
except Exception:traceback.print_exc()
finally:native.close()
