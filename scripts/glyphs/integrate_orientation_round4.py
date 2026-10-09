"""Run the actual offline oriented Docling pipeline and record its stage frames."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from docling.document_converter import DocumentConverter,ImageFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.accelerator_options import AcceleratorOptions
from greekocr.deploy.docling_plugin.options import GlossapiOcrOptions
from greekocr.deploy.docling_plugin.orientation import OrientationPdfPipeline


class Trace:
    def __init__(self,stage,model,events):self.stage,self.model,self.events=stage,model,events
    def __getattr__(self,name):return getattr(self.model,name)
    def __call__(self,conv,pages):
        pages=list(pages)
        self.events.append(dict(stage=self.stage,phase='enter',sizes=[[p.size.width,p.size.height] for p in pages]))
        for p in self.model(conv,pages):
            image=p.get_image(scale=1)
            self.events.append(dict(stage=self.stage,phase='exit',page=p.page_no,size=[p.size.width,p.size.height],
                image_size=list(image.size),image_sha256=hashlib.sha256(image.tobytes()).hexdigest()))
            yield p


class AuditPipeline(OrientationPdfPipeline):
    instances=[]
    def __init__(self,pipeline_options):
        super().__init__(pipeline_options);self.events=[]
        for attr,stage in [('preprocessing_model','normalize'),('layout_model','layout'),('ocr_model','ocr'),('table_model','table')]:
            setattr(self,attr,Trace(stage,getattr(self,attr),self.events))
        self.instances.append(self)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--checkpoint',type=Path,required=True)
    ap.add_argument('--input',type=Path,default=ROOT/'.astra/pages/s2-6419488b7f8e69fd20da-p00001.png')
    ap.add_argument('--out',type=Path,default=ROOT/'.astra/out/orientation-acceptance');a=ap.parse_args();a.out.mkdir(exist_ok=True,parents=True)
    opts=PdfPipelineOptions(allow_external_plugins=True,
        ocr_options=GlossapiOcrOptions(checkpoint=a.checkpoint,codec=ROOT/'greekocr/deploy/docling_plugin/recognizer/v1.json',
            recognition_mode='oriented',replace_policy='all',crop_scale=1),
        accelerator_options=AcceleratorOptions(device='cpu',num_threads=4),do_ocr=True,do_table_structure=True,
        generate_parsed_pages=True,generate_page_images=True)
    converter=DocumentConverter(format_options={InputFormat.IMAGE:ImageFormatOption(pipeline_cls=AuditPipeline,pipeline_options=opts)})
    start=time.monotonic();result=converter.convert(a.input);pipeline=AuditPipeline.instances[-1]
    doc=result.document.model_dump(mode='json')
    (a.out/f'{a.input.stem}.document.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
    records=dict(status=str(result.status),errors=[str(e) for e in result.errors],seconds=time.monotonic()-start,
                 events=pipeline.events,normalization=pipeline.preprocessing_model.records,
                 table_adaptation=pipeline.table_model.records,ocr=pipeline.ocr_model.call_log)
    (a.out/f'{a.input.stem}.pipeline.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    order=[x['stage'] for x in pipeline.events if x['phase']=='enter']
    summary=dict(passed=order==['normalize','layout','ocr','table'] and not result.errors and str(result.status)=='ConversionStatus.SUCCESS',
                 order=order,status=str(result.status),errors=records['errors'],seconds=records['seconds'],
                 normalization=[{k:r[k] for k in ('page_no','applied','mixed','orientation_cw')} for r in records['normalization']],
                 tables=[dict(rows=t['data']['num_rows'],columns=t['data']['num_cols'],orientation=t['data']['orientation']) for t in doc['tables']],
                 evidence=f'{a.input.stem}.pipeline.json')
    (a.out/'pipeline.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
