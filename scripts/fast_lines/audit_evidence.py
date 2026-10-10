"""Audit cached development evidence and render selected nine-detector comparisons."""
import argparse
import hashlib
import json
from pathlib import Path
from statistics import median
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(".astra/fast_lines")
OUT = ROOT / "out/q6_review"
PARKED = "s2-6419488b7f8e69fd20da-p00001"


def read(path):
    return json.loads(path.read_text())


def aggregate(rows):
    return {"pages": len(rows), "totals": {field: sum(v[field] for v in rows.values())
            for field in next(iter(rows.values())) if field != "line_h"},
            "medians": {field: median(v[field] for v in rows.values())
                        for field in ("paddle_s", "extra_s", "ink_regions")}}


def ours_items(lines):
    for line in lines:
        if line.get("discounted"):
            continue
        n = len(line["top"])
        xs = [line["x0"] + (line["x1"] - line["x0"]) * i / max(1, n - 1) for i in range(n)]
        yield {"polygon": list(zip(xs, line["top"])) + list(zip(xs, line["bottom"]))[::-1],
               "baseline": list(zip(xs, line["baseline"]))}


def comparison(key, models):
    with Image.open(Path(".astra/pages") / (key + ".png")) as source:
        source = source.convert("RGB")
        w, h = source.size
        panels = []
        for model in models + ["ours"]:
            if model == "ours":
                items = list(ours_items(read(ROOT / "ours_lines" / (key + ".lines.json"))))
                unit = "kept"
            else:
                record = read(ROOT / "detectors" / model / (key + ".json"))
                items, unit = record["items"], record["unit"]
            thumb = ImageOps.contain(source, (490, 690))
            sx, sy = thumb.width / w, thumb.height / h
            draw = ImageDraw.Draw(thumb)
            for item in items:
                if item.get("discounted"):
                    continue
                pts = [(x * sx, y * sy) for x, y in item["polygon"]]
                if len(pts) > 1:
                    draw.line(pts + pts[:1], fill=(0, 110, 220), width=1)
                if item.get("baseline"):
                    draw.line([(x * sx, y * sy) for x, y in item["baseline"]], fill=(210, 50, 0), width=1)
            panel = Image.new("RGB", (500, 720), "#eeeeee")
            panel.paste(thumb, ((500 - thumb.width) // 2, 28))
            ImageDraw.Draw(panel).text((3, 4), f"{model}: {len(items)} {unit}", fill="black")
            panels.append(panel)
        canvas = Image.new("RGB", (2500, 1440), "white")
        for i, panel in enumerate(panels):
            canvas.paste(panel, ((i % 5) * 500, (i // 5) * 720))
        canvas.save(OUT / (key + "_detectors.jpg"), quality=92)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages", nargs="*", default=[], help="Dev-page prefixes to render")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    keys = sorted(p.stem for p in Path(".astra/pages").glob("*.png"))
    assert len(keys) == 54
    summary_path = ROOT / "prototype/stages_summary.json"
    stats = read(summary_path)["pages"]
    assert set(stats) == set(keys)
    models = sorted(p.name for p in (ROOT / "detectors").iterdir() if p.is_dir())
    audit = {"stage_sha256": hashlib.sha256(summary_path.read_bytes()).hexdigest(),
             "all": aggregate(stats), "upright": aggregate({k: v for k, v in stats.items() if k != PARKED}),
             "parked": PARKED, "models": {}, "pages": {}}
    for model in models:
        records = [read(ROOT / "detectors" / model / (key + ".json")) for key in keys]
        audit["models"][model] = {"pages": len(records), "items": sum(len(r["items"]) for r in records),
                                    "median_s_cached": median(r["seconds"] for r in records),
                                    "units": sorted({r["unit"] for r in records})}
    for key in keys:
        lines = read(ROOT / "ours_lines" / (key + ".lines.json"))
        kept = [l for l in lines if not l.get("discounted")]
        audit["pages"][key] = {"stages": stats[key], "ours_raw_kept": len(kept),
            "ours_discounted": len(lines) - len(kept),
            "geometry_sources": {s: sum(l.get("geometry_source") == s for l in kept)
                                 for s in sorted({l.get("geometry_source", "unknown") for l in kept})},
            "detector_items": {m: len(read(ROOT / "detectors" / m / (key + ".json"))["items"]) for m in models}}
        if any(key.startswith(prefix) for prefix in args.pages):
            comparison(key, models)
    (OUT / "audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps({k: v for k, v in audit.items() if k != "pages"}, indent=2))


if __name__ == "__main__":
    main()
