"""The owner's common decision/correction sheet contract (entirely offline)."""
import base64
import io
from importlib.resources import files

from bs4 import BeautifulSoup
from PIL import Image
import pytest

from greekocr.adjudicate.owner_sheet import render


def card(**fields):
    return dict(line_id='line<&', image=Image.new('RGB', (400, 80), 'white'),
                rows=[{'name': 'Google', 'text': 'printed <text>'}], **fields)


def soup(cards, **spec):
    return BeautifulSoup(render(cards, dict(title='Review', **spec)), 'html.parser')


def test_decision_card_versions_tool_overlay_and_prefix():
    svg = '<svg viewBox="0 0 400 80"><rect class="tbox" x="1" y="2" width="30" height="20"/></svg>'
    versions = [dict(name=name, verdict=verdict, text=reason) for name, verdict, reason in
                [('0.6', 'KEEP', 'old hidden reason'), ('0.7', 'DROP', 'too much padding'),
                 ('0.8', 'KEEP', 'length and padding match')]]
    s = soup([card(tool_verdict='KEEP', versions=versions, overlay_svg=svg)],
             variant='decision', sheet_prefix='segeval')
    c = s.select_one('.card')
    assert c['data-tool'] == 'KEEP'
    assert c.select_one('.toolpill').get_text() == 'tool: KEEP'
    assert c.select_one('.verdict').name == 'button'
    assert [r.th.get_text() for r in c.select('tr.version')] == ['0.7', '0.8 (latest)']
    assert 'old hidden reason' not in c.get_text()
    assert c.select_one('.ov svg')['viewbox'] == '0 0 400 80'
    assert c.select_one('.notes')['data-id'] == 'segeval:line<&'
    assert c.select_one('.notes')['data-line'] == 'line<&'
    assert c.select_one('.ov')['style'] == 'width:940px'
    assert 'KEEP = keep the line; DROP = drop the line.' in s.get_text()


def test_correction_card_changed_segments_and_printed():
    versions = [dict(name='Older', text='obsolete'), dict(name='Before', text='быть'),
                dict(name='After', verdict='CHANGED', segments=[dict(text='быт'), dict(text='ъ', kind='changed')])]
    s = soup([card(tool_verdict='CHANGED', versions=versions, printed='')], variant='correction', sheet_prefix='ru1')
    assert s.body['data-variant'] == 'correction'
    assert s.select_one('.card')['data-tool'] == 'CHANGED'
    assert [r.th.get_text() for r in s.select('tr.version')] == ['Before', 'After (latest)']
    assert s.select_one('tr.version mark').get_text() == 'ъ'
    assert s.select_one('.printed')['value'] == ''
    assert s.select_one('.notes')['data-id'] == 'ru1:line<&'
    assert 'KEEP = accept the proposed correction; DROP = reject it.' in s.get_text()


def test_legacy_identity_groups_sections_zooms_clean_lens_and_data():
    clean = Image.new('RGB', (400, 80), 'red')
    s = soup([card(group='g', slot=3, clean_image=clean, printed='truth',
                   zooms=[dict(image=clean, alt='detail')], data={'source': 'saved'})],
             groups=[dict(id='g', heading='Group', section='s', gap='2 cards')],
             sections=[dict(id='s', heading='Section', header='Context')])
    assert s.select_one('.notes')['data-id'] == 'line<&:s3'
    assert s.select_one('.notes')['data-slot'] == '3'
    assert s.select_one('.card')['data-source'] == 'saved'
    assert s.select_one('header h2').get_text() == 'Section'
    assert s.select_one('h3').get_text() == 'Group'
    assert s.select_one('.zoom')['alt'] == 'detail'
    assert 'background-image:url(data:image/png;base64,' in s.select_one('.lens')['style']
    assert s.select_one('.printed')['value'] == 'truth'
    legacy = soup([card()])
    assert legacy.select_one('.notes')['data-line'] == 'line<&'
    assert 'data-id' not in legacy.select_one('.notes').attrs
    assert not legacy.select('.toolpill,.printed')


def test_explicit_document_identity_and_unique_documents():
    c = card(doc_id='old:doc', note_data={'line': 'line<&', 'id': 'old:doc', 'kind': 'legacy'})
    assert soup([c], sheet_prefix='new').select_one('.notes')['data-id'] == 'old:doc'
    with pytest.raises(ValueError, match='duplicate note document'):
        render([c, c], {'title': 'x'})
    for data in [{'line': 'line<&', 'id': 'wrong'}, {'line': 'wrong', 'id': 'old:doc'}]:
        with pytest.raises(ValueError, match='identity disagree'):
            render([dict(c, note_data=data)], {'title': 'x'})


