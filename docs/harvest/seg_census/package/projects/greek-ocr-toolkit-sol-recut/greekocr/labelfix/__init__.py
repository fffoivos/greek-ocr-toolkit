"""Google-label correction for the Greek OCR harvest (owner brief, 16 Oct 2026).

Training labels are Google Document AI reads (silver). A label is corrected only where
three independent witnesses agree against Google: our recogniser's reading, a regime
lexicon built from proofread human text, and the ink of the crop itself. See
docs/labelfix/REPORT.md for the method and its limits.

Modules
-------
text        NFD tokenisation, vowel clusters, diff classification, guards
lexicon     per-regime frequency lexicons (build, load, query)
ctc_align   recogniser forward pass -> per-character x ranges in crop pixels
ink         ink evidence (mark blobs above / below a vowel) via glyphs.components
rules       the rule engine (pure functions, unit-tested)
candidates  Google-vs-model word alignment -> evidenced candidates
deck        the owner's yes/no review deck (static HTML)
"""
from __future__ import annotations

__all__ = ['__version__']
__version__ = '0.1.0'
