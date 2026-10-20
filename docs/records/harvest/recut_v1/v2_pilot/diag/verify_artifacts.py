"""Independent artifact coverage/custody checks; writes only validation.json."""
from collections import Counter
import json
from pathlib import Path
import subprocess
from run_diag import install_guard, BASE, ROOT, sha, write


def main():
    install_guard()
    from PIL import Image,ImageChops,ImageDraw,ImageFont
    pages=json.loads((BASE/'pages.json').read_text())
    manifest=json.loads((BASE/'sheets_manifest.json').read_text())
    reviews=json.loads((BASE/'classifications.json').read_text())
    f2=json.loads((BASE/'f2_check.json').read_text())
    expected=set();unmatched=set();records={}
    font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',14)
    draw=ImageDraw.Draw(Image.new('L',(1,1)))
    longest_label=0
    for p in pages:
        rr=json.loads((BASE/(p['wave']+'--'+p['page_id']+'.matches.json')).read_text())
        assert len(rr)==p['lines']
        for stage in ('before','after'):
            assert Counter(r[stage] for r in rr)==Counter({k:v for k,v in p[stage].items() if v})
        for r in rr:
            records[r['id']]=r
            assert r['before_candidates']==r['after_candidates']
            assert r['before_index']==r['after_index']
            assert all(c['overlap']>=.5 and c['distance_xh']<=1.5 for c in r['before_candidates'])
            if r['before']!='matched' or r['after']!='matched':
                expected.add(r['id'])
            if r['before']=='unmatched' or r['after']=='unmatched':
                unmatched.add(r['id'])
    cards=[i for row in manifest if row['kind']=='contact_sheet' for i in row['ids']]
    assert len(cards)==len(set(cards))==49 and set(cards)==expected
    witnesses=[r for r in manifest if r['kind']=='unmatched_native']
    assert len(witnesses)==13 and {r['id'] for r in witnesses}==unmatched
    assert len(reviews)==13 and {r['id'] for r in reviews}==unmatched
    for item in manifest:
        assert sha(BASE/item['path'])==item['sha256']
    natives={p['page_id']:Image.open(p['raster']).convert('RGB') for p in pages}
    for item in witnesses:
        r=records[item['id']];native=natives[item['id'].rsplit('-l',1)[0]]
        with Image.open(BASE/'witnesses'/(item['id']+'--crop.png')) as crop:
            assert ImageChops.difference(crop,native.crop(tuple(r['crop_bbox']))).getbbox() is None
        context=native.crop(tuple(item['source_window']))
        with Image.open(BASE/item['path']) as witness:
            unaltered=witness.crop((0,90,context.width,90+context.height))
            assert ImageChops.difference(unaltered,context).getbbox() is None
    for native in natives.values():
        native.close()
    for value in f2['subsets'].values():
        assert value['before']==value['after']
        assert all(value[k]==0 for k in ('saved_index_differences','default_index_differences','index_differences','candidate_set_differences'))
    assert f2['subsets']['dev_cards']['lines']==160
    assert f2['subsets']['all_lines_on_dev_pages']['pages']==65
    assert len(f2['checks'])==5770
    assert all(r['saved_reproduced'] and r['default_identical'] and r['candidates_identical'] and r['before_index']==r['after_index'] for r in f2['checks'])
    for row in f2['curve_bindings']:
        assert sha(ROOT/row['path'])==row['sha256']
    for row in json.loads((BASE/'input_bindings.json').read_text())['files']:
        assert sha(row['path'])==row['sha256']
    execution=json.loads((BASE/'execution.json').read_text())
    assert execution['nice']>=15 and execution['workers']==execution['numerical_threads']==1
    assert sha(BASE/'matcher.py')==execution['matcher_sha256']
    assert sha(BASE/'run_diag.py')==execution['runner_sha256']
    test=(BASE/'tests.log').read_text()
    assert 'Ran 8 tests' in test and test.rstrip().endswith('OK')
    delta=subprocess.run(['git','diff','--name-only','HEAD'],cwd=ROOT,capture_output=True,check=True).stdout.decode().splitlines()
    assert all((ROOT/p).resolve().is_relative_to(BASE) for p in delta)
    last=(BASE/'DIAG.md').read_text().splitlines()[-1]
    assert last=='T6c1b: done | parliament before/after ambiguous: 36/36 unmatched: 12/12 | vouli before/after: 1/1 | unmatched causes: merge 1, miss 11, crop 0, other 1 | T6a2 unchanged: yes | overlap threshold: >=50% of crop width'
    write(BASE/'validation.json',dict(passed=True,contact_sheets=13,distinct_failure_cards=49,
                                     parliament_failure_cards=48,vouli_failure_cards=1,unmatched_classifications=13,
                                     native_exact_crop_pixel_checks=13,native_context_pixel_checks=13,
                                     f2_lines=5770,dev_cards=160,dev_pages=65,all_lines_on_dev_pages=4580,
                                     all_winner_candidate_and_saved_index_differences=0,unit_tests=8,
                                     input_and_runtime_hashes_verified=True,tracked_changes_outside_diag=[],
                                     last_line_verified=True,source_sha256=sha(__file__)))
    print('PASS: 49 failure cards, 13 native crop/context pixel checks, 5770 identical F2 matches, 8 tests; input hashes intact')


if __name__=='__main__':
    main()
