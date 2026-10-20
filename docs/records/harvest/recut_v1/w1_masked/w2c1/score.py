#!/usr/bin/env python3
"""Offline W2 letters/crop gate; fixed replacement routing, deterministic reports."""
import argparse
import json
import sys
from pathlib import Path
from collections import Counter
from build import HERE, PACK_ROOT, STRATA, CANONICAL, COLLECTOR, bedname, rows, sha, dump
from repack_config import REPLACEMENTS
sys.path.insert(0,str(HERE/"tools"))
from map_answers import map_records

BARS_SOURCE=COLLECTOR/'docs/harvest/collect_v3/c1/C1_REPORT.md'

def metric(answers,field):
 counts=dict(sorted(Counter(a[field] for a in answers).items()))
 n=len(answers);yes=counts.get('y',0)
 return dict(n=n,yes=yes,counts=counts,rate=yes/n if n else None)

def score(root=HERE,pack_root=PACK_ROOT):
 if sha(root/'tools/scan_rollout.py')!=CANONICAL:raise ValueError('canonical scanner hash mismatch')
 if 'Gate: letters ≥90 and crop_ok ≥90 (point estimate, n=100)' not in BARS_SOURCE.read_text():raise ValueError('C1 bars changed; review required')
 evidence={};contexts=[];results=[]
 def bind(path):evidence[str(path)]=sha(path)
 bind(root/'tools/scan_rollout.py');bind(BARS_SOURCE)
 for source,cls in STRATA:
  original=bedname(source,cls);answers=[];cs=[];seen=set()
  draw=rows(root/'keys'/original/'draw.jsonl');bind(root/'keys'/original/'draw.jsonl')
  for index,ctx in enumerate(('c1','c2')):
   bed,reader=REPLACEMENTS.get((original,ctx),(original,ctx))
   rp=root/'receipts'/bed/(reader+'.json');bind(rp);receipt=json.loads(rp.read_text())
   info=dict(original_context=original+'/'+ctx,selected_context=bed+'/'+reader,status=receipt['status'],included=False)
   contexts.append(info);cs.append(info)
   if receipt['status']!='audit clean':
    if (original,ctx) not in REPLACEMENTS:raise ValueError('original good context lost eligibility: '+bed+'/'+reader)
    continue
   if receipt.get('scanner_rc')!=0 or receipt.get('map_rc')!=0 or receipt.get('rc')!=0 or receipt.get('canonical_scanner_sha256')!=CANONICAL:raise ValueError('invalid run receipt')
   sp=root/'scan'/bed/(reader+'.scan.json');scan=json.loads(sp.read_text());bind(sp)
   if scan.get('ok') is not True or scan.get('violations') or scan.get('scanner_version')!='v4.4-canonical' or scan.get('manifest_check_skipped') is not False:raise ValueError('invalid scan')
   rollout=Path(receipt['rollout']);bind(rollout)
   if scan.get('rollout')!=str(rollout) or scan.get('rollout_sha256')!=sha(rollout):raise ValueError('rollout binding changed')
   kp=root/'keys'/(bed+'.json');bind(kp);key=json.loads(kp.read_text())
   cp=pack_root/bed/reader/'cards.jsonl';bind(cp)
   ap=root/'answers'/bed/(reader+'.jsonl');bind(ap)
   mapped,controls=map_records('bsb',reader,rows(ap),key,rows(cp))
   if len(mapped)!=50 or len(controls['controls'])!=5:raise ValueError('wrong bed/control counts')
   expected={r['id'] for r in draw[index*50:(index+1)*50]}
   actual={a['card_id'] for a in mapped}
   if actual!=expected or seen&actual:raise ValueError('draw coverage mismatch')
   seen|=actual
   for suffix,value in [('.mapped.jsonl',mapped),('.controls.json',controls)]:
    path=root/'answers'/bed/(reader+suffix);bind(path)
    saved=rows(path) if suffix.endswith('jsonl') else json.loads(path.read_text())
    if saved!=value:raise ValueError('saved mapping/controls changed')
   if receipt.get('controls')!=controls or receipt.get('context_flagged')!=controls['flagged']:raise ValueError('receipt controls changed')
   info.update(included=True,controls=controls,weekly_used_before=receipt['weekly_used_before'],weekly_used_after=receipt['weekly_used_after'])
   answers.extend(mapped)
  letters=metric(answers,'letters');crop=metric(answers,'crop_ok');n=len(answers)
  flagged=any(c.get('controls',{}).get('flagged',False) for c in cs)
  observed=('PASS' if letters['yes']*10>=n*9 and crop['yes']*10>=n*9 else 'FAIL') if n else 'UNAVAILABLE'
  complete=n==100
  verdict=('FAIL' if flagged or observed=='FAIL' else 'PASS') if complete else 'PENDING'
  controlrows=[c for x in cs for c in x.get('controls',{}).get('controls',[])]
  results.append(dict(stratum=original.removeprefix('w2c1_'),source=source,primary_class=cls,n=n,expected_n=100,partial=not complete,letters=letters,crop_ok=crop,marks='pending Opus; Sol whole-line marks excluded (including all grave-heavy Greek strata)',controls=dict(n=len(controlrows),passed=sum(c['passed'] for c in controlrows),errors=sum(not c['passed'] for c in controlrows),flagged=flagged),observed_gate=observed,verdict=verdict,contexts=[c['selected_context'] for c in cs]))
 return dict(partial=any(r['partial'] for r in results),included_contexts=sum(c['included'] for c in contexts),expected_contexts=16,bars=dict(letters=0.90,crop_ok=0.90,n=100,source=str(BARS_SOURCE),sha256=sha(BARS_SOURCE),controls='more than one error flags a context; flagged complete strata FAIL'),canonical_scanner_sha256=CANONICAL,strata=results,contexts=contexts,inputs_sha256=dict(sorted(evidence.items())))

