"""Exact-import edits-only SF7 candidate and uniform blind audit frame."""
import sys,json,collections,unicodedata as ud,hashlib,random
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
sys.path.insert(0,str(BASE));from build_rb7 import rows,sha,dump,RAW,SEL,OUT,PREREG
PART={'psili':'\u0313','dasia':'\u0314','acute':'\u0301','grave':'\u0300','circumflex':'\u0342','diaeresis':'\u0308','dialytika':'\u0308','subscript':'\u0345'}
HEAD={'psili':'breathing','dasia':'breathing','acute':'accent','grave':'accent','circumflex':'accent','diaeresis':'dialytika','dialytika':'dialytika','subscript':'subscript'}
def raw_clusters(text):
 cs=[]
 for i,c in enumerate(text):
  if ud.combining(c) and cs:cs[-1][2]+=c;cs[-1][1]=i+1
  else:cs.append([i,i+1,c])
 return cs

def edits_from_traces(t,variant,policy):
 by=collections.defaultdict(list)
 for e in t.get('marks',[]):by[e['boundary']].append(e)
 result=[]
 for slot,events in sorted(by.items()):
  rm=sorted([e for e in events if e['operation']=='SUBSTITUTE' and e['direction']=='remove'],key=lambda e:e['part']);ad=sorted([e for e in events if e['operation']=='SUBSTITUTE' and e['direction']=='add'],key=lambda e:e['part'])
  paired=[]
  for a in rm:
   b=min(ad,key=lambda e:(HEAD[a['part']]!=HEAD[e['part']],e['part']));ad.remove(b);paired.append((a,b))
  assert not ad
  pairs=paired+[(None,e) for e in events if e['operation']=='ADD']+[(e,None) for e in events if e['operation']=='DELETE']
  for a,b in pairs:
   kind='substitution' if a and b else 'addition' if b else 'deletion';part=(b or a)['part']
   evidence=[e for e in t.get('additions',[]) if b and e['boundary']==slot and e['part']==b['part']]
   evidence += [e for e in t.get('deletions',[]) if a and e.get('letter')==slot and e.get('character')==PART[a['part']]]
   rule='reader_alone_substitution' if kind=='substitution' else 'sf6_unchanged_deletion_guard' if kind=='deletion' else 'A_subscript_owned_below_ink' if variant=='A' and part=='subscript' else 'A_reader_alone' if variant=='A' else 'B_reader_and_detector_or_scored_recogniser'
   result.append(dict(slot=slot,kind=kind,head=HEAD[part],from_part=a['part'] if a else None,to_part=b['part'] if b else None,rule=rule,signals=[e.get('signals',{}) for e in evidence],signal_traces=evidence,variant=variant,policy_digest=policy,source_job='3687228'))
 for q in t.get('quotes',[]):
  assert q['operation']!='HOLD'
  if q['operation']=='CONSUME_ALIAS':
   result.append(dict(slot=q['boundary'],kind='quote_alias_consume',head='quote_alias',rule='SQ1',signals=dict(mark_source_ids=q['mark_source_ids'],quote_source_ids=q['quote_source_ids']),trace=q,variant=variant,policy_digest=policy,source_job='3687228'))
 return result

