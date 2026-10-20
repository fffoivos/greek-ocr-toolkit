"""Docling plugin options and reviewable deployment plans."""
from typing import Any
from greekocr.types import PathLike
__all__ = ['plugin_options']

def plugin_options(checkpoint: PathLike, codec: PathLike, *, routing_sidecar: PathLike | None = None,
                   replace_policy: str = 'routed_pages', checkpoint_sha256: str | None = None,
                   device: str = 'cpu') -> Any:
    from .docling_plugin.options import GlossapiOcrOptions
    return GlossapiOcrOptions(checkpoint=checkpoint, codec=codec, routing_sidecar=routing_sidecar,
                             replace_policy=replace_policy, checkpoint_sha256=checkpoint_sha256, device=device)
