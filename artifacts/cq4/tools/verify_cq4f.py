"""Offline CQ4F custody, coverage and coordinator-entrypoint checks; no readers."""
import collections
import hashlib
import json
from pathlib import Path
from unittest.mock import patch
import workflow as w
from closure import scan


def main():
 out=w.OUT
 digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
 source=out.parents[1]/'../greek-ocr-toolkit-spellcheck-r2cards/artifacts/cq4'
 with patch.object(w.subprocess,'run',side_effect=AssertionError('reader/subprocess forbidden during verification')):
  w.frozen_verified()
  assert digest(out/'initial_ledger.json')==digest(source/'initial_ledger.json')
  for p in (out/'scans').glob('*_initial_*.json'):
   assert digest(p)==digest(source/'scans'/p.name)
  imported=w.load(out/'rescan_ledger.json')
  assert len(imported)==15 and all(r['status']=='VALID' and r['control_errors']<=1 for r in imported)
  first=w.valid_answers('initial')
  assert collections.Counter(name for _,_,name in first.values())==dict(wcap=300,topup=1205)
  expected={sid for sid,(_,answer,_) in first.items() if w.reread_trigger(answer)}
  contexts=w.load(out/'reread_contexts.json');actual=[]
  for c in contexts:
   rd=Path(c['directory']);assert not (rd/'answers.jsonl').exists()
   assert digest(rd.parent/'MANIFEST.r1.json')==c['manifest_sha256']
   key=w.load(c['key'])['items'];closure=scan(rd,key,write=False)
   assert closure['ok'],closure['violations']
   actual.extend(tuple(x['slot_id']) for x in key.values() if not x['control'])
  assert len(actual)==len(set(actual)) and set(actual)==expected
  assert w.load(out/'reread_ledger.json')==[]
  # The coordinator runner sees these packs as pending and respects the usage guard.
  with patch.object(w,'probe',return_value=dict(weekly_used=78)) as probe:
   try:w.run_all('reread')
   except RuntimeError as exc:assert 'weekly usage >=78%' in str(exc)
   else:raise AssertionError('runner did not stop at usage guard')
   assert probe.call_count==1 and probe.call_args.args==(contexts[0]['tag']+'_before',)
  # Aggregation must refuse incomplete rereads before writing any output.
  with patch.object(w,'dump') as dump,patch.object(w,'jsonl') as jsonl,patch.object(w,'contact_sheet') as sheet:
   try:w.aggregate()
   except AssertionError as exc:assert str(exc)=='RUN_ALL incomplete'
   else:raise AssertionError('aggregate accepted missing rereads')
   dump.assert_not_called();jsonl.assert_not_called();sheet.assert_not_called()
 receipt=dict(status='PASS',network_used=False,reader_runs=0,initial_valid_contexts=18,
  initial_slots=len(first),reread_targets=len(actual),reread_contexts=len(contexts),
  exact_trigger_coverage=True,original_v44_records_unchanged=True,pack_closure='7/7 PASS',
  runner_usage_guard='PASS (mocked; no probe launched)',aggregate_incomplete_guard='PASS')
 w.dump(out/'cq4f_validation.json',receipt)
 print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
