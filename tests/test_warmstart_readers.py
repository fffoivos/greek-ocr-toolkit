import copy
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import numpy as np
import pytest
import torch
from PIL import Image
from greekocr.warmstart import map_donor_state, map_paddle_state, preprocess, compare_endpoints, convert_donor, verify_init, qualify_parity
from greekocr.readers import load_ours, load_kalchas, load_cllg, load_cllg_worker, load_service, load_paddle_r01, load_r03, build_cllg_contract
from greekocr._vendor.bench.e2_teachers import Unavailable


def test_r03_key_mapping_preserves_frm_drops_only_auxiliary():
    keys=('encoder.x','decoder.ctc_decoder.char_token','decoder.ctc_decoder.fc_kv.weight',
          'decoder.ctc_decoder.w_atten_block.x','decoder.ctc_decoder.fc.weight','decoder.gtc_decoder.x')
    state={k:torch.ones(2,2) for k in keys}
    mapped,layers,dropped=map_donor_state('R03',state)
    assert 'decoder.char_token' in mapped and 'decoder.fc_kv.weight' in mapped
    assert dropped==['decoder.gtc_decoder.x'] and layers['encoder.x']['transform']=='identity'
    assert torch.equal(mapped['encoder.x'],state['encoder.x'])
    with pytest.raises(ValueError,match='unrecognized'):map_donor_state('R03',{'bad':torch.ones(1)})

@pytest.mark.parametrize('family',['R01','R02'])
def test_paddle_torch_mapping_explicit(family):
    state={'module.model.backbone.x':torch.ones(2),'head.encoder.x':torch.ones(2),'head.head.weight':torch.ones(2,2)}
    mapped,_,dropped=map_donor_state(family,state)
    assert set(mapped)=={'native.model.backbone.x','native.head.encoder.x','native.head.head.weight'} and not dropped
    with pytest.raises(ValueError,match='unrecognized'):map_donor_state(family,{'foo':torch.zeros(1)})


def test_paddle_transpose_and_exhaustive_map():
    expected={'head.weight':torch.zeros(3,2),'bn.num_batches_tracked':torch.zeros((),dtype=torch.int64)}
    state={'linear':np.arange(6).reshape(2,3),'head.nrtr.aux':np.ones(2)}
    mapping={'linear':dict(target='head.weight',transform='transpose2d')}
    mapped=map_paddle_state(state,mapping,expected)
    assert torch.equal(mapped['head.weight'],torch.tensor(state['linear'].T))
    assert mapped['bn.num_batches_tracked'].item()==0
    with pytest.raises(ValueError,match='unmapped'):map_paddle_state(dict(state,encoder_unmapped=np.ones(2)),mapping,expected)
    with pytest.raises(ValueError,match='shape'):map_paddle_state(state,mapping,{'head.weight':torch.zeros(1)})

@pytest.mark.parametrize('size,target',[( (2,2),320),((601,48),601),((1001,100),480)])
def test_paddle_dynamic_pad_rule(size,target):
    image=Image.new('RGB',size,(255,0,0))
    result=preprocess(image,dict(color='BGR',height=48,interpolation='linear',pad_width=320,
       pad_rule='paddle_dynamic',mean=[.5]*3,std=[.5]*3))
    assert result.shape==(1,3,48,target) and result.dtype==torch.float32
    assert result[0,0,0,0]==-1 and result[0,2,0,0]==1
    width=min(int(np.ceil(48*size[0]/size[1])),target)
    if width<target:assert torch.count_nonzero(result[...,width:])==0


def test_native_fixed_padding_and_bad_color():
    image=Image.new('RGB',(2,2),(255,0,0))
    result=preprocess(image,dict(color='RGB',height=2,interpolation='linear',pad_width=4))
    assert result.shape==(1,3,2,4) and result[0,0,0,0]==1
    with pytest.raises(ValueError,match='color'):preprocess(image,dict(color='invalid'))
    with pytest.raises(ValueError,match='narrower'):preprocess(image,dict(color='RGB',height=2,interpolation='linear',pad_width=1))


