"""Dataset-card sections, with measured exactness and coverage read from receipts."""
import json
from pathlib import Path
import re


GENERATION_MARKER = '<!-- hfd-card-generation: {} -->'
GENERATION_RE = re.compile(r'<!-- hfd-card-generation: (v0\.\d+) -->')
RECIPE_RE = r'<!-- hfd-recipe:{} -->\n\n```python\n(.*?)\n```'
INTRO_END = '## Exactness of the frozen trained view'
JOINS_START = '## Layered joins and updates'
JOINS_END = '## Raw Google text and corrections'
CONFIG_DESCRIPTIONS = {
    'real': 'Frozen prepared005 real trainer rows and image bytes (default)',
    'synthetic': 'Frozen prepared005 train; identified source-build val/reserved if present',
    'lines': 'Real line inventory without image bytes or label text',
    'labels_current': 'Current label and label_version_id per row_key',
    'label_versions': 'Append-only raw, correction, release and trained labels',
    'current_features': 'Features for the current label version',
    'row_features': 'Append-only features by row and label version',
    'crops': 'Original crop bytes keyed by crop_sha256',
    'page_images': 'Original page raster bytes',
    'synthetic_lines': 'Synthetic occurrence metadata and provenance',
    'training_membership': 'Train/reference membership and trainer payload locators',
    'book_registry': 'Book registry and split assignments',
    'book_sources': 'Detailed source bibliography and exact-book locators',
    'reference_images': 'Appended reference image variants keyed by crop_sha256 (not original crops)',
}


def introduction(version, configs):
    text = GENERATION_MARKER.format(version) + '\n\n' + f'''A line-image dataset for **Greek OCR v0.10 (x1, x1.5 and x2)**. The line dataset
version is **{version}**. It covers Greek, both modern (monotonic) and polytonic;
Latin; Cyrillic; mixed Greek-Latin; numbers and page furniture.

The **frozen trained view** is the prepared005 rows the three models trained on,
including their held-out splits: the same image bytes, labels, codec, splits and
source pools. `data/real` and `data/synthetic/train` stay fixed as corrections
advance. Identified synthetic val/reserved splits are additional source-build
views, outside that frozen trained view. Current corrections live in separate
label tables. The frozen view is named separately from the evolving `main` branch.

## Load the dataset

```python
from datasets import load_dataset
repo = "fffoivos/greek-ocr-lines"
revision = "{version}"  # this card's generation tag; use this same revision throughout
real = load_dataset(repo, "real", revision=revision)  # default config, all real splits
synthetic = load_dataset(repo, "synthetic", revision=revision)
```

Every config loads independently; `load_dataset` and the HF viewer do not join
layers. Table and image configs use the `inventory` split. Available configs in
this build (use `load_dataset(repo, name, split=split, revision=revision)`):

| Config | Splits | Contents |
| --- | --- | --- |
'''
    for name, splits in sorted(configs.items()):
        text += f'| `{name}` | {", ".join(f"`{s}`" for s in splits)} | {CONFIG_DESCRIPTIONS.get(name, "Relational " + name.replace("_", " ") + " inventory")} |\n'
    return text + '\n'


def validate_a1(report):
    """Refuse a PASS claim from a failed, partial or internally inconsistent receipt."""
    files = report.get('files', [])
    if (report.get('status') != 'PASS' or report.get('errors') or not files
            or any(f.get('status') != 'PASS' or f.get('mismatch_count') != 0 for f in files)
            or not report.get('runtime_sha256')
            or report['runtime_sha256'] != report.get('expected_runtime_sha256')
            or not report.get('counts_per_split')
            or report['counts_per_split'] != report.get('public_counts_per_split')):
        raise ValueError('card requires a complete PASS A1.json receipt')
    return report


def exactness(root):
    path = Path(root) / 'manifests/A1.json'
    text = '## Exactness of the frozen trained view\n\n'
    if not path.is_file():
        return text + ('A1.json is not bound to this build; exactness counts are unavailable here. '
                       'Supply the coordinator\'s PASS receipt with `--a1-report` before publication.\n\n')
    report = validate_a1(json.loads(path.read_text()))
    mismatches = sum(f['mismatch_count'] for f in report['files'])
    text += (f'**A1 PASS:** {len(report["files"]):,} files, {len(report.get("errors", [])):,} errors, '
             f'{mismatches:,} mismatches. Prepared005 runtime SHA-256: '
             f'`{report["runtime_sha256"]}`. Public comparison revision: `{report["revision"]}`. '
             'Counts below are read from [A1.json](manifests/A1.json), not inferred from pool sizes.\n\n'
             '`data/real` and `data/synthetic/train` are exactly the prepared005 rows the three '
             'models trained on. A1 compares occurrences by pool, source shard and row ordinal, '
             'including ordered row identity and image bytes; missing, duplicated, extra or '
             'reordered occurrences fail. Licence-column removal and the byte-equivalent '
             'pool/image representation are the documented packaging differences.\n\n'
             '| Frozen split | Rows |\n| --- | ---: |\n')
    for split, rows in sorted(report['counts_per_split'].items()):
        text += f'| `{split}` | {rows:,} |\n'
    return text + '\n'


