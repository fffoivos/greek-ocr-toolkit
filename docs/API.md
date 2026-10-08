# Public API

The public surface is the typed functions/classes explicitly exported by the API modules below. `_vendor`, the discovery runner and recognizer internals are private. Re-exported functions are documented once at their defining module. The preserved Docling entry point is also documented.

Every example has two lines. Lowercase names such as `candidate_rows`, `client`, `image`, `recorded_metadata`, and `donor_spec` denote caller-supplied, locally staged inputs; they do not acquire data. Operational examples are node-side invocations, not actions performed during this phase.

Shared types: `PathLike = str | Path`, `Record = dict[str, Any]`; reader, batch-reader, native-reference and HTTP return values have structural protocols in `greekocr/types.py`.

Recipe registry is immutable snapshot identity; mix custody additionally requires exact committed HEAD blobs in the explicit `repo`. Extraction page indices are zero-based. Word-tag absence returns `None` and must be disclosed. Native import document maps are TSV (`path`, `source_doc_id`).

Strict scoring requires raw NFD GT and unchanged predictions. Bake-off decomposes both text and prediction; reading records need `text`, `prediction`, `cohort`, `script_class`, `crop_path`. E1 summaries need `gt`, `prediction`, `arm`, `seed`, `instrument`, `script_class`, `crop_path` and optional category metadata.

Discovery defaults to offline and uses a caller-owned evidence directory. R01/R03 specs bind local pinned checkouts/configs/weights and reviewed native preprocessing. CLLG workers expose `read_batch`, `close`, `binding`, `last_batch_ms`; close them when finished. Service hooks require explicit enabling and the original credential environment variables.

Node environment plans do not execute. Kraken requires the staged wheel with SHA-256 `82faba07d9fa4746cb822c669e822570f8a8c42a9ac1570ad187326cedbd48e4`; E2WS additionally requires a pinned PaddleOCR requirements file. Use original environment evidence in `docs/origins/greek-page-ocr/docs/ocr_program_2026-10-06/E2_NOTES.md`. Pod clients obtain `PRIME_INTELLECT_CONTROL_KEY` from env; mock `PodClient` for offline work. Watches need bounded probes and direct terminal confirmation.

### `greekocr.annotate.line_categories`

`def line_categories(row: Record) -> list[str]`

```python
from greekocr.annotate import line_categories
tags = line_categories({"text":"ΑΒΓ ... 123", "width":1600})
```

### `greekocr.annotate.script_class`

`def script_class(text: str) -> str | None`

```python
from greekocr.annotate import script_class
kind = script_class("ἅλφα Latin")
```

### `greekocr.annotate.word_tags`

`def word_tags(text: str) -> list[Record]`

Diagnostic fallback tags, never a fabricated factory-sidecar receipt.

```python
from greekocr.annotate import word_tags
tags = word_tags("ἅλφα Latin")
```

### `greekocr.annotate.load_word_tags`

`def load_word_tags(build_dir: PathLike) -> list[Record] | None`

Return only the receipt-bound sidecar; historical absence returns None.

```python
from greekocr.annotate import load_word_tags
tags_or_none = load_word_tags("real")
```

### `greekocr.cli.main`

`def main(argv: Sequence[str] | None=None) -> int`

```python
from greekocr.cli import main
exit_code = main(["annotate", "ἅλφα Latin"])
```

### `greekocr.deploy.plugin_options`

`def plugin_options(checkpoint: PathLike, codec: PathLike, *, routing_sidecar: PathLike | None=None, replace_policy: str='routed_pages', checkpoint_sha256: str | None=None, device: str='cpu') -> Any`

```python
from greekocr.deploy import plugin_options
options = plugin_options("weights.pt", "codec/v1.json", routing_sidecar="routes.jsonl")
```

### `greekocr.deploy.docling_plugin.docling_plugin.ocr_engines`

`def ocr_engines()`