def test_scale_normalised_parity_keeps_raw_errors_and_greedy():
    native={k:np.array([[[0,64,1]]],dtype=np.float32) for k in ('backbone','neck','logits')}
    converted={k:v+np.float32(.00029) for k,v in native.items()}
    receipt=compare_endpoints(native,converted)
    assert receipt['logits']['max_abs']>1e-4 and receipt['logits']['max_abs_over_ref_max']<1e-4
    converted['neck']=converted['neck']+.01
    with pytest.raises(ValueError,match='tolerance'):compare_endpoints(native,converted)
    swapped={k:v.copy() for k,v in native.items()};swapped['logits']=np.array([[[0,1,64]]],dtype=np.float32)
    with pytest.raises(ValueError):compare_endpoints(native,swapped)

@pytest.mark.parametrize('bad',['shape','nonfinite','greedy'])
def test_parity_adversarial_inputs(bad):
    native={k:np.array([[[0,1,1]]],np.float32) for k in ('backbone','neck','logits')}
    actual=copy.deepcopy(native)
    if bad=='shape':actual['backbone']=np.zeros((1,2,3),np.float32)
    if bad=='nonfinite':actual['neck'][0,0,0]=np.nan
    if bad=='greedy':actual['logits'][0,0,2]+=np.float32(1e-6)
    with pytest.raises(ValueError):compare_endpoints(native,actual)


def test_parity_refuses_wrong_case_count_before_model_load(tmp_path):
    crops=tmp_path/'crops.jsonl';crops.write_text('{}\n')
    with pytest.raises(ValueError,match='100'):qualify_parity({},'unused',crops,tmp_path/'parity')
    assert not (tmp_path/'parity').exists()


def test_preprocessing_qualification_independent_source(tmp_path):
    from greekocr._vendor.bench.e2_parity import preprocessing_check
    source=tmp_path/'native_source.py';source.write_text('recorded upstream fixture')
    from greekocr.ops import file_sha256
    crop=tmp_path/'crop.png';Image.new('RGB',(8,8),255).save(crop)
    contract=dict(color='RGB',height=8,interpolation='linear')
    rows=[]
    for i in range(20):
        unique=tmp_path/f'crop-{i}.png';Image.new('RGB',(8,8),255).save(unique)
        rows.append(dict(crop_path=str(unique),parity_kind=('short','very_long','blank','padded')[i%4]))
    native=SimpleNamespace(binding=dict(preprocessing_source=str(source),preprocessing_source_sha256=file_sha256(source)),
      preprocess=lambda p:preprocess(Image.open(p),contract).numpy())
    out=tmp_path/'preprocess';out.mkdir()
    receipt=preprocessing_check(native,rows,dict(preprocess=contract),out)
    assert receipt['passed'] and receipt['crops']==20 and len(receipt['checks'])==20
    native.preprocess=lambda p:np.zeros((1,3,8,8),dtype=np.float32)
    with pytest.raises(ValueError,match='tolerance'):preprocessing_check(native,rows,dict(preprocess=contract),out)


def test_ours_real_cpu_loader_and_raw_decoder(tmp_path):
    from greekocr._vendor.train.model import build_model
    from greekocr._vendor.train.cer import load_codec
    codec_path=Path(__file__).resolve().parents[1]/'greekocr/_vendor/codec/v1.json'
    codec=load_codec(str(codec_path));model,_=build_model(n_classes=codec.n_classes,verbose=False)
    checkpoint=tmp_path/'weights.pt';torch.save(dict(model=model.state_dict(),arch='compact',head='nfd',
       codec_version='v1',n_classes=codec.n_classes),checkpoint)
    crop=tmp_path/'line.png';Image.new('L',(64,48),255).save(crop)
    reader=load_ours(checkpoint,codec_path)
    assert isinstance(reader.read(crop),str) and reader.rec.device=='cpu'
    batch=reader.preprocess(crop)
    assert batch['images'].shape[-1]>=64+128 and batch['images'].dtype==torch.float32
    assert reader.binding['decoder'].startswith('train.cer.greedy_decode_line')


def test_kalchas_missing_runtime_and_checksum_guards(tmp_path,monkeypatch):
    from greekocr._vendor.bench.e2_teachers import Kalchas
    def load(self,spec):raise ModuleNotFoundError('fixture missing',name='scipy')
    monkeypatch.setattr(Kalchas,'_load',load)
    with pytest.raises(Unavailable,match='scipy'):load_kalchas({})
    checkpoint=tmp_path/'wrong.safetensors';checkpoint.write_bytes(b'fixture')
    with pytest.raises(ValueError,match='filename'):load_cllg(dict(checkpoint=checkpoint,readme=tmp_path/'README'))

