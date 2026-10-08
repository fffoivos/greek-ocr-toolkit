"""Node-only original-framework references. Native checkouts/weights are local.

Each exposes an independent upstream image preprocessing path, followed by
endpoints on FP32 tensors. The harness checks preprocessing before logits.
"""
from __future__ import annotations
import atexit
import inspect
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import tempfile
import threading
import time
import weakref
from greekocr._vendor.bench.common import sha256


def kraken_codec_order(codec):
    """Preserve Kraken's multi-codepoint/multi-label codec, in label order."""
    mapping = getattr(codec,'c2l',None)
    if not isinstance(mapping,dict) or not mapping:
        raise ValueError('loaded Kraken model has no c2l codec mapping')
    entries = [dict(text=text,labels=list(labels)) for text,labels in mapping.items()]
    if any(not isinstance(e['text'],str) or not e['labels']
           or any(not isinstance(i,int) or i<0 for i in e['labels']) for e in entries):
        raise ValueError('invalid loaded Kraken codec')
    return sorted(entries,key=lambda e:(e['labels'],e['text']))


def cllg_kraken(checkpoint, contract=None, *, python=None, timeout=300):
    """Run pinned Kraken in ~/venvs/cllg, isolated from the benchmark runtime.

    The worker loads the safetensors container with kraken.models, describes
    its actual codec/transforms, and serves JSON batches with one loaded model.
    last_batch_ms measures a successful request after worker readiness, excluding
    process/model startup (including IPC and crop preprocessing/inference).
    """
    checkpoint = Path(checkpoint).expanduser().resolve()
    # absolute(), not resolve(): resolving the venv's python symlink escapes to the base interpreter (no torch)
    interpreter = Path(python or os.environ.get('CLLG_PYTHON', '~/venvs/cllg/bin/python')).expanduser().absolute()
    worker = Path(__file__).resolve().parents[1] / 'scripts/fetch/r2_cllg_worker.py'
    checkpoint_hash = sha256(checkpoint)
    command = [str(interpreter), '-I', str(worker), '--checkpoint', str(checkpoint),
               '--checkpoint-sha256', checkpoint_hash]

    def invoke(paths, *, describe=False):
        args = command + (['--describe'] if describe else [])
        try:
            result = subprocess.run(args, input=json.dumps(paths, ensure_ascii=False),
                                    text=True, encoding='utf-8', capture_output=True,
                                    check=True, timeout=timeout)
        except FileNotFoundError as error:
            raise ModuleNotFoundError(
                'CLLG venv Python is absent; run scripts/fetch/r2_cllg_env.sh on the Linux node '
                'or set CLLG_PYTHON: '+str(interpreter), name='cllg_venv') from error
        except subprocess.CalledProcessError as error:
            raise ValueError('CLLG Kraken worker failed: '+(error.stderr or str(error))[-4000:]) from error
        except subprocess.TimeoutExpired as error:
            raise RuntimeError(f'CLLG Kraken worker exceeded {timeout}s') from error
        try: return json.loads(result.stdout)
        except json.JSONDecodeError as error:
            raise ValueError('CLLG Kraken worker returned invalid JSON') from error

    binding = invoke([], describe=True)
    prep = binding.get('preprocess') if isinstance(binding, dict) else None
    if (not isinstance(binding, dict) or binding.get('checkpoint_sha256') != checkpoint_hash
            or not isinstance(binding.get('class_order'), list) or not binding['class_order']
            or not isinstance(prep, dict) or prep.get('kraken_version') != '7.1.1'
            or prep.get('factory') != 'kraken.lib.dataset:ImageInputTransforms'):
        raise ValueError('CLLG Kraken worker returned an invalid model binding')
    binding['worker_sha256'] = sha256(worker)
    if contract is not None:
        for key in ('checkpoint_sha256','class_order','preprocess'):
            if contract.get(key)!=binding[key]: raise ValueError('CLLG loaded model/transform contract changed: '+key)
    class Native:
        def __init__(self):
            self.binding = binding
            self.last_batch_ms = None
            self._process = None
            self._stderr = None
            self._reader = None
            self._responses = None

        def _start(self):
            # A file keeps upstream diagnostics from filling a stderr pipe.
            self._stderr = tempfile.TemporaryFile()
            try:
                process = subprocess.Popen(command + ['--serve'], stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=self._stderr, text=True,
                    encoding='utf-8', bufsize=1)
            except FileNotFoundError as error:
                self._stderr.close()
                self._stderr = None
                raise ModuleNotFoundError(
                    'CLLG venv Python is absent; run scripts/fetch/r2_cllg_env.sh on the Linux node '
                    'or set CLLG_PYTHON: '+str(interpreter), name='cllg_venv') from error
            except Exception:
                self._stderr.close()
                self._stderr = None
                raise
            self._process = process
            # weak reference: a strong atexit reference would keep the reader alive (destructor test).
            atexit.register(lambda ref=weakref.ref(self): (ref() and ref().close()))
            responses = self._responses = queue.Queue()

            def receive():
                try:
                    for line in process.stdout:
                        responses.put(line)
                finally:
                    responses.put('')

            # Capture only process/queue, so this thread cannot retain Native.
            self._reader = threading.Thread(target=receive, daemon=True)
            self._reader.start()
            # Wait for model load before timing even the first real batch.
            self._exchange([])

        def _exchange(self, paths):
            self._process.stdin.write(json.dumps(paths, ensure_ascii=False) + '\n')
            self._process.stdin.flush()
            try:
                line = self._responses.get(timeout=timeout)
            except queue.Empty as error:
                raise RuntimeError(f'CLLG Kraken worker exceeded {timeout}s') from error
            if not line:
                raise BrokenPipeError('CLLG Kraken worker closed stdout')
            try:
                result = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError('CLLG Kraken worker returned invalid JSON') from error
            if isinstance(result, dict) and 'error' in result:
                raise ValueError('CLLG Kraken worker failed: '+str(result['error']))
            if (not isinstance(result, list) or len(result) != len(paths)
                    or any(not isinstance(text, str) for text in result)):
                raise ValueError('CLLG Kraken worker must return one string per crop')
            return result

        def _diagnostics(self):
            self._stderr.seek(0, os.SEEK_END)
            self._stderr.seek(max(0, self._stderr.tell() - 4000))
            return self._stderr.read().decode('utf-8', errors='replace')

        def read_batch(self, paths):
            self.last_batch_ms = None
            paths = [str(Path(path).expanduser().resolve()) for path in paths]
            if not paths:
                self.last_batch_ms = 0.0
                return []
            for attempt in range(2):
                try:
                    if self._process is None:
                        self._start()
                    start = time.perf_counter()
                    result = self._exchange(paths)
                except BrokenPipeError as error:
                    detail = self._diagnostics()
                    self.close()
                    if attempt:
                        raise RuntimeError('CLLG Kraken worker pipe broke after restart: '+
                                           (detail or str(error))) from error
                except RuntimeError:
                    # A late response must not become the next batch's result.
                    self.close()
                    raise
                else:
                    self.last_batch_ms = (time.perf_counter() - start) * 1000
                    return result

        def read(self,path): return self.read_batch([path])[0]

        def close(self):
            process, self._process = self._process, None
            if process is None:
                return
            try:
                try:
                    process.stdin.close()
                except BrokenPipeError:
                    pass
                try:
                    process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    process.terminate()
                    try:
                        process.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
            finally:
                self._reader.join(timeout=1)
                process.stdout.close()
                self._stderr.close()
                self._stderr = None
                self._reader = None
                self._responses = None

        def __del__(self):
            # At interpreter shutdown the reader thread's buffered pipe may be locked (daemon thread);
            # closing then aborts the process. atexit (registered in _start) handles the orderly case.
            if sys.is_finalizing():
                return
            try:
                self.close()
            except Exception:
                pass
    return Native()