```python
from greekocr.deploy.docling_plugin.docling_plugin import ocr_engines
engines = ocr_engines()
```

### `greekocr.deploy.node_envs.EnvironmentRecipe`

```python
from greekocr.deploy.node_envs import EnvironmentRecipe
recipe = EnvironmentRecipe("ocr", "3.11", "https://download.pytorch.org/whl/cu126", ("safetensors==0.7.0",))
```

### `greekocr.deploy.node_envs.environment_recipes`

`def environment_recipes() -> dict[str, EnvironmentRecipe]`

Owner-bound environments; CLLG is isolated from Paddle/Transformers.

```python
from greekocr.deploy.node_envs import environment_recipes
recipes = environment_recipes()
```

### `greekocr.deploy.node_envs.environment_plan`

`def environment_plan(name: str, venv: PathLike, *, wheelhouse: PathLike | None=None, paddle_requirements: PathLike | None=None) -> list[list[str]]`

Return shell-free argv lists; Kraken needs a pre-staged, hash-checked wheel.

```python
from greekocr.deploy.node_envs import environment_plan
commands = environment_plan("cllg-gpu", "/node/venvs/cllg-gpu", wheelhouse="/node/wheels")
```

### `greekocr.deploy.node_envs.write_environment_script`

`def write_environment_script(name: str, venv: PathLike, out: PathLike, *, wheelhouse: PathLike | None=None, paddle_requirements: PathLike | None=None) -> Path`

Write a Linux-only setup script; caller reviews/executes it on the node.

```python
from greekocr.deploy.node_envs import write_environment_script
script = write_environment_script("e2ws", "/node/venvs/e2ws", "setup.sh", paddle_requirements="/node/PaddleOCR/requirements.txt")
```

### `greekocr.deploy.pods.PodClient`

```python
from greekocr.deploy.pods import PodClient
client = PodClient(lambda method, path, body: {"status":"ACTIVE"})
```

### `greekocr.deploy.pods.PodClient.request`

`def request(self, method: str, path: str, body: Record | None=None) -> Record`

```python
from greekocr.deploy.pods import PodClient
result = PodClient(mock_transport).request("GET", "/api/v1/pods/pod-id")
```

### `greekocr.deploy.pods.pod_client`

`def pod_client(*, env: Mapping[str, str] | None=None, timeout: float=60) -> PodClient`

```python
from greekocr.deploy.pods import pod_client
client = pod_client()
```

### `greekocr.deploy.pods.select_offer`

`def select_offer(offers: list[Record]) -> Record`

Preserved GPU/provider priority, then lowest on-demand price per priority.

```python
from greekocr.deploy.pods import select_offer
offer = select_offer(recorded_offers)
```

### `greekocr.deploy.pods.create_pod`

`def create_pod(client: PodClient, *, name: str='greek-ocr-e2-20261008', public_key: str | None=None) -> Record`

```python
from greekocr.deploy.pods import create_pod
receipt = create_pod(client, name="greek-ocr-worker", public_key=ssh_public_key)
```

### `greekocr.deploy.pods.pod_status`

`def pod_status(client: PodClient, pod_id: str) -> Record`

```python
from greekocr.deploy.pods import pod_status
status = pod_status(client, "pod-id")
```

### `greekocr.deploy.pods.terminate_pod`

`def terminate_pod(client: PodClient, pod_id: str) -> Record`

```python
from greekocr.deploy.pods import terminate_pod
result = terminate_pod(client, "pod-id")
```

### `greekocr.deploy.pods.ensure_pod`

`def ensure_pod(client: PodClient, state: PathLike, *, name: str='greek-ocr-e2-20261008', public_key: str | None=None, timeout: float=1500, poll_seconds: float=20, emit: Callable[[str], None]=print, clock: Callable[[], float]=time.monotonic, sleep: Callable[[float], None]=time.sleep) -> Record`

Reuse or create, record each poll, and emit ACTIVE/FAILED/TIMEOUT liveness.

