#!/usr/bin/env python3
"""Factory-manifest final-best evaluation using the unchanged strict evaluator."""
import argparse
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from greekocr._vendor.bench.common import write_rows
from greekocr._vendor.bench.e1_common import ROOT, atomic_json, read_json, sha256, check_files
from greekocr._vendor.train.mix import validate, load_rows


def evaluate_run(out, run_name, instrument, mix_path, *, device='cuda', extra_metadata=None):
    # Gate before Torch/model/device, as in training.
    mix = validate(mix_path, role='eval')
    pools = load_rows(mix, 'reserved')
    if len(pools) != 1 or mix['components'][0]['fraction'] != 1:
        raise ValueError('E1 instrument must be a single complete factory component')
    rows = pools[0]
    dest = Path(out)/'runs'/run_name
    complete = read_json(dest/'E1_RUN_COMPLETE.json')
    transfer_digest = complete['binding']['transfer_binding_sha256']
    if transfer_digest is not None:
        check_files(read_json(Path(out)/'transfer_binding.json'))
        if sha256(Path(out)/'transfer_binding.json') != transfer_digest:
            raise ValueError('transfer custody snapshot changed since training')
    elif instrument == 'transfer_dev':
        raise ValueError('transfer evaluation was disabled for this run')
    component = mix['components'][0]
    disclosure = component.get('disclosure') if component['kind'] == 'legacy_eval' else None
    for name, digest in complete['checkpoint_hashes'].items():
        if sha256(dest/name) != digest:
            raise ValueError('final checkpoint changed after completion')
    for name, digest in complete['artifact_hashes'].items():
        if sha256(dest/name) != digest:
            raise ValueError('training log/metadata changed after completion')
    if sha256(dest/'data_provenance.json') != complete['provenance_sha256']:
        raise ValueError('training provenance changed')
    ckpt = dest/'best.pt'
    import torch
    from greekocr._vendor.bench.e1_common import runtime_binding
    sys.path.insert(0, str(ROOT/'train'))
    from greekocr._vendor.train.cer import load_codec
    from greekocr._vendor.train.data import ManifestDataset, make_loader
    from greekocr._vendor.train.eval_cer import evaluate, load_checkpoint
    from greekocr._vendor.train.model import amp_dtype_for
    runtime = runtime_binding(device)
    if complete['runtime'] != runtime:
        raise ValueError('evaluation runtime differs from training runtime')
    pred = Path(out)/'predictions'/f'{run_name}_{instrument}.jsonl'
    receipt = pred.with_suffix('.receipt.json')
    binding = dict(checkpoint_sha256=sha256(ckpt), provenance_sha256=complete['provenance_sha256'],
        mix_sha256=sha256(mix_path), resolved_mix=mix, runtime=runtime, bs=64,
        component_receipts={str(Path(c['build_dir'] if c['kind']=='synthetic' else c['shard_dir'])/'build_info.json'):
                            sha256(Path(c['build_dir'] if c['kind']=='synthetic' else c['shard_dir'])/'build_info.json')
                            for c in mix['components']},
        codec_sha256=sha256(ROOT/'codec/v1.json'), evaluator_sha256=sha256(ROOT/'train/eval_cer.py'),
        adapter_sha256=sha256(__file__))
    metadata = {}
    if component['kind'] == 'real':
        sidecar = Path(component['shard_dir'])/'word_tags.jsonl'
        info = read_json(Path(component['shard_dir'])/'build_info.json')
        digest = info.get('word_tags_sha256')
        if digest is None:
            # E1's historical receipt predates this optional field. Never use an
            # unbound sidecar, even if somebody has staged one next to it.
            binding.update(word_tags='absent', word_tags_source='rule-derived',
                word_tags_disclosure='word_tags: absent; historical receipt has no bound sidecar; displayed tags are rule-derived')
        else:
            if sha256(sidecar) != digest:
                raise ValueError('real word-tag sidecar changed')
            from greekocr._vendor.bench.common import read_rows
            metadata = {r['line_id']: r for r in read_rows(sidecar)}
            binding.update(word_tags='present', word_tags_source='factory-sidecar', word_tags_sha256=digest)
    else:
        binding.update(word_tags='absent', word_tags_source='rule-derived')
    binding['word_tags_rule_sha256'] = sha256(ROOT/'bench/line_categories.py')
    if extra_metadata:
        from greekocr._vendor.bench.common import read_rows
        for r in read_rows(extra_metadata):
            metadata.setdefault(r['line_id'], {}).update({k:r[k] for k in
                ('font_names','font_size_pt','size_pt','size','page_median_font_size_pt','italic','bold') if k in r})
        binding['extra_metadata_sha256'] = sha256(extra_metadata)
    if receipt.exists():
        saved = read_json(receipt)
        if saved['binding'] != binding or saved['predictions_sha256'] != sha256(pred):
            raise ValueError('stale or altered E1 evaluation receipt')
        for name,digest in saved['crop_hashes'].items():
            if sha256(name) != digest:
                raise ValueError('materialized evaluation crop changed')
        return saved
    codec = load_codec(str(ROOT/'codec/v1.json'))
    ds = ManifestDataset(rows, codec.version, codec.n_classes-1, 'reserved')
    loader, sampler = make_loader(ds, 64, shuffle=False)
    indices = iter(i for batch in sampler for i in batch)
    provenance = read_json(dest/'data_provenance.json')
    seen = {f for e in provenance['epochs'].values() for f in e['train']['marginals']['counts']['font']}
    heldout = set(read_json(ROOT/'factory/recipe.v5.json')['fonts']['held_out'])
    predicted = []
    cropdir = Path(out)/'eval_crops'/instrument
    cropdir.mkdir(parents=True, exist_ok=True)
    def collect(ref, hyp, edits):
        index = next(indices); row = rows[index]
        crop = cropdir/f'{index:06d}.png'
        if crop.exists() and crop.read_bytes() != row['image_png']:
            raise ValueError('materialized eval crop changed')
        crop.write_bytes(row['image_png'])
        meta = {k:v for k,v in row.items() if k not in ('image_png','label_ids','gt_nfd','gt_nfc') and not k.startswith('_')}
        font = row['font']
        status = 'seen' if font in seen else 'held_out' if font in heldout else 'unknown' if font in ('real','unknown','') else 'held_out'
        predicted.append(dict(meta, gt=ref, prediction=hyp, edits=edits, crop_path=str(crop),
            font_status=status, arm=run_name.rsplit('_s',1)[0], seed=int(run_name.rsplit('_s',1)[1]), instrument=instrument))
        from greekocr._vendor.bench.line_categories import word_tags, categories, RULE_VERSION
        side = metadata.get(row['line_id'], {})
        predicted[-1].update({k:side[k] for k in ('word_tags','font_names','font_size_pt','size_pt','size',
                            'page_median_font_size_pt','italic','bold') if k in side})
        predicted[-1].setdefault('word_tags', word_tags(ref))
        predicted[-1].update(word_tags_status=binding['word_tags'], word_tags_source=
            'factory-sidecar' if 'word_tags' in side else 'rule-derived')
        predicted[-1].update(line_categories=categories(predicted[-1]), category_rule=RULE_VERSION)
        if disclosure:
            predicted[-1].update(component_kind='legacy_eval', provenance_status='unprovenanced_recipe',
                                 disclosure=disclosure)
    # Trusted, hash-bound checkpoints from this runner only. A tensor-only temporary wrapper
    # makes the unchanged safe eval loader work without a safetensors installation.
    donor = torch.load(ckpt, map_location='cpu', weights_only=False)
    with tempfile.TemporaryDirectory(prefix='e1-weights-') as temp:
        weights = Path(temp)/'weights.pt'
        torch.save({k:donor[k] for k in ('model','arch','head','codec_version','n_classes')}, weights)
        del donor
        model, _ = load_checkpoint(str(weights), codec, torch.device(device))
    result = evaluate(model, loader, codec, torch.device(device), amp_dtype=amp_dtype_for(torch.device(device)),
                      per_script=True, line_callback=collect)
    if result['n_lines'] != len(rows):
        raise ValueError('evaluation did not cover complete instrument')
    pred.parent.mkdir(parents=True, exist_ok=True)
    tmp = pred.with_suffix('.jsonl.tmp'); write_rows(tmp, predicted); tmp.replace(pred)
    saved = dict(binding=binding, predictions_sha256=sha256(pred), result=result,
                 crop_hashes={r['crop_path']:sha256(r['crop_path']) for r in predicted})
    saved['result'].update(word_tags=binding['word_tags'], word_tags_source=binding['word_tags_source'])
    if disclosure:
        from greekocr._vendor.train.mix import disclose_numbers
        disclose_numbers(saved['result'], disclosure)
    atomic_json(receipt, saved)
    print(f'E1_EVAL: {run_name}/{instrument}: CER={result["cer"]:.6f}' +
          (f' [unprovenanced_recipe: {disclosure}]' if disclosure else ''), flush=True)
    return saved


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--run', required=True)
    ap.add_argument('--instrument', required=True)
    ap.add_argument('--mix', required=True, type=Path)
    a = ap.parse_args()
    evaluate_run(a.out, a.run, a.instrument, a.mix)
