"""Bounded regression/report audit for round four's opt-in orientation path."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import shutil
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as ndi

ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from scripts.glyphs.archive.audit_tables_round4 import metrics
from scripts.glyphs.archive.evaluate_tables_round4 import geometry,intersect,area

OUT=ROOT/'.astra/out';OLD=ROOT/'.astra/previous_round4_part2';ACCEPT=OUT/'orientation-acceptance'


def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def element_coverages(annotation,records,ink):
    """Retain exact coverage even above 98%; a passing element is not 100%."""
    rows=[]
    for table in annotation['tables']:
        own=[p for p in records if intersect(p['box_pixels'],table['extent'])/max(1,area(p['box_pixels']))>.8]
        for cell in table['cells']:
            if cell['empty']:continue
            for element in cell['text_elements']:
                a,t,b,bot=map(int,element['box']);target=ink[t:bot,a:b];mask=np.zeros_like(target)
                for piece in own:
                    x,y,r,d=map(int,piece['box_pixels'])
                    if intersect((a,t,b,bot),(x,y,r,d)):
                        mask[max(0,y-t):min(bot,d)-t,max(0,x-a):min(b,r)-a]=True
                rows.append(dict(table=table['id'],cell=cell['id'],element=element['id'],box=element['box'],
                                 coverage=float((mask&target).sum()/max(1,target.sum()))))
    return rows


def real_case_image(key):
    """New output only: annotated source crops plus its current full-page view."""
    page=Image.open(ROOT/'.astra/pages'/f'{key}.png').convert('RGB')
    words=read(OUT/f'{key}.words.json')['words']
    rois=[('Title: expected CW270',(180,487,320,1907)),
          ('Header: expected CW180',(1270,3922,1530,4037)),
          ('Folio: upright / ambiguous',(1610,187,1810,297)),
          ('Number rows: expected CW270',(1710,390,2390,1180))]
    canvas=Image.new('RGB',(1700,1900),'white');d=ImageDraw.Draw(canvas)
    full=Image.open(OUT/f'{key}.orientation.jpg');full.thumbnail((1200,1840));canvas.paste(full,(20,40))
    d.text((20,15),'Case 35 - current oriented words (not a certified transcription)',fill='black')
    y=55
    for title,box in rois:
        crop=page.crop(box);draw=ImageDraw.Draw(crop)
        for w in words:
            b=w['box_pixels']
            if max(box[0],b[0])>=min(box[2],b[2]) or max(box[1],b[1])>=min(box[3],b[3]):continue
            points=[(p[0]-box[0],p[1]-box[1]) for p in w['corners_pixels']]
            draw.line(points+[points[0]],fill='red' if w['orientation_cw'] is not None else 'gray',width=2)
        if crop.height>2*crop.width:crop=crop.rotate(270,expand=True)
        crop.thumbnail((450,380));d.text((1225,y),title,fill='black');canvas.paste(crop,(1225,y+25));y+=crop.height+70
    path=OUT/'cases/r3-case-35-orientation.jpg';path.parent.mkdir(exist_ok=True);canvas.save(path,quality=93)
    return path


def main():
    keys=sorted(p.stem for p in (ROOT/'.astra/pages').glob('*.png'))
    assert len(keys)==54
    artifact_audit=read(OUT/'orientation-artifact-audit.json')
    assert artifact_audit['passed'] and artifact_audit['pages']==94
    preserved_receipts=[]
    for directory in ('acceptance','integration'):
        for path in sorted((OLD/directory).rglob('*')):
            if path.is_file():
                current=OUT/path.relative_to(OLD)
                assert current.is_file() and sha(path)==sha(current),str(current)
                preserved_receipts.append(dict(path=str(current.relative_to(ROOT)),sha256=sha(current)))
    rows=[]
    for key in keys:
        before=read(OLD/f'{key}.checks.json');after=read(OUT/f'{key}.checks.json')
        oldlines=read(OLD/f'{key}.lines.json');newlines=read(OUT/f'{key}.lines.json')
        oldmetrics,newmetrics=metrics(before,oldlines),metrics(after,newlines)
        worse={k:dict(old=v,new=newmetrics[k]) for k,v in oldmetrics.items() if newmetrics[k]>v+1e-10}
        words=read(OUT/f'{key}.words.json');values=words['words']
        # Every output links to the unchanged source image, not a truth label.
        assert words['source_sha256']==sha(ROOT/'.astra/pages'/f'{key}.png')
        assert len({w['word_id'] for w in values})==len(values)
        assert all(np.isfinite(w['corners_pixels']).all() for w in values)
        oldcells=read(OLD/f'{key}.cells.json')['cells'];newcells=read(OUT/f'{key}.cells.json')['cells']
        local=read(OUT/f'{key}.oriented.lines.json')
        localchecks=read(OUT/f'{key}.oriented.checks.json')
        localmetrics=metrics(localchecks,local['lines'])
        localworse={k:dict(old=v,new=localmetrics[k]) for k,v in oldmetrics.items() if localmetrics[k]>v+1e-10}
        rows.append(dict(key=key,lines_exact=oldlines==newlines,checks_exact=before==after,
                         compatibility_cells_exact=oldcells==newcells,old=oldmetrics,current=newmetrics,
                         compatibility_worsened=worse,oriented_main_frame_worsened=localworse,
                         oriented_main_frame_cw=words['groups'][0]['orientation_cw'],
                         words=len(values),accepted=sum(w['orientation_cw'] is not None for w in values),
                         orientation_counts={str(a):sum(w['orientation_cw']==a for w in values) for a in (0,90,180,270,None)},
                         recognized=sum(bool(w['text'].strip()) for w in values),
                         word_sha256=sha(OUT/f'{key}.words.json')))
        # One new-output image for every page case. No discounted lines appear.
        shutil.copyfile(OUT/f'{key}.orientation.jpg',OUT/'cases'/f'orientation-{key}.jpg')
    table_rows=[]
    old_accept=read(OLD/'acceptance/summary.json')
    for path in sorted((ROOT/'docs/records/tables/annotations').glob('*.json')):
        ann=read(path);key=path.stem
        image=Image.open(ROOT/'.astra/pages'/f'{key}.png')
        records=read(OUT/f'{key}.words.json')['words']
        geo=geometry(ann,records,image)
        old=old_accept[key]['geometry']
        gray=np.asarray(image.convert('L'));bg=ndi.maximum_filter(gray,size=max(3,round(.015*min(gray.shape))))
        ink=bg.astype(float)-gray>30
        previous=element_coverages(ann,read(OLD/f'{key}.cells.json')['cells'],ink)
        current=element_coverages(ann,records,ink)
        assert sum(r['coverage']>=.98 for r in previous)==sum(t['complete'] for t in old['tables'])
        assert sum(r['coverage']>=.98 for r in current)==sum(t['complete'] for t in geo['tables'])
        oldcoverage={(r['table'],r['cell'],r['element']):r['coverage'] for r in previous}
        pairs=[dict(**r,old_coverage=oldcoverage[(r['table'],r['cell'],r['element'])]) for r in current]
        losses=[r for r in pairs if r['coverage']<r['old_coverage']-1e-10]
        table_rows.append(dict(key=key,old_complete=sum(t['complete'] for t in old['tables']),
            oriented_complete=sum(t['complete'] for t in geo['tables']),total=sum(t['elements'] for t in geo['tables']),
            old_crossings=len(old['crossing_pieces']),oriented_crossings=len(geo['crossing_pieces']),
            element_coverage_regressions=losses,element_coverage_pairs=pairs,geometry=geo,
            passed=not losses and len(geo['crossing_pieces'])<=len(old['crossing_pieces'])))
    realkey='s2-6419488b7f8e69fd20da-p00001';casepath=real_case_image(realkey)
    gates=read(ACCEPT/'gates.json');pipeline=read(ACCEPT/'pipeline.json')
    rotated=sorted((OUT/'rotated').glob('*.words.json'));assert len(rotated)==40
    for path in rotated:
        r=read(path)
        assert all(np.isfinite(w['corners_pixels']).all() for w in r['words'])
    suite=ET.parse(ROOT/'.astra/orientation-tests-final.xml').getroot();s=suite.find('testsuite')
    test_counts={k:int(s.attrib[k]) for k in ('tests','failures','errors','skipped')}
    test_counts['passed']=test_counts['tests']-sum(test_counts[k] for k in ('failures','errors','skipped'))
    attempt=ROOT/'.astra/orientation-commit-attempt.json'
    commit=read(attempt) if attempt.exists() else dict(committed=False,reason='Commit attempt pending; see final delivery message.')
    report=dict(base_commit='f611ee2',result='PARTIAL',gates=gates,tests=test_counts,pages=rows,tables=table_rows,commit=commit,
        artifact_audit='../../.astra/out/orientation-artifact-audit.json',preserved_part2_acceptance_receipts=preserved_receipts,
        rotated_outputs=len(rotated),pipeline=pipeline,compatibility_preserved=all(r['lines_exact'] and r['checks_exact'] and r['compatibility_cells_exact'] for r in rows),
        input_scope='54 supplied development PNGs and fixed research fixtures; no held-out pages',
        research_source='.astra/orientation_research/REPORT.md (requested docs/records/research/ORIENTATION_20261009.md absent)',
        implementation={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'greekocr/glyphs/orientation.py',ROOT/'greekocr/glyphs/oriented_page.py',ROOT/'greekocr/deploy/docling_plugin/orientation.py',ROOT/'greekocr/deploy/docling_plugin/model.py']})
    target=ROOT/'docs/records/reviews/PAGE_LINES_ROUND4_ORIENTATION_20261009.json'
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    lines=['# Page lines round 4, part 3: orientation — 9 October 2026','',
      '## Case 35: the real sideways table','',
      '**Partial result.** The new path finds the dominant clockwise 270° writing, normalizes local views, and maps ordered word corners and guide samples back to the source page. The full Docling conversion succeeds and the adapted table is 8×15 with `Table.orientation=rot_90` (CCW). This is not a claim that its real grid or text is correct. The title and perpendicular headers remain incompletely segmented; the folio is absent in blind output.','',
      '| Part of page | Measured result | Status |','|---|---|---|',
      '| Title | The standalone crop has the correct vertical axis but abstains between 90/270. The full-page words inherit 270° from the block; most title letters are still missed or fragmented. | Not fixed |',
      '| «Καπνοῦ» | Oracle crop selects 180°; recognition is `Καπνο͂`, not an exact transcription. Blind discovery finds a 180° region, but its word crops are incomplete. | Orientation improved; word recovery not fixed |',
      '| Folio | Oracle crop abstains with alternatives 0/180; blind output misses the folio. | Not fixed |',
      '| Number rows | Most emitted numeric pieces inherit 270°; they are recognized in horizontal local views. Some digits remain split or omitted; no numeric transcription accuracy is claimed. | Improved axis handling; incomplete |',
      '| Table | Actual Heron → oriented OCR → adapted Accurate V1 → reading order: SUCCESS, 8×15, `rot_90`. Image and tokens rotate together. | Adapter works; real structure not certified |','',
      f'[Current case image](../../.astra/out/cases/{casepath.name}) · [actual pipeline receipt](../../.astra/out/orientation-acceptance/{realkey}.pipeline.json) · [document](../../.astra/out/orientation-acceptance/{realkey}.document.json)','',
      '## Research acceptance gate','',
      'The specification was read in full from `.astra/orientation_research/REPORT.md`; the requested `docs/records/research/ORIENTATION_20261009.md` was not present. Fixtures were SHA-256 verified against the supplied manifest. No fixture was regenerated or altered. `evaluate_orientation_round4.py --require-gate` enforces the gate independently of unit-test success.','',
      '| Gate | This implementation | Result |','|---|---|---|']
    for g in gates['gates']:
        numbers=g['numbers']
        if g['gate']=='pipeline stage ordering':
            detail='Both conversions SUCCESS; normalize → layout → OCR → table verified. Uniform-page normalization incorrectly vetoed as mixed.'
        else:
            detail='; '.join(f'{k}: {v}' for k,v in numbers.items())
        lines.append(f"| {g['gate']} | {detail} | {'PASS' if g['passed'] else '**FAIL / incomplete**'} |")
    lines+=['',
      'Whole-page accepted-polarity coverage is reported separately from axis accuracy. Unknown is never counted as a correct polarity. Skew is recorded separately; these tests do not certify deskew-angle accuracy. The 40 fitter comparisons use the labelled upright normalization to isolate the fitter, with only byte-identical normalized rasters sharing a fit (10 fresh fits). They do not certify the automatic direction decision.','',
      'The word fallback uses the plugin’s supported **compact** recognizer, `t1_compact_nfd_s0/best.safetensors`, bound to the packaged v1 codec. The newer local A32 checkpoint is not supported by this plugin’s frozen architecture registry and was not substituted. Crop preparation removes uniform external canvas before estimating grey paper/ink, normalizes contrast, then pads by 0.1 body heights, matching the recognizer’s documented ink-height policy. Both axis-consistent readings and scores are preserved. Thresholds are conservative evidence margins, **not calibrated probabilities**; production calibration remains undone.','',
      'Blind discovery uses component neighbours and rule exclusion before any horizontal fit. Its union IoU and threshold-ink coverage are scored only afterward using the fixed ROI. These are not manually annotated word precision/recall. Remaining proposals outside inserted regions and missed faint units are retained in `blind.json`.','',
      '## Code and invocation','',
      '- `greekocr/glyphs/orientation.py`: quarter-turn frames, axis/skew evidence, block polarity, optional Tesseract OSD, recognizer two-reading fallback, consistent word crops, and blind chains in both axes.',
      '- `greekocr/glyphs/oriented_page.py`: horizontal fitting in local views, within-piece word splitting, separately addressable word IDs, and inverse-mapped corners and parametric guides.',
      '- `greekocr/deploy/docling_plugin/orientation.py`: coherent backend adapter before layout; table-stage wrapper rotates page image/table bounds/tokens together and maps cells back while retaining logical rows/columns.',
      '- `GlossapiOcrOptions(recognition_mode="oriented")` selects the experimental word output. Use `ImageFormatOption(pipeline_cls=OrientationPdfPipeline, pipeline_options=options)` (or the corresponding PDF format option). An OCR entry point alone cannot normalize before layout.',
      '- Every emitted Greek TextCell has `from_ocr=True`, ordered BL/BR/TR/TL corners, and `TextDirection.LEFT_TO_RIGHT`. OCR confidence is independent of orientation confidence. Unknown cells retain alternatives and an explicitly labelled geometry hypothesis. Unknown words do not vote for table rotation. Native cached words/chars are cleared.',
      '- `textlayer` and `detector` compatibility modes are unchanged. Because the acceptance gate fails, **oriented mode is opt-in and is not promoted as a replacement for part 2**.','',
      '## All 54 pages against part 2','',
      '**The compatibility detector’s 54 line/check records and all delivered cell records are unchanged.** Existing outputs were preserved before work in `.astra/previous_round4_part2`. New recognized orientation output is in `<key>.words.json` and `<key>.orientation.jpg`; local main-frame lines/checks are in `<key>.oriented.lines.json` and `<key>.oriented.checks.json`. `cells.json` links to the opt-in word output. Thus the following compatibility preservation is not evidence that the new word path has no regressions. Local replacement groups are not counted by the old horizontal diagnostics.','',
      'C/F/X/O/B = cuts / foreign ink / rule crossings / overlaps / broken pairs. Each old→new pair compares the part-2 compatibility output. Every changed main-frame metric in the opt-in path is listed afterward. Each page links to its new-output case image: green 0°, blue 90°, purple 180°, orange 270°, grey unknown. Arrows mark the proposed reading direction.','',
      '| Page | Part-2 C/F/X/O/B → current | Exact lines/checks/cells | New words / accepted orientation | Compatibility worse? |',
      '|---|---|---|---:|---|']
    fields=['cut_ink_lines','foreign_ink_lines','rule_gutter_crossings','boundary_overlaps','broken_line_pairs']
    for r in rows:
        a='/'.join(str(r['old'][k]) for k in fields);b='/'.join(str(r['current'][k]) for k in fields)
        exact='/'.join('yes' if r[k] else 'NO' for k in ('lines_exact','checks_exact','compatibility_cells_exact'))
        lines.append(f"| [{r['key']}](../../.astra/out/cases/orientation-{r['key']}.jpg) | {a} → {b} | {exact} | {r['words']} / {r['accepted']} | {'YES' if r['compatibility_worsened'] else 'No'} |")
    lines+=['','### Every main-frame increase in the opt-in orientation path','',
            'These main-frame counts exclude the additional locally replaced groups. A rotated frame changes the diagnostic denominator; increases are still disclosed.']
    for r in rows:
        if r['oriented_main_frame_worsened']:
            lines.append('- `'+r['key']+'`: '+', '.join(f"{k} {v['old']} → {v['new']}" for k,v in r['oriented_main_frame_worsened'].items())+'.')
    if not any(r['oriented_main_frame_worsened'] for r in rows):lines.append('No main-frame increases.')
    lines+=['','## Eight table pages: new words versus part-2 acceptance geometry','',
      'The part-1/part-2 acceptance and pipeline receipts remain unchanged for compatibility mode. The new word path is measured separately below with the same provisional annotations and ≥98% contrast-ink coverage definition. **It does not meet the no-regression requirement.** Full new-path final-grid ownership has not been certified on all eight pages.','',
      '| Page | Complete elements: part 2 → oriented / total | Crossing pieces: part 2 → oriented | Elements with lower coverage | Geometry preserved? |',
      '|---|---:|---:|---:|---|']
    for r in table_rows:
        lines.append(f"| `{r['key']}` | {r['old_complete']} → {r['oriented_complete']} / {r['total']} | {r['old_crossings']} → {r['oriented_crossings']} | {len(r['element_coverage_regressions'])} | {'Yes' if r['passed'] else '**NO**'} |")
    lines+=['','## Artifacts, tests, and remaining work','',
      f"All 54 development pages and 40 whole-page rotation fixtures have new recognized word JSON and review images. All 54 also have a case image under `.astra/out/cases/`; the combined case-35 image is linked above. Rotated outputs live in `.astra/out/rotated/`. Rotated inference reuses only SHA-256-identical normalized grayscale tensors, retains the measured automatic decision/abstention, and inverse-maps each fixture separately. It never uses fixture truth to decide output direction. The manifest labels are used only in acceptance scoring.",
      '',f"Full pytest: **{test_counts['passed']} passed, {test_counts['failures']} failed, {test_counts['errors']} errors, {test_counts['skipped']} skipped** ({test_counts['tests']} collected). The 16 browser skips are the pre-existing missing-Chromium skips. API regenerated. New tests cover ordered corner mapping with offsets/scales, grey-paper crop padding, numeric/garbage abstention, all 100 whole/skew/word axis fixtures, normalized fitter reversibility, actual backend metadata, the real four-turn TableFormer grid, stage wiring, and plugin confidence/LTR/source-ownership contracts. The acceptance gate remains failed despite passing unit tests.",'',
      '- Short-word polarity is far below the required 46/48 decisions. The four pasted words are safe (correct or abstained), but that does not repair low standalone decision coverage.',
      '- Blind regions miss faint inserted words/lines and parts of blocks. Local chains do not yet have source-disjoint precision/recall qualification or complete manual word annotations.',
      '- The real title, headers and folio are not completely recovered. Numeric pieces can inherit a direction from a block, but isolated numerals cannot establish polarity.',
      '- Full-page versus local grouping, tiny crop fitting, noise suppression, table-piece recall and integration with the horizontal diagnostics require more work. Residual skew is measured, not independently validated as deskew.',
      '- A fresh uniform CW90 fixture (`s2-49598b2e848ab1f0ee1e-p00001__r90`) was falsely classified as mixed by the pre-layout guard. Its accepted 90-degree direction was not applied. The adapter is wired before layout and controlled tests verify its transformed backend, but automatic global normalization is not fully qualified.',
      '- The adapter preserves controlled logical tables under rotation; it cannot correct TableFormer’s intrinsic real-grid errors. Real table token survival or SUCCESS status is not a grid acceptance result.',
      '- No held-out pages were accessed, no model was downloaded, no push was made, and no detached/background job was started. All subprocesses were foreground tool sessions.',
      '', 'Every saved word was checked for finite bounded corners, inverse-frame consistency, pixel/page-unit guide consistency, explicit hypothesis status, and separate recognition confidence. Preliminary guide-unit fields were migrated with before/after file hashes; directions, recognized text, pixel boxes and review images were unchanged by that migration. Rotated views with an incorrectly shared accepted/unknown prior were rerun using the corrected cache key. These checks validate serialization, not detection accuracy.',
      '', 'Evidence: [compact review JSON](PAGE_LINES_ROUND4_ORIENTATION_20261009.json), [94-page geometry audit](../../.astra/out/orientation-artifact-audit.json), [gate details](../../.astra/out/orientation-acceptance/gates.json), [blind discovery](../../.astra/out/orientation-acceptance/blind.json), [word decisions](../../.astra/out/orientation-acceptance/decisions.json), [test log](../../.astra/orientation-tests-final.log).',
      '', '## Reproduce','',
      'Use the Python in `.astra/BRIEF.md` with `PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`. The recognizer checkpoint is an explicit argument; the codec hash is verified by its loader.','',
      '```sh',
      'python scripts/glyphs/archive/evaluate_orientation_round4.py --checkpoint "$CKPT" --require-gate',
      'python scripts/glyphs/archive/render_orientation_round4.py --checkpoint "$CKPT"',
      'python scripts/glyphs/archive/render_orientation_round4.py --checkpoint "$CKPT" --rotated --out .astra/out/rotated',
      'python scripts/glyphs/archive/integrate_orientation_round4.py --checkpoint "$CKPT"',
      'python scripts/generate_api_docs.py',
      'python -m pytest -p no:cacheprovider -q --junitxml=.astra/orientation-tests-final.xml',
      'python scripts/glyphs/archive/audit_orientation_round4.py',
      'python scripts/glyphs/archive/report_orientation_round4.py','```','',
      '## Commit handoff','',
      ('**No commit was created.** The authorized commit script reached `git add`, which failed with exit 128: the sandbox could not create the worktree’s `index.lock` (`Operation not permitted`). HEAD remains `f611ee2` on `astra/page-lines-4`. '
       'The 18-file patch was replayed byte-for-byte against that base, then checked in reverse. [Commit script](../../.astra/commit-page-lines-round4-orientation.sh), [patch](../../.astra/page-lines-round4-orientation.patch), and [validation receipt](../../.astra/round4-orientation-patch-validation.json) provide the requested fallback. The script verifies the branch, base revision, empty index and file hashes before committing with both requested trailers. It does not push.'
       if attempt.exists() and not commit['committed'] else 'See the final delivery message for the actual commit outcome.')]
    (ROOT/'docs/records/reviews/PAGE_LINES_ROUND4_ORIENTATION_20261009.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(pages=len(rows),rotated=len(rotated),compatibility_preserved=report['compatibility_preserved'],tables_without_regression=sum(r['passed'] for r in table_rows),tests=test_counts)))


if __name__=='__main__':main()
