"""Write the review receipt from frozen specs and the test run."""
import collections, hashlib, json
from pathlib import Path
from scripts.layout_paths import relocated
ROOT=Path(__file__).resolve().parents[2]
D=relocated(ROOT/'docs/owner_sheets')
NAMES=['failure_modes_per_class','segmentation_failures']
def main():
    specs={n:json.loads((D/n/'spec.json').read_text()) for n in NAMES}
    hashes=json.loads((D/'input_sha256.json').read_text())
    receipt=json.loads((ROOT/'artifacts/owner_sheets/qa/test_results.json').read_text())
    a,b=[specs[n] for n in NAMES]
    sizes=[(ROOT/'artifacts/owner_sheets'/f'{n}.html').stat().st_size/1_000_000 for n in NAMES]
    last=f"OS1 READY: A cards {len(a['lines'])} (sections 10, subsections {len(a['groups'])}, gaps {sum('gap' in g for g in a['groups'])}); B cards {len(b['lines'])} (groups 6); size A {sizes[0]:.2f} MB, B {sizes[1]:.2f} MB; tests {receipt['passed']} passed"
    out=['# OS1 owner-sheet receipt','',
         'Both self-contained HTML sheets are produced by `greekocr.adjudicate.owner_sheet.render` and its packaged CSS/JS. No network calls, input edits, or `.git` writes were used. Sheet A was built first. Sizes below use decimal MB.','',
         'Rebuild with the specified Python: `python scripts/review/build_failure_modes_per_class.py` and `python scripts/review/build_segmentation_failures.py`. Selection regeneration: `PYTHONPATH=. python scripts/review/prepare_os1_specs.py`. Selection uses seed 20261017, explicit fault-to-checker-evidence candidate pools in that script, sorted IDs, and seeded shuffling. Scarce pools are allocated first to keep one card and one note document per line within each sheet. Each subsection takes up to three examples. The specs freeze the selected IDs and every candidate pool.','',
         'T6b location: the collect-v3 SG1 `build_gallery.py` points to the actual verdict directory in the sibling checkout: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/`. The six main verdict files and three corresponding `cards/*_key.json` files for Gazette, kosmopolis and lekythos are bound below. The requested collect-v3 directory contains the pointer rather than those verdict files.','',
         '## Format conformance','',
         'Reference: `docs/records/labelfix/spellcheck/sheet_format_reference_v4.html`. Its static cards share `div.card`, image crops, `table.w` with named rows, `div.row` and `span.pill`. Both sheets use those same elements and class names through the standard renderer. The reference is stripped (its images contain `STRIPPED`) and does not itself contain line-ID, note, Printed-input, or magnifier markup. Those OS1 requirements use the existing renderer classes: `.lid`, `.notes[data-line]`, `.pr`, `.printed`, `.note`, `.nrow`, `.status`, `.zw`, `.lens`. There is one Google row and one editable Printed field in each card, one note textarea initialized with the checker detail, and doc ID exactly equal to the line ID. The existing runtime saves Printed and Note together and restores persisted values. The runtime tests exercise DB loading, edits and saving. No new card layout or summary strips were added.','',
         'The renderer gained data-driven section/subsection headings and initial note text; existing card structure and CSS/JS are retained. One header paragraph appears at the top of each sheet; each A section has one header block. Images use proportional `height:auto`; every crop has the standard hover lens. B strips use `.zoomrow` / `.zoom`. All image data is embedded; no external assets are loaded. Owner-facing text contains no model names or question-mark placeholders. One uncertain checker glyph placeholder in B was expanded from `?` to `[uncertain]`; its exact original detail remains in spec provenance.','',
         '## Evidence and limits','',
         'Printed is populated only when a source supplies a complete print, or every clause of its checker detail can be applied as an exact unique substitution to the full Google label. It is empty for incomplete, uncertain, or non-substitutable details. Each card records the rule used in `provenance.printed_basis`. This is reconstruction from existing adjudication, not a new transcription.','',
         'Some checked crop PNGs are absent from the requested W1 crop directory. They were reconstructed locally from cached page rasters and recorded crop bounds, without resizing, rotation, masking, or recutting. Reconstructed PNG bytes do not match the historical crop hashes; the report does not claim original-byte parity. Tests establish equality to the cached raster at the recorded bounds. Both historical and recovered hashes are retained in spec provenance. T6b checker detail refers to its masked-card audit, while the displayed crop is the original W1 Google geometry as requested.','',
         'The cross-cutting character rows are not extra class sections: A mirrors the nine coordinator class tables, splitting the Cyrillic fault rows into Russian and Serbian, giving ten sections and forty subsections. Prose examples also illustrate capital faults; Greek words in mixed-script lines can illustrate the same Greek mark faults. The original stratum is recoverable from each card key and candidate mapping.','',
         'The 19% figure is copied from the coordinator. Current `counts.json` identifies the underlying pilot as 501 missed admitted boxes among 2,624 printed rows (19.09298780487805%), with archived visual adjudication and admitted-box scope; it is not a census of absence from all raw boxes. C1 and T6b overrun rates are unpaired samples with different admission mixes, so the header makes no causal masking-fix claim.','',
         '## Sheet A: Failure modes per class','',f"Cards: {len(a['lines'])}; sections: 10; subsections: {len(a['groups'])}; gaps: {sum('gap' in g for g in a['groups'])}; Printed prefilled: {sum(bool(c['printed']) for c in a['lines'])}.",'']
    for section in a['sections']:
        lines=[c for c in a['lines'] if any(c['group']==g['id'] for g in a['groups'] if g['section']==section['id'])]
        out += [f"### {section['heading']} — {len(lines)} cards",'',section['header'],'']
        for g in [g for g in a['groups'] if g['section']==section['id']]:
            ids=[c['line_id'] for c in a['lines'] if c['group']==g['id']]
            out += [f"- **{g['heading']}**: {len(ids)} cards; {g['candidate_count']} matching checked candidates." + (f" Gap: {g['gap']}." if 'gap' in g else '')]
            out += [f"  - `{lid}`" for lid in ids]
        out.append('')
    out += ['## Sheet B: Segmentation failures','',
            'C1 selection contains all eight merged witnesses: seven `merged_two_lines` tags plus probe c098, whose detail explicitly says a full previous line is inside the crop. Four fragment witnesses use SG1’s existing classification; that classification is a crop-clipped witness, without an independent annotation of full printed-row extent. The five clipped cards are the five Gazette C1 clipped witnesses. Probe c053 is also merged and appears once in the merged group with an additional clipped pill. The column card is ELSTAT c068. Twelve overruns are seeded and spread round-robin across strata. Four rotated Gazette crops have height greater than width. All 24 SG1 examples remain present.','',
            'After line-ID deduplication the six primary groups contain:','']
    for g in b['groups']:
        lines=[c for c in b['lines'] if c['group']==g['id']]
        out += [f"### {g['heading']} — {len(lines)} cards",'']+[f"- `{c['line_id']}`" for c in lines]+['']
    out += [f"All {len(b['lines'])} B cards have page strips. Gaps: none in crop/strip availability after local recovery. Four rotated cards are verified by native image dimensions. B includes 24 SG1 cards; remaining cards are C1 additions.",'',
            'The seventh `missing_box` group is a disabled data hook in B’s spec. Although the current examples file now includes three SG2 records, OS1 explicitly excludes that group, so none were built. Enabling it requires a separate scope decision and page-strip evidence of the stated absent-box scope.','',
            '## Crop recovery ledger','']
    for name,s in specs.items():
        recovered=[c for c in s['lines'] if c['provenance'].get('crop',{}).get('reconstructed')]
        out += [f"### {name}: {len(recovered)} reconstructed crops",'']
        for c in recovered:
            p=c['provenance']['crop']
            out += [f"- `{c['line_id']}`; bounds `{p['bbox']}`; historical `{p['expected_sha256']}`; recovered `{p['recovered_sha256']}`; page `{p['page']}`"]
        out.append('')
    out += ['## Inputs and SHA-256','',
            'The following shared source ledger covers both sheets. Per-card verdict/key/crop/page paths in each spec bind individual cards to this ledger; A additionally uses the coordinator, aggregate results and yer table, while B additionally uses SG1 examples, strips and counts. Local recovered crops are identified above; generated strips are derived outputs rather than source inputs. The ledger is also machine-readable in `docs/records/owner_sheets/input_sha256.json`.','',
            '| Path | SHA-256 |','| --- | --- |']
    for p,h in sorted(hashes.items()):out.append(f'| `{p}` | `{h}` |')
    out += ['','### Renderer and frozen artifacts','', '| Path | SHA-256 |','| --- | --- |']
    for p in [ROOT/'docs/records/labelfix/spellcheck/sheet_format_reference_v4.html',ROOT/'greekocr/adjudicate/owner_sheet.py',ROOT/'greekocr/adjudicate/owner_sheet.css',ROOT/'greekocr/adjudicate/owner_sheet.js']+[D/n/'spec.json' for n in NAMES]+[ROOT/'artifacts/owner_sheets'/f'{n}.html' for n in NAMES]:
        out.append(f"| `{p.relative_to(ROOT)}` | `{hashlib.sha256(p.read_bytes()).hexdigest()}` |")
    out += ['','## Validation','',
            f"`{receipt['command']}`: **{receipt['passed']} passed**. Test output: `artifacts/owner_sheets/qa/pytest.txt`. Checks cover exact re-rendering, card/spec counts, note identity, checker-detail text, printed prefill, embedded-image decoding, all image paths, reference class conformance, class/fault/rate fidelity, gap labels, selection counts, SG1 preservation, six-group order, all B strips, rotated dimensions, input hashes and recovered raster pixels. Existing adjudication and JavaScript runtime tests pass.",'',
            'Live browser screenshot QA was attempted offline but unavailable: the installed Playwright package expects uncached browser revisions, and system Chrome terminates during sandboxed launch. No browser download or network fallback was used. Visible browser layout and live signed-in DB operation are therefore not claimed. The shipped CSS and runtime acceptance checks remain the format and interaction evidence.','',last]
    (D/'OS1_REPORT.md').write_text('\n'.join(out)+'\n')
    print(last)
if __name__=='__main__':main()
