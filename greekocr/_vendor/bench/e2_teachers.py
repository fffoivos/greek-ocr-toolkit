"""Local, byte-bound crop readers. No fetching; credentials are never serialized."""
from __future__ import annotations
import hashlib
import importlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import socket
import sys
import unicodedata as ud
from PIL import Image
from greekocr._vendor.bench.common import sha256

KALCHAS_REV = '7a0f9fddcfb14276bc48850abcc6706170583eb9'
KALCHAS_RUNTIME = ('numpy', 'torch', 'torchvision', 'Pillow', 'scipy')
SERVICE_ENV = {
    'google': ('GOOGLE_APPLICATION_CREDENTIALS', 'GOOGLE_CLOUD_PROJECT', 'DOCUMENTAI_PROCESSOR_ID', 'DOCUMENTAI_LOCATION'),
    'azure': ('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT', 'AZURE_DOCUMENT_INTELLIGENCE_KEY'),
    'mistral': ('MISTRAL_API_KEY',),
}


class Unavailable(ValueError): pass


def hook(spec, *args):
    module, func = spec.rsplit(':', 1)
    mod = importlib.import_module(module)
    return getattr(mod, func)(*args), dict(adapter=spec, adapter_sha256=sha256(mod.__file__))


def validate_files(spec):
    for path, digest in spec.get('files', {}).items():
        if sha256(path) != digest: raise ValueError('teacher input changed: '+path)


