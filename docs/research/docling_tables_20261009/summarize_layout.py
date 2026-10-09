"""Validate layout evidence and pin source/model/input hashes, without inference."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'experiments'
SP=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/lib/python3.11/site-packages')
summary=json.loads((OUT/'layout-summary.json').read_text())
assert len(summary['cases'])==27
pages={case['metrics']['page'] for case in summary['cases']}
assert len(pages)==3
for page in sorted(pages):
    cases=[c for c in summary['cases'] if c['metrics']['page']==page]
    assert len(cases)==9
    assert all(c['metrics']['raw_identical_to_line'] and c['metrics']['tables_identical_to_line'] for c in cases)
    assert len({c['metrics']['raw_sha256'] for c in cases})==1
    for case in cases:
        m=case['metrics']
        saved=json.loads((OUT/f"{page}.layout.{m['variant']}.json").read_text())
        assert saved['raw_tables']==case['raw_tables']
        assert saved['final_tables']==case['final_tables']
        assert m['input_cells']==m['unique_table_tokens']+m['excluded_from_tables']
        assert m['table_text_cells']==m['unique_table_tokens']  # no duplicate admission on these pages
        if m['variant'] in ('no_cells','border_crossing_only','fused_table_and_outside_only'):
            assert m['table_text_cells']==0
    print(page,'9 variants: raw predictions and retained table identities identical')

names=[
 'docling/models/stages/layout/layout_object_detection_model.py',
 'docling/models/stages/layout/layout_postprocessing_model.py',
 'docling/utils/layout_postprocessor.py',
 'docling/models/inference_engines/object_detection/transformers_engine.py',
 'docling/models/inference_engines/object_detection/base.py',
 'docling/models/inference_engines/common/hf_vision_base.py',
 'docling/models/inference_engines/vlm/_utils.py',
 'docling/datamodel/pipeline_options.py','docling/datamodel/stage_model_specs.py',
 'docling/pipeline/standard_pdf_pipeline.py']
files=[SP/name for name in names]
snapshot=Path(summary['model_snapshot'])
files += [snapshot/name for name in ('config.json','preprocessor_config.json','model.safetensors')]
files += [ROOT/'research_layout.py',ROOT/'research_tables.py',Path(__file__)]
files += [ROOT/'pages'/f'{page}.png' for page in sorted(pages)]
files += [ROOT/'round3'/f'{page}.lines.json' for page in sorted(pages)]
manifest=[dict(path=str(p),size=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]
(OUT/'layout-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
assert summary['source_hashes'][str(ROOT/'research_layout.py')]==hashlib.sha256((ROOT/'research_layout.py').read_bytes()).hexdigest()
times=[c['metrics']['neural_seconds'] for c in summary['cases']]
print('Neural seconds range:',min(times),max(times))
print('Layout manifest:',len(manifest),'source, script, model, and input files')
