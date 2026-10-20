"""Summarize saved evidence, without running networks or reading PDF text."""
import os
os.environ['HF_HUB_OFFLINE']='1'
import csv
import hashlib
import json
from pathlib import Path
from collections import defaultdict
from research_tables import ROOT, OUT, save, serial
from docling_ibm_models.tableformer.data_management.tf_cell_matcher import CellMatcher

records=[]
comparisons=[]
for mode in ['accurate','fast']:
    summary=json.loads((OUT/f'summary-{mode}.json').read_text())
    for record in summary['metrics']:
        p=OUT/f"{record['page']}.{mode}.{record['variant']}.matching-{int(record['matching'])}.json"
        j=json.loads(p.read_text())
        if record['matching']:
            d=j['raw_tableformer']['predict_details']
            raw=CellMatcher({'predict':{'pdf_cell_iou_thres':.05}}).match_cells(
                {'tokens':d['pdf_cells'],'height':d['page_height'],'width':d['page_width']},
                d['table_bbox'],d['prediction'])
            record['initial_multi_matches']=sum(len(m)>1 for m in raw['matches'].values())
            record['initial_unmatched']=len(d['pdf_cells'])-len(raw['matches'])
            record['final_multi_matches']=sum(len(m)>1 for m in d['matches'].values())
        records.append(record)
        if record['variant'] in ['wide','word']:
            parents=defaultdict(list)
            for cell in j['cells']:
                if cell['token'] in j['landing']:
                    parents[cell['line']].append((cell['token'],j['landing'][cell['token']]))
            split_parents={li:ls for li,ls in parents.items() if len(ls)>1}
            multi_landed={li:ls for li,ls in split_parents.items()
                         if len({x['table_cell'] for _,landing in ls for x in landing})>1}
            comparisons.append(dict(page=record['page'],mode=mode,variant=record['variant'],
                 split_parents_in_table=len(split_parents),parents_reaching_multiple_table_cells=len(multi_landed),
                 examples=list(multi_landed.items())[:5]))
save('combined-summary.json',dict(metrics=records,split_parent_comparisons=comparisons))
keys=list(dict.fromkeys(k for r in records for k in r))
with (OUT/'summary.csv').open('w') as f:
    writer=csv.DictWriter(f,fieldnames=keys)
    writer.writeheader(); writer.writerows(records)
print('experiment table')
for r in records:
    print('|', ' | '.join(str(r[k]) for k in ['mode','page','variant','table_cells','rows','cols','table_input_cells','assigned','split','duplicated','lost']), '|')
print('parent comparisons')
for c in comparisons:
    print({k:v for k,v in c.items() if k!='examples'})

# Pin the actual installed source (could be locally modified), weights, and
# pixel/detector inputs. Never read pages/*.boxes.json.
sp=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/lib/python3.11/site-packages')
source_names=[
 'docling/pipeline/standard_pdf_pipeline.py','docling/datamodel/pipeline_options.py',
 'docling/datamodel/base_models.py','docling/models/base_ocr_model.py',
 'docling/models/stages/layout/layout_object_detection_model.py',
 'docling/models/stages/layout/layout_postprocessing_model.py','docling/utils/layout_postprocessor.py',
 'docling/models/stages/table_structure/table_structure_model.py',
 'docling/models/stages/table_structure/table_structure_model_v2.py',
 'docling/models/stages/table_structure/table_structure_model_granite_vision.py',
 'docling/models/stages/page_preprocessing/page_preprocessing_model.py',
 'docling/models/stages/page_assemble/page_assemble_model.py',
 'docling/models/stages/reading_order/readingorder_model.py',
 'docling/models/stages/ocr/easyocr_model.py','docling/models/stages/ocr/tesseract_ocr_model.py',
 'docling/models/stages/ocr/tesseract_ocr_cli_model.py',
 'docling/backend/docling_parse_backend.py','docling/backend/image_backend.py','docling/backend/pypdfium2_backend.py',
 'docling_core/types/doc/page.py','docling_core/types/doc/base.py',
 'docling_core/types/doc/items/table/table_data.py',
 'docling_ibm_models/tableformer/data_management/tf_predictor.py',
 'docling_ibm_models/tableformer/data_management/tf_cell_matcher.py',
 'docling_ibm_models/tableformer/data_management/matching_post_processor.py']
files=[sp/p for p in source_names]
files+=list((ROOT/'pages').glob('*.png'))+list((ROOT/'round3').glob('*.json'))
from research_tables import MODEL_ROOT
files+=list(MODEL_ROOT.glob('*/*.json'))+list(MODEL_ROOT.glob('*/*.safetensors'))
files+=[Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/deploy/docling_plugin')/p for p in ['model.py','options.py']]
files+=[Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/tests/test_docling_contract.py'),
 Path('/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/DOCLING_PLUGIN_CONTRACT.md')]
save('manifest.json',[dict(path=str(p),size=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files])
