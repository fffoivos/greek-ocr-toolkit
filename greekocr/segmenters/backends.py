"""Inference-session injection only; native detector pre/postprocessing is unchanged.

CoreML options: https://onnxruntime.ai/docs/execution-providers/CoreML-ExecutionProvider.html
Shape specialization also covers the smaller recovery crops that R8 may request.
"""
from pathlib import Path
from types import SimpleNamespace
import hashlib
import json
import os
import re
import threading
from time import perf_counter

_LOG_LOCK = threading.Lock()


def session_options():
    import onnxruntime as ort
    opts = ort.SessionOptions()
    opts.intra_op_num_threads = opts.inter_op_num_threads = 1
    opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    return opts


def partition_counts(log):
    matches = re.findall(r'number of partitions supported by CoreML: (\d+)\s+'
                         r'number of nodes in the graph: (\d+)\s+'
                         r'number of nodes supported by CoreML: (\d+)', log)
    if not matches:
        raise RuntimeError('CoreML partition counts missing from verbose ORT log')
    partitions, total, supported = map(int, matches[-1])
    return dict(partitions=partitions, graph_nodes=total, coreml_nodes=supported,
                cpu_fallback_nodes=total-supported)


class CoreMLSession:
    """ORT-compatible lazy session, one static specialization per tensor shape.

    All calls are made on the GPU owner in the overlap runner. ORT stderr during
    initialization is retained verbatim, and the execution profile is finalized
    explicitly. Provider presence alone is never treated as offload evidence.
    """
    def __init__(self, model_path, cache_dir):
        import onnx
        import onnxruntime as ort
        if 'CoreMLExecutionProvider' not in ort.get_available_providers():
            raise RuntimeError('CoreMLExecutionProvider unavailable')
        self.path = Path(model_path)
        self.cache = Path(cache_dir).expanduser()
        self.cache.mkdir(parents=True, exist_ok=True)
        self.model_sha256 = hashlib.sha256(self.path.read_bytes()).hexdigest()
        self.name = onnx.load(self.path).graph.input[0].name
        self.sessions = {}
        self.records = []
        self.last_call_metrics = {}
        self.options = dict(ModelFormat='MLProgram', MLComputeUnits='CPUAndGPU',
                            RequireStaticInputShapes='1', EnableOnSubgraphs='0',
                            AllowLowPrecisionAccumulationOnGPU='0',
                            ProfileComputePlan='1')

    def get_inputs(self):
        return [SimpleNamespace(name=self.name)]

    def get_providers(self):
        return ['CoreMLExecutionProvider', 'CPUExecutionProvider']

    def run(self, outputs, feed):
        import onnx
        import onnxruntime as ort
        shape = tuple(feed[self.name].shape)
        if shape not in self.sessions:
            setup_start = perf_counter()
            model = onnx.load(self.path)
            for dim, value in zip(model.graph.input[0].type.tensor_type.shape.dim, shape):
                dim.ClearField('dim_param'); dim.dim_value = value
            # Stale intermediate symbolic shapes must be inferred from this input.
            del model.graph.value_info[:]
            for output in model.graph.output:
                for dim in output.type.tensor_type.shape.dim:
                    dim.ClearField('dim_value'); dim.ClearField('dim_param')
            model = onnx.shape_inference.infer_shapes(model)
            # The EP's internal partition hash is unchanged by input dimensions.
            # Both the session AND the physical compiled cache must be isolated.
            key = hashlib.sha256((self.model_sha256 + ':' + 'x'.join(map(str, shape))).encode()).hexdigest()[:60]
            item = model.metadata_props.add(); item.key = 'CACHE_KEY'; item.value = key
            folder = self.cache/key; folder.mkdir(exist_ok=True)
            provider_options = dict(self.options, ModelCacheDirectory=str(folder))
            opts = session_options()
            opts.log_severity_level = 0; opts.log_verbosity_level = 1
            opts.logid = 'r8-coreml-'+key
            opts.enable_profiling = True; opts.profile_file_prefix = str(folder/'profile')
            log = folder/'ort-verbose.log'
            # C++ ORT writes to fd 2, not Python's redirect_stderr.
            with _LOG_LOCK, log.open('wb') as stream:
                saved = os.dup(2)
                try:
                    os.dup2(stream.fileno(), 2)
                    session = ort.InferenceSession(model.SerializeToString(), sess_options=opts,
                        providers=[('CoreMLExecutionProvider', provider_options), 'CPUExecutionProvider'])
                    session.disable_fallback()
                finally:
                    os.dup2(saved, 2); os.close(saved)
            if 'CoreMLExecutionProvider' not in session.get_providers():
                session.end_profiling()
                raise RuntimeError(f'CoreML initialization fell back entirely to CPU; see {log}')
            counts = partition_counts(log.read_text(errors='replace'))
            print('COREML_PARTITIONS', json.dumps(dict(shape=shape, **counts)), flush=True)
            if not counts['partitions'] or not counts['coreml_nodes']:
                session.end_profiling()
                raise RuntimeError(f'CoreML entirely falls back to CPU for {shape}; see {log}')
            self.sessions[shape] = session
            self.records.append(dict(shape=list(shape), cache_key=key,
                model_sha256=self.model_sha256, cache_directory=str(folder),
                setup_s=perf_counter()-setup_start, calls=[], log=str(log), **counts))
        record = next(r for r in self.records if r['shape'] == list(shape))
        start = perf_counter()
        result = self.sessions[shape].run(outputs, feed)
        record['calls'].append(dict(inference_s=perf_counter()-start,
                                    warmup=not record['calls']))
        self.last_call_metrics = dict(record['calls'][-1],
            setup_s=record['setup_s'] if len(record['calls']) == 1 else 0.)
        return result

    def finish(self):
        for shape, session in self.sessions.items():
            record = next(r for r in self.records if r['shape'] == list(shape))
            if 'profile' in record:
                continue
            profile = session.end_profiling()
            record['profile'] = profile
            events = json.loads(Path(profile).read_text())
            nodes = {}
            for event in events:
                provider = event.get('args', {}).get('provider')
                if event.get('cat') == 'Node' and provider:
                    nodes.setdefault(provider, set()).add(event['name'])
            record['executed_nodes_by_provider'] = {p:len(v) for p,v in nodes.items()}
            if not nodes.get('CoreMLExecutionProvider'):
                raise RuntimeError('CoreML profile contains no executed CoreML partitions')
        return dict(device='coreml', options=self.options, shapes=self.records,
                    strategy='one static ORT session and ModelCacheDirectory per model SHA256 + input shape')


def make_session(model_path, detector_device='cpu', coreml_cache=None):
    if detector_device not in ('cpu', 'coreml'):
        raise ValueError('detector_device must be cpu or coreml; MPS detector was removed; use coreml for GPU')
    if detector_device == 'coreml':
        cache = coreml_cache or os.environ.get('GREEKOCR_COREML_CACHE')
        if cache is None:
            cache = Path(os.environ.get('GREEKOCR_CACHE_DIR', Path.home()/'.cache/greekocr')).expanduser()/'coreml'
        return CoreMLSession(model_path, cache)
    import onnxruntime as ort
    return ort.InferenceSession(str(model_path), sess_options=session_options(),
                                providers=['CPUExecutionProvider'])
