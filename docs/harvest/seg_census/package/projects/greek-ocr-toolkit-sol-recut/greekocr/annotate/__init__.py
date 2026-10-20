"""Frozen line categories and factory-compatible script/word tags."""
from __future__ import annotations
import json
from pathlib import Path
from greekocr.types import PathLike, Record
from greekocr._vendor.bench.line_categories import categories as _categories, word_tags as _words
from greekocr._vendor.bench.o4b_common import tag as _tag
from greekocr._vendor.train.mix import sha256
from .line_features import LineFeatures, line_features, load_lexicon
from .font import FontEstimate, font_estimate, font_style, train_font_classifier
from .sources import source_metadata
from .pipeline import annotate_records, distribution_report
from .strata import stratum_key, stratum_counts, sampling_weights
__all__ = ['line_categories', 'script_class', 'word_tags', 'load_word_tags',
           'LineFeatures', 'line_features', 'load_lexicon', 'FontEstimate', 'font_estimate',
           'font_style', 'train_font_classifier', 'source_metadata', 'annotate_records',
           'distribution_report', 'stratum_key', 'stratum_counts', 'sampling_weights']

def line_categories(row: Record) -> list[str]:
    return _categories(row)


def script_class(text: str) -> str | None:
    return _tag(text)


def word_tags(text: str) -> list[Record]:
    """Diagnostic fallback tags, never a fabricated factory-sidecar receipt."""
    return _words(text)


def load_word_tags(build_dir: PathLike) -> list[Record] | None:
    """Return only the receipt-bound sidecar; historical absence returns None."""
    root = Path(build_dir)
    info = json.loads((root/'build_info.json').read_text())
    digest = info.get('word_tags_sha256')
    if not digest: return None
    if sha256(root/'word_tags.jsonl') != digest: raise ValueError('word-tag sidecar hash mismatch')
    return [json.loads(s) for s in (root/'word_tags.jsonl').read_text().splitlines() if s.strip()]
