"""Coordinates are source pixels; page_size is caller metadata, never a rescale."""
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

import numpy as np


@dataclass(frozen=True)
class SegmenterInfo:
    name: str
    generation: int
    detector_model: str
    deps: tuple[str, ...]
    status: str


@dataclass
class Line:
    id: str
    polygon: list[list[float]]
    bbox: tuple[float, float, float, float]
    baseline: list[list[float]] | None
    status: Literal['kept', 'dropped']
    reason: str | None
    extras: dict[str, Any] = field(default_factory=dict)


@dataclass
class SegmentationResult:
    segmenter: str
    lines: list[Line]
    image_size: tuple[int, int]
    page_size: tuple[float, float]
    timings: dict[str, Any]
    extras: dict[str, Any] = field(default_factory=dict)


class Segmenter(Protocol):
    info: SegmenterInfo

    def segment(self, page_image: np.ndarray, *, page_size=None,
                layout=None) -> SegmentationResult: ...
