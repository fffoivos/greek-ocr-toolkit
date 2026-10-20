"""RU4E2 scope, native pixels and wave-1c population boundaries (offline fixtures)."""
import json
from pathlib import Path
import sys
from unittest.mock import patch
import pytest
from PIL import Image, PngImagePlugin
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/secondary'))
import ru4e2 as n
m=n.m


def test_census_or_rule_and_raw_offsets(tmp_path):
    meta=tmp_path/'meta.json';meta.write_text('[]')
    sources={s:tmp_path/(s+'.jsonl') for s in ('test','dev')}
    rr=[dict(id='a',source='wikisource_ru',doc='one',script_class='latin',label='  домъ домъ домъ домъ домъ конь. конь-\t'),
        dict(id='b',source='x',doc='two',script_class='Cyrillic',label='і'),
        dict(id='c',source='x',doc='three',script_class='latin',label='abЯ'),
        dict(id='d',source='x',doc='four',script_class='latin',label='Яюб')]
    m.jsonl(sources['test'],rr);m.jsonl(sources['dev'],[])
    data,books=n.census(sources,meta)
    assert {r['id'] for r in data}=={'a','b','d'}
    by={b['book']:b for b in books}
    assert by['wikisource_ru:one']['final_soft']==1
    assert by['wikisource_ru:one']['final_hard']==5
    assert by['x:two']['orthography']=='pre_reform'
    assert by['x:four']['orthography']=='other'
    selected,pp,_,_=m.inventory(sources,{'wikisource_ru:one'}, {'a'})
    assert len(pp)==1 and rr[0]['label'][pp[0]['offset']]=='ь'
    assert selected[0]['label'].encode()==rr[0]['label'].encode()


def test_selected_ids_do_not_expand_to_whole_book(tmp_path):
    p=tmp_path/'test.jsonl'
    m.jsonl(p,[dict(id=i,source='s',doc='d',label='конь') for i in ('yes','no')])
    selected,pp,_,_=m.inventory({'test':p},{'s:d'}, {'yes'})
    assert [r['id'] for r in selected]==['yes']
    assert [r['row_id'] for r in pp]==['yes']


def test_metadata_removed_without_pixel_change(tmp_path):
    original=tmp_path/'original.png';im=Image.new('RGB',(17,9),(3,19,71))
    metadata=PngImagePlugin.PngInfo();metadata.add_text('answer','do not expose')
    im.save(original,pnginfo=metadata)
    before=m.sha(original)
    path,provenance=n.clean_crop(original,tmp_path/'cache')
    assert m.sha(original)==before==provenance['original_crop_sha256']
    with Image.open(path) as copy:
        assert not copy.info and copy.tobytes()==im.tobytes() and copy.size==im.size
    assert m.sha(path)!=before
    assert n.clean_crop(original,tmp_path/'cache')[0]==path


def test_wave_sample_is_not_full_census(tmp_path):
    data=[dict(id=i,ru4e_split='test',script_class='cyrillic',label='домъ') for i in ('one','two')]
    manifest=tmp_path/'wave1c_prep/manifest_fix1.json';m.dump(manifest,[])
    for job,arm in [('job01','ctrl'),('job02','lc')]:
        for seed in range(3):
            for view in ('v2_test','v2_test_full_coverage'):
                p=tmp_path/'wave1c'/job/'predictions'/f'{arm}_s{seed}_{view}.jsonl'
                m.jsonl(p,[dict(line_id='one',script_class='cyrillic',gt='домъ')])
                m.dump(p.with_suffix('.receipt.json'),dict(predictions_sha256=m.sha(p)))
    result=n.compare_wave(data,tmp_path)
    assert result['matches'] is False
    assert len(result['comparisons'])==12
    assert all(r['missing_from_scored']==['two'] for r in result['comparisons'])


def test_non_nine_book_build_with_explicit_scope(tmp_path):
    p=tmp_path/'test.jsonl';image=tmp_path/'source.png'
    metadata=PngImagePlugin.PngInfo();metadata.add_text('private','original')
    Image.new('L',(15,7),123).save(image,pnginfo=metadata)
    m.jsonl(p,[dict(id='one',source='s',doc='d',label='домъ конь',crop=str(image))])
    b=tmp_path/'books.json';m.dump(b,dict(books={'s:d':{}}))
    clean,provenance=n.clean_crop(image,tmp_path/'cache')
    masked,slots=m.mask('домъ')
    for slot in slots:slot.update(control_truth='ъ')
    pool=[dict(control=True,row_id='control',source_id='control',book='c',slots=slots,masked_text=masked,
               image=str(clean),source_crop_sha256=m.sha(clean))]
    art,pack=tmp_path/'art',tmp_path/'packs'
    info=m.build({'test':p},b,art,pack,pool,selected_ids={'one'},
                 prepare_crop=lambda path:n.clean_crop(path,tmp_path/'cache'))
    assert info['candidate_positions']==1 and info['candidate_lines']==1
    one=m.rows(pack/'ctx01/r1/items.jsonl');two=m.rows(pack/'ctx01/r2/items.jsonl')
    assert [r['crop'] for r in one]==[r['crop'] for r in two][::-1]
    assert not {r['item_id'] for r in one}&{r['item_id'] for r in two}
    assert info['budget']['item_reads']==4
    key=json.loads((art/'keys/ctx01.json').read_text())
    candidate=next(r for r in key['items'].values() if not r['control'])
    assert candidate['original_crop_sha256']==m.sha(image)
    assert m.drive(art,pack,dry_run=True)['reads']==0