def training():
    return '''## Training use and selection roles

All three models used the same data and the same **0.5 real / 0.5 synthetic draw
share**: non_parliament 0.4639, parliament 0.0361, synthetic 0.5. The sampler seed
was **20261015**, with **8 epochs of 1,586,454 draws** and one shuffled permutation
of each real train pool per epoch. These are draw shares, not dataset row shares.
The sampler preparation seed is distinct from a model run's seed.

| Model | Batch size | Updates |
| --- | ---: | ---: |
| x1 | 256 | 49,584 |
| x1.5 | 256 | 49,584 |
| x2 | 64 | 198,312 |

Per-model update counts differ by batch size and are also given on the
[model card](https://huggingface.co/fffoivos/greek-ocr).
`trained_in` means **"in the train pool of"**; per-row draw counts remain null
without a keyed draw trace.

**seal04_dev selected checkpoints.** harvest_dev + seal04_dev (pooled dev)
selected Stage B hyperparameters. harvest_test and seal04_test are report-only.
**Test sets never selected anything.** seal04 retains diagnostic-only and
historical exposure caveats; edition isolation does not establish absence of
historical checkpoint exposure.

## Label quality

Astra's sample found **33/412 = 8%** of base-harvest labels not matching the print
(rounded). This is a sampled label limitation, not a segmentation score.
Labels transcribe what is printed, including misprints, rather than normalising
it to expected spelling.

'''


LOADER_DATASETS = """import json
from datasets import Image, load_dataset
from huggingface_hub import hf_hub_download

repo, revision = "fffoivos/greek-ocr-lines", "@VERSION@"


def load(name, split="inventory", columns=None, where=None):
    ds = load_dataset(repo, name, split=split, revision=revision)
    if where is not None:
        column, values = where[0], set(where[1])
        ds = ds.filter(lambda value: value in values, input_columns=column)
    if columns is not None:
        ds = ds.select_columns(columns)
    for column, feature in ds.features.items():
        if isinstance(feature, Image):
            ds = ds.cast_column(column, Image(decode=False))  # original bytes, no re-encoding
    return ds.to_pandas()


def read_json(path):
    with open(hf_hub_download(repo, path, repo_type="dataset", revision=revision)) as stream:
        return json.load(stream)"""

LOADER_PYARROW = """import json
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
import yaml

# root = Path(huggingface_hub.snapshot_download(repo, repo_type="dataset", revision=revision))
card_yaml = yaml.safe_load((root / "README.md").read_text(encoding="utf-8").split("---", 2)[1])
declared = {c["config_name"]: {f["split"]: [f["path"]] if isinstance(f["path"], str) else f["path"]
                               for f in c["data_files"]} for c in card_yaml["configs"]}


def load(name, split="inventory", columns=None, where=None):
    filters = None if where is None else [(where[0], "in", list(where[1]))]
    tables = [pq.read_table(root / path, columns=columns, filters=filters)
              for path in declared[name][split]]
    return pa.concat_tables(tables).to_pandas()  # one schema per declared config/split


def read_json(path):
    return json.loads((root / path).read_text(encoding="utf-8"))"""

