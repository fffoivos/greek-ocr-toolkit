"""Donor architecture adapters, installed only by the E2 launcher/evaluator.

Certified train.py is unchanged. RGB donor kernels are retained; grayscale is
replicated. Only the final classifier is swapped. No compact-backbone relabeling.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from PIL import Image
import torch
from torch import nn
from torch.nn import functional as F


def preprocess(image, contract):
    """Native parity/teacher input, not the trainer's 48-high strip transform."""
    import cv2
    image = image.convert('RGB'); array = np.asarray(image)
    w, h = image.size
    if contract['color'] == 'BGR': array = array[:, :, ::-1].copy()
    elif contract['color'] != 'RGB': raise ValueError('native color must be BGR/RGB')
    if contract.get('ratio_shapes'):
        rounding={'ceil':np.ceil,'nearest':np.around}[contract.get('ratio_rounding','ceil')]
        ratio = min(contract.get('max_ratio', 12), max(1, int(rounding(w/h))))
        height, width = contract['ratio_shapes'].get(str(ratio), (32,32*ratio))
    else:
        height = contract['height']; width = int(np.ceil(height*w/h))
        width = max(contract.get('min_width',1), min(width,contract.get('max_width',100000)))
    interpolation = {'linear':cv2.INTER_LINEAR, 'cubic':cv2.INTER_CUBIC,
                     'bicubic_pil':None}[contract['interpolation']]
    if interpolation is None:
        im = Image.fromarray(array).resize((width,height),Image.Resampling.BICUBIC); array=np.asarray(im)
    else: array=cv2.resize(array,(width,height),interpolation=interpolation)
    x = array.astype(np.float32)/255
    x = (x-np.asarray(contract.get('mean',[.5,.5,.5])))/np.asarray(contract.get('std',[.5,.5,.5]))
    if contract.get('pad_rule') == 'paddle_dynamic':
        # PaddleOCR predict_rec.resize_norm_img (single-image batch): imgW = int(H * max(W0/H, w/h)),
        # resized_w = min(ceil(H*w/h), imgW), right zero padding to imgW. W0 = pad_width (320 for PP-OCRv5 rec).
        target = int(height * max(contract['pad_width']/height, w/h))
        if width > target:
            array = cv2.resize(np.asarray(image)[:, :, ::-1].copy() if contract['color']=='BGR' else np.asarray(image),
                               (target,height), interpolation=interpolation) if interpolation is not None else array[:, :target]
            x = (array.astype(np.float32)/255 - np.asarray(contract.get('mean',[.5,.5,.5])))/np.asarray(contract.get('std',[.5,.5,.5]))
            width = target
        x = np.pad(x,((0,0),(0,target-width),(0,0)),constant_values=contract.get('pad_value',0))
    elif contract.get('pad_width'):
        if width > contract['pad_width']: raise ValueError('native pad width narrower than crop')
        x = np.pad(x,((0,0),(0,contract['pad_width']-width),(0,0)),constant_values=contract.get('pad_value',0))
    return torch.from_numpy(np.ascontiguousarray(x.transpose(2,0,1))).float()[None]


class PaddleDonor(nn.Module):
    def __init__(self, config, classes, family='R01'):
        super().__init__()
        if family == 'R01':
            from transformers import PPOCRV5MobileRecConfig as Config, PPOCRV5MobileRecForTextRecognition as Model
        elif family == 'R02':
            from transformers import PPOCRV6SmallRecConfig as Config, PPOCRV6SmallRecForTextRecognition as Model
        else: raise ValueError('unknown Paddle donor')
        self.native = Model(Config.from_dict(config))
        self.native.head.head = nn.Linear(self.native.head.head.in_features, classes)
        self.n_classes = classes

    def endpoints(self, x):
        features = self.native.model(x).last_hidden_state
        neck = self.native.head.encoder(features).last_hidden_state
        return dict(backbone=features, neck=neck, logits=self.native.head.head(neck))

    def forward(self, x):
        if x.shape[1:] and (x.shape[1] != 1 or x.shape[2] != 48): raise ValueError('E2 strip contract: B,1,48,W')
        original_width = x.shape[-1]
        # Paddle's final width pooling floors. Extend only background to the
        # next multiple of four for the trainer's ceil(W/4) time contract.
        extra = (-original_width) % 4
        if extra: x = torch.cat((x, x[..., -1:].expand(*x.shape[:-1], extra)), dim=-1)
        logits = self.endpoints(x.repeat(1,3,1,1))['logits']
        if logits.shape[1] != (original_width+3)//4: raise ValueError('donor violates CTC W/4 contract')
        return F.log_softmax(logits, dim=-1)


class R03Donor(nn.Module):
    def __init__(self, config, classes):
        super().__init__()
        from greekocr._vendor.rec.openocr_vendored.svtrv2_lnconv_two33 import SVTRv2LNConvTwo33
        from greekocr._vendor.rec.openocr_vendored.rctc_decoder import RCTCDecoder
        encoder = dict(config['encoder'])
        if encoder.get('dims') != [64,128,256] or encoder.get('depths') != [3,6,3]:
            raise ValueError('R03 requires upstream SVTRv2-T dimensions/depths, not our derived small arm')
        encoder.pop('name',None); encoder['in_channels']=3
        self.encoder = SVTRv2LNConvTwo33(**encoder)
        self.decoder = RCTCDecoder(in_channels=256, out_channels=classes)
        self.n_classes = classes

    def endpoints(self, x):
        backbone = self.encoder(x); captured = {}
        handle = self.decoder.fc.register_forward_hook(lambda m,a,b: captured.update(neck=a[0],logits=b))
        try: self.decoder(backbone)
        finally: handle.remove()
        return dict(backbone=backbone, **captured)

    def forward(self, x):
        if x.shape[1] != 1 or x.shape[2] != 48: raise ValueError('E2 strip contract: B,1,48,W')
        out=self.endpoints(x.repeat(1,3,1,1))['logits']
        if out.shape[1] != (x.shape[-1]+3)//4: raise ValueError('donor violates CTC W/4 contract')
        return F.log_softmax(out,dim=-1)


def build_donor(family, config, classes):
    return R03Donor(config,classes) if family=='R03' else PaddleDonor(config,classes,family)


def register(donors):
    """Explicit architecture registration outside the frozen trainer's source."""
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'train'))
    from greekocr._vendor.train import model
    from greekocr._vendor.train import train as trainer
    for family, config in donors.items():
        arch = 'e2_'+family.lower()
        model.ARCHS[arch] = lambda classes, f=family, c=config: build_donor(f,c,classes)
        if arch not in trainer.ARCH_CHOICES: trainer.ARCH_CHOICES += (arch,)
    return trainer
