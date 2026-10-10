"""Typed JSON records and result containers; pixel arrays stay in segmentation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, NotRequired, TYPE_CHECKING, TypedDict

from .lines import PageSegmentation
from .options import PageOptions
from .tables import TextPiece

if TYPE_CHECKING:
    from ..glyphs.oriented_page import OrientedPage

__all__ = ['PageResult', 'BookResult']


class Address(TypedDict):
    page_side: str
    column_id: str
    block_id: str
    row_id: str
    piece_index: int
    reading_order: int


class LineRecord(Address):
    x0: int
    x1: int
    xheight: float
    column: int
    baseline: list[float]
    meanline: list[float]
    font_top: list[float]
    font_bottom: list[float]
    accent_top: list[float]
    accent_bottom: list[float]
    top: list[float]
    bottom: list[float]
    discounted: str | None
    neighbours: dict[str, Any]
    segment_indices: list[int]
    hint_indices: list[int]
    segment_positions: list[list[int]]
    support: int
    geometry_source: str
    borrowed: list[str]
    ink_classes: dict[str, int]
    contrast: float
    guide_residuals: dict[str, Any]
    row_source: NotRequired[str]
    pieces: NotRequired[list[LineRecord]]


class LeafRecord(TypedDict):
    id: str
    page_side: str
    boundary_ids: list[str]
    polygon: list[list[float]]


class ColumnRecord(TypedDict):
    id: str
    page_side: str
    boundary_ids: list[str]
    left_boundary: dict[str, Any]
    right_boundary: dict[str, Any]
    line_indices: list[int]
    reading_order: int


class BlockRecord(TypedDict):
    id: str
    column_id: str
    page_side: str
    table_id: str | None
    kind: str
    line_indices: list[int]


class RowRecord(TypedDict):
    id: str
    page_side: str
    column_id: str
    block_id: str
    table_id: str | None
    row_source: str | None
    row_sources: list[str]
    discounted: bool
    line_indices: list[int]
    piece_indices: list[int]
    reading_order: int
    box_pixels: list[float]
    joinable: NotRequired[bool]


class GlyphRecord(TypedDict):
    page_key: str | None
    book_id: str | None
    glyph_id: str | None
    line_id: str | None
    page_side: str | None
    column_id: str | None
    spatial_column_id: str | None
    row_id: str | None
    block_id: str | None
    entity_kind: str | None
    ink_class: str | None
    xheight_source: str | None
    coverage_state: str | None
    legacy_state: str | None
    legacy_coverage_state: str | None
    font_group: str | None
    font_role: str | None
    book_font_group: NotRequired[str | None]
    book_font_role: NotRequired[str | None]
    line_index: int | None
    piece_index: int | None
    nearest_line_index: int | None
    ink_pixels: int | None
    holes: int | None
    hole_area: int | None
    pieces: int | None
    merged: int | None
    color_available: bool | None
    resolved: bool | None
    thickened: bool | None
    front_text: bool | None
    show_through_candidate: bool | None
    stamp_watermark_candidate: bool | None
    non_text: bool | None
    faint: bool | None
    blurred: bool | None
    line_inconsistent: bool | None
    letter_like: bool | None
    colored: bool | None
    large_blob: bool | None
    rule_like: bool | None
    mirrored: bool | None
    book_front_text: NotRequired[bool | None]
    book_show_through_candidate: NotRequired[bool | None]
    book_stamp_watermark_candidate: NotRequired[bool | None]
    book_non_text: NotRequired[bool | None]
    book_faint: NotRequired[bool | None]
    book_blurred: NotRequired[bool | None]
    book_line_inconsistent: NotRequired[bool | None]
    book_letter_like: NotRequired[bool | None]
    book_colored: NotRequired[bool | None]
    book_large_blob: NotRequired[bool | None]
    book_rule_like: NotRequired[bool | None]
    book_mirrored: NotRequired[bool | None]
    xheight_px: float | None
    xheight_page_width: float | None
    body_height_xh: float | None
    body_width_xh: float | None
    legacy_score: float | None
    legacy_contrast_ratio: float | None
    rise_xh: float | None
    depth_xh: float | None
    stroke_ratio_line: float | None
    ink_gray: float | None
    darkness: float | None
    paper_gray: float | None
    contrast_absolute: float | None
    contrast_local: float | None
    edge_sharpness: float | None
    color_spread: float | None
    height_xh: float | None
    width_xh: float | None
    stroke_width_px: float | None
    stroke_width_xh: float | None
    fill: float | None
    hole_fraction: float | None
    line_residual_xh: float | None
    contrast_ratio: float | None
    edge_ratio: float | None
    book_contrast_ratio: NotRequired[float | None]
    book_edge_ratio: NotRequired[float | None]
    box: list[int]
    body_box: list[int] | None
    attached_marks: list[dict[str, Any]]

class StatisticsResult(TypedDict):
    stats: dict[str, Any]
    glyphs: list[GlyphRecord]


@dataclass
class PageResult:
    """One input image, its physical leaves, addresses, delivery and measurements."""

    page_key: str
    book_id: str | None
    image_size: tuple[int, int]
    page_size: tuple[float, float]
    options: PageOptions
    segmentation: PageSegmentation = field(repr=False)
    lines: list[LineRecord]
    pieces: list[TextPiece]
    delivery: list[LineRecord]
    statistics: StatisticsResult | None = None
    orientation: OrientedPage | None = None
    regions: list = field(default_factory=list)
    files: dict[str, str] = field(default_factory=dict)

    @property
    def structure(self) -> dict[str, Any]:
        return self.segmentation.structure

    @property
    def pages(self) -> list[LeafRecord]:
        return self.structure['pages']

    @property
    def columns(self) -> list[ColumnRecord]:
        return self.structure['columns']

    @property
    def blocks(self) -> list[BlockRecord]:
        return self.structure['blocks']

    @property
    def rows(self) -> list[RowRecord]:
        return self.structure['rows']

    @property
    def glyphs(self) -> list[GlyphRecord]:
        return self.statistics['glyphs'] if self.statistics is not None else []

    def to_records(self) -> dict[str, Any]:
        """Return the current geometry file payloads without rounding or refitting."""
        return dict(lines=self.lines, structure=self.structure,
                    segments=[dict(line_id=f'{self.page_key}-s{i:05d}', box=list(box))
                              for i, box in enumerate(self.segmentation.segments)],
                    cells=dict(image_size=list(self.image_size), page_size=list(self.page_size),
                               page_units='caller page size; defaults to source pixels',
                               cells=[p.to_record(i, self.image_size, self.page_size)
                                      for i, p in enumerate(self.pieces)]),
                    delivery=self.delivery,
                    rows=dict(schema_version=1, rows=self.delivery, blocked_rows=[], complete=True,
                              geometry_policy='Exact original piece samples; interpolate only missing gap samples.')
                         if self.options.join_lines and self.options.granularity == 'rows' else None,
                    checks=dict(key=self.page_key, image_size=list(self.image_size),
                                xheight=self.segmentation.xheight, **self.segmentation.diagnostics))


@dataclass
class BookResult:
    """Ordered page results plus Q2 book and corpus summaries when requested."""

    book_id: str
    pages: list[PageResult]
    statistics: dict[str, Any] | None = None
    corpus: dict[str, Any] | None = None
    files: dict[str, str] = field(default_factory=dict)