RECIPE_JOIN = """import hashlib
import pandas as pd

manifest = read_json("manifests/MANIFEST.json")
configs = read_json("manifests/CONFIGS.json")
occurrence = {o["public_path"]: o for o in manifest["frozen_trained"]["occurrence_mapping"]}
OCC = ["pool", "source_shard", "source_ordinal"]

members = load("training_membership", columns=[
    "membership_id", "model_id", "role", "selection_role", "pool", "source_shard", "source_ordinal",
    "trainer_line_id", "row_key", "gt_nfc", "synthetic_key", "synthetic_match_group",
    "synthetic_mapping_status", "synthetic_candidate_count"])
MODEL = sorted(members["model_id"].dropna().unique())[0]  # x1, x1.5 and x2 share prepared005 rows
members = members[members["model_id"] == MODEL].drop(columns="model_id")
assert not members.duplicated(OCC).any(), "one membership per prepared occurrence"


def frozen_occurrences(config):
    # Frozen rows in published file order, each tagged with its prepared005 occurrence.
    frames = []
    for split, paths in configs[config].items():
        frozen = [path in occurrence for path in paths]
        if not any(frozen):
            continue  # identified synthetic val/reserved views are outside the trained view
        assert all(frozen), (config, split)
        rows = load(config, split, columns=["line_id", "gt_nfc"])
        sizes = [occurrence[path]["rows"] for path in paths]
        assert len(rows) == sum(sizes), (config, split)
        rows["hf_split"] = split
        rows["pool"] = [occurrence[p]["pool"] for p, n in zip(paths, sizes) for _ in range(n)]
        rows["source_shard"] = [occurrence[p]["prepared_path"] for p, n in zip(paths, sizes) for _ in range(n)]
        rows["source_ordinal"] = [i for n in sizes for i in range(n)]
        frames.append(rows)
    return pd.concat(frames, ignore_index=True)


def with_membership(frozen):
    joined = frozen.merge(members, on=OCC, how="left", validate="one_to_one",
                          suffixes=("_frozen", ""), indicator=True)
    assert (joined.pop("_merge") == "both").all(), "frozen occurrence without membership"
    assert (joined["line_id"] == joined["trainer_line_id"]).all(), "trainer line id differs"
    assert (joined["gt_nfc_frozen"] == joined["gt_nfc"]).all(), "trainer label differs"
    return joined.drop(columns="gt_nfc_frozen")


# Every real observation (trainer_line_id may be null) -> current label -> current features.
lines = load("lines", columns=["row_key", "trainer_line_id", "book_id", "split",
                               "crop_sha256", "original_custody"])
labels = load("labels_current", columns=["row_key", "label_version_id", "label_variant",
                                         "text", "text_sha256"])
features = load("current_features").drop(columns=["label_variant"])
assert lines["row_key"].is_unique and labels["row_key"].is_unique and features["row_key"].is_unique
current = lines.merge(labels, on="row_key", how="left", validate="one_to_one", indicator=True)
assert (current.pop("_merge") == "both").all(), "line without current label"
current = current.merge(features, on="row_key", how="left", validate="one_to_one",
                        suffixes=("", "_feature"), indicator=True)
has_text = current["text"].notna()
assert (current.pop("_merge")[has_text] == "both").all(), "current label without features"
assert (current.loc[has_text, "label_version_id_feature"] == current.loc[has_text, "label_version_id"]).all()
assert (current.loc[has_text, "label_sha256"] == current.loc[has_text, "text_sha256"]).all()

# Original crops by content hash; every verified original crop is published.
crop_index = load("crops", columns=["crop_sha256"])
verified = current["original_custody"].notna()
assert crop_index["crop_sha256"].is_unique
assert current.loc[verified, "crop_sha256"].isin(crop_index["crop_sha256"]).all(), "verified crop missing"
wanted = sorted(set(current.loc[verified, "crop_sha256"]))[:4]
if wanted:
    crops = load("crops", columns=["crop_sha256", "image"], where=("crop_sha256", wanted))
    crops = crops.set_index("crop_sha256")
    for h in wanted:
        assert hashlib.sha256(crops.loc[h, "image"]["bytes"]).hexdigest() == h  # original bytes

# Real trained view: occurrence -> one model's membership -> metadata by row_key.
real = with_membership(frozen_occurrences("real"))
assert real["row_key"].notna().all()
assert len(real) == int(members["row_key"].notna().sum()), "membership without frozen occurrence"
real = real.merge(current, on="row_key", how="left", validate="many_to_one",
                  suffixes=("", "_line"), indicator=True)
assert (real.pop("_merge") == "both").all(), "trainer occurrence without line metadata"

# Synthetic trained view: occurrence -> membership -> synthetic_lines by synthetic_key; for
# indistinguishable identical observations the key is null and every candidate is listed.
meta = load("synthetic_lines", columns=[
    "synthetic_key", "synthetic_match_group", "factory_build_id", "split", "line_id",
    "reuse_index", "gt_nfc", "image_sha256", "font", "severity", "applied_ops"])
assert meta["synthetic_key"].is_unique
synthetic = with_membership(frozen_occurrences("synthetic"))
assert synthetic["synthetic_match_group"].notna().all()
assert len(synthetic) == int(members["synthetic_match_group"].notna().sum())
unique = synthetic["synthetic_mapping_status"] == "unique_exact"
exact = synthetic[unique].merge(
    meta.drop(columns=["synthetic_match_group", "line_id", "gt_nfc"]), on="synthetic_key",
    how="left", validate="many_to_one", indicator=True)
assert (exact.pop("_merge") == "both").all(), "synthetic occurrence without metadata"
ambiguous = synthetic[~unique].copy()
assert (ambiguous["synthetic_mapping_status"] == "ambiguous_identical_observations").all()
candidates = meta.groupby("synthetic_match_group")["synthetic_key"].agg(sorted)
ambiguous["synthetic_key_candidates"] = ambiguous["synthetic_match_group"].map(candidates)
assert ambiguous["synthetic_key_candidates"].notna().all()
assert (ambiguous["synthetic_key_candidates"].map(len) == ambiguous["synthetic_candidate_count"]).all()
synthetic = pd.concat([exact, ambiguous], ignore_index=True)

# Identified synthetic val/reserved views: published in synthetic_key order.
views = {}
for split, paths in configs.get("synthetic", {}).items():
    if any(path in occurrence for path in paths):
        continue
    view = load("synthetic", split)
    keyed = meta[meta["split"] == split].sort_values("synthetic_key", ignore_index=True)
    assert len(view) == len(keyed), split
    if "synthetic_key" not in view.columns:
        view["synthetic_key"] = keyed["synthetic_key"]
    image_sha256 = view["image"].map(lambda image: hashlib.sha256(image["bytes"]).hexdigest())
    assert (view["synthetic_key"] == keyed["synthetic_key"]).all(), split
    assert (image_sha256 == keyed["image_sha256"]).all(), split
    assert (view["line_id"] == keyed["line_id"]).all() and (view["gt_nfc"] == keyed["gt_nfc"]).all(), split
    views[split] = view.drop(columns=["image"])[["synthetic_key"]].merge(
        meta, on="synthetic_key", how="left", validate="one_to_one")"""


