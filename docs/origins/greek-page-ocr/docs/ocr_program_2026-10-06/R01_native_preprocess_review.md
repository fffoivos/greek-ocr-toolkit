# R01 (el_PP-OCRv5_mobile_rec) native preprocessing review — 8 Oct 2026, coordinator

Reviewed on the node against the pinned PaddleOCR checkout `dab3fe35379033fdcb2d0e9572fac0b36c9a9ebf`
(`tools/infer/predict_rec.py::TextRecognizer.resize_norm_img`, lines 208–262) and the staged `R01/paddle/inference.yml`
(`RecResizeImg.image_shape: [3, 48, 320]`, `img_mode: BGR`, algorithm SVTR_LCNet):

- `rec_image_shape = [3, 48, 320]`; `rec_algorithm = SVTR_LCNet` (not RARE, so no hard 320 cap on the resized width).
- Per batch `max_wh_ratio = max(320/48, w/h)`; `imgW = int(48 * max_wh_ratio)`; `resized_w = min(ceil(48 * w/h), imgW)`.
- `cv2.resize(img, (resized_w, 48))` (default INTER_LINEAR), BGR as read by `cv2.imread`, float32, `/255`, `-0.5`, `/0.5`,
  right zero-padding to `imgW` (`padding_im[:, :, 0:resized_w] = resized_image`).
- The bench adapter `bench/e2_native.py::r01_preprocessor` calls the predictor's own `resize_norm_img` with
  `max_wh_ratio = max(320/48, w/h)` for a single image, i.e. exactly the single-image batch case above.

Recorded in `/opt/e2-assets/R01/spec.json` as `native_preprocess.reviewed: true` (the E2 config shipped with `reviewed: false`,
which the parity tool refuses). Parity crops: `/opt/e2-assets/parity/100_train_crops.jsonl` = 30 short + 30 very_long synthetic
train lines, 30 padded real imports (letterboxed) from the E1 f50 TRAIN pool, and 10 synthesized blank canvases (parity compares
native vs converted tensors, so blank inputs are a legitimate edge case; they carry no label).
