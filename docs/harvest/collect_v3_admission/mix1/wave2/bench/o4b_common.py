"""O4b custody, codec-v1 admission and document partitioning. No shard writer."""
from __future__ import annotations

import hashlib
import json
import unicodedata as ud
from collections import Counter
from pathlib import Path

from bench.codec_coverage import load_v1, normalize_v1
from bench.common import ROOT, sha256, write_json, write_rows

TIERS = {'gold', 'silver', 'silver_ocr_layer', 'silver_agreed', 'gold_aligned', 'flagged'}
PARTITION = 'o4b-documents-v1'


def nfc(text):
    # No spelling, punctuation, lunate or confusable rewrite in the source label.
    return ud.normalize('NFC', ' '.join(text.split()))


def tag(text):
    """Frozen factory/corpus::classify rules, including base-attached poly marks.

    Additional two-script Cyrillic categories map to the real-import v1 class.
    Factory re-tags words; this tag's implementation and source are recorded.
    """
    greek = latin = cyr = poly = False
    previous = ''
    for c in ud.normalize('NFD', text):
        cp = ord(c)
        greek |= 0x370 <= cp <= 0x3ff or 0x1f00 <= cp <= 0x1fff
        latin |= c.isascii() and c.isalpha() or 0xc0 <= cp <= 0x24f
        cyr |= 0x400 <= cp <= 0x4ff
        if ud.category(c).startswith('M'):
            poly |= (bool(previous) and (0x370 <= ord(previous) <= 0x3ff or
                     0x1f00 <= ord(previous) <= 0x1fff) and c in '\u0313\u0314\u0342\u0345\u0300\u0304\u0306')
        else:
            previous = c
    if greek and latin:
        return 'greek_latin_cs'
    if cyr:
        return 'cyrillic'
    if greek:
        return 'greek_poly' if poly else 'greek_mono'
    return 'latin' if latin else None


def resolve_exclusions(documents, identities):
    """Every exposure must be a reviewed alias or a known canonical value."""
    identities = set(identities)
    unresolved = sorted(identities - set(documents) - set(documents.values()))
    if unresolved:
        raise ValueError('unresolved exclusion identities: '+', '.join(unresolved))
    return sorted(identities | {documents[d] for d in identities if d in documents})


class Partition:
    """Reviewed work identities + two compulsory exclusion cohorts, fail closed.

    documents maps dataset-native doc keys to a canonical work (same edition,
    serial volumes and mirrors share a key). No per-page/line split inference.
    SHA exclusions catch byte-identical books across differently named sources.
    """
    def __init__(self, path, seed=20261007):
        self.path, self.seed = Path(path), seed
        self.manifest = json.loads(self.path.read_text())
        m = self.manifest
        if m.get('schema') != PARTITION or m.get('reviewed') is not True:
            raise ValueError('need reviewed o4b-documents-v1 manifest')
        self.documents = m['documents']
        if not self.documents or any(not isinstance(v, str) or not v.strip() for v in self.documents.values()):
            raise ValueError('nonempty canonical document identities required')
        self.excluded = set()
        self.hashes = set()
        resolve_exclusions(self.documents, [d for c in m['cohorts'].values() for d in c.get('documents', [])])
        for name in ('O5_E1_test', 'C1'):
            cohort = m['cohorts'][name]
            if not cohort.get('evidence') or not cohort.get('documents'):
                raise ValueError(f'{name}: explicit document list and evidence required')
            self.excluded.update(resolve_exclusions(self.documents, cohort['documents']))
            self.hashes.update(cohort.get('sha256', []))
        for name, cohort in m['cohorts'].items():
            if name in ('O5_E1_test', 'C1'): continue
            if not cohort.get('evidence') or not cohort.get('documents'):
                raise ValueError(f'{name}: explicit document list and evidence required')
            self.excluded.update(resolve_exclusions(self.documents, cohort['documents']))
            self.hashes.update(cohort.get('sha256', []))
        self.overrides = m.get('split_overrides', {})
        if any(s not in ('train', 'val', 'reserved') or d not in self.documents.values()
               for d, s in self.overrides.items()):
            raise ValueError('split overrides require canonical works and valid splits')
        self.binding = dict(partition_id=PARTITION, seed=seed, exclusions_sha256=sha256(path),
                            rule='sha256(seed/canonical-work) mod 1000: train<900 val<950 reserved>=950')
        if self.overrides:
            self.binding.update(rule=m.get('e2_split_rule', 'reviewed canonical-work overrides; hash rule for other works'),
                                split_overrides=dict(self.overrides))

    def assign(self, doc, digest=None):
        if doc not in self.documents:
            raise ValueError(f'unreviewed document identity: {doc}')
        group = self.documents[doc]
        if doc in self.excluded or group in self.excluded or digest in self.hashes:
            return group, None
        if group in self.overrides:
            return group, self.overrides[group]
        bucket = int(hashlib.sha256(f'{self.seed}/{group}'.encode()).hexdigest(), 16) % 1000
        return group, 'train' if bucket < 900 else 'val' if bucket < 950 else 'reserved'


