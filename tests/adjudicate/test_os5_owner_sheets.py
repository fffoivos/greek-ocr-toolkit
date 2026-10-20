"""OS5 verified tuples, exact OS4 prefix, words and native detection rasters."""
import copy
import hashlib
from pathlib import Path
from tests._paths import require_file

from PIL import Image, ImageChops, ImageDraw

from scripts.review.build_owner_sheets_v2 import (
    DEST, OUT, NAMES, OS5_GROUP, OS5_SELECTION, read, r2a_cards,
)
from scripts.review.retag_owner_sheets_os4 import apply


def test_os5_preserves_every_existing_card_and_group():
    before = [read(DEST/'inputs'/f'os3_{name}.json') for name in NAMES]
    expected = copy.deepcopy(before)
    apply(expected)
    actual = read(DEST/NAMES[0]/'spec.json')
    assert len(actual['lines']) == 185
    assert actual['lines'][:-5] == expected[0]['lines']
    assert actual['groups'][:-1] == expected[0]['groups']
    assert actual['sections'] == expected[0]['sections']
    assert actual['groups'][-1] == dict(id=OS5_GROUP, heading='What moved in R2a (not adopted)', shown_count=5)
    assert len({c['doc_id'] for c in actual['lines']}) == 185


def test_os5_source_replay_words_and_slot_identity(tmp_path, monkeypatch):
    from scripts.review import build_owner_sheets_v2 as builder
    monkeypatch.setattr(builder, 'OUT', tmp_path)
    actual = read(DEST/NAMES[0]/'spec.json')['lines'][-5:]
    expected = r2a_cards()  # Re-verifies source records and HEADS, offline.
    # The saved spec records the producing worktree; replay writes its raster
    # in this checkout. Compare the physical raster before rebinding that path.
    for saved, replayed in zip(actual, expected):
        assert Path(saved['image']).read_bytes() == Path(replayed['image']).read_bytes()
    assert [dict(card, image=replayed['image']) for card, replayed in zip(actual, expected)] == expected
    expected_words = [
        ('ἀμπλακίην', 'ἀμπλακίην', 'ἀμπλακίῃν'),
        ('ἦσαν', 'ἦσαν', 'ᾖσαν'),
        ('μαῦρα', 'μαῦρα', 'μαῧρα'),
        ('πῆς;', 'πῇς', 'πῆς'),
        ('καὶ', 'καὶ', 'καἲ'),
    ]
    import unicodedata
    nfc = lambda s: unicodedata.normalize('NFC', s)
    for card, selection, words in zip(actual, OS5_SELECTION, expected_words):
        seed, lid, slot, truth, after, change = selection
        assert card['doc_id'] == f'{lid}:s{slot}'
        assert [r['name'] for r in card['rows']] == ['Google', 'Before', f'After (R2a, seed {seed})']
        assert [r['text'] for r in card['rows']] == list(map(nfc, words))
        assert card['printed'] == nfc(words[1])
        tags = [t['text'] for t in card['tags']]
        assert tags == [f'seed {seed}', change] + (['owner witness'] if lid.startswith('602cc72e') else [])
        ev = card['evidence'][0]
        assert (ev['truth'], ev['before'], ev['after']) == (truth, truth, after)


def test_os5_full_native_crop_saved_detections_and_highlight():
    for card in read(DEST/NAMES[0]/'spec.json')['lines'][-5:]:
        ev = card['evidence'][0]
        assert hashlib.sha256(Path(ev['crop']).read_bytes()).hexdigest() == ev['crop_sha256']
        with Image.open(ev['crop']) as im:
            expected = im.convert('RGB')
        draw = ImageDraw.Draw(expected)
        for slot in ev['detections']:
            for key, color in [('above',(30,140,60)), ('apostrophes',(30,140,60)),
                               ('below',(40,80,200)), ('attached',(120,120,120))]:
                for mark in slot['evidence'].get(key, []):
                    draw.rectangle(mark['bbox'], outline=color, width=1)
        x0, _, x1, _ = ev['bbox']
        draw.rectangle([x0-2,0,x1+2,expected.height-1], outline=(200,40,40), width=2)
        with Image.open(card['image']) as actual:
            assert actual.size == expected.size == tuple(card['image_size'])
            assert ImageChops.difference(actual.convert('RGB'), expected).getbbox() is None
    manifest = (DEST/'v2_html_sha256.txt').read_text()
    for name in NAMES:
        path = OUT/f'{name}.html'
        assert f'{hashlib.sha256(require_file(path).read_bytes()).hexdigest()}  artifacts/owner_sheets/v2/{name}.html' in manifest
