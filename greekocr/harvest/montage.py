"""Native-pixel montage layout and offline Google box assignment (T14).

This module never calls a reader. It deliberately leaves the pilot's older
montage implementation and the production/single-crop path unchanged.
"""
from __future__ import annotations

import hashlib
import io
import math
from pathlib import Path
import statistics
from typing import Any, Iterable
import unicodedata

from PIL import Image, ImageDraw

from .core import edits, list_return
from .readers import atomic, polygon_box, response_pieces

__all__ = ["build_montages", "assign_lines", "response_lines", "response_symbols",
           "assign_symbols", "compare_nfd", "summarise"]


def _render(records):
    images = []
    for record in records:
        with Image.open(record["straight_crop"]) as source:
            if source.mode not in ("L", "RGB"):
                raise ValueError("native crops must be 8-bit L or RGB, without alpha")
            images.append(source.copy())
    mode = "L" if all(image.mode == "L" for image in images) else "RGB"
    width = max(image.width for image in images)
    gaps = [max(60, left.height, right.height) for left, right in zip(images, images[1:])]
    height = sum(image.height for image in images) + sum(gaps)
    image = Image.new(mode, (width, height), 255 if mode == "L" else (255, 255, 255))
    draw = ImageDraw.Draw(image)
    boxes, separators = {}, []
    y = 0
    for i, (record, crop) in enumerate(zip(records, images)):
        image.paste(crop, (0, y))
        boxes[record["id"]] = dict(x0=0, x1=crop.width, y0=y, y1=y + crop.height,
            width=crop.width, height=crop.height, crop=str(Path(record["straight_crop"]).resolve()),
            crop_sha256=hashlib.sha256(Path(record["straight_crop"]).read_bytes()).hexdigest())
        y += crop.height
        if i < len(gaps):
            gap = gaps[i]
            rule_y = y + (gap - 2) // 2
            draw.rectangle((0, rule_y, width - 1, rule_y + 1),
                           fill=153 if mode == "L" else (153, 153, 153))
            separators.append(dict(y0=y, y1=y + gap, rule_y0=rule_y, rule_y1=rule_y + 2))
            y += gap
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    return stream.getvalue(), dict(width=width, height=height, mode=mode,
                                  boxes=boxes, separators=separators)


def build_montages(records: Iterable[dict[str, Any]], n: int, images_dir: str | Path,
                   maps_dir: str | Path, *, max_width: int = 2600,
                   max_height: int = 10000, max_png_bytes: int = 8_000_000) -> list[dict[str, Any]]:
    """Stack up to N crops, preserving pixels; split on height or encoded size.

    N is 10, 20 or 40. Bands and rules use half-open coordinates. Each gap is
    max(60, the two adjacent native crop heights); a centred 2px 40%-black rule
    is grey 153 on white 255. A too-large singleton fails instead of resizing.
    Returns maps, also saved separately from the bulk PNG files.
    """
    if isinstance(n, bool) or not isinstance(n, int) or n not in (10, 20, 40):
        raise ValueError("N must be 10, 20 or 40")
    records = list(records)
    if len({record["id"] for record in records}) != len(records):
        raise ValueError("crop IDs must be unique")
    if any(isinstance(value, bool) or not isinstance(value, int) or not 0 < value <= ceiling
           for value, ceiling in ((max_width, 2600), (max_height, 10000), (max_png_bytes, 8_000_000))):
        raise ValueError("integer size limits must be positive and cannot exceed T14 ceilings")
    for record in records:
        with Image.open(record["straight_crop"]) as crop:
            if crop.width > max_width:
                raise ValueError("crop exceeds montage width; native pixels cannot be resized")
    images_dir, maps_dir = Path(images_dir), Path(maps_dir)
    images_dir.mkdir(parents=True, exist_ok=True)
    maps_dir.mkdir(parents=True, exist_ok=True)
    result = []

    def emit(group, split_reasons):
        sizes = []
        for record in group:
            with Image.open(record["straight_crop"]) as crop:
                sizes.append(crop.size)
        height = sum(h for _, h in sizes) + sum(max(60, a[1], b[1]) for a, b in zip(sizes, sizes[1:]))
        if height > max_height:
            if len(group) == 1:
                raise ValueError("native singleton exceeds montage height/PNG limit")
            midpoint = len(group) // 2
            emit(group[:midpoint], split_reasons + ["height"])
            emit(group[midpoint:], split_reasons + ["height"])
            return
        data, layout = _render(group)
        if layout["height"] > max_height or len(data) > max_png_bytes:
            if len(group) == 1:
                raise ValueError("native singleton exceeds montage height/PNG limit")
            reason = "height" if layout["height"] > max_height else "png_bytes"
            midpoint = len(group) // 2
            emit(group[:midpoint], split_reasons + [reason])
            emit(group[midpoint:], split_reasons + [reason])
            return
        name = f"n{n:02d}-{len(result):03d}"
        image_path, map_path = images_dir / (name + ".png"), maps_dir / (name + ".map.json")
        # Byte-identical reruns do not modify bulk images or trigger new requests.
        if image_path.exists() and image_path.read_bytes() != data:
            raise ValueError("existing montage changed; choose a new evidence directory")
        if not image_path.exists():
            image_path.write_bytes(data)
        mapping = dict(schema="greekocr-montage-1", n=n, actual_n=len(group),
            image=str(image_path.resolve()), image_sha256=hashlib.sha256(data).hexdigest(),
            png_bytes=len(data), map=str(map_path.resolve()), split_reasons=split_reasons,
            limits=dict(width=max_width, height=max_height, png_bytes=max_png_bytes), **layout)
        atomic(map_path, mapping)
        result.append(mapping)

    for start in range(0, len(records), n):
        emit(records[start:start + n], [])
    return result