def inside(root, name):
    root = Path(root).resolve()
    path = (root / name).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError(f'missing file or path escape: {name}')
    return path


def rights(meta):
    if meta.get('rights_reviewed') is not True:
        raise ValueError('dataset/scan AND transcription rights must be reviewed')
    for key in ('licence', 'source_url', 'attribution', 'licence_evidence'):
        if not isinstance(meta.get(key), str) or not meta[key].strip():
            raise ValueError(f'missing rights field: {key}')
    if meta['licence'].casefold() in ('unknown', 'unspecified', 'pending'):
        raise ValueError('unresolved licence')


class Admission:
    def __init__(self, partition, out):
        self.partition, self.out = partition, Path(out)
        self.atoms, self.folds = load_v1()
        self.rows, self.rejected, self.ids = [], [], set()
        self.reasons, self.unknown, self.sources = Counter(), Counter(), Counter()

    def add(self, record):
        r = dict(record)
        for k in ('line_id', 'source_doc_id', 'source_dataset', 'label_tier', 'licence'):
            if not r.get(k):
                raise ValueError(f'missing record field {k}')
        if r['label_tier'] not in TIERS:
            raise ValueError('invalid label_tier')
        if r['line_id'] in self.ids:
            raise ValueError('duplicate line_id: ' + r['line_id'])
        self.ids.add(r['line_id'])
        r['text_raw'] = r.get('text_raw', r['text'])
        r['text'] = nfc(r['text'])
        normalized = normalize_v1(r['text'], self.folds)
        bad = Counter(c for c in normalized if c not in self.atoms)
        self.unknown.update(bad)
        group, split = self.partition.assign(r['source_doc_id'], r.get('document_sha256'))
        r.update(source_native_doc_id=r['source_doc_id'], source_doc_id=group,
                 split=split or 'reserved', partition_id=PARTITION,
                 licence=r['licence'], license=r['licence'], script_class=tag(normalized),
                 script_tagger='o4b_common.tag (factory/corpus::classify v1 parity)',
                 codec_version='v1', unknown_atoms={f'U+{ord(c):04X}': n for c, n in bad.items()})
        reasons = list(r.get('reject_reasons', []))
        if not split: reasons.append('excluded_document')
        if bad: reasons.append('codec_v1_unknown')
        if not normalized: reasons.append('empty_text')
        if not r['script_class']: reasons.append('no_script')
        if r['label_tier'] == 'flagged': reasons.append('label_flagged')
        if r.get('admitted') is False and not reasons: reasons.append('source_not_admitted')
        p = Path(r['crop_path'])
        if not p.is_file(): reasons.append('missing_crop')
        if p.is_file():
            from PIL import Image
            try:
                with Image.open(p) as image:
                    image.verify()
                r['crop_sha256'] = sha256(p)
            except (OSError, ValueError): reasons.append('invalid_crop')
        r.update(admitted=not reasons, reject_reasons=sorted(set(reasons)))
        self.reasons.update(r['reject_reasons'])
        self.sources[r['source_dataset']] += 1
        (self.rows if r['admitted'] else self.rejected).append(r)
        return r

    def finish(self):
        self.out.mkdir(parents=True, exist_ok=True)
        write_rows(self.out/'records.jsonl', self.rows)
        write_rows(self.out/'rejected.jsonl', self.rejected)
        report = dict(**self.partition.binding, admitted=len(self.rows), rejected=len(self.rejected),
                      reasons=dict(self.reasons), sources=dict(self.sources),
                      unknown_atom_counts={f'U+{ord(c):04X}': n for c, n in sorted(self.unknown.items())},
                      tiers=dict(Counter(r['label_tier'] for r in self.rows)),
                      doc_splits={r['source_doc_id']: r['split'] for r in self.rows},
                      records_sha256=sha256(self.out/'records.jsonl'),
                      code_sha256=sha256(__file__), codec_source_sha256=sha256(ROOT/'factory/src/codec.rs'),
                      training_shards_written=False)
        write_json(self.out/'report.json', report)
        return report


def fresh(out):
    out = Path(out)
    if out.exists() and any(out.iterdir()):
        raise ValueError('use a fresh output directory; inputs and provenance are immutable')
    out.mkdir(parents=True, exist_ok=True)