def recipe_blocks(text):
    """The literal card recipe code blocks, each published exactly once."""
    blocks = {}
    for name in ('loader-datasets', 'loader-pyarrow', 'join'):
        found = re.findall(RECIPE_RE.format(name), text, flags=re.S)
        if len(found) != 1:
            raise ValueError('card recipe block missing or duplicated: ' + name)
        blocks[name] = found[0]
    return blocks


def joins(version):
    return (JOINS_START + '''

HF loading and the viewer do not join layers. The recipe below reconstructs the
trained view and all real observations, asserting cardinality and complete
matching at every step. It needs `pandas` and `pyarrow`. Define
`load(name, split, columns, where)` and `read_json(path)` with either loader,
then run the join block unchanged. With `datasets`:

<!-- hfd-recipe:loader-datasets -->

```python
''' + LOADER_DATASETS.replace('@VERSION@', version) + '''
```

Or, without `datasets`, from a complete local download of the same revision
(`root`), reading exactly the files declared in this card's YAML:

<!-- hfd-recipe:loader-pyarrow -->

```python
''' + LOADER_PYARROW + '''
```

The join itself. The frozen occurrence mapping in `manifests/MANIFEST.json`
gives every frozen row its prepared005 occurrence (pool, prepared shard,
ordinal). One model's `training_membership` gives each occurrence its
`row_key` or synthetic identity. Metadata, current labels and current features
join by `row_key`; original crops join by `crop_sha256`. Lines outside the
trained view have a null `trainer_line_id` and still join by `row_key`:

<!-- hfd-recipe:join -->

```python
''' + RECIPE_JOIN + '''
```

`real` is the real trained view with metadata, current labels and features;
`current` holds every real observation; `synthetic` is the synthetic trained
view; `views` holds identified synthetic val/reserved views. Features use
`row_key` and the immutable label-version ID (`label_version_id`);
`label_variant_name` is the human variant name. Trainer/reference variant
locators live in `training_membership`; reference-only memberships have
`membership_kind=reference_image` and no invented model or draw evidence.
Legacy synthetic `(line_id, reuse_index, split)` attributes may collide, so join
by occurrence and `synthetic_key`. `synthetic_lines` retains all agreed
synthetic fields and null reasons.

See [UPDATING.md](UPDATING.md). Corrections never touch `data/` or `images/`.
Updates append label versions and features, then publish `labels/current` and
`tables/current_features` together. Both current projections are rewritten
whole: updating is metadata-only (no image re-upload), not proportional to the
number of corrected rows. Each substantive correction generation gets a
new immutable tag; tags are never moved. The frozen trained view remains fixed.

''')


