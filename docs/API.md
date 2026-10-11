# Public API

For the page entry point and examples, start with [PAGES_GUIDE.md](PAGES_GUIDE.md). Page stages now live in `greekocr.pages`; the corresponding `greekocr.glyphs` imports remain compatibility aliases. Crop APIs are unchanged.

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

### `greekocr.annotate.font.FontEstimate`

Predicted factory font id/style, uncalibrated distance/margin and model provenance.

```python
from greekocr.annotate.font import FontEstimate
estimate = FontEstimate(None, None, None, None, None, False)
```

### `greekocr.annotate.font.FontEstimate.to_dict`

`def to_dict(self) -> dict[str, Any]`

Return a JSON-serializable prediction record.

```python
from greekocr.annotate.font import FontEstimate
record = features.to_dict()
```

### `greekocr.annotate.font.font_style`

`def font_style(font: str | None, styles: Mapping[str, str] | None=None) -> str | None`

Map known factory font ids to shared styles; unidentified/real fonts stay unset.

```python
from greekocr.annotate.font import font_style
style = font_style("GFSDidot_Classic")
```

### `greekocr.annotate.font.font_estimate`

`def font_estimate(image: Image.Image | np.ndarray | PathLike, *, model: PathLike | Mapping[str, Any] | None=None) -> FontEstimate`

Predict using an explicit local model; absent model/blank/outside support abstains.

```python
from greekocr.annotate.font import font_estimate
estimate = font_estimate(image, model="font_model.json")
```

### `greekocr.annotate.font.train_font_classifier`

`def train_font_classifier(shards: PathLike, out_model: PathLike, *, styles: Mapping[str, str] | None=None, max_lines: int | None=None) -> dict[str, Any]`

Fit streaming font centroids from known synthetic fonts, entirely in numpy on CPU.

```python
from greekocr.annotate.font import train_font_classifier
model = train_font_classifier("synthetic/train", "font_model.json")
```

### `greekocr.annotate.line_features.LineFeatures`

JSON-ready measurements; definitions and missing-value rules in LINE_METADATA.md.

```python
from greekocr.annotate.line_features import LineFeatures
features = LineFeatures(**measured_field_values)
```

### `greekocr.annotate.line_features.LineFeatures.to_dict`

`def to_dict(self) -> dict[str, Any]`

Return only built-in finite values, suitable for json.dumps(allow_nan=False).

```python
from greekocr.annotate.line_features import LineFeatures
record = features.to_dict()
```

### `greekocr.annotate.line_features.load_lexicon`

`def load_lexicon(lexicon: PathLike | Iterable[str]) -> frozenset[str]`

