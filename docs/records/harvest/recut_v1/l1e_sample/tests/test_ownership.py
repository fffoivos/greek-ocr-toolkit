import hashlib
from types import SimpleNamespace
import numpy as np
from PIL import Image
import pytest

from test_runner import runner
from greekocr.glyphs.foreign_ink import mask_foreign_ink, prepare_mask_page
from greekocr.glyphs.components import EIGHT
from scipy import ndimage as ndi


def digest(mask):
    return hashlib.sha256(mask.tobytes()).hexdigest()


def partition():
    labels = np.array([[0, 1, 2], [3, 4, 5]], dtype=np.uint8)
    ink = labels != 0
    proposed = labels >= 2
    abstained = labels == 5
    mask = (labels >= 2) & (labels <= 4)
    return labels, ink, proposed, abstained, mask


def test_all_classes_partition_the_applied_mask_and_abstentions():
    labels, ink, proposed, abstained, mask = partition()
    result = runner.check_ownership_map(labels, ink, proposed, abstained, mask, digest(mask))
    assert result['mask_union_sha256'] == digest(mask)
    assert result['abstained_sha256'] == digest(abstained)
    assert result['class_pixels'] == {str(i): 1 for i in range(6)}


@pytest.mark.parametrize('change', ['union', 'hash', 'abstention', 'background', 'keep', 'shape', 'dtype'])
def test_map_invariants_fail_loudly(change):
    labels, ink, proposed, abstained, mask = partition()
    sha = digest(mask)
    if change == 'union':
        labels[0, 2] = 1
    elif change == 'hash':
        sha = '0' * 64
    elif change == 'abstention':
        labels[1, 2] = 1
    elif change == 'background':
        labels[0, 0] = 1
    elif change == 'keep':
        labels[0, 1] = 0
    elif change == 'shape':
        labels = labels.T
    elif change == 'dtype':
        labels = labels.astype(np.int32)
    with pytest.raises(RuntimeError, match='ownership'):
        runner.check_ownership_map(labels, ink, proposed, abstained, mask, sha)


def test_png_alignment_nonzero_origin_asymmetric_corners_and_borders(tmp_path):
    box = [17, 29, 24, 33]
    labels = np.zeros((4, 7), dtype=np.uint8)
    labels[0] = 1
    labels[-1] = 2
    labels[1, 0] = 3
    labels[1, -1] = 4
    labels[2, -1] = 5
    destination = tmp_path / 'ownership/round1/doc/p000001-l0001.png'
    runner.save_ownership_map(destination, labels, box)
    with Image.open(destination) as opened:
        assert opened.mode == 'L' and opened.size == (7, 4)
        assert np.array_equal(np.asarray(opened), labels)
    header = destination.read_bytes()
    assert header[24] == 8 and header[25] == 0  # 8-bit greyscale IHDR, no palette/resampling.


def test_png_rejects_transposed_dimensions(tmp_path):
    with pytest.raises(RuntimeError, match='aligned'):
        runner.save_ownership_map(tmp_path / 'bad.png', np.zeros((7, 4), np.uint8), [17, 29, 24, 33])


def curve(centre, width=100):
    return dict(x0=0, x1=width, xheight=10., baseline=np.full(width, centre + 5.),
                meanline=np.full(width, centre - 5.))


