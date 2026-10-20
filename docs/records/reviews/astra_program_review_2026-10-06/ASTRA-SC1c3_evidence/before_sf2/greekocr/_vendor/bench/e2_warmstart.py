"""Weights-only head swap: retain donor backbone+neck, produce donor_init.pt.

Uses the official installed Transformers mapping for R01 and byte-pinned local
config/weights. R03 maps upstream encoder and CTC FRM to the vendored network.
Native logits parity is a separate node gate, never inferred from key compatibility.
"""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
import torch
from greekocr._vendor.bench.common import sha256
from greekocr._vendor.bench.e1_common import ROOT, atomic_json, read_json
from greekocr._vendor.bench.e2_models import build_donor

SOURCES = {
 'R01': dict(url='https://huggingface.co/PaddlePaddle/el_PP-OCRv5_mobile_rec_safetensors',licence='Apache-2.0'),
 'R03': dict(url='https://drive.google.com/drive/folders/12ZUGkCS7tEhFhWa2RKKtyB0tPjhH4d9s',licence='Apache-2.0'),
 'R02': dict(url='https://huggingface.co/PaddlePaddle/PP-OCRv6_small_rec_safetensors',licence='Apache-2.0'),
}


def checkpoint_hash(payload):
    from greekocr._vendor.train import train as trainer
    trainer._runtime()
    return trainer.checkpoint_state_sha256(payload)


def load_state(path):
    if str(path).endswith('.safetensors'):
        from safetensors.torch import load_file
        return load_file(str(path))
    obj=torch.load(path,map_location='cpu',weights_only=True)
    return obj.get('state_dict',obj.get('model',obj))


def mapping(family, state):
    """Exact key mapping. Unexpected extra layers fail; no fuzzy shape/name matching."""
    mapped={}; layers={}; dropped=[]
    for key,value in state.items():
        if key.startswith('module.'): key=key[7:]
        if family in ('R01','R02'):
            if key.startswith(('model.backbone.','head.encoder.','head.head.')):
                new='native.'+key
            else: raise ValueError('official HF mapping missing/unrecognized donor key: '+key)
        elif family=='R03':
            if key.startswith('encoder.'): new=key
            elif key.startswith('decoder.ctc_decoder.'): new='decoder.'+key[len('decoder.ctc_decoder.'):]
            elif key.startswith('decoder.gtc_decoder.'):
                dropped.append(key); continue
            else: raise ValueError('unrecognized R03 donor key: '+key)
        else: raise ValueError('unknown donor')
        if new in mapped: raise ValueError('duplicate mapped layer')
        mapped[new]=value; layers[key]=dict(target=new,transform='identity')
    return mapped,layers,dropped


def paddle_map(state, layer_map, expected):
    """Node-only Paddle -> official HF map. Every retained key explicitly bound.

    Paddle Linear [in,out] -> Torch [out,in] uses transpose2d; conv weights
    remain OIHW; BatchNorm _mean/_variance -> running_mean/running_var.
    A reviewed layer map is required; a guessed regex is not a parity proof.
    """
    result={}; used=set()
    for source, spec in layer_map.items():
        target=spec['target']; value=torch.as_tensor(state[source])
        if spec['transform']=='transpose2d': value=value.T.contiguous()
        elif spec['transform']!='identity': raise ValueError('unknown Paddle layer transform')
        if target not in expected or value.shape != expected[target].shape: raise ValueError('Paddle mapping shape mismatch: '+source)
        result[target]=value; used.add(source)
    for name,value in expected.items():
        if name.endswith('num_batches_tracked') and name not in result: result[name]=torch.zeros_like(value)
    if set(result)!=set(expected): raise ValueError('incomplete Paddle mapping')
    leftovers=set(state)-used
    if any(not k.startswith('head.nrtr') for k in leftovers): raise ValueError('unmapped retained Paddle layers')
    return result


def verify_init(path):
    ck=torch.load(path,map_location='cpu',weights_only=True)
    if ck.get('state_hash_version')!=2 or ck.get('state_sha256')!=checkpoint_hash(ck):
        raise ValueError('donor_init state digest mismatch')
    return ck


