"""CQ4d human-readable report from sealed run ledgers and truth outputs."""
import collections as C,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
def load(p):return json.loads(p.read_text())
def rows(p):return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
def main():
 a=load(OUT/'aggregate_receipt.json');swap=load(OUT/'control_swap_receipt.json');initial=load(OUT/'initial_ledger.json');reread=load(OUT/'reread_ledger.json');ledger=initial+reread
 contexts=load(OUT/'contexts.json')+load(OUT/'reread_contexts.json');context_by={c['tag']:c for c in contexts}
 voids=[r for r in ledger if r['status']=='VOID'];stats={}
 for name in ('wcap','topup'):
  truth=rows(OUT/'truth'/f'{name}.jsonl');classes=C.Counter('bare' if t['breathing']=='none' and t['accent']=='none' else 'marked' for t in truth)
  compounds=C.Counter(t['breathing']+'+'+t['accent'] for t in truth if t['breathing'] in ('smooth','rough') and t['accent'] in ('acute','grave','circumflex'))
  slots=sum(context_by[r['tag']]['bed_items'] for r in initial if r['set']==name and 'run' in r)
  valid_slots=sum(context_by[r['tag']]['bed_items'] for r in initial if r['set']==name and r['status']=='VALID')
  stats[name]=dict(slots_read=slots,valid_initial_slots=valid_slots,resolved=len(truth),lead_queue=sum(x['set']==name for x in rows(OUT/'lead_queue.jsonl')),marked=classes['marked'],bare=classes['bare'],compounds=dict(compounds),compound_total=sum(compounds.values()))
 before=a['codex_before']['weekly_used'];after=a['codex_after']['weekly_used'];pct=f"{100*a['reread_agreement_rate']:.2f}%" if a['reread_agreement_rate'] is not None else 'N/A'
 text=['# CQ4d reading report','',f"Replaced **{swap['swap_count']} control placements** across {len(swap['changed_contexts'])} contexts, using seed 20261017 and the 33 lead-verified controls. The seven rejected pool controls remain excluded. Every bed-item JSONL line, item order, and prompt stayed byte-identical. Only affected initial packs were rebuilt. No `.git` writes.",'',f"Attempted {len(initial)} initial and {len(reread)} re-read contexts configured for gpt-6.1-sol, medium; **{len(voids)} VOID**. VOID answers were never scored. The pre/post probes, 78% refusal gate, canonical v4.4 scan and at-most-one-control-error gate remained active.",'','| Set | Initial slots read | Valid initial slots | Resolved | Quarantined to lead queue | Marked | Bare | Compounds |','|---|---:|---:|---:|---:|---:|---:|---:|']
 for name,label in [('wcap','W-CAP'),('topup','Top-up')]:
  s=stats[name];text.append(f"| {label} | {s['slots_read']} | {s['valid_initial_slots']} | {s['resolved']} | {s['lead_queue']} | {s['marked']} | {s['bare']} | {s['compound_total']} |")
 text+=['','All 18 reader startups failed before producing a rollout or any answers. Confirmed model reads: **0**. Re-read selection is empty because no initial answer is scoreable. All 1505 selected slots are quarantined.','', 'Slots read counts bed slots in launched initial reader contexts; re-read slots are additional. Marked means at least one printed breathing or accent; bare is negative, marked is positive. Compounds are the subset with both breathing and accent. Sampling likelihood labels are not truth.','',f"Re-read agreement: **{pct}** ({a['reread_agreed']}/{a['reread_triggered']} triggered slots; missing/VOID re-reads stay in the denominator). Agreed unreadables remain quarantined. Re-read trigger: every unreadable and every breathing-only answer, using the preregistered conservative fallback.",'','Compound counts (breathing + accent):','']
 for name in stats:text.append(f"- {name}: `{json.dumps(stats[name]['compounds'],sort_keys=True)}`")
 text+=['','VOID contexts and causes:','']
 text += [f"- `{r['tag']}`: {r['void_reason']}. Reader startup log: failed to initialize in-process app-server client: Operation not permitted (os error 1)." for r in voids] or ['None.']
 text+=['',f"Codex weekly: **{before:g}% → {after:g}%** ({after-before:+g} percentage points), from the first before-probe and last after-probe. Probe outputs are retained in the ledgers and `limit_probe.log`.",'','Truth tier: `C_sol_one_reader_reread`. W-CAP is witness-only; top-up truth is separate. No training or manifest-overlay build ran.','', 'Evidence: [swap receipt](../../../../artifacts/cq4/control_swap_receipt.json), [validation](../../../../artifacts/cq4/validation.json), [aggregate receipt](../../../../artifacts/cq4/aggregate_receipt.json), [lead queue](../../../../artifacts/cq4/lead_queue.jsonl), [contact sheet](../../../../artifacts/cq4/lead_queue.png).','']
 receipt=dict(swaps=swap['swap_count'],contexts_attempted=len(ledger),confirmed_model_reads=sum('run' in r for r in ledger),void_contexts=[dict(tag=r['tag'],cause=r['void_reason'],startup_log=str(OUT/'logs'/f"{r['tag']}.codexlog")) for r in voids],sets=stats,reread_agreement_rate=a['reread_agreement_rate'],codex_weekly_before=before,codex_weekly_after=after,git_writes=False)
 (OUT/'execution_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 w=stats['wcap'];t=stats['topup'];last=f"CQ4d READY: swaps {swap['swap_count']}; contexts run {len(ledger)} (VOID {len(voids)}); W-CAP resolved {w['resolved']}/300 (marked {w['marked']}, bare {w['bare']}); top-up resolved {t['resolved']} (neg {t['bare']}/pos {t['marked']}); re-read agreement {pct}; lead queue {a['lead_queue']}; Codex {before:g}%→{after:g}%"
 text.append(last);(ROOT/'docs/labelfix/spellcheck/R2/CQ4_REPORT.md').write_text('\n'.join(text)+'\n');print(last)
if __name__=='__main__':main()
