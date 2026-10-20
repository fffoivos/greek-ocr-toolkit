"""Replay all 888 local calibration crops; reuse frozen source-context observations.

Fresh crop orientation, detector/refocus, baseline, labels, box and padding run
through NativeSegmenter. Reconciliation consumes the same saved raw page context
used by verify_filter_parity.py; source pages are not reprocessed in this check.
"""
from collections import Counter
import gzip
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
import time

D=Path(__file__).resolve().parent
ROOT=D.parents[4]
sys.path.insert(0,str(ROOT))
from replay_segeval1 import offline, fail_timeout
sys.addaudithook(offline)
from greekocr.harvest.line_pipeline_native import NativeSegmenter, character_count


def main():
    site=ROOT.parent/'ocr-review-sites-20261018'
    report_path=site/'review-data/box-length-experiment.json'
    native_path=site/'review-data/font-normalized/predicted-rows.json.gz'
    context_path=site/'qa/word-tolerance/context-evidence.json'
    report=json.loads(report_path.read_text())['rows']
    natives={r['id']:r for r in json.loads(gzip.decompress(native_path.read_bytes()))}
    contexts={r['id']:r for r in json.loads(context_path.read_text())['rows']}
    population_path=site/'review-data/population.json'
    population=json.loads(population_path.read_text())
    detail_cache={}; detail_sources={}
    for old in report:
        meta=natives[old['id']]
        if meta.get('google_text') is None or 'content_class' not in meta:
            chunk=old['index']//population['detail_chunk_size']
            path=site/f'population-data/details/{chunk:05d}.json.gz'
            if chunk not in detail_cache:
                detail_cache[chunk]=json.loads(gzip.decompress(path.read_bytes()))
                detail_sources[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
            detail=detail_cache[chunk][old['index']%population['detail_chunk_size']]
            assert detail[0]==old['id'] and detail[4]==old['image_sha256']
            codes=dict(part.split(':') for part in detail[8].split('|'))
            meta['google_text']=detail[2]
            meta['content_class']=population['codebooks']['classes'][int(codes['class'])]
        assert character_count(meta['google_text'])==old['characters']
    paths={r['id']:site/'population-images'/(r['image_sha256']+'.png') for r in report}
    assert len(report)==888 and all(p.is_file() for p in paths.values())
    replay_path=D/'replay_calibration.jsonl'
    completed={r['line_id']:r for r in map(json.loads,replay_path.read_text().splitlines())} if replay_path.exists() else {}
    versions=json.loads((ROOT/'docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
    worker=NativeSegmenter(versions,ROOT/'scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict')
    worker.context=lambda row,*args:contexts.get(row['id'],dict(status='unavailable',reason='no saved calibration source context'))
    signal.signal(signal.SIGALRM,fail_timeout)
    flips=[];failures=[];zero=[];box_drift=[];counts=Counter();started=time.monotonic()
    try:
        with (D/'replay_calibration.jsonl').open('w') as output:
            for i,old in enumerate(report,1):
                rid=old['id'];meta=natives[rid]
                assert character_count(meta['google_text'])==old['characters']
                assert hashlib.sha256(paths[rid].read_bytes()).hexdigest()==old['image_sha256']
                row=dict(id=rid,parent_id='accepted-calibration-888',split='unassigned',
                    crop_path=str(paths[rid]),crop_sha256=old['image_sha256'],raw_text=meta['google_text'],
                    script_class=old['script'],primary_class=meta['content_class'])
                try:
                    signal.alarm(120)
                    after=completed[rid]['after'] if rid in completed else worker(row)
                    assert after['binding']['crop_sha256']==row['crop_sha256']
                    assert after['policy_sha256']==worker.policy_sha and after['tool_version']=='0.6'
                except Exception as exc:
                    failures.append(dict(line_id=rid,type=type(exc).__name__,error=str(exc)))
                    print(json.dumps(failures[-1]),flush=True);continue
                finally:signal.alarm(0)
                a=after['evidence'];rf=a['box_evidence'].get('row_frame')
                b=old['box_evidence'];ab=a['box_evidence']
                before_verdict=old['judgements']['current']['verdict']
                comp=dict(bbox=ab.get('bbox')==b.get('bbox'),
                    expected=ab.get('predictions',[None]*3)[2]==b['predictions'][2],
                    total_padding_line_heights=a['padding_evidence'].get('total_padding_line_heights')==old['padding_evidence'].get('total_padding_line_heights'))
                if not comp['bbox']:box_drift.append(dict(line_id=rid,before=b.get('bbox'),after=ab.get('bbox')))
                if rf and rf['angle_deg']==0:zero.append(dict(line_id=rid,**comp))
                record=dict(line_id=rid,index=old['index'],before=old,after=after,
                    verdict_before=before_verdict,verdict_after=after['verdict'],
                    reason_before=old['judgements']['current']['reason'],reason_after=after['reason'],
                    owner_rating=old['owner_rating'],theta_deg=rf['angle_deg'] if rf else None,
                    ratio_before=(old['characters']+1)/(b['predictions'][2]+1),
                    ratio_after=(old['characters']+1)/(ab['predictions'][2]+1) if ab.get('available') else None,
                    parity=comp,context_source='frozen saved raw source-context observations')
                output.write(json.dumps(record,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n');output.flush()
                counts[f'{before_verdict}->{after["verdict"]}']+=1
                if after['verdict']!=before_verdict:
                    flips.append({k:record[k] for k in ['line_id','index','verdict_before','verdict_after','reason_before','reason_after','owner_rating','theta_deg','ratio_before','ratio_after']} | dict(
                        upright_height=b['bbox'][3]-b['bbox'][1],row_frame_height=rf['height'] if rf else None,
                        bbox_parity=comp['bbox']))
                if i%25==0:print(f'{i}/888 measured; flips={len(flips)}',flush=True)
    finally:worker.close()
    receipt=dict(rows=sum(counts.values()),elapsed_seconds=time.monotonic()-started,
        reused_completed_rows=len(completed),new_native_crops=888-len(completed),flips=flips,
        flip_count=len(flips),verdict_transitions=dict(counts),theta0_rows=len(zero),
        theta0_comparisons=zero,theta0_exact=sum(all(r[k] for k in ['bbox','expected','total_padding_line_heights']) for r in zero),
        theta0_mismatches=[r for r in zero if not all(r[k] for k in ['bbox','expected','total_padding_line_heights'])],
        bbox_drift=box_drift,failures=failures,
        scope='Fresh native crop replay with saved raw page-context observations; no source-page detector rerun.',
        source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [report_path,native_path,context_path,population_path]} | detail_sources)
    (D/'cp3_calibration_summary.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('flips','theta0_comparisons','source_sha256')},ensure_ascii=False,indent=2),flush=True)
    assert not failures and receipt['rows']==888


if __name__=='__main__':main()
