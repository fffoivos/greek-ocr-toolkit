"""Options for the routed, per-page Docling OCR replacement engine."""
from pathlib import Path
from typing import ClassVar, Literal

from docling.datamodel.pipeline_options import OcrOptions
from pydantic import Field, model_validator
from greekocr.pages.options import OutputOptions


class GlossapiOcrOptions(OcrOptions):
    # Docling's factory reads the discriminator on the CLASS, as for bundled engines.
    kind: ClassVar[Literal["glossapi"]] = "glossapi"
    lang: list[str] = Field(default_factory=lambda: ["el", "en"])
    checkpoint: Path
    codec: Path | None = None
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
        if self.replace_policy == "routed_pages" and self.routing_sidecar is None:
            raise ValueError("routed_pages requires a routing_sidecar")
        self.page_options()
        return self
