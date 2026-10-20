"""Detector-backed geometry audit; no recognizer or prediction dependency."""
from .ownership import ownership
from .span import span_audit, assemble
from .clipping import clipping

__all__ = ["ownership", "span_audit", "assemble", "clipping"]
