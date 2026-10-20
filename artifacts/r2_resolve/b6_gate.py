import subprocess,json
from pathlib import Path
py='/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python'
src=Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad')
for t in ['T2','T4']:
 for r in ['r1','r2']:
  for i in range(8):
   p=src/f'r2read_{t}_{r}'/f'b{i:02}'
   out=Path('artifacts/r2_resolve')/t/'batch_gates'/r/f'b{i:02}'
   subprocess.run([py,'scripts/labelfix/r2_cards_resolve.py','--dry-run','--deck',f'docs/labelfix/spellcheck/R2/decks/{t}','--reader1',str(p/'answers.jsonl'),'--manifest',str(p/'cards.jsonl'),'--out',str(out)],check=True)
   g=json.loads((out/'validation_receipt.json').read_text())
   print(t,r,i,'PASS' if g['accepted'] else 'FAIL','controls',g['controls'],'errors',g['control_errors'],'invalid',g['invalid_answer_count'],flush=True)
