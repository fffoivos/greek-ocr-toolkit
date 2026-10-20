"""RB7 byte-patch functions copied unchanged except parameterised source job."""
import json,collections,unicodedata as ud,hashlib
from pathlib import Path
from scripts.labelfix.clariden.l1_common import rows,sha256,write_json
SOURCE_JOB=None
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
   result.append(dict(slot=slot,kind=kind,head=HEAD[part],from_part=a['part'] if a else None,to_part=b['part'] if b else None,rule=rule,signals=[e.get('signals',{}) for e in evidence],signal_traces=evidence,variant=variant,policy_digest=policy,source_job=SOURCE_JOB))
 for q in t.get('quotes',[]):
  assert q['operation']!='HOLD'
  if q['operation']=='CONSUME_ALIAS':
   result.append(dict(slot=q['boundary'],kind='quote_alias_consume',head='quote_alias',rule='SQ1',signals=dict(mark_source_ids=q['mark_source_ids'],quote_source_ids=q['quote_source_ids']),trace=q,variant=variant,policy_digest=policy,source_job=SOURCE_JOB))
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
 return dict(line_id=r['line_id'],text=new,parent='google_raw_v2_import',parent_text_sha256=hashlib.sha256(raw).hexdigest(),wave=source['wave'],variant=r['variant'],policy_digest=r['policy_sha'],source_job=SOURCE_JOB,edits=edits,byte_patches=patches)


def release(raw, selection, overlay, out, split, source_job):
 global SOURCE_JOB
 SOURCE_JOB=str(source_job)
 source={r['id']:r for r in rows(raw)}; selected={r['id']:r for r in rows(selection)}
 converted=[];seen=set();normalization_only=[]
 for r in rows(overlay):
  lid=r['line_id'];assert lid in selected and lid not in seen;seen.add(lid)
  assert source[lid]['label'].encode()==selected[lid]['label'].encode()
  if r['status']!='corrected':continue
  v=convert(r,source[lid])
  if v:converted.append(dict(v,release_id='sf7_rc1_test_edits_A',split=split))
  else:normalization_only.append(lid)
 assert seen==set(selected)
 target=Path(out)/f'release_edits_only_{split}_A.jsonl'
 with target.open('x',encoding='utf8') as f:
  for r in sorted(converted,key=lambda r:r['line_id']):f.write(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n')
 actual=list(rows(target));assert actual==sorted(converted,key=lambda r:r['line_id'])
 assert len({r['line_id'] for r in actual})==len(actual)
 kind=collections.Counter(e['kind'] for r in actual for e in r['edits'])
 receipt=dict(schema='rb7-edits-only-release-v1',release_id='sf7_rc1_test_edits_A',split=split,
 status='candidate_pre_audit',bound=False,parent='google_raw_v2_import',parent_path=str(raw),
 parent_sha256=sha256(raw),selection_sha256=sha256(selection),overlay_sha256=sha256(overlay),
 path=str(target),sha256=sha256(target),row_count=len(actual),edit_count=sum(kind.values()),
 edit_counts_by_kind=dict(kind),source_job=SOURCE_JOB,variant='A',
 policy_digest='f41e05636d165f1d15edbdb4f2bb6c1aa46721962a96302be8c4dce7ce305047',
 preregistration_sha256='64a84ed0c8799026d44f066570b54075e9b9d1fbca8e2f099cfc9e9451189b2d',
 normalization_only=normalization_only,verification=dict(all_rows_selected=True,no_unchanged_rows=True,
 exact_utf8_forward_reverse_patch_reconstruction=True,output_readback=True))
 write_json(Path(out)/f'RELEASE_RECEIPT_{split}.json',receipt)
 return receipt
