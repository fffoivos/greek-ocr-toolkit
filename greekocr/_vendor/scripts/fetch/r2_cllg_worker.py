"""Linux CLLG worker: stdin JSON crop-path list -> stdout JSON string list.

--describe emits the loaded model binding instead. No model downloads, page
segmentation, binarization, or Unicode normalization occur here.
--serve keeps the model loaded for newline-delimited JSON requests.
--confidence returns text, character probabilities and mean/min/log summaries.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.metadata
import inspect
import json
import math
import os
from pathlib import Path
import re
import sys


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def load(checkpoint, expected_hash):
    import torch
    from kraken.configs import RecognitionInferenceConfig
    from kraken.lib.dataset import ImageInputTransforms
    from kraken.lib.ppocr import PPOCRv6Model
    from kraken.models import load_safetensors
    from kraken.tasks import RecognitionTaskModel

    version = importlib.metadata.version('kraken')
    if version != '7.1.1':
        raise ValueError('CLLG worker requires pinned Kraken 7.1.1; installed '+version)
    actual_hash = file_sha256(checkpoint)
    if actual_hash != expected_hash:
        raise ValueError('CLLG checkpoint SHA256 changed')
    nets = load_safetensors(checkpoint, tasks=['recognition'])
    if len(nets) != 1 or not isinstance(nets[0], PPOCRv6Model):
        raise ValueError('CLLG must contain exactly one PP-OCRv6 recognition model')
    net = nets[0]
    # Execution placement is an environment choice, not model identity: it is kept out of the binding.
    # CLLG_ACCELERATOR=cuda needs a CUDA torch in the worker venv (see r2_cllg_env.sh for the CPU pin).
    accelerator = os.environ.get('CLLG_ACCELERATOR', 'cpu')
    if accelerator not in ('cpu', 'cuda'):
        raise ValueError('CLLG_ACCELERATOR must be cpu or cuda')
    if accelerator == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('CLLG_ACCELERATOR=cuda but torch.cuda.is_available() is False')
    threads = int(os.environ.get('CLLG_THREADS', '1'))
    net.float().eval()
    net.cuda() if accelerator == 'cuda' else net.cpu()
    config = RecognitionInferenceConfig(accelerator=accelerator, device=1,
        precision='32-true', batch_size=1, num_line_workers=0, padding=16,
        bidi_reordering=False, num_threads=threads)
    torch.set_num_threads(config.num_threads)

    batch, channels, height, width = net.input
    # This is the same transform constructor used by upstream CTC bbox
    # inference. RGB input prevents CenterNormalizer even with valid_norm=True.
    args = (batch, height, width, channels, (config.padding, 0))
    parameters = inspect.signature(ImageInputTransforms).bind(*args, valid_norm=True, dtype=torch.float32)
    parameters.apply_defaults()
    transforms = ImageInputTransforms(*args, valid_norm=True, dtype=torch.float32)
    source = Path(inspect.getfile(ImageInputTransforms)).resolve()
    values = dict(parameters.arguments)
    values['dtype'] = str(values['dtype'])
    prep = dict(factory='kraken.lib.dataset:ImageInputTransforms', input_shape=list(net.input),
        parameters=values, source_sha256=file_sha256(source), kraken_version=version,
        input_color='PIL grayscale L; upstream converts to RGB', tensor_dtype='float32',
        transforms=[re.sub(r'0x[0-9a-fA-F]+', '<address>', repr(t)) for t in transforms.transforms],
        crop_geometry='full-image bbox; no baseline or polygon warp',
        output_normalization='none')
    mapping = getattr(net.codec, 'c2l', None)
    if not isinstance(mapping, dict) or not mapping:
        raise ValueError('loaded CLLG model has no codec')
    order = sorted((dict(text=text, labels=list(labels)) for text, labels in mapping.items()),
                   key=lambda entry: (entry['labels'], entry['text']))
    binding = dict(checkpoint_sha256=actual_hash, class_order=order, preprocess=prep,
        loader='kraken.models:load_safetensors', loader_sha256=file_sha256(inspect.getfile(load_safetensors)),
        model_class='kraken.lib.ppocr:PPOCRv6Model', model_source_sha256=file_sha256(inspect.getfile(PPOCRv6Model)),
        preprocessing_source=str(source), preprocessing_source_sha256=file_sha256(source),
        runtime_versions={name: importlib.metadata.version(name) for name in
                          ('kraken', 'torch', 'torchvision', 'safetensors', 'lightning', 'Pillow')})
    return RecognitionTaskModel(nets), config, json.loads(json.dumps(binding))


def recognize(model, config, paths, *, confidence=False):
    from PIL import Image
    from kraken.containers import BBoxLine, Segmentation

    if not isinstance(paths, list) or any(not isinstance(path, str) for path in paths):
        raise ValueError('stdin must be a JSON list of crop paths')
    predictions = []
    for path in paths:
        with Image.open(path) as image:
            image = image.convert('L')
            segmentation = Segmentation(type='bbox', imagename=path,
                text_direction='horizontal-lr', script_detection=False,
                lines=[BBoxLine(id='line-0', bbox=(0, 0, image.width, image.height))])
            records = list(model.predict(image, segmentation, config))
        if len(records) != 1 or not isinstance(records[0].prediction, str):
            raise ValueError('Kraken must return exactly one string for each crop')
        if confidence:
            probabilities = [float(value) for value in records[0].confidences]
            if any(not math.isfinite(p) or not 0 <= p <= 1 for p in probabilities):
                raise ValueError('Kraken character confidences must be finite probabilities in [0, 1]')
            predictions.append(dict(text=records[0].prediction,
                character_confidences=probabilities,
                mean_confidence=sum(probabilities)/len(probabilities) if probabilities else None,
                min_confidence=min(probabilities) if probabilities else None,
                mean_log_probability=sum(math.log(max(p, 1e-300)) for p in probabilities)/len(probabilities)
                    if probabilities else None))
        else:
            predictions.append(records[0].prediction)
    return predictions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint', type=Path, required=True)
    parser.add_argument('--checkpoint-sha256', required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--describe', action='store_true')
    mode.add_argument('--serve', action='store_true')
    parser.add_argument('--confidence', action='store_true')
    args = parser.parse_args()
    # Imports and upstream diagnostics cannot contaminate the JSON protocol.
    with contextlib.redirect_stdout(sys.stderr):
        model, config, binding = load(args.checkpoint, args.checkpoint_sha256)
    if args.serve:
        for line in sys.stdin:
            try:
                with contextlib.redirect_stdout(sys.stderr):
                    result = recognize(model, config, json.loads(line), **({'confidence': True} if args.confidence else {}))
            except Exception as error:
                result = {'error': str(error)}
            print(json.dumps(result, ensure_ascii=False, allow_nan=False), flush=True)
        return
    with contextlib.redirect_stdout(sys.stderr):
        result = binding if args.describe else recognize(model, config, json.load(sys.stdin),
            **({'confidence': True} if args.confidence else {}))
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))


if __name__ == '__main__':
    main()
