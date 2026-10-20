"""Image-layout adapters. No PDF text is used to propose table regions."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Sequence

from PIL import Image

TableRegions = Sequence[tuple[str, Sequence[float]]]
LayoutProvider = Callable[[Image.Image], TableRegions]

# Dimensionless confidence gates: retain the Q2 Docling table/index proposals.
TABLE_CONFIDENCE = .5
INDEX_CONFIDENCE = .45
# Page units: the development PNGs were rendered at three pixels per page unit.
RESEARCH_PIXELS_PER_UNIT = 3.


def read_layout(path: str | Path, image_size: Sequence[int]) -> list:
    """Read Q2 retained regions or explicit pixel boxes, validating their frame."""
    data = json.loads(Path(path).read_text())
    if isinstance(data, list):
        return [(str(row['id']), row['box_pixels']) for row in data]
    if 'retained' not in data:
        raise ValueError('layout needs retained regions or a list of id/box_pixels records')
    size = data.get('image_size')
    if size is not None and list(size) != list(image_size):
        raise ValueError('layout image_size differs from the input raster')
    page_size = data.get('page_size')
    sx, sy = ([image_size[i] / page_size[i] for i in range(2)] if page_size
              else [RESEARCH_PIXELS_PER_UNIT] * 2)
    return [(str(row['id']), [v * scale for v, scale in zip(row['box'], (sx, sy, sx, sy))])
            for row in data['retained']]


def docling_regions(layout: object, image_size: Sequence[int], page_size: Sequence[float], *,
                    oriented: bool = False) -> list:
    """Convert Docling TOPLEFT proposals using measured x/y render ratios."""
    from docling_core.types.doc import DocItemLabel
    sx, sy = [image_size[i] / page_size[i] for i in range(2)]
    regions = []
    for cluster in getattr(layout, 'clusters', []):
        if cluster.label not in (DocItemLabel.TABLE, DocItemLabel.DOCUMENT_INDEX):
            continue
        threshold = TABLE_CONFIDENCE if oriented or cluster.label == DocItemLabel.TABLE else INDEX_CONFIDENCE
        if cluster.confidence < threshold:
            continue
        box = cluster.bbox.to_top_left_origin(page_height=page_size[1])
        regions.append((str(cluster.id), (box.l*sx, box.t*sy, box.r*sx, box.b*sy)))
    return regions


def compute_layout(image: Image.Image) -> list:
    """Compute Docling's image-only layout using its locally available model."""
    from types import SimpleNamespace
    from tempfile import TemporaryDirectory
    from docling.datamodel.accelerator_options import AcceleratorOptions
    from docling.datamodel.pipeline_options import LayoutObjectDetectionOptions
    from docling.models.stages.layout.layout_object_detection_model import LayoutObjectDetectionModel
    from docling_core.types.doc import Size
    from huggingface_hub import snapshot_download
    # A local snapshot is required before Docling can initialise its detector.
    artifacts = snapshot_download('docling-project/docling-layout-heron', local_files_only=True)
    # Docling expects a model-named child below its artifact root. The symlink
    # supplies that layout without copying weights or modifying the HF cache.
    with TemporaryDirectory(prefix='greekocr-layout-') as temporary:
        (Path(temporary) / 'docling-project--docling-layout-heron').symlink_to(artifacts, target_is_directory=True)
        model = LayoutObjectDetectionModel(artifacts_path=Path(temporary),
            accelerator_options=AcceleratorOptions(device='cpu'), options=LayoutObjectDetectionOptions())
    page = SimpleNamespace(page_no=1, size=Size(width=image.width, height=image.height),
                           _backend=SimpleNamespace(is_valid=lambda: True),
                           predictions=SimpleNamespace(layout=None), get_image=lambda scale: image)
    model.predict_layout(SimpleNamespace(timings={}), [page])
    return docling_regions(page.predictions.layout, image.size, image.size)
