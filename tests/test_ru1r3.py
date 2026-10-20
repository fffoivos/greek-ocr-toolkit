"""Offline r3 routing, closure and finalisation fixtures; never invoke a reader."""
import json
import os
import subprocess
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts/secondary'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts/secondary/reading'))
from common import dump, jsonl, rows
from ru1_decide import accepted_contexts, combine, decide
from ru1_finalize_r3 import finalize
from ru1_map_answers import map_records

WORK = Path(__file__).resolve().parents[1]


@pytest.fixture
def prepared(tmp_path):
    art=tmp_path/'art'; packs=tmp_path/'packs'
    for ctx, reader, stem in accepted_contexts():
        iid='k0000000001'; row='row-'+ctx
        item=dict(item_id=iid, slots=1)
        meta=dict(row_id=row,source_id=row,control=False,
                  slots=[dict(offset=1,google='ь',kind='final',prior='unknown')])
        key=dict(context=ctx,readers={reader:[iid]},items={iid:meta})
        answer=dict(item_id=iid,slots={'1':'ъ'},confidence={'1':'high'},
                    unmarked_final_hard_signs=[],pre1918='yes',note='')
        jsonl(packs/ctx/reader/'items.jsonl',[item]); dump(art/f'keys/{stem}.json',key)
        jsonl(art/f'answers/{stem}.jsonl',[answer]); dump(art/f'answers/{stem}.scan.json',dict(ok=True,violations=[]))
        mapped, score=map_records([answer],key,[item],reader)
        jsonl(art/f'answers/{stem}.mapped.jsonl',mapped); dump(art/f'answers/{stem}.controls.json',score)
    return art,packs


@pytest.mark.parametrize('void_r2',['absent','unclean','malformed','clean_conflicting'])
def test_combiner_r3_ignores_r2(prepared,void_r2):
    art,_=prepared
    if void_r2 != 'absent':
        path=art/'answers/ctx04.r2.mapped.jsonl'
        if void_r2=='malformed': path.write_text('not JSON')
        else:
            record=rows(art/'answers/ctx04.r3.mapped.jsonl')[0]; record['call']='ь'
            jsonl(path,[record]); dump(art/'answers/ctx04.r2.controls.json',dict(status='VALID'))
            dump(art/'answers/ctx04.r2.scan.json',dict(ok=void_r2=='clean_conflicting'))
    summary=combine(art)
    assert summary['status']=='complete' and summary['counts']=={'edit_hard':4}
    assert 'ctx04.r3' in summary['input_contexts'] and 'ctx04.r2' not in summary['input_contexts']
    record=next(d for d in rows(art/'decisions.jsonl') if d['row_id']=='row-ctx04')
    assert set(record['reads'])=={'r1','r3'}
    assert record['reads']['r3']['context']=='ctx04/r3'


def test_combiner_missing_r3_never_falls_back(prepared):
    art,_=prepared
    for suffix in ['mapped.jsonl','controls.json','scan.json']:
        (art/f'answers/ctx04.r2.{suffix}').write_bytes((art/f'answers/ctx04.r3.{suffix}').read_bytes())
    (art/'answers/ctx04.r3.mapped.jsonl').unlink()
    summary=combine(art)
    assert summary['status']!='complete'
    record=next(d for d in rows(art/'decisions.jsonl') if d['row_id']=='row-ctx04')
    assert record['reason']=='missing_independent_reads' and record['reads']['r3'] is None


def test_combiner_unclean_r3_refuses(prepared):
    art,_=prepared; dump(art/'answers/ctx04.r3.scan.json',dict(ok=False))
    with pytest.raises(ValueError,match='unclean'): combine(art)


def test_ctx04_r2_never_independent():
    p=dict(row_id='row',source_id='row',offset=1,google='ь',kind='final',prior='unknown')
    reads=[dict(reader=r,context='ctx04/'+r,call='ъ',gate_status='VALID') for r in ['r1','r2']]
    assert decide(p,reads)['reason']=='missing_independent_reads'


@pytest.mark.parametrize('failure',['missing','false','violations','skipped','non_boolean'])
def test_finalize_scan_gate_before_any_writes(prepared,failure):
    art,packs=prepared; path=art/'answers/ctx04.r3.scan.json'
    if failure=='missing': path.unlink()
    else: dump(path,dict(ok=1 if failure=='non_boolean' else failure!='false',
        violations=['unresolved'] if failure=='violations' else [],manifest_check_skipped=failure=='skipped'))
    before={str(p):p.read_bytes() for p in art.rglob('*') if p.is_file()}
    with pytest.raises(ValueError,match='scan has not cleared'): finalize(art,packs,owner_build=lambda:pytest.fail('owner called'))
    assert before=={str(p):p.read_bytes() for p in art.rglob('*') if p.is_file()}


@pytest.mark.parametrize('stem',[s for _,_,s in accepted_contexts()])
def test_finalize_all_eight_scans_required(prepared,stem):
    art,packs=prepared; (art/f'answers/{stem}.scan.json').unlink()
    with pytest.raises(ValueError,match=stem): finalize(art,packs)


