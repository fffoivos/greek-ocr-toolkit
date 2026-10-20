"""CP-5r regression controls and durable-input storage lifecycle."""
from collections import Counter
from pathlib import Path
import unicodedata as ud
import pytest
from PIL import Image
from collect_v3.common import read_json,write_json,write_rows,rows,sha
from collect_v3.config import config,SPECS
from collect_v3.vendor.lookalike_rule import apply,is_lookalike
from collect_v3.pipeline import primary
from collect_v3.rules import apply_rules
from collect_v3.runner import probe_qualified,finalize
from collect_v3.storage import compact,materialize,ensure_crop
from collect_v3.tests.test_rev2 import row

ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'docs/harvest/collect_v3'

@pytest.mark.parametrize('token,expected',[('Η.','H.'),('Τ.','T.'),('Τ.','T.')])
def test_lookalike_mapping_witnesses(token,expected,request):
    prefix=['V.','N.','Iph.'][request.node.callspec.indices['token']]
    assert apply(prefix+' '+token+' Smith')==(prefix+' '+expected+' Smith','mapped')

@pytest.mark.parametrize('form',['NFC','NFD'])
@pytest.mark.parametrize('token',['ό','ὅ','ο\u0301','ο\u0338','Η\u0301'])
def test_accented_token_never_maps(form,token):
    token=ud.normalize(form,token)
    assert not is_lookalike('('+token+').')
    assert apply('Latin '+token+' Latin')==(ud.normalize('NFC','Latin '+token+' Latin'),'unchanged')

@pytest.mark.parametrize('token',['υ','αυ','Ηυ','υτ.'])
def test_upsilon_ambiguity_excludes_line(token):
    assert apply('Latin '+token+' Latin')==(None,'excluded')


def test_660_recount_and_binding():
    receipt=read_json(ART/'lookalike_recount.json');pool=rows(ART/'lookalike_660_candidates.jsonl')
    assert len(pool)==660 and sha(ART/'lookalike_660_candidates.jsonl')==receipt['candidates_sha256']
    assert sha(ROOT/'collect_v3/vendor/lookalike_rule.py')==receipt['rule_sha256']
    assert Counter(apply(r['label'])[1] for r in pool)=={'unchanged':618,'mapped':3,'excluded':39}
    assert Counter(apply(ud.normalize('NFD',r['label']))[1] for r in pool)==receipt['outcomes']

@pytest.mark.parametrize('year',[1982,1985,1986,1990])
def test_gazette_physical_class_wins_over_year(year):
    r=dict(inventory={'greek_letters':30},line_tags=[],mixed_line=False,script_class='greek_poly')
    page=dict(source='gazette_modern',year=year)
    assert primary(r,page)=='poly1900'
    a=row(source='gazette_modern',year=year,script_class='greek_poly');a['primary_class']=primary(r,page)
    apply_rules([a]);assert a['gazette_polytonic'] and a['marks_correction_required'] and not a['admitted'] and not a['candidate_usable']
    assert a['source_marks']['rate'] is None
    assert 'gazette_polytonic_failed_v2' in a['text_exclusions']
    stale=row('stale',source='gazette_modern',year=year,script_class='greek_poly');stale['primary_class']='modern_scanned'
    apply_rules([stale]);assert stale['primary_class']=='poly1900' and not stale['candidate_usable']
    r['script_class']='greek_mono';assert primary(r,page)=='modern_scanned'


def test_gazette_manifests_probe_fallback_and_conditional_alternative():
    w1=[r for r in rows(ART/'W1_manifest.jsonl') if r['source']=='gazette_modern']
    w2=[r for r in rows(ART/'W2_manifest.jsonl') if r['source']=='gazette_modern']
    alt=rows(ART/'W2_gazette_probe_qualified.jsonl')
    assert len(w1)==240 and Counter(r['item_record']['year'] for r in w1)=={1982:10,1983:10,1984:10,1985:10,1986:40,1987:40,1988:40,1989:40,1990:40}
    assert len(w2)==960 and set(r['item_record']['year'] for r in w2)==set(range(1986,1991))
    assert len(alt)==960 and set(r['item_record']['year'] for r in alt)==set(range(1982,1991))
    assert not {r['id'] for r in w1}&{r['id'] for r in w2+alt}
    assert len({r['id'] for r in alt})==960
    assert not probe_qualified({})
    assert probe_qualified({'probe_1982_1985':dict(passed=True,letters=dict(y=90,n=100),monotonic_share=.71,pages=40)})

