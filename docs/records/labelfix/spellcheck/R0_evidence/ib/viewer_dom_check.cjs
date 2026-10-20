const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = process.argv[2];
const html = fs.readFileSync(path, 'utf8');
const script = html.split('<script>')[1].split('</script>')[0];
const store = new Map();
class Element {
  constructor(tag) { this.tag=tag; this.children=[]; this.dataset={}; this.style={}; }
  append(...children) { this.children.push(...children); }
  click() { this.clicked=true; }
}
const main = new Element('main'), exportButton = new Element('button');
const sandbox = { document: { createElement:tag=>new Element(tag), querySelector:q=>q==='main'?main:q==='#export'?exportButton:null }, localStorage:{getItem:k=>store.get(k)||null,setItem:(k,v)=>store.set(k,v)}, Blob, URL };
vm.createContext(sandbox);
vm.runInContext(script, sandbox);
const items=vm.runInContext('items',sandbox);
assert.equal(main.children.length,items.length);
for(let i=0;i<items.length;i++) {
  const card=main.children[i];
  assert.equal(card.children[0].textContent,items[i].id);
  assert.equal(card.children.find(e=>e.tag==='img').src,items[i].img);
  const detail=card.children.find(e=>e.tag==='details');
  assert.equal(detail.open,true);
  assert.equal(detail.children.find(e=>e.tag==='img').src,items[i].line_img);
  assert.equal(card.children.filter(e=>e.tag==='button').length,['A','B','C'].filter(k=>k in items[i]).length);
}
main.children[0].children.find(e=>e.tag==='button').onclick();
const note=main.children[0].children.find(e=>e.tag==='textarea');
note.value='QA only, in-memory DOM';note.oninput();
let answers=JSON.parse(store.get('r0-blind-ib-v1'));
assert.equal(answers[items[0].id].choice,'A');
assert.equal(answers[items[0].id].note,note.value);
assert.equal(main.children[0].style.border,'2px solid #276');
exportButton.onclick();
assert.equal(store.has('r0-blind-v1'),false);
console.log(JSON.stringify({complete:true,cards:items.length,all_image_references_match:true,all_full_line_details_open:true,candidate_button_counts_match:true,choice_and_note_persist:true,export_handler_runs:true,storage_isolated_from_R0_and_IA:true,test_environment:'in-memory DOM harness; no browser rendering claimed'}));
