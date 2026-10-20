"""Streaming JSONL and optional Arrow shard I/O, shared by annotation and font fitting."""
from __future__ import annotations

import base64
from io import BytesIO
import json
from pathlib import Path
from typing import Any, Iterator

from PIL import Image


def iter_records(path: Path) -> Iterator[tuple[dict[str, Any], Path]]:
    if path.is_dir():
        files = sorted(path.rglob('shard-*.parquet'))
        if not files:
            files = sorted(path.rglob('*.jsonl'))
        if not files:
            raise ValueError(f'no JSONL or shard-*.parquet files in {path}')
        for file in files:
            yield from iter_records(file)
    elif path.suffix == '.parquet':
        try:
            import pyarrow.parquet as pq
        except ImportError as exc:
            raise ImportError('Parquet shard I/O requires the optional pyarrow package') from exc
        for batch in pq.ParquetFile(path).iter_batches(batch_size=256):
            for row in batch.to_pylist():
                yield row, path.parent
    else:
        with path.open(encoding='utf-8') as stream:
            for number, line in enumerate(stream, 1):
                if line.strip():
                    row = json.loads(line)
                    if not isinstance(row, dict):
                        raise ValueError(f'{path}:{number}: expected a JSON object')
                    yield row, path.parent


def record_image(row: dict[str, Any], root: Path) -> tuple[Image.Image, Path | None]:
    if row.get('image_png') is not None:
        value = row['image_png']
        payload = base64.b64decode(value, validate=True) if isinstance(value, str) else value
        with Image.open(BytesIO(payload)) as image:
            image.load()
            return image.copy(), None
    name = next((row[k] for k in ('crop_path', 'image_path', 'file', 'path') if row.get(k)), None)
    if name is None:
        raise ValueError('line record needs crop_path/image_path/file or image_png')
    path = Path(name)
    path = (root / path).resolve() if not path.is_absolute() else path.resolve()
    with Image.open(path) as image:
        image.load()
        return image.copy(), path


def record_text(row: dict[str, Any]) -> str | None:
    return next((row[k] for k in ('text', 'gt_nfc', 'gt_nfd', 'gt', 'layer') if row.get(k) is not None), None)