@pytest.mark.parametrize('name',['google','azure','mistral'])
def test_service_stub_never_implicitly_runs(name,monkeypatch):
    from greekocr._vendor.bench.e2_teachers import SERVICE_ENV
    for key in SERVICE_ENV[name]:monkeypatch.delenv(key,raising=False)
    with pytest.raises(Unavailable,match='service absent'):load_service(name,{})
    with pytest.raises(Unavailable,match='absent credential'):load_service(name,{},enabled=True)
    for key in SERVICE_ENV[name]:monkeypatch.setenv(key,'fixture-secret')
    with pytest.raises(Unavailable,match='explicit service'):load_service(name,{},enabled=True)


def test_public_native_framework_loaders_forward_exact_specs(monkeypatch):
    from greekocr._vendor.bench import e2_native as native
    spec={'checkpoint':'local-only'};marker=object()
    monkeypatch.setattr(native,'r01_paddle',lambda s:marker if s is spec else None)
    monkeypatch.setattr(native,'r03_openocr',lambda s:marker if s is spec else None)
    assert load_paddle_r01(spec) is marker and load_r03(spec) is marker


def test_cllg_public_worker_keeps_pinned_binding(tmp_path,monkeypatch):
    from greekocr._vendor.bench import e2_native as native
    marker=object();seen=[]
    def load(*args,**kwargs):seen.append((args,kwargs));return marker
    monkeypatch.setattr(native,'cllg_kraken',load)
    assert load_cllg_worker('checkpoint',{'reviewed':True},python='/venv/python',timeout=8) is marker
    assert seen[0][1]==dict(python='/venv/python',timeout=8)

@pytest.mark.parametrize('family',['R01','R03'])
def test_real_cpu_converter_retains_layers_and_binds_init(tmp_path,family):
    from greekocr._vendor.bench.e2_models import build_donor
    if family=='R03':
        from greekocr._vendor.rec.svtrv2_model import VARIANTS
        encoder=copy.deepcopy(VARIANTS['small']);encoder['dims']=[64,128,256];encoder['num_heads']=[2,4,8]
        config={'encoder':encoder}
    else:
        from transformers import PPOCRV5MobileRecConfig
        config=PPOCRV5MobileRecConfig().to_dict()
    native=build_donor(family,config,95)
    if family=='R03':
        state={('decoder.ctc_decoder.'+k[len('decoder.'):] if k.startswith('decoder.') else k):v.clone()
               for k,v in native.state_dict().items()}
        state['decoder.gtc_decoder.fixture']=torch.ones(1)
    else:state={k.removeprefix('native.'):v.clone() for k,v in native.state_dict().items()}
    source=tmp_path/'upstream.pt';torch.save({'state_dict':state},source)
    cfg=tmp_path/'config.json';cfg.write_text(json.dumps(config))
    codec=Path(__file__).resolve().parents[1]/'greekocr/_vendor/codec/v1.json'
    provenance=convert_donor(family,source,cfg,tmp_path/'converted','fixture-pinned-revision',codec=codec)
    checkpoint=verify_init(tmp_path/'converted/donor_init.pt')
    assert checkpoint['n_classes']==248 and checkpoint['state_hash_version']==2
    original=torch.load(tmp_path/'converted/native_before_swap.pt',map_location='cpu',weights_only=True)
    head='decoder.fc' if family=='R03' else 'native.head.head'
    for key,value in original['model'].items():
        if not key.startswith(head+'.'):assert torch.equal(value,checkpoint['model'][key])
    assert checkpoint['model'][head+'.weight'].shape[0]==248
    assert provenance['parity_status'].startswith('node-only')
    checkpoint['model'][head+'.bias'][0]+=1
    tampered=tmp_path/'tampered.pt';torch.save(checkpoint,tampered)
    with pytest.raises(ValueError,match='digest'):verify_init(tampered)
    with pytest.raises(ValueError,match='immutable'):convert_donor(family,source,cfg,tmp_path/'bad','main',codec=codec)


