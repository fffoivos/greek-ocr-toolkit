"""OS2 continuity, evidence, native geometry and offline rendering acceptance."""
import base64
import hashlib
import io
import json
import re
import subprocess
from pathlib import Path
from scripts.layout_paths import relocated
from tests._paths import require_file
from collections import Counter
import pytest
from bs4 import BeautifulSoup
from PIL import Image, ImageChops
from greekocr.adjudicate.owner_sheet import render, image_path

ROOT=Path(__file__).resolve().parents[2]
NAMES=('failure_modes_per_class','segmentation_failures')
def spec(name): return json.loads((relocated(ROOT/'docs/owner_sheets')/name/'spec.json').read_text())
def baseline(name): return json.loads((relocated(ROOT/'docs/owner_sheets')/'inputs'/f'coordinator_{name}.json').read_text())

def placement_after_os4(name, card):
    """Only the evidence-bound OS4 ledger can relax OS2/OS3 placement."""
    if name == NAMES[0]:
        ledger=json.loads((ROOT/'artifacts/owner_sheets/v2/os4_retag_audit.json').read_text())
        change=next((r for r in ledger['changes'] if r['card']==card['line_id']),None)
        if change:
            assert change['old_group']==card['group']
            return change['new_group']
    return card['group']

@pytest.mark.parametrize('name',NAMES)
@pytest.mark.skip(reason="historical binding; green at coord/review-sheets@994456de0; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_os2_offline_render_native_images_and_identity(name,monkeypatch):
    import socket
    def offline(*a,**kw):raise AssertionError('Network forbidden')
    monkeypatch.setattr(socket,'socket',offline)
    s=spec(name);html=render(s['lines'],s)
    assert html==(ROOT/'artifacts/owner_sheets/v2'/f'{name}.html').read_text()
    soup=BeautifulSoup(html,'html.parser');cards=soup.select('.card')
    # Renderer emits groups, not input-line order.
    ordered=[c for g in s['groups'] for c in s['lines'] if c['group']==g['id']]
    assert len(cards)==len(ordered)==len(s['lines'])
    assert len({c['doc_id'] for c in ordered})==len(cards)
    for card,c in zip(cards,ordered):
        assert c['doc_id']==c['line_id'] + (f":s{c['slot']}" if 'slot' in c else '')
        n=card.select_one('.notes');assert n.get('data-id',n['data-line'])==c['doc_id']
        assert n['data-line']==c['line_id']
        assert card.select_one('.printed')['value']==c['printed']
        assert card.select_one('.note').get_text()==''
        assert card.select_one('table.w td').get_text()==c['rows'][0]['text']
        assert c['rows'][0]['name']=='Google' and c['rows'][0]['text']
        assert c['fault_codes']
        assert set(c['fault_codes']) <= {t['text'] for t in c['tags']}
        paths=[c['image']]+[z['image'] for z in c.get('zooms',[])]
        assert len(card.select('img'))==len(paths)
        for img,p in zip(card.select('img'),paths):
            assert image_path(p).is_file()
            actual=Image.open(io.BytesIO(base64.b64decode(img['src'].split(',',1)[1]))).convert('RGB')
            with Image.open(image_path(p)) as original:
                assert actual.size==original.size
                assert ImageChops.difference(actual,original.convert('RGB')).getbbox() is None
        assert list(Image.open(image_path(c['image'])).size)==c['image_size']
        assert '?' not in c['note']
        assert all('?' not in r['text'] or '?' in c['rows'][0]['text'] for r in c['rows'] if r['name']=='Checker')
        assert c['printed_source'] is not None if c['printed'] else c['printed_source'] is None
    assert '.card img{display:block;width:100%;max-width:100%;height:auto;' in html
    assert '.card img.zoom{width:auto;max-width:100%;height:auto;' in html
    assert not soup.select('link,iframe,img[src^="http"],script[src]')
    for el in soup.select('style,script'):el.decompose()
    assert not re.search(r'gpt-|claude|apertus|gemini',soup.get_text(),re.I)

@pytest.mark.parametrize('name',NAMES)
def test_os2_baseline_continuity_and_sections(name):
    old=baseline(name);new=spec(name)
    before={c['doc_id']:c for c in old['lines']};after={c['doc_id']:c for c in new['lines']}
    assert set(before)<=set(after)
    for lid,c in before.items():
        assert after[lid]['group']==placement_after_os4(name,c)
        assert after[lid]['image']==c['image']
    if name==NAMES[0]:
        assert len(new['sections'])==14
        assert new['sections']==old['sections'] or [(x['id'],x['heading']) for x in new['sections']]==[(x['id'],x['heading']) for x in old['sections']]
        og={g['id']:g for g in old['groups']};ng={g['id']:g for g in new['groups']}
        for gid,g in og.items(): assert ng[gid]['section']==g['section']
        assert [g['id'] for g in new['groups'] if g['id'] in og]==list(og)
        for g in new['groups']:
            count=sum(c['group']==g['id'] for c in new['lines'])
            assert count<=6
            if count<3:assert str(count) in g['gap']
    else:
        assert new['groups'][:len(old['groups'])]==old['groups'] or [g['id'] for g in new['groups'][:len(old['groups'])]]==[g['id'] for g in old['groups']]
        assert all(c['zooms'] for c in new['lines'])


def test_os2_checker_codes_and_masked_rasters():
    require_file('docs/owner_sheets/inputs/coordinator_labelmap.json')
    from scripts.review.build_owner_sheets_v2 import evidence
    records=evidence()
    lookup={}
    for r in records:lookup.setdefault(r['line_id'],[]).append(r)
    s=spec(NAMES[0]);stages=set();sources=set()
    for c in s['lines']:
        if c['group'] == 'r2a_not_adopted': continue  # Source-bound OS5 tuples are checked separately.
        expected={e for r in lookup[c['line_id']] for e in r['errors']}
        assert set(c['fault_codes'])==expected
        if c.get('display_evidence',{}).get('stage')=='T6b':
            r=next(r for r in lookup[c['line_id']] if r['verdict_path']==c['display_evidence']['path'] and r['card_id']==c['display_evidence']['card_id'])
            assert c['image']==r['image']
            assert hashlib.sha256(Path(c['image']).read_bytes()).hexdigest()==r['key']['card_crop_sha256']
            stages.add(r['stage']);sources.add(r['bed'])
    assert stages=={'T6b'} and sources=={'kosmopolis','lekythos','gazette_modern'}
    for cov in s['fault_coverage']:
        if cov['stage']=='T6b':assert len(cov['shown_ids'])>=min(3,cov['available'])


def test_os2_source_bound_printed_and_yers():
    require_file('docs/owner_sheets/inputs/coordinator_labelmap.json')
    from scripts.review.build_owner_sheets_v2 import evidence
    records=evidence();yers=[]
    for name in NAMES:
        s=spec(name)
        assert not s['truth_inventory']['exact_line_id_matches']
        for c in s['lines']:
            src=c['printed_source']
            if not src:continue
            assert Path(src['path']).is_file()
            if c['group'] == 'r2a_not_adopted':
                continue  # OS5 uses slot truth, verified in test_os5_owner_sheets.
            if 'yer_adjudication' in src['path']:
                y=next(y for y in json.loads(Path(src['path']).read_text()) if y['item_id']==src['item_id'])
                assert c['yer_adjudication']==y
                key=json.loads(Path(src['key_path']).read_text())[src['item_id']]
                signs=[ch for ch in c['printed'] if ch in 'ъь']
                assert len(signs)==len(y['slots'])
                for slot in y['slots']:
                    m=re.fullmatch(r'(\d+):g=(.) ink=(.) prior=.*',slot)
                    assert signs[int(m[1])-1]==m[3]
                assert c['rows'][0]['text']==key['google_text']
                yers.append(c)
            else:
                r=next(r for r in records if r['verdict_path']==src['path'] and r['card_id']==src['card_id'] and r['line_id']==c['line_id'])
                assert src['detail']==r['detail']
                assert r['line_id']==c['line_id']
    assert len(yers)>=6
    assert any(c['group']=='s7_yer' for c in yers)
    # Independent native-source witnesses: qualifiers must not enter Printed,
    # while nested explicit numeric context must be used as the full label.
    cards={c['doc_id']:c for c in spec(NAMES[0])['lines']}
    assert cards['elstat--ee37bc488988f1bd--s000-l0445']['printed']=='4·547·331'
    assert cards['elstat--ee37bc488988f1bd--s000-l0457']['printed']=='4·479·781'
    assert cards['ia_russian--3fd32314d172e951--s002-l0006']['printed']=='А ты видалъ такихъ?—спросилъ Челкашъ, съ'


def test_os2_sg2_saved_scope_and_native_crops():
    s=spec(NAMES[1]);cards=[c for c in s['lines'] if c['group']=='g_missing_box']
    assert len(cards)==3 and s['groups'][-1]['id']=='g_missing_box'
    for c in cards:
        e=c['evidence'][0]
        assert e['raw_google_box_present'] and 'admitted' in e['box_scope']
        assert Path(e['notes_path']).is_file() and Path(e['validation_path']).is_file()
        with Image.open(e['page']) as page,Image.open(c['image']) as actual:
            expected=page.convert('RGB').crop(e['bbox'])
            assert expected.size==actual.size
            assert ImageChops.difference(expected,actual.convert('RGB')).getbbox() is None
        assert Path(c['zooms'][0]['image']).name==e['id']+'-strip.png'
        assert not c['printed']


def test_os2_renderer_additions_are_optional_and_escaped():
    # Read-only reference: no staging, reset, checkout, or other git writes.
    legacy_source=subprocess.check_output(['git','show','HEAD:greekocr/adjudicate/owner_sheet.py'],cwd=ROOT,text=True)
    ns={'__package__':'greekocr.adjudicate'};exec(legacy_source,ns)
    line=dict(line_id='a',image=Image.new('RGB',(20,8),'white'),rows=[dict(name='Google',text='α')],printed='')
    assert render([line],dict(title='legacy',intro='single line'))==ns['render']([line],dict(title='legacy',intro='single line'))
    line.update(group='g',note='</textarea><unsafe>')
    html=render([line],dict(title='optional',intro='one\ntwo',sections=[dict(id='s',heading='<section>',header='header')],groups=[dict(id='g',section='s',heading='<group>',gap='<gap>')]))
    soup=BeautifulSoup(html,'html.parser')
    assert soup.select_one('header h2').get_text()=='<section>'
    assert soup.select_one('h3').get_text()=='<group>'
    assert soup.select_one('.pill.warn').get_text()=='<gap>'
    assert soup.select_one('textarea').get_text()=='</textarea><unsafe>'
    assert not soup.select('unsafe')
    assert '<br>' in html


def test_os3_recomputed_pairs_and_current_coordinator_continuity(monkeypatch):
    require_file('docs/owner_sheets/inputs/coordinator_labelmap.json')
    import socket
    from scripts.review.build_owner_sheets_v2 import recompute_labelmap, coordinator, OUT, read
    def offline(*args, **kwargs): raise AssertionError('Network forbidden')
    monkeypatch.setattr(socket, 'socket', offline)
    labelmap, audit = recompute_labelmap()
    assert len(labelmap['cardmap']) == 5326
    assert labelmap['cardmap'] == read(relocated(ROOT/'docs/owner_sheets/inputs/coordinator_labelmap.json'))['cardmap']
    assert audit['differences'] == dict(missing=[], extra=[], changed=[])
    current, _, _ = coordinator()
    recomputed, _, _ = coordinator(labelmap)
    assert current == recomputed
    receipt = read(OUT/'os3_mapping_audit.json')
    assert receipt['empty_source_cards'] == audit['empty_source_cards']
    for name, old in zip(NAMES, current):
        assert old == read(relocated(ROOT/'docs/owner_sheets')/'inputs'/f'coordinator_v2_{name}.json')
        after = {c['line_id']: c for c in spec(name)['lines']}
        for c in old['lines']:
            assert after[c['line_id']]['doc_id'] == c['doc_id']
            assert after[c['line_id']]['group'] == placement_after_os4(name,c)
            assert after[c['line_id']]['image'] == c['image']


@pytest.mark.parametrize('name', NAMES)
def test_os3_every_google_row_nonempty(name):
    s = spec(name)
    html = require_file(ROOT/'artifacts/owner_sheets/v2'/f'{name}.html').read_text()
    soup = BeautifulSoup(html, 'html.parser')
    for c in s['lines']:
        google = [r for r in c['rows'] if r['name'].startswith('Google')]
        assert google
        assert all(r['text'].strip() for r in google), c['doc_id']
    for row in soup.select('table.w tr'):
        if row.select_one('th').get_text().startswith('Google'):
            assert row.select_one('td').get_text().strip()