Read UTF-8 words (one per line; # comments), folding accents, case and final sigma.

```python
from greekocr.annotate.line_features import load_lexicon
words = load_lexicon("greek_words.txt")
```

### `greekocr.annotate.line_features.line_features`

`def line_features(image: Image.Image | np.ndarray | PathLike, text: str | None=None, *, geometry: Any=None, lexicon: PathLike | Iterable[str] | None=None) -> LineFeatures`

Measure a line at its native scale; optional geometry/Greek lexicon never changes pixels.

```python
from greekocr.annotate.line_features import line_features
features = line_features(image, "ἅλφα", geometry=geometry_receipt)
```

### `greekocr.annotate.pipeline.annotate_records`

`def annotate_records(records_jsonl: PathLike, out_jsonl: PathLike, *, catalogue: Any=None, lexicon: PathLike | Iterable[str] | None=None, font_model: PathLike | Mapping[str, Any] | None=None) -> dict[str, Any]`

Stream records into a new atomic JSONL sidecar; preserve labels, provenance and admission.

```python
from greekocr.annotate.pipeline import annotate_records
receipt = annotate_records("records.jsonl", "annotated.jsonl", lexicon="greek_words.txt")
```

### `greekocr.annotate.pipeline.distribution_report`

`def distribution_report(out_jsonl: PathLike, *, catalogue: Any=None, lexicon: PathLike | Iterable[str] | None=None, font_model: PathLike | Mapping[str, Any] | None=None) -> str`

Report all numeric quantiles/histograms and categorical counts per source, including unknowns.

```python
from greekocr.annotate.pipeline import distribution_report
markdown = distribution_report("annotated.jsonl")
```

### `greekocr.annotate.sources.source_metadata`

`def source_metadata(record: Mapping[str, Any], catalogue: Any=None) -> Record`

Join by document identity; preserve unknown rights and distinguish fetch from publication years.

```python
from greekocr.annotate.sources import source_metadata
metadata = source_metadata(line_record, document_catalogue)
```

### `greekocr.annotate.strata.stratum_key`

`def stratum_key(record: Mapping[str, Any]) -> StratumKey`

Return script/polytonic/document/year/contrast/ink/font axes with explicit unknown bins.

```python
from greekocr.annotate.strata import stratum_key
key = stratum_key(annotated_record)
```

### `greekocr.annotate.strata.stratum_counts`

`def stratum_counts(records: Iterable[Mapping[str, Any]]) -> dict[StratumKey, int]`

Count existing supply only; missing strata are never fabricated.

```python
from greekocr.annotate.strata import stratum_counts
counts = stratum_counts(annotated_records)
```

### `greekocr.annotate.strata.sampling_weights`

`def sampling_weights(records: Iterable[Mapping[str, Any]], *, floor: float=0.0, floors: Mapping[StratumKey, float] | None=None, targets: Mapping[StratumKey, float] | None=None) -> list[float]`

Return normalized per-record probabilities with guaranteed per-stratum mass floors.

```python
from greekocr.annotate.strata import sampling_weights
probabilities = sampling_weights(annotated_records, floor=.01)
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

### `greekocr.glyphs.baseline.Crossing`

```python
from greekocr.glyphs.baseline import Crossing
crossing = skew_line(glyphs).crossings[0]
```

### `greekocr.glyphs.baseline.CutSpan`

```python
from greekocr.glyphs.baseline import CutSpan
span = skew_line(glyphs).cut_spans[0]
```

### `greekocr.glyphs.baseline.CutLetter`

```python
from greekocr.glyphs.baseline import CutLetter
cut = skew_line(glyphs).cut_letters[0]
```

### `greekocr.glyphs.baseline.SecondLine`

```python
from greekocr.glyphs.baseline import SecondLine
second = second_line(glyphs)
```

### `greekocr.glyphs.baseline.second_line`

`def second_line(glyphs: LineGlyphs) -> SecondLine | None`

Fit a band to the ink the main band does not explain (outside its body ± 0.3 x-heights).

```python
from greekocr.glyphs.baseline import second_line
second = second_line(line_glyphs(Image.open("crop.png")))
```

### `greekocr.glyphs.baseline.SkewLine`

```python
from greekocr.glyphs.baseline import SkewLine
line = skew_line(glyphs)
```

### `greekocr.glyphs.baseline.skew_line`

`def skew_line(glyphs: LineGlyphs, boxes: list[LetterBox] | None=None) -> SkewLine`

```python
from greekocr.glyphs.baseline import skew_line
line = skew_line(line_glyphs(Image.open("crop.png")))
```

### `greekocr.glyphs.baseline.GuideLines`

```python
from greekocr.glyphs.baseline import GuideLines
main_line = text_lines(glyphs)[0]
```

### `greekocr.glyphs.baseline.text_lines`

`def text_lines(glyphs: LineGlyphs, *, max_per_side: int=3) -> list[GuideLines]`

The main line and every neighbour line (above / below), each with its four guide lines.

```python
from greekocr.glyphs.baseline import text_lines
lines = text_lines(line_glyphs(Image.open("crop.png")))
```

### `greekocr.glyphs.columns.Segment`

```python
from greekocr.glyphs.columns import Segment
segment = column_segments(Image.open("crop.png"))[0]
```

### `greekocr.glyphs.columns.column_rules`

`def column_rules(crop: Image.Image | NDArray[Any]) -> list[tuple[int, int]]`

x-ranges of vertical rules: tall thin ink spanning most of the crop height.

```python
from greekocr.glyphs.columns import column_rules
rules = column_rules(Image.open("crop.png"))
```

### `greekocr.glyphs.columns.column_segments`

`def column_segments(crop: Image.Image | NDArray[Any], **kw: Any) -> list[Segment]`

Cut at rules; each segment gets its own line_glyphs (own band, skew, bends, guide lines).

```python
from greekocr.glyphs.columns import column_segments
segments = column_segments(Image.open("crop.png"), xh_prior=None)
```

### `greekocr.glyphs.components.to_gray`

`def to_gray(crop: Image.Image | NDArray[Any]) -> NDArray[np.float64]`

Grayscale float array in [0, 255], ink dark.

```python
from greekocr.glyphs.components import to_gray
gray = to_gray(Image.open("crop.png"))
```

### `greekocr.glyphs.components.binarise`

`def binarise(gray: NDArray[np.float64], *, window: int | None=None, k: float=0.2) -> NDArray[np.bool_]`

Ink mask = Sauvola local threshold (window ≈ crop height) AND a loose global floor, PLUS faint components.

```python
from greekocr.glyphs.components import binarise
ink = binarise(gray)
```

### `greekocr.glyphs.components.Band`

The letter band as functions of x: top = mean line, bottom = baseline (row coordinates, may lie outside the crop).

```python
from greekocr.glyphs.components import Band
band = line_glyphs(Image.open("crop.png")).band
```

### `greekocr.glyphs.components.Band.at`

`def at(self, x: float) -> tuple[float, float]`

```python
from greekocr.glyphs.components import Band
mean_line, baseline = band.at(120.0)
```

### `greekocr.glyphs.components.Component`

One 8-connected ink component. `rel_*` fields are normalised by the line x-height.

```python
from greekocr.glyphs.components import Component
component = Component(1, (10, 20, 25, 45), 100, 17.0, 32.0)
```

### `greekocr.glyphs.components.LineGlyphs`

```python
from greekocr.glyphs.components import LineGlyphs
glyphs = line_glyphs(Image.open("crop.png"))
```

### `greekocr.glyphs.components.line_glyphs`

`def line_glyphs(crop: Image.Image | NDArray[Any], *, seed: int=0, xh_prior: float | None=None, focus: tuple[float, float] | None=None) -> LineGlyphs`

Components with descriptors and roles plus the letter band they define. CPU, a few ms for a 1500×80 strip.

```python
from greekocr.glyphs.components import line_glyphs
glyphs = line_glyphs(Image.open("crop.png"), xh_prior=None)
```

### `greekocr.glyphs.evaluate.GlyphScore`

```python
from greekocr.glyphs.evaluate import GlyphScore
total = GlyphScore()
```

### `greekocr.glyphs.evaluate.GlyphScore.add`

`def add(self, other: 'GlyphScore') -> None`

```python
from greekocr.glyphs.evaluate import GlyphScore
total.add(score_rendered(rendered))
```

### `greekocr.glyphs.evaluate.score_rendered`

`def score_rendered(sample: Rendered, glyphs: LineGlyphs | None=None, boxes: list[LetterBox] | None=None, *, state_truth: str='print') -> GlyphScore`

state_truth: 'print' = the physical print (clean ink after defects); 'visible' = ink at least a quarter of the

```python
from greekocr.glyphs.evaluate import score_rendered
score = score_rendered(render_truth_line("ἀνδρώας", "GFSDidot-Regular.ttf"))
```

### `greekocr.glyphs.evaluate.summarise`

`def summarise(score: GlyphScore) -> dict[str, object]`

```python
from greekocr.glyphs.evaluate import summarise
rates = summarise(score)
```

### `greekocr.glyphs.ink.LetterInk`

```python
from greekocr.glyphs.ink import LetterInk
letter = ink_profile(glyphs).letters[0]
```

### `greekocr.glyphs.ink.InkProfile`

```python
from greekocr.glyphs.ink import InkProfile
profile = ink_profile(glyphs)
```

### `greekocr.glyphs.ink.ink_profile`

`def ink_profile(glyphs: LineGlyphs, boxes: list[LetterBox] | None=None, *, reference_contrast: float | None=None) -> InkProfile`

```python
from greekocr.glyphs.ink import ink_profile
profile = ink_profile(line_glyphs(Image.open("crop.png")))
```

### `greekocr.glyphs.letters.LetterBox`

```python
from greekocr.glyphs.letters import LetterBox
box = letter_boxes(glyphs)[0]
```

### `greekocr.glyphs.letters.middle_mask`

`def middle_mask(glyphs: LineGlyphs) -> np.ndarray`

```python
from greekocr.glyphs.letters import middle_mask
mid = middle_mask(line_glyphs(Image.open("crop.png")))
```

### `greekocr.glyphs.letters.letter_boxes`

`def letter_boxes(glyphs: LineGlyphs) -> list[LetterBox]`

```python
from greekocr.glyphs.letters import letter_boxes
boxes = letter_boxes(line_glyphs(Image.open("crop.png")))
```

### `greekocr.glyphs.lines_api.LineImage`

```python
from greekocr.glyphs.lines_api import LineImage
line = separate_lines(Image.open("crop.png"))[0]
```

### `greekocr.glyphs.lines_api.straighten`

`def straighten(gray: NDArray[np.float64], base: NDArray[np.float64], xh: float, *, paper: float, above: float=ABOVE, below: float=BELOW) -> tuple[NDArray[np.float64], NDArray[np.bool_], int]`

Resample every column so the baseline lands on one row; linear interpolation along each column.

```python
from greekocr.glyphs.lines_api import straighten
flat, missing, baseline_row = straighten(glyphs.gray, glyphs.band.bottom, glyphs.band.xh, paper=glyphs.paper)
```

### `greekocr.glyphs.lines_api.straighten_edges`

`def straighten_edges(base: NDArray[np.float64], xh: float, height: int, *, above: float=ABOVE, below: float=BELOW) -> tuple[NDArray[np.bool_], NDArray[np.bool_]]`

Directional masks of the straightened grid: source above the crop top / below the crop bottom (CP-G3 F2).

```python
from greekocr.glyphs.lines_api import straighten_edges
above_top, below_bottom = straighten_edges(glyphs.band.bottom, glyphs.band.xh, glyphs.height)
```

### `greekocr.glyphs.lines_api.separate_lines`

`def separate_lines(crop: Image.Image | NDArray[Any], *, min_visible: float=0.5, tight: bool=True, margin: float=0.2, level_deg: float=0.0, **kw: Any) -> list[LineImage]`

One straightened image per text line. Recogniser-facing default: tight=True, margin=0.2 x-heights — the image is

```python
from greekocr.glyphs.lines_api import separate_lines
lines = separate_lines(Image.open("crop.png"), min_visible=.5)
```

### `greekocr.glyphs.orientation.QuarterTurn`

Exact boundary-coordinate transform from a source crop to upright pixels.

```python
from greekocr.glyphs.orientation import QuarterTurn
frame = QuarterTurn(image.width, image.height, 270, offset=(11, 13))
```

### `greekocr.glyphs.orientation.QuarterTurn.points`

`def points(self, points: Sequence[Sequence[float]] | np.ndarray, *, inverse: bool=False) -> np.ndarray`

Map N corners or guide samples; never reduce an oriented quad to AABB.

```python
from greekocr.glyphs.orientation import QuarterTurn
mapped = frame.points(corners, inverse=True)
```

### `greekocr.glyphs.orientation.QuarterTurn.image`

`def image(self, image: Image.Image) -> Image.Image`

Normalize pixels with exact transposition (no quarter-turn resampling).

```python
from greekocr.glyphs.orientation import QuarterTurn
upright = frame.image(image)
```

### `greekocr.glyphs.orientation.QuarterTurn.rectangle`

`def rectangle(self, box: Sequence[float], *, inverse: bool=True) -> np.ndarray`

Ordered BL, BR, TR, TL corners, mapped from an upright text box.

```python
from greekocr.glyphs.orientation import QuarterTurn
corners = frame.rectangle((10, 20, 80, 45))
```

### `greekocr.glyphs.orientation.Orientation`

Axis, polarity, residual skew and their independent evidence.

```python
from greekocr.glyphs.orientation import Orientation
decision = Orientation(axis="horizontal", orientation_cw=None, alternatives=[0, 180])
```

### `greekocr.glyphs.orientation.Orientation.to_record`

`def to_record(self) -> dict`

JSON-ready record; None serializes as explicit unknown (null).

```python
from greekocr.glyphs.orientation import Orientation
record = decision.to_record()
```

### `greekocr.glyphs.orientation.measure_orientation`

`def measure_orientation(image: Image.Image, *, use_osd: bool=False, unit: str='block', axis_hint: str | None=None, content_kind: str='unknown', font_reference: dict | None=None) -> Orientation`

Compare fitted guides in both region readings; words never decide alone.

```python
from greekocr.glyphs.orientation import measure_orientation
decision = measure_orientation(image, use_osd=False, unit="block")
```

### `greekocr.glyphs.orientation.canonical_word_crop`

`def canonical_word_crop(image: Image.Image) -> Image.Image`

Remove arbitrary margins, keep all significant ink, add 0.1 body heights.

```python
from greekocr.glyphs.orientation import canonical_word_crop
crop = canonical_word_crop(word_image)
```

### `greekocr.glyphs.orientation.recognizer_polarity`

`def recognizer_polarity(image: Image.Image, orientation: Orientation, recognizer: _Recognizer, *, margin: float=0.12) -> Orientation`

Compare axis-consistent readings with our recognizer; retain both on doubt.

```python
from greekocr.glyphs.orientation import recognizer_polarity
decision = recognizer_polarity(crop, axis_decision, recognizer)
```

### `greekocr.glyphs.orientation.discover_directions`

`def discover_directions(image: Image.Image) -> list[dict]`

Propose local chains in BOTH axes before fitting any horizontal lines.

```python
from greekocr.glyphs.orientation import discover_directions
proposals = discover_directions(page_image)
```

### `greekocr.glyphs.orientation_regions.axis_regions`

`def axis_regions(proposals: Sequence[dict]) -> list[dict]`

Join same-axis chains by typographic whitespace; reject crossing fragments.

```python
from greekocr.glyphs.orientation_regions import axis_regions
regions = axis_regions(discover_directions(image))
```

### `greekocr.glyphs.orientation_regions.resolve_regions`

`def resolve_regions(regions: Sequence[dict], *, main_id: str | None=None) -> list[dict]`

Inherit within explicit groups, then retain at most two accepted angles.

```python
from greekocr.glyphs.orientation_regions import resolve_regions
regions = resolve_regions(measured_regions, main_id="page")
```

### `greekocr.glyphs.orientation_regions.page_regions`

`def page_regions(image: Image.Image, *, proposals: list[dict] | None=None, dominant: Orientation | None=None, use_osd: bool=False) -> tuple[Orientation, list[dict], list[dict]]`

Discover before fitting; compare both readings of main and minority regions.

```python
from greekocr.glyphs.orientation_regions import page_regions
dominant, regions, proposals = page_regions(image, use_osd=False)
```

### `greekocr.glyphs.oriented_page.OrientedWord`

A separately recognizable word and its local guides, in a reversible frame.

```python
from greekocr.glyphs.oriented_page import OrientedWord
word = OrientedWord(**measured_word_geometry)
```

### `greekocr.glyphs.oriented_page.OrientedWord.to_record`

`def to_record(self, image_size: Sequence[int], page_size: Sequence[float] | None=None) -> dict`

Serialize original-frame corners, local guides and separate confidences.

```python
from greekocr.glyphs.oriented_page import OrientedWord
record = word.to_record(image.size, (page_width, page_height))
```

### `greekocr.glyphs.oriented_page.OrientedPage`

Legacy horizontal records plus independent local-frame words and evidence.

```python
from greekocr.glyphs.oriented_page import OrientedPage
page = OrientedPage(**measured_oriented_page)
```

### `greekocr.glyphs.oriented_page.oriented_page`

`def oriented_page(image: Image.Image, table_regions: Sequence[tuple[str, Sequence[float]]]=(), *, recognizer: _Recognizer | None=None, use_osd: bool=False, segmentation: Any=None, pieces: list | None=None, dominant: Orientation | None=None, discover: bool=True, supplement: bool=True) -> OrientedPage`

Discover directions, normalize groups, fit, split and inverse-map words.

```python
from greekocr.glyphs.oriented_page import oriented_page
page = oriented_page(image, table_regions, recognizer=recognizer)
```

### `greekocr.glyphs.page_lines.PageTextLine`

```python
from greekocr.glyphs.page_lines import PageTextLine
lines = page_lines(page, boxes)  # list[PageTextLine]
```

### `greekocr.glyphs.page_lines.page_lines`

`def page_lines(page: Image.Image | NDArray[Any], boxes: list[tuple[int, int, int, int]], *, margin: float=0.25) -> list[PageTextLine]`

```python
from greekocr.glyphs.page_lines import page_lines
lines = page_lines(page, boxes, margin=0.25)
```

### `greekocr.glyphs.readability.Readability`

```python
from greekocr.glyphs.readability import Readability
verdict = readability(Image.open("crop.png"))
```

### `greekocr.glyphs.readability.readability`

`def readability(crop: Image.Image, *, xh_prior: float | None=None, limits: dict[str, float | None]=LIMITS) -> Readability`

Verdict and reasons for one crop under a reader's limits (READER_LIMITS['cllg'] by default).

```python
from greekocr.glyphs.readability import readability
verdict = readability(Image.open("crop.png"), xh_prior=None, limits=READER_LIMITS["cllg"])
```

### `greekocr.glyphs.recut.LineFit`

One text line fitted on a text-layer box, in page coordinates.

```python
from greekocr.glyphs.recut import LineFit
fits = fit_box(gray_page, (x0, y0, x1, y1))  # list[LineFit]
```

### `greekocr.glyphs.recut.LineFit.base_at`

`def base_at(self, xs: NDArray[np.float64]) -> NDArray[np.float64]`

Baseline at page columns xs; linear continuation with the end slopes beyond the fitted range.

```python
from greekocr.glyphs.recut import LineFit
rows = fit.base_at(np.arange(x0, x1, dtype=float))
```

### `greekocr.glyphs.recut.Recut`

```python
from greekocr.glyphs.recut import Recut
lines = recut_lines(page, (x0, y0, x1, y1))  # list[Recut]
```

### `greekocr.glyphs.recut.PageLine`

A line of the page after fix_page.

```python
from greekocr.glyphs.recut import PageLine
lines = fix_page(page, boxes)  # list[PageLine]
```

### `greekocr.glyphs.recut.fit_box`

`def fit_box(gray: NDArray[np.float64], box: tuple[int, int, int, int], xh_prior: float | None=None, *, box_index: int=-1, splits: bool=True, fit_rows: tuple[int, int] | None=None) -> list[LineFit]`

Step 1–2 for one box: the box's own line per column segment ('main'), and — when `splits` — every other full

```python
from greekocr.glyphs.recut import fit_box
fits = fit_box(gray_page, (x0, y0, x1, y1), xh_prior=None)
```

### `greekocr.glyphs.recut.fix_page`

`def fix_page(page: Image.Image | NDArray[Any], boxes: list[tuple[int, int, int, int]], *, only: set[int] | None=None, xh_prior: float | None=None, margin: float=0.25, mode: str='curve', separator: str='voronoi') -> list[PageLine]`

The whole-page operation (module docstring): every text-layer box of a page in, every text line out.

```python
from greekocr.glyphs.recut import fix_page
lines = fix_page(page, boxes, only=None, margin=0.25, mode="curve")
```

### `greekocr.glyphs.recut.recut_lines`

`def recut_lines(page: Image.Image | NDArray[Any], box: tuple[int, int, int, int], *, mode: str='curve', margin: float=0.25, extend: bool=True, isolate: bool=True, xh_prior: float | None=None, neighbours: list[LineFit] | None=None, pitch_xh: float | None=None, page_xh: float | None=None) -> list[Recut]`

One box on its own: one Recut per column segment's main line (no page context unless `neighbours` given).

```python
from greekocr.glyphs.recut import recut_lines
lines = recut_lines(page, (x0, y0, x1, y1), mode="curve", margin=0.25)
```

### `greekocr.glyphs.recut.recut_page`

`def recut_page(page: Image.Image | NDArray[Any], boxes: list[tuple[int, int, int, int]], *, only: set[int] | None=None, **kw: Any) -> list[list[Recut]]`

Per box, the Recuts of its lines from fix_page (main lines first, then split lines).

```python
from greekocr.glyphs.recut import recut_page
per_box = recut_page(page, [(x0, y0, x1, y1), ...], mode="curve")
```

### `greekocr.glyphs.report.document_of`

`def document_of(name: str) -> str | None`

```python
from greekocr.glyphs.report import document_of
document = document_of("s2-60f24a3d8a2d714767f2-p00003-l00024.png")
```

### `greekocr.glyphs.report.clipped_fraction`

`def clipped_fraction(glyphs: LineGlyphs) -> float`

Share of letter boxes whose ink touches the top or bottom crop edge.

```python
from greekocr.glyphs.report import clipped_fraction
share = clipped_fraction(line_glyphs(Image.open("crop.png")))
```

### `greekocr.glyphs.report.document_priors`

`def document_priors(paths: Iterable[PathLike]) -> dict[str, dict[str, float]]`

Median x-height per document over its complete crops: {document: {'xh': .., 'n': ..}}.

```python
from greekocr.glyphs.report import document_priors
priors = document_priors(["crops/a.png", "crops/b.png"])
```

### `greekocr.glyphs.report.line_record`

`def line_record(path: PathLike, *, priors: Mapping[str, Mapping[str, float]] | None=None, label: str='', step: int=4) -> dict[str, Any]`

JSON-ready record of a crop: one entry per column segment (columns split at rules / unaligned wide gaps), each

```python
from greekocr.glyphs.report import line_record
record = line_record("crop.png", priors=priors)
```

### `greekocr.glyphs.synthetic.UnsupportedText`

The font cannot draw every character of the requested text.

```python
from greekocr.glyphs.synthetic import UnsupportedText
error = UnsupportedText("font cannot draw ᾿")
```

### `greekocr.glyphs.synthetic.TruthGlyph`

```python
from greekocr.glyphs.synthetic import TruthGlyph
glyph = render_truth_line("ἀνδρώας", "GFSDidot-Regular.ttf").glyphs[0]
```

### `greekocr.glyphs.synthetic.Rendered`

```python
from greekocr.glyphs.synthetic import Rendered
rendered = render_truth_line("ἀνδρώας", "GFSDidot-Regular.ttf", degrade=False)
```

### `greekocr.glyphs.synthetic.Rendered.visible`

`def visible(self, fraction: float=0.25) -> NDArray[np.bool_]`

Pixels at least `fraction` of the way from paper tone to ink tone in the noise-free scan.

```python
from greekocr.glyphs.synthetic import Rendered
seen = rendered.visible(.25)
```

### `greekocr.glyphs.synthetic.font_covers`

`def font_covers(path: PathLike, text: str) -> tuple[bool, str]`

Every grapheme of `text` renders, differs from .notdef, and keeps its marks.

```python
from greekocr.glyphs.synthetic import font_covers
ok, reason = font_covers("GFSDidot-Regular.ttf", "ἀνδρώας")
```

### `greekocr.glyphs.synthetic.font_supports_polytonic`

`def font_supports_polytonic(path: PathLike, size: int=48) -> tuple[bool, str]`

Gate on a fixed polytonic probe (incl. spacing breathings); per-text coverage is enforced at render time.

```python
from greekocr.glyphs.synthetic import font_supports_polytonic
ok, reason = font_supports_polytonic("GFSDidot-Regular.ttf")
```

### `greekocr.glyphs.synthetic.render_truth_line`

`def render_truth_line(text: str, font_path: PathLike, *, size: int=40, rng: random.Random | None=None, degrade: bool=True, pad: int | None=None, neighbours: tuple[str, str] | None=None, ink_defects: Sequence[tuple[float, float, str, float]]=(), bend: tuple[str, float, float] | None=None, second_line: str | None=None) -> Rendered`

Render `text` with per-pixel truth and an optional randomised scan model (skew ±2°, blur, ink gain, noise).

```python
from greekocr.glyphs.synthetic import render_truth_line
rendered = render_truth_line("ἀνδρώας κύστεως", "GFSDidot-Regular.ttf", size=40, bend=("left", -1.0, .3))
```

### `greekocr.glyphs.synthetic.usable_fonts`

`def usable_fonts(paths: Sequence[PathLike]) -> tuple[list[Path], dict[str, str]]`

```python
from greekocr.glyphs.synthetic import usable_fonts
fonts, rejected = usable_fonts(["GFSDidot-Regular.ttf", "XCharter-Regular.otf"])
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

### `greekocr.pages.api.process_page`

`def process_page(image: PageImage, *, options: PageOptions=PageOptions(), page_key: str | None=None, book_id: str | None=None, table_regions: TableRegions | None=None, layout_provider: LayoutProvider | None=None, page_size: Sequence[float] | None=None, recognizer: Any=None) -> PageResult`

Analyse one raster; optional layout, orientation, joining, statistics and files.

```python
from greekocr.pages.api import process_page
result = process_page(image, options=PageOptions(statistics=True))
```

### `greekocr.pages.api.process_book`

`def process_book(pages: Iterable[PageImage | PageResult], *, book_id: str, options: PageOptions=PageOptions(), table_regions: Mapping[str, TableRegions] | None=None, layout_provider: LayoutProvider | None=None, page_size: Sequence[float] | None=None, recognizer: Any=None) -> BookResult`

Process ordered pages, then apply Q2 leave-one-page-out book statistics.

```python
from greekocr.pages.api import process_book
result = process_book(page_images, book_id="book-1", options=PageOptions(statistics=True))
```

### `greekocr.pages.lines.LineSegment`

One printed line; all curves use page pixel coordinates, x1 exclusive.

```python
from greekocr.pages.lines import LineSegment
line = LineSegment(**measured_line_geometry)
```

### `greekocr.pages.lines.LineSegment.unroll`

`def unroll(self, page: Image.Image | NDArray[Any], *, xheight: int=32) -> Image.Image`

Return a grayscale strip with meanline at 1.5 and baseline at 2.5 x-heights.

```python
from greekocr.pages.lines import LineSegment
image = line.unroll(page_image, xheight=32)
```

### `greekocr.pages.lines.LineSegment.to_record`

`def to_record(self) -> dict`

JSON-ready review record, including the once-built neighbour graph.

```python
from greekocr.pages.lines import LineSegment
record = line.to_record()
```

### `greekocr.pages.lines.PageSegmentation`

Final lines and their pixel-segment provenance, with measurable diagnostics.

```python
from greekocr.pages.lines import PageSegmentation
result = PageSegmentation(**measured_page_geometry)
```

### `greekocr.pages.lines.segment_page`

`def segment_page(page: Image.Image | NDArray[Any], hints: Sequence[Sequence[float]] | None=None) -> PageSegmentation`

Analyse pixels and return rough segments, final lines, and diagnostic counts.

```python
from greekocr.pages.lines import segment_page
result = segment_page(page_image, hints=None)
```

### `greekocr.pages.lines.page_line_segments`

`def page_line_segments(page: Image.Image | NDArray[Any], hints: Sequence[Sequence[float]] | None=None) -> list[LineSegment]`

Return one curved segment per detected printed line, starting from pixels.

```python
from greekocr.pages.lines import page_line_segments
lines = page_line_segments(page_image, hints=None)
```

### `greekocr.pages.lines.extract_line_image`

`def extract_line_image(page: Image.Image | NDArray[Any], line: LineSegment, *, xheight: int=32) -> Image.Image`

Unroll raw pixels within the tessellated boundary at a fixed x-height position.

```python
from greekocr.pages.lines import extract_line_image
image = extract_line_image(page_image, line, xheight=32)
```

### `greekocr.pages.options.OutputOptions`

Files to write; no directory means an in-memory call with no file writes.

```python
from greekocr.pages.options import OutputOptions
outputs = OutputOptions("page-output", frozenset({"lines", "structure", "cells"}))
```

### `greekocr.pages.options.PageOptions`

Pipeline switches; defaults preserve ordinary Q2 page delivery.

```python
from greekocr.pages.options import PageOptions
options = PageOptions(tables=True, join_lines=True, granularity="rows", statistics=True)
```

### `greekocr.pages.records.PageResult`

One input image, its physical leaves, addresses, delivery and measurements.

```python
from greekocr.pages.records import PageResult
result = PageResult(**measured_page_result)
```

### `greekocr.pages.records.PageResult.to_records`

`def to_records(self) -> dict[str, Any]`

Return the current geometry file payloads without rounding or refitting.

```python
from greekocr.pages.records import PageResult
records = result.to_records()
```

### `greekocr.pages.records.BookResult`

Ordered page results plus Q2 book and corpus summaries when requested.

```python
from greekocr.pages.records import BookResult
result = BookResult(book_id="book-1", pages=page_results)
```

### `greekocr.pages.statistics.page_statistics`

`def page_statistics(image: Image.Image | np.ndarray, lines: Sequence[dict[str, Any]], *, page_key: str, book_id: str | None=None, structure: dict[str, Any] | None=None) -> dict[str, Any]`

Measure a page using Q1 line records, returning `glyphs` and JSON-ready `stats`; inputs are never mutated.

```python
from greekocr.pages.statistics import page_statistics
result = page_statistics(image, q1_line_records, page_key="page-1", book_id="book-1", structure=q1_structure)
```

### `greekocr.pages.statistics.book_statistics`

`def book_statistics(pages: Sequence[dict[str, Any]], *, book_id: str) -> dict[str, Any]`

Return book aggregates and copied page tables enriched with independent, leave-one-page-out references.

```python
from greekocr.pages.statistics import book_statistics
book = book_statistics(measured_pages, book_id="book-1")
```

### `greekocr.pages.statistics.corpus_statistics`

`def corpus_statistics(pages: Sequence[dict[str, Any]]) -> dict[str, Any]`

Return the page summary table and explicitly page- and glyph-weighted descriptive readability scores.

```python
from greekocr.pages.statistics import corpus_statistics
corpus = corpus_statistics(measured_pages)
```

### `greekocr.pages.statistics.write_statistics`

`def write_statistics(result: dict[str, Any], directory: str | Path) -> dict[str, str]`

Write a page's glyph Parquet (JSONL without pyarrow) and stats JSON; never write Q1 geometry.

```python
from greekocr.pages.statistics import write_statistics
paths = write_statistics(result, "statistics-output")
```

### `greekocr.pages.statistics.render_glyph_statistics`

`def render_glyph_statistics(image: Image.Image, result: dict[str, Any]) -> Image.Image`

Return a source-size glyph overlay: green intact, orange under, red over, cyan show-through, violet stamp.

```python
from greekocr.pages.statistics import render_glyph_statistics
overlay = render_glyph_statistics(image, result)
```

### `greekocr.pages.statistics.render_book_statistics`

`def render_book_statistics(stats: dict[str, Any]) -> Image.Image`

Draw per-page size, contrast, coverage, candidate ink and readability traces with explicit scales.

```python
from greekocr.pages.statistics import render_book_statistics
figure = render_book_statistics(book["stats"])
```

### `greekocr.pages.structure.build_structure`

`def build_structure(lines: list[dict], pieces: list[dict], image_size: Sequence[int], *, gutters: Sequence=(), rules: Sequence[dict]=(), boundaries: Sequence[dict]=(), fold: dict | bool | None=None, page: Image.Image | np.ndarray | None=None) -> dict`

Add addresses to line/cell records in place without changing geometry.

```python
from greekocr.pages.structure import build_structure
structure = build_structure(line_records, cell_records, image.size, gutters=detected_gutters, rules=detected_rules, page=image)
```

### `greekocr.pages.structure.join_pieces`

`def join_pieces(pieces: Sequence[dict], *, structure: dict) -> dict`

Join one addressed row, rejecting mixed addresses and boundary crossings.

```python
from greekocr.pages.structure import join_pieces
row = join_pieces(addressed_row_pieces, structure=structure)
```

### `greekocr.pages.structure.delivery_records`

`def delivery_records(lines: Sequence[dict], *, structure: dict, granularity: str='default') -> list[dict]`

Return whole ordinary rows and table pieces; optionally all rows or pieces.

```python
from greekocr.pages.structure import delivery_records
records = delivery_records(line_records, structure=structure, granularity="default")
```

### `greekocr.pages.structure.joining_result`

`def joining_result(lines: Sequence[dict], *, structure: dict, pieces: Sequence[dict]=(), granularity: str='default') -> dict`

Q1b partial delivery: annotate safety and retain every refused row.

```python
from greekocr.pages.structure import joining_result
result = joining_result(line_records, structure=structure, pieces=cell_records, granularity="rows")
```

### `greekocr.pages.structure.render_structure`

`def render_structure(page: Image.Image, lines: Sequence[dict], structure: dict) -> Image.Image`

Draw row colours, piece order, finite column boundaries and the fold.

```python
from greekocr.pages.structure import render_structure
overlay = render_structure(image, line_records, structure)
```

### `greekocr.pages.tables.TextPiece`

A recognition crop and its tight TOPLEFT envelope in original pixels.

```python
from greekocr.pages.tables import TextPiece
piece = TextPiece((10, 20, 80, 45), 0, detected_line, "table-0", "piece-0")
```

### `greekocr.pages.tables.TextPiece.to_record`

`def to_record(self, index: int, image_size: Sequence[int], page_size: Sequence[float]) -> dict`

Serialize pixel and page-unit boxes using the actual image/page ratios.

```python
from greekocr.pages.tables import TextPiece
record = piece.to_record(0, image.size, (page_width, page_height))
```

### `greekocr.pages.tables.table_text_pieces`

`def table_text_pieces(page: Image.Image | NDArray[Any], region: Sequence[float], table_id: str='table-0', table_index: int=0) -> list[TextPiece]`

Return pixel-derived within-row pieces for an image-layout table region.

```python
from greekocr.pages.tables import table_text_pieces
pieces = table_text_pieces(image, (10, 20, 800, 900))
```

### `greekocr.pages.tables.recognition_pieces`

`def recognition_pieces(page: Image.Image | NDArray[Any], lines: list[LineSegment], table_regions: Sequence[tuple[str, Sequence[float]]]=(), *, supplement: bool=True) -> tuple[list[TextPiece], list, PageSegmentation | None]`

Shared delivery path for the plugin and offline review harness.

```python
from greekocr.pages.tables import recognition_pieces
pieces, regions, prefix = recognition_pieces(image, detected_lines, image_layout_regions)
```

### `greekocr.pages.tables.prepare_delivery`

`def prepare_delivery(page: Image.Image | NDArray[Any], result: PageSegmentation, table_regions: Sequence[tuple[str, Sequence[float]]]=(), *, supplement: bool=True) -> tuple[PageSegmentation, list[TextPiece], list]`

Attach table recovery to a normal segmentation, retaining audit candidates.

```python
from greekocr.pages.tables import prepare_delivery
result, pieces, regions = prepare_delivery(image, segmentation, image_layout_regions)
```

### `greekocr.readers.cllg.load_cllg`

`def load_cllg(spec: Record) -> Reader`

```python
from greekocr.readers.cllg import load_cllg
reader = load_cllg({"checkpoint":"ppocr_v6_tau090.safetensors", "readme":"README.md", "contract":"readme_contract.json"})
```

### `greekocr.readers.cllg.load_cllg_worker`

`def load_cllg_worker(checkpoint: PathLike, contract: Record | None=None, *, python: PathLike | None=None, timeout: float=300, confidence: bool=False) -> BatchReader | ConfidenceBatchReader`

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

### `greekocr.readers.services.docai_driver.summarize_run`

`def summarize_run(manifest: list[dict], predictions: list[dict], ledger: list[dict], repeat: int) -> dict`

```python
from greekocr.readers.services.docai_driver import summarize_run
summary = summarize_run(frozen_manifest_rows, prediction_rows, ledger_rows, repeat=2)
```

### `greekocr.readers.services.docai_driver.run_manifest`

`def run_manifest(manifest: str | Path, out: str | Path, *, reader: DocAIReader | None=None, fresh: bool=False, repeat: int=1, concurrency: int=4, max_cost_usd: float=10.0, **reader_options: object) -> dict`

```python
from greekocr.readers.services.docai_driver import run_manifest
summary = run_manifest("docai_manifest.jsonl", "docai_run", project="project", location="eu", processor_id="processor")
```

### `greekocr.readers.services.docai_manifest.build_polytondb_manifest`

`def build_polytondb_manifest(root: str | Path) -> list[dict]`

```python
from greekocr.readers.services.docai_manifest import build_polytondb_manifest
rows = build_polytondb_manifest("tests/fixtures/polytondb_gold300")
```

### `greekocr.readers.services.docai_manifest.build_o4d_manifest`

`def build_o4d_manifest(root: str | Path, *, sample: bool=False) -> list[dict]`

```python
from greekocr.readers.services.docai_manifest import build_o4d_manifest
rows = build_o4d_manifest("tests/fixtures/o4d_lines")
```

### `greekocr.readers.services.docai_manifest.build_borndigital_manifest`

`def build_borndigital_manifest(root: str | Path) -> list[dict]`

```python
from greekocr.readers.services.docai_manifest import build_borndigital_manifest
rows = build_borndigital_manifest("tests/fixtures/borndigital100")
```

### `greekocr.readers.services.docai_manifest.build_manifest`

`def build_manifest(fixtures_root: str | Path, out: str | Path, *, cohorts: Sequence[str]=DEFAULT_COHORTS) -> dict`

```python
from greekocr.readers.services.docai_manifest import build_manifest
receipt = build_manifest("tests/fixtures", "docai_manifest.jsonl")
```

### `greekocr.readers.services.docai_manifest.load_manifest`

`def load_manifest(path: str | Path) -> list[dict]`

```python
from greekocr.readers.services.docai_manifest import load_manifest
rows = load_manifest("docai_manifest.jsonl")
```

### `greekocr.readers.services.google_docai.Reading`

```python
from greekocr.readers.services.google_docai import Reading
reading = Reading(**recorded_reading_values)
```

### `greekocr.readers.services.google_docai.DocAIError`

A service failure, with its response retained when available.

```python
from greekocr.readers.services.google_docai import DocAIError
error = DocAIError("recorded service failure")
```

### `greekocr.readers.services.google_docai.DocAIReader`

```python
from greekocr.readers.services.google_docai import DocAIReader
reader = DocAIReader("project", "eu", "processor", version="pretrained-ocr-v2.1-2024-08-07")
```

### `greekocr.readers.services.google_docai.DocAIReader.binding`

`def binding(self) -> dict`

Return a new deterministic JSON object; None version means unpinned default.

```python
from greekocr.readers.services.google_docai import DocAIReader
provenance = reader.binding()
```

### `greekocr.readers.services.google_docai.DocAIReader.read`

`def read(self, path: str | Path, *, fresh: bool | None=None, expected_sha256: str | None=None) -> Reading`

```python
from greekocr.readers.services.google_docai import DocAIReader
reading = reader.read("crop.png")
```

### `greekocr.readers.services.google_docai.DocAIReader.read_batch`

`def read_batch(self, paths: Iterable[str | Path], concurrency: int=4, *, fresh: bool | None=None) -> list[Reading]`

```python
from greekocr.readers.services.google_docai import DocAIReader
readings = reader.read_batch(["crop.png"], concurrency=4)
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

`def refine_line(page_image: Image.Image, box: Box, *, pad: int=DEFAULT_PAD, policy: GeometryPolicy='v3') -> LineCrop`

Rectify a local line; v1/v2 preserve historical crop behavior for comparison.

```python
from greekocr.real.geometry import refine_line
crop = refine_line(image, (10, 20, 800, 70), pad=16)
```

### `greekocr.real.geometry.crop_quality`

`def crop_quality(original_crop: Image.Image, refined_crop: Image.Image, diagnostics: GeometryDiagnostics | Mapping[str, Any]) -> dict[str, Any]`

Measure pixel-only crop signals using recorded page-to-strip geometry.

```python
from greekocr.real.geometry import crop_quality
quality = crop_quality(original_crop, refined_crop, geometry_receipt)
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

`def refine_page_lines(pdf_page_image: Image.Image, text_layer_boxes: Sequence[TextLayerBox | Box | Mapping[str, Any]], *, pad: int=DEFAULT_PAD, policy: GeometryPolicy='v3') -> list[LineCrop]`

Refine pixel boxes in input order; split labels are withheld for caller assignment.

```python
from greekocr.real.geometry import refine_page_lines
crops = refine_page_lines(image, text_layer_boxes, pad=16)
```

### `greekocr.real.geometry_evaluate.inter_reader_cer`

`def inter_reader_cer(first: str, second: str) -> float`

Symmetric NFD codepoint CER, distance / max(lengths, 1); zero is agreement.

```python
from greekocr.real.geometry_evaluate import inter_reader_cer
cer = inter_reader_cer("ἅλφα", "άλφα")
```

### `greekocr.real.geometry_evaluate.evaluate_geometry`

`def evaluate_geometry(records: PathLike | Sequence[Mapping[str, Any]], *, page_images: PathLike | Mapping[str, PathLike] | None=None, policies: Sequence[str]=POLICIES, readers: Mapping[str, EvaluationReader], out: PathLike, pad: int=DEFAULT_PAD, blind_seed: int=0) -> dict[str, Any]`

Save every policy crop, pixel/reader evidence, summaries and a blind A/B page.

```python
from greekocr.real.geometry_evaluate import evaluate_geometry
receipt = evaluate_geometry("records.jsonl", readers=reader_hooks, out="geometry-evaluation")
```

### `greekocr.real.geometry_measure.comparison_scores`

`def comparison_scores(text: str, old: str, new: str) -> dict[str, Any]`

Replay historical layer-agreement diagnostics, never reference accuracy.

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

### `greekocr.real.sources.web_render.PageRecord`

Capture receipt and absolute artifact paths (None for failed captures).

```python
from greekocr.real.sources.web_render import PageRecord
page = PageRecord(page_id, html_path, pdf_path, png_path, dom_path, print_dom_path, receipt_path, receipt)
```

### `greekocr.real.sources.web_render.render_pages`

`def render_pages(urls: Iterable[PathLike | Mapping[str, object]], out_dir: PathLike, *, viewport: tuple[int, int] | Mapping[str, int]=(794, 1123), scale: float=1.5, max_page_height: int=20000, print_to_pdf: bool=True, screenshot: bool=True, block_media: bool=True, licences: Mapping[str, str] | None=None, offline: bool=False, interval: float=1.0, timeout: float=30.0, client: _PoliteHTTP | None=None) -> list[PageRecord]`

Render pages with polite top-level navigation and a 2*timeout page watchdog.

```python
from greekocr.real.sources.web_render import render_pages
pages = render_pages(["fixture.html"], "rendered", viewport=(794,1123), scale=2, offline=True)
```

### `greekocr.real.sources.web_render.records_from_dom`

`def records_from_dom(png: PathLike, dom_lines: PathLike | Mapping[str, object] | Sequence[Record], *, receipt: Mapping[str, object] | None=None) -> list[Record]`

Return per-text-node fragments in screenshot pixels, preserving raw text.

```python
from greekocr.real.sources.web_render import records_from_dom
lines = records_from_dom("rendered/page.png", "rendered/dom.json")
```

### `greekocr.real.sources.web_render.records_from_pdf`

`def records_from_pdf(pdf_path: PathLike, *, dom_lines: PathLike | Mapping[str, object] | None=None, receipt: Mapping[str, object] | None=None, out_dir: PathLike | None=None, iou_threshold: float=0.5) -> list[Record]`

Use the vendored PDFium extractor and write an independent DOM agreement report.

```python
from greekocr.real.sources.web_render import records_from_pdf
lines = records_from_pdf("rendered/page.pdf")
```

### `greekocr.real.sources.web_render.degrade_twins`

`def degrade_twins(page_png: PathLike, labels: Sequence[Record], *, out_dir: PathLike | None=None, seed: int=0) -> Record`

Call a vendored degradation adapter if present, else report unavailable (no fake twin).

```python
from greekocr.real.sources.web_render import degrade_twins
result = degrade_twins("rendered/page.png", exact_line_records, seed=0)
```

### `greekocr.real.sources.web_render.page_records`

`def page_records(directory: PathLike) -> Record`

Verify capture hashes and extract all available screenshot/PDF records offline.

```python
from greekocr.real.sources.web_render import page_records
summary = page_records("rendered")
```

### `greekocr.real.sources.web_sources.source_catalog`

`def source_catalog() -> dict[str, Record]`

Return seed metadata with conservative licence tags and >=1 second rates.

```python
from greekocr.real.sources.web_sources import source_catalog
catalog = source_catalog()
```

### `greekocr.real.sources.web_sources.mastodon_post_html`

`def mastodon_post_html(post: Record) -> str`

Render recorded public JSON as inert post HTML, with author and source link.

```python
from greekocr.real.sources.web_sources import mastodon_post_html
html = mastodon_post_html(recorded_public_post_json)
```

### `greekocr.real.sources.web_sources.source_pages`

`def source_pages(sources: Sequence[str], max_pages: int=10, *, category: str | None=None, mastodon_instance: str='https://mastodon.social', client: _PoliteHTTP | None=None) -> Iterator[Record]`

Yield bounded seeds/articles; discovery fetches only when iteration needs it.

```python
from greekocr.real.sources.web_sources import source_pages
seeds = list(source_pages(["wikisource"], max_pages=1, category="Αρχαία ελληνική ποίηση"))
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

### `greekocr.verify.images.ImageChecks`

Line summaries. Units, sign conventions and provisional thresholds: docs/VERIFY.md.

```python
from greekocr.verify.images import ImageChecks
checks = ImageChecks(**measured_image_values)
```

### `greekocr.verify.images.ImageChecks.to_dict`

`def to_dict(self) -> dict`

```python
from greekocr.verify.images import ImageChecks
record = features.to_dict()
```

### `greekocr.verify.images.Profile`

Per-column functions; half-open segments and 16x64 quality, 1=good/0=bad.

```python
from greekocr.verify.images import Profile
profile = Profile(**measured_profile_values)
```

### `greekocr.verify.images.Profile.to_dict`

`def to_dict(self) -> dict[str, Any]`

```python
from greekocr.verify.images import Profile
record = features.to_dict()
```

### `greekocr.verify.images.readability_profile`

`def readability_profile(crop: Crop, *, threshold: float=0.55) -> Profile`

Bounded analysis grid, native border checks, original-coordinate functions.

```python
from greekocr.verify.images import readability_profile
profile = readability_profile("crop.png")
```

### `greekocr.verify.images.image_checks`

`def image_checks(crop: Crop) -> ImageChecks`

Return the scalar summaries of readability_profile, using the same analysis.

```python
from greekocr.verify.images import image_checks
checks = image_checks("crop.png")
```

### `greekocr.verify.images.render_overlay`

`def render_overlay(crop: Crop, profile: Profile) -> bytes`

Return PNG bytes: raster, translucent 2-D defects and half-open red segments.

```python
from greekocr.verify.images import render_overlay
png_bytes = render_overlay("crop.png", profile)
```

### `greekocr.verify.judges.vlm_annotate`

`def vlm_annotate(crops: Iterable[str | Path], *, model: str='gpt-6-luna', schema: dict=READABILITY_SCHEMA, batch_size: int=4, cache: str | Path | None=None, budget: CallBudget | None=None, receipts_dir: str | Path='docs/verify/receipts') -> list[dict]`

One-to-four independent numbered attachments per call; return JSON-ready rows.

```python
from greekocr.verify.judges import vlm_annotate
rows = vlm_annotate(["crop.png"], cache="readability_cache.jsonl")
```

### `greekocr.verify.judges.judge_texts`

`def judge_texts(texts: Iterable[str], *, model: str='gpt-6-luna', batch_size: int=4, cache: str | Path | None=None, budget: CallBudget | None=None, receipts_dir: str | Path='docs/verify/receipts') -> list[dict]`

Cached batches of at most four readings; the job reserves <=200 text calls.

```python
from greekocr.verify.judges import judge_texts
rows = judge_texts(["ἡ χώρα", "ὁ δήμος"], cache="text_cache.jsonl")
```

### `greekocr.verify.judges.llm_judge`

`def llm_judge(text: str, *, model: str='gpt-6-luna', cache: str | Path | None=None, budget: CallBudget | None=None, receipts_dir: str | Path='docs/verify/receipts') -> dict`

Return {good_greek, problems, receipt}; reusing a cache costs no invocation.

```python
from greekocr.verify.judges import llm_judge
judgement = llm_judge("ἡ χώρα", cache="text_cache.jsonl")
```

### `greekocr.verify.text.TextChecks`

All ratios/scores are 0..1; None means unavailable, not a negative result.

```python
from greekocr.verify.text import TextChecks
checks = TextChecks(**measured_text_values)
```

### `greekocr.verify.text.TextChecks.to_dict`

`def to_dict(self) -> dict`

```python
from greekocr.verify.text import TextChecks
record = features.to_dict()
```

### `greekocr.verify.text.text_checks`

`def text_checks(text: str) -> TextChecks`

Check normalized graphemes, not NFC-vs-NFD representation differences.

```python
from greekocr.verify.text import text_checks
checks = text_checks("ἡ χώρα")
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

## Failed-line Document AI audit (T10 prototype)

`prototypes.harvest.google_failed_lines` audits the R7 owner's crop catalogue before any harvest. It uses the existing `DocAIReader`, Greek hints and symbol output, excludes Anemi by both page ID and filename before adapter access, and binds response envelopes to image SHA-256 plus processor/options. Byte-identical crops reuse one request. No `.git` writes, crop straightening, held-out processing or training-data harvest are performed.

```sh
.venv/bin/python scripts/harvest/google_failed_lines.py
.venv/bin/python scripts/harvest/google_failed_lines.py --offline
```

Options: `--catalogue DIRECTORY`, `--out DIRECTORY`, `--offline`. Defaults are the supplied sibling `greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/failed_lines` catalogue and this repository's `docs/harvest`. Offline regeneration reads saved envelopes without ADC or network. A missing cache stops; it never silently calls Google.

- `load_catalogues(directory) -> list[dict]`: flatten the two JSON catalogues' `current_output_items`, validate paths, retain owner metadata, dimensions, SHA and withheld rows. Marked-region crops are excluded from calls.
- `derive_comment_crops(directory, rows, output) -> list[dict]`: bind explicit current-owner box numbers only when saved R6 item geometry and display order equal R7; intersect exact polygons and crop native grayscale pixels. Reuse existing catalogue items, preserve association and source hashes. Ambiguous historical/page-wide comments remain unmeasured.
- `crop_metrics(raw, width, height) -> dict`: actual layout-line count/text, line confidence, symbol confidence, empty flag, characters excluding CR/LF, characters per 100 image-width pixels, and raw Greek code-point set. If layout lines are absent the text-split fallback is labelled.
- `characters_table(rows) -> dict`: ALL and each present source, exact emitted code-point counts, requested historical-character observations, and NFD combining marks attached to Greek letters; deduplicate image SHA values.
- `cached_response(row, output, reader, offline=False) -> dict`: response envelope with raw response and hash, image hash, binding and adapter receipt. Never calls Anemi. Changed bindings/hashes or unresolved attempts fail closed. No fresh/retry option is exposed.
- `run(directory, out, offline=False, reader=None) -> dict`: sequential audit; durable attempt journal, adapter receipts/ledger, response envelopes, CSV/JSON metrics, character tables, per-type report, local-file-image review HTML and cost receipt. Stops on the first request error, including permission/billing errors, preserving a partial report.

Outputs: `DOCAI_FAILED_LINES_v1.md`, `docai_failed_lines_review.html`, and `docai_failed_lines/{responses,adapter_receipts,attempts,derived_crops,images,inventory.json,metrics.json,crops.csv,characters.csv,characters.json,summary.json,page_comment_coverage.json,receipt.json}`. Receipt cost is a base list-price estimate, not a billing statement. Confidence exposure thresholds are diagnostic and single-line silent candidates require visual confirmation against source geometry.

Validate the frozen v1 artifacts without network:

```sh
.venv/bin/python scripts/harvest/validate_google_failed_lines.py
```

The validator recomputes all crop metrics and character counts, verifies raw responses/image hashes/CSV IDs/cards/links and one API call per image SHA, and writes `docai_failed_lines/validation.json`. It checks responsive CSS constraints; it does not claim a rendered desktop/phone viewport check. Hash-bound manual observations are retained in `visual_findings.json` and shown on the corresponding cards.

## Cloud Vision service reader (T11)

Explicit opt-in and ADC; raw SHA-cached annotations plus NFD public text. See [READERS_VISION.md](READERS_VISION.md).

### `greekocr.readers.services.google_vision.VisionError`

A retained service failure; the same crop is never automatically retried.

```python
from greekocr.readers.services.google_vision import VisionError
error = VisionError("retained service refusal")
```

### `greekocr.readers.services.google_vision.VisionReading`

```python
from greekocr.readers.services.google_vision import VisionReading
reading = VisionReading(**recorded_vision_values)
```

### `greekocr.readers.services.google_vision.VisionReader`

Construct explicitly; ADC and requests are loaded only on a cache miss.

```python
from greekocr.readers.services.google_vision import VisionReader
reader = VisionReader("quota-project", language_hints=("el", "grc"))
```

### `greekocr.readers.services.google_vision.VisionReader.binding`

`def binding(self) -> dict[str, Any]`

Return defensive request settings, including hints and unpinned model.

```python
from greekocr.readers.services.google_vision import VisionReader
binding = reader.binding()
```

### `greekocr.readers.services.google_vision.VisionReader.read`

`def read(self, path: str | Path) -> str`

Return NFD text, retaining whitespace and all reported lines.

```python
from greekocr.readers.services.google_vision import VisionReader
text = reader.read("crop.png")
```

### `greekocr.readers.services.google_vision.VisionReader.read_annotation`

`def read_annotation(self, path: str | Path, *, expected_sha256: str | None=None) -> VisionReading`

Return full annotation, flattened hierarchy, confidence and receipt.

```python
from greekocr.readers.services.google_vision import VisionReader
reading = reader.read_annotation("crop.png")
```

### `greekocr.readers.services.google_vision.load_google_vision`

`def load_google_vision(*, enabled: bool=False, user_project: str | None=None, language_hints: Iterable[str]=('el', 'grc'), responses_dir: str | Path=DEFAULT_RESPONSES) -> VisionReader`

Factory gated by explicit opt-in or GREEKOCR_ENABLE_GOOGLE_VISION=1, then ADC.

```python
from greekocr.readers.services.google_vision import load_google_vision
reader = load_google_vision(enabled=True, user_project="quota-project")
```

### Failed-line engine comparison

```sh
python scripts/harvest/google_failed_lines.py --engine vision --include-anemi
python scripts/harvest/google_failed_lines.py --engine vision --include-anemi --offline
```

`--engine docai` remains the default. Vision accepts `--language-hints el grc` (the default); empty hints are possible with `--language-hints`. All responses bind the hints. `--out` is the parent report directory; data go into `<out>/vision_failed_lines/`, while comparison reads the existing `<out>/docai_failed_lines/` cache. No DocAI request is made for comparison. See [VISION_VS_DOCAI_v1.md](harvest/VISION_VS_DOCAI_v1.md).