def test_kalchas_mps_cpu_mapping_and_process_state_restored(tmp_path,monkeypatch):
    import socket,types,os
    from greekocr._vendor.bench.e2_teachers import KALCHAS_REV
    root=tmp_path/'checkout';folder=root/'kalchas/checkpoints/Kalchas';folder.mkdir(parents=True)
    checkpoint=folder/'model9_best_loss_1.35.pt';artifacts=folder/'model9_best_loss_1.35_artifacts.pt'
    torch.save(torch.nn.Linear(2,2).state_dict(),checkpoint);torch.save({'codec':'fixture'},artifacts)
    code=root/'kalchas/ocr.py'
    code.write_text('''import torch
class Native:
    def __init__(self,state):
        self.network=torch.nn.Linear(2,2)
        self.network.load_state_dict(state)
    def ocr(self,images):return ['ά' for image in images]
def load_ocr_model(name,device='cpu'):
    if fail:raise RuntimeError('recorded native failure')
    state=torch.load('kalchas/checkpoints/Kalchas/model9_best_loss_1.35.pt')
    return Native(state)
''')
    package=types.ModuleType('kalchas');package.__path__=[str(root/'kalchas')]
    module=types.ModuleType('kalchas.ocr');module.__file__=str(code)
    exec(compile(code.read_text(),str(code),'exec'),module.__dict__);module.fail=False
    monkeypatch.setitem(sys.modules,'kalchas',package);monkeypatch.setitem(sys.modules,'kalchas.ocr',module)
    monkeypatch.setattr(sys,'path',sys.path.copy())
    def output(command,**kwargs):
        assert kwargs['env']['GIT_OPTIONAL_LOCKS']=='0'
        return KALCHAS_REV+'\n' if 'rev-parse' in command else ''
    monkeypatch.setattr(subprocess,'check_output',output)
    original_load=torch.load;calls=[]
    def record_load(*args,**kwargs):calls.append(kwargs);return original_load(*args,**kwargs)
    monkeypatch.setattr(torch,'load',record_load)
    connect=socket.socket.connect;cwd=Path.cwd()
    spec=dict(checkout=str(root),checkpoint=str(checkpoint),model_name='Kalchas')
    reader=load_kalchas(spec)
    assert calls[0]['map_location']=='cpu' and reader.binding['native_state_equals_released_checkpoint']
    assert torch.load is record_load and socket.socket.connect is connect and Path.cwd()==cwd
    crop=tmp_path/'crop.png';Image.new('L',(64,48),255).save(crop)
    assert reader.read(crop)=='α\u0301' and 'MPS' in reader.load_disclosure
    module.fail=True
    with pytest.raises(RuntimeError,match='recorded native failure'):load_kalchas(spec)
    assert torch.load is record_load and socket.socket.connect is connect and Path.cwd()==cwd


def test_cllg_contract_readme_evidence_and_drift(tmp_path,monkeypatch):
    from greekocr._vendor.bench import e2_native as native
    from greekocr._vendor.bench.e2_teachers import cllg_contract
    from greekocr.ops import file_sha256
    readme=tmp_path/'README.md';readme.write_text('''---
software_name: kraken
software_hints: [kraken 7.1]
script: [Grek, Latn]
metrics: {CER: 4.54}
license: CC-BY-4.0
base_model: [https://doi.org/10.5281/zenodo.10592716]
model_type: [recognition]
---
Reduced schema fixture, not the publisher MD5-pinned README.
''')
    checkpoint=tmp_path/'fixture';checkpoint.write_bytes(b'fixture')
    binding=dict(class_order=[dict(text='α',labels=[1])],preprocess=dict(factory='kraken.lib.dataset:ImageInputTransforms',
      source_sha256='fixture',kraken_version='7.1.1'),checkpoint_sha256=file_sha256(checkpoint))
    monkeypatch.setattr(native,'cllg_kraken',lambda *a:SimpleNamespace(binding=binding))
    out=tmp_path/'contract.json';contract=build_cllg_contract(readme,checkpoint,out)
    assert cllg_contract(readme,out)==contract and contract['reviewed'] and contract['backend']=='kraken-native'
    contract['facts']['licence']='invented';out.write_text(json.dumps(contract))
    with pytest.raises(Unavailable,match='licence'):cllg_contract(readme,out)
