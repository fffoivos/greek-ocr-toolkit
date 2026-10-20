// Run the actual shipped edition adapter against an instrumented DOM/DB fixture.
// This checks action semantics; it is not a browser-rendering/screenshot substitute.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const text=fs.readFileSync(__dirname+'/OWNER_REVIEW.html','utf8');
const payload=JSON.parse(text.split('const SPLIT1_CARDS = ')[1].split(';\n')[0]);
const code=fs.readFileSync(__dirname+'/sheet_adapter.js','utf8');
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
class Node{
 constructor(){this.dataset={};this.listeners={};this.value='';this.style={};this.textContent='';this.className='';this.attributes={};const set=new Set();this.classList={toggle:(k,v)=>{if(v===undefined)v=!set.has(k);v?set.add(k):set.delete(k);return v},add:k=>set.add(k),remove:k=>set.delete(k),contains:k=>set.has(k)};}
 addEventListener(name,fn){(this.listeners[name]??=[]).push(fn)}
 fire(name,args={}){for(const fn of this.listeners[name]||[])fn({target:this,stopPropagation(){},preventDefault(){},...args})}
 setAttribute(k,v){this.attributes[k]=v} focus(){this.fire('focusin')} blur(){this.fire('blur')} scrollIntoView(){} appendChild(){}
}
class Card extends Node{
 constructor(rec){super();this.nodes={};for(const k of ['.verdict','.note','.notes','.toolpill','.lock-label','.active-edition','.status'])this.nodes[k]=new Node();this.nodes['.notes'].querySelector=s=>s==='label'?this.label??=new Node():this.nodes[s];this.cells=[new Node(),new Node(),new Node(),new Node()];this.select=rec.entries.length>1?new Node():null;}
 querySelector(s){if(s==='.issue-select')return this.select;return this.nodes[s]}
 querySelectorAll(s){return s==='.edition-metadata td'?this.cells:[]}
}
async function fixture(seed={},lag=0){
 const cards=payload.map(x=>new Card(x)),document=new Node();document.querySelectorAll=s=>s==='.card'?cards:[];document.createElement=()=>new Node();document.body=new Node();const writes=[],reads=[];
 const db={doc(path){return {async get(){reads.push(path);return {exists:!!seed[path],data:()=>seed[path]||{}}},async set(doc,opts){writes.push({path,doc,opts});seed[path]={...seed[path],...doc}}}}};
 const context={SPLIT1_CARDS:JSON.parse(JSON.stringify(payload)),document,window:{claude:{use:async()=>{if(lag)await delay(lag);return db}}},setTimeout,clearTimeout,Date,Set,JSON,Promise,console};
 vm.runInNewContext(code,context);await delay(lag?10:50);return {cards,document,writes,reads,seed};
}
(async()=>{
 const first=payload[0].entries[0].edition_id,path='notes/split1:'+first;
 const f=await fixture({[path]:{note:'saved owner note',verdict:'DROP',updated:'2026-10-19 13:00'}});
 await delay(1100);assert.equal(f.reads.length,payload.reduce((n,c)=>n+c.entries.length,0));assert.equal(f.writes.length,0);
 assert.equal(f.cards[0].querySelector('.note').value,'saved owner note');assert.equal(f.cards[0].dataset.verdict,'DROP');
 f.cards[0].querySelector('.note').fire('blur');f.cards[0].fire('focusin');await delay(100);assert.equal(f.writes.length,0,'hydration/focus/blur must not write');
 f.cards[0].querySelector('.verdict').fire('click');await delay(380);assert.equal(f.writes.length,1);assert.equal(f.writes[0].path,path);assert.equal(f.writes[0].doc.verdict,'KEEP');
 assert.deepEqual(Object.keys(f.writes[0].doc).sort(),['line_id','note','updated','verdict']);assert.match(f.writes[0].doc.updated,/^\d{4}-\d\d-\d\d \d\d:\d\d$/);
 const note=f.cards[0].querySelector('.note');note.value='edited';note.fire('input');note.value='edited once';note.fire('input');await delay(1000);assert.equal(f.writes.length,2,'debounce yields one document write');assert.equal(f.writes[1].doc.note,'edited once');
 const gi=payload.findIndex(c=>c.entries.length>1),g=f.cards[gi];g.select.value='1';g.select.fire('change');await delay(100);assert.equal(f.writes.length,2,'issue selection must not write');assert.equal(g.querySelector('.notes').dataset.id,'split1:'+payload[gi].entries[1].edition_id);
 g.querySelector('.verdict').fire('click');await delay(380);assert.equal(f.writes.length,3);assert.equal(f.writes[2].path,'notes/split1:'+payload[gi].entries[1].edition_id);
 g.select.value='0';g.select.fire('change');g.select.value='1';g.select.fire('change');await delay(100);assert.equal(g.dataset.verdict,'KEEP');assert.equal(f.writes.length,3,'switching back preserves independent state without writes');
 const reload=await fixture(f.seed);await delay(1050);assert.equal(reload.writes.length,0);assert.equal(reload.cards[0].querySelector('.note').value,'edited once');
 // Edits made before DB connection survive hydration and write only the edited edition.
 const early=await fixture({[path]:{note:'old database note',verdict:'DROP'}},160);const en=early.cards[0].querySelector('.note');en.value='early edit';en.fire('input');await delay(1200);assert.equal(en.value,'early edit');assert.equal(early.writes.length,1);assert.equal(early.writes[0].doc.note,'early edit');assert.equal(early.writes[0].doc.verdict,'DROP');
 console.log('Runtime: no load/focus/blur/selector writes; one edition per action; debounce, hydration, reload, early edits, stable notes IDs passed.');
})().catch(e=>{console.error(e);process.exitCode=1});
