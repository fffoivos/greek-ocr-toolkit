(function () {
  const manifest = JSON.parse(document.getElementById('manifest').textContent);
  const reader = new URLSearchParams(location.search).get('reader') === '2' ? 2 : 1;
  const cards = reader === 2 ? [...manifest].reverse() : manifest;
  const storage = 'adjudicate-v1:' + document.body.dataset.deck + ':' + reader;
  const answers = JSON.parse(localStorage.getItem(storage) || '{}');
  const save = () => localStorage.setItem(storage, JSON.stringify(answers));
  document.getElementById('assignment').textContent = 'Reader ' + reader;
  for (const card of cards) {
    const article = document.createElement('article');
    const heading = document.createElement('h2'); heading.textContent = card.id; article.append(heading);
    for (const field of (card.mark_img ? ['line_img','img','mark_img'] : ['img','line_img'])) {
      const image = document.createElement('img'); image.src = card[field];
      image.alt = field === 'mark_img' ? 'Letter 8×' : field === 'img' ? 'Target crop' : 'Full line'; article.append(image);
    }
    const answer = answers[card.id] || {id:card.id,answer:'',printed:null,confidence:'medium',note:''};
    const choices = document.createElement('select');
    const options = card.options || Object.fromEntries(['A','B','C'].filter(k => k in card).map(k => [k,card[k]]));
    for (const [value,text] of [['','Choose'],...Object.entries(options),['literal','none of these'],['unreadable','unreadable']]) {
      const option = document.createElement('option'); option.value=value; option.textContent=value in options ? value+': '+text : text; choices.append(option);
    }
    choices.value=answer.answer;
    const printed=document.createElement('input'); printed.placeholder='Complete literal transcription'; printed.value=answer.printed || '';
    const confidence=document.createElement('select');
    for (const text of ['high','medium','low']) {const option=document.createElement('option');option.value=text;option.textContent=text;confidence.append(option);}
    confidence.value=answer.confidence;
    const note=document.createElement('textarea');note.placeholder='Note';note.value=answer.note;
    function update() { answers[card.id]={id:card.id,answer:choices.value,printed:choices.value==='literal'?printed.value:null,confidence:confidence.value,note:note.value};save(); }
    for (const [name,input] of [['Answer',choices],['Printed',printed],['Confidence',confidence],['Note',note]]) {
      const label=document.createElement('label');label.append(document.createTextNode(name+' '),input);article.append(label);input.addEventListener('input',update);
    }
    document.getElementById('cards').append(article);
  }
  document.getElementById('export').addEventListener('click', () => {
    const rows=cards.map(c=>answers[c.id] || {id:c.id,answer:'',printed:null,confidence:'medium',note:''});
    const link=document.createElement('a');const url=URL.createObjectURL(new Blob([JSON.stringify(rows,null,2)],{type:'application/json'}));
    link.href=url;link.download='reader_'+reader+'.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
})();