```python
from greekocr.deploy.pods import ensure_pod
receipt = ensure_pod(client, "pod_state.json", timeout=1500)
```

### `greekocr.ops.rate_limit.rate_limited_client`

`def rate_limited_client(source: str, root: PathLike, *, offline: bool=True, interval: float=2, budget: int=2000000000) -> DiscoveryHTTP`

```python
from greekocr.ops.rate_limit import rate_limited_client
client = rate_limited_client("archive", "evidence/archive", offline=True)
```

### `greekocr.ops.receipts.file_sha256`

`def file_sha256(path: PathLike) -> str`

```python
from greekocr.ops.receipts import file_sha256
digest = file_sha256("records.jsonl")
```

### `greekocr.ops.receipts.verify_files`

`def verify_files(binding: Mapping[str, str]) -> None`

```python
from greekocr.ops.receipts import verify_files
verify_files({"records.jsonl": expected_sha256})
```

### `greekocr.ops.receipts.write_receipt`

`def write_receipt(path: PathLike, receipt: Record) -> None`

```python
from greekocr.ops.receipts import write_receipt
write_receipt("receipt.json", {"training":False})
```

### `greekocr.ops.secrets.require_env`

`def require_env(names: Sequence[str], *, env: Mapping[str, str] | None=None) -> dict[str, str]`

```python
from greekocr.ops.secrets import require_env
secrets = require_env(["PRIME_INTELLECT_CONTROL_KEY"])
```

### `greekocr.ops.watch.Observation`

```python
from greekocr.ops.watch import Observation
observation = Observation(alive=True, log_bytes=100, done=False)
```

### `greekocr.ops.watch.WatchResult`

```python
from greekocr.ops.watch import WatchResult
result = WatchResult(state="DONE", polls=1, elapsed_s=0.1)
```

### `greekocr.ops.watch.watch`

`def watch(label: str, probe: Callable[[], Observation], *, max_seconds: float=1800, stall_seconds: float=900, poll_seconds: float=20, lost_after: int=4, emit: Callable[[str], None]=print, clock: Callable[[], float]=time.monotonic, sleep: Callable[[float], None]=time.sleep) -> WatchResult`

Caller probes must also be bounded; growth measures liveness, never kills.

```python
from greekocr.ops.watch import watch
result = watch("job", bounded_probe, max_seconds=1800, emit=print)
```

### `greekocr.ops.watch.bounded_ssh`

`def bounded_ssh(host: str, command: Sequence[str], *, timeout: float=45) -> subprocess.CompletedProcess[str]`

Batch SSH with connection bound, keepalive and a local process timeout.

```python
from greekocr.ops.watch import bounded_ssh
completed = bounded_ssh("worker", ["tail","-n","1","job.log"], timeout=45)
```

### `greekocr.readers.cllg.load_cllg`

`def load_cllg(spec: Record) -> Reader`

```python
from greekocr.readers.cllg import load_cllg
reader = load_cllg({"checkpoint":"ppocr_v6_tau090.safetensors", "readme":"README.md", "contract":"readme_contract.json"})
```

### `greekocr.readers.cllg.load_cllg_worker`

`def load_cllg_worker(checkpoint: PathLike, contract: Record | None=None, *, python: PathLike | None=None, timeout: float=300) -> BatchReader`

```python
from greekocr.readers.cllg import load_cllg_worker
reader = load_cllg_worker("ppocr_v6_tau090.safetensors", python="/node/venvs/cllg/bin/python")
```

### `greekocr.readers.cllg.build_cllg_contract`

`def build_cllg_contract(readme: PathLike, checkpoint: PathLike, out: PathLike) -> Record`

```python
from greekocr.readers.cllg import build_cllg_contract
contract = build_cllg_contract("README.md", "ppocr_v6_tau090.safetensors", "readme_contract.json")
```

### `greekocr.readers.kalchas.load_kalchas`

`def load_kalchas(spec: Record) -> Reader`