def retarget(text, generation):
    """Point every generation reference in a card at a new generation.

    Front matter, title, introduction and loader revisions change together; a
    remaining stale reference is a hard failure.
    """
    if not re.fullmatch(r'v0\.\d+', generation):
        raise ValueError('generation must be v0.n')
    found = set(GENERATION_RE.findall(text))
    if len(found) > 1:
        raise ValueError('card names several current generations')
    if found:
        old = found.pop()
    else:
        match = re.search(r'^pretty_name: "Greek OCR lines (v0\.\d+)"$', text, flags=re.M)
        if not match:
            raise ValueError('card generation not found')
        old = match.group(1)
    if old == generation:
        return text
    # Only generation references: component versions and history lines keep their values.
    forms = [GENERATION_MARKER, 'pretty_name: "Greek OCR lines {}"', '# Greek OCR lines {}\n',
             'version is **{}**', 'revision = "{}"', '"fffoivos/greek-ocr-lines", "{}"']
    for form in forms:
        text = text.replace(form.format(old), form.format(generation))
    stale = [form.format(old) for form in forms if form.format(old) in text]
    stale += [block for block in re.findall(r'```python\n(.*?)```', text, flags=re.S) if f'"{old}"' in block][:1]
    if stale:
        raise ValueError('stale card generation reference remains: ' + stale[0][:80])
    return text


def front_matter(text, configs):
    """Rewrite the YAML config block from CONFIGS.json, keeping other front matter."""
    if not text.startswith('---\n') or '\n---\n' not in text[4:]:
        raise ValueError('card lacks YAML front matter')
    head, body = text[4:].split('\n---\n', 1)
    lines = head.split('\nconfigs:', 1)[0].rstrip('\n').split('\n') + ['configs:']
    for name in [n for n in ('real', 'synthetic') if n in configs] + sorted(set(configs) - {'real', 'synthetic'}):
        lines += ['  - config_name: ' + name]
        if name == ('real' if 'real' in configs else 'lines'):
            lines += ['    default: true']
        lines += ['    data_files:']
        for split, paths in configs[name].items():
            lines += ['      - split: ' + split, '        path: ' + json.dumps(paths)]
    return '---\n' + '\n'.join(lines) + '\n---\n' + body


def card_generation(text):
    found = set(GENERATION_RE.findall(text))
    match = re.search(r'^pretty_name: "Greek OCR lines (v0\.\d+)"$', text, flags=re.M)
    if len(found) > 1 or not (found or match):
        raise ValueError('card generation not found or ambiguous')
    return found.pop() if found else match.group(1)


def refresh_card(root, generation=None):
    """Regenerate this module's sections in an existing package README.

    For a derived candidate whose builder card predates the executable recipe:
    the introduction, config YAML, joins and custody sections are rewritten from
    the package's own manifests; every other section is kept byte-for-byte. The
    caller regenerates MANIFEST/SHA256SUMS afterwards.
    """
    root = Path(root)
    path = root / 'README.md'
    text = path.read_text()
    configs = json.loads((root / 'manifests/CONFIGS.json').read_text())
    version = card_generation(text)
    title = re.search(r'^# Greek OCR lines v0\.\d+\n\n(?:\*\*Bounded smoke build; incomplete populations\.\*\*\n\n)?',
                      text, flags=re.M)
    if not title or text.count(INTRO_END) != 1 or text.count(JOINS_START) != 1 or text.count(JOINS_END) != 1:
        raise ValueError('card sections not found exactly once')
    text = text[:title.end()] + introduction(version, configs) + text[text.index(INTRO_END):]
    # Replacing joins through the raw-label heading also replaces a previous custody section.
    text = text[:text.index(JOINS_START)] + joins(version) + custody(root) + text[text.index(JOINS_END):]
    text = front_matter(text, configs)
    if generation:
        text = retarget(text, generation)
    recipe_blocks(text)
    path.write_text(text)
    return text


