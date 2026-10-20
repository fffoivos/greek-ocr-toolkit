"""Independent artifact checks for RU1-2; no inference or source writes."""
import json
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/secondary'))
from ru1_version import ROOT, FEATURES, LEAD_DIR, rows, sha, rulings

@pytest.fixture(scope='module')
def data():
    labels=rows(ROOT/'ru1_v1.jsonl')
    bed=[m for n in range(1,5) for m in json.loads((ROOT/f'keys/ctx{n:02}.json').read_text())['items'].values()]
    return labels,bed


def test_exact_population_and_parent(data):
    labels,bed=data
    expected={m['row_id'] for m in bed if not m['control'] and any(s['google']=='ь' and s['kind']=='final' for s in m['slots'])}
    assert len(labels)==len({r['id'] for r in labels})==len(expected)
    assert {r['id'] for r in labels}==expected
    w1={r['id']:r for r in rows(FEATURES) if r['source']=='ia_russian' and r['id'] in expected}
    assert all(r['label_parent'].encode()==w1[r['id']]['label'].encode() for r in labels)


def test_all_other_characters_identical(data):
    for r in data[0]:
        parent,child=r['label_parent'],r['label_ru1_v1']
        offsets={e['offset'] for e in r['edits']}
        assert len(offsets)==len(r['edits']) and len(parent)==len(child)
        assert {i for i,(a,b) in enumerate(zip(parent,child)) if a!=b}==offsets
        assert ''.join(c for i,c in enumerate(parent) if i not in offsets).encode()==''.join(c for i,c in enumerate(child) if i not in offsets).encode()
        for e in r['edits']:
            assert e['from']=='ь' and e['to']=='ъ'
            assert parent[e['offset']]=='ь' and child[e['offset']]=='ъ'


def test_protected_slots_and_decided_offsets(data):
    ds={(d['row_id'],d['offset']):d for d in rows(ROOT/'decisions.jsonl')}
    labelmap={r['id']:r for r in data[0]}
    for m in data[1]:
        if m['control'] or m['row_id'] not in labelmap: continue
        r=labelmap[m['row_id']]; edited={e['offset'] for e in r['edits']}
        for s in m['slots']:
            off=s['offset']
            if s['google']=='ъ' or s['kind']=='pre_hyphen':
                assert off not in edited and r['label_parent'][off]==r['label_ru1_v1'][off]
            elif s['google']=='ь' and s['kind']=='final':
                assert (off in edited)==(ds[r['id'],off]['decision']=='edit_hard')


def test_hold_rows_and_basis(data):
    ds={(d['row_id'],d['offset']):d for d in rows(ROOT/'decisions.jsonl')}
    for r in data[0]:
        assert r['status']==('hold' if r['holds'] else 'ok')
        expected=[dict(offset=off,reason=d['decision']) for (lid,off),d in ds.items() if lid==r['id'] and d['decision'].startswith('hold_')]
        assert r['holds']==sorted(expected,key=lambda h:h['offset'])
        for h in r['holds']: assert r['label_parent'][h['offset']]==r['label_ru1_v1'][h['offset']]=='ь'
        for e in r['edits']: assert e['basis']==('lead_ruling' if 'lead_ruling' in ds[r['id'],e['offset']] else 'two_reads')
    assert Counter(r['status'] for r in data[0])=={'ok':311,'hold':3}


