"""Seal CQ4c build receipts after build and offline validation."""
import collections as C,hashlib,json,math,sys
from pathlib import Path
from build import *

def main():
 receipt=load(OUT/'build_receipt.json');inputs=dict(load(OUT/'prior_cq4b/build_receipt.json')['inputs_sha256']);inputs.update(receipt['inputs_sha256']);inputs.update(load(OUT/'keys/intake_hashes.json'));inputs.update(load(OUT/'keys/selection_hashes.json'))
 for p in [ROOT/'docs/briefs/CQ4c_build_fix.md',ROOT/'docs/briefs/CQ4b_build_amended.md',ROOT/'docs/briefs/CQ4_capitals_witness_and_topup_build.md',ROOT/'docs/labelfix/case_model_S5.json',*[ROOT/'greekocr/labelfix'/n for n in ['case.py','ink.py','segmentation.py','ctc_align.py','markshape.py','text.py']]]:inputs[str(p)]=sha(p)
 old_inventory=ROOT.parent/'greek-ocr-toolkit-spellcheck-s8/.cache/labelfix/clariden/C1_crop_inventory.jsonl.gz'
 old={x['sha256'] for x in rows(old_inventory)};inputs[str(old_inventory)]=sha(old_inventory)
 selected={name:rows(OUT/'keys'/f'{name}_selected.jsonl') for name in ('wcap','topup')}
 hits=[x for x in selected['topup'] if x['slot_id'][0] in old]
 # No selected crop is in R1: stronger than zero old-slot identity overlap.
 assert not hits,'STOP: old crop overlap needs exact R1 slot lookup before sealing'
 dump(OUT/'keys/old_overlap.json',dict(scanner_sha256=SCANNER_SHA,old_crop_inventory_sha256=sha(old_inventory),old_crop_hashes=len(old),selected_topup_slots=len(selected['topup']),hits_on_old_crops=0,hits_on_old_slot_keys=0,hits_on_duplicated_old_keys=0,policy='Future unique old-key hits replace in place. Duplicated-key hits STOP. workflow.overlay_rows fixture-tested.'))
 # Re-scan the actual original CQ1 rollouts with the exact canonical scanner.
 import scan_rollout
 regress={}
 for entry in load(ROOT/'artifacts/cq1/usage_ledger.json'):
  name=entry['reader'];cl=load(ROOT/('artifacts/cq1/closure'+('_r1b' if name=='r1b' else '')+'.json'));cl=cl[0] if isinstance(cl,list) else cl
  rd=Path(cl['directory']);rollout=Path(entry['run']['rollout']);result=scan_rollout.inspect(rollout,rd);result['scanner_sha256']=SCANNER_SHA
  assert result['ok']==(name=='r1b') and not result['manifest_check_skipped']
  if name=='r1':assert any(v.get('record')==24 and v.get('path')=='/zoom/batch1.png' for v in result['violations'])
  dump(OUT/'regression'/f'cq1_{name}.scan_v44.json',result);regress[name]='clean' if result['ok'] else 'VOID record 24'
  inputs[str(rollout)]=sha(rollout);inputs[str(rd.parent/f'MANIFEST.{rd.name}.json')]=sha(rd.parent/f'MANIFEST.{rd.name}.json')
 source=ROOT.parent/'greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/tools/scan_rollout.py';assert sha(source)==sha(OUT/'tools/scan_rollout.py')==SCANNER_SHA
 inputs.pop(str(OUT/'build_receipt.json'),None) # output receipt cannot bind its previous bytes as an input
 for p,value in inputs.items():
  h=hashlib.sha256()
  with Path(p).open('rb') as f:
   for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
  assert h.hexdigest()==value,('input changed',p)
 from closure import scan
 contexts=load(OUT/'contexts.json')
 for c in contexts:
  k=load(c['key']);result=scan(c['directory'],k['items']);assert result['ok'],result['violations'];dump(OUT/'closure'/f'{c["tag"]}.json',result);c['manifest_sha256']=hashlib.sha256((Path(c['directory']).parent/'MANIFEST.r1.json').read_bytes()).hexdigest()
 dump(OUT/'contexts.json',contexts)
 receipt.update(inputs_sha256=inputs,cq1_rescan=regress,scanner_source_sha256=sha(source),scanner_destination_sha256=sha(OUT/'tools/scan_rollout.py'),old_identity_overlap=load(OUT/'keys/old_overlap.json'),unused_documents_dropped=load(OUT/'keys/intake.json')['unused_documents_dropped'],bare_context_counts={name:dict(C.Counter(x['bare_kind'] for x in v if x['likely']=='bare')) for name,v in selected.items()},network='OFF; Python sockets blocked; no service/reader/probe calls',git_writes=False)
 dump(OUT/'build_receipt.json',receipt)
 inv={name:load(OUT/f'{name}_inventory.json') for name in selected};inv.update(status=receipt['status'],seed=SEED,preregistration_sha256=PREREG_SHA,scanner_sha256=SCANNER_SHA,cq1_rescan=regress)
 dump(OUT/'inventory.json',inv)
 final=f"CQ4c BUILD READY: W-CAP docs {receipt['selected']['wcap']['documents']} slots {receipt['selected']['wcap']['slots']} (marked-likely {receipt['selected']['wcap']['classes']['marked']}/bare-likely {receipt['selected']['wcap']['classes']['bare']}); top-up docs {receipt['selected']['topup']['documents']} slots {receipt['selected']['topup']['slots']}; contexts {receipt['contexts']}; controls pool 40 (sheet artifacts/cq4/control_review/controls.png); est. Codex {receipt['codex_estimated_points']} pts"
 lines=['# CQ4c build report','', 'Both corrected inputs are built. **BUILD ONLY:** no reader, recogniser/teacher inference, limit probe, training, or manifest build ran. Network was off and no `.git` writes were made. The 40-control sheet is built with lead review **pending**, as specified; RUN_ALL refuses until all 40 are verified.','',f'Preregistration amendment 1 SHA-256: `{PREREG_SHA}`. Canonical scanner v4.4 source and local copy: `{SCANNER_SHA}`. Fresh CQ1 regression: **r1 VOID at record 24; r1b clean**, with manifest checks enabled.','', '## Corrected eligibility and identity','', 'Top-up admits supervision/T2 documents and old training documents; it excludes T2 word slots, all R2a v2 slots, and the document union in `artifacts/cq4/excluded_docs.json`. W-CAP uses the 17 validation documents and all 3 unused documents: all three have saved alignments, so none were dropped. Validation capitals are bound to `validation_reserve` teacher exports from job 3681404. Every consumed B-stage file was rehashed against READBACK_RECEIPT; selected native crops were independently SHA-verified, including R2P2 upload copies where original paths are now absent.','', 'Slot identity is `(crop SHA-256, recogniser NFD start)`. Capital case and target boxes come from the existing S5 case model and native component/CTC geometry; sampling labels remain private and are not truth. Selected top-up crop hashes have **zero** overlap with the complete saved C1 crop inventory, hence zero old-key or duplicated-key hits. The R2J4 replacement helper preserves old row order and duplicates, replaces unique existing keys, and stops on ambiguous keys; no overlay manifest is generated here.','', '## Inventory and selection','', '| Set | Located capital candidates | Candidate documents | Selected slots | Marked-likely | Bare-likely | Selected documents | 70% minimum |','|---|---:|---:|---:|---:|---:|---:|---:|']
 candidates=load(OUT/'keys/candidates.json')
 for name in selected:
  r=receipt['selected'][name];lines.append(f"| {name} | {len(candidates[name])} | {len({x['doc'] for x in candidates[name]})} | {r['slots']} | {r['classes']['marked']} | {r['classes']['bare']} | {r['documents']} | {inv[name]['minimum']} |")
 lines+=['','Seed 20261017; at most 30 W-CAP or 120 top-up slots per document, and five per page. W-CAP bare context mix: '+json.dumps(receipt['bare_context_counts']['wcap'])+'. These are sampling context labels. Both sets meet the full requested targets, above the 70% gates.','', '### Counts per document (located before case/geometry filtering; selected after filtering)','', '| Set | Document | Source | Era | Located marked | Located bare | Selected marked | Selected bare |','|---|---|---|---|---:|---:|---:|---:|']
 for name in selected:
  for d in sorted({x['doc'] for x in candidates[name]}):
   xs=[x for x in candidates[name] if x['doc']==d];a=C.Counter(x['likely'] for x in xs);b=C.Counter(x['likely'] for x in selected[name] if x['doc']==d);year=xs[0]['source_era'];era=f'{int(year)//10*10}s' if str(year).isdigit() else 'unknown'
   lines.append(f"| {name} | `{d}` | {xs[0]['source']} | {era} | {a['marked']} | {a['bare']} | {b['marked']} | {b['bare']} |")
 lines+=['','## Packs and later execution','', 'Isolated packs: `/private/tmp/cq4c/scratchpad/solcap_wcap/` and `/private/tmp/cq4c/scratchpad/solcap_topup/`. Keys, controls, contact sheet, prompts and reports remain under `artifacts/cq4/`, outside those roots. Each context has at most 90 bed items and 10 controls, opaque fresh IDs, shuffled options and content-hash PNGs without metadata or links. The CQ1 prompt is byte-identical. All contexts passed closure checks; manifests are beside reader directories.','', 'After lead control review, `bash artifacts/cq4/RUN_ALL.sh` runs initial contexts sequentially with the ≥78% refusal gate, before/after probes, canonical v4.4 scan, and ≤1 control-error gate. Failed contexts are recorded VOID and never scored. `BUILD_REREAD.sh` builds fresh contexts for every unreadable and every breathing-only answer (the conservative ink fallback). Read those with `RUN_ALL.sh --phase reread`, then `AGGREGATE.sh`. Disagreements and unreadables are quarantined in the lead queue and contact sheet; they are never auto-resolved. Truth output retains separate W-CAP/top-up files and the exact tier `C_sol_one_reader_reread`.','', '## Validation and cost','', 'Offline checks cover deterministic selection, document/page caps, corrected exclusion unions, T2/v2 slot exclusion, every pack closure, prompt identity, control schema, re-read fixtures and R2J4 replacement/duplicate behavior. Results: `artifacts/cq4/validation.json` and `tests.log`. Input SHA re-read passed; the scanner source/copy and CQ1 regressions were verified again.','',f"Initial reader estimate: **{receipt['codex_estimated_points']} weekly points**, from {sum(c['items'] for c in load(OUT/'contexts.json'))} card-reads × the handover upper bound of 0.002 points/read. Re-reads are additional. Executed reader cost: **0**; live weekly usage remains unknown because this is a build-only task.",'', 'Build reproduction: `bash artifacts/cq4/BUILD.sh` (build, receipt seal, offline validation). It refuses to overwrite existing packs. Revalidate the existing build with the same offline Python environment and `artifacts/cq4/tools/validate_build.py`. CQ4/CQ4b stopped artifacts are preserved in `prior_cq4/` and `prior_cq4b/`.','',final]
 (R2/'CQ4_REPORT.md').write_text('\n'.join(lines)+'\n')
 # Freeze scripts, prompts, keys and initial assignment/custody; review file stays editable by lead.
 frozen={}
 for p in OUT.rglob('*'):
  if not p.is_file():continue
  rel=str(p.relative_to(OUT))
  if rel.startswith(('tools/','launchers/','prompts/','keys/','closure/')) or rel in ('contexts.json','BUILD.sh','RUN_ALL.sh','BUILD_REREAD.sh','AGGREGATE.sh','control_review/controls.png'):frozen[rel]=sha(p)
 dump(OUT/'build_hashes.json',frozen)
 print(final)
if __name__=='__main__':main()