def convert(family, checkpoint, config, out, revision, *, seed=0, codec=ROOT/'codec/v1.json'):
    import sys
    sys.path.insert(0,str(ROOT/'train'))
    from greekocr._vendor.train.cer import load_codec
    if str(config).endswith(('.yml','.yaml')):
        import yaml
        source_config=yaml.safe_load(Path(config).read_text())
        if family!='R03': raise ValueError('R01/R02 require the official HF config.json')
        spec=dict(encoder=source_config['Architecture']['Encoder'])
    else: spec=read_json(config)
    classes=load_codec(str(codec)).n_classes
    if classes!=248 or load_codec(str(codec)).version!='v1': raise ValueError('E2 pins codec v1 = 248; v2 is later')
    if not revision or revision in ('main','HEAD','latest'): raise ValueError('immutable donor revision required')
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    raw=load_state(checkpoint); mapped,layers,dropped=mapping(family,raw)
    classifier='decoder.fc' if family=='R03' else 'native.head.head'
    original_classes=mapped[classifier+'.weight'].shape[0]
    model=build_donor(family,spec,original_classes)
    # HF deliberately omits these BN counters. Fill only this named, documented state.
    for name,value in model.state_dict().items():
        if name.endswith('num_batches_tracked') and name not in mapped: mapped[name]=torch.zeros_like(value)
    model.load_state_dict(mapped,strict=True)
    original=dict(model={k:v.clone() for k,v in model.state_dict().items()}, family=family,
                  config=spec,n_classes=original_classes,source_sha256=sha256(checkpoint))
    torch.save(original,out/'native_before_swap.pt')
    retained={k:v for k,v in mapped.items() if not k.startswith(classifier+'.')}
    torch.manual_seed(seed)
    swapped=build_donor(family,spec,classes)
    new_state=swapped.state_dict()
    for name,value in retained.items(): new_state[name]=value
    swapped.load_state_dict(new_state,strict=True)
    for k in retained:
        if not torch.equal(swapped.state_dict()[k],mapped[k]): raise ValueError('retained layer changed: '+k)
    dropped += [k for k,v in layers.items() if v['target'].startswith(classifier+'.')]
    provenance=dict(family=family,source_url=SOURCES[family]['url'],revision=revision,licence=SOURCES[family]['licence'],
        source_sha256=sha256(checkpoint),config_sha256=sha256(config),codec_sha256=sha256(codec),
        layer_mapping=layers,dropped_layers=dropped,seed=seed,
        final_classifier=dict(input=256 if family=='R03' else 120,output=classes),
        channels='retain RGB kernels; trainer replicates grayscale; no averaging',
        time_contract='R01/R02 trainer-only right-background extension to W multiple of 4; original logits parity endpoints have no extension',
        auxiliary_removed='SMTR' if family=='R03' else 'NRTR (absent in official HF release)',
        parity_status='node-only: native pre-softmax parity not yet run',
        preprocessing='native parity contract supplied in donor spec; training uses frozen 48px/own-bg strip contract')
    atomic_json(out/'donor_provenance.json',provenance)
    payload=dict(model={k:v.clone() for k,v in swapped.state_dict().items()},arch='e2_'+family.lower(),head='nfd',
        codec_version='v1',n_classes=classes,codec_sha256=sha256(codec),state_hash_version=2,
        donor_provenance_sha256=sha256(out/'donor_provenance.json'),config=spec)
    payload['state_sha256']=checkpoint_hash(payload)
    torch.save(payload,out/'donor_init.pt')
    verify_init(out/'donor_init.pt')
    return provenance


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--donor',choices=SOURCES,required=True);p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--config',type=Path,required=True);p.add_argument('--revision',required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--seed',type=int,default=0)
    a=p.parse_args();convert(a.donor,a.checkpoint,a.config,a.out,a.revision,seed=a.seed)


if __name__=='__main__': main()