```python
from greekocr.readers.kalchas import load_kalchas
reader = load_kalchas({"checkout":"/node/kalchas", "checkpoint":"/node/kalchas/kalchas/checkpoints/Kalchas/model9_best_loss_1.35.pt"})
```

### `greekocr.readers.ours.load_ours`

`def load_ours(checkpoint: PathLike, codec: PathLike) -> Reader`

```python
from greekocr.readers.ours import load_ours
reader = load_ours("weights.pt", "codec/v1.json")
```

### `greekocr.readers.paddle_r01.load_paddle_r01`

`def load_paddle_r01(spec: Record) -> NativeReference`

```python
from greekocr.readers.paddle_r01 import load_paddle_r01
reference = load_paddle_r01(r01_spec)
```

### `greekocr.readers.paddle_r01.load_r03`

`def load_r03(spec: Record) -> NativeReference`

```python
from greekocr.readers.paddle_r01 import load_r03
reference = load_r03(r03_spec)
```

### `greekocr.readers.services.load_service`

`def load_service(name: str, spec: Record, *, enabled: bool=False) -> Reader`

```python
from greekocr.readers.services import load_service
reader = load_service("mistral", {"factory":"my_service:factory"}, enabled=True)
```

### `greekocr.real.adjudicate.adjudicate_lines`

`def adjudicate_lines(rows: Iterable[Record], reader: CropReader, teacher: CropReader | None, *, supported: Sequence[str]=('greek_poly', 'greek_mono'), teacher_binding: Record | None=None) -> list[Record]`

```python
from greekocr.real.adjudicate import adjudicate_lines
rows = adjudicate_lines(candidate_rows, ours.read, teacher.read)
```

### `greekocr.real.adjudicate.adjudicate_file`

`def adjudicate_file(records: PathLike, out: PathLike, reader: CropReader, teacher: CropReader | None, *, supported: Sequence[str]=('greek_poly', 'greek_mono'), teacher_binding: Record | None=None, reader_binding: Record | None=None) -> Record`

```python
from greekocr.real.adjudicate import adjudicate_file
receipt = adjudicate_file("records.jsonl", "adjudicated", ours.read, teacher.read)
```

### `greekocr.real.extract.extract_lines`

`def extract_lines(sources: PathLike, partition: PathLike, out: PathLike, *, pages: Sequence[int] | None=None, seed: int=20261007) -> Record`

Extract reviewed PDF/DjVu sources; API page indices are zero-based.

```python
from greekocr.real.extract import extract_lines
receipt = extract_lines("sources.json", "partition.json", "lines", pages=[0,1])
```

### `greekocr.real.geometry.Component`

An 8-connected ink component in top-origin, half-open page pixels.

```python
from greekocr.real.geometry import Component
component = Component(1, (10, 20, 25, 45), 100, 17.0, 32.0)
```

### `greekocr.real.geometry.BaselineCurve`

y = c2*t*t + c1*t + c0, t=(page_x-x_origin)/x_scale.

```python
from greekocr.real.geometry import BaselineCurve
curve = BaselineCurve(2.0, 1.0, 40.0, 100.0, 100.0)
```

### `greekocr.real.geometry.BaselineCurve.evaluate`

`def evaluate(self, x: float) -> float`

Evaluate a page-space baseline at a page-space horizontal position.

```python
from greekocr.real.geometry import BaselineCurve
page_y = BaselineCurve(2.0, 1.0, 40.0, 100.0, 100.0).evaluate(120.0)
```

### `greekocr.real.geometry.GeometryDiagnostics`

Output-strip geometry plus the unchanged input candidate's legacy evidence.

```python
from greekocr.real.geometry import GeometryDiagnostics
diagnostics = GeometryDiagnostics(1, 2, 12.0, 25.0, .15, False, 150, 1.0, (0, 8), ())
```

### `greekocr.real.geometry.Admission`

