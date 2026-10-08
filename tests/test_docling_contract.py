"""Ported offline Docling contracts; full original archived in docs/origins."""
from pathlib import Path
from types import SimpleNamespace
import json
import pytest

def test_factory_registration():
    pytest.importorskip("docling")
    from docling.models.factories import get_ocr_factory
    from greekocr.deploy.docling_plugin.options import GlossapiOcrOptions
    from greekocr.deploy.docling_plugin.model import GlossapiOcrModel

    factory = get_ocr_factory(allow_external_plugins=True)
    assert "glossapi" in factory.registered_kind
    assert factory.classes[GlossapiOcrOptions] is GlossapiOcrModel
    assert factory.registered_meta[GlossapiOcrOptions].plugin_name == "glossapi"
    assert "glossapi" not in get_ocr_factory(allow_external_plugins=False).registered_kind


def test_page_replacement_boundary(tmp_path, monkeypatch):
    pytest.importorskip("docling")
    import numpy as np
    from PIL import Image
    from docling.datamodel.accelerator_options import AcceleratorOptions
    from docling_core.types.doc import BoundingBox
    from docling_core.types.doc.page import BoundingRectangle, TextCell
    from greekocr.deploy.docling_plugin.model import GlossapiOcrModel
    from greekocr.deploy.docling_plugin.options import GlossapiOcrOptions

    route = tmp_path / "quality.jsonl"
    route.write_text(json.dumps(dict(filename="doc.pdf", pages=[
        dict(page=1, page_needs_ocr=True), dict(page=2, page_needs_ocr=False),
        dict(page=3, page_needs_ocr=True, chars=0, decision="scanned_page", image_area_ratio=1)])) + "\n")
    def cell(text, from_ocr=False):
        return TextCell(index=0, text=text, orig=text, from_ocr=from_ocr,
                        rect=BoundingRectangle.from_bounding_box(BoundingBox(l=2,t=2,r=40,b=14)))
    def page(number, cells):
        parsed = SimpleNamespace(textline_cells=cells, has_lines=bool(cells),
                                 word_cells=[cell("bad word"), cell("OCR word", True)],
                                 char_cells=[cell("x")], has_words=True, has_chars=True)
        return SimpleNamespace(page_no=number, parsed_page=parsed, size=SimpleNamespace(height=30),
                               get_image=lambda **kwargs: Image.fromarray(np.full((90,150),255,dtype=np.uint8)))
    pages = [page(1,[cell("corrupt")]), page(2,[cell("keep")]), page(3,[])]
    original_rect = pages[0].parsed_page.textline_cells[0].rect.model_dump()
    clean = pages[1].parsed_page
    options = GlossapiOcrOptions(checkpoint=tmp_path/"unused.pt",codec=tmp_path/"unused.json",
                                routing_sidecar=route)
    model = GlossapiOcrModel(enabled=True, artifacts_path=None, options=options,
                            accelerator_options=AcceleratorOptions(device="cpu"))
    monkeypatch.setattr(model,"_get_recognizer",lambda:SimpleNamespace(recognize=lambda strips:[("Αθήνα",.9)]*len(strips)))
    out = list(model(SimpleNamespace(input=SimpleNamespace(file=Path("doc.pdf"))), pages))
    assert out == pages
    replaced = out[0].parsed_page
    assert replaced.textline_cells[0].text == "Αθήνα"
    assert replaced.textline_cells[0].from_ocr
    assert replaced.textline_cells[0].rect.model_dump() == original_rect
    assert [c.text for c in replaced.word_cells] == ["OCR word"]
    assert replaced.has_words and not replaced.char_cells and not replaced.has_chars
    assert out[1].parsed_page is clean and clean.textline_cells[0].text == "keep"
    assert not options.force_full_page_ocr
    assert [(r["page"],r["status"]) for r in model.call_log] == [(1,"replaced"),(3,"unsupported")]
    assert model.unsupported_counts == {"no_textlayer_lines": 1}
    options.mode = "detector"
    assert list(model(SimpleNamespace(input=SimpleNamespace(file=Path("doc.pdf"))), [pages[0]])) == [pages[0]]
    assert model.unsupported_counts["detector_out_of_scope"] == 1