def native_checkout(spec):
    root=Path(spec['native_checkout']).resolve()
    git_env = dict(os.environ,GIT_OPTIONAL_LOCKS='0')
    revision=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True,env=git_env).strip()
    if revision!=spec['native_revision'] or len(revision)!=40:raise ValueError('native inference revision mismatch')
    if subprocess.check_output(['git','-C',str(root),'diff','--name-only','HEAD'],text=True,env=git_env).strip():
        raise ValueError('native inference checkout has edits')
    # PaddleOCR and OpenOCR both publish a top-level `tools` package. The
    # sequential R01/R03 parity stages must import the selected checkout's copy.
    for name,module in list(sys.modules.items()):
        if name=='tools' or name.startswith('tools.'):
            source=getattr(module,'__file__',None)
            locations=getattr(module,'__path__',[]) or []
            origins=[Path(source).resolve()] if source else [Path(p).resolve() for p in locations]
            if any(not p.is_relative_to(root) for p in origins):del sys.modules[name]
    sys.path.insert(0,str(root));return root


def yaml_config(path):
    import yaml
    return yaml.safe_load(Path(path).read_text())


def r01_preprocessor(spec, root):
    """Call the pinned Paddle predictor itself, using reviewed predictor options."""
    import cv2
    import numpy as np
    from tools.infer.predict_rec import TextRecognizer
    source=Path(inspect.getfile(TextRecognizer)).resolve()
    if not source.is_relative_to(root):raise ValueError('Paddle preprocessing import escaped checkout')
    options=spec.get('native_preprocess',{})
    if options.get('reviewed') is not True or not options.get('rec_image_shape'):
        raise ValueError('review actual Paddle predictor rec_image_shape/dynamic-width options on node')
    # Avoid predictor construction (which can load/download inference weights).
    predictor=TextRecognizer.__new__(TextRecognizer)
    predictor.rec_image_shape=options['rec_image_shape']
    predictor.rec_algorithm='SVTR_LCNet';predictor.use_onnx=False
    def transform(path):
        image=cv2.imread(str(path),cv2.IMREAD_COLOR)
        if image is None:raise ValueError('native Paddle image decode failed')
        ratio=max(predictor.rec_image_shape[2]/predictor.rec_image_shape[1], image.shape[1]/image.shape[0])
        return np.asarray(predictor.resize_norm_img(image,ratio),dtype=np.float32)[None]
    return transform,source