Geometry decision, named policy thresholds and diagnostic evidence.

```python
from greekocr.real.geometry import Admission
decision = Admission(True, "scan", (), thresholds, diagnostic_record)
```

### `greekocr.real.geometry.Admission.receipt`

`def receipt(self) -> dict[str, Any]`

Return a JSON-serializable policy receipt; admission is never human gold.

```python
from greekocr.real.geometry import Admission
record = result.receipt()
```

### `greekocr.real.geometry.LineCrop`

Rectified grayscale strip and page-space provenance; text stays provisional.

```python
from greekocr.real.geometry import LineCrop
crop = LineCrop(image, box, padded_box, refined_box, curve, kept, dropped, diagnostics, 30, 5)
```

### `greekocr.real.geometry.LineCrop.receipt`

`def receipt(self) -> dict[str, Any]`

Return deterministic geometry metadata, excluding raster image bytes.

```python
from greekocr.real.geometry import LineCrop
record = result.receipt()
```

### `greekocr.real.geometry.TextLayerBox`

A pixel line box, raw label and optional original vendored admission row.

```python
from greekocr.real.geometry import TextLayerBox
candidate = TextLayerBox((10, 20, 800, 70), "ἀλήθεια λέξεις", recorded_legacy_row)
```

### `greekocr.real.geometry.ink_components`

`def ink_components(page_image: Image.Image, box: Box | None=None) -> tuple[Component, ...]`

Measure significant ink in a pixel box (or the whole locally staged image).

```python
from greekocr.real.geometry import ink_components
components = ink_components(image, (10, 20, 800, 70))
```

### `greekocr.real.geometry.split_multiline`

`def split_multiline(box: Box, components: Sequence[Component]) -> list[PixelBox]`

Split supported baseline clusters inside a box; never assign label substrings.

```python
from greekocr.real.geometry import split_multiline
boxes = split_multiline((10, 20, 800, 120), components)
```

### `greekocr.real.geometry.refine_line`

`def refine_line(page_image: Image.Image, box: Box, *, pad: int=DEFAULT_PAD) -> LineCrop`

Select one baseline, fit glyph bottoms robustly and sample a curved ink strip.

```python
from greekocr.real.geometry import refine_line
crop = refine_line(image, (10, 20, 800, 70), pad=16)
```

### `greekocr.real.geometry.scan_admission`

`def scan_admission(diagnostics: GeometryDiagnostics | Mapping[str, Any], *, profile: Profile='scan') -> Admission`

Gate rectified scan geometry or replay the complete unchanged vendored rule.

```python
from greekocr.real.geometry import scan_admission
decision = scan_admission(crop.diagnostics, profile="scan")
```

### `greekocr.real.geometry.hyphen_at_line_end`

`def hyphen_at_line_end(crop: LineCrop | Image.Image, text: str) -> bool`

Flag a terminal dash after a body glyph when the raw label lacks a hyphen.

```python
from greekocr.real.geometry import hyphen_at_line_end
missing = hyphen_at_line_end(crop, "ἀλήθεια λέξεις")
```

### `greekocr.real.geometry.refine_page_lines`

`def refine_page_lines(pdf_page_image: Image.Image, text_layer_boxes: Sequence[TextLayerBox | Box | Mapping[str, Any]], *, pad: int=DEFAULT_PAD) -> list[LineCrop]`

Refine pixel boxes in input order; split labels are withheld for caller assignment.

```python
from greekocr.real.geometry import refine_page_lines
crops = refine_page_lines(image, text_layer_boxes, pad=16)
```

### `greekocr.real.geometry_measure.comparison_scores`

`def comparison_scores(text: str, old: str, new: str) -> dict[str, Any]`

Match the O4d coordinator's NFD SequenceMatcher score and trimmed exacts.

```python
from greekocr.real.geometry_measure import comparison_scores
scores = comparison_scores("ἅ", "α", "α\u0314\u0301")
```