def fraction(m):return f"{m['yes']}/{m['n']} ({m['rate']:.1%})" if m['n'] else 'pending (0/0)'
def render(result):
 text=['# W2C1 results — '+('PARTIAL preview' if result['partial'] else 'complete letters/crop check'),'',f"Included {result['included_contexts']}/16 contexts; VOID originals are excluded permanently. Replacements are used only after a clean canonical scan and complete mapping.",'','C1 bars: letters ≥90% and crop_ok ≥90%, point estimates on 100 bed cards per stratum. Source: [C1_REPORT.md]('+result['bars']['source']+'). Controls are excluded from bed denominators; >1 control error flags a context and prevents a passing stratum. Missing contexts are pending, never zero-score cards. `u` stays in the denominator and is not an exact match.','', 'Letters exact-match means `letters=y` under LABEL_CHECK_v2 (base letters/digits/words and script; diacritics ignored). These are reader label-quality calls, not independent reader-accuracy measurements.','', '| Stratum | Bed cards | Letters exact match | crop_ok | Controls passed | Observed ≥90% bars | Stratum pass/fail |','|---|---:|---:|---:|---:|---|---|']
 for r in result['strata']:
  c=r['controls'];text.append(f"| {r['stratum']} | {r['n']}/100 | {fraction(r['letters'])} | {fraction(r['crop_ok'])} | {c['passed']}/{c['n']}"+(' FLAGGED' if c['flagged'] else '')+f" | {r['observed_gate']} | {r['verdict']}"+(' (partial)' if r['partial'] else '')+' |')
 text+=['','Marks: pending Opus for grave-heavy strata; all Sol whole-line mark calls are excluded from decisions under HANDOVER §§1, 3. No marks pass or admission is claimed. Partial observed gates do not establish a 100-card stratum result.','', '## Context custody','']
 for c in result['contexts']:
  text.append(f"- `{c['selected_context']}`: "+('included' if c['included'] else c['status'])+(f"; controls {5-c['controls']['control_errors']}/5; weekly probe before/after {c['weekly_used_before']:g}%/{c['weekly_used_after']:g}% (recorded, not live)" if c['included'] else ''))
 text+=['',f"Canonical scanner SHA-256: `{CANONICAL}`. JSON records all scoring input hashes. Reports are deterministic and use no network, probe, reader, or live features file.",'']
 return '\n'.join(text)
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',type=Path,default=HERE);args=parser.parse_args()
 result=score();dump(args.output_dir/'W2C1_RESULTS.json',result);(args.output_dir/'W2C1_RESULTS.md').write_text(render(result));print('PARTIAL' if result['partial'] else 'COMPLETE',result['included_contexts'],'contexts')
if __name__=='__main__':main()