@pytest.mark.parametrize('change',[{'letters':{'y':89,'n':100}},{'monotonic_share':None},{'monotonic_share':float('nan')},{'pages':39},{'letters':{'y':36,'n':39}}])
def test_probe_cannot_enter_w2_without_qualification(change):
    value=dict(passed=True,letters=dict(y=90,n=100),monotonic_share=.7,pages=40);value.update(change)
    with pytest.raises(ValueError):probe_qualified({'probe_1982_1985':value})


def test_same_period_yields_and_corrected_inventory():
    assert SPECS['serbia'][4]['cyrillic']==614/30 and SPECS['lekythos'][1]==13
    assert SPECS['gazette_modern'][4]==dict(modern_scanned=525/12,numerics_tables=67/12,headings_caps=57/12,dialogue_fiction=36/12)
    inventory=next(r for r in read_json(ART/'remaining_inventory.json')['sources'] if r['source']=='nlg')
    assert inventory['remaining_items']==23 and inventory['known_capped_pages']<=920
    receipt=read_json(ART/'plan_receipt.json')
    assert receipt['gazette']['frame_issues']==37764
    assert receipt['class_projection']['modern_scanned']['W1_candidate_rows']==8750
    assert receipt['class_projection']['modern_scanned']['candidate_rows']==50750


def test_compaction_refuses_corruption_and_preserves_only_bound_inputs(tmp_path):
    image=tmp_path/'cache/pages/p.jpg';image.parent.mkdir(parents=True);Image.new('L',(100,30),255).save(image)
    response=tmp_path/'responses/p.json';write_json(response,{'document':{'pages':[{'lines':[],'tokens':[]}]}})
    crop=tmp_path/'W1/crops/r.png';crop.parent.mkdir(parents=True);Image.new('L',(100,30),255).save(crop)
    r=row(crop=str(crop));record=dict(id='p',source='nlg',status='completed',tranche='W1',image=str(image),image_sha256=sha(image),response=str(response),response_sha256=sha(response),rows=[r],analysis_page={'id':'p'})
    path=tmp_path/'W1/pages/p.json';write_json(path,record);write_rows(tmp_path/'W1/features.jsonl',[r])
    write_json(tmp_path/'W1/c1/nlg__poly1850_key.json',{'c001':{'line_id':'r'}})
    response.write_text('{}')
    with pytest.raises(ValueError,match='hash mismatch'):compact(tmp_path,tmp_path/'cache','W1')
    assert crop.exists() and 'rows' in read_json(path)
    write_json(response,{'document':{'pages':[{'lines':[],'tokens':[]}]}})
    result=compact(tmp_path,tmp_path/'cache','W1')
    assert result['pages']==1 and image.exists() and response.exists()
    assert 'rows' not in read_json(path) and not crop.exists() and not (tmp_path/'W1/features.jsonl').exists()
    assert (tmp_path/'W1/c1/nlg__poly1850_key.json').exists()


def test_offline_materialization_and_review_crop_hash(tmp_path,monkeypatch):
    from collect_v3 import pipeline
    image=tmp_path/'cache/pages/p.jpg';image.parent.mkdir(parents=True);Image.new('L',(100,30),255).save(image)
    response=tmp_path/'responses/p.json';write_json(response,{'document':{'text':'α','pages':[{'lines':[{}]}]}})
    def analyse(page,raw,cache,crop_root,**kwargs):
        import io
        from collect_v3.common import atomic_bytes
        crop=Path(crop_root)/'r.png';buf=io.BytesIO()
        with Image.open(page['image']) as im:im.convert('L').crop((0,0,100,20)).save(buf,format='PNG',compress_level=3)
        atomic_bytes(crop,buf.getvalue());r=row(crop=str(crop));r.update(crop_bbox=[0,0,100,20],crop_sha256=sha(crop));return [r]
    monkeypatch.setattr(pipeline,'analyse',analyse)
    write_json(tmp_path/'W1/pages/p.json',dict(id='p',source='nlg',status='completed',tranche='W1',image=str(image),image_sha256=sha(image),response=str(response),response_sha256=sha(response),analysis_page={'id':'p'}))
    rr=materialize(tmp_path,'W1');assert len(rr)==1 and not Path(rr[0]['crop']).exists()
    assert sha(ensure_crop(rr[0]))==rr[0]['crop_sha256']
    compact(tmp_path,tmp_path/'cache','W1');assert not Path(rr[0]['crop']).exists()
    assert config()['storage_diet']
    with pytest.raises(ValueError,match='must be retained'):config(prune_images=True)