def raw_labels(root):
    coverage = json.loads((Path(root) / 'manifests/COVERAGE.json').read_text())
    text = '''## Raw Google text and corrections

`label_versions` contains `raw` (Google text), `census_g2`/`census06_g2`
(the census label), route variants such as `sf7`, `ru1` and `n1`, `release`
(the released label), and `trained` (the exact trainer label). `labels_current`
selects the incumbent release/correction label; it does not replace trained text.
Harvest raw values are recovered from saved Google responses, bound to response,
anchors/contributors, row locator and producer, and accepted only when they
hash-equal the recorded raw_text_sha256. Public text is distinct from raw Google
response payloads, which stay in the private archive.

`reconstructed_from_recorded_edits` means a route's recorded edits were composed
against the raw parent. Its before/after is raw versus raw plus that route's
edits, not an observed historical intermediate and not a sequential tool replay.
Recorded composition is followed by the recorded normalisation; no assisted
decision or inference is rerun. Endpoint hash equality alone is insufficient.
`route_statuses`, `correction_bindings`, `raw_text_field`, `before_sha256`,
`normalization`, `source_locator` and `source_sha256` retain that provenance.
Statuses distinguish applied, assisted, no_change, out_of_scope and unresolved;
a missing edit record remains unknown with a reason.

Unavailable/unverified text is null with `reason` (for example, absent response,
locator/hash mismatch or missing recorded edits); null never means an empty
transcription or a successful no-change. The observed reason strings and counts
below come from [COVERAGE.json](manifests/COVERAGE.json), `raw_text`:

| Wave | Rows | Hash-verified raw | Null reasons (count) |
| --- | ---: | ---: | --- |
'''
    for wave, counts in sorted(coverage.get('raw_text', {}).items()):
        reasons = ', '.join(f'{k}: {v:,}' for k, v in sorted(counts.get('nulls_by_reason', {}).items())) or 'none'
        text += f'| {wave} | {counts["rows"]:,} | {counts["recovered_raw"]:,} | {reasons} |\n'
    if not coverage.get('raw_text'):
        text += '| No harvest wave measured in this build | — | — | See build scope |\n'
    return text + ('\nCoverage denominators are selected source observations; overlapping populations '
                   'must not be summed as distinct lines. `unresolved_binding_consequences`, '
                   '`binding_writes` and `historical_unknowns` retain other null reasons and '
                   'their release consequences. Correction route provenance is in `label_versions`.\n\n'
                   '## Licence and sources\n\nLicence fields were intentionally removed by owner decision. '
                   'The detailed source fields provide a way to find the exact book: provider, item, '
                   'edition, volume, title, year, source/catalogue URLs and page convention where retained.\n\n')


ARCHIVE_REPO = 'fffoivos/greek-ocr-lines-archive'
CUSTODY_START = '## Private archive custody'
ARCHIVE_INDEX = 'manifests/ARCHIVE_INDEX.json'
ARCHIVE_MEMBERS = 'manifests/ARCHIVE_MEMBERS.parquet'
EMPTY_SHA256 = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
EMPTY_BLOB = 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391'
MEMBER_COLUMNS = ['shard', 'member', 'offset', 'bytes', 'sha256', 'source_path']
HEX64 = re.compile('[0-9a-f]{64}')


def _read_back(entry):
    """The archive uploader's readback rule: file-byte SHA256 + size, or the empty blob."""
    remote = entry.get('remote') or {}
    if remote.get('path') != entry['path'] or remote.get('size') != entry['bytes']:
        return False
    if remote.get('sha256'):
        return remote['sha256'] == entry['sha256']
    return entry['bytes'] == 0 and entry['sha256'] == EMPTY_SHA256 and remote.get('blob_id') == EMPTY_BLOB


