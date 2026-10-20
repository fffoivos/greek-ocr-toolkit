import json, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
OUTD = Path(sys.argv[1])
rs = [json.loads(l) for l in open(OUTD / 'samples.jsonl')]
typ = [r for r in rs if r['set'].startswith('typology')]
uni = [r for r in typ if r['set'] == 'typology_uniform']; sup = [r for r in typ if r['set'] != 'typology_uniform']
ORDER = ['word_or_phrase', 'heading_caps_display', 'abbreviation_reference_label', 'punctuation_only', 'roman_numeral_lowercase',
         'noise_non_text', 'handwriting', 'foreign_script_printed', 'map_figure_ornament_logo', 'scan_watermark', 'show_through_mirrored',
         'cut_fragment', 'multi_line_crop', 'text_covers_part_of_crop']
o = []; w = o.append
cu = Counter(r['type'] for r in uni); cs = Counter(r['type'] for r in sup)
w('| type | uniform sample n (of 120) | % | owner supplement n (of 59) | 0.5 KEEP / DROP / UNCERTAIN (all 179) | owner good / bad (rated rows) | median w×h px | median ratio | median ratio/char |')
w('|---|---:|---:|---:|---|---|---|---:|---:|')
for t in ORDER:
    sel = [r for r in typ if r['type'] == t]
    v = Counter(r['verdict_05'] for r in sel)
    good = sum(r['owner'] in ('fine', 'KEEP') for r in sel); bad = sum(r['owner'] in ('faulty', 'DROP') for r in sel)
    mw = np.median([r['width'] for r in sel]); mh = np.median([r['height'] for r in sel])
    mr = np.median([r['width'] / r['height'] for r in sel]); mrc = np.median([r['width'] / r['height'] / r['chars'] for r in sel])
    w(f'| {t} | {cu[t]} | {100*cu[t]/120:.1f}% | {cs[t]} | {v["KEEP"]} / {v["DROP"]} / {v["UNCERTAIN"]} | {good} / {bad} | {mw:.0f}×{mh:.0f} | {mr:.2f} | {mrc:.2f} |')
w(f'| **total** | {len(uni)} | 100% | {len(sup)} | ' + ' / '.join(str(sum(r["verdict_05"] == k for r in typ)) for k in ('KEEP', 'DROP', 'UNCERTAIN')) +
  f' | {sum(r["owner"] in ("fine","KEEP") for r in typ)} / {sum(r["owner"] in ("faulty","DROP") for r in typ)} | | | |')
w('\n### Examples (3 per type; uniform sample first, then supplement)\n')
for t in ORDER:
    sel = [r for r in uni if r['type'] == t] + [r for r in sup if r['type'] == t]
    w(f'\n**{t}**\n')
    w('| line_id | population | crop_path | Google text | w×h | chars | 0.5 | owner | note |')
    w('|---|---|---|---|---|---:|---|---|---|')
    for r in sel[:3]:
        w(f'| {r["line_id"]} | {r["population"]} | `{r["crop_path"]}` | `{r["text"]}` | {r["width"]}×{r["height"]} | {r["chars"]} | {r["verdict_05"]} | {r["owner"] or ""} | {r["note"] or ""} |')
# owner false rejects by type
w('\n### Owner-good short non-numeric rows that 0.5 or 0.8 dropped, by type (150 + 888 rated rows in the 179)\n')
fr = Counter(r['type'] for r in typ if r['owner'] in ('fine', 'KEEP') and 'DROP' in (r['verdict_05'], r['verdict_08']))
w('| type | n |'); w('|---|---:|')
for t, n in fr.most_common():
    w(f'| {t} | {n} |')
(Path(sys.argv[2]) / '_typology_tables.md').write_text('\n'.join(o) + '\n')
print('\n'.join(o[:20])); print(fr)
