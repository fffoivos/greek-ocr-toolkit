import json,hashlib
from pathlib import Path
p=Path('artifacts/sq1');c=json.loads((p/'census.json').read_text());report=Path('docs/labelfix/spellcheck/SQ1_QUOTE_BREATHING.md')
sha=hashlib.sha256((p/'census.py').read_bytes()).hexdigest();(p/'census.sha256').write_text(sha+'  census.py\n')
s='''
## Read-only Clariden exposure census

Production run `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1e_20261017/l1r_sf6_3680729` is complete. The census streamed all three overlay files on the login node, with no remote filesystem writes. It checked unique IDs and exact population equality with the selection: **124,669 lines per mode**, including **1,753** original lines with a requested quote alias immediately before a Greek capital. The final scan took **%.2f seconds**. An initial scan was repeated after correcting modifier-apostrophe letter indexing and including word-initial lowercase spacing-breathing sites; total scan time was about 127 seconds. No authentication error occurred and no certificate refresh was attempted.

The production policy binding is `%s`; it binds the merged L1R3 packaging. Its gate SHA matches the frozen local gate; the local 16-path policy remains `6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406`. Packaging bindings are not interchangeable.

A match requires the same alphabetic base sequence and a newly added NFD psili, dasia, acute, grave or circumflex on the matched capital. Elision modifier characters are excluded from letter indexing, as in the frozen gate. Counts below are **actual emitted labels**, excluding HOLD proposals. Sites and unique lines are separately recorded; modes are not summed.

| Mode | (i) Kept quote + added mark, lines | (ii) Removed quote + added mark, lines | Matching HOLD proposals, lines | Google spacing-breathing lines / sites | Released spacing lines / attached sites |
|---|---:|---:|---:|---:|---:|
'''%(c['elapsed_seconds'],c['policy']['sha256'])
for mode,v in c['modes'].items():
 x=v['counts'];s+=f"| {mode} | {x['i_kept_lines']} | {x['ii_removed_lines']} | {x['hold_candidate_lines']} | {x['spacing_google_lines']} / {x['spacing_google_sites']} | {x['spacing_released_lines']} / {x['spacing_attached_sites']} |\n"
s+='''
**There are no ten example IDs for (i): its measured population is empty.** `examples_i=[]` in every mode. Ten HOLD proposal examples per mode, clearly labeled as HOLD, are retained in the JSON instead. Zero released exposure is an abstention result for this population; it does not establish that the gate has learned the physical distinction, nor cover the collect-v3 W1/W2/W3 population. The selected legacy waves are listed below.

Category (ii) is also empty, so no removal rule actually fired on a released quote-alias-plus-added-mark case. The code's leading-quote stripping and SF5/SF6b spacing MOVE paths are described above; they must not be reported as observed category-(ii) releases.

Per-alias results are identical across the three modes:

| Google alias | (i) lines | (ii) lines | Matching HOLD lines |
|---|---:|---:|---:|
'''
v=c['modes']['presence']
for key,x in v['groups'].items():
 if key.startswith('alias:'):s+=f"| `{key[6:]}` | {x['i_kept_lines']} | {x['ii_removed_lines']} | {x['hold_lines']} |\n"
s+='\nPer-wave results, also identical across modes for (i), (ii), HOLD and original spacing counts:\n\n| Wave | (i) | (ii) | Matching HOLD | Google spacing lines |\n|---|---:|---:|---:|---:|\n'
for key,x in v['groups'].items():
 if key.startswith('wave:'):s+=f"| {key[5:]} | {x['i_kept_lines']} | {x['ii_removed_lines']} | {x['hold_lines']} | {x.get('spacing_google_lines',0)} |\n"
s+='\nPer-source results for (i), (ii) and matching HOLD are identical across modes:\n\n| Source | (i) | (ii) | Matching HOLD | Google spacing lines |\n|---|---:|---:|---:|---:|\n'
for key,x in v['groups'].items():
 if key.startswith('source:'):s+=f"| {key[7:]} | {x['i_kept_lines']} | {x['ii_removed_lines']} | {x['hold_lines']} | {x.get('spacing_google_lines',0)} |\n"
s+='''
The JSON also includes wave × source cells for each mode. For contrast, the explicit `᾿᾽` spacing path has **167 lines / 169 sites** in the source; **165 lines / 167 sites** precede capitals, and two further sites are word-initial lowercase vowels. These are source candidate counts, not 169 successful MOVEs. Only ENSEMBLE_AB emits an attachment: one released line / one attached site, reported by the saved `spacing_breathings_attached` census. PRESENCE and FULL emit none. This does not claim that every spacing case is physically adjudicated.

[Census JSON](../../../../artifacts/sq1/census.json), [executed census script](../../../../artifacts/sq1/census.py), [script SHA receipt](../../../../artifacts/sq1/census.sha256). Script SHA-256: `%s`. Input selection/receipt hashes, exact overlay paths, compressed sizes, policy source map, examples and per-mode cells are in the JSON. The script uses standard-library text/JSON inspection, not inference or gate recomposition, with a 210-second alarm.

## Frozen-scope verification

All **30** local labelfix Python files and the **16 policy paths** were hash-checked before and after (overlapping files counted once in the receipt). No protected bytes changed. [Before](../../../../artifacts/sq1/protected_before.json), [after](../../../../artifacts/sq1/protected_after.json). The one-line executable verification confirms detector/owner-sidecar equality, source-blob ownership, R1 factors, both final HOLD decisions and the isolated quote-retaining renderer witness. No gate fix was implemented.

SQ1 READY: line emits HOLD; clusters 1 compound (2 component blobs); distinguishes no; exposure (i) kept-quote+added-mark 0 lines, (ii) 0; fix shape stated
'''%sha
report.write_text(report.read_text().replace('../../../..//artifacts','../../../../artifacts')+s)
# Confirm local frozen gate is the same one certified by production packaging.
a=json.loads((p/'line_result.json').read_text());assert a['policy']['sources']['greekocr/labelfix/release_gate.py']==c['policy']['sources']['greekocr/labelfix/release_gate.py']
assert all(v['lines']==c['selected_lines'] for v in c['modes'].values())
assert all(v['counts']['i_kept_lines']==v['counts']['ii_removed_lines']==0 for v in c['modes'].values())
print(sha)