### `greekocr.real.geometry_measure.summarize_measurements`

`def summarize_measurements(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]`

Aggregate successfully scored pairs; errors never count as improvements.

```python
from greekocr.real.geometry_measure import summarize_measurements
summary = summarize_measurements(scored_geometry_rows)
```

### `greekocr.real.geometry_measure.measure_geometry`

`def measure_geometry(lines: PathLike | Sequence[Mapping[str, Any]], reader: CropReader, *, out: PathLike | None=None, pad: int=DEFAULT_PAD, reader_name: str | None=None) -> dict[str, Any]`

Read each original path and its refined PNG with a caller-supplied reader.

```python
from greekocr.real.geometry_measure import measure_geometry
receipt = measure_geometry("lines.jsonl", cllg.read, out="geometry-measure", pad=16)
```

### `greekocr.real.importers.native_rows`

`def native_rows(spec: Record, root: PathLike) -> Iterator[Record]`

Parse reviewed dataset formats, retaining native paths and labels.

```python
from greekocr.real.importers import native_rows
rows = list(native_rows({"format":"pairs", "document_map":"documents.tsv"}, "dataset"))
```

### `greekocr.real.importers.import_dataset`

`def import_dataset(manifest: PathLike, partition: PathLike, out: PathLike, *, seed: int=20261007) -> Record`

```python
from greekocr.real.importers import import_dataset
receipt = import_dataset("datasets.json", "partition.json", "imported")
```

### `greekocr.real.importers.import_real_shards`

`def import_real_shards(records: PathLike, crops: PathLike, binary: PathLike, out: PathLike, *, partition: str, timeout: float=3600) -> Record`

```python
from greekocr.real.importers import import_real_shards
receipt = import_real_shards("adjudicated/records.jsonl", "crops", "/node/linefactory", "real", partition="o4b-documents-v1")
```

### `greekocr.real.partition.DocumentPartition`

```python
from greekocr.real.partition import DocumentPartition
partition = DocumentPartition("reviewed_partition.json")
```

### `greekocr.real.partition.DocumentPartition.assign`

`def assign(self, document: str, sha256: str | None=None) -> tuple[str, str | None]`

Return canonical work and split; excluded works get None.

```python
from greekocr.real.partition import DocumentPartition
work, split = DocumentPartition("reviewed_partition.json").assign("book-id")
```

### `greekocr.real.partition.resolve_exclusions`

`def resolve_exclusions(documents: Mapping[str, str], identities: Sequence[str]) -> list[str]`

Resolve every known alias; unknown exposure identities are errors.

```python
from greekocr.real.partition import resolve_exclusions
excluded = resolve_exclusions({"mirror":"canonical-work"}, ["mirror"])
```

### `greekocr.real.partition.build_partition`

`def build_partition(o5: PathLike, c1: PathLike, document_map: PathLike, out: PathLike, *, reviewed: bool=False) -> Record`

```python
from greekocr.real.partition import build_partition
receipt = build_partition("o5_info.json", "c1.json", "document_map.json", "partition.json", reviewed=True)
```

### `greekocr.real.sources.discovery.parse_source`

`def parse_source(source: str, metadata: Record, *, identifier: str='', language: str='el') -> Record`

Parse recorded metadata only; never infer confirmed rights or gold labels.

```python
from greekocr.real.sources.discovery import parse_source
row = parse_source("parliament", recorded_metadata)
```

### `greekocr.real.sources.discovery.discovery_command`

`def discovery_command(source: str, out: PathLike, *, offline: bool=True, args: Sequence[str]=(), python: PathLike=sys.executable, evidence_root: PathLike | None=None, timeout: float=1800) -> list[str]`

```python
from greekocr.real.sources.discovery import discovery_command
argv = discovery_command("archive", "evidence/archive.jsonl", offline=True)
```

### `greekocr.real.sources.discovery.run_discovery`

