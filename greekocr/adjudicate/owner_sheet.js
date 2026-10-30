(async function () {
  const cards = [...document.querySelectorAll('.card')];
  const boxes = cards.map(card => card.querySelector('.notes[data-line]'));
  const status = (el, text, ok) => {
    el.querySelector('.status').textContent = text;
    el.classList.toggle('saved', !!ok);
  };
  const value = (card, el) => JSON.stringify([
    el.querySelector('.note').value, card.dataset.verdict || '',
    el.querySelector('.printed')?.value ?? null
  ]);
  // No-write-on-load: snapshot LIVE value fields, never textContent/defaultValue.
  // Only input or mark events set edited; hydration, focus and blur cannot do so.
  const initial = new Map(cards.map((card, i) => [boxes[i], value(card, boxes[i])]));
  const tally = document.createElement('div');
  tally.id = 'tally'; tally.setAttribute('aria-live', 'polite'); document.body.appendChild(tally);
  function count() {
    let keep = 0, drop = 0;
    cards.forEach(card => { if (card.dataset.verdict === 'KEEP') keep++; else if (card.dataset.verdict === 'DROP') drop++; });
    tally.innerHTML = '<b class="k">' + keep + ' KEEP</b> · <b class="d">' + drop + ' DROP</b> · ' +
      (cards.length - keep - drop) + ' unmarked · ↑↓ move · space marks · b boxes · z zoom · d details';
  }
  function show(card, verdict) {
    card.dataset.verdict = verdict || '';
    const badge = card.querySelector('.verdict');
    badge.textContent = verdict === 'KEEP' ? '✓ KEEP' : verdict === 'DROP' ? '✗ DROP' : '–';
    badge.className = 'verdict ' + (verdict || '');
    badge.setAttribute('aria-label', 'Owner mark: ' + (verdict || 'unmarked'));
    card.classList.toggle('vkeep', verdict === 'KEEP');
    card.classList.toggle('vdrop', verdict === 'DROP');
    count();
  }
  let db = null, cur = -1;
  function select(index, focus = false, scroll = true) {
    if (index < 0 || index >= cards.length) return;
    if (cur >= 0) cards[cur].classList.remove('cur');
    cur = index; cards[cur].classList.add('cur');
    if (focus) cards[cur].querySelector('.note').focus({preventScroll: true});
    // Card top at the top of the screen: the crop is seen first and the note stays reachable.
    if (scroll) cards[cur].scrollIntoView({block: 'start', behavior: 'instant'});
  }
  const states = cards.map((card, i) => {
    const el = boxes[i], note = el.querySelector('.note'), printed = el.querySelector('.printed');
    const state = {card, el, note, printed, last: initial.get(el), edited: false, dirty: new Set(), ready: false,
      timer: null, busy: false, again: false};
    async function flush() {
      // Absolute guard: no action means no write, including after a load or blur.
      if (!state.edited || !state.ready || !db) return;
      if (state.busy) { state.again = true; return; }
      const snapshot = value(card, el);
      if (snapshot === state.last) return;
      state.busy = true;
      status(el, 'saving…', false);
      const doc = {note: note.value, verdict: card.dataset.verdict || '',
        updated: new Date().toLocaleString('sv-SE', {timeZone: 'Europe/Athens'}).slice(0, 16), line_id: el.dataset.line};
      if (printed) {
        doc.printed = printed.value;
        doc.printed_edited = printed.value !== printed.defaultValue;
      }
      if (el.dataset.slot !== undefined) doc.slot = el.dataset.slot;
      try {
        await db.doc('notes/' + (el.dataset.id || el.dataset.line)).set(doc, {merge: true});
        state.last = snapshot;
        status(el, 'saved ' + doc.updated, true);
      } catch (_) { status(el, 'not saved, keep going to retry', false); }
      state.busy = false;
      if (state.again) { state.again = false; await flush(); }
    }
    state.schedule = (delay = 900) => { clearTimeout(state.timer); state.timer = setTimeout(flush, delay); };
    state.edit = (field, delay = 900) => {
      state.edited = true; state.dirty.add(field);
      status(el, db ? 'editing…' : 'editing (waiting for signed-in database)…', false);
      state.schedule(delay);
    };
    [note, printed].filter(Boolean).forEach(input => {
      input.addEventListener('input', () => state.edit(input === note ? 'note' : 'printed'));
      input.addEventListener('blur', () => { clearTimeout(state.timer); flush(); });
    });
    card.querySelector('.verdict').addEventListener('click', event => {
      event.stopPropagation(); select(i, false, false); cycle(i);
    });
    card.addEventListener('click', () => select(i, false, false));
    card.addEventListener('focusin', () => { if (cur !== i) select(i, false, false); });
    return state;
  });
  function cycle(index) {
    const state = states[index];
    if (!state) return;
    show(state.card, state.card.dataset.verdict === 'KEEP' ? 'DROP' : 'KEEP');
    state.edit('verdict', 300);
  }
  document.addEventListener('keydown', event => {
    if (event.ctrlKey || event.metaKey || event.altKey || event.isComposing) return;
    const inText = event.target.matches?.('textarea,input');
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault();
      select(cur < 0 ? 0 : cur + (event.key === 'ArrowDown' ? 1 : -1), true);
    } else if (event.key === ' ') {
      if (inText && event.target.value !== '') return;
      event.preventDefault(); if (cur < 0) select(0); cycle(cur);
    } else if (event.key === 'Escape' && inText) {
      event.target.blur();
    } else if (event.key.toLowerCase() === 'd' && !inText) {
      if (cur < 0) select(0);
      cards[cur].classList.toggle('open');
    } else if (event.key.toLowerCase() === 'b' && !inText) {
      document.body.classList.toggle('noboxes');
    } else if (event.key.toLowerCase() === 'z' && !inText) {
      if (cur < 0) select(0);
      const ov = cards[cur]?.querySelector('.ov');
      if (!ov) return;
      const big = ov.classList.toggle('big');
      ov.style.width = (big ? Math.round(Number(ov.dataset.w) * 3) : ov.dataset.dw) + 'px';
      cards[cur].querySelector('.lens').hidden = true;
    }
  }, true);
  // Sheets built before the tall layout: detect a vertical crop from the overlay's viewBox and re-size it.
  cards.forEach(card => {
    const ov = card.querySelector('.ov');
    if (!ov || card.classList.contains('tall')) return;
    const vb = (ov.querySelector('svg')?.getAttribute('viewBox') || '').split(/\s+/).map(Number);
    const w = Number(ov.dataset.w), h = vb.length === 4 ? vb[3] : 0;
    if (!(h > w)) return;
    card.classList.add('tall');
    const dw = Math.max(1, Math.round(w * Math.min(3, 940 / w, 640 / h)));
    ov.style.width = dw + 'px'; ov.dataset.dw = dw;
  });
  cards.forEach((card, i) => card.querySelector('table.w')?.addEventListener('click', () => {
    select(i, false, false); card.classList.toggle('open');
  }));
  count();
  // Listeners are installed before awaiting the connection: early edits survive.
  try { db = await (window.claude?.use ? window.claude.use('db') : null); } catch (_) {}
  if (!db) {
    boxes.forEach(el => status(el, 'marks, notes and Printed save in the signed-in view', false));
    return;
  }
  // Each card reads its own document; no collection limit silently drops notes.
  await Promise.all(states.map(async state => {
    const {card, el, note, printed} = state;
    try {
      const snapshot = await db.doc('notes/' + (el.dataset.id || el.dataset.line)).get();
      if (snapshot.exists) {
        const data = snapshot.data() || {};
        const baseline = JSON.parse(initial.get(el));
        if (typeof data.note === 'string') baseline[0] = data.note;
        if (data.verdict === 'KEEP' || data.verdict === 'DROP' || data.verdict === '') baseline[1] = data.verdict;
        if (printed && typeof data.printed === 'string') baseline[2] = data.printed;
        if (!state.dirty.has('note')) note.value = baseline[0];
        if (!state.dirty.has('verdict')) show(card, baseline[1]);
        if (printed && !state.dirty.has('printed')) printed.value = baseline[2];
        state.last = JSON.stringify(baseline);
        if (!state.edited) status(el, 'saved ' + (data.updated || ''), true);
      }
    } catch (_) { if (!state.edited) status(el, 'could not load notes', false); }
    state.ready = true;
    if (state.edited) state.schedule();
  }));
})();
(function () {
  const Z = 3;
  document.querySelectorAll('.zw').forEach(wrapper => {
    const img = wrapper.querySelector('img,svg.sprite'), lens = wrapper.querySelector('.lens');
    const sprite = img.matches('svg.sprite');
    // A caller-supplied clean raster must remain the magnifier source.
    if (!lens.style.backgroundImage) lens.style.backgroundImage = 'url(' + (sprite ? img.dataset.src : img.src) + ')';
    function show(event) {
      const rect = img.getBoundingClientRect(), x = event.clientX - rect.left, y = event.clientY - rect.top;
      if (x < 0 || y < 0 || x > rect.width || y > rect.height) { lens.hidden = true; return; }
      lens.hidden = false;
      const width = lens.offsetWidth, height = lens.offsetHeight;
      lens.style.left = Math.max(8, Math.min(window.innerWidth - width - 8, event.clientX - width / 2)) + 'px';
      lens.style.top = (rect.top >= height + 12 ? rect.top - height - 12 :
        Math.max(8, Math.min(window.innerHeight - height - 8, rect.bottom + 12))) + 'px';
      const factor = sprite ? rect.width / Number(img.closest('.ov').dataset.w) : 1;
      lens.style.backgroundSize = (sprite ? Number(img.dataset.sw) * factor : rect.width) * Z + 'px ' +
        (sprite ? Number(img.dataset.sh) * factor : rect.height) * Z + 'px';
      lens.style.backgroundPosition = (width / 2 - (x + (sprite ? Number(img.dataset.x) * factor : 0)) * Z) + 'px ' +
        (height / 2 - (y + (sprite ? Number(img.dataset.y) * factor : 0)) * Z) + 'px';
    }
    img.addEventListener('pointermove', event => { if (event.pointerType !== 'touch') show(event); });
    img.addEventListener('pointerleave', event => { if (event.pointerType !== 'touch') lens.hidden = true; });
    img.addEventListener('click', event => { if (lens.hidden) show(event); else lens.hidden = true; });
  });
  document.addEventListener('click', event => {
    if (!event.target.closest('.zw')) document.querySelectorAll('.lens').forEach(lens => lens.hidden = true);
  });
})();
