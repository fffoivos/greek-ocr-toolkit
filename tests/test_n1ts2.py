"""Partial lead authority, uncertainty, physical boxes and third-reader custody."""
import copy
import json
from pathlib import Path
from greekocr.ops.data_root import input_path as _data_input
from tests._paths import require_file
import sys
from collections import Counter
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/numerics'))
import n1ts
import n1ts2
from n1t_boxes import detection_image,COLORS
from greekocr.numerics.owner_v2 import build,GROUPS
from test_n1t import owner_fixture,vote
from greekocr.numerics.combine_v2 import decide


def test_partial_only_raised_and_hold_keeps_google(tmp_path):
    line,slots,ds=owner_fixture(tmp_path)
    # Both raised cells must be supplied, while a separate review cell remains pending.
    other=next(s for s in slots if s['glyph']==' ')
    i=next(i for i,d in enumerate(ds) if d['slot_id']==other['slot_id'])
    ds[i]=decide(other,[vote(meaning='space'),vote('r2','nothing')])
    raised,_=n1ts.selections(ds)
    rulings=[dict(slot_id=d['slot_id'],truth='hold' if j==0 else 'raised dot') for j,d in enumerate(raised)]
    before=copy.deepcopy(ds)
    final=n1ts.apply_lead(slots,ds,rulings,partial=True)
    assert ds==before and final[i]==ds[i]
    assert sum(d['status']=='lead_review' for d in final)==2
    assert final[next(i for i,d in enumerate(final) if d['slot_id']==raised[0]['slot_id'])]['reason']=='lead_hold_too_faint'
    c=build([line],slots,final)[0][0]
    assert c['printed']=='1-234 5·678'
    assert 'unsure:lead_hold_too_faint' in c['rows'][2]['text']
    assert 'unsure:reader_disagreement' in {t['text'] for t in c['tags']}
    with pytest.raises(ValueError,match='raised set'):n1ts.apply_lead(slots,ds,rulings[:-1],partial=True)


def test_lead_edit_rule_outside_thousands(tmp_path):
    line,slots,ds=owner_fixture(tmp_path)
    raised,_=n1ts.selections(ds)
    for s in slots:s['grammar_candidates']=['other']
    final=n1ts.apply_lead(slots,ds,[dict(slot_id=d['slot_id'],truth='raised dot') for d in raised],partial=True)
    assert sum(d['edit_candidate'] is not None for d in final)==2
    assert all(d['edit'] is None and not d['apply_edit'] for d in final)


def test_box_raster_number_and_dashed_style(tmp_path):
    from PIL import Image
    image=Image.new('RGB',(120,40),'white')
    slots=[dict(number=7,style='unsure',locator_span=[10,40],evidence={'attached':[dict(bbox=[10,5,40,30])]}),
           dict(number=12,style='decided-changed',locator_span=[60,90],evidence={'attached':[dict(bbox=[60,5,90,30])]})]
    out=detection_image(image,slots)
    assert out.size==(240,110)
    assert out.getpixel((20,10))!=(255,255,255)
    assert out.getpixel((28,10))==(255,255,255) # physical dash gap
    assert out.getpixel((128,10))!=(255,255,255) # solid changed box
    assert any(p!=(255,255,255) for p in out.crop((0,80,240,110)).getdata())


def test_actual_rulings_and_all_pending_slots_retained():
    require_file('artifacts/n1/n1t2/slots.jsonl')
    slots,ds,_,_=n1ts.combine();r= n1ts.rows(n1ts.BASE/'lead_t.jsonl')
    assert Counter(x['truth'] for x in r)=={'raised dot':18,'baseline dot':2,'nothing':2,'hold':2}
    assert n1ts.sha(n1ts.BASE/'lead_t.jsonl')==(_data_input(n1ts.BASE/'lead_t.jsonl.sha256')).read_text().split()[0]
    final=n1ts.apply_lead(slots,ds,r,partial=True);byid={d['slot_id']:d for d in final}
    ruled={x['slot_id'] for x in r}
    assert all(d==byid[d['slot_id']] for d in ds if d['slot_id'] not in ruled)
    assert sum(d['truth_candidate'] is None for d in final)==640
    cards,spec=build(n1ts.rows(n1ts.OUT/'lines.jsonl'),slots,final)
    ss={s['slot_id']:s for s in slots}
    for c in cards:
        for b in c['slots']:
            assert ss[b['slot_id']]['read_reason']!='geometry-only'
            assert b['style'] in COLORS
        if c['group']==GROUPS[0]:
            assert any(ss[d['slot_id']]['glyph']=='-' and d['truth_candidate']=='raised dot' and
                       (d['status']=='lead_ruled' or d['agreement']) for d in final if d['line_id']==c['line_id'])
    audit=n1ts2.geometry_audit(slots,ds)
    assert len(audit['slots'])==30 and len(audit['disagreements'])==13 and not audit['safe']
    assert {'baseline dot','comma'}<={m for a in audit['disagreements'] for m in a['nonspace_marks']}


