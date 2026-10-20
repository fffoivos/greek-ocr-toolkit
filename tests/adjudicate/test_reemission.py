import json
from pathlib import Path
import numpy as np
from PIL import Image
import pytest
from greekocr.adjudicate.owner_sheet import render, detection_image
from greekocr.adjudicate.deck import build_deck
from scripts.review.cu4_reemit import compare_owner
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/cleanup_step4'


@pytest.mark.parametrize('name,count',[('reader_errors_heldout',39),('accent_corrections_checked',100)])
@pytest.mark.skip(reason="historical binding; green at coord/review-sheets@888c0d512; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_owner_content_and_pixels(name,count):
    spec=json.loads((OUT/'specs'/f'{name}.json').read_text())
    diff=compare_owner((OUT/'reference'/f'{name}.html').read_text(),render(spec['lines'],spec))
    assert diff['cards']==count
    assert diff['diffs']==[]


def test_owner_escape_groups_identity_and_detection_pixels():
    image=Image.new('RGB',(100,40),'white')
    slots=[dict(locator_span=[10,20],evidence=dict(above=[dict(bbox=[10,2,14,6])],below=[dict(bbox=[15,25,19,29])],attached=[dict(bbox=[30,10,34,14])]))]
    output=detection_image(image,slots)
    assert output.getpixel((20,4))==(30,140,60)
    assert output.getpixel((30,50))==(40,80,200)
    assert output.getpixel((60,20))==(120,120,120)
    card=dict(line_id='x<y',image=image,slots=slots,rows=[dict(name='Ours',text='<script>')],printed='"<',slot=3)
    html=render([card],dict(title='<title>'))
    assert '&lt;script&gt;' in html and 'data-id="x&lt;y:s3"' in html
    with pytest.raises(ValueError,match='duplicate'):render([card,card],dict(title='x'))
    with pytest.raises(ValueError,match='group'):render([card],dict(title='x',groups=[]))


def test_r0_ib_native_crop_reemission(tmp_path):
    spec=json.loads((OUT/'specs/R0_cards_ib.json').read_text())
    spec['blind_dir']=str(tmp_path/'blind')
    receipt=build_deck(spec)
    expected=sorted(spec['items']+spec['controls'],key=lambda r:r['position'])
    cards=json.loads((tmp_path/'blind/items_blind.json').read_text())
    assert len(cards)==336
    keys=json.loads(Path(receipt['private_key']).read_text())
    for old,new,key in zip(expected,cards,keys):
        assert new['id']==old['id']
        assert {k:new[k] for k in ('A','B','C') if k in new}==old['options']
        assert key['control']==old['control'] and key['geometry']['zoom_scale']==old['zoom_scale']
        for field,source in [('img',old['old_img']),('line_img',old['old_line_img'])]:
            root=Path(old['line_image']).parents[1]
            with Image.open(root/source) as a,Image.open(tmp_path/'blind'/new[field]) as b:
                assert np.array_equal(np.array(a),np.array(b))