def response_lines(engine: str, raw: dict[str, Any], size: tuple[int, int]) -> list[dict[str, Any]]:
    """Engine lines: DocAI line layouts; Vision detectedBreak symbol box unions.

    Vision paragraphs end a line even when no explicit final break is present.
    DocAI paragraph layouts are used only when a page has no line layouts.
    Text-only responses cannot establish geometry and fail closed as lost.
    """
    if engine not in ("vision", "docai"):
        raise ValueError("unknown reader")
    if engine == "vision":
        return response_pieces(engine, raw, size)
    document = raw["document"]
    text = document.get("text", "")
    result = []
    for page in document.get("pages", []):
        kind = "lines" if page.get("lines") else "paragraphs"
        for node in page.get(kind, []):
            layout = node.get("layout", {})
            box = polygon_box(layout.get("boundingPoly", {}), size)
            if box:
                value = "".join(text[int(s.get("startIndex", 0)):int(s["endIndex"])]
                    for s in layout.get("textAnchor", {}).get("textSegments", []))
                result.append(dict(text=value, bbox=box, confidence=layout.get("confidence"),
                                   source=kind))
    return result


def _hits(box, boxes):
    if len(box) != 4 or not all(math.isfinite(v) for v in box):
        raise ValueError("box must contain four finite pixel coordinates")
    height = box[3] - box[1]
    if height <= 0 or box[2] <= box[0]:
        return []
    # Band assignment is by height, deliberately independent of line width.
    return [(ident, overlap / height) for ident, band in boxes.items()
            if (overlap := max(0, min(box[3], band["y1"]) - max(box[1], band["y0"]))) > 0]


def assign_lines(lines: Iterable[dict[str, Any]], mapping: dict[str, Any], *,
                 threshold: float = .70) -> dict[str, Any]:
    """Assign >=70% box height to a crop; cross-band boxes mark every hit merged.

    Status flags are independent: a merged crop can also be lost or split.
    `status` uses merged > lost > split > ok; counts use the boolean flags.
    Split side-by-side pieces use the pilot list-return rule. Stacked splits
    retain their reading separated by LF and remain rejected, without repair.
    """
    if not .5 < threshold <= 1:
        raise ValueError("assignment threshold must be >.5 and <=1")
    boxes = mapping["boxes"]
    groups = {ident: [] for ident in boxes}
    merged = {ident: [] for ident in boxes}
    audit = []
    for index, line in enumerate(lines):
        hits = _hits(line["bbox"], boxes)
        entry = dict(index=index, line=line, overlaps=dict(hits), crop_id=None)
        if len(hits) > 1:
            entry["status"] = "merged"
            for ident, _ in hits:
                merged[ident].append(index)
        elif hits and hits[0][1] >= threshold:
            ident = hits[0][0]
            groups[ident].append(dict(line, line_index=index))
            entry.update(status="assigned", crop_id=ident)
        else:
            entry["status"] = "unassigned"
        audit.append(entry)
    crops = {}
    for ident, pieces in groups.items():
        parsed = list_return(pieces)
        text = parsed["text"]
        if parsed["rejected"] and pieces:
            text = "\n".join(p["text"].strip() for p in sorted(pieces, key=lambda p: (p["bbox"][1], p["bbox"][0])))
        is_merged, lost, split = bool(merged[ident]), not pieces, len(pieces) >= 2
        crops[ident] = dict(text=text, status="merged" if is_merged else "lost" if lost else "split" if split else "ok",
            merged=is_merged, lost=lost, split=split, assigned_line_count=len(pieces),
            merged_line_indices=merged[ident], pieces=pieces, flags=parsed["flags"],
            dropped=parsed["dropped"], rejected=is_merged or parsed["rejected"])
    return dict(crops=crops, lines=audit, merged_box_count=sum(a["status"] == "merged" for a in audit),
                unassigned_box_count=sum(a["status"] == "unassigned" for a in audit))