def r03_preprocessor(spec, root):
    """Use OpenOCR's own evaluation ratio-resize method without opening LMDB."""
    import numpy as np
    from PIL import Image
    from torchvision import transforms as T
    from tools.data.ratio_dataset_tvresize import RatioDataSetTVResize
    source=Path(inspect.getfile(RatioDataSetTVResize)).resolve()
    if not source.is_relative_to(root):raise ValueError('OpenOCR preprocessing import escaped checkout')
    cfg=yaml_config(spec['native_config'])['Eval'];dataset=cfg['dataset'];loader=cfg['loader']
    decode=[op['DecodeImagePIL'] for op in dataset.get('transforms',[]) if 'DecodeImagePIL' in op]
    if (dataset['name']!='RatioDataSetTVResize' or dataset.get('padding',True)
            or dataset.get('padding_rand',False) or dataset.get('padding_doub',False)
            or len(decode)!=1 or (decode[0] or {}).get('img_mode','RGB')!='RGB'):
        raise ValueError('qualify deterministic native OpenOCR Eval RatioDataSetTVResize with padding disabled')
    instance=RatioDataSetTVResize.__new__(RatioDataSetTVResize)
    instance.padding_rand=False;instance.padding_doub=False;instance.error=0
    instance.base_shape=dataset.get('base_shape',[[64,64],[96,48],[112,40],[128,32]])
    instance.base_h=dataset.get('base_h',32);instance.interpolation=T.InterpolationMode.BICUBIC
    instance.transforms=T.Compose([T.ToTensor(),T.Normalize(.5,.5)])
    def transform(path):
        with Image.open(path) as im:
            image=im.convert('RGB')
            ratio=int(np.clip(np.around(image.width/image.height),loader.get('min_ratio',1),loader.get('max_ratio',10)))
            result=instance.resize_norm_img({'image':image},ratio,padding=False)
        if result is None:raise ValueError('native OpenOCR preprocessing rejected crop')
        return result['image'][None]
    return transform,source


