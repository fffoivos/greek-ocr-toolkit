"""Offline E1 inference/logits adapter. No checkpoint fallback or downloads."""
from __future__ import annotations
import math
from pathlib import Path
import numpy as np
from PIL import Image
from greekocr._vendor.bench.common import sha256


def strip(image):
    image = image.convert('L')
    w, h = image.size
    nw, nh = max(1, round(w*48/h)), 48
    if nw > 2560:
        nw, nh = 2560, round(h*2560/w)
        if nh < 14: raise ValueError('strip_below_14px_floor')
    a = np.asarray(image.resize((nw, nh), Image.Resampling.LANCZOS), dtype=np.float32)/255
    out = np.full((48, max(64, nw)), float(np.median(a[:, -2:])), dtype=np.float32)
    out[(48-nh)//2:(48-nh)//2+nh, :nw] = a
    return out


class E1:
    def __init__(self, checkpoint, codec, device='cpu'):
        from greekocr._vendor.pipeline.recognize import Recognizer
        self.rec = Recognizer(str(checkpoint), str(codec), device)
        self.binding = dict(checkpoint_sha256=sha256(checkpoint), codec_sha256=sha256(codec),
                            adapter_sha256=sha256(__file__), preprocessing='import-real resize/letterbox + Recognizer own-bg halo')
        self.atoms = self.rec.codec.atom_by_id

    def read(self, path):
        with Image.open(path) as image: s = strip(image)
        return self.rec.recognize([s])[0][0]

    def logits(self, image):
        import torch
        from greekocr._vendor.train.model import DET_PAD_MARGIN, masked_forward
        s = strip(image); width = s.shape[1]
        canvas = np.pad(s, ((0, 0), (0, DET_PAD_MARGIN)), constant_values=float(np.median(s[:, -2:])))
        batch = torch.from_numpy((canvas-.5)/.5)[None, None].to(self.rec.device)
        lengths = torch.tensor([math.ceil(width/4)])
        with torch.no_grad():
            lp = masked_forward(self.rec.model, batch, lengths)[0, :int(lengths[0])]
        return lp.cpu().numpy().astype(np.float64)


class DBNet:
    def __init__(self, checkpoint, device='cpu'):
        from greekocr._vendor.train.detector_common import build_model
        self.model = build_model('db_mobilenet_v3_large', str(checkpoint), device).eval()
        self.device = device
        self.binding = dict(backend='local docTR DBNet db_mobilenet_v3_large', checkpoint_sha256=sha256(checkpoint),
                            two_pass=True, ink_gate=True, reading_order='DT8', box_thresh=.1)

    def boxes(self, image):
        from greekocr._vendor.pipeline.page_ocr_detector import detect_lines
        return detect_lines(self.model, np.asarray(image.convert('L'), dtype=np.float32)/255, self.device)
