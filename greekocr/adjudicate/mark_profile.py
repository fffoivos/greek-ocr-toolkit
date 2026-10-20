"""Tranche-6 mark views from native pixels: line, word 3×, letter 8×."""
from __future__ import annotations
import math
from PIL import Image

__all__ = ['mark_views']


def mark_views(image: Image.Image, word_box: list[float], letter_box: list[float]) -> dict[str, Image.Image]:
    """Return native line and explicit 3×/8× crops, validating both native boxes.

    The 8× letter view is an explicit mark-profile protocol, separate from CU4's
    ordinary 3× blind crop cap; no interpolation changes the underlying evidence.
    """
    result = {'line': image.convert('RGB')}
    for name,box,scale in [('word',word_box,3),('letter',letter_box,8)]:
        if len(box)!=4 or not all(math.isfinite(x) for x in box) or not (0<=box[0]<box[2]<=image.width and 0<=box[1]<box[3]<=image.height):
            raise ValueError('invalid native mark crop box')
        crop = image.crop(box).convert('RGB')
        result[name] = crop.resize((crop.width*scale,crop.height*scale),Image.Resampling.NEAREST)
    return result
