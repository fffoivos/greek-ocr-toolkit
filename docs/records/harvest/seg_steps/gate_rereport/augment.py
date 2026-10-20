"""Exhaustive script-only coordinator comparison and evidence-based book flag review."""
import analyze as a
import gzip,json,unicodedata as ud
from collections import Counter,defaultdict
O=a.OUT
s=json.loads((O/'summary.json').read_text())
coord=json.loads(a.track('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/db202b49-34e2-49d2-9fbd-271fe776b56d/scratchpad/foreign_mixed_ids.json').read_text())
cs={k:set(v) for k,v in coord.items()};flag={r['id']:r for r in map(json.loads,(O/'unexpected_scripts_rows.jsonl').read_text().splitlines())}
diffs=[];seen=set();presence=defaultdict(lambda:dict(rows=0,books=set()));raw_book=defaultdict(set);np=0
with gzip.open(a.BASE/'cells/population_cells.jsonl.gz','rt') as f:
 for l in f:
  r=json.loads(l);rid=r['row_id'];seen.add(rid);text=r['raw_text'];iv=a.inventory(text,a.CODEC)
  kind='mixed' if iv['mixed_words'] else 'foreign' if rid in flag else None
  # Ordinals alone are separately displayed in the codec table but still obey the actual gate.
  if kind is None and any(c in text for c in 'ºªµ'):
   row=dict(r,id=rid,book_id=rid.split('--')[1] if '--' in rid else rid.rsplit('-l',1)[0],page_id=rid.rsplit('-l',1)[0],crop_bbox=[0,0,r['width_px'],r['height_px']]);ex=a.expectations(row,{})
   g=a.content_gate_exclusion(text,iv,ex,a.CODEC,row,{})
   if g and g[1][0]['reason']=='unexpected_script':kind='foreign'
  c='mixed' if rid in cs['mixed'] else 'foreign' if rid in cs['foreign'] else None
  if c!=kind:
   row=dict(r,id=rid,book_id=rid.split('--')[1] if '--' in rid else rid.rsplit('-l',1)[0],page_id=rid.rsplit('-l',1)[0],crop_bbox=[0,0,r['width_px'],r['height_px']]);ex=a.expectations(row,{});gate=a.content_gate_exclusion(text,iv,ex,a.CODEC,row,{})
   reason='Pipeline source policy rejects stand-alone Latin in Cyrillic source' if kind=='foreign' and iv['scripts'].get('latin') and not iv['scripts'].get('other') and not iv['scripts'].get('greek') else 'Pipeline source/class expected scripts differ from generic Unicode baseline' if kind=='foreign' else 'Pipeline codec letter classification / adm.words tokenization / mixed-before-foreign precedence'
   diffs.append(dict(id=rid,coordinator=c,pipeline=kind,text=text,reason=reason,words=iv['mixed_words'],scripts=iv['scripts'],expected=ex,gate=gate))
  book=rid.split('--')[1] if '--' in rid else None
  for script in {a.named_script(c) for c in text if a.codec_letter_script(c,a.CODEC) and c not in 'ºªµ'}:
   key=(r['source'],script);presence[key]['rows']+=1;presence[key]['books'].add(book)
  np+=1
  if np%200000==0:print('COMPARE',np,flush=True)
a.write('coordinator_census_disagreements.jsonl',diffs)
a.dump('raw_script_presence.json',[dict(source=k[0],script=k[1],rows=v['rows'],books=len(v['books'])) for k,v in sorted(presence.items())])
finite=list(map(json.loads,(O/'coordinator_disagreements.jsonl').read_text().splitlines()))
s['coordinator_census_disagreements']=len(diffs);s['coordinator_all_unique_disagreements']=len({r['id'] for r in diffs+finite});s['coordinator_ids_outside_census']=sorted((cs['foreign']|cs['mixed'])-seen)
# Review raw-text examples, rather than treating repeated short tokens as language proof.
gs=list(map(json.loads,(O/'unexpected_scripts_by_book.jsonl').read_text().splitlines()))
real_hebrew={('ia_poly1850','5aa15e93b2f445b8'),('ia_poly1850','ebcfd6056abfa776'),('ia_poly1850','09f9190274fc82bd'),('ia_poly1850','41e90f3ba967f920')}
for g in gs:
 src,b,sc=g['source'],g['book'],g['script']
 if (src,b) in real_hebrew and sc=='HEBREW' or src=='ia_greek_latin' and sc=='HEBREW':
  g.update(classification='a',borderline=False,rationale='Raw scholarly apparatus/quotation context supports legitimate Hebrew, including Aleph manuscript sigla. Single letter does not imply confusion; mixed-word DROP still takes precedence.')
 elif src=='ia_poly1850' and b=='26e14cb9c90b750f' and sc=='CJK':
  g.update(classification='a',borderline=False,rationale='232 rows, many long CJK-only sequences: strong real Chinese-content evidence; mixed row still DROP.')
 elif src=='ia_poly1850' and b=='174d84a441d69a70' and sc in ('SYRIAC','ARABIC'):
  g.update(classification='a',borderline=(sc=='ARABIC'),rationale='Syriac words and explicit Biblical/grammar context; Arabic forms occur beside English glosses too. Script identity in Arabic-like OCR forms is borderline without pixels.')
 elif sc in ('ARABIC','HEBREW','CJK') and g['classification']=='a':
  g.update(classification='c',borderline=True,rationale='Repeated short tokens/fragmentary OCR; count or whole-token status alone does not establish real language. Raw examples are compatible with ditto marks, rules or damaged glyphs; pixels unverified.')
 elif sc in ('greek','latin','cyrillic'):
  if g['mixed_word_rows']>=.5*g['rows']:
   g.update(classification='b',rationale='Predominantly letters inside mixed-script words. DROP is the mixed-word rule; actual intended glyphs are not verified from pixels.',borderline=g['rows']<3)
  else:
   g.update(classification='a' if sc=='latin' and src in ('serbia','ia_russian') else 'b',borderline=True,rationale='Stand-alone script words or short tokens, not predominantly mixed-word confusion. Latin bibliographic content is plausible; book expectation needs review, no change made.' if sc=='latin' else 'Whole or short tokens occur; script confusion versus real other-language text is unresolved from raw OCR alone.')
a.write('unexpected_scripts_by_book.jsonl',gs)
s['census']['class_counts']=dict(Counter(g['classification'] for g in gs));s['census']['borderline_entries']=sum(g['borderline'] for g in gs)
a.dump('summary.json',s)
print('COMPARE COMPLETE',len(diffs),s['coordinator_all_unique_disagreements'],flush=True)
