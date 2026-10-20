"""Unchanged existing collection-v2 crop spelling/physical path functions.

Source: greek-page-ocr-wave2/bench/e3_prepare.py
Source SHA256: ed85d309164963720858f12692a9cbd32afda7f4716f0ffd8f4d5d24eca54943
"""
from pathlib import Path, PurePosixPath


def rewrite_crop(crop, wave):
    parts = PurePosixPath(crop).parts
    prefix = ('docs', 'harvest', 'harvest_big', wave, 'crops')
    if parts[:5] != prefix or len(parts) != 7 or any(p in ('..', '.') for p in parts):
        raise ValueError(f'invalid toolkit crop spelling: {crop}')
    if not parts[-1].endswith('.png'):
        raise ValueError(f'expected PNG crop: {crop}')
    return str(PurePosixPath(wave, *parts[5:]))


def physical_crop(crops, spelling, layout):
    parts = PurePosixPath(spelling).parts
    if len(parts) != 3 or any(p in ('.', '..') for p in parts) or PurePosixPath(spelling).is_absolute():
        raise ValueError(f'invalid node crop spelling: {spelling}')
    relative = Path(parts[0], 'crops', *parts[1:]) if layout == 'toolkit' else Path(*parts)
    path = (Path(crops)/relative).resolve()
    if not path.is_relative_to(Path(crops).resolve()):
        raise ValueError(f'crop outside --crops: {spelling}')
    return path, relative.as_posix()
