// Exercise shipped JS offline: real events, delayed reads/writes and fake timers.
const assert = require('node:assert/strict'), fs = require('node:fs'), vm = require('node:vm');
const code = fs.readFileSync(process.argv[2], 'utf8');
const classes = () => {
  const names = new Set();
  return {add(n) { names.add(n); }, remove(n) { names.delete(n); }, contains(n) { return names.has(n); },
    toggle(n, force) { const on = force === undefined ? !names.has(n) : force; if (on) names.add(n); else names.delete(n); return on; }};
};
function element(extra = {}) {
  return {events: {}, classList: classes(), style: {}, setAttribute() {},
    addEventListener(k, f) { (this.events[k] ??= []).push(f); },
    fire(k, event = {}) { this.events[k]?.forEach(f => f(event)); }, ...extra};
}
async function settle() { for (let i = 0; i < 30; i++) await Promise.resolve(); }
function boot() {
  const timers = new Map(), writes = [], reads = [], pendingWrites = [];
  let timerId = 0, resolveDb;
  const document = element({body: element({appendChild() {}}), createElement: () => element()});
  const cards = [0, 1].map(i => {
    const note = element({value: 'live note', textContent: 'STALE HTML', defaultValue: 'STALE HTML',
      matches: () => true, focus() { document.activeElement = this; card.fire('focusin'); }, blur() { this.fire('blur'); }});
    const printed = element({value: 'live printed', defaultValue: 'STALE PREFILL', matches: () => true});
    const badge = element();
    const box = element({dataset: {id: 'line' + i + ':s4', line: 'line' + i, slot: '4'},
      querySelector(s) { return {'.note': note, '.printed': printed, '.status': {}}[s]; }});
    const lens = element({hidden: true, offsetWidth: 300, offsetHeight: 130, style: {backgroundImage: 'url(clean.png)'}});
    const img = element({src: 'marked.png', getBoundingClientRect() { return {left: 0, top: 0, bottom: 100, width: 600, height: 100}; }});
    const ov = element({dataset: {w: '600', dw: '600'}, querySelector() { return null; }});
    const wrapper = {querySelector(s) { return s === 'img' ? img : lens; }};
    const card = element({dataset: {}, scrollIntoView() {},
      querySelector(s) { return {'.notes[data-line]': box, '.note': note, '.verdict': badge, '.ov': ov, '.lens': lens}[s]; },
      note, printed, badge, box, lens, img, ov, wrapper});
    return card;
  });
  document.querySelectorAll = s => s === '.card' ? cards : s === '.zw' ? cards.map(c => c.wrapper) : cards.map(c => c.lens);
  const db = {doc(path) { return {get() { return new Promise(resolve => reads.push({path, resolve})); },
    set(value, opts) { writes.push({path, value, opts}); return new Promise(resolve => pendingWrites.push(resolve)); }}; }};
  vm.runInNewContext(code, {window: {innerWidth: 1200, innerHeight: 800, claude: {use: () => new Promise(r => resolveDb = r)}},
    document, Date, Promise, JSON, Set, Map,
    setTimeout(fn, ms) { assert.ok(ms === 900 || ms === 300); timers.set(++timerId, fn); return timerId; },
    clearTimeout(id) { timers.delete(id); }});
  return {cards, document, writes, timers, reads, pendingWrites,
    async connect() { resolveDb(db); await settle(); },
    async hydrate(data) { reads.forEach(r => r.resolve({exists: data !== null, data: () => data})); await settle(); },
    async tick() { const callbacks = [...timers.values()]; timers.clear(); callbacks.forEach(f => f()); await settle(); },
    key(key, target = {matches: () => false}) { document.fire('keydown', {key, target, preventDefault() {}}); }};
}
(async () => {
  for (const saved of [null, {note: 'stored', verdict: 'DROP', printed: 'stored printed', updated: '2026-10-19 10:20'}]) {
    const h = boot(); await h.connect(); await h.hydrate(saved);
    h.cards.forEach(c => c.note.blur()); await h.tick();
    assert.equal(h.writes.length, 0, 'load, hydration, focus and blur MUST NEVER write');
    if (saved) {
      assert.equal(h.cards[0].note.value, 'stored'); assert.equal(h.cards[0].printed.value, 'stored printed');
      assert.equal(h.cards[0].dataset.verdict, 'DROP');
    }
  }
  const h = boot(), [c, second] = h.cards;
  // Capture genuine input before the connection resolves, without a load write.
  c.note.value = 'first'; c.note.fire('input');
  await h.connect(); await h.tick(); assert.equal(h.writes.length, 0, 'wait for the saved document before merging');
  await h.hydrate({note: 'old', printed: 'stored truth', verdict: 'DROP'});
  assert.equal(c.note.value, 'first'); assert.equal(c.printed.value, 'stored truth'); assert.equal(c.dataset.verdict, 'DROP');
  c.badge.fire('click', {stopPropagation() {}}); // DROP -> KEEP, preserve the loaded note/Printed.
  await h.tick(); assert.equal(h.writes.length, 1);
  assert.equal(h.writes[0].value.note, 'first'); assert.equal(h.writes[0].value.verdict, 'KEEP');
  assert.equal(h.writes[0].value.printed, 'stored truth'); assert.equal(h.writes[0].value.line_id, 'line0');
  assert.equal(h.writes[0].path, 'notes/line0:s4'); assert.deepEqual({...h.writes[0].opts}, {merge: true});
  assert.match(h.writes[0].value.updated, /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/);
  assert.equal(h.writes[0].value.updated, new Date().toLocaleString('sv-SE', {timeZone: 'Europe/Athens'}).slice(0, 16));
  // An in-flight write snapshots its fields; blur queues the newest edit.
  c.note.value = 'second'; c.printed.value = 'fixed'; c.note.fire('input'); c.printed.fire('input'); c.printed.fire('blur');
  h.pendingWrites.shift()(); await settle(); assert.equal(h.writes.length, 2);
  assert.equal(h.writes[1].value.note, 'second'); assert.equal(h.writes[1].value.printed, 'fixed');
  assert.equal(h.writes[1].value.printed_edited, true); assert.equal(h.writes[1].value.slot, '4');
  h.pendingWrites.shift()(); await settle();
  // Arrow keys navigate from within notes and transfer focus; nonempty notes keep spaces.
  h.key('ArrowDown', c.note); assert.equal(h.document.activeElement, second.note);
  const previous = second.dataset.verdict; h.key(' ', second.note); assert.equal(second.dataset.verdict, previous);
  second.note.value = ''; second.note.fire('input'); h.key(' ', second.note); assert.equal(second.dataset.verdict, 'KEEP');
  h.key(' ', second.note); assert.equal(second.dataset.verdict, 'DROP');
  h.key(' ', second.note); assert.equal(second.dataset.verdict, 'KEEP');
  h.key('ArrowUp', second.note); assert.equal(h.document.activeElement, c.note);
  h.key('b'); assert.equal(h.document.body.classList.contains('noboxes'), true);
  h.key('z'); assert.equal(c.ov.style.width, '1800px'); h.key('z'); assert.equal(c.ov.style.width, '600px');
  // Hover and tap use the caller's clean raster at 3x, with no lens-source overwrite.
  c.img.fire('pointermove', {clientX: 100, clientY: 20, pointerType: 'mouse'});
  assert.equal(c.lens.hidden, false); assert.equal(c.lens.style.backgroundImage, 'url(clean.png)');
  assert.equal(c.lens.style.backgroundSize, '1800px 300px');
  c.img.fire('click', {clientX: 100, clientY: 20, pointerType: 'touch'}); assert.equal(c.lens.hidden, true);
  c.img.fire('click', {clientX: 100, clientY: 20, pointerType: 'touch'}); assert.equal(c.lens.hidden, false);
  console.log('owner runtime: no load writes (missing/existing docs, live values), early edits, unified saves, load/write races, keys, Printed and clean lens pass');
})().catch(error => { console.error(error); process.exitCode = 1; });
