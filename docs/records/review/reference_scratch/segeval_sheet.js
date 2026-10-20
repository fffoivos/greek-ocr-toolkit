(async function () {
  const cards = [...document.querySelectorAll('.card')];
  const boxes = cards.map(c => c.querySelector('.notes[data-line]'));
  const tally = document.createElement('div'); tally.id = 'tally'; document.body.appendChild(tally);
  const CYCLE = ['', 'KEEP', 'DROP'];
  const savers = new Map();
  function count() {
    let k = 0, d = 0;
    cards.forEach(c => { if (c.dataset.verdict === 'KEEP') k++; else if (c.dataset.verdict === 'DROP') d++; });
    tally.innerHTML = '<b class="k">' + k + ' KEEP</b> · <b class="d">' + d + ' DROP</b> · ' + (cards.length - k - d) + ' unmarked · ↑↓ move · space marks · b boxes';
  }
  function show(c, v) {
    c.dataset.verdict = v || '';
    const b = c.querySelector('.verdict');
    b.textContent = v === 'KEEP' ? '✓ KEEP' : v === 'DROP' ? '✗ DROP' : '–';
    b.className = 'verdict ' + (v || '');
    c.classList.toggle('vkeep', v === 'KEEP'); c.classList.toggle('vdrop', v === 'DROP');
    count();
  }
  function cycle(c) {
    const v = (c.dataset.verdict === 'KEEP') ? 'DROP' : 'KEEP';
    show(c, v);
    const s = savers.get(c); if (s) s(v);
  }
  let cur = -1;
  function select(i, focus) {
    if (i < 0 || i >= cards.length) return;
    if (cur >= 0) cards[cur].classList.remove('cur');
    cur = i; cards[i].classList.add('cur');
    if (focus) { const t = cards[i].querySelector('.note'); if (t) t.focus({preventScroll: true}); }
    cards[i].scrollIntoView({block: 'center', behavior: 'instant'});
  }
  cards.forEach((c, i) => {
    const b = document.createElement('span'); b.className = 'verdict'; b.textContent = '–'; b.title = 'click or press space to toggle KEEP / DROP';
    c.querySelector('.lid').appendChild(b);
    b.addEventListener('click', e => { e.stopPropagation(); select(i, false); cycle(c); });
    c.addEventListener('click', () => { if (cur !== i) { if (cur >= 0) cards[cur].classList.remove('cur'); cur = i; c.classList.add('cur'); } });
    c.addEventListener('focusin', () => { if (cur !== i) { if (cur >= 0) cards[cur].classList.remove('cur'); cur = i; c.classList.add('cur'); } });
  });
  document.addEventListener('keydown', e => {
    const inText = e.target.matches && e.target.matches('textarea,input');
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      select(cur < 0 ? 0 : cur + (e.key === 'ArrowDown' ? 1 : -1), true);
      return;
    }
    if (e.key === ' ') {
      if (inText && e.target.value !== '') return;
      e.preventDefault();
      if (cur < 0) select(0, false);
      cycle(cards[cur]);
      return;
    }
    if (e.key === 'Escape' && inText) { e.target.blur(); return; }
    if ((e.key === 'b' || e.key === 'B') && !inText) { document.body.classList.toggle('noboxes'); }
    if ((e.key === 'z' || e.key === 'Z') && !inText) {
      if (cur < 0) select(0, false);
      const ov = cards[cur].querySelector('.ov'); if (!ov) return;
      const big = ov.classList.toggle('big');
      ov.style.width = (big ? Math.round(ov.dataset.w * 3) : ov.dataset.dw) + 'px';
    }
  }, true);
  count();

  const status = (el, text, ok) => { el.querySelector('.status').textContent = text; el.classList.toggle('saved', !!ok); };
  const initial = new Map(cards.map((c, i) => [boxes[i], JSON.stringify([boxes[i].querySelector('.note').value, c.dataset.verdict || ''])]));
  let db = null;
  try { db = await (window.claude?.use ? window.claude.use('db') : null); } catch (_) {}
  if (!db) {
    boxes.forEach(el => status(el, 'marks and notes save in the signed-in view', false));
    return;
  }
  await Promise.all(cards.map(async (card, i) => {
    const el = boxes[i];
    const id = el.dataset.id || el.dataset.line;
    const note = el.querySelector('.note');
    let timer = null, busy = false, again = false, pendingVerdict = null;
    const value = () => JSON.stringify([note.value, card.dataset.verdict || '']);
    let last = initial.get(el), edited = value() !== last;
    async function flush() {
      if (busy) { again = true; return; }
      const snapshot = value();
      if (snapshot === last) return;
      busy = true;
      status(el, 'saving…', false);
      const doc = {note: note.value, verdict: card.dataset.verdict || '', updated: new Date().toLocaleString('sv-SE', {timeZone: 'Europe/Athens'}).slice(0,16), line_id: el.dataset.line};
      try {
        await db.doc('notes/' + id).set(doc, {merge: true});
        last = snapshot;
        status(el, 'saved ' + doc.updated, true);
      } catch (_) { status(el, 'not saved, keep going to retry', false); }
      busy = false;
      if (again) { again = false; await flush(); }
    }
    savers.set(card, v => { edited = true; status(el, 'saving mark…', false); clearTimeout(timer); timer = setTimeout(flush, 300); });
    note.addEventListener('input', () => { edited = true; status(el, 'editing…', false); clearTimeout(timer); timer = setTimeout(flush, 900); });
    note.addEventListener('blur', () => { clearTimeout(timer); flush(); });
    try {
      const snapshot = await db.doc('notes/' + id).get();
      if (snapshot.exists && !edited) {
        const data = snapshot.data() || {};
        if (typeof data.note === 'string') note.value = data.note;
        if (data.verdict === 'KEEP' || data.verdict === 'DROP') show(card, data.verdict);
        last = value(); status(el, 'saved ' + (data.updated || ''), true);
      }
    } catch (_) { if (!edited) status(el, 'could not load notes', false); }
  }));
})();
(function () {
  const Z = 3;
  document.querySelectorAll('.zw').forEach(wrapper => {
    const img = wrapper.querySelector('img'), lens = wrapper.querySelector('.lens');
    lens.style.backgroundImage = 'url(' + img.src + ')';
    function show(event) {
      const rect = img.getBoundingClientRect(), x = event.clientX - rect.left, y = event.clientY - rect.top;
      if (x < 0 || y < 0 || x > rect.width || y > rect.height) { lens.hidden = true; return; }
      lens.hidden = false;
      const width = lens.offsetWidth, height = lens.offsetHeight;
      lens.style.left = Math.max(0, Math.min(rect.width-width, x-width/2)) + 'px';
      lens.style.top = (y-height-12 < -rect.top ? y+16 : y-height-12) + 'px';
      lens.style.backgroundSize = rect.width*Z + 'px ' + rect.height*Z + 'px';
      lens.style.backgroundPosition = (width/2-x*Z) + 'px ' + (height/2-y*Z) + 'px';
    }
    img.addEventListener('pointermove', event => { if (event.pointerType !== 'touch') show(event); });
    img.addEventListener('pointerleave', event => { if (event.pointerType !== 'touch') lens.hidden = true; });
    img.addEventListener('click', event => { if (lens.hidden) show(event); else lens.hidden = true; });
  });
})();