def build_archive_index(upload_receipt, consolidation_readback, consolidation_plan, members_root):
    """Source hash -> private archive revision, path and tar member, from PASS receipts only.

    Returns the JSON index and the member-level Arrow table. Nothing is inferred
    beyond the receipts: every object was read back by the upload receipt, every
    packed member comes from a MEMBERS.parquet whose bytes the receipt verified.
    """
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq
    from .common import assert_clean, sha
    upload_receipt, consolidation_readback, consolidation_plan = map(
        Path, (upload_receipt, consolidation_readback, consolidation_plan))
    upload = json.loads(upload_receipt.read_text())
    readback = json.loads(consolidation_readback.read_text())
    plan = json.loads(consolidation_plan.read_text())
    if upload.get('status') != 'PASS' or upload.get('repo') != ARCHIVE_REPO or not upload.get('verified_files'):
        raise ValueError('archive index requires a PASS upload receipt for ' + ARCHIVE_REPO)
    if (readback.get('status') != 'PASS' or readback.get('deletions') != [] or plan.get('repo') != ARCHIVE_REPO
            or plan.get('deletions') != [] or readback.get('verified_copies') != len(plan.get('operations', []))):
        raise ValueError('archive index requires a PASS copy-only consolidation readback matching its plan')
    for value in (upload['revision'], readback['revision']):
        if not re.fullmatch('[0-9a-f]{40}', value):
            raise ValueError('archive revision must be a full commit id')
    files = sorted(upload['verified_files'], key=lambda e: e['path'])
    by_path = {e['path']: e for e in files}
    if len(by_path) != len(files):
        raise ValueError('duplicate archive upload path')
    objects = []
    for e in files:
        if not HEX64.fullmatch(e['sha256']) or not _read_back(e):
            raise ValueError('archive object lacks byte readback: ' + e['path'])
        objects.append({'sha256': e['sha256'], 'bytes': e['bytes'], 'path': e['path'],
                        'original_locator': e.get('source_path')})
    packed, tables = [], []
    for e in files:
        if not e['path'].endswith('/MEMBERS.parquet'):
            continue
        item = e['path'].rsplit('/', 1)[0]
        local = Path(members_root) / e['path']
        if local.stat().st_size != e['bytes'] or sha(local) != e['sha256']:
            raise ValueError('member manifest differs from uploaded bytes: ' + e['path'])
        table = pq.read_table(local)
        if table.column_names != MEMBER_COLUMNS:
            raise ValueError('unexpected member manifest columns: ' + e['path'])
        shards = sorted(set(table.column('shard').to_pylist()))
        archive_paths = pc.binary_join_element_wise(pa.scalar(item), table.column('shard'), '/')
        for shard in shards:
            entry = by_path.get(item + '/' + shard)
            if entry is None or '/' in shard:
                raise ValueError('packed shard was not uploaded: ' + item + '/' + shard)
            mask = pc.equal(table.column('shard'), shard)
            end = pc.max(pc.add(pc.filter(table.column('offset'), mask), pc.filter(table.column('bytes'), mask))).as_py()
            if end > entry['bytes']:
                raise ValueError('tar member extends beyond its shard: ' + item + '/' + shard)
        if (table.num_rows == 0 or not pc.all(pc.match_substring_regex(table.column('sha256'), '^[0-9a-f]{64}$')).as_py()
                or pc.min(table.column('offset')).as_py() < 0 or pc.min(table.column('bytes')).as_py() < 0):
            raise ValueError('invalid member manifest values: ' + e['path'])
        tables.append(pa.table({'sha256': table.column('sha256'), 'bytes': table.column('bytes'),
            'archive_path': archive_paths, 'tar_member': table.column('member'),
            'tar_offset': table.column('offset'), 'original_locator': table.column('source_path'),
            'item': pa.array([item] * table.num_rows, pa.string())}))
        packed.append({'item': item, 'members_path': e['path'], 'members_sha256': e['sha256'],
                       'members': table.num_rows,
                       'shards': [{'path': item + '/' + s, 'sha256': by_path[item + '/' + s]['sha256'],
                                   'bytes': by_path[item + '/' + s]['bytes']} for s in shards]})
    members = pa.concat_tables(tables) if tables else pa.table(
        {k: pa.array([], t) for k, t in (('sha256', pa.string()), ('bytes', pa.int64()), ('archive_path', pa.string()),
         ('tar_member', pa.string()), ('tar_offset', pa.int64()), ('original_locator', pa.string()), ('item', pa.string()))})
    copies = []
    for op in plan['operations']:
        if op['path_in_repo'] in by_path:
            raise ValueError('consolidation copy collides with an uploaded path: ' + op['path_in_repo'])
        expected = op.get('expected') or {}
        copies.append({'path': op['path_in_repo'], 'bytes': expected.get('size'), 'sha256': expected.get('sha256'),
                       'blob_id': expected.get('blob_id'), 'source_revision': op['src_revision'],
                       'source_path': op['src_path_in_repo']})
    if len({c['path'] for c in copies}) != len(copies):
        raise ValueError('duplicate consolidation destination')
    index = {
        'schema': 'hfd-archive-index-v1', 'repo': ARCHIVE_REPO, 'private': True,
        'revision': readback['revision'], 'upload_revision': upload['revision'],
        'lineage': ('Objects were read back by file-byte SHA256 and size at upload_revision. The consolidation '
                    'committed copy operations only on main, with zero deletions, ending at revision. '
                    'The consolidation receipt does not record its parent commit; see GAPS.'),
        'receipts': {name: {'file': path.name, 'sha256': sha(path), 'bytes': path.stat().st_size}
                     for name, path in (('upload', upload_receipt), ('consolidation_readback', consolidation_readback),
                                        ('consolidation_plan', consolidation_plan))},
        'counts': {'objects': len(objects), 'object_bytes': sum(o['bytes'] for o in objects),
                   'packed_items': len(packed), 'tar_members': members.num_rows, 'consolidated_copies': len(copies)},
        'resolution': ('A source SHA256 resolves to an archive object path (objects), or to a tar member at a byte '
                       'offset inside an archive shard (members table), or to a consolidated branch copy. '
                       'original_locator is the historical source path, retained as an identity, not a fetchable URL.'),
        'objects': objects, 'packed_items': packed, 'consolidated_copies': copies,
    }
    assert_clean(index)
    return index, members