def test_reconstructed_sets_match_frozen_mask_with_real_empty_ring():
    # A tiny corner component has only a one-pixel background gap; its outer
    # ring is entirely other ink. The lower foreign component has paper around it.
    pixels = np.full((160, 100), 240, np.uint8)
    pixels[:35] = 20
    pixels[75:85, 30:40] = 20
    pixels[115:125, 50:60] = 20
    prepared = prepare_mask_page(Image.fromarray(pixels))
    prepared.ink[:35] = True
    prepared.ink[:3, :3] = False
    prepared.ink[:2, :2] = True
    prepared.labels, _ = ndi.label(prepared.ink, structure=EIGHT)
    prepared.objects = ndi.find_objects(prepared.labels)
    own, upper, lower = curve(80), curve(40), curve(120)
    neighbours = [upper, own, lower]
    box = [0, 0, 90, 130]
    result = mask_foreign_ink(prepared, own, neighbours, box)
    ink, proposed, abstained = runner.ownership_sets(prepared, own, neighbours, box)
    assert result.mask.any() and abstained.any()
    assert np.array_equal(proposed & ~abstained, result.mask)
    labels = np.zeros(ink.shape, np.uint8)
    labels[ink & ~proposed] = 1
    labels[result.mask] = 4
    labels[abstained] = 5
    runner.check_ownership_map(labels, ink, proposed, abstained, result.mask, result.record['mask_sha256'])


def test_crop_comparison_rejects_byte_difference_even_with_identical_pixels(tmp_path):
    image = Image.fromarray(np.arange(200, dtype=np.uint8).reshape(10, 20))
    previous, current = tmp_path / 'old.png', tmp_path / 'new.png'
    image.save(previous, compress_level=3)
    image.save(current, compress_level=0)
    record = dict(id='line', mask_sha256='same-mask')
    reference = dict(path=str(previous), masked_sha256=runner.sha(previous), mask_sha256='same-mask')
    with pytest.raises(RuntimeError, match='comparison mismatch for line'):
        runner.compare_crop(current, record, reference)
    current.write_bytes(previous.read_bytes())
    assert runner.compare_crop(current, record, reference)['crops_identical']
    record['mask_sha256'] = 'different-mask'
    with pytest.raises(RuntimeError, match='comparison mismatch'):
        runner.compare_crop(current, record, reference)


def test_comparison_binding_rejects_missing_ids_and_reference_hash_changes(tmp_path, monkeypatch):
    import json
    monkeypatch.setattr(runner, 'OUTPUT', tmp_path / 'new')
    previous = tmp_path / 'previous'
    previous.mkdir()
    relative = 'crops/round1/doc/p000001-l0001.png'
    path = previous / relative
    path.parent.mkdir(parents=True)
    Image.new('L', (7, 4)).save(path)
    record = dict(id='line', masked_path=relative, old_box=[17, 29, 24, 33],
                  masked_sha256=runner.sha(path), mask_sha256='mask')
    pages = [dict(wave='round1', doc='doc', lines=[dict(id='line', crop=relative, crop_bbox=record['old_box'])])]
    metadata = previous / 'lines.jsonl'
    metadata.write_text(json.dumps(record) + '\n')
    assert runner.bind_comparison(previous, pages)['records']['line']['path'] == str(path)
    path.write_bytes(b'changed')
    with pytest.raises(ValueError, match='comparison crop hash mismatch'):
        runner.bind_comparison(previous, pages)
    metadata.write_text('')
    with pytest.raises(ValueError, match='missing comparison IDs'):
        runner.bind_comparison(previous, pages)


def classified_fixture():
    pixels = np.full((170, 100), 240, np.uint8)
    pixels[35:45, 10:20] = 20
    pixels[75:85, 30:40] = 20
    pixels[115:125, 50:60] = 20
    prepared = prepare_mask_page(Image.fromarray(pixels))
    lines = [curve(y) for y in (40, 80, 120, 160)]
    result = mask_foreign_ink(prepared, lines[1], lines, [7, 35, 91, 125])
    detector = prepared.labels * 10 + (prepared.labels > 0) * 60
    detector[35:45, 15:20] = 0  # part of a masking CC has no detector observation
    owned = {i: dict(component_ids=ids) for i, ids in enumerate(([70], [80], [], [90]))}
    return prepared, detector, owned, lines, result