@pytest.mark.parametrize("chars,decision,image_ratio,unsupported", [
    (2, "scanned_page", .85, True),
    (3, "scanned_page", .47, True),
    (5, "scanned_page", .38, True),
    (49, "scanned_page", .36, True),
    (50, "scanned_page", .36, False),
    (3, "garbage_greek_text", 0, False),
    (3, "garbage_greek_text", .5, True),
    (66, "garbage_greek_text", 0, False),
])
def test_raster_body_keeps_native_cells_and_records_recognition(
        tmp_path, monkeypatch, chars, decision, image_ratio, unsupported):
    pytest.importorskip("docling")
    from PIL import Image
    from docling.datamodel.accelerator_options import AcceleratorOptions
    from docling_core.types.doc import BoundingBox
    from docling_core.types.doc.page import BoundingRectangle, TextCell
    from greekocr.deploy.docling_plugin.model import GlossapiOcrModel
    from greekocr.deploy.docling_plugin.options import GlossapiOcrOptions

    route = tmp_path/"route.jsonl"
    route.write_text(json.dumps(dict(filename="arbitrary.pdf", pages=[dict(
        page=7, page_needs_ocr=True, chars=chars, decision=decision,
        image_area_ratio=image_ratio)]))+"\n")
    cell = TextCell(index=0, text="77", orig="77", from_ocr=False,
                    rect=BoundingRectangle.from_bounding_box(BoundingBox(l=2,t=2,r=40,b=14)))
    parsed = SimpleNamespace(textline_cells=[cell], has_lines=True, word_cells=[cell],
                             char_cells=[cell], has_words=True, has_chars=True)
    page = SimpleNamespace(page_no=7, parsed_page=parsed, size=SimpleNamespace(height=30),
                           get_image=lambda **kw: Image.new("L", (150,90), 255))
    options = GlossapiOcrOptions(checkpoint=tmp_path/"unused.pt", codec=tmp_path/"unused.json",
                                routing_sidecar=route, call_log=tmp_path/"calls.jsonl")
    model = GlossapiOcrModel(enabled=True, artifacts_path=None, options=options,
                            accelerator_options=AcceleratorOptions(device="cpu"))
    calls = []
    def recognize(strips):
        calls.append(len(strips))
        return [("78", .9)]
    monkeypatch.setattr(model, "_get_recognizer", lambda: SimpleNamespace(recognize=recognize))
    assert list(model(SimpleNamespace(input=SimpleNamespace(file=Path("arbitrary.pdf"))), [page])) == [page]
    record = json.loads(options.call_log.read_text())
    assert calls == [1] and record["recognition_performed"]
    assert record["lines"][0]["text"] == "78"
    assert record["body_support"]["textlayer_chars"] == chars
    assert record["body_support"]["chars_source"] == "sidecar"
    assert record["status"] == ("unsupported" if unsupported else "replaced")
    assert record["installed"] is not unsupported
    if unsupported:
        assert record["reason"] == "raster_body" and model.unsupported_counts == {"raster_body": 1}
        assert parsed.textline_cells == [cell] and parsed.word_cells == parsed.char_cells == [cell]
        assert cell.text == "77" and not cell.from_ocr
    else:
        assert parsed.textline_cells[0].text == "78" and parsed.textline_cells[0].from_ocr


def test_checkpoint_failure_instructions_reference_available_export(tmp_path, monkeypatch):
    from greekocr.deploy.docling_plugin.recognizer import ckpt_io
    def reject(*args, **kwargs):
        assert kwargs["weights_only"] is True
        raise ValueError("unsafe resume object")
    monkeypatch.setattr(ckpt_io.torch, "load", reject)
    with pytest.raises(RuntimeError, match="trusted training/export environment") as exc:
        ckpt_io.load_model_weights(str(tmp_path/"legacy.pt"))
    assert "convert_pt_to_safetensors" not in str(exc.value)


def test_conflicting_sidecar_support_metadata_fails_closed(tmp_path):
    from docling.datamodel.accelerator_options import AcceleratorOptions
    from greekocr.deploy.docling_plugin.model import GlossapiOcrModel
    from greekocr.deploy.docling_plugin.options import GlossapiOcrOptions
    route = tmp_path/"route.jsonl"
    route.write_text("".join(json.dumps(dict(filename="doc.pdf", pages=[dict(
        page=1, page_needs_ocr=True, chars=chars, decision="scanned_page")]))+"\n"
        for chars in [3, 300]))
    options = GlossapiOcrOptions(checkpoint=Path("unused.pt"), codec=Path("unused.json"),
                                routing_sidecar=route)
    with pytest.raises(ValueError, match="conflicting routing rows"):
        GlossapiOcrModel(enabled=True, artifacts_path=None, options=options,
                        accelerator_options=AcceleratorOptions(device="cpu"))


def test_checkpoint_pin_rejects_changed_artifact(tmp_path):
    pytest.importorskip("docling")
    from docling.datamodel.accelerator_options import AcceleratorOptions
    from greekocr.deploy.docling_plugin.model import GlossapiOcrModel
    from greekocr.deploy.docling_plugin.options import GlossapiOcrOptions
    checkpoint = tmp_path/"changed.pt"; checkpoint.write_bytes(b"changed")
    options = GlossapiOcrOptions(checkpoint=checkpoint,codec=Path("unused.json"),
                                replace_policy="all",checkpoint_sha256="0"*64)
    model = GlossapiOcrModel(enabled=True,artifacts_path=None,options=options,
                            accelerator_options=AcceleratorOptions(device="cpu"))
    with pytest.raises(ValueError,match="sha256 mismatch"):
        model._get_recognizer()