def test_finalize_mapping_combiner_owner_summary_order(prepared):
    art,packs=prepared
    for p in (art/'answers').glob('*.mapped.jsonl'): p.unlink()
    # A VOID legacy scan must have no effect on accepted finalisation.
    dump(art/'answers/ctx04.r2.scan.json',dict(ok=False,violations=['15 unmatched']))
    called=[]
    def owner():
        assert (art/'answers/ctx04.r3.mapped.jsonl').is_file()
        assert json.loads((art/'decisions.summary.json').read_text())['status']=='complete'
        assert not (art/'finalization.summary.json').exists()
        called.append(True)
        return dict(html='fixture.html',html_bytes=100)
    result=finalize(art,packs,owner_build=owner)
    assert called==[True] and result['status']=='complete'
    assert result['steps']==['scan_check','mapping','combiner','owner_sheet','summary']
    assert json.loads((art/'finalization.summary.json').read_text())==result


def test_finalize_owner_failure_no_success_summary(prepared):
    art,packs=prepared
    def owner(): raise ValueError('owner fixture failure')
    with pytest.raises(ValueError,match='owner fixture'): finalize(art,packs,owner_build=owner)
    assert not (art/'finalization.summary.json').exists()


def test_finalize_dry_run_no_writes(prepared):
    art,packs=prepared
    before={str(p):p.read_bytes() for p in art.rglob('*') if p.is_file()}
    out=finalize(art,packs,dry_run=True)
    assert out['dry_run'] and out['scans_cleared'] and not out['writes']
    assert before=={str(p):p.read_bytes() for p in art.rglob('*') if p.is_file()}


def test_r3_launcher_paths():
    p=subprocess.run(['bash',str(WORK/'scripts/secondary/reading/run_bed.sh'),'ctx04','r3'],
        env=dict(os.environ,RU1_DRY_RUN='1'),capture_output=True,text=True,check=True)
    out=dict(l.split('=',1) for l in p.stdout.splitlines())
    for field,suffix in [('answers','jsonl'),('scan','scan.json'),('mapped','mapped.jsonl'),('controls','controls.json')]:
        assert out[field]==str(WORK/f'artifacts/ru1/answers/ctx04.r3.{suffix}')
    assert out['key']==str(WORK/'artifacts/ru1/keys/ctx04.r3.json') and out['pack'].endswith('/ctx04/r3')


def test_void_launcher_refused():
    p=subprocess.run(['bash',str(WORK/'scripts/secondary/reading/run_bed.sh'),'ctx04','r2'],
        env=dict(os.environ,RU1_DRY_RUN='1'),capture_output=True)
    assert p.returncode==64


def test_r3_build_and_closure_fixture(tmp_path,monkeypatch):
    from PIL import Image
    import ru1_third_reader as builder
    import scan_packs
    from common import sha
    art=tmp_path/'art'; packs=tmp_path/'packs'; source=packs/'ctx04/r1'
    (source/'crops').mkdir(parents=True)
    image=source/'crops/temp.png'; Image.new('RGB',(10,10),'white').save(image)
    h=sha(image); image.rename(source/f'crops/{h}.png')
    items=[dict(item_id=f'k{n:010x}',crop=f'crops/{h}.png',slots=1,masked_text=f'{n}⟦1⟧') for n in range(1,10)]
    key=dict(readers={'r1':[i['item_id'] for i in items]},items={i['item_id']:dict(source_id='secret',control=n%3==0,source_crop_sha256=h) for n,i in enumerate(items)})
    jsonl(source/'items.jsonl',items);dump(art/'keys/ctx04.json',key)
    monkeypatch.setattr(builder,'ROOT',art);monkeypatch.setattr(builder,'PACK_ROOT',packs);monkeypatch.setattr(scan_packs,'ROOT',art)
    result=builder.build(); assert result['ok'] and result['items']==9 and result['controls']==3
    with pytest.raises(ValueError,match='overwrite'):builder.build()
    r3=packs/'ctx04/r3'; assert scan_packs.scan(r3,'yer')['ok']
    key3=json.loads((art/'keys/ctx04.r3.json').read_text())
    assert sorted(map(lambda m:json.dumps(m,sort_keys=True),key3['items'].values()))==sorted(map(lambda m:json.dumps(m,sort_keys=True),key['items'].values()))
    reordered=rows(r3/'items.jsonl');reordered[0],reordered[1]=reordered[1],reordered[0]
    jsonl(r3/'items.jsonl',reordered)
    assert not scan_packs.scan(r3,'yer')['ok']


def test_mapper_r3_dry_run():
    p=subprocess.run([sys.executable,'-B',str(WORK/'scripts/secondary/reading/ru1_map_answers.py'),
        'ctx04',str(WORK/'artifacts/ru1/answers/ctx04.r3.jsonl'),'--reader','r3','--dry-run'],
        capture_output=True,text=True,check=True)
    result=json.loads(p.stdout)
    assert result['dry_run'] and result['items']==88
    assert result['mapped'].endswith('/ctx04.r3.mapped.jsonl') and result['key'].endswith('/ctx04.r3.json')


def test_finalizer_shell_dry_run():
    p=subprocess.run(['bash',str(WORK/'scripts/secondary/ru1_finalize.sh'),'--dry-run'],
        capture_output=True,text=True,check=True)
    result=json.loads(p.stdout)
    assert result['dry_run'] and not result['writes']
    assert result['accepted_contexts'][-1]=='ctx04.r3' and result['excluded']==['ctx04.r2']