class Kalchas:
    def __init__(self, spec):
        try: self._load(spec)
        except ModuleNotFoundError as error:
            raise Unavailable(f'Kalchas missing runtime module {error.name!r}; '
                f'stage offline dependencies: {", ".join(KALCHAS_RUNTIME)} '
                '(torchvision must match torch; Pillow imports as PIL)') from error

    def _load(self, spec):
        root = Path(spec['checkout']).resolve()
        git_env = dict(os.environ,GIT_OPTIONAL_LOCKS='0')
        rev = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True,env=git_env).strip()
        if rev != KALCHAS_REV: raise ValueError('Kalchas must use pinned 7a0f9fdd checkout')
        dirty = subprocess.check_output(['git', '-C', str(root), 'diff', '--name-only', 'HEAD'], text=True,env=git_env)
        if dirty.strip(): raise ValueError('Kalchas tracked inference code has edits')
        checkpoint = Path(spec['checkpoint']).resolve()
        if not checkpoint.is_relative_to(root): raise ValueError('stage released weights in the native checkout')
        model_name = spec.get('model_name', 'Kalchas')
        released = {'Kalchas':'kalchas/checkpoints/Kalchas/model9_best_loss_1.35.pt',
                    'Polyton-DB':'kalchas/checkpoints/Polyton-DB/99_model_best_loss_1.184.pt'}
        if model_name not in released or checkpoint != root/released[model_name]:
            raise ValueError('Kalchas registry model/checkpoint mismatch')
        artifacts = checkpoint.with_name(checkpoint.stem+'_artifacts.pt')
        for path in (checkpoint, artifacts):
            if not path.is_file(): raise Unavailable('stage Kalchas released weights AND codec artifacts: '+str(path))
        sys.path.insert(0, str(root))
        from kalchas.ocr import load_ocr_model
        if not Path(inspect.getfile(load_ocr_model)).resolve().is_relative_to(root):
            raise ValueError('Kalchas import escaped pinned checkout')
        # Native registry name and CPU device, per the pinned installed API.
        kwargs = dict(spec.get('load_kwargs', {}))
        # 8 Oct 2026 (coordinator, disclosed): 'cuda' is allowed when the config asks for it (the Vouli
        # adjudication over 51k lines ran at 123 lines/min with Kalchas on CPU). The device is part of the
        # recorded binding (load_kwargs), and the bake-off ms/line column then reports that device's timing.
        if kwargs.get('device','cpu') not in ('cpu','cuda'): raise ValueError('Kalchas device must be cpu or cuda')
        kwargs['device'] = kwargs.get('device','cpu')
        inspect.signature(load_ocr_model).bind(model_name, **kwargs)
        # The released API can expose only a registry name. Verify its actual
        # tensors against the specified released bytes, rather than trusting name.
        original_connect = socket.socket.connect
        def offline(*args, **kw): raise Unavailable('Kalchas attempted network acquisition; stage native checkpoint locally')
        socket.socket.connect = offline
        # This release's registry opens weights/artifacts relative to cwd.
        # Use its native loader unchanged, and always restore process state.
        previous_cwd = Path.cwd()
        import torch, functools
        _torch_load = torch.load
        # Kalchas's checkpoints were saved on an Apple MPS device; its loader calls torch.load without
        # map_location, which fails on Linux. Force CPU mapping during the native load only (disclosed).
        torch.load = functools.partial(_torch_load, map_location='cpu')
        try:
            os.chdir(root)
            self.model = load_ocr_model(model_name, **kwargs)
        finally:
            torch.load = _torch_load
            os.chdir(previous_cwd)
            socket.socket.connect = original_connect
        self.load_disclosure = 'torch.load map_location=cpu forced during native load (MPS-saved checkpoints)'
        import torch
        raw = torch.load(checkpoint, map_location='cpu', weights_only=True)
        state = raw.get('state_dict', raw.get('model_state_dict', raw.get('model', raw)))
        if not isinstance(state, dict) or not all(torch.is_tensor(v) for v in state.values()):
            raise Unavailable('Kalchas released checkpoint needs reviewed native state extraction')
        state = {k.removeprefix('module.'):v for k,v in state.items()}
        modules = [self.model, *vars(self.model).values()]
        matched = False
        for module in modules:
            if isinstance(module, torch.nn.Module):
                loaded = {k.removeprefix('module.'):v for k,v in module.state_dict().items()}
                if loaded.keys() == state.keys() and all(torch.equal(v.cpu(),state[k].cpu()) for k,v in loaded.items()):
                    matched = True; break
        if not matched: raise ValueError('Kalchas native reader did not load specified released tensors')
        self.binding = dict(revision=rev, licence='Apache-2.0', checkpoint_sha256=sha256(checkpoint),
            artifacts_sha256=sha256(artifacts), model_name=model_name,
            gold_overlap_risk=model_name=='Polyton-DB', runtime_dependencies=list(KALCHAS_RUNTIME),
            native_loader_sha256=sha256(inspect.getfile(load_ocr_model)), load_kwargs=kwargs,
            native_state_equals_released_checkpoint=True,
            preprocessing='native Kalchas .ocr([PIL grayscale line]); native code pinned')

    def read(self, path):
        with Image.open(path) as image: result = self.model.ocr([image.convert('L')])
        if len(result) != 1 or not isinstance(result[0], str): raise ValueError('Kalchas output contract')
        return ud.normalize('NFD', result[0])


def cllg_contract(readme, contract_path):
    """README establishes software facts; the loaded model establishes its codec/transform."""
    from greekocr._vendor.bench.e2_cllg_contract import readme_facts
    text = Path(readme).read_text(encoding='utf-8')
    contract = json.loads(Path(contract_path).read_text())
    if contract.get('readme_sha256') != sha256(readme) or contract.get('reviewed') is not True:
        raise Unavailable('CLLG preprocessing contract must be reviewed against README')
    try: facts, excerpts = readme_facts(readme)
    except ValueError as error: raise Unavailable(str(error)) from error
    for fact, expected in facts.items():
        quoted = contract.get('readme_evidence',{}).get(fact)
        quotes = quoted if isinstance(quoted,list) else [quoted]
        if (fact not in contract.get('established',[]) or contract.get('facts',{}).get(fact)!=expected
                or quoted!=excerpts[fact] or not all(isinstance(q,str) and q.strip() and q in text for q in quotes)):
            raise Unavailable('CLLG README does not establish '+fact+'; regenerate readme_contract.json')
    if contract.get('backend')!='kraken-native' or contract.get('factory')!='greekocr._vendor.bench.e2_native:cllg_kraken':
        raise Unavailable('CLLG README establishes Kraken 7.1; require kraken-native backend and bench.e2_native:cllg_kraken')
    if not isinstance(contract.get('class_order'),list) or not contract['class_order']:
        raise Unavailable('CLLG loaded model codec ordering is absent')
    prep = contract.get('preprocess',{})
    if prep.get('factory')!='kraken.lib.dataset:ImageInputTransforms' or not prep.get('source_sha256'):
        raise Unavailable('CLLG native Kraken line transform contract is absent')
    return contract


