"""Review witness diversity and original bound-support claims, saved evidence only."""
import analyze as a
import json
from collections import Counter
O=a.OUT;s=json.loads((O/'summary.json').read_text());flags=[json.loads(l) for l in (O/'unexpected_scripts_rows.jsonl').read_text().splitlines()];gs=[json.loads(l) for l in (O/'unexpected_scripts_by_book.jsonl').read_text().splitlines()]
for g in gs:
 rr=[r for r in flags if r['source']==g['source'] and r['book']==g['book'] and any(a.named_script(c)==g['script'] for c in r['text'])]
 freq=Counter(r['text'] for r in rr);unique={r['text']:r for r in rr}
 ordered=sorted(unique.values(),key=lambda r:(-len(r['text']),r['id'])) if g['classification']=='a' else sorted(unique.values(),key=lambda r:(-freq[r['text']],-len(r['text']),r['id']))
 if g['classification']=='c' and len(ordered)>2:ordered=[ordered[0]]+sorted(ordered[1:],key=lambda r:(-len(r['text']),r['id']))
 g['examples']=[]
 for r in ordered[:3]:
  whole=[w for w in a.adm.words(r['text']) if len([c for c in w if a.named_script(c)==g['script']])>=2 and {a.named_script(c) for c in w if a.codec_letter_script(c,a.CODEC)}=={g['script']}]
  g['examples'].append(dict(id=r['id'],text=r['text'],outcome=r['outcome'],reason=r['reason'],whole_words=whole,mixed_words=r['mixed_words']))
a.write('unexpected_scripts_by_book.jsonl',gs)
bp=[json.loads(l) for l in (a.STEPS/'s5/band_population.jsonl').read_text().splitlines()];ds={r['id']:r for r in map(json.loads,(O/'row_decisions.jsonl').read_text().splitlines())};support={}
for mode in ('before','mixed_foreign','part2_only','all'):
 p=[r for r in bp if mode=='before' or not (ds[r['line_id']]['part1'] if mode=='mixed_foreign' else ds[r['line_id']]['part2'] if mode=='part2_only' else ds[r['line_id']]['kind'])]
 support[mode]={}
 for group in ('overall','numeric'):
  rr=[r for r in p if a.SWEEP.GROUPS[group](r)];opt=s['sweeps'][mode][group]['end_to_end']['proposed'];band=(opt['L'],opt['U'])
  support[mode][group]=dict(neighbours=a.SWEEP.neighbour_moves(rr,band),owner=dict(Counter(r['owner_mark'] for r in rr)),proposed=band)
 short=[r for r in p if r['owner_mark']=='KEEP' and not r['small'] and r['chars']<=10 and not a.SWEEP.in_band(r,.5,1.5)]
 support[mode]['short_owner_keep_outside_small']=dict(n=len(short),original_proposal_kept=sum(a.SWEEP.in_band(r,.3,2) for r in short),ids=[r['line_id'] for r in short])
s['bound_support']=support
# Baseline files are references, not run targets.
receipt=json.loads((O/'receipt.json').read_text())
for step in ('s1','s2','s3','s4'):
 p=a.STEPS/step/'validate_report.py';receipt['input_sha256'][str(p)]=a.sha(p)
receipt['input_sha256'][str(a.STEPS/'s1/inputs.jsonl')]=a.sha(a.STEPS/'s1/inputs.jsonl')
a.dump('summary.json',s);a.dump('receipt.json',receipt)
print('Reviewed witness diversity and bound support',flush=True)
