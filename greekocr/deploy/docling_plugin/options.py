"""Options for the routed, per-page Docling OCR replacement engine."""
from pathlib import Path
from typing import ClassVar, Literal

from docling.datamodel.pipeline_options import OcrOptions
from pydantic import Field, StrictBool, model_validator
from greekocr.pages.options import OutputOptions


class GlossapiOcrOptions(OcrOptions):
    # Docling's factory reads the discriminator on the CLASS, as for bundled engines.
    kind: ClassVar[Literal["glossapi"]] = "glossapi"
    lang: list[str] = Field(default_factory=lambda: ["el", "en"])
    checkpoint: Path | None = None
    codec: Path | None = None
    release_dir: Path | None = None
    model_repo: str = 'fffoivos/greek-ocr'
    model_variant: Literal['x1', 'x1.5', 'x2'] | None = None
    model_revision: str | None = Field(default=None, min_length=1)
    model_manifest_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    segmenter: Literal['pixel_slow', 'paddle_small_heuristics_r7', 'paddle_small_heuristics_r8'] = 'paddle_small_heuristics_r8'
    segmenter_detector: Literal['small'] = 'small'
    detector_device: Literal['cpu', 'coreml'] = 'cpu'
    segmenter_preset: Literal['born_digital', 'clean_scan', 'degraded_scan'] = 'clean_scan'
    segmenter_rules: dict[str, StrictBool] = Field(default_factory=dict)
    ornament_seeds: list[Path] = Field(default_factory=list)
    hole_seeds: list[Path] = Field(default_factory=list)
    config_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    recognition_mode: Literal["textlayer", "detector", "oriented"] = "textlayer"
    crop_scale: float = Field(default=3.0, gt=0, allow_inf_nan=False)
    device: str = "cpu"
    routing_sidecar: Path | None = None
    replace_policy: Literal["routed_pages", "all"] = "routed_pages"
    checkpoint_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    call_log: Path | None = None
    tables: bool = True
    join_lines: bool = False
    granularity: Literal['default', 'rows', 'pieces'] = 'default'
    statistics: bool = False
    discounted: Literal['keep', 'drop'] = 'keep'
    outputs: OutputOptions = Field(default_factory=OutputOptions)

    def page_options(self):
        """Map detector switches to the same options used by Python and the CLI."""
        from greekocr.pages import PageOptions
        return PageOptions(tables=self.tables, orientation=self.recognition_mode == 'oriented',
                           strict_geometry=self.recognition_mode == 'detector',
                           join_lines=self.join_lines, granularity=self.granularity,
                           statistics=self.statistics, discounted=self.discounted, outputs=self.outputs)

    @model_validator(mode="after")
    def validate_replacement(self):
        if self.checkpoint is None and self.release_dir is None:
            if self.model_variant is None or self.model_revision is None:
                raise ValueError('model_variant and model_revision are required without release_dir or checkpoint')
            if self.codec is not None:
                raise ValueError('downloaded release contains its codec; do not supply codec')
        if self.release_dir is not None and self.codec is not None:
            raise ValueError('release_dir contains its codec; do not supply codec')
        from greekocr.segmenters.api import _rules, _PIXEL_RULES, _FAST_RULES
        if self.segmenter == 'pixel_slow':
            existing = dict(tables='tables', orientation='recognition_mode', join_lines='join_lines')
            for key, option in existing.items():
                if key in self.segmenter_rules:
                    raise ValueError(f"pixel_slow segmenter_rules[{key!r}]: use the existing {option} option")
        defaults = dict(_PIXEL_RULES if self.segmenter == 'pixel_slow' else _FAST_RULES)
        if self.segmenter == 'paddle_small_heuristics_r8':
            defaults['final_export'] = False
        rules = _rules(defaults, self.segmenter_preset, self.segmenter_rules)
        if rules['ornaments'] and not self.ornament_seeds:
            raise ValueError('ornaments requires ornament_seeds')
        if rules['spiral_holes'] and not self.hole_seeds:
            raise ValueError('spiral_holes requires hole_seeds')
        if self.segmenter != 'pixel_slow':
            pixel_only = ('join_lines', 'granularity', 'statistics', 'outputs', 'tables', 'discounted')
            changed = [name for name in pixel_only if name in self.model_fields_set
                       and getattr(self, name) != type(self).model_fields[name].get_default(call_default_factory=True)]
            if self.recognition_mode == 'oriented':
                changed.append('recognition_mode=oriented')
            if changed:
                raise ValueError(f"{', '.join(changed)} requires segmenter='pixel_slow'")
        if self.replace_policy == "routed_pages" and self.routing_sidecar is None:
            raise ValueError("routed_pages requires a routing_sidecar")
        self.page_options()
        return self
