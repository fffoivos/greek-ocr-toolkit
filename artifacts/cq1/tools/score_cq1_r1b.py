"""Score one frozen CQ1 answer file; fail closed on coverage/schema/leak errors."""
import argparse,collections,json
from pathlib import Path
from common import ROOT,PACK_ROOT,rows,dump,sha

def score(answer,scan,before,after):
 key=json.loads((ROOT/'keys/cap1.json').read_text());ids=key['readers']['r1'];answers=rows(answer)
 audit=json.loads(Path(scan).read_text());assert audit['ok'] and audit['scanner_version']=='4.3' and not audit.get('manifest_check_skipped',True),'Run void: leak scan failed'
 assert [a.get('item_id') for a in answers]==ids,'answer order/coverage mismatch'
 assert len(answers)==66 and len(set(ids))==66
 detail=[]
 for a in answers:
  assert set(a)=={'item_id','breathing','accent','confidence','note'}
  assert a['confidence'] in ('high','low') and isinstance(a['note'],str)
  k=key['items'][a['item_id']];p=k['public'];assert a['breathing'] in p['breathing_options'] and a['accent'] in p['accent_options']
  got=dict(breathing=p['breathing_options'][a['breathing']],accent=p['accent_options'][a['accent']]);want=k['expected']
  detail.append(dict(item_id=a['item_id'],control=k['control'],expected=want,observed=got,exact=got==want,invented_breathing=got['breathing'] in ('smooth','rough') and want['breathing']=='none',wrong_breathing=got['breathing'] in ('smooth','rough') and got['breathing']!=want['breathing'],invented_accent=got['accent'] in ('acute','grave','circumflex') and want['accent']=='none',unreadable='unreadable' in got.values()))
 def metrics(data):
  return dict(n=len(data),exact=sum(x['exact'] for x in data),exact_tuple_agreement=sum(x['exact'] for x in data)/len(data),invented_breathings=sum(x['invented_breathing'] for x in data),wrong_breathing_types_including_inventions=sum(x['wrong_breathing'] for x in data),invented_accents=sum(x['invented_accent'] for x in data),unreadables=sum(x['unreadable'] for x in data))
 bed=metrics([x for x in detail if not x['control']]);ctrl=metrics([x for x in detail if x['control']]);ctrl['errors']=6-ctrl['exact'];ctrl['context_flagged']=ctrl['errors']>1
 # Wrong hook type is a tuple error; the preregistered invention count is absent -> present.
 valid=not ctrl['context_flagged'];qualifies=valid and bed['exact']>=57 and bed['invented_breathings']==0
 result=dict(status='scored',valid=valid,qualifies=qualifies,bed=bed,controls=ctrl,weekly_probe_before=before,weekly_probe_after=after,answer_sha256=sha(answer),scan_sha256=sha(scan),details=detail,scope='Capital T2 available tuples only; no capital grave available. Does not authorize R2a-2.')
 dump(ROOT/'answers/r1b.score.json',result)
 report=ROOT.parents[1]/'docs/labelfix/spellcheck/R2/CQ1_R1B_REPORT.md'
 report.write_text(f'''# CQ1 capitals qualification\n\nStatus: completed; {'QUALIFIED' if qualifies else 'NOT QUALIFIED'} on the available T2 bed.\n\nOne gpt-6.1-sol reader, medium, network OFF; seed 20261017. Bed 60 (30 positive / 30 negative), controls 6. Exact tuple: {bed['exact']}/60 ({bed['exact_tuple_agreement']:.1%}); invented breathings {bed['invented_breathings']}, invented accents {bed['invented_accents']}, unreadables {bed['unreadables']}. Controls {ctrl['exact']}/6; context flagged: {ctrl['context_flagged']}. Leak scan v4.3 passed with manifest checks.\n\nBar: at least 57/60 exact and zero invented breathings; more than one control error voids qualification. See `artifacts/cq1/answers/r1b.score.json` for per-item results and wrong hook types.\n\nWeekly budget before: {before}\n\nWeekly budget after: {after}\n\nNo capital grave exists in T2 resolved truth, so this result cannot qualify that tuple. Existing-v2 overlap and future top-up reservation are listed in `artifacts/cq1/keys/`. T4 documents excluded. R2a-2 remains the owner's decision.\n''')
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('answers',type=Path);p.add_argument('scan',type=Path);p.add_argument('--before',required=True);p.add_argument('--after',required=True);a=p.parse_args();r=score(a.answers,a.scan,a.before,a.after);print(json.dumps({k:v for k,v in r.items() if k!='details'},indent=2))
