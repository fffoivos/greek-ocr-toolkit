"""E2's E1 crop reader and mandatory 200-row v7 evaluation-path gate.

No network or accelerator use. Production qualification needs the staged v7
shards and retrained checkpoints; fixture qualification is never a substitute.
"""
from __future__ import annotations
from pathlib import Path
import sys
import tempfile
import numpy as np
from PIL import Image
from greekocr._vendor.bench.common import sha256
from greekocr._vendor.bench.e1_common import ROOT, atomic_json
from greekocr._vendor.bench.o4b_models import E1, strip


class E1Reader(E1):
    """Use evaluation's uint8 padding, FP32 scaling and raw atom decoder."""
    def __init__(self, checkpoint, codec, device='cpu'):
        super().__init__(checkpoint, codec, device)
        self.binding.update(adapter_sha256=sha256(__file__),
            preprocessing='48px exported strips unchanged; raw crops import-real resize/letterbox; '
                          'train.data.collate_strips uint8 own-bg halo, FP32 px/255 -> (x-.5)/.5',
            decoder='train.cer.greedy_decode_line; raw atoms, no serving NFC conversion',
            data_sha256=sha256(ROOT/'train/data.py'),
            model_sha256=sha256(ROOT/'train/model.py'),
            decoder_sha256=sha256(ROOT/'train/cer.py'),
            resize_sha256=sha256(ROOT/'bench/o4b_models.py'))

    def sample(self, path):
        with Image.open(path) as image:
            if image.mode == 'L' and image.height == 48 and 64 <= image.width <= 2560:
                # Avoid resampling/letterboxing a factory strip a second time.
                pixels = np.asarray(image, dtype=np.uint8).copy()
            else:
                pixels = np.rint(strip(image)*255).clip(0,255).astype(np.uint8)
        return dict(image=pixels, width=pixels.shape[1], label=np.array([1],dtype=np.int64),
                    script_class='unknown')

    def preprocess(self, path):
        from greekocr._vendor.train.data import collate_strips
        return collate_strips([self.sample(path)])

    def read(self, path):
        import torch
        from greekocr._vendor.train.cer import greedy_decode_line
        from greekocr._vendor.train.model import masked_forward
        batch = self.preprocess(path)
        with torch.inference_mode():
            logits = masked_forward(self.rec.model, batch['images'].to(self.rec.device), batch['input_lengths'])
        length = int(batch['input_lengths'][0])
        return greedy_decode_line(logits[0,:length].argmax(-1).cpu().tolist(), self.rec.codec)


def compare_paths(rows, engine, reference_model, codec, cropdir):
    """Exact decoded strings; evaluation retains factory label_ids and bs64."""
    import torch
    from greekocr._vendor.train.data import ManifestDataset, make_loader
    from greekocr._vendor.train.eval_cer import evaluate
    from greekocr._vendor.train.model import amp_dtype_for
    cropdir = Path(cropdir); cropdir.mkdir(parents=True, exist_ok=True)
    dataset = ManifestDataset(rows, codec.version, codec.n_classes-1, 'reserved')
    loader, sampler = make_loader(dataset, 64, shuffle=False)
    indices = iter(i for batch in sampler for i in batch)
    references = {}
    def collect(ref, hyp, edits): references[next(indices)] = (ref,hyp)
    evaluate(reference_model, loader, codec, torch.device('cpu'),
             amp_dtype=amp_dtype_for(torch.device('cpu')), line_callback=collect)
    checks = []
    for i,row in enumerate(rows):
        crop = cropdir/f'{i:04d}.png'; crop.write_bytes(row['image_png'])
        ref,hyp = references[i]; actual = engine.read(crop)
        checks.append(dict(line_id=row['line_id'], crop_sha256=sha256(crop),
            gt=ref, evaluation=hyp, reader=actual, identical=hyp == actual))
    matched = sum(c['identical'] for c in checks)
    return dict(rows=len(rows), identical=matched, identical_fraction=matched/len(rows),
                passed=len(rows)>=200 and matched/len(rows)>=.99, checks=checks)


def qualify_readers(candidates, mix_path, out):
    """Run before bake-off scoring, every time; no trust in stale pass booleans."""
    out = Path(out)
    specs = {n:s for n,s in candidates.items() if s['kind']=='e1'}
    report = dict(schema='e2-reader-parity-v1', passed=False, required_rows=200,
        required_identical_fraction=.99, device='cpu', batch_size=64,
        comparison='exact raw decoded strings; no Unicode or whitespace folding',
        candidates={}, evaluator_sha256=sha256(ROOT/'train/eval_cer.py'),
        adapter_sha256=sha256(__file__))
    try:
        if not specs:
            report.update(passed=True, status='not_required: no E1 candidates')
            atomic_json(out/'reader_parity.json',report)
            return {}
        if mix_path is None: raise ValueError('v7 mix required for reader parity before scoring')
        from greekocr._vendor.train.mix import validate, load_rows
        mix = validate(mix_path, role='eval')
        components = mix['components']
        if (len(components)!=1 or components[0]['kind']!='synthetic' or components[0]['fraction']!=1
                or components[0]['recipe_sha256']!=sha256(ROOT/'factory/recipe.v7.json')):
            raise ValueError('reader parity requires the bound v7 synthetic held-out instrument')
        pools = load_rows(mix,'reserved')
        rows = sorted(pools[0],key=lambda r:r['line_id'])[:200]
        if len(rows)!=200 or len({r['line_id'] for r in rows})!=200:
            raise ValueError('reader parity needs 200 distinct v7 rows')
        report.update(mix_sha256=sha256(mix_path), resolved_mix=mix,
            data_sha256=sha256(ROOT/'train/data.py'), model_sha256=sha256(ROOT/'train/model.py'),
            codec_sha256=sha256(ROOT/'codec/v1.json'))
        sys.path.insert(0,str(ROOT/'train'))
        from greekocr._vendor.train.cer import load_codec
        from greekocr._vendor.train.eval_cer import load_checkpoint
        from greekocr._vendor.bench.e2_teachers import reader
        import torch
        codec = load_codec(str(ROOT/'codec/v1.json')); engines = {}
        for name,spec in specs.items():
            engine = reader(spec); engines[name] = engine
            # Same trusted tensor-only wrapper as e1_eval, independently loaded
            # through the evaluator, rather than reusing the serving model.
            state = torch.load(spec['checkpoint'],map_location='cpu',weights_only=False)
            with tempfile.TemporaryDirectory(prefix='e2-reader-weights-') as temp:
                weights = Path(temp)/'weights.pt'
                torch.save({k:state[k] for k in ('model','arch','head','codec_version','n_classes')},weights)
                model,_ = load_checkpoint(str(weights),codec,torch.device('cpu'))
            check = compare_paths(rows,engine,model,codec,out/'reader_parity_crops')
            report['candidates'][name] = dict(binding=engine.binding, **check)
            del model
        report['passed'] = all(c['passed'] for c in report['candidates'].values())
        atomic_json(out/'reader_parity.json',report)
        if not report['passed']: raise ValueError('reader parity below 99% identical decoded strings on 200 v7 rows')
        return engines
    except Exception as error:
        report.update(passed=False, reason=str(error))
        atomic_json(out/'reader_parity.json',report)
        raise