def test_native_crosswalk_keeps_unassigned_pixels_and_nonadjacent_owner_ids():
    prepared, detector, owned, lines, result = classified_fixture()
    labels, components, checks = runner.build_ownership_map(
        prepared, detector, owned, lines, 1, [7, 35, 91, 125], result)
    assert np.all(labels[:10, 3:8] == 2)
    assert np.all(labels[:10, 8:13] == 4)
    assert np.all(labels[40:50, 23:33] == 1)
    assert np.all(labels[80:90, 43:53] == 3)
    assert checks['mask_union_sha256'] == result.record['mask_sha256']
    assert {(r['class_value'], r['owner_row_id'], r['side'], r['pixel_count']) for r in components} == {
        (2, 0, 'above', 50), (4, None, 'unassigned', 50), (1, 1, 'own', 100), (3, 3, 'below', 100)}
    assert sum(r['pixel_count'] for r in components) == 300
    assert {r['component_id'] for r in components} == {1, 2, 3}
    assert {r['detector_component_id'] for r in components} == {None, 70, 80, 90}


def test_duplicate_detector_owner_is_rejected():
    prepared, detector, owned, lines, result = classified_fixture()
    owned[2]['component_ids'] = [70]
    with pytest.raises(RuntimeError, match='multiple owner rows'):
        runner.build_ownership_map(prepared, detector, owned, lines, 1, [7, 35, 91, 125], result)


def test_invalid_ribbon_retains_explicit_component_owner_without_fabricating_unassigned():
    prepared, detector, owned, lines, result = classified_fixture()
    lines = [SimpleNamespace(**line, component_ids=owned[i]['component_ids']) for i, line in enumerate(lines)]
    owned.pop(3)
    labels, components, _ = runner.build_ownership_map(
        prepared, detector, owned, lines, 1, [7, 35, 91, 125], result)
    assert np.all(labels[80:90, 43:53] == 3)
    lower = [r for r in components if r['owner_row_id'] == 3]
    assert len(lower) == 1 and lower[0]['owner_geometry_valid'] is False


def test_masked_detector_own_pixels_retain_owner_and_flag_pixel_side_exception():
    prepared, detector, owned, lines, result = classified_fixture()
    owned[0]['component_ids'] = []
    owned[3]['component_ids'] = []
    owned[1]['component_ids'].extend([70, 90])
    labels, components, checks = runner.build_ownership_map(
        prepared, detector, owned, lines, 1, [7, 35, 91, 125], result)
    assert checks['mask_union_sha256'] == result.record['mask_sha256']
    assert checks['detector_own_masked_pixels'] == 150
    conflicts = [r for r in components if r['ownership_conflict']]
    assert {(r['class_value'], r['owner_row_id'], r['side'], r['pixel_count']) for r in conflicts} == {
        (2, 1, 'above', 50), (3, 1, 'below', 100)}
    assert all(r['side_basis'] == 'pixel_position' for r in conflicts)
    assert np.all(labels[:10, 8:13] == 4)  # truly unassigned pixels stay distinct


@pytest.mark.parametrize('index,reason', [(None, 'unmatched'), (1, 'ambiguous')])
def test_identity_maps_keep_all_ink_with_explicit_non_voronoi_basis(index, reason):
    prepared, detector, owned, lines, _ = classified_fixture()
    box = [7, 35, 91, 125]
    original, record = runner.identity(prepared.image.crop(box), box)
    result = SimpleNamespace(image=original, record=record, mask=np.zeros((90, 84), bool))
    labels, components, checks = runner.build_ownership_map(
        prepared, detector, owned, lines, index, box, result, reason)
    assert set(np.unique(labels)) == {0, 1}
    assert np.array_equal(labels == 1, prepared.ink[35:125, 7:91])
    assert all(r['class_value'] == 1 for r in components)
    assert checks['keep_basis'] == 'identity_unmasked'
    assert checks['mask_union_sha256'] == record['mask_sha256']
    assert {r['side'] for r in components} == {'unresolved', 'unassigned'}
