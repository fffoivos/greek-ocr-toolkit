"""Frozen paired statistics, exact native validation and per-source receipts."""
from __future__ import annotations
import sys,json,hashlib
from collections import defaultdict,Counter
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(OUT));sys.path.insert(0,str(OUT.parent))
import run as current
prior=current.prior
# Reuse T6a's seeded paired line and page-cluster bootstrap implementation.
import importlib.util
spec=importlib.util.spec_from_file_location('t6a_summary',OUT.parent/'summarize.py')
legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)


def paired_stats(rr,key):
    result=legacy.paired_stats([dict(r,recut_edits=r['masked_edits']) for r in rr],key)
    return {k.replace('recut','masked'):v for k,v in result.items()}


def validate(records):
    features,_=prior.bind();expected={r['id']:r for r in features}
    assert len(records)==len(expected)==5770 and set(expected)=={r['id'] for r in records}
    sources=defaultdict(lambda:dict(lines=0,changed=0,unchanged=0,masked_pixels=0))
    noop_pixels=0;reexecuted=0
    for r in records:
        e=expected[r['id']];box=e['crop_bbox']
        assert r['old_box']==r['crop_box']==box
        assert r['google_text']==e['label_after_conventions'] and r['original_page']==e['crop_page_path']
        paths=[OUT/r[f'{arm}_path'] for arm in ('original','masked')]
        for arm,path in zip(('original','masked'),paths):assert prior.file_sha256(path)==r[f'{arm}_sha256']
        assert r['original_sha256']==e['crop_sha256']
        with Image.open(paths[0]) as image:a=np.asarray(image).copy();mode=image.mode;size=image.size
        with Image.open(paths[1]) as image:b=np.asarray(image).copy();assert mode==image.mode and size==image.size
        assert size==(box[2]-box[0],box[3]-box[1])
        mask=np.any(a!=b,axis=2) if a.ndim==3 else a!=b
        assert bool(mask.any())==r['changed']
        assert int(mask.sum())==r['native_changed_pixels']
        if r['masked_pixel_count']!=r['native_changed_pixels']:
            # A local median may equal a selected pixel's original value. The
            # painted mask then cannot be reconstructed from the raster diff.
            from greekocr.glyphs.foreign_ink import mask_foreign_ink
            native=Image.open(r['original_page']).copy()
            lines=current.runtime_lines(native,r['page_id'])
            proposal=mask_foreign_ink(native,lines[r['runtime_index']],lines,box)
            assert np.array_equal(np.asarray(proposal.image),b)
            assert proposal.record['masked_pixel_count']==r['masked_pixel_count']
            assert not (mask&~proposal.mask).any()
            painted=proposal.mask;reexecuted+=1
            noop_pixels+=r['masked_pixel_count']-r['native_changed_pixels']
        else:
            painted=mask
        assert hashlib.sha256(painted.tobytes()).hexdigest()==r['mask_sha256']
        for fill in r['fills']:
            if fill['fill'] is not None:
                assert fill['ring_pixels']>0
                assert np.array_equal(np.rint(fill['ring_median']).astype(np.uint8),np.asarray(fill['fill'],np.uint8))
        if not r['changed']:assert r['original_sha256']==r['masked_sha256']
        v=sources[r['stratum']];v['lines']+=1;v['changed']+=r['changed'];v['unchanged']+=not r['changed'];v['masked_pixels']+=int(mask.sum())
    frozen=prior.read_json(OUT/'params.json')
    assert frozen['source_hashes']==current.source_hashes()
    assert frozen['params_sha256']==hashlib.sha256(json.dumps(frozen['params'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
    for path,digest in frozen['inputs'].items():assert prior.file_sha256(path)==digest
    caller_freeze=prior.read_json(OUT/'binding_freeze.json')
    for path,digest in caller_freeze['driver_hashes'].items():assert prior.file_sha256(OUT/path)==digest
    manifest=prior.read_json(OUT/'runtime_manifest.json')
    assert {r['page_id'] for r in records}=={p['page_id'] for p in manifest['pages']}
    curve_paths={p['path'] for p in manifest['pages']}
    for r in records:assert r['runtime_curves_path'] in curve_paths
    for p in manifest['pages']:
        assert prior.file_sha256(OUT/p['path'])==p['sha256']
        assert p['binding']['source_hashes']==frozen['source_hashes']
    for p in prior.rows(OUT/'f2/provenance.jsonl'):
        assert prior.file_sha256(p['source'])==p['source_sha256']
        assert prior.file_sha256(p['raw_response'])==p['raw_sha256']
        assert prior.file_sha256(Path(p['cache'])/'receipt.json')==p['cache_receipt_sha256']
    import subprocess
    preserved=['greekocr/glyphs/vertical_recut.py','greekocr/glyphs/recut.py','greekocr/glyphs/lines_api.py',
               'greekocr/pages/lines.py','greekocr/pages/pixels.py','greekocr/pages/tables.py',
               'greekocr/deploy/docling_plugin/model.py']
    assert not subprocess.check_output(['git','diff','9ac8b357','--',*preserved],cwd=ROOT)
    value=dict(native_pairs_verified=5770,all_original_hashes_match_pinned_features=True,
        all_masks_reconstructed_or_reexecuted_and_hash_verified=True,
        masks_reexecuted_for_noop_fill=reexecuted,selected_fill_pixels_already_equal_to_median=noop_pixels,
        all_geometry_labels_and_modes_unchanged=True,all_page_and_response_sources_reverified=True,
        fresh_runtime_curve_payloads_sha256_verified=True,frozen_driver_hashes_verified=True,
        per_source=dict(sources),unchanged_runtime_and_T6a_sources=preserved,network='OFF',w1_accessed=False)
    prior.write_json(OUT/'validation.json',value);return value


def main():
    frozen=prior.read_json(OUT/'params.json');records=prior.rows(OUT/'f2/records.jsonl')
    binding=prior.read_json(OUT/'harm/binding.json')
    assert binding['params_sha256']==frozen['params_sha256'] and binding['records_sha256']==prior.file_sha256(OUT/'f2/records.jsonl')
    assert binding['frozen_utc']<binding['started_utc']
    for name,key in [('out/e4/wave1a/job01/runs/ctrl_s0/best.pt','model_sha256'),('out/e4/wave1a/job01/runs/ctrl_s0/best.safetensors','weights_sha256'),('codec/v1.json','codec_sha256')]:
        assert prior.file_sha256(prior.OCR/name)==binding[key]
    for name,key in [('train/eval_cer.py','evaluator_sha256'),('train/data.py','collator_sha256'),('bench/o4b_models.py','preprocessing_sha256')]:
        assert prior.file_sha256(prior.OCR/name)==binding[key]
    old={r['id']:r for r in prior.rows(OUT/'harm/original.jsonl')};new={r['id']:r for r in prior.rows(OUT/'harm/masked.jsonl')}
    assert len(old)==len(new)==len(records)==5770 and set(old)==set(new)=={r['id'] for r in records}
    for arm in ('original','masked'):
        receipt=prior.read_json(OUT/'harm'/f'{arm}.receipt.json')
        assert receipt['binding']==binding and receipt['predictions_sha256']==prior.file_sha256(OUT/'harm'/f'{arm}.jsonl')
    pairs=[]
    for r in records:
        a,b=old[r['id']],new[r['id']]
        assert a['ref']==b['ref'] and a['ref_len']==b['ref_len']
        if not r['changed']:assert a['prediction']==b['prediction'] and a['edits']==b['edits']
        pairs.append(dict(id=r['id'],page_id=r['page_id'],stratum=r['stratum'],changed=r['changed'],
            geometry_clean=r['geometry_clean'],crop_ok=r['dev']['crop_ok'] if r['dev'] else None,
            original_edits=a['edits'],masked_edits=b['edits'],ref_len=a['ref_len'],
            original_prediction=a['prediction'],masked_prediction=b['prediction']))
    prior.write_rows(OUT/'harm/paired.jsonl',pairs)
    validation=validate(records)
    summary={}
    subsets=dict(all=lambda r:True,changed=lambda r:r['changed'],unchanged=lambda r:not r['changed'],
                 crop_ok_n=lambda r:r['crop_ok']=='n',crop_ok_y=lambda r:r['crop_ok']=='y',geometry_clean=lambda r:r['geometry_clean'])
    dev_summary=prior.read_json(OUT/'dev/summary.json')
    for source in (*prior.SOURCES,'overall'):
        rr=[r for r in pairs if source=='overall' or r['stratum']==source]
        summary[source]={name:paired_stats([r for r in rr if select(r)],f't6a2/{source}/{name}') for name,select in subsets.items()}
        if source!='overall':
            source_records=[r for r in records if r['stratum']==source]
            prior.write_json(OUT/source/'receipt.json',dict(source=source,lines=len(rr),
                changed=sum(r['changed'] for r in rr),unchanged_predictions_exact=True,
                params_sha256=frozen['params_sha256'],fresh_runtime_manifest_sha256=prior.file_sha256(OUT/'runtime_manifest.json'),records_sha256=prior.file_sha256(OUT/'f2'/source/'records.jsonl'),
                dev=dev_summary[source],harm=summary[source],native_validation=validation['per_source'][source],
                model_sha256=binding['model_sha256'],admitted=0,default_enabled=False))
    prior.write_json(OUT/'harm/summary.json',dict(results=summary,bootstrap_replicates=5000,
        difference='masked minus original; negative favours masking',
        bootstrap_methods=['paired line resampling','paired page-cluster resampling'],
        unchanged_predictions_exact=True,unchanged_lines=sum(not r['changed'] for r in records),
        overall_nonworsening_pass=summary['overall']['all']['difference']<=0,
        own_ink_safety_pass=dev_summary['overall']['own_y_lost']==0,
        admitted=0))
    custody_paths=['params.json','binding_freeze.json','runtime_manifest.json','f2/records.jsonl',
        'dev/records.jsonl','dev/component_audit.jsonl','dev/visual_review.jsonl','harm/binding.json',
        'harm/original.jsonl','harm/original_reproduction.json','harm/masked.jsonl','harm/paired.jsonl','harm/summary.json','validation.json','tests.log']
    prior.write_json(OUT/'experiment_identity.json',dict(params_sha256=frozen['params_sha256'],
        files={p:prior.file_sha256(OUT/p) for p in custody_paths},source_hashes=frozen['source_hashes'],
        admitted=0,default_enabled=False,network='OFF'))
    print(json.dumps(summary['overall'],indent=2),flush=True)

if __name__=='__main__':main()