def write_archive_index(out_root, upload_receipt, consolidation_readback, consolidation_plan, members_root):
    import pyarrow.parquet as pq
    from .common import atomic_json, info
    out_root = Path(out_root)
    index_path, members_path = out_root / ARCHIVE_INDEX, out_root / ARCHIVE_MEMBERS
    if index_path.exists() or members_path.exists():
        raise ValueError('archive index outputs already exist')
    index, members = build_archive_index(upload_receipt, consolidation_readback, consolidation_plan, members_root)
    members_path.parent.mkdir(parents=True, exist_ok=True)
    partial = members_path.with_name(members_path.name + '.partial')
    pq.write_table(members, partial, compression='zstd', row_group_size=65536)
    partial.replace(members_path)
    index['members_table'] = {**{k: v for k, v in info(members_path, out_root).items() if k != 'path'},
                              'path': ARCHIVE_MEMBERS, 'rows': members.num_rows}
    atomic_json(index_path, index)
    return {'index': ARCHIVE_INDEX, 'members': ARCHIVE_MEMBERS, **index['counts']}


def custody(root):
    path = Path(root) / ARCHIVE_INDEX
    if not path.is_file():
        return ''
    index = json.loads(path.read_text())
    counts = index['counts']
    return (CUSTODY_START + f'''

Source objects are preserved in the private archive `{index["repo"]}` at
revision `{index["revision"]}`. [ARCHIVE_INDEX.json](manifests/ARCHIVE_INDEX.json)
maps each source SHA256 to its archive path: {counts["objects"]:,} archive
objects, {counts["tar_members"]:,} members of {counts["packed_items"]:,} packed
items (tar member and byte offset, in
[ARCHIVE_MEMBERS.parquet](manifests/ARCHIVE_MEMBERS.parquet)) and
{counts["consolidated_copies"]:,} consolidated branch copies. Objects were read
back by SHA256 at upload revision `{index["upload_revision"]}`. Historical
locators and older repository identities are kept as identities; they are not
fetchable public URLs. The archive is private and is not needed to use this
dataset.

''')


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description='Card refresh and archive custody index writer')
    sub = p.add_subparsers(dest='command', required=True)
    refresh = sub.add_parser('refresh', help='regenerate card sections in an existing package README')
    refresh.add_argument('root', type=Path)
    refresh.add_argument('--generation')
    index = sub.add_parser('archive-index', help='write manifests/ARCHIVE_INDEX.json and ARCHIVE_MEMBERS.parquet')
    index.add_argument('--out', type=Path, required=True, help='candidate root (writes under manifests/)')
    index.add_argument('--upload-receipt', type=Path, required=True)
    index.add_argument('--consolidation-readback', type=Path, required=True)
    index.add_argument('--consolidation-plan', type=Path, required=True)
    index.add_argument('--members-root', type=Path, required=True, help='archive upload tree holding MEMBERS.parquet')
    args = p.parse_args(argv)
    if args.command == 'refresh':
        refresh_card(args.root, args.generation)
        print(json.dumps({'refreshed': str(args.root / 'README.md')}))
    else:
        print(json.dumps(write_archive_index(args.out, args.upload_receipt, args.consolidation_readback,
                                             args.consolidation_plan, args.members_root), sort_keys=True))
    return 0


if __name__ == '__main__':
    import sys
    if __package__ in (None, ''):
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
        __package__ = 'scripts.release_v0_dataset'
        import importlib
        sys.exit(importlib.import_module('scripts.release_v0_dataset.card').main())
    sys.exit(main())
