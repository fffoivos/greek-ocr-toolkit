"""Actual offline DocumentConverter pipeline, detector plugin with injected labels.

Runs image layout, OCR, postprocessing, V1 TableFormer, assembly and reading
order. The recognizer is the ONLY substitution: labels isolate geometry.
"""
import os
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
from pathlib import Path
import sys,json,time,argparse
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from docling.document_converter import DocumentConverter,ImageFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions,TableFormerMode
from docling.datamodel.accelerator_options import AcceleratorOptions
from greekocr.deploy.docling_plugin.options import GlossapiOcrOptions
from greekocr.deploy.docling_plugin.model import GlossapiOcrModel

OUT=ROOT/'.astra/out/integration';OUT.mkdir(exist_ok=True)
models=[]
original_init=GlossapiOcrModel.__init__
def init(self,**kw):
 original_init(self,**kw);models.append(self)
GlossapiOcrModel.__init__=init
class Labels:
 def recognize(self,strips):return [(f'LABEL{i:05d}',1.) for i in range(len(strips))]
GlossapiOcrModel._get_recognizer=lambda self:Labels()

options=PdfPipelineOptions(allow_external_plugins=True,
 ocr_options=GlossapiOcrOptions(checkpoint=Path('unused-label-injection'),codec=Path('unused-label-injection'),
  recognition_mode='detector',replace_policy='all',crop_scale=1),
 accelerator_options=AcceleratorOptions(device='cpu',num_threads=4),
 do_ocr=True,do_table_structure=True)
converter=DocumentConverter(format_options={InputFormat.IMAGE:ImageFormatOption(pipeline_options=options)})
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--keys',nargs='*',help='Rerun selected pages, retaining completed results for other pages')
args=parser.parse_args()
summary=json.loads((OUT/'summary.json').read_text()) if args.keys and (OUT/'summary.json').exists() else {}
for f in sorted((ROOT/'docs/tables/annotations').glob('*.json')):
 if args.keys and f.stem not in args.keys:continue
 key=f.stem;start=time.monotonic();print('START',key,flush=True)
 try:
  result=converter.convert(ROOT/'.astra/pages'/f'{key}.png')
  doc=result.document.model_dump(mode='json')
  (OUT/f'{key}.document.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
  records=[r for model in models for r in model.call_log if r['filename']==key+'.png']
  tokens=[c for t in doc['tables'] for c in t['data']['table_cells']]
  summary[key]=dict(status=str(result.status),seconds=time.monotonic()-start,tables=len(doc['tables']),
   table_labels=sum(len(c['text'].split()) for c in tokens),ocr_records=records,
   errors=[str(e) for e in result.errors],
   table_shapes=[dict(rows=t['data']['num_rows'],columns=t['data']['num_cols'],cells=len(t['data']['table_cells'])) for t in doc['tables']])
 except Exception as exc:
  summary[key]=dict(error=repr(exc),seconds=time.monotonic()-start)
 print('END',key,{k:v for k,v in summary[key].items() if k!='ocr_records'},flush=True)
 (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
