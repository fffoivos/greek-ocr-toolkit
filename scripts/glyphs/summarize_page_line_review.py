"""Build the committed round-2 development report from completed local audits."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / '.astra/out'
DOC = ROOT / 'docs/reviews/PAGE_LINES_ROUND2_20261009.md'
DATA = DOC.with_suffix('.json')


def main():
    test_log = (ROOT / '.astra/tests-final.log').read_text()
    matches = re.findall(r'(\d+) passed', test_log)
    assert matches and not re.search(r'\d+ failed', test_log), 'a complete passing test log is required'
    passed = int(matches[-1])
    rows = json.loads((OUT / 'checks.json').read_text())
    audit = json.loads((OUT / 'artifact_audit.json').read_text())
    curl = json.loads((OUT / 'curl_contacts.json').read_text())
    assert len(rows) == audit['pages'] == 48
    assert not audit['failures'], audit['failures']
    assert len({r['implementation_sha256'] for r in rows}) == 1
    fields = ['pixel_segments', 'final_lines', 'multi_line_segments', 'strip_edge_touch_lines', 'cut_ink_lines', 'foreign_ink_lines',
              'rule_gutter_crossings', 'boundary_overlaps', 'broken_line_pairs']
    totals = {k: sum(r[k] for r in rows) for k in fields}
    comparisons = [r['hint_comparison'] for r in rows if r['hint_comparison'] is not None]
    assert len(comparisons) == 24 and all(r['identical_pixel_geometry'] for r in comparisons)
    retained = 1 - sum(r['cut_assigned_ink_pixels'] for r in rows) / sum(r['assigned_ink_pixels'] for r in rows)
    data = dict(status='PARTIAL', pages=rows, totals=totals, artifact_audit=audit, curl_contacts=curl,
                assigned_ink_retained_fraction=retained, tests=dict(passed=passed, total=passed, log_sha256=hashlib.sha256(test_log.encode()).hexdigest()),
                assessment='Detection and ink purity remain incomplete; diagnostic ownership is not ground truth.')
    DATA.write_text(json.dumps(data, indent=2) + '\n')
    parts = ['# Page lines, round 2 — 9 October 2026', '',
             '**Status: PARTIAL.** Code, 48-page artifacts and audits are delivered; the clean one-line OCR acceptance test is not met on every real page.', '',
             'The pipeline starts with pixel regions bounded by rules and persistent gutters. The existing crop fitter finds all bands inside each region. Letter contacts are pooled into shared geometry; actual bottoms refine the fit so capital tops cannot pull it upward. Facing font lines define a shared midpoint boundary. Original pixels are unrolled with a fixed x-height position. Optional text-layer rectangles record provenance only.', '',
             'Implementation and measurement definitions: [PAGE_LINE_SEGMENTS.md](../PAGE_LINE_SEGMENTS.md). The original crop implementations are unchanged. The default Docling native-line path is unchanged; its opt-in detector path consumes these strips.', '',
             f'All **{passed:,}/{passed:,}** requested and added tests pass, including the frozen 40-crop set, curl set, provenance/API contracts and Docling contracts. The recognizer is mocked in integration tests. All **48** saved page sets pass the independent array/image audit. All **24** Vouli hint comparisons have exactly identical geometry.', '',
             f'Assigned component ink retained: **{retained:.3%}** over the development pages. This is not detection recall or OCR accuracy. Cut flags include ink excluded by a curved seam before whitening, even if white padding keeps the raster edge blank. Raw raster-edge counts and unassigned body-component counts are in the JSON.', '',
             '## Per-page checks', '',
             'Seg = pixel segments; Multi = segments referenced by more than one final line; Edge = dark ink touching the delivered top/bottom raster edge; Cut = source-boundary/window cuts or delivered raster-edge ink; Foreign = regions containing another line\'s assigned component; Cross = detected rule/gutter crossings; Overlap = positive region intersections; Broken = aligned disjoint pairs without a detected stop. Cut/Foreign/Broken are algorithmic diagnostics, not independent manual labels.', '',
             '| Page | Seg | Lines | Multi | Edge | Cut | Foreign | Cross | Overlap | Broken |',
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in rows:
        parts.append('| ' + r['key'] + ' | ' + ' | '.join(str(r[k]) for k in fields) + ' |')
    parts += ['| **Total** | ' + ' | '.join(str(totals[k]) for k in fields) + ' |', '',
              '## Independent curl contacts', '',
              'The frozen crop pixels were verified to match their registered locations on the page exactly. The nearest corresponding detected line is evaluated; this is a geometry check, not a detection-recall score.', '',
              '| Frozen crop | Covered contacts | Median error px | Maximum error px |',
              '|---|---:|---:|---:|']
    for r in curl['lines']:
        parts.append(f"| {r['crop']} | {r['covered_contacts']}/{r['contacts']} | {r['median_absolute_error_px']:.2f} | {r['max_absolute_error_px']:.2f} |")
    parts += ['', '## What remains wrong', '',
              '* `an-1f8e7d022643-p000003`: the ornamental title border still produces false text bands. Decorative initials can also lose part of their extent.',
              '* `an-d6002cf45e4d-p000058`: some engraving details still receive lines; illustration rejection is incomplete.',
              '* `an-778126cc8c2b-p000010` and `an-ef481610a820-p000181`: bleed-through, staining and stamps still confuse line identity and introduce extra bands.',
              '* `an-d83e7a198ade-p000099`: the small-type footnote columns are not separated reliably. Zero detected-stop crossings does not establish that every true column boundary was detected.',
              '* `an-7a2b17a3fb0f-p000200`, `s2-200e977f2dab5291c42c-p00035`, and `s2-831443dc5e6f1ccfbaf5-p00020`: table pieces remain imperfect; some small cells are missed or split and some neighbouring ink remains. No table structure is inferred.',
              '* `s2-09f5dfca4af4d74173c6-p00005`, `s2-0ce9d1025b3f23c7119e-p00001`, `s2-74cdb23a34ca4a6cd01e-p00002`, `s2-d1ed1c2db37f431f4acb-p00001`, and `s2-dfcc21869afc140111ce-p00001`: faint dense print still produces weak/extra bands. The measurements do not establish OCR-ready purity.',
              '* `an-ffccc97c07de-p000152`: connected Arabic-script words are less reliable than the Greek body text; some pieces are split or missed.',
              '* `s2-49598b2e848ab1f0ee1e-p00001`: the bottom-contact refinement improves the reviewed capital starts, but the left-end contacts of frozen crop 23 remain outside the crop tool\'s 6-pixel maximum-error criterion. The crop-level regression itself still passes unchanged.',
              '* Midpoint seams can cut tight accents/descenders. The output deliberately reports those pixels rather than concealing the problem with extra white padding or component erasure. Spatial lane IDs and reading order remain approximate in changing layouts.', '',
              'No held-out pages were inspected. The other OCR text in the optional hint files was not used as a reference. This round is a reproducible implementation and review result, not a claim that the clean-line goal is solved.', '',
              '## Artifacts and reproduction', '',
              'The 48 source-size overlays, fixed-scale unrolled sheets, pixel segment JSON, final line JSON and per-page checks are in `.astra/out/`. `artifact_audit.json` binds their hashes; `curl_contacts.json` binds the frozen contact audit. These large artifacts are local/ignored; this report and its companion JSON are part of the code handoff.', '',
              'Use the commands in `docs/PAGE_LINE_SEGMENTS.md`; all runs here used the brief\'s venv Python, `PYTHONDONTWRITEBYTECODE=1`, and pytest `-p no:cacheprovider`. No background job, network push or OCR model inference was launched.', '']
    DOC.write_text('\n'.join(parts))
    print(DOC.relative_to(ROOT), totals, 'retained', retained)


if __name__ == '__main__':
    main()