def convert(r,source):
 text=source['label'];cs=raw_clusters(text);proposal_letters=[c for c in raw_clusters(r['label']) if ud.normalize('NFD',c[2])[0].isalpha()];letters=[c for c in cs if ud.normalize('NFD',c[2])[0].isalpha()];t=r['rule_traces'];replacements={}
 for slot in sorted({e['boundary'] for e in t.get('marks',[])}):
  start,end,raw=letters[slot];value=ud.normalize('NFD',raw)
  for e in t['marks']:
   if e['boundary']==slot and e['direction']=='remove':
    atom=PART[e['part']];assert atom in value,(r['line_id'],e,value);value=value.replace(atom,'',1)
  for e in t['marks']:
   if e['boundary']==slot and e['direction']=='add':
    atom=PART[e['part']];assert atom not in value;value+=atom
  value=ud.normalize('NFD',value)
  proposed=ud.normalize('NFD',proposal_letters[slot][2])
  assert value[0]==proposed[0] and collections.Counter(value[1:])==collections.Counter(proposed[1:])
  value=proposed
  # Touch only the edited grapheme; retain an explicitly decomposed source style.
  value=value if raw!=ud.normalize('NFC',raw) else ud.normalize('NFC',value)
  assert raw!=value;replacements[start]=(end,value,slot)
 for q in t.get('quotes',[]):
  if q['operation']=='CONSUME_ALIAS':
   # Original start is NFD; locate the immediately preposed raw alias by slot.
   target=letters[q['boundary']][0];prev=next(c for c in cs if c[1]==target)
   assert prev[2]==q['alias'];replacements[prev[0]]=(prev[1],'',q['boundary'])
 # Every non-mark deletion must be explicitly accounted for, never silently dropped.
 for e in t.get('deletions',[]):assert e.get('category')=='mark',e
 out=[];patches=[];cursor=0;output_bytes=0
 for start,(end,value,slot) in sorted(replacements.items()):
  assert start>=cursor
  unchanged=text[cursor:start];out.append(unchanged);output_bytes+=len(unchanged.encode())
  patches.append(dict(slot=slot,raw_byte_start=len(text[:start].encode()),raw_byte_end=len(text[:end].encode()),output_byte_start=output_bytes,output_byte_end=output_bytes+len(value.encode()),before=text[start:end],after=value))
  out.append(value);output_bytes+=len(value.encode());cursor=end
 out.append(text[cursor:]);new=''.join(out);edits=edits_from_traces(t,r['variant'],r['policy_sha'])
 if not replacements:
  assert not edits;return None
 assert new.encode()!=text.encode()
 assert [ud.normalize('NFD',c[2]) for c in raw_clusters(new) if ud.normalize('NFD',c[2])[0].isalpha()]==[ud.normalize('NFD',c[2]) for c in raw_clusters(r['label']) if ud.normalize('NFD',c[2])[0].isalpha()]
 # Independent reconstruction from raw byte spans proves all untouched bytes match.
 raw=text.encode();newb=new.encode();last=0;pieces=[];reverse=[];lastout=0
 for p in patches:
  a,b=p['raw_byte_start'],p['raw_byte_end'];x,y=p['output_byte_start'],p['output_byte_end']
  assert raw[last:a]==newb[lastout:x]
  assert raw[a:b]==p['before'].encode() and newb[x:y]==p['after'].encode()
  pieces.extend([raw[last:a],p['after'].encode()]);reverse.extend([newb[lastout:x],p['before'].encode()]);last=b;lastout=y
 pieces.append(raw[last:]);reverse.append(newb[lastout:]);assert b''.join(pieces)==newb and b''.join(reverse)==raw and raw[last:]==newb[lastout:]
 for e in edits:e['byte_patches']=[p for p in patches if p['slot']==e['slot'] and ((e['kind']=='quote_alias_consume')==(p['after']==''))]
 return dict(line_id=r['line_id'],text=new,parent='google_raw_v2_import',parent_text_sha256=hashlib.sha256(raw).hexdigest(),wave=source['wave'],variant=r['variant'],policy_digest=r['policy_sha'],source_job='3687228',edits=edits,byte_patches=patches)

