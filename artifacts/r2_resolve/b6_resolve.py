import sys,json,collections
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from scripts.labelfix import r2_cards_resolve as R
src=Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad')
for t in ['T2','T4']:
 out=Path('artifacts/r2_resolve')/t;deck=Path('docs/labelfix/spellcheck/R2/decks')/t
 cards=R.read(deck/'blind/cards.jsonl'); order=[c['card_id'] for c in cards]
 for r in ['r1','r2']:
  aa=[a for i in range(8) for a in R.read(src/f'r2read_{t}_{r}'/f'b{i:02}'/'answers.jsonl')]
  assert len(aa)==len(set(a['card_id'] for a in aa))==880
  byid={a['card_id']:a for a in aa}; assert set(byid)==set(order)
  R.write(out/'inputs'/f'{r}.jsonl',[byid[i] for i in (order if r=='r1' else order[::-1])])
 R.run(deck,out/'inputs/r1.jsonl',out/'inputs/r2.jsonl',out)
 print(t,json.loads((out/'resolution_receipt.json').read_text()))
