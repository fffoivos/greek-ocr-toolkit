"""Exercise the actual owner-sheet autosave script without a network or database."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import pytest


def test_note_only_save_never_submits_printed_prefill(tmp_path):
    node=shutil.which('node')
    if not node:pytest.skip('node unavailable')
    path=Path(__file__).resolve().parents[2]/'scripts/labelfix/sheet_build.py'
    spec=importlib.util.spec_from_file_location('owner_sheet',path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    script=mod.SCRIPT.removeprefix('<script>').removesuffix('</script>')
    harness=r'''
const assert=require('node:assert/strict');
const values={printed:'GOOGLE',note:'old'}; const events={}; const saved=[];
function field(k){return {get value(){return values[k]},set value(x){values[k]=x},addEventListener(e,f){(events[k+e]??=[]).push(f)}}}
const fields={printed:field('printed'),note:field('note'),status:{textContent:''}};
const card={dataset:{line:'x'},querySelector(s){return fields[s.slice(1)]},classList:{toggle(){}}};
const db={collection(){return {limit(){return {async get(){return {docs:[{exists:true,id:'x',data(){return {printed:'UNEDITED_PREFILL',note:'old'}}}]}}}}}},doc(){return {async set(body,opts){saved.push({body,opts})}}}};
global.window={claude:{async use(){return db}}};global.document={querySelectorAll(){return [card]},querySelector(){return card}};
async function fire(k,e){for(const f of events[k+e]||[])f();await new Promise(r=>setImmediate(r))}
(async()=>{eval(SCRIPT);await new Promise(r=>setImmediate(r));
assert.equal(values.printed,'GOOGLE');values.note='my note';await fire('note','input');await fire('note','blur');
assert.equal(saved.length,1);assert.equal('printed' in saved[0].body,false);assert.equal('printed_edited' in saved[0].body,false);assert.equal(saved[0].opts.merge,true);
values.printed='PRINT';await fire('printed','input');await fire('printed','blur');assert.equal(saved[1].body.printed,'PRINT');assert.equal(saved[1].body.printed_edited,true);
})().catch(e=>{console.error(e);process.exit(1)});
'''
    js=tmp_path/'check.js';js.write_text('const SCRIPT='+json.dumps(script)+';\n'+harness)
    subprocess.run([node,str(js)],check=True,capture_output=True,text=True,timeout=10)
