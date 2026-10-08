"""Independent raster readability and Greek-text quality diagnostics.

Cheap checks are offline; Codex judges run only when explicitly invoked.
"""
from .images import ImageChecks, Profile, image_checks, readability_profile, render_overlay
from .text import TextChecks, text_checks
from .judges import READABILITY_SCHEMA, CallBudget, vlm_annotate, llm_judge, judge_texts

__all__ = ['ImageChecks', 'Profile', 'image_checks', 'readability_profile', 'render_overlay',
           'TextChecks', 'text_checks', 'READABILITY_SCHEMA', 'CallBudget', 'vlm_annotate',
           'llm_judge', 'judge_texts']