class CLLG:
    """Released recognition model; README facts plus model-derived Kraken contract."""
    def __init__(self, spec):
        checkpoint, readme = Path(spec['checkpoint']), Path(spec['readme'])
        if checkpoint.name != 'ppocr_v6_tau090.safetensors': raise ValueError('CLLG weight filename mismatch')
        if hashlib.md5(readme.read_bytes()).hexdigest() != '046be7d582b1435bf027227b78651198':
            raise ValueError('need the published Zenodo 22232579 README (MD5 receipt)')
        if hashlib.md5(checkpoint.read_bytes()).hexdigest() != '2b59c47ba44a58ca7200d6f0e51676dd':
            raise ValueError('CLLG publisher checksum mismatch')
        contract = cllg_contract(readme, spec['contract'])
        try: self.native, bound = hook(contract['factory'], str(checkpoint), contract)
        except ModuleNotFoundError as error:
            raise Unavailable(f'CLLG kraken-native missing runtime module {error.name!r}; stage Kraken 7.1 dependencies offline') from error
        if self.native.binding.get('checkpoint_sha256') != sha256(checkpoint):
            raise ValueError('native CLLG reader must bind actually loaded checkpoint')
        self.binding = dict(licence='CC-BY-4.0', doi='10.5281/zenodo.22232579',
            checkpoint_sha256=sha256(checkpoint), readme_sha256=sha256(readme),
            contract_sha256=sha256(spec['contract']), preprocessing=contract,
            native=self.native.binding, **bound)

    def read(self, path): return ud.normalize('NFD', self.native.read(path))


class Service:
    def __init__(self, name, spec):
        missing = [key for key in SERVICE_ENV[name] if not os.environ.get(key)]
        if missing: raise Unavailable('no-op: absent credential/config env '+', '.join(missing))
        if not spec.get('factory'):
            raise Unavailable('credentials present; supply explicit service module:factory hook')
        self.reader, bound = hook(spec['factory'], name)
        self.binding = dict(service=name, credential_env=list(SERVICE_ENV[name]), **bound,
                            latency_kind='remote wall; CPU ms/line NA')

    def read(self, path): return ud.normalize('NFD', self.reader(Path(path)))


def reader(spec, codec='codec/v1.json', *, service=False):
    validate_files(spec)
    kind = spec['kind']
    if kind == 'e1':
        from greekocr._vendor.bench.e2_reader_parity import E1Reader
        import torch
        from greekocr._vendor.train import train as trainer
        trainer._runtime()
        checkpoint=Path(spec['checkpoint'])
        state=torch.load(checkpoint,map_location='cpu',weights_only=False)
        if state.get('state_hash_version') != 2 or state.get('state_sha256') != trainer.checkpoint_state_sha256(state):
            raise ValueError('retrained teacher checkpoint state digest mismatch')
        engine=E1Reader(checkpoint,codec,'cpu')
        loaded=engine.rec.model.state_dict();expected=state['model']
        if loaded.keys()!=expected.keys() or any(loaded[k].dtype!=v.dtype or not torch.equal(loaded[k].cpu(),v.cpu()) for k,v in expected.items()):
            raise ValueError('actually loaded E1 weights differ from retrained checkpoint')
        sibling=checkpoint.with_suffix('.safetensors')
        engine.binding.update(loaded_weights_sha256=sha256(sibling if sibling.exists() else checkpoint),
                              checkpoint_state_sha256=state['state_sha256'],loaded_state_equals_checkpoint=True)
        return engine
    if kind == 'kalchas': return Kalchas(spec)
    if kind == 'cllg': return CLLG(spec)
    if kind == 'service':
        if not service: raise Unavailable('no-op: --service absent')
        return Service(spec['service'], spec)
    raise ValueError('unknown teacher kind: '+kind)