def test_pdf_retention_stable_and_unstable_url(tmp_path):
    import pypdfium2 as pdfium
    from collect_v3.routes.providers import Routes
    from collect_v3.transport import HTTP,HostBucket
    from collect_v3.offline import VirtualClock,no_network
    doc=pdfium.PdfDocument.new();doc.new_page(100,150);pdf=tmp_path/'fixture.pdf';doc.save(pdf);doc.close()
    clock=VirtualClock()
    http=HTTP(tmp_path/'cache',sender=lambda url:(200,{},b'User-agent: *\nAllow: /') if url.endswith('/robots.txt') else (200,{},pdf.read_bytes()),bucket=HostBucket(tmp_path/'limiter',clock=clock.time,sleep=clock.sleep))
    routes=Routes(http,tmp_path/'cache')
    for stable in (True,False):
        item=dict(provider='lekythos',id=str(stable),route='pdf',url=f'https://source.invalid/{stable}.pdf',stable_redownload_url=stable)
        record=dict(id=str(stable),source='lekythos',item=str(stable),item_record=item,item_pages=1,page=1,page_slot=0,page_seed='seed')
        with no_network():page=routes.fetch(record)
        assert page['source_pdf_retained']==(not stable)
        assert (tmp_path/'cache/render_bindings'/(str(stable)+'.json')).exists()
        assert bool(list((tmp_path/'cache/http').glob('*.body')))==(not stable)
        assert routes.fetch(record)['image_sha256']==page['image_sha256']
    def no_prefetch(record):raise AssertionError('IIIF bounds resolution must not consume the W2 image quota')
    routes.fetch=no_prefetch
    routes.prepare_pages([{'route':'iiif'},{'route':'ia'}])


def test_c2_caps_use_deduped_rows_and_block_violating_classes(tmp_path):
    from collect_v3.cards import cards
    a=row(crop='unneeded.png');a.update(usable_final=True,candidate_usable=True,label_after_conventions=a['fixed_label'])
    write_rows(tmp_path/'W1/features.jsonl',[a])
    assert cards(config(output_root=str(tmp_path)),'W1','C2')==[]
    blocked=read_json(tmp_path/'W1/c2/release_cap_blocks.json')
    assert blocked['stage']=='after_dedupe' and blocked['blocked_classes']==['poly1850']


def test_commit_helper_excludes_even_tracked_ignored_files(tmp_path):
    import subprocess
    from collect_v3.commit_helper import nonignored
    subprocess.run(['git','init','-q',str(tmp_path)],check=True)
    (tmp_path/'.gitignore').write_text('ignored/\n')
    (tmp_path/'ignored').mkdir();(tmp_path/'ignored/replay.json').write_text('{}')
    (tmp_path/'source.py').write_text('pass\n')
    subprocess.run(['git','-C',str(tmp_path),'add','-f','ignored/replay.json'],check=True)
    paths,ignored=nonignored(['source.py','ignored/replay.json'],root=tmp_path)
    assert paths==['source.py'] and ignored==['ignored/replay.json']


def test_c1_gazette_periods_never_pool(tmp_path):
    from collect_v3.cards import cards
    image=tmp_path/'crop.png';Image.new('L',(10,10),255).save(image)
    rr=[]
    for i in range(160):
        a=row(str(i),source='gazette_modern',crop=str(image));a.update(primary_class='modern_scanned',year=1984 if i<80 else 1988,gazette_stratum='probe_1982_1985' if i<80 else 'measured_1986_1990',crop_sha256=sha(image),label_after_conventions=a['fixed_label'],candidate_usable=True,usable_final=False,source_marks={},crop_tight_page=True)
        rr.append(a)
    write_rows(tmp_path/'W1/features.jsonl',rr)
    report=cards(config(output_root=str(tmp_path)),'W1','C1')
    assert len(report)==2 and {r['gazette_stratum'] for r in report}=={'probe_1982_1985','measured_1986_1990'}
    assert all(r['pool']==80 and r['cards']==80 for r in report)


def test_c2_caps_and_release_pool_cover_both_waves(tmp_path):
    from collect_v3.cards import cards
    image=tmp_path/'crop.png';Image.new('L',(10,10),255).save(image)
    rr=[]
    for i in range(10):
        a=row(str(i),crop=str(image));a.update(item=f'book{i}',tranche='W1' if i<9 else 'W2',usable_final=True,candidate_usable=True,crop_sha256=sha(image),label_after_conventions=a['fixed_label'],source_marks={})
        rr.append(a)
    write_rows(tmp_path/'W1/features.jsonl',rr[:9]);write_rows(tmp_path/'W2/features.jsonl',rr[9:])
    report=cards(config(output_root=str(tmp_path)),'W2','C2')
    assert len(report)==1 and report[0]['pool']==10 and report[0]['cards']==10
    assert read_json(tmp_path/'W2/c2/release_cap_blocks.json')['blocked_classes']==[]
    spread=read_json(tmp_path/'W2/audits/spread_caps.json')
    assert spread['stage']=='after_dedupe' and all(r['class_rows']==10 and r['passed'] for r in spread['rows'])