def main():
 scores=json.load(open(BASE/'lqb_scores.json'));v=scores['choice']['variant'];source={r['id']:r for r in rows(RAW)};selection={r['id']:r for r in rows(SEL)}
 release=list(rows(BASE/f'compact_{v}.jsonl'));corrected=[dict(r,variant=v) for r in release if r['status']=='corrected'];converted=[];normalization_only=[]
 for r in corrected:
  assert r['line_id'] in selection
  assert source[r['line_id']]['label'].encode()==selection[r['line_id']]['label'].encode()
  out=convert(r,source[r['line_id']])
  if out:converted.append(out)
  else:normalization_only.append(r['line_id'])
 target=BASE/f'release_edits_only_{v}.jsonl'
 with target.open('w') as f:
  for r in sorted(converted,key=lambda r:r['line_id']):f.write(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n')
 reread=list(rows(target));assert len(reread)==len(converted) and len({r['line_id'] for r in reread})==len(converted)
 kind=collections.Counter(e['kind'] for r in reread for e in r['edits']);head=collections.Counter(e['head'] for r in reread for e in r['edits']);waves={}
 for wave in sorted({r['wave'] for r in reread}):
  rr=[r for r in reread if r['wave']==wave];waves[wave]=dict(rows=len(rr),edits=sum(len(r['edits']) for r in rr),by_kind=dict(collections.Counter(e['kind'] for r in rr for e in r['edits'])),by_head=dict(collections.Counter(e['head'] for r in rr for e in r['edits'])))
 lqb=Path.home()/'Projects/greek-ocr-toolkit-secondary/docs/labelfix/lqb';truth_paths=[lqb/'truth_v1.jsonl',lqb/'truth_v1_1.jsonl'];excluded={r['line_id'] for p in truth_paths for r in rows(p)}
 auditpath=ROOT/'docs/labelfix/spellcheck/clariden/L1R3_evidence/production_3680729_3680730/audit100_ids.jsonl';auditids={r['line_id'] for r in rows(auditpath)};assert len(auditids)==100
 keypath=ROOT/'docs/labelfix/spellcheck/S8_DEV/private/audit100/items_key.json';auditids|={r['line_id'] for r in json.load(open(keypath)) if not r.get('control',False)}
 eligible=sorted([r['line_id'] for r in reread if r['line_id'] not in excluded|auditids]);assert len(eligible)>=100
 draw=random.Random(20261017).sample(eligible,100)
 frame=BASE/'audit100_frame.jsonl'
 with frame.open('w') as f:
  for i,lid in enumerate(draw,1):
   s=source[lid];f.write(json.dumps(dict(audit_id=f'RB7-{i:03d}',line_id=lid,wave=s['wave'],doc=s.get('doc'),crop=s.get('crop'),seed=20261017,inclusion_probability=100/len(eligible)),ensure_ascii=False,sort_keys=True)+'\n')
 assert len(set(draw))==100 and not set(draw)&(excluded|auditids)
 receipt=dict(schema='rb7-edits-only-release-v1',status='candidate_pre_audit',variant=v,parent='google_raw_v2_import',parent_path=str(RAW),parent_sha256=sha(RAW),path=str(target.relative_to(ROOT)),sha256=sha(target),row_count=len(reread),edit_count=sum(kind.values()),edit_counts_by_kind=dict(kind),edit_counts_by_head=dict(head),per_wave=waves,policy_digest=corrected[0]['policy_sha'],preregistration_sha256=PREREG,source_job='3687228',readback_receipt_sha256=sha(OUT/'READBACK_RECEIPT.json'),lqb_scores_sha256=sha(BASE/'lqb_scores.json'),selection_sha256=sha(SEL),source_corrected_rows=len(corrected),excluded_composer_normalization_only=dict(count=len(normalization_only),line_ids=normalization_only),verification=dict(all_rows_selected=True,no_unchanged_rows=True,exact_utf8_byte_patch_reconstruction=True,raw_and_selection_labels_identical=True,output_readback=True),audit=dict(frame_sha256=sha(frame),rows=100,seed=20261017,design='Python random.Random(seed).sample(sorted eligible exact line IDs,100), uniform without replacement',eligible_rows=len(eligible),truth_excluded_lines=len(excluded),audit100_excluded_lines=len(auditids),excluded_corrected_rows=len(reread)-len(eligible),truth_files={str(p):sha(p) for p in truth_paths},audit100_files={str(p):sha(p) for p in (auditpath,keypath)},reader_packs_built=False),bound=False,submitted=False)
 dump(BASE/'RELEASE_RECEIPT.json',receipt);print('release',len(reread),sum(kind.values()),sha(target),'normalization-only',len(normalization_only),'audit eligible',len(eligible),flush=True)
if __name__=='__main__':main()