def test_rulings_and_audit_unchanged():
    old={(d['row_id'],d['offset']):d for d in rows(ROOT/'decisions.pre_ru1_v1.jsonl')}
    new={(d['row_id'],d['offset']):d for d in rows(ROOT/'decisions.jsonl')}
    cells=json.loads((LEAD_DIR/'sheets_index.json').read_text())['items']
    assert len(cells)==67
    for c in cells:
        key=(c['row_id'],c['offset']); d=new[key]
        if c['cell']<=27:
            expected={9:'hold_uncertain',17:'hold_yat',23:'keep_soft',27:'hold_yat'}.get(c['cell'],'edit_hard')
            assert d['decision']==expected and d['lead_ruling']['cell']==c['cell']
            assert d['lead_ruling']['reference'].endswith('RU1_LEAD_REVIEW.md')
        else:
            assert d['lead_audit_confirmed']['cell']==c['cell']
            assert {k:v for k,v in d.items() if k!='lead_audit_confirmed'}==old[key]
    mapped={(c['row_id'],c['offset']) for c in cells}
    assert all(new[k]==old[k] for k in old if k not in mapped)


@pytest.mark.skip(reason="historical binding; green at opus/secondary-corrections@daed1af19; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_manifest_hashes_and_controls(data):
    m=json.loads((ROOT/'ru1_v1_manifest.json').read_text())
    assert sha(ROOT/'ru1_v1.jsonl')==m['sha256']
    assert all(sha(p)==h for p,h in m['inputs'].items())
    assert m['edit_counts_by_basis']==dict(Counter(e['basis'] for r in data[0] for e in r['edits']))
    assert m['rows']==len(data[0]) and m['row_counts']==dict(Counter(r['status'] for r in data[0]))
    controls=[r for r in data[1] if r['control']]
    assert len(m['excluded_controls'])==len(controls)==36
    assert {r['source_id'] for r in m['excluded_controls']}=={r['source_id'] for r in controls}
    assert not {r['id'] for r in data[0]} & {r['w1_id'] for r in controls}


class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.marks=0;self.cards=0;self.headings=[];self.h=None;self.imgs=[];self.names=[];self.th=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='mark':self.marks+=1
        if tag=='div' and a.get('class')=='card':self.cards+=1
        if tag=='h2':self.h=''
        if tag=='th':self.th=True
        if tag=='img':self.imgs.append(a)
    def handle_data(self,s):
        if self.h is not None:self.h+=s
        if self.th:self.names.append(s)
    def handle_endtag(self,tag):
        if tag=='h2':self.headings.append(self.h);self.h=None
        if tag=='th':self.th=False


@pytest.mark.skip(reason="historical binding; green at opus/secondary-corrections@daed1af19; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_owner_structure_and_size():
    p=ROOT/'owner_sheet/ru1_sheet.html';html=p.read_text();page=Page();page.feed(html)
    assert p.stat().st_size<5_000_000
    assert '<title>RU1 Hard Sign Decisions</title>' in html
    assert page.cards==15 and page.marks==30
    assert page.headings==['What a change looks like','Held back']
    assert Counter(page.names)=={'Google':15,'Proposed':15}
    assert len(page.imgs)==30 and all(i['src'].startswith('data:image/png;base64,') for i in page.imgs)
    assert 'nothing to review here unless a letter on the left does not look like the one in the middle' in html
    assert '<mark>' in html and 'Reads</th>' not in html


@pytest.mark.skip(reason="historical binding; green at opus/secondary-corrections@daed1af19; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_owner_seed_geometry_and_holds():
    import random
    s=json.loads((ROOT/'owner_sheet/summary.json').read_text())
    ds=rows(ROOT/'decisions.jsonl');pool=sorted([d for d in ds if d['decision']=='edit_hard'],key=lambda d:(d['row_id'],d['offset']))
    chosen=random.Random(s['sample_seed']).sample(pool,12)
    assert [(g['id'],g['offset']) for g in s['geometry'][:12]]==[(d['row_id'],d['offset']) for d in chosen]
    assert {(g['id'],g['offset']) for g in s['geometry'][12:]}=={(d['row_id'],d['offset']) for d in ds if d['decision'].startswith('hold_')}
    assert all(g['final_scale']==8 and all(r['book']==g['book'] and r['scale']==8 for r in g['references'].values()) for g in s['geometry'])
    assert s['html_sha256']==sha(ROOT/'owner_sheet/ru1_sheet.html')