@pytest.mark.parametrize('verdict', ['CHANGED', 'UNCHANGED', 'UNCERTAIN'])
def test_correction_states_and_default_printed(verdict):
    s = soup([card(tool_verdict=verdict)], variant='correction')
    assert s.select_one('.card')['data-tool'] == verdict
    assert s.select_one('.toolpill').get_text() == f'tool: {verdict}'
    assert s.select_one('.printed')['value'] == ''


def test_legacy_tool_attribute_and_data_uri():
    first = soup([card()])
    c = card(data={'tool': 'DROP'})
    c['image'] = first.select_one('.ov img')['src']
    s = soup([c])
    assert s.select_one('.toolpill').get_text() == 'tool: DROP'
    assert s.select_one('.notes')['data-line'] == 'line<&'
    assert 'data-id' not in s.select_one('.notes').attrs
    assert s.select_one('.ov')['data-w'] == '400'


@pytest.mark.parametrize('size,display,expected', [((100, 40), {}, 300), ((2000, 100), {}, 940),
                                                ((100, 400), {}, 160), ((400, 80), {'scale': 1}, 400),
                                                ((400, 80), {'max_width': 600}, 600),
                                                ((400, 80), {'scale': 9, 'max_width': 2000}, 940)])
def test_display_caps(size, display, expected):
    c = card(display=display)
    c['image'] = Image.new('RGB', size)
    s = soup([c])
    assert s.select_one('.ov')['style'] == f'width:{expected}px'
    assert int(s.select_one('.ov')['data-w']) == size[0]
    assert ('tall' in s.select_one('.card')['class']) == (size[1] > size[0])  # vertical segments get the side-by-side layout
    img = Image.open(io.BytesIO(base64.b64decode(s.select_one('.ov img')['src'].split(',')[1])))
    assert img.size == size  # sizing changes display, never the native pixels


def test_frames_overlay_classes_and_dark_mode():
    css = files('greekocr.adjudicate').joinpath('owner_sheet.css').read_text()
    assert 'border:3px solid var(--line)' in css
    assert 'inset:6px;border:3px solid transparent' in css
    assert '.card.cur{outline:0;background:var(--selected)}' in css
    for verdict in ['KEEP', 'DROP', 'UNCERTAIN', 'CHANGED', 'UNCHANGED']:
        assert f'.card[data-tool="{verdict}"]::before' in css
    for cls in ['tbox', 'rframe', 'asc', 'base', 'mean', 'desc', 'nasc', 'nbase', 'wmain', 'wwhole',
                'wpart', 'wunres', 'cutspan', 'cutspan2', 'cross']:
        assert f'.ov .{cls}' in css
    assert 'prefers-color-scheme:dark' in css and ':root[data-theme="dark"]' in css


@pytest.mark.parametrize('filename,variant', [('decision_gate2.html', 'decision'), ('correction_ru1.html', 'correction')])
def test_demo_is_self_contained(filename, variant):
    from pathlib import Path
    s = BeautifulSoup((Path(__file__).resolve().parents[1] / 'docs/B_training_data/d_review/demo' / filename).read_text(), 'html.parser')
    assert s.body['data-variant'] == variant
    assert len(s.select('.card')) == 12
    assert len(s.select('.toolpill')) == 12
    assert len(s.select('tr.version')) == 24
    assert len({n['data-id'] for n in s.select('.notes')}) == 12
    assert not s.select('link,iframe,img[src^="http"],script[src]')
    assert len(s.select('.printed')) == (12 if variant == 'correction' else 0)


def test_javascript_no_write_on_load_guard_and_unified_document():
    js = files('greekocr.adjudicate').joinpath('owner_sheet.js').read_text()
    assert "el.querySelector('.note').value" in js
    assert "el.querySelector('.printed')?.value ?? null" in js
    assert 'last: initial.get(el), edited: false' in js
    assert 'if (!state.edited || !state.ready || !db) return;' in js
    assert 'if (snapshot === state.last) return;' in js
    assert 'if (state.edited) state.schedule();' in js
    assert js.count('.set(doc, {merge: true})') == 1
    assert 'doc.printed = printed.value' in js and "verdict: card.dataset.verdict || ''" in js
    assert "timeZone: 'Europe/Athens'" in js


def test_prior_mark_is_a_dashed_border_not_a_verdict():
    c = card(); c['prior'] = 'DROP'
    s = soup([c])
    assert 'pdrop' in s.select_one('.card')['class']
    assert 'data-verdict' not in s.select_one('.card').attrs  # the sheet still starts unmarked
    with pytest.raises(ValueError):
        soup([dict(card(), prior='MAYBE')])
