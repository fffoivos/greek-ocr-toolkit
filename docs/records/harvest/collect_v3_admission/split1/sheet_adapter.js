// Edition adapter of owner_sheet.js: same actions, frames, clock and notes schema.
// Gazette groups have one visible card but independent states and DB IDs per issue.
(async function () {
 const cards=[...document.querySelectorAll('.card')];let db=null,cur=-1;
 const tally=document.createElement('div');tally.id='tally';document.body.appendChild(tally);
 const states=SPLIT1_CARDS.map((c,i)=>({card:cards[i],active:0,entries:c.entries.map(e=>({...e,note:'',verdict:'',last:JSON.stringify(['','']),edited:false,dirty:new Set(),ready:false,busy:false,timer:null,again:false}))}));
 const all=states.flatMap(c=>c.entries);
 function count(){let k=0,d=0;all.forEach(e=>{if(e.verdict==='KEEP')k++;if(e.verdict==='DROP')d++});tally.innerHTML=`<b class="k">${k} KEEP</b> · <b class="d">${d} DROP</b> · ${all.length-k-d} unmarked editions · ↑↓ · space · z · b`;}
 function status(c,e,msg){e.status=msg;if(c.entries[c.active]===e)c.card.querySelector('.status').textContent=msg;}
 function show(c){
  const e=c.entries[c.active],card=c.card,b=card.querySelector('.verdict'),n=card.querySelector('.note'),box=card.querySelector('.notes');
  card.dataset.verdict=e.verdict;card.dataset.tool=e.split.toUpperCase();card.classList.toggle('vkeep',e.verdict==='KEEP');card.classList.toggle('vdrop',e.verdict==='DROP');
  b.textContent=e.verdict==='KEEP'?'✓ KEEP':e.verdict==='DROP'?'✗ DROP':'–';b.className='verdict '+e.verdict;b.setAttribute('aria-label','Owner mark: '+(e.verdict||'unmarked'));
  const pill=card.querySelector('.toolpill');pill.className='toolpill '+e.split.toUpperCase();pill.textContent='tool: '+e.split.toUpperCase();
  card.querySelector('.lock-label').textContent=e.forced?'🔒 forced by v2 — side locked':'';
  box.dataset.line=e.edition_id;box.dataset.id='split1:'+e.edition_id;n.value=e.note;n.id='n-split1:'+e.edition_id;box.querySelector('label').htmlFor=n.id;
  card.querySelector('.active-edition').textContent='Active edition '+e.edition_id+' · '+e.documents.join(', ');
  const cells=card.querySelectorAll('.edition-metadata td');[e.title,e.source+' / '+e.year,JSON.stringify(e.classes),e.reason].forEach((x,i)=>{cells[i].textContent=x});
  card.querySelector('.status').textContent=e.status||'unpublished local sheet — save requires signed-in artifact database';count();
 }
 function select(i,focus=false,scroll=true){if(i<0||i>=cards.length)return;if(cur>=0)cards[cur].classList.remove('cur');cur=i;cards[i].classList.add('cur');if(focus)cards[i].querySelector('.note').focus({preventScroll:true});if(scroll)cards[i].scrollIntoView({block:'center',behavior:'instant'});}
 async function flush(c,e){
  // Absolute no-write-on-load: only real input/mark events set edited.
  if(!e.edited||!e.ready||!db)return;
  if(e.busy){e.again=true;return}const snapshot=JSON.stringify([e.note,e.verdict]);if(snapshot===e.last)return;
  e.busy=true;status(c,e,'saving…');
  const doc={note:e.note,verdict:e.verdict,updated:new Date().toLocaleString('sv-SE',{timeZone:'Europe/Athens'}).slice(0,16),line_id:e.edition_id};
  try{await db.doc('notes/split1:'+e.edition_id).set(doc,{merge:true});e.last=snapshot;status(c,e,'saved '+doc.updated)}catch(_){status(c,e,'not saved; edit to retry')}
  e.busy=false;if(e.again){e.again=false;await flush(c,e)}
 }
 function edit(c,e,field,delay=900){e.edited=true;e.dirty.add(field);status(c,e,db?'editing…':'editing (waiting for signed-in database)…');clearTimeout(e.timer);e.timer=setTimeout(()=>flush(c,e),delay)}
 function cycle(c){const e=c.entries[c.active];e.verdict=e.verdict==='KEEP'?'DROP':'KEEP';show(c);edit(c,e,'verdict',300)}
 states.forEach((c,i)=>{
  const note=c.card.querySelector('.note');show(c);
  note.addEventListener('input',()=>{const e=c.entries[c.active];e.note=note.value;edit(c,e,'note')});
  note.addEventListener('blur',()=>{const e=c.entries[c.active];clearTimeout(e.timer);flush(c,e)});
  c.card.querySelector('.verdict').addEventListener('click',ev=>{ev.stopPropagation();select(i,false,false);cycle(c)});
  c.card.addEventListener('click',()=>select(i,false,false));c.card.addEventListener('focusin',()=>{if(cur!==i)select(i,false,false)});
  c.card.querySelector('.issue-select')?.addEventListener('change',ev=>{const old=c.entries[c.active];clearTimeout(old.timer);flush(c,old);c.active=Number(ev.target.value);show(c)});
 });
 document.addEventListener('keydown',ev=>{
  if(ev.ctrlKey||ev.metaKey||ev.altKey||ev.isComposing)return;
  const inText=ev.target.matches?.('textarea,input');if(ev.target.matches?.('select'))return;
  if(ev.key==='ArrowDown'||ev.key==='ArrowUp'){ev.preventDefault();select(cur<0?0:cur+(ev.key==='ArrowDown'?1:-1),true)}
  else if(ev.key===' '){if(inText&&ev.target.value!=='')return;ev.preventDefault();if(cur<0)select(0);cycle(states[cur])}
  else if(ev.key==='Escape'&&inText)ev.target.blur();
  else if(ev.key.toLowerCase()==='b'&&!inText)document.body.classList.toggle('noboxes');
  else if(ev.key.toLowerCase()==='z'&&!inText){if(cur<0)select(0);cards[cur].querySelectorAll('.ov').forEach(ov=>{const big=ov.classList.toggle('big');ov.style.width=(big?Math.round(Number(ov.dataset.w)*3):ov.dataset.dw)+'px'});cards[cur].querySelectorAll('.lens').forEach(x=>x.hidden=true)}
 },true);
 count();
 // Listeners precede connection/hydration so early edits are never overwritten.
 try{db=await(window.claude?.use?window.claude.use('db'):null)}catch(_){}
 if(!db)return;
 await Promise.all(states.flatMap(c=>c.entries.map(async e=>{
  try{const snap=await db.doc('notes/split1:'+e.edition_id).get();if(snap.exists){const data=snap.data()||{};let note=typeof data.note==='string'?data.note:'',verdict=['KEEP','DROP',''].includes(data.verdict)?data.verdict:'';if(!e.dirty.has('note'))e.note=note;if(!e.dirty.has('verdict'))e.verdict=verdict;e.last=JSON.stringify([note,verdict]);if(!e.edited)e.status='saved '+(data.updated||'')}}catch(_){e.status='could not load notes'}
  e.ready=true;if(c.entries[c.active]===e)show(c);if(e.edited){clearTimeout(e.timer);e.timer=setTimeout(()=>flush(c,e),900)}
 })));
})();
