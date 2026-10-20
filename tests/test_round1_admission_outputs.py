"""Tiny offline corpus exercises the artifact and native-raster boundary."""
import hashlib
import json
from pathlib import Path

import pytest
from PIL import Image

from scripts.harvest.admit_round1 import build, wrap_label
from scripts.harvest.validate_round1_admission import validate


@pytest.fixture
def corpus(tmp_path):
    records, manifest, books = [], [], []
    for i in range(8):
        key = f"book{i}"
        year = 1860 + (i // 4)*10
        path = f"images/{key}-000001.png"
        (tmp_path / "images").mkdir(exist_ok=True)
        image = Image.new("L", (80, 160))
        image.putdata([(x + 3*y) % 256 for y in range(160) for x in range(80)])
        image.save(tmp_path / path)
        digest = hashlib.sha256((tmp_path / path).read_bytes()).hexdigest()
        books.append(dict(key=key, title=f"Book {i}"))
        manifest.append(dict(image=path, gate=dict(image_sha256=digest)))
        texts = [("Κοινή ελληνική γραμμή", [5, 10, 75, 50], .95, []),
                 (f"Σήμερα γράφουμε ελληνικά {i}", [5, 42, 75, 82], .95, []),
                 ("1", [5, 75, 75, 90], .95, []),
                 ("ελληνική λέξη 漢", [5, 110, 75, 150], .88, ["tall_box"])]
        for line, (text, bbox, confidence, flags) in enumerate(texts, 1):
            records.append(dict(id=f"{key}-p000001-l{line:04d}", page_id=f"{key}-p000001", page=1,
                book_key=key, year=year, decade=year, line_number=line, docai_text=text,
                bbox=bbox, confidence=confidence, flags=flags, image=path,
                image_sha256=digest, read_batch="synthetic"))
    for name, value in (("manifest.json", manifest), ("selection.json", dict(books=books))):
        (tmp_path / name).write_text(json.dumps(value))
    (tmp_path / "records.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
    return tmp_path


def run(corpus, sheets=False):
    return build(corpus, records_path=Path("records.jsonl"),
                 manifest_path=Path("manifest.json"),
                 selection_path=Path("selection.json"),
                 output_dir=Path("output"),
                 bulk_dir=Path("bulk"), holdout_count=4, dev_count=1,
                 make_sheets=sheets, emit=lambda *a, **k: None)


def test_artifacts_reconcile_and_full_native_pixel_replay(corpus):
    summary = run(corpus)
    assert summary["input_lines"] == 32
    assert summary["admitted_before_o5"] == 16
    assert summary["admitted"] == summary["crops"] == 12
    assert summary["rejected"] == 20 and summary["label_in_holdout"] == 4
    assert summary["per_split"] == dict(train=4, dev=2, test=6)
    assert summary["per_reason"]["foreign_script"] == 8
    assert summary["per_reason"]["low_confidence"] == summary["per_reason"]["tall_box"] == 8
    assert summary["per_reason"]["bad_page"] == 0
    result = validate(corpus, Path("output"), emit=lambda *a, **k: None)
    assert result["passed"] and result["native_pixels_checked"] == 12
    assert result["train_holdout_equal_labels"] == 0


def test_repeat_run_preserves_crop_bytes(corpus):
    run(corpus)
    before = {str(p): p.read_bytes() for p in (corpus / "bulk/crops").rglob("*.png")}
    admitted_before = (corpus / "output/admitted.jsonl").read_bytes()
    run(corpus)
    assert admitted_before == (corpus / "output/admitted.jsonl").read_bytes()
    assert before == {str(p): p.read_bytes() for p in (corpus / "bulk/crops").rglob("*.png")}


def test_changed_page_custody_fails_before_publication(corpus):
    path = corpus / "images/book0-000001.png"
    Image.new("L", (80, 160), 255).save(path)
    with pytest.raises(ValueError, match="page pixels differ"):
        run(corpus)
    assert not (corpus / "output/admitted.jsonl").exists()


def test_changed_crop_fails_validation(corpus):
    run(corpus)
    crop = next((corpus / "bulk/crops").rglob("*.png"))
    Image.new("L", (10, 10), 255).save(crop)
    with pytest.raises(AssertionError):
        validate(corpus, Path("output"), emit=lambda *a, **k: None)


def test_contact_sheets_small_class_and_empty_class(corpus):
    summary = run(corpus, sheets=True)
    assert summary["contact_sheets"]["greek_mono"]["count"] == 12
    assert summary["contact_sheets"]["cyrillic"]["count"] == 0
    assert all(c["font_size"] == 20 for c in summary["contact_sheets"].values())
    assert validate(corpus, Path("output"), emit=lambda *a, **k: None)["contact_sheets"] == 5


def test_label_wrap_keeps_every_character():
    from PIL import ImageDraw
    from scripts.harvest.admit_round1 import choose_font
    font, _ = choose_font()
    draw = ImageDraw.Draw(Image.new("L", (1, 1)))
    text = "ὁλόκληρη λέξη καὶ παντοῦ αβγδεζηθ" * 4
    lines = wrap_label(draw, text, font, 100)
    assert "".join(lines) == text and len(lines) > 1
    assert all(draw.textlength(line, font=font) <= 100 for line in lines)
