"""Unchanged census04 200-row builder + whole pipeline, with native observations injected.

No job scripts, srun, readers or live census. Both split modes use the same
0.3.1 tool binding to isolate routing behavior; new manifest verified separately.
"""
from collections import Counter
from copy import deepcopy
import importlib.util, json, os, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'docs/records/harvest/pipe032'
sys.path.insert(0,str(ROOT))
def offline(event,args):
    if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo'):raise RuntimeError('PIPE032 network OFF')
sys.addaudithook(offline)
from greekocr.harvest import line_pipeline_census as current
from greekocr.harvest.line_pipeline import canonical,digest,identity

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def decisions(root):return [json.loads(s) for s in (root/'decisions.jsonl').read_text().splitlines()]
def normal(d):
    # The declared pipeline version and code/config binding necessarily change.
    return {k:v for k,v in d.items() if k not in ('pipeline_version','run_binding_sha256')}
def counts(ds):return {k:sum(d['disposition']==k for d in ds) for k in ('ADMIT','HOLD','DROP')}
def dump(path,x):path.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def main():
    work=Path(tempfile.mkdtemp(prefix='pipe032-mock-',dir='/private/tmp'))
    oldlp=module('greekocr.harvest.pipe032_old_pipeline',OUT/'baseline/line_pipeline.py')
    old=module('greekocr.harvest.pipe032_old_census',OUT/'baseline/line_pipeline_census.py');old.Pipeline=oldlp.Pipeline
    c4=module('greekocr.harvest.line_pipeline_census04',ROOT/'docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census04.py')
    mock=module('pipe032_original_mock',ROOT/'docs/records/harvest/seg_census/mock_batch.py')
    mock.D=ROOT.parent/'greek-ocr-data/docs/harvest/seg_census'
    mock.PROJECTS=work/'projects'
    fixture=mock.PROJECTS/'greek-ocr-toolkit-sol-recut'
    vp=fixture/'docs/harvest/line_pipeline/tool_versions.json';vp.parent.mkdir(parents=True);vp.write_bytes((OUT/'baseline/tool_versions.json').read_bytes())
    codec=fixture/'greekocr/_vendor/codec/v2.json';codec.parent.mkdir(parents=True);codec.symlink_to(ROOT/'greekocr/_vendor/codec/v2.json')
    build=work/'inputs';build.mkdir();config_path,split=mock.build(build)
    config=json.loads(config_path.read_text())
    seg_version=json.loads(vp.read_text())['tools']['segmentation']['version']
    observations={r['key']:r['result'] for r in map(json.loads,(build/'observations.jsonl').read_text().splitlines())}
    def factory():
        def observe(row):
            answer=deepcopy(observations[canonical([row['parent_id'],row['id']])])
            assert answer['raw_text_sha256']==digest(row['raw_text'])
            assert answer['binding']['crop_sha256']==row['crop_sha256']
            answer.update(binding=identity(row),tool_version=seg_version)
            return answer
        return observe
    summary={}
    for mode in ('mode-i','mode-ii'):
        cfg=deepcopy(config)
        if mode=='mode-ii':cfg['split_input']=dict(path=str(split),sha256=current.file_sha(split))
        ds={}
        for tag,implementation,scope in [('before',old,[]),('empty',current,[]),('polytonic-out',current,['polytonic'])]:
            c4.census=implementation
            target=work/(mode+'-'+tag)
            c4.run(dict(cfg,routes_out_of_scope=scope),target,execute=True,segmenter_factory=factory)
            ds[tag]=decisions(target)
            assert len(ds[tag])==200 and not any(d['disposition']=='INFRA_ERROR' for d in ds[tag])
            (OUT/(mode+'-'+tag+'.jsonl')).write_text(''.join(canonical(d)+'\n' for d in ds[tag]))
        differences=[dict(binding=b['binding'],before=normal(b),after=normal(a)) for b,a in zip(ds['before'],ds['empty']) if normal(b)!=normal(a)]
        moves=[]
        for b,a in zip(ds['before'],ds['polytonic-out']):
            if b['disposition']!=a['disposition']:
                assert b['disposition']=='HOLD' and a['disposition'] in ('ADMIT','DROP')
                assert b['reasons'] and all(r['reason']=='correction_unresolved' and r['tool']=='polytonic' for r in b['reasons'])
                moves.append(dict(binding=b['binding'],before=b['disposition'],after=a['disposition'],before_reasons=b['reasons']))
        summary[mode]=dict(rows=200,empty_config_differences=differences,before=counts(ds['before']),after=counts(ds['polytonic-out']),movers=moves,
            scope_counts=json.loads((work/(mode+'-polytonic-out')/'summary.json').read_text())['corrections_not_applied'])
        assert not differences
    dump(OUT/'mock_receipt.json',dict(summary=summary,work=str(work),builder=dict(path=str(ROOT/'docs/records/harvest/seg_census/mock_batch.py'),sha256=current.file_sha(ROOT/'docs/records/harvest/seg_census/mock_batch.py')),
        slice=dict(path=str(mock.D/'mock_slice_inputs.jsonl.gz'),sha256=current.file_sha(mock.D/'mock_slice_inputs.jsonl.gz')),
        comparison='every complete decision after excluding only pipeline_version and run_binding_sha256; shared original 0.3.1 manifest; saved native observations relabeled to bound version; synthetic qualified no-change correction fixtures unchanged',network=False,readers=0,slurm=0,census=0))
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
