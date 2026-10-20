"""Text-only numeric proposals; no glyph inference or correction."""
from .tokens import NumericToken, Slot, tokenize

__all__ = ["NumericToken", "Slot", "tokenize"]
