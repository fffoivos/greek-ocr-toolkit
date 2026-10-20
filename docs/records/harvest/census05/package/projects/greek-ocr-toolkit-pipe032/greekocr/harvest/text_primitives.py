"""Admission text primitives. No spelling, script folding or label correction."""
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import unicodedata as ud

from greekocr._vendor.train.cer import load_codec as validating_load_codec
from greekocr.labelfix.text import nfc, nfd, is_mark


@lru_cache(maxsize=8192)
def unicode_letter_script(char):
    """Single fallback for letters outside the codec and legacy diagnostics."""
    if not ud.category(char).startswith('L'):
        return None
    name = ud.name(char, 'UNNAMED')
    return next((s.lower() for s in ('GREEK', 'LATIN', 'CYRILLIC') if s in name), 'other')


def codec_view(path=None):
    path = Path(path) if path else Path(__file__).resolve().parents[1] / '_vendor/codec/v2.json'
    raw = path.read_bytes()
    obj = json.loads(raw)
    codec = validating_load_codec(str(path))
    if path.read_bytes() != raw:
        raise ValueError('codec changed during validation')
    if obj['policy']['normalization'] != 'NFD':
        raise ValueError('standard admission requires the NFD codec contract')
    metadata = {codec.atom_by_id[a['id']]: dict(kind=a['kind'], script=a['script']) for a in codec.atoms}
    if len(metadata) != len(codec.atoms):
        raise ValueError('duplicate codec character')
    return dict(version=codec.version, path=str(path.resolve()),
                sha256=hashlib.sha256(raw).hexdigest(), atoms=frozenset(metadata),
                metadata=metadata, policy=obj['policy'],
                nonletter_atoms=frozenset(c for c, a in metadata.items()
                                         if a['kind'] in ('punct', 'sym', 'space', 'digit')))


def codec_letter_script(char, codec):
    """One letter vote, using NFD base metadata; inherited marks never vote.

    Literal spacing atoms declared as punctuation are not letters even where
    Unicode calls them modifier letters. Fallback is diagnostic, never folding.
    """
    if char in codec['nonletter_atoms'] or not ud.category(char).startswith('L'):
        return None
    names = dict(grek='greek', latn='latin', cyrl='cyrillic')
    for base in nfd(char):
        if is_mark(base):
            continue
        atom = codec['metadata'].get(base)
        if atom is not None:
            if atom['kind'] != 'base':
                return None
            return names.get(atom['script'], 'other')
        return unicode_letter_script(base)
    return None


def normalize_current(raw, *, mode='admission-dot-nfc-v1'):
    """Current R8/NFC/whitespace policy with an ordered audit trail."""
    if mode != 'admission-dot-nfc-v1':
        raise ValueError('unknown normalization mode')
    dotted = raw.replace('\u02d9', '\u00b7')
    composed = nfc(dotted)
    text = ' '.join(composed.split())
    changes = []
    if dotted != raw:
        changes.append('R8:dot_above_to_middle_dot')
    if composed != dotted:
        changes.append('NFC')
    if text != composed:
        changes.append('collapse_whitespace')
    return text, changes