def response_symbols(engine: str, raw: dict[str, Any], size: tuple[int, int]) -> list[dict[str, Any]]:
    """Extract symbol text, native boxes and confidence from unchanged raw JSON."""
    result = []
    if engine == "vision":
        for page in raw.get("responses", [{}])[0].get("fullTextAnnotation", {}).get("pages", []):
            for block in page.get("blocks", []):
                for paragraph in block.get("paragraphs", []):
                    for word in paragraph.get("words", []):
                        for symbol in word.get("symbols", []):
                            result.append(dict(text=symbol.get("text", ""), confidence=symbol.get("confidence"),
                                bbox=polygon_box(symbol.get("boundingBox", {}), size)))
    elif engine == "docai":
        document = raw["document"]
        text = document.get("text", "")
        for page in document.get("pages", []):
            for symbol in page.get("symbols", []):
                layout = symbol.get("layout", {})
                value = "".join(text[int(s.get("startIndex", 0)):int(s["endIndex"])]
                    for s in layout.get("textAnchor", {}).get("textSegments", []))
                result.append(dict(text=value, confidence=layout.get("confidence"),
                    bbox=polygon_box(layout.get("boundingPoly", {}), size)))
    else:
        raise ValueError("unknown reader")
    return result


def assign_symbols(symbols: Iterable[dict[str, Any]], mapping: dict[str, Any], *,
                   threshold: float = .70) -> dict[str, Any]:
    """Apply the same band rule independently to symbol-confidence observations."""
    groups = {ident: [] for ident in mapping["boxes"]}
    unassigned = []
    for symbol in symbols:
        hits = _hits(symbol["bbox"], mapping["boxes"]) if symbol["bbox"] else []
        if len(hits) == 1 and hits[0][1] >= threshold:
            groups[hits[0][0]].append(symbol)
        else:
            unassigned.append(symbol)
    return dict(crops=groups, unassigned=unassigned)


def compare_nfd(single: str, montage: str) -> dict[str, Any]:
    """Exact NFD codepoint equality and Levenshtein CER, without whitespace folding."""
    a, b = unicodedata.normalize("NFD", single), unicodedata.normalize("NFD", montage)
    distance = edits(a, b)
    return dict(identical=a == b, nfd_edits=distance, single_nfd_length=len(a),
                nfd_cer=distance / max(1, len(a)))


def summarise(comparisons: Iterable[dict[str, Any]], montage_count: int) -> dict[str, Any]:
    """Aggregate a reader/N cohort, including symbol-weighted confidence means."""
    rows = list(comparisons)
    if not rows:
        raise ValueError("empty cohort")
    result = dict(lines=len(rows), identical_count=sum(r["identical"] for r in rows),
        identical_pct=100 * sum(r["identical"] for r in rows) / len(rows),
        median_nfd_cer=statistics.median(r["nfd_cer"] for r in rows),
        merged=sum(r["merged"] for r in rows), lost=sum(r["lost"] for r in rows),
        split=sum(r["split"] for r in rows), rejected=sum(r["rejected"] for r in rows),
        montages=montage_count, cost_per_1000_lines_usd=round(montage_count * .0015 * 1000 / len(rows), 6))
    for prefix in ("single", "montage"):
        values = [float(symbol["confidence"]) for row in rows for symbol in row[prefix + "_symbols"]
                  if symbol.get("confidence") is not None]
        result[prefix + "_symbol_count"] = len(values)
        result[prefix + "_mean_symbol_confidence"] = statistics.mean(values) if values else None
    a, b = result["single_mean_symbol_confidence"], result["montage_mean_symbol_confidence"]
    result["confidence_delta"] = b - a if a is not None and b is not None else None
    result["adopt"] = (result["identical_pct"] >= 97 and not result["merged"] and not result["lost"]
                       and all(r.get("service_status", "ok") == "ok" for r in rows))
    return result
