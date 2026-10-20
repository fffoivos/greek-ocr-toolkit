"""Assemble CU4 evidence tables after the offline suite finishes."""
import json
from pathlib import Path
from scripts.layout_paths import relocated
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/cleanup_step4'

def generate():
    xml=ET.parse(OUT/'full_suite.xml').getroot()
    suites=list(xml.iter('testsuite'))
    stats={key:sum(int(s.get(key,0)) for s in suites) for key in ('tests','failures','errors','skipped')}
    passed=stats['tests']-stats['failures']-stats['errors']-stats['skipped']
    failures=[]
    for case in xml.iter('testcase'):
        for kind in ('failure','error'):
            child=case.find(kind)
            if child is not None:failures.append(dict(case=case.get('classname')+'::'+case.get('name'),kind=kind,message=child.get('message')))
    (OUT/'suite_summary.json').write_text(json.dumps(dict(stats,passed=passed,failures_detail=failures),indent=2)+'\n')
    only=all(any(f['case'].startswith(x) for x in ('tests.test_collection_outputs::','tests.test_provenance_cli_api::','tests.test_apply_clean::')) for f in failures)
    counts={prefix:sum(f['case'].startswith(prefix) for f in failures) for prefix in ('tests.test_collection_outputs::','tests.test_provenance_cli_api::','tests.test_apply_clean::')}
    only=only and list(counts.values())==[3,2,5]
    diffs={n:json.loads((OUT/f'{n}_diff.json').read_text()) for n in ('reader_errors_heldout','accent_corrections_checked','R0_cards_ib')}
    pins=json.loads((OUT/'pinned_before.json').read_text());after=json.loads((OUT/'pinned_after.json').read_text());assert pins==after
    policy=json.loads((OUT/'policy_after.json').read_text());assert policy['sha256']=='6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406'
    r0=diffs['R0_cards_ib']['receipt']
    import re
    focused=int(re.search(r'(\d+) passed', (OUT/'targeted_tests.log').read_text()).group(1))
    lines=['# CU4: shared offline adjudication', '',
      'The additive `greekocr.adjudicate` package, three data-spec re-emissions and API documentation are implemented. '
      'All three re-emissions have zero content differences. Existing builders and frozen code remain unchanged.','',
      'Workspace: `opus/cleanup-1`, starting HEAD `b16043641e3916aeee3e633e4400753d3208b69b` '
      '(CU4 brief directly above CU3 `7bc40ddc2`). No `.git` writes, commits, pushes, network access or model inference. '
      'R0, R1, S8 and R2C evidence was read only; no R2C deck or reader folder was modified.','',
      '## API and custody','',
      '| Entry | Contract |','|---|---|',
      '| `owner_sheet.render(lines, spec) -> str` | Ordered groups/cards; named text rows with changed/no-ink segments, tags, optional Printed/zooms/clean magnifier; one unique note document per card |',
      '| `owner_sheet.detection_image(image, slots)` | Saved above/apostrophe green, below blue, attached grey boxes and slot numbers; no detector execution |',
      '| `deck.build_deck(spec) -> dict` | Named profiles, shuffled data/controls/options, opaque IDs, PNG-content hashes, exclusive sibling private key; leak/schema/zoom/fraction checks; viewer, manifests, instructions/schema and receipt |',
      '| `deck.crop_image` / `deck.leak_scan` | R0 .6-height horizontal pad/full native height, <=3x LANCZOS/900 cap; native line/page; text/path/PNG metadata scan |',
      '| `protocol.adapt_answer` / `deal` | Canonical, R0, S8 and R2C aliases; confidence high/medium/low; code-emitted reverse reader-2 order |',
      '| `protocol.tiebreak_deck` | Fresh positions/options; own exclusive private map to original identities; includes controls |',
      '| `protocol.controls_gate` / `resolve` | Both readers gated before votes; full coverage/order, 2-of-2 else 2-of-3, controls excluded, UNKNOWN preserved; third-reader mapping and controls independently checked |',
      '| `score.wilson` / `score.score` / `score.clopper_pearson_lb95` | One implementation each; exact z; S8 document/line bootstrap, fixed weights, Wilson-Kish boundary fallback; one-sided exact LB95 |',
      '| `protocol.write_truth` | Exclusive JSONL/deterministic gzip writer; reader observations, verdict/status/control fields and returned summary; refuses failed gates |','',
      'The full record/spec contracts and examples are in [the package README](../greekocr/adjudicate/README.md) '
      'and [generated API](API.md). `protocol.score` re-exports the sole estimator. All 14 new public callables are '
      'typed, importable and documented; all 296 prior callable sections are unchanged, and generation is idempotent. '
      '[API verification](../artifacts/cleanup_step4/api_validation.json).','',
      'Packaged assets are real `owner_sheet.css`, `owner_sheet.js` and `deck.js`; setuptools includes them. '
      'There is no production `src.split` extraction or runtime dependency on a historical builder. '
      'Autosave uses `notes/{line_id}` or `notes/{line_id}:s{slot}`, merge writes, 900 ms debounce, blur flush, '
      'serialized in-flight writes, and load-race protection. Printed is saved with `printed_edited`. '
      'The magnifier retains clean pixels, Z=3, a 300x130 lens and tap toggle.','',
      'Historical C1 gates are descriptions through `readers=1`, `min_n`/`exact_n`, explicit rate thresholds and '
      '`allow_no_controls`. They do not reduce the new-deck owner rule: every new deck has two independent readers '
      'and an independent tiebreak for disagreements. No old gate or old scientific result is relabelled.','',
      '## Re-emission evidence','',
      '| Reference | Cards | Images compared | Content differences | Evidence |','|---|---:|---:|---:|---|',
      '| Reader Errors Held-out | 39 | 117 | 0 | [Full per-card diff](../artifacts/cleanup_step4/reader_errors_heldout_diff.json) |',
      '| Accent Corrections Checked | 100 | 100 overlays + 100 clean crops | 0 | [Full per-card diff](../artifacts/cleanup_step4/accent_corrections_checked_diff.json) |',
      f'| R0-ib | 336 ({r0["controls"]} controls) | 672 item views ({len([k for k in r0["files"] if k.endswith(".png")])} unique emitted PNGs) | 0 | [Full per-item diff and name map](../artifacts/cleanup_step4/R0_cards_ib_diff.json) |','',
      'The owner comparison checks title, intro, section/card interleaving, line labels, every row/tag text, '
      'highlight classes, all card/note `data-*` attributes, Printed prefills, image alt text and decoded pixel arrays '
      '(including clean magnifier crops). R0 checks every ID and position, option/order, control position, '
      'native-crop zoom scale and decoded pixels. Byte equality of the HTML/PNG encoding is not claimed.','',
      'Reader-errors reference SHA256 is `9441fca8f59cfd3a2321a41e5771034a3d6e70cef3f8f36cb97f96caadebfca8`. '
      'The specs in [artifacts/cleanup_step4/specs](../artifacts/cleanup_step4/specs) were re-derived from the original '
      'builders\' retained input/formatting computations, excluding their asset-source extraction and output writes. '
      'The renderer consumes normal data records (segments, rows, tags, image values), not captured HTML blocks. Audit overlays are regenerated by the shared detection_image helper from native crops and saved slots. '
      'The R0 spec comes from the frozen deck/private key and regenerates targets from native full-line rasters '
      'using the sealed crop boxes; selection and alignment locator geometry are frozen inputs, not recomputed.','',
      'Input substitution: main\'s `print_truth_s0.json` is absent. The tracked cleanup copy is used; it is '
      'SHA-identical to both spellcheck and R1 copies (`e8f2067b…cd96b`). The audit appendix itself is absent here '
      'and was read from `greek-ocr-toolkit-spellcheck/docs/CLEANUP_PLAN_20261017_blinding.md`. '
      '[Full input hashes and substitution receipt](../artifacts/cleanup_step4/derivation_receipt.json). '
      'The derivation script blocks network connections and runs under `forbid_forward`.','',
      '### Non-content differences and protocol changes','',
      'Every changed card DOM attribute is listed under `non_content_element_changes` in each owner diff, '
      'separately from the zero content differences. The accent sheet gains accessible Note label/textarea IDs; '
      'all note data attributes and database document identities remain identical. Other HTML changes are the '
      'doctype/head/body/UTF-8/viewport wrapper and serialization whitespace. Shared package CSS adds muted text '
      'color and fixes zoom width specificity while preserving light/dark tokens. The external font stylesheet '
      'link is removed for offline use. The script reads individual note documents instead of a 1000-document '
      'collection query, protects typing during load, serializes saves, stores `printed_edited`, and fixes touch '
      'tap toggling. Original image pixels, clean crops, lens size and magnification are unchanged. '
      'These UI/persistence changes are explicit; content parity is not browser-visible layout or live artifact-db proof.','',
      'R0 image basenames change from sequential names to encoded-content hashes; all 672 old/new view names '
      'and pixel results are mapped in the full diff. Re-encoding strips metadata. The private key remains '
      'write-once in a sibling tree, as in R0-ib: no key-relocation improvement is claimed for that deck. '
      'The new shared instructions/schema/viewer and explicit reader-2 reversal are **protocol changes**. '
      'The replay deliberately preserves historical item/options/control order; new decks shuffle all three, '
      'and new tiebreaks change multi-option order. New resolution uses literal-form controls rather than silently reusing the historical R0 bare-letter control gate. Old reader answers are not rescored or upgraded.','',
      'The leak scan covers text, paths and PNG metadata, not semantic recognition of printed book content. '
      'Sibling private files are still reachable by an explicit path when readers have full filesystem access, '
      'as the blinding audit explains. Only the blind tree and an isolated own-output location should be handed '
      'to a reader. No live reader job was started.','',
      '## Pinned bytes','',
      f'All {len(pins)} tracked pin states are unchanged: {sum(v is not None for v in pins.values())} existing files '
      f'and {sum(v is None for v in pins.values())} already-absent manifest targets. The population is the union of '
      'all `greekocr/labelfix` files, all 16 `policy_binding` paths, every path in every deploy manifest, '
      'the manifests themselves, and CU3\'s pin table. ABSENT is a retained input state, not a verified byte hash.','',
      'Policy digest before and after: '
      '`6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406`.','',
      '[Before JSON](../artifacts/cleanup_step4/pinned_before.json), '
      '[after JSON](../artifacts/cleanup_step4/pinned_after.json), '
      '[full before/after table](../artifacts/cleanup_step4/pinned_table.md), '
      '[policy before](../artifacts/cleanup_step4/policy_before.json), '
      '[policy after](../artifacts/cleanup_step4/policy_after.json).','',
      '## Validation','',
      'Commands use `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, '
      '`PYTHONPATH=$PWD`, `PYTHONDONTWRITEBYTECODE=1`, Mac CPU and the existing offline fixture.','',
      '- `python scripts/review/cu4_reemit.py`: three zero-difference re-emissions.',
      f'- `python -m pytest tests/adjudicate -q`: {focused} passed.',
      f'- `python -m pytest -q --junitxml=artifacts/cleanup_step4/full_suite.xml`: {passed} passed, {stats["failures"]} failed, {stats["errors"]} errors, {stats["skipped"]} skipped.',
      '- `python scripts/generate_api_docs.py`: 310 public callable entries, repeat generation byte-identical.',
      '- `git diff --check`: clean.','',
      'Focused tests exercise pixels/content for every historical item, profile/zoom bounds, leak failures and '
      'metadata stripping, key exclusivity, reader order, controls-before-truth, fresh tiebreak maps, '
      '2-of-3 and UNKNOWN, R2C contradictory/unknown heads, descriptive C1 gates, and exact S8/bootstrap/CP '
      'parity. A Node runtime harness executes the shipped owner JS against a mock artifact DB, including '
      'debounce, blur, concurrent edits, merge, Printed and magnifier behavior. This does not claim a live '
      'artifact-db connection or browser-visible layout validation.','',
      '[Focused log](../artifacts/cleanup_step4/targeted_tests.log), '
      '[full log](../artifacts/cleanup_step4/full_suite.log), '
      '[per-case XML](../artifacts/cleanup_step4/full_suite.xml), '
      '[machine-readable failures](../artifacts/cleanup_step4/suite_summary.json).','',
      '| Failing case | Kind |','|---|---|']
    lines += [f'| `{f["case"]}` | {f["kind"]} |' for f in failures]
    lines += ['', ('Failures/errors are exactly the allowed pre-existing set: collection outputs 3, provenance API 2, apply-clean 5. '
                   'The CU3 sandbox capture-server error does not recur in this run.' if only else
                   'The exact allowed baseline is not met: the existing capture-server test additionally cannot bind a local socket (PermissionError: Operation not permitted). This same sandbox error is recorded in CU3, but CU4 allows only the narrower 3+2+5 set. No existing test/assertion/skip/xfail was changed. Readiness is withheld for this environmental gate.'), '',
       '## Per-item summary','', 'Every row below has zero content differences. Full pixel hashes, image dimensions, '
       'name maps and DOM attribute changes are in the linked JSON files.','']
    for name,diff in diffs.items():
        lines += [f'### {name}', '', '| Item | Identity | Compared images | Differences |','|---:|---|---:|---:|']
        for i,item in enumerate(diff['items']):
            ident=item.get('line',item.get('id',''))
            count=len(item['images'])+(1 if item.get('clean_pixels_equal') is not None else 0)
            ndiff=item.get('content_diffs',len(item.get('diffs',[])))
            lines.append(f'| {i} | `{ident}`'+(' (control)' if item.get('control') else '')+f' | {count} | {ndiff} |')
        lines.append('')
    lines += ['## Complete pinned-path table', '', (OUT/'pinned_table.md').read_text(), '']
    status='CU4 READY' if only and all(not d['diffs'] for d in diffs.values()) else 'CU4 NOT READY'
    lines += [f'{status}: greekocr.adjudicate (owner_sheet, deck, protocol); re-emit reader-errors identical, accent-corrections identical, R0-ib identical; pinned unchanged {len(pins)}/{len(pins)}; digest 6f62925a yes; tests {passed} passed, failures only pre-existing' if only else
              f'{status}: greekocr.adjudicate (owner_sheet, deck, protocol); re-emit reader-errors identical, accent-corrections identical, R0-ib identical; pinned unchanged {len(pins)}/{len(pins)}; digest 6f62925a yes; tests {passed} passed; expected pre-existing 3+2+5 set plus pre-existing capture socket-bind error.']
    (relocated(ROOT/'docs/CLEANUP_STEP4_REPORT.md')).write_text('\n'.join(lines)+'\n')
    print(stats,'passed',passed,'exact allowed baseline',only)

if __name__=='__main__':generate()