def r03_openocr(spec):
    import torch
    root=native_checkout(spec)
    from openrec.modeling import build_model
    if not Path(inspect.getfile(build_model)).resolve().is_relative_to(root):raise ValueError('OpenOCR import escaped native checkout')
    cfg=yaml_config(spec['native_config'])['Architecture']
    # Explicit CTC inference: keep SMTR weights for strict native restoration,
    # call the native CTC decoder directly, never the config's infer_gtc path.
    model=build_model(cfg)
    raw=torch.load(spec['checkpoint'],map_location='cpu',weights_only=True)
    state=raw.get('state_dict',raw.get('model',raw))
    state={k.removeprefix('module.'):v for k,v in state.items()}
    model.load_state_dict(state,strict=True);model.float().eval().cpu()
    decoder=model.decoder.ctc_decoder
    transform,prep_source=r03_preprocessor(spec,root)
    class Native:
        binding=dict(checkpoint_sha256=sha256(spec['checkpoint']),revision=spec['native_revision'],
                     config_sha256=sha256(spec['native_config']),loader_sha256=sha256(inspect.getfile(build_model)),
                     preprocessing_source=str(prep_source),preprocessing_source_sha256=sha256(prep_source))
        def preprocess(self,path):return transform(path)
        def endpoints(self,x):
            backbone=model.encoder(x);captured={}
            handle=decoder.fc.register_forward_hook(lambda m,a,b:captured.update(neck=a[0],logits=b))
            try:decoder(backbone)
            finally:handle.remove()
            return dict(backbone=backbone,**captured)
    return Native()


def r01_paddle(spec):
    import paddle
    paddle.set_device('cpu')
    root=native_checkout(spec)
    from ppocr.modeling.architectures import build_model
    if not Path(inspect.getfile(build_model)).resolve().is_relative_to(root):raise ValueError('Paddle import escaped native checkout')
    full=yaml_config(spec['native_config']); cfg=full['Architecture']
    if cfg.get('Head',{}).get('name')=='MultiHead':
        # Upstream rule (tools/eval.py, non-distillation MultiHead branch): head widths come from the dictionary
        # that the PostProcess builds. Relative dict paths in the yaml resolve against the checkout root.
        from ppocr.postprocess import build_post_process
        previous=Path.cwd()
        try:
            os.chdir(root); post=build_post_process(full['PostProcess'],full['Global'])
        finally: os.chdir(previous)
        char_num=len(getattr(post,'character'))
        if full['PostProcess']['name']=='SARLabelDecode': char_num-=2
        if full['PostProcess']['name']=='NRTRLabelDecode': char_num-=3
        cfg['Head']['out_channels_list']={'CTCLabelDecode':char_num,'SARLabelDecode':char_num+2,'NRTRLabelDecode':char_num+3}
    model=build_model(cfg)
    state=paddle.load(spec['native_checkpoint'])
    missing,unexpected=model.set_state_dict(state)
    if missing or unexpected:raise ValueError(f'native Paddle missing/unexpected layers: {missing}/{unexpected}')
    model.eval()
    transform,prep_source=r01_preprocessor(spec,root)
    class Native:
        binding=dict(checkpoint_sha256=sha256(spec['native_checkpoint']),revision=spec['native_revision'],
                     config_sha256=sha256(spec['native_config']),loader_sha256=sha256(inspect.getfile(build_model)),
                     preprocessing_source=str(prep_source),preprocessing_source_sha256=sha256(prep_source))
        def preprocess(self,path):return transform(path)
        def endpoints(self,x):
            x=paddle.to_tensor(x.detach().cpu().numpy(),dtype='float32')
            with paddle.no_grad():
                backbone=model.backbone(x)
                if getattr(model,'neck',None) is not None:backbone=model.neck(backbone)
                neck=model.head.ctc_encoder(backbone)
                logits=model.head.ctc_head.fc(neck)
            return dict(backbone=backbone.numpy(),neck=neck.numpy(),logits=logits.numpy())
    return Native()