`def run_discovery(source: str, out: PathLike, *, offline: bool=True, args: Sequence[str]=(), timeout: float=1800, evidence_root: PathLike | None=None) -> subprocess.CompletedProcess[str]`

Run native CLI on a worker; arguments include original bounded crawl controls.

```python
from greekocr.real.sources.discovery import run_discovery
completed = run_discovery("archive", "evidence/archive.jsonl", offline=True, args=["--max-pages","1"])
```

### `greekocr.real.sources.discovery.http_client`

`def http_client(source: str, root: PathLike, *, offline: bool=True, interval: float=2, budget: int=2000000000) -> DiscoveryHTTP`

Expose the preserved rate-lock/cache/ledger transport with an explicit root.

```python
from greekocr.real.sources.discovery import http_client
client = http_client("anemi", "evidence/anemi", offline=True, interval=2)
```

### `greekocr.real.sources.parliament.refetch_pdf_cache`

`def refetch_pdf_cache(manifest: PathLike, out: PathLike, *, timeout: float=1800) -> list[Record]`

Preserve three attempts and hash-before-publication; return verified file receipts.

```python
from greekocr.real.sources.parliament import refetch_pdf_cache
receipts = refetch_pdf_cache("pdf_cache_refetch.jsonl", "pdf_cache")
```

### `greekocr.real.sources.parliament.stage_parliament`

`def stage_parliament(candidate_root: PathLike, out: PathLike, *, timeout: float=1800) -> list[Record]`

Ranked S2 staging, with original MD5-match flags and SHA-256 receipts.

```python
from greekocr.real.sources.parliament import stage_parliament
receipts = stage_parliament("/node/project", "parliament_s2")
```

### `greekocr.score.strict_cer`

`def strict_cer(reference: str, prediction: str) -> float`

Score codepoints as supplied; predictions are never renormalized.

```python
from greekocr.score import strict_cer
cer = strict_cer("α\u0313", "α")
```

### `greekocr.score.edit_distance`

`def edit_distance(reference: str, prediction: str) -> int`

```python
from greekocr.score import edit_distance
edits = edit_distance("Α", "A")
```

### `greekocr.score.score_readings`

`def score_readings(readings: Sequence[Record]) -> Record`

Bake-off NFD decomposition of both inputs, with marks and homoglyphs.

```python
from greekocr.score import score_readings
report = score_readings([{"text":"ἅ", "prediction":"ά", "cohort":"gold", "script_class":"greek_poly", "crop_path":"crop.png"}])
```

### `greekocr.score.summarize_predictions`

`def summarize_predictions(rows: Sequence[Record]) -> Record`

Strict E1 readout, including overlapping diagnostic by_category strata.

```python
from greekocr.score import summarize_predictions
report = summarize_predictions(raw_nfd_prediction_rows)
```

### `greekocr.score.write_readout`

`def write_readout(predictions: Sequence[PathLike], out: PathLike, *, require_complete: bool=False, transfer_enabled: bool | None=None, title: str='E1') -> Record`

```python
from greekocr.score import write_readout
report = write_readout(["predictions.jsonl"], "readout", transfer_enabled=False)
```

### `greekocr.synth.Recipe`

```python
from greekocr.synth import Recipe
recipe = Recipe("custom", recipe_path, expected_sha256, origin_commit)
```

### `greekocr.synth.recipe_registry`

`def recipe_registry() -> dict[str, Recipe]`

Return v5/v7/v8 pinned to the captured source bytes (not a mutable rehash).

```python
from greekocr.synth import recipe_registry
registry = recipe_registry()
```

### `greekocr.synth.verify_recipe_sha`

`def verify_recipe_sha(recipe: Recipe | PathLike, expected: str | None=None) -> str`

Assert recipe byte identity; unknown paths require an explicit expected digest.

```python
from greekocr.synth import verify_recipe_sha
digest = verify_recipe_sha("v5")
```

### `greekocr.synth.build_shards`