@pytest.mark.skip(reason="historical binding; green at opus/secondary-corrections@c5f864222; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_actual_r3_coverage_fresh_ids_controls_and_completed_reading():
    from n1_render import SCRATCH
    from n1_pack_closure import scan
    from greekocr.numerics.combine_v2 import MEANINGS,DASHES
    final=json.loads((_data_input(n1ts.OUT/'lead_decisions.json')).read_text())['decisions']
    expected={d['slot_id'] for d in final if d['status']=='lead_review' and d['reason'] in n1ts2.REASONS}
    out=n1ts.BASE/'n1t3';seen=Counter();ids=set();contexts=sorted((SCRATCH/'sol_packs/n1t3').glob('ctx*'))
    oldids={iid for p in (n1ts.OUT/'keys').glob('*.json') for iid in json.loads(_data_input(p).read_text())['items']}
    assert len(expected)==479 and len(contexts)==6
    oldorders=[]
    for reader in ('r1','r2'):
        suffix='' if reader=='r1' else '.r2'
        oldorders.append([i['slot_id'] for p in sorted((n1ts.OUT/'keys').glob('ctx*'+suffix+'.json'))
                          if ('.r2.' in p.name)==(reader=='r2') for i in json.loads(_data_input(p).read_text())['items'].values() if i['control_truth'] is None and i['slot_id'] in expected])
    order=[]
    for ctx in contexts:
        key=json.loads((_data_input(out/'keys'/(ctx.name+'.r3.json'))).read_text())
        assert set(key['readers'])=={'r3'} and len(key['items'])<=100
        assert not ids.intersection(key['items']) and not oldids.intersection(key['items']);ids.update(key['items'])
        controls=[i for i in key['items'].values() if i['control_truth'] is not None]
        assert len(controls)==len({i['slot_id'] for i in controls})==9
        assert {'raised dot',*DASHES}<={i['control_truth'] for i in controls}
        for iid in key['readers']['r3']:
            item=key['items'][iid]
            if item['control_truth'] is None:seen[item['slot_id']]+=1;order.append(item['slot_id'])
        assert scan(ctx/'r3',out,completed=True,meanings=MEANINGS)['ok']
        assert (ctx/'r3/answers.jsonl').exists()
        assert n1ts.rows(ctx/'r3/answers.jsonl')==n1ts.rows(n1ts.BASE/'answers/n1t3'/(ctx.name+'.r3.jsonl'))
    assert seen==Counter({s:1 for s in expected})
    assert all(order!=o and order!=list(reversed(o)) for o in oldorders)
    assert len(list((n1ts.BASE/'answers/n1t3').glob('*.jsonl')))==6


def test_note_identity_legacy_fallback_in_html():
    require_file('artifacts/n1/owner_sheet/n1_sheet.html')
    html=(_data_input(n1ts.BASE/'owner_sheet/n1_sheet.html')).read_text()
    assert 'data-legacy-note-ids=' in html and 'el.dataset.legacyNoteIds' in html
    assert "saved.filter(d => d.printed_edited" in html
    assert 'boxes with a dashed outline are gaps we have not decided yet; their Google character is kept in Ours' in html


def test_legacy_note_loading_preserves_two_notes_without_remote_write(tmp_path):
    require_file('artifacts/n1/owner_sheet/n1_sheet.html')
    import subprocess
    html=(_data_input(n1ts.BASE/'owner_sheet/n1_sheet.html')).read_text()
    js=html.split('<script>')[1].split('</script>')[0]
    harness=r'''
const assert = require('assert');
const reads=[],writes=[];
function field(value) { return {value,defaultValue:value,addEventListener(){}}; }
function element(id, legacy) {
 const note=field(''),printed=field('proposal');
 return {dataset:{line:id,legacyNoteIds:JSON.stringify([legacy])},note,printed,
 querySelector(s){return s==='.note'?note:s==='.printed'?printed:{textContent:''};},
 classList:{toggle(){}}};
}
const cards=[element('line-a','old-a'),element('line-b','old-b')];
const saved={'old-a':{note:'missed first one',printed:'7.504.643',printed_edited:true},
 'old-b':{note:'arent the rest detected?',printed:'old proposal',printed_edited:false}};
global.window={claude:{use:async()=>({doc(path){return {async get(){reads.push(path);const data=saved[path.slice(6)];return {exists:!!data,data:()=>data};},async set(){writes.push(path);}};}})}};
global.document={querySelectorAll(s){return s.startsWith('.notes')?cards:[];},addEventListener(){}};
'''
    checks=r'''
setImmediate(()=>{
 assert.equal(cards[0].note.value,'missed first one');
 assert.equal(cards[0].printed.value,'7.504.643');
 assert.equal(cards[1].note.value,'arent the rest detected?');
 assert.equal(cards[1].printed.value,'proposal');
 assert.deepEqual(writes,[]);
 assert(reads.includes('notes/old-a')&&reads.includes('notes/old-b'));
});
'''
    p=tmp_path/'notes.cjs';p.write_text(harness+js+checks)
    r=subprocess.run(['node',str(p)],capture_output=True,text=True)
    assert r.returncode==0,r.stderr
