"""Make labelled contact sheets of existing evidence; no detection or filtering."""
from pathlib import Path
import argparse
from PIL import Image, ImageDraw, ImageOps


def sheet(paths, labels, dest, columns, width, height):
    canvas = Image.new("RGB", (columns * width, ((len(paths) + columns - 1) // columns) * height), "#dddddd")
    draw = ImageDraw.Draw(canvas)
    for i, (path, label) in enumerate(zip(paths, labels)):
        x, y = (i % columns) * width, (i // columns) * height
        with Image.open(path) as source:
            thumb = ImageOps.contain(source.convert("RGB"), (width - 8, height - 28))
            canvas.paste(thumb, (x + (width - thumb.width) // 2, y + 24))
        draw.text((x + 4, y + 4), label, fill="black")
    canvas.save(dest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(".astra/fast_lines"))
    args = parser.parse_args()
    out = args.root / "out/q6_review"
    out.mkdir(parents=True, exist_ok=True)
    pages = sorted(Path(".astra/pages").glob("*.png"))
    assert len(pages) == 54
    for start in range(0, len(pages), 6):
        batch = pages[start:start + 6]
        sheet(batch, [p.stem for p in batch], out / f"pages_{start // 6 + 1:02d}.jpg", 3, 600, 800)
    for page in pages:
        key = page.stem
        paths = sorted((args.root / "stage_images").glob(f"{key}_*.jpg"))
        assert len(paths) == 7, (key, len(paths))
        sheet(paths, [p.stem.rsplit("_", 1)[-1] for p in paths], out / f"{key}_stages.jpg", 7, 360, 560)
    print(f"{len(pages)} pages; {len(pages)} seven-stage sheets; output: {out}")


if __name__ == "__main__":
    main()
