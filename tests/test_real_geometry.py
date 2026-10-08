"""O4d G1: recorded scan geometry and independent negative/synthetic contracts."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import pytest
from scipy import ndimage

from greekocr.cli import main
from greekocr.real.geometry import (
    GEOMETRY_POLICY, BASELINE_CLUSTER_TOLERANCE,
    DEFAULT_PAD, SCAN_MAX_CURL_PX, SCAN_MIN_INK_COVERAGE, SCAN_MAX_INK_COVERAGE,
    Admission, BaselineCurve, GeometryDiagnostics, TextLayerBox, hyphen_at_line_end,
    ink_components, refine_line, refine_page_lines, scan_admission, split_multiline,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT/'tests/fixtures/o4d_lines'
INDEX = json.loads((FIXTURES/'index.json').read_text())
ROWS = INDEX['lines']
LEGACY = json.loads((ROOT/'tests/data/o4d_legacy_admission.json').read_text())
REGRESSIONS = sorted((FIXTURES/'regressions').glob('*_old.png'))


def open_strip(row):
    with Image.open(FIXTURES/row['file']) as im:
        return im.convert('L')


@pytest.mark.parametrize('record', LEGACY['rows'], ids=lambda r: r['file'])
def test_independent_old_contract_before_geometry_change(record):
    """Replay captured old diagnostics, not a relaxed copy of the vendor rule."""
    from greekocr._vendor.bench.admission import admit, ink_diagnostics, char_ink_diagnostics
    path = FIXTURES/record['file']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256']
    source = next(r for r in ROWS if r['file'] == record['file'])
    image = open_strip(source)
    old = dict(text=source['layer'], bbox_pixel=[0, 0, *image.size])
    old.update(ink_diagnostics(image, [0, 0, *image.size]))
    old.update(char_ink_diagnostics(image, []))
    admit(old)
    assert old == record['diagnostics']
    assert not old['admitted'] and old['unexplained_ink']
    decision = scan_admission(old, profile='born_digital')
    assert list(decision.reject_reasons) == old['reject_reasons']


def test_bound_fixture_and_vendor_identity():
    assert len(ROWS) == 44
    assert hashlib.sha256((FIXTURES/'index.json').read_bytes()).hexdigest() == LEGACY['index_sha256']
    assert hashlib.sha256((ROOT/'greekocr/_vendor/bench/admission.py').read_bytes()).hexdigest() == LEGACY['vendor_sha256']
    # No owner classifications are invented: these fixtures arrived without notes.
    assert INDEX['owner_notes'] == {}


def test_two_visible_baselines_split_and_labels_remain_unassigned():
    # line01 visibly includes an upper line and a lower neighbour across the width.
    row = ROWS[0]
    image = open_strip(row)
    boxes = split_multiline((0, 0, *image.size), ink_components(image))
    assert len(boxes) == 2
    assert boxes[0][1] < boxes[1][1]
    assert boxes[0][3] < boxes[1][3]
    lines = refine_page_lines(image, [TextLayerBox((0, 0, *image.size), row['layer'])])
    assert len(lines) == 2
    assert {line.split_index for line in lines} == {0, 1}
    assert all(line.input_index == 0 and line.parent_box == (0, 0, *image.size) for line in lines)
    assert all(line.text is None and line.text_assignment_required for line in lines)
    assert all(line.source_text == row['layer'] for line in lines)
    assert all(line.diagnostics.n_baselines == 1 for line in lines)
    assert all(line.diagnostics.hyphen_missing_in_label is None for line in lines)


def selected_scan_mask(image, components):
    """Independent connected-pixel census of the documented scan ink definition."""
    a = np.asarray(image, dtype=np.int16)
    background = np.asarray(image.filter(ImageFilter.BoxBlur(15)), dtype=np.int16)
    labels, _ = ndimage.label((a < 80) | ((a < 220) & (background-a >= 12)),
                              structure=np.ones((3, 3)))
    return np.isin(labels, [c.id for c in components])


def row_profiles(mask):
    width = mask.shape[1]
    return [mask[:, :int(.15*width)].sum(axis=1),
            mask[:, int(.85*width):].sum(axis=1)]


def profile_center(profile):
    return float(np.dot(np.arange(len(profile)), profile)/profile.sum())


@pytest.mark.parametrize('row', [ROWS[0], ROWS[5]], ids=['downward-end', 'upward-end'])
def test_curled_fixture_end_profiles_preserve_ink_and_flatten(row):
    image = open_strip(row)
    result = refine_line(image, (0, 0, *image.size), pad=DEFAULT_PAD)
    # Measure the chosen track, independently of neighbouring components now
    # deliberately protected by the wide v2 band. The raster also retains paper
    # and light stroke edges, so its dark-pixel total need not equal component area.
    target = result.diagnostics.baseline_clusters[result.diagnostics.selected_cluster_index]
    body = [c for c in result.kept_components if c.id in target['component_ids']]
    before_mask = selected_scan_mask(image, body)
    ys, xs = np.nonzero(before_mask)
    out_ys = np.array([y-round(result.curve.evaluate(x))+result.ascent for y, x in zip(ys, xs)])
    out_xs = xs-result.refined_box[0]
    assert np.all(np.asarray(result.image)[out_ys, out_xs] == np.asarray(image)[ys, xs])
    after_mask = np.zeros((result.image.height, image.width), dtype=bool)
    after_mask[out_ys, xs] = True
    before, after = row_profiles(before_mask), row_profiles(after_mask)
    # Both terminal 15% regions retain every selected pixel, with white row margins.
    assert [int(p.sum()) for p in before] == [int(p.sum()) for p in after]
    assert all(p.sum() > 500 and p[:2].sum() == 0 and p[-2:].sum() == 0 for p in after)
    before_gap = abs(profile_center(before[0])-profile_center(before[1]))
    after_gap = abs(profile_center(after[0])-profile_center(after[1]))
    assert before_gap > 20 and after_gap < .40*before_gap
    assert result.diagnostics.retained_ink_fraction == 1.0
    assert after_mask.sum() == sum(c.area for c in body)
    assert result.dropped_components and result.diagnostics.source_n_baselines == 2


def preservation_census(image, result):
    """Independent page-to-strip mapping and dark-pixel count, no component mask."""
    x0, y0, x1, y1 = result.source_box
    columns = np.arange(x0, x1)
    baseline = np.array([result.curve.evaluate(int(x)) for x in columns])[None, :]
    rows = np.arange(y0, y1)[:, None]
    height = result.diagnostics.x_height_px
    band = (rows >= baseline-1.9*height) & (rows <= baseline+.6*height)
    marks = band & (rows < baseline-height)
    source = np.asarray(image.crop(result.source_box))
    output_rows = rows-np.round(baseline).astype(int)+result.ascent
    output_columns = (columns-result.refined_box[0])[None, :]
    valid = (output_rows >= 0) & (output_rows < result.image.height)
    output = np.asarray(result.image)[np.clip(output_rows, 0, result.image.height-1), output_columns]
    before = source < 220
    after = (output < 220) & valid
    return source, output, band, valid, [
        (int((before & zone).sum()), int((after & zone).sum())) for zone in (band, marks)]


@pytest.mark.parametrize('path', [*[FIXTURES/r['file'] for r in ROWS], *REGRESSIONS], ids=lambda p: p.name)
def test_v2_band_and_diacritic_ink_preservation_on_every_original(path):
    with Image.open(path) as im:
        image = im.convert('L')
    result = refine_line(image, (0, 0, *image.size))
    source, output, band, valid, counts = preservation_census(image, result)
    (band_old, band_new), (marks_old, marks_new) = counts
    assert band_old > 0
    assert band_new >= .97*band_old
    assert marks_new >= .95*marks_old
    # Stronger than an ink count: every in-band source intensity is unchanged.
    assert np.all(valid[band])
    assert np.array_equal(source[band], output[band])
    diag = result.diagnostics
    assert diag.policy == GEOMETRY_POLICY == 'o4d-local-line-geometry-v2'
    assert (diag.band_ink_original, diag.band_ink_refined) == (band_old, band_new)
    assert (diag.diacritic_ink_original, diag.diacritic_ink_refined) == (marks_old, marks_new)
    assert diag.band_ink_retained_fraction == diag.diacritic_ink_retained_fraction == 1.0
    distances = [c['distance_to_box_center_px'] for c in diag.baseline_clusters]
    assert diag.selected_cluster_index == distances.index(min(distances))
    assert sum(c['selected'] for c in diag.baseline_clusters) == 1
    if path in REGRESSIONS:
        # Each supplied old/new pair remains evidence; v1 is never used as a page.
        companion = path.with_name(path.name.replace('_old.png', '_new.png'))
        assert companion.is_file()


def test_v2_selects_nearest_baseline_even_with_stronger_neighbour_and_keeps_stacked_marks():
    image = Image.new('L', (420, 160), 245)
    draw = ImageDraw.Draw(image)
    for x in range(35, 390, 35):
        draw.rectangle((x, 48, x+10, 67), fill=45)
        # Detached stacked marks, including above the nominal 1.9-height band.
        draw.rectangle((x+2, 38, x+5, 40), fill=20)
        draw.rectangle((x+2, 19, x+5, 21), fill=35)
    for x in range(10, 410, 18):
        draw.rectangle((x, 103, x+12, 122), fill=0)
    # Both tracks have body centres inside this tall layer box. Ink support
    # favours the neighbour, but its baseline is farther from the box centre.
    box = (0, 30, 420, 116)
    result = refine_line(image, box, pad=30)
    clusters = result.diagnostics.baseline_clusters
    assert len(clusters) == 2
    target = clusters[result.diagnostics.selected_cluster_index]
    other = next(c for c in clusters if not c['selected'])
    assert target['support_ink_pixels'] < other['support_ink_pixels']
    assert target['distance_to_box_center_px'] < other['distance_to_box_center_px']
    assert abs(result.curve.evaluate(200)-67) < 1
    assert result.dropped_components and all(c.box[1] >= 103 for c in result.dropped_components)
    marks = [c for c in ink_components(image) if c.box[1] in (19, 38)]
    assert len(marks) == 22
    assert all(c.id in {k.id for k in result.kept_components} for c in marks)
    for c in marks:
        x, y = int(c.center_x), int(c.center_y)
        assert result.image.getpixel((x-result.refined_box[0], y-round(result.curve.evaluate(x))+result.ascent)) == image.getpixel((x, y))
    # Copy paper and light antialias pixels, rather than recolouring them white.
    assert 245 in np.unique(np.asarray(result.image))


def test_v2_keeps_overlapping_neighbour_components_but_masks_only_outside_cluster():
    image = Image.new('L', (420, 170), 255)
    draw = ImageDraw.Draw(image)
    for x in range(25, 390, 30):
        draw.rectangle((x, 40, x+10, 59), fill=0)
        # Other body track is above the target. Its tall bodies overlap the band
        # even though their centres are assigned to that upper baseline.
        draw.rectangle((x, 12, x+10, 31), fill=20)
        draw.rectangle((x, 112, x+10, 131), fill=30)
    result = refine_line(image, (0, 35, 420, 80), pad=80)
    height = result.diagnostics.x_height_px
    kept = {c.id for c in result.kept_components}
    for c in ink_components(image):
        xs = range(c.box[0], c.box[2])
        overlaps = any(c.box[1] <= result.curve.evaluate(x)+.6*height and
                       c.box[3] > result.curve.evaluate(x)-1.9*height for x in xs)
        if overlaps:
            assert c.id in kept
    assert any(c.box[1] == 12 for c in result.kept_components)
    assert any(c.box[1] == 112 for c in result.dropped_components)


def test_tightened_cluster_tolerance_and_repeat_split_are_deterministic():
    assert BASELINE_CLUSTER_TOLERANCE < .55
    image = open_strip(ROWS[0])
    components = ink_components(image)
    first = split_multiline((0, 0, *image.size), components)
    assert len(first) == 2
    assert first == split_multiline((0, 0, *image.size), components)
    # With 0.55-height tolerance, an intermediate track absorbed these two
    # complete 20-pixel bodies. The stricter tolerance must distinguish them.
    close = Image.new('L', (420, 100), 255)
    draw = ImageDraw.Draw(close)
    for x in range(25, 390, 30):
        draw.rectangle((x, 30, x+10, 49), fill=0)
        draw.rectangle((x, 51, x+10, 70), fill=0)
    boxes = split_multiline((0, 0, *close.size), ink_components(close))
    assert len(boxes) == 2
    assert boxes[0][1:4:2] == (30, 50)
    assert boxes[1][1:4:2] == (51, 71)


def test_diacritic_assigned_to_another_cluster_is_kept_even_outside_the_band():
    image = Image.new('L', (420, 130), 255)
    draw = ImageDraw.Draw(image)
    for x in range(30, 380, 35):
        draw.rectangle((x, 40, x+10, 59), fill=45)
        draw.rectangle((x+17, 0, x+27, 19), fill=30)
        # This tiny mark is nearest the upper body cluster but horizontally
        # over the target body. Its entire bbox lies above the protected band.
        draw.rectangle((x+2, 9, x+5, 11), fill=20)
    result = refine_line(image, (0, 35, 420, 80), pad=40)
    assert len(result.diagnostics.baseline_clusters) == 2
    assert abs(result.curve.evaluate(200)-59) < 1
    marks = [c for c in result.kept_components if c.box[1] == 9]
    assert len(marks) == 10
    assert all(c.id in result.diagnostics.diacritic_component_ids for c in marks)
    assert all(c.box[3] < result.curve.evaluate(c.center_x)-1.9*result.diagnostics.x_height_px for c in marks)
    assert any(c.box[1] == 0 for c in result.dropped_components)


def test_available_terminal_sigma_extends_inboard_text_box():
    # Original page/box coordinates are absent. Deliberately clip the available ς
    # in line24 (γυρίζεις), while retaining the original strip as the page raster.
    image = open_strip(ROWS[23])
    result = refine_line(image, (0, 0, 1457, 50), pad=16)
    assert result.diagnostics.horizontal_extension_px[1] >= 6
    assert result.refined_box[2] >= 1463
    sigma = next(c for c in result.kept_components if c.box == (1451, 26, 1463, 47))
    assert sigma.area == 170
    mask = np.asarray(result.image) < 220
    assert mask[:, 1457:1463].sum() > 0
    # A padded search that cannot reach the full glyph exposes less ink.
    tight = refine_line(image, (0, 0, 1457, 50), pad=0)
    assert sum(c.area for c in tight.kept_components if c.box[0] >= 1450) < sigma.area
    assert 'right' in tight.diagnostics.search_boundary_ink


def test_pixels_missing_at_source_boundary_are_disclosed():
    image = open_strip(ROWS[6])  # Θεσσαλίας ends at the already-cut image boundary.
    result = refine_line(image, (0, 0, *image.size))
    assert 'right' in result.diagnostics.source_boundary_ink
    assert result.refined_box[2] <= image.width
    assert result.diagnostics.horizontal_extension_px[1] == 0


def test_visible_hyphen_missing_from_layer_is_flagged_without_repair():
    row = ROWS[1]  # Ink says πρόσω-; the label ends with U+0002, not a hyphen.
    image = open_strip(row)
    line = refine_line(image, (0, 0, image.width, 50))
    assert hyphen_at_line_end(line, row['layer'])
    assert hyphen_at_line_end(line.image, row['layer'])
    assert not hyphen_at_line_end(line, row['layer'].rstrip()+'-')
    result, = refine_page_lines(image, [TextLayerBox((0, 0, image.width, 50), row['layer'])])
    assert result.diagnostics.hyphen_missing_in_label is True
    assert result.text == result.source_text == row['layer']


def test_scan_gate_fixture_coverage_and_born_digital_rejection():
    scans, born = [], []
    for row in ROWS:
        image = open_strip(row)
        result = refine_line(image, (0, 0, *image.size))
        scans.append(scan_admission(result.diagnostics))
        born.append(scan_admission(replace(result.diagnostics,
                                          legacy=result.diagnostics.legacy | {'text': row['layer']}),
                                   profile='born_digital'))
    assert sum(a.admitted for a in scans) >= 36  # ceil(80% of 44).
    assert sum(a.admitted for a in born) == 0
    assert all(a.diagnostics['legacy']['unexplained_ink'] for a in scans)
    assert all(a.thresholds['curl_amplitude_px_max'] == SCAN_MAX_CURL_PX for a in scans)


@pytest.mark.parametrize('row', ROWS, ids=lambda r: r['file'])
def test_fixture_determinism_and_no_caller_rng_or_image_mutation(row):
    image = open_strip(row)
    pixels = image.tobytes()
    np.random.seed(2026)
    first = refine_line(image, (0, 0, *image.size))
    sample = np.random.random()
    np.random.seed(2026)
    assert sample == np.random.random()
    second = refine_line(image, (0, 0, *image.size))
    assert first.image.tobytes() == second.image.tobytes()
    assert first.receipt() == second.receipt()
    assert scan_admission(first.diagnostics).receipt() == scan_admission(second.diagnostics).receipt()
    assert image.tobytes() == pixels


def gate_input(**updates):
    return dict(n_baselines=1, curl_amplitude_px=10.0, ink_coverage=.15,
                blank_ink=False, unexplained_ink=True, missing_ink=True,
                ink_bbox_error=1.0) | updates


@pytest.mark.parametrize('updates,reason', [
    ({'n_baselines': 2}, 'multiline_ink'), ({'n_baselines': 0}, 'no_baseline'),
    ({'curl_amplitude_px': SCAN_MAX_CURL_PX+.01}, 'excessive_curl'),
    ({'curl_amplitude_px': float('nan')}, 'excessive_curl'),
    ({'curl_amplitude_px': float('inf')}, 'excessive_curl'),
    ({'curl_amplitude_px': -1}, 'excessive_curl'),
    ({'ink_coverage': SCAN_MIN_INK_COVERAGE-.001}, 'ink_coverage'),
    ({'ink_coverage': SCAN_MAX_INK_COVERAGE+.001}, 'ink_coverage'),
    ({'ink_coverage': float('nan')}, 'ink_coverage'),
    ({'blank_ink': True}, 'blank_ink'), ({'cross_column': True}, 'cross_column'),
])
def test_scan_gate_negative_conditions(updates, reason):
    admission = scan_admission(gate_input(**updates))
    assert not admission.admitted and reason in admission.reject_reasons


@pytest.mark.parametrize('coverage', [SCAN_MIN_INK_COVERAGE, SCAN_MAX_INK_COVERAGE])
def test_scan_gate_inclusive_boundaries_and_legacy_diagnostics(coverage):
    admission = scan_admission(gate_input(curl_amplitude_px=SCAN_MAX_CURL_PX, ink_coverage=coverage))
    assert admission.admitted and admission.diagnostics['unexplained_ink']
    assert admission.diagnostics['missing_ink'] and admission.diagnostics['ink_bbox_error'] == 1
    assert json.loads(json.dumps(admission.receipt()))['thresholds']['ink_coverage_min'] == SCAN_MIN_INK_COVERAGE


def test_born_digital_replays_other_vendor_rules_without_mutating_input():
    row = dict(text='ἀλήθεια λέξεις', bbox_pixel=[0, 0, 320, 48], ink_bbox_error=.25,
               unexplained_ink=False, missing_ink=False, cross_column=False)
    assert scan_admission(row, profile='born_digital').admitted
    assert 'text_raw' not in row
    row['unexplained_ink'] = True
    row['missing_ink'] = True
    row['ink_bbox_error'] = .251
    assert scan_admission(row, profile='born_digital').reject_reasons == (
        'unexplained_ink', 'missing_ink', 'ink_bbox_mismatch')
    row.update(text='α\x02', cross_column=True)
    decision = scan_admission(row, profile='born_digital')
    assert 'control' in decision.reject_reasons and 'cross_column' in decision.reject_reasons
    with pytest.raises(ValueError, match='profile'):
        scan_admission(gate_input(), profile='unsupported')
    with pytest.raises(ValueError, match='original text'):
        scan_admission(gate_input(), profile='born_digital')


def synthetic_line():
    image = Image.new('L', (440, 130), 255)
    draw = ImageDraw.Draw(image)
    for i, x in enumerate(range(25, 415, 30)):
        t = (x-220)/200
        bottom = round(47+12*t*t+11*t)
        if i in (3, 8):
            bottom += 12  # Two descender outliers must not bias the baseline.
        draw.rectangle((x-5, bottom-19, x+5, bottom), fill=0)
        draw.rectangle((x-4, 94, x+4, 112), fill=0)  # Independent lower baseline.
    return image


def test_known_quadratic_fit_rejects_descenders_and_neighbour():
    image = synthetic_line()
    result = refine_line(image, (10, 15, 430, 75), pad=48)
    for x in (55, 190, 370):
        t = (x-220)/200
        assert abs(result.curve.evaluate(x)-(47+12*t*t+11*t)) < 4
    assert all(c.center_y < 85 for c in result.kept_components)
    assert any(c.center_y >= 94 for c in result.dropped_components)
    assert result.diagnostics.n_baselines == 1
    assert result.diagnostics.retained_ink_fraction == 1


def test_blank_single_line_and_box_validation():
    blank = Image.new('L', (200, 80), 255)
    result = refine_line(blank, (0, 0, 200, 80))
    assert result.diagnostics.blank_ink and result.diagnostics.n_baselines == 0
    assert not scan_admission(result.diagnostics).admitted
    assert not hyphen_at_line_end(result, 'λέξη')
    assert split_multiline((0, 0, 200, 80), ()) == [(0, 0, 200, 80)]
    for box in ((0, 0, 0, 10), (0, 0, float('nan'), 10), (201, 0, 300, 20)):
        with pytest.raises(ValueError):
            refine_line(blank, box)
    for pad in (-1, True, 1.5):
        with pytest.raises(ValueError, match='pad'):
            refine_line(blank, (0, 0, 100, 50), pad=pad)
    assert refine_page_lines(blank, []) == []


def test_hyphen_negatives_for_punctuation_rule_and_existing_labels():
    image = Image.new('L', (200, 60), 255)
    draw = ImageDraw.Draw(image)
    for x in (20, 50, 80):
        draw.rectangle((x, 15, x+12, 40), fill=0)
    draw.rectangle((100, 33, 103, 37), fill=0)  # A terminal dot is not a hyphen.
    assert not hyphen_at_line_end(image, 'λέξεις')
    draw.rectangle((106, 25, 119, 28), fill=0)
    assert hyphen_at_line_end(image, 'λέξεις')
    for suffix in ('-', '\u00ad', '\u2010', '\u2011'):
        assert not hyphen_at_line_end(image, 'λέξεις'+suffix+' ')
    draw.rectangle((106, 25, 199, 28), fill=0)  # A long rule is not a hyphen.
    assert not hyphen_at_line_end(image, 'λέξεις')


def test_driver_pixel_mapping_and_cli_roundtrip(tmp_path, capsys):
    row = ROWS[1]
    source = FIXTURES/row['file']
    image = open_strip(row)
    entry = dict(bbox_pixel=[0, 0, image.width, 50], text=row['layer'])
    direct, = refine_page_lines(image, [entry])
    assert direct.text == row['layer'] and direct.diagnostics.hyphen_missing_in_label
    boxes = tmp_path/'boxes.json'
    boxes.write_text(json.dumps({'boxes': [entry]}))
    out = tmp_path/'refined'
    argv = ['geometry', 'refine', '--image', str(source), '--boxes', str(boxes), '--out', str(out)]
    assert main(argv) == 0
    printed = json.loads(capsys.readouterr().out)
    receipt = json.loads((out/'receipt.json').read_text())
    assert printed == receipt
    assert receipt['input_boxes'] == receipt['output_lines'] == receipt['admitted'] == 1
    assert receipt['image_sha256'] == hashlib.sha256(source.read_bytes()).hexdigest()
    raster = out/receipt['lines'][0]['crop_path']
    assert receipt['lines'][0]['crop_sha256'] == hashlib.sha256(raster.read_bytes()).hexdigest()
    assert receipt['lines'][0]['diagnostics']['hyphen_missing_in_label']
    with Image.open(raster) as saved:
        assert saved.tobytes() == direct.image.tobytes()
    # Re-running creates identical receipts/PNG bytes and refuses an occupied path.
    other = tmp_path/'repeat'
    assert main(argv[:-1]+[str(other)]) == 0
    assert json.loads(capsys.readouterr().out) == receipt
    assert (other/'line00000.png').read_bytes() == raster.read_bytes()
    assert main(argv) == 3
    assert 'File exists' in capsys.readouterr().err
    assert json.loads((out/'receipt.json').read_text()) == receipt
    invalid = tmp_path/'invalid'
    assert main(argv[:-1]+[str(invalid), '--pad', '-1']) == 3
    assert not invalid.exists()
    capsys.readouterr()
    born = tmp_path/'born'
    assert main(argv[:-1]+[str(born), '--profile', 'born_digital']) == 0
    assert json.loads(capsys.readouterr().out)['admitted'] == 0


def test_cli_keeps_blank_reject_and_split_provenance(tmp_path, capsys):
    source = tmp_path/'blank.png'
    Image.new('L', (200, 60), 255).save(source)
    boxes = tmp_path/'boxes.json'
    boxes.write_text(json.dumps([[0, 0, 200, 60]]))
    out = tmp_path/'blank-out'
    assert main(['geometry', 'refine', '--image', str(source), '--boxes', str(boxes),
                 '--out', str(out)]) == 0
    receipt = json.loads(capsys.readouterr().out)
    assert receipt['admitted'] == 0 and (out/'line00000.png').exists()
    assert 'blank_ink' in receipt['lines'][0]['admission']['reject_reasons']
    assert receipt['lines'][0]['text'] is None