`def build_shards(recipe: Recipe | str, binary: PathLike, out: PathLike, *, pool: PathLike, workdir: PathLike | None=None, timeout: float=3600) -> Record`

Run an existing linefactory; require its audit, recipe and exact shard receipt.

```python
from greekocr.synth import build_shards
receipt = build_shards("v5", "/node/linefactory", "out", pool="pool.jsonl", workdir="/node/greek-page-ocr")
```

### `greekocr.synth.build_mix`

`def build_mix(components: Sequence[Record], out: PathLike, *, repo: PathLike, seed: int=0, codec_version: str='v1', created_by: str='greekocr.synth', notes: str='', role: str='train') -> Record`

Bind factory receipts using the unchanged HEAD-blob custody validator.

```python
from greekocr.synth import build_mix
manifest = build_mix([{"kind":"synthetic", "build_dir":"synth", "fraction":1}], "mix.json", repo="/node/greek-page-ocr")
```

### `greekocr.synth.validate_mix`

`def validate_mix(path: PathLike, *, repo: PathLike, role: str='train') -> Record`

Fail closed on recipes, role, receipt fields and exact shard membership.

```python
from greekocr.synth import validate_mix
resolved = validate_mix("mix.json", repo="/node/greek-page-ocr", role="train")
```

### `greekocr.synth.assemble_mix`

`def assemble_mix(groups: Sequence[Sequence[Record]], fractions: Sequence[float], seed: int, *, epoch: int=0, max_rows: int | None=None) -> tuple[list[Record], list[int]]`

Unchanged largest-remainder quotas and seed:epoch:component cycling.

```python
from greekocr.synth import assemble_mix
rows, counts = assemble_mix([[{"line_id":"a"}], [{"line_id":"b"}]], [.25,.75], seed=0)
```

### `greekocr.warmstart.map_donor_state`

`def map_donor_state(family: str, state: Mapping[str, Any]) -> tuple[Record, Record, list[str]]`

```python
from greekocr.warmstart import map_donor_state
mapped, layers, dropped = map_donor_state("R03", upstream_tensor_state)
```

### `greekocr.warmstart.map_paddle_state`

`def map_paddle_state(state: Mapping[str, Any], layer_map: Record, expected: Mapping[str, Any]) -> Record`

```python
from greekocr.warmstart import map_paddle_state
mapped = map_paddle_state(paddle_state, reviewed_layer_map, expected_torch_state)
```

### `greekocr.warmstart.preprocess`

`def preprocess(image: Image.Image, contract: Record) -> Any`

```python
from greekocr.warmstart import preprocess
tensor = preprocess(image, {"color":"BGR", "height":48, "interpolation":"linear", "pad_rule":"paddle_dynamic", "pad_width":320})
```

### `greekocr.warmstart.compare_endpoints`

`def compare_endpoints(native: Mapping[str, Any], converted: Mapping[str, Any]) -> Record`

```python
from greekocr.warmstart import compare_endpoints
receipt = compare_endpoints(native_endpoints, converted_endpoints)
```

### `greekocr.warmstart.convert_donor`

`def convert_donor(family: str, checkpoint: PathLike, config: PathLike, out: PathLike, revision: str, *, codec: PathLike, seed: int=0) -> Record`

```python
from greekocr.warmstart import convert_donor
receipt = convert_donor("R03", "upstream.pt", "config.json", "converted", "immutable-sha", codec="codec/v1.json")
```

### `greekocr.warmstart.verify_init`

`def verify_init(path: PathLike) -> Record`

```python
from greekocr.warmstart import verify_init
checkpoint = verify_init("converted/donor_init.pt")
```

### `greekocr.warmstart.qualify_parity`

`def qualify_parity(spec: Record, converted: PathLike, crops: PathLike, out: PathLike) -> Record`

```python
from greekocr.warmstart import qualify_parity
receipt = qualify_parity(donor_spec, "converted/native_before_swap.pt", "100_crops.jsonl", "parity")
```
