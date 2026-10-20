"""LQB3 source, sampling, coverage and rendered-report contracts."""
import importlib.util
import json
from pathlib import Path
from greekocr.ops.data_root import input_path as _data_input
from tests._paths import require_file
import pytest
from greekocr.labelfix import lqb

spec=importlib.util.spec_from_file_location('build_v2',lqb.ROOT/'scripts/lqb/build_v2.py')
v2=importlib.util.module_from_spec(spec);spec.loader.exec_module(v2)

FROZEN=lqb.DEFAULT/'validation/lqb3/frozen'

def read(name):
    path=FROZEN/name
    return json.loads((_data_input(path if path.exists() else lqb.DEFAULT/name)).read_text())


@pytest.mark.skip(reason="historical binding; green at opus/secondary-corrections@462bebaa1; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_v2_source_hashes_and_outputs():
    # Historical output custody survives later source-code revisions.
    r=read('LQB3_RECEIPT.json')
    superseded={'scripts/lqb/build_scoreboard.py','greekocr/labelfix/lqb.py','tests/test_lqb.py','tests/test_lqb3.py'}
    changes=[]
    for p,h in r['inputs'].items():
        if lqb.sha256(p)!=h:
            # The historical receipt names the producing secondary worktree.
            parts = Path(p).parts
            producer = next(i for i, part in enumerate(parts)
                            if part.startswith('greek-ocr-toolkit'))
            relative = str(Path(*parts[producer + 1:]))
            assert relative in superseded,p
            changes.append(relative)
    assert 'scripts/lqb/build_scoreboard.py' in changes
    for p,h in r['outputs'].items():assert lqb.sha256(FROZEN/p)==h,p
    assert r['network'] is False and r['git_writes'] is False and r['peer_writes'] is False


def test_frozen_truth_and_flags_unchanged():
    require_file('docs/records/labelfix/lqb/truth_v1.jsonl')
    r=read('LQB2_RECEIPT.json')
    assert lqb.sha256(lqb.DEFAULT/'truth_v1.jsonl')=='9f31e392e51b2c1b39e6d7ae5d23f949f4580f1b0bbefdd4d2d6e158013dfbe4'
    assert lqb.sha256(lqb.DEFAULT/'truth_v1_flags.jsonl')=='945cb12e114fce3200d401935d5300ff11b1e1329862a2ef1c5ae7b38b4a0f59'


@pytest.mark.parametrize('cls',['polytonic marks','capitals','numeric separators','punctuation and dashes','superscripts and rare glyphs','mixed-script lookalikes','Latin','modern monotonic Greek','Cyrillic'])
def test_every_class_has_baseline(cls):
    rs=[r for r in read('baseline_v2.json') if r['class_name']==cls]
    assert rs
    assert all(r['sample_type'] in ('uniform','locked_stratum') for r in rs)
    assert all(r['n'] or r['truth_needed'] for r in rs)


def test_head_directions_not_fabricated():
    rs=read('baseline_v2.json')[:12]
    assert len({r['metric'] for r in rs})==12
    assert all(r['status']=='not measured' and r['ci95'] is None for r in rs)


def test_all_c1_strata_and_verdicts_used():
    source=json.loads((_data_input(v2.COLLECT/'c1/c1_results.json')).read_text())
    rs=read('baseline_v2.json')
    for key,agg in source.items():
        scopes=[r for r in rs if r['source_set']=='C1/'+key]
        assert scopes,key
        for metric,field in [('letters / digits / words (strict card verdict)','letters'),('marks (any head; card verdict)','marks'),('crop (physical card verdict)','crop_ok')]:
            row=next(r for r in scopes if r['metric']==metric)
            assert row['sample_type']=='uniform' and row['tier']=='A'
            verdicts=[]
            for suffix in ['a','b']:verdicts+=list(lqb.rows(v2.COLLECT/f'c1/verdicts/{key}__{suffix}.jsonl'))
            known=[r[field] for r in verdicts if r[field] in ('y','n')]
            extra=len(row.get('raw_adjustments',[])) if field=='letters' else 0
            assert row['n']==len(known) and row['errors']==known.count('n')+extra


def test_wilson_and_no_pooled_rates():
    for r in read('baseline_v2.json'):
        if not r['n']:continue
        assert r['stratum'] and r['source_set']
        lo,hi=v2.wilson(r['errors'],r['n'])
        assert r['ci95']==[lo,hi] and lo<=r['rate']<=hi
        assert 'pooled' not in r['stratum']


def test_locked_selected_ia_not_population():
    r=next(r for r in read('baseline_v2.json') if r['source_set']=='R0_ia_letters')
    assert r['status']=='not measured'
    assert r['diagnostic']['headline']['errors_per_100'] is None
    assert r['diagnostic']['headline']['opportunities']>0


def test_sx1_released_only_and_google_binding():
    registry=read('versions.json');sf=registry['versions']['sf6_release']
    extract=list(lqb.rows(v2.SX/'sf6_release_extract_lqb.jsonl'))
    predictions=lqb.load_version('sf6_release',registry)
    assert len(predictions)==28
    for r in extract:
        if r['modes']['FULL']['status']=='HOLD':assert r['line_id'] not in predictions
        else:assert predictions[r['line_id']]==r['modes']['FULL']['label']
    google=lqb.load_version('google_raw',registry)
    assert all(google[r['line_id']]==r['google_text'] for r in extract)


def test_headline_out_of_sample_and_source_split():
    h=read('headline_v2.json');score=read('score_v2.json')
    assert 'audit100 (decision_audit)' in h['line']
    assert 'Cyrillic' not in h['line'] and 'RU1' not in h['line']
    v=h['by_source']['audit100/decision_audit']
    pair=score['paired']['google_raw→sf6_release']['marks|A+B']
    assert v['a_errors']==pair['a_errors'] and v['b_errors']==pair['b_errors']
    assert len(h['bottom_line'].split('. '))<=4


def test_n1_registered_unadopted_and_in_sample():
    require_file('artifacts/n1/owner_sheet/cards.json')
    reg=read('versions.json')['versions']['n1_proposal_v1']
    assert reg['adoption']=='UNADOPTED' and reg['parent']=='google_raw'
    cards=json.loads((_data_input(lqb.ROOT/'artifacts/n1/owner_sheet/cards.json')).read_text())
    proposals={r['line_id']:r['label'] for r in lqb.rows(lqb.DEFAULT/'n1_proposal_v1.jsonl')}
    assert len(proposals)==len(cards)==207
    for c in cards:assert proposals[c['line_id']]==next(r['text'] for r in c['rows'] if r['name']=='Ours')
    row=read('score_v2.json')['versions']['n1_proposal_v1']['n1_separator|A+B']
    assert row['in_sample']['items']==103 and row['headline']['items']==0


def test_baseline_first_and_page_budget():
    require_file('docs/records/labelfix/lqb/validation/lqb3/frozen/scoreboard.html')
    p=FROZEN/'scoreboard.html';s=_data_input(p).read_text()
    assert _data_input(p).stat().st_size<14_000_000
    assert s.index('id="baseline"')<s.index('id="headline"')<s.index('Version scores')
    assert 'UNADOPTED' in s and 'Bottom line' not in s
    assert s.index('Cyrillic')>s.index('modern monotonic Greek')
    assert 'sf6 release (accents): not scored yet;' not in s


def test_supplemental_google_hash_and_conflict_fail_closed(tmp_path):
    p=tmp_path/'base.jsonl';p.write_text('{"id":"x","text":"a"}\n')
    q=tmp_path/'other.jsonl';q.write_text('{"id":"x","text":"b"}\n')
    entry=dict(path=str(p),sha256=lqb.sha256(p),text_field='text',supplemental_sources=[dict(path=str(q),sha256=lqb.sha256(q),id_field='id',text_field='text')])
    with pytest.raises(ValueError,match='conflicting source'):lqb.load_version('v',{'versions':{'v':entry}})
    entry['supplemental_sources'][0]['sha256']='0'*64
    with pytest.raises(ValueError,match='supplemental sha256'):lqb.load_version('v',{'versions':{'v':entry}})


@pytest.mark.parametrize('name',['T6b/gazette_modern','T6b/kosmopolis','T6b/lekythos','T6b/gazette_probe_supplement','masked/caps1','masked/caps3','masked/kosmo2','masked/ruc1'])
def test_masked_sources_accounted_for(name):
    rs=[r for r in read('baseline_v2.json') if r['source_set']==name]
    assert rs
    assert all(r['sample_type']=='uniform' and r['stratum'] for r in rs)
    if name.startswith('masked/'):
        assert all(r['status']=='not measured' and r['truth_needed'] for r in rs)


def test_raw_google_duplicate_corrections_explicit():
    rs=read('baseline_v2.json')
    for source,error in [('C1/ia_poly1850__latin',11),('C1/serbia__cyrillic',4)]:
        r=next(r for r in rs if r['source_set']==source and r['metric'].startswith('letters'))
        assert r['errors']==error and len(r['raw_adjustments'])==1
