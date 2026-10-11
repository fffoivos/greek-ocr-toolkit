"""Offline, hash-bound Vision / Document AI diagnostic comparison and report."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import unicodedata

from greekocr.score import edit_distance
from prototypes.harvest.google_failed_lines import (
    SPECIAL, atomic_json, build_review, canonical, characters_table, crop_metrics,
    distribution, fmt, response_path, sha256, summarise, write_csv,
)

RARE = 'ϗȣϛϲϝϙϡ'


def rare_only_changes(reference: str, prediction: str) -> bool:
    """All edits in a minimum-distance alignment touch an actual rare glyph.

    Ties prefer a rare-touching optimal path when one exists. This tests the
    existence of such an alignment, not a guessed equivalence of look-alikes.
    """
    previous = [(j, all(c in RARE for c in prediction[:j])) for j in range(len(prediction) + 1)]
    for i, a in enumerate(reference, 1):
        current = [(i, all(c in RARE for c in reference[:i]))]
        for j, b in enumerate(prediction, 1):
            cost, valid = previous[j-1]
            candidates = [(cost + (a != b), valid and (a == b or a in RARE or b in RARE)),
                (previous[j][0] + 1, previous[j][1] and a in RARE),
                (current[j-1][0] + 1, current[j-1][1] and b in RARE)]
            minimum = min(x[0] for x in candidates)
            current.append((minimum, any(x[1] for x in candidates if x[0] == minimum)))
        previous = current
    distance, only_rare = previous[-1]
    return distance > 0 and only_rare


def comparison_metrics(docai_text: str, vision_text: str) -> dict:
    """Strict NFD pairwise disagreement; neither engine is ground truth."""
    a, b = [unicodedata.normalize('NFD', t) for t in (docai_text, vision_text)]
    edits = edit_distance(a, b)
    forward = edits / len(a) if a else (0.0 if not b else None)
    reverse = edits / len(b) if b else (0.0 if not a else None)
    return dict(raw_equal=docai_text == vision_text, nfd_equal=a == b, nfd_edits=edits,
        nfd_equal_without_cr_lf=a.replace('\r', '').replace('\n', '') == b.replace('\r', '').replace('\n', ''),
        nfd_equal_collapsed_whitespace=' '.join(a.split()) == ' '.join(b.split()),
        docai_nfd_characters=len(a), vision_nfd_characters=len(b),
        nfd_cer_docai_reference=forward, nfd_cer_vision_reference=reverse,
        mean_bidirectional_nfd_cer=(forward + reverse) / 2 if forward is not None and reverse is not None else None,
        rare_glyphs_vision=''.join(c for c in RARE if c in vision_text),
        rare_only_disagreement=rare_only_changes(a, b))


def compare_rows(vision: list[dict], docai: list[dict], docai_output: Path) -> list[dict]:
    by_id = {r['crop_id']: r for r in docai}
    if len(by_id) != len(docai):
        raise ValueError('duplicate Document AI crop IDs')
    result = []
    for v in vision:
        d = by_id.get(v['crop_id'])
        pair = dict(crop_id=v['crop_id'], crop_sha256=v['crop_sha256'], source=v['source'],
            failure_type=v['failure_type'], failure_types=v['failure_types'],
            vision_status=v['status'], docai_status=d['status'] if d else 'missing',
            vision_text=v.get('text'), docai_text=d.get('text') if d else None)
        if d and d['crop_sha256'] != v['crop_sha256']:
            raise ValueError('engine crop SHA mismatch: ' + v['crop_id'])
        for engine, row in [('docai', d), ('vision', v)]:
            for key in ('mean_symbol_confidence', 'min_symbol_confidence', 'lines_returned', 'treatment', 'exposure_signals'):
                pair[engine + '_' + key] = row.get(key) if row else None
        if d and d['status'] == 'ok':
            envelope = json.loads(response_path(docai_output, d).read_text())
            if envelope['crop_sha256'] != d['crop_sha256'] or hashlib.sha256(canonical(envelope['response']).encode()).hexdigest() != envelope['response_sha256']:
                raise ValueError('Document AI response envelope changed')
            raw_path = Path(envelope['raw_json_path'])
            if json.loads(raw_path.read_text()) != envelope['response']:
                raise ValueError('Document AI original raw response changed')
            for key, value in crop_metrics(envelope['response'], d['width_px'], d['height_px']).items():
                if d[key] != value:
                    raise ValueError(f'Document AI metric changed: {d["crop_id"]} {key}')
            pair['docai_response_sha256'] = envelope['response_sha256']
        if v['status'] == 'ok' and d and d['status'] == 'ok':
            pair.update(comparison_metrics(d['text'], v['text']))
        else:
            pair.update({key: None for key in comparison_metrics('', '')})
        result.append(pair)
    return result


def agreement(rows: list[dict]) -> dict:
    pairs = [r for r in rows if r['nfd_equal'] is not None]
    reference_atoms = sum(r['docai_nfd_characters'] for r in pairs)
    prediction_atoms = sum(r['vision_nfd_characters'] for r in pairs)
    edits = sum(r['nfd_edits'] for r in pairs)
    return dict(n_crops=len(rows), n_paired=len(pairs), raw_equal=sum(r['raw_equal'] for r in pairs),
        nfd_equal=sum(r['nfd_equal'] for r in pairs),
        nfd_equal_without_cr_lf=sum(r['nfd_equal_without_cr_lf'] for r in pairs),
        nfd_equal_collapsed_whitespace=sum(r['nfd_equal_collapsed_whitespace'] for r in pairs),
        nfd_agreement_rate=sum(r['nfd_equal'] for r in pairs) / len(pairs) if pairs else None,
        raw_agreement_rate=sum(r['raw_equal'] for r in pairs) / len(pairs) if pairs else None,
        pooled_nfd_edits=edits, docai_nfd_characters=reference_atoms, vision_nfd_characters=prediction_atoms,
        pooled_nfd_cer_docai_reference=edits / reference_atoms if reference_atoms else None,
        pooled_nfd_cer_vision_reference=edits / prediction_atoms if prediction_atoms else None)


def md_text(text: str | None) -> str:
    if text is None:
        return '—'
    # HTML entities keep emitted punctuation literal in a Markdown table.
    import html
    return html.escape(text).replace('|', '&#124;').replace('\r', '&#13;').replace('\n', '<br>') or '(empty)'


def build_vision_artifacts(rows, comments, directory, out, rec):
    output = out / 'vision_failed_lines'
    effects = json.loads((directory / 'page_comments.json').read_text())['effects']
    summary = summarise(rows, list(effects))
    for kind, stats in summary['types'].items():
        associated = [c for c in comments if kind in c['failure_types']]
        stats.update(n_page_comments=len(associated),
            n_bound_page_comments=sum(any(b['failure_type'] == kind for b in c['bindings']) for c in associated),
            n_withheld_anemi_page_comments=sum(c['status'] == 'withheld_anemi_page' for c in associated))
    chars = characters_table(rows)
    for filename, value in [('metrics.json', rows), ('summary.json', summary), ('characters.json', chars),
                            ('page_comment_coverage.json', comments), ('receipt.json', rec)]:
        atomic_json(output / filename, value)
    write_csv(output / 'crops.csv', rows)
    char_rows = [dict(source=source, character=c, codepoint=f'U+{ord(c):04X}', unicode_name=unicodedata.name(c, 'CONTROL'), count=n)
        for source, table in chars.items() for c, n in table['character_counts'].items()]
    write_csv(output / 'characters.csv', char_rows)
    docai_output = out / 'docai_failed_lines'
    docai_path = docai_output / 'metrics.json'
    docai = json.loads(docai_path.read_text()) if docai_path.exists() else []
    ds = summarise(docai, list(effects))
    dc = characters_table(docai)
    pairs = compare_rows(rows, docai, docai_output)
    controls = [r for r in pairs if r['failure_type'] == 'control_owner_verified']
    selected = [r for r in pairs if r['rare_glyphs_vision'] or r['rare_only_disagreement']]
    rare_crops = sum(bool(r['rare_glyphs_vision']) for r in pairs)
    unique_controls = list({r['crop_sha256']: r for r in controls}.values())
    comp = dict(status=rec['status'], controls=agreement(controls),
        controls_unique_images=agreement(unique_controls), all=agreement(pairs),
        rare_glyph_crops_vision=rare_crops,
        rare_glyph_unique_images_vision=len({r['crop_sha256'] for r in pairs if r['rare_glyphs_vision']}),
        rare_only_disagreement_crops=sum(bool(r['rare_only_disagreement']) for r in pairs),
        failure_types={kind: agreement([r for r in pairs if kind in r['failure_types']]) for kind in effects},
        docai_metrics_sha256=sha256(docai_path) if docai_path.exists() else None,
        vision_metrics_sha256=sha256(output / 'metrics.json'),
        docai_binding=json.loads((docai_output / 'receipt.json').read_text())['binding'] if docai else None,
        vision_binding=rec['binding'])
    atomic_json(output / 'comparison_summary.json', comp)
    atomic_json(output / 'comparison.json', pairs)
    write_csv(output / 'comparison.csv', pairs)
    write_csv(output / 'rare_glyph_crops.csv', selected)
    rec['rare_glyph_crops_vision'] = rare_crops
    rec['comparison_paired_crops'] = comp['all']['n_paired']
    atomic_json(output / 'receipt.json', rec)
    a = comp['controls']
    lines = ['# Cloud Vision vs Document AI on failed lines — v1', '',
        f"Status: **{rec['status']}**. {rec['measured_crop_ids']}/{len(rows)} Vision crop IDs measured; {comp['all']['n_paired']} hash-matched pairs. Anemi included: **{rec['include_anemi']}**. Crops with Vision output containing any of `{RARE}`: **{rare_crops}** ({comp['rare_glyph_unique_images_vision']} distinct images).", '',
        '## Controls agreement and baseline', '',
        f"Controls are owner-verified crop regions, not gold OCR transcripts. Strict NFD agreement: **{a['nfd_equal']}/{a['n_paired']} ({100*a['nfd_agreement_rate']:.2f}%)**." if a['n_paired'] else 'No paired control readings.',
        f"Raw-text agreement: {a['raw_equal']}/{a['n_paired']}. Pooled strict NFD CER with DocAI as reference: {fmt(a['pooled_nfd_cer_docai_reference'])}; reverse: {fmt(a['pooled_nfd_cer_vision_reference'])}. Unique-image control agreement: {comp['controls_unique_images']['nfd_equal']}/{comp['controls_unique_images']['n_paired']}.", '',
        f"Whitespace diagnostics only: removing CR/LF gives {a['nfd_equal_without_cr_lf']}/{a['n_paired']} identical controls; collapsing all whitespace gives {a['nfd_equal_collapsed_whitespace']}/{a['n_paired']}. These do not replace strict agreement/CER. Terminal newline conventions account for some, but not all, disagreement.", '',
        '| Engine | Control crop IDs / unique images | Returned-line distribution | Empty | Mean symbol confidence median / p05 | Minimum median / p05 | Chars/100px median (p05–p95) | Exposed / silent candidates |',
        '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for name, s in [('Document AI', ds), ('Cloud Vision', summary)]:
        b = s['types']['control_owner_verified']
        lines.append(f"| {name} | {b['n_measured']} / {b['n_unique_images']} | `{b['lines_returned_distribution']}` | {b['empty_count']} | {fmt(b['mean_symbol_confidence']['median'])} / {fmt(s['low_confidence_threshold'])} | {fmt(b['min_symbol_confidence']['median'])} / {fmt(s['low_min_confidence_threshold'])} | {fmt(b['characters_per_100px_width']['median'])} ({fmt(b['characters_per_100px_width']['p05'])}–{fmt(b['characters_per_100px_width']['p95'])}) | {b['exposed_count']} / {b['silent_candidate_count']} |")
    lines += ['', '## Scope and measurement', '',
        f"Same two catalogues and exact comment-region bindings as T10: {rec['catalogued_current_output_crops']} catalogue IDs plus {rec['derived_comment_crops']} derived IDs. Anemi measured IDs: {sum(r['status']=='ok' and r['source']=='Anemi' for r in rows)}; Vouli: {sum(r['status']=='ok' and r['source']=='Vouli' for r in rows)}. Distinct measured images: {rec['unique_measured_crop_sha256']}. Duplicate bytes share one request. Character tables count each SHA once; crop statistics and agreement count each ID unless explicitly labelled unique-image. Types overlap and must not be summed. Marked-region images are not sent; these are development crops, not held-out pages.", '',
        f"Vision binding: `{canonical(rec['binding'])}`. [Vision REST endpoint](https://docs.cloud.google.com/vision/docs/reference/rest/v1/images/annotate). [Google's language list](https://docs.cloud.google.com/vision/docs/languages) lists `grc` as experimental (checked 11 October 2026). The provider default model is unpinned; receipts do not claim a resolved model version.", '',
        f"Document AI binding: `{canonical(comp['docai_binding'])}`. Existing cached responses only; **zero new DocAI calls**. Comparison recomputes DocAI metrics from the hash-checked raw responses. The current T10 metrics contain Anemi even though historical prose in its report still says withheld; this comparison uses verified per-crop evidence, not that stale scope sentence.", '',
        'Vision has paragraphs and symbol `detectedBreak` fields, not DocAI layout-line objects. Each paragraph is preserved; within it only reported LINE_BREAK, EOL_SURE_SPACE or HYPHEN splits a line. SPACE/SURE_SPACE preserve spaces and isPrefix is honoured. HYPHEN splits a line without inventing an emitted character. Per-line confidence is the enclosing paragraph confidence, explicitly labelled in metrics. No geometry-based splitting. Missing hierarchy uses a labelled raw-text splitlines fallback. [Annotation schema](https://docs.cloud.google.com/vision/docs/reference/rest/v1/AnnotateImageResponse).', '',
        'Public Vision read() returns NFD; reports and character counts retain the raw fullTextAnnotation.text. CER normalises both raw texts to NFD and preserves all case, spaces, punctuation and terminal newlines. Edits / DocAI NFD length is directional disagreement, not accuracy; reverse and mean bidirectional CER are also in CSV. An empty reference with a nonempty opposite reading has undefined CER (null); edits are retained. Two empty readings agree with CER 0. No glyph-level gold/exposure denominator is supplied, so emitted rare glyphs do not prove recognition correctness and absence does not prove model incapability.', '',
        'Treatment uses the same diagnostic as T10: multiple returned lines, empty text, or mean/min symbol confidence below that engine’s control p05. A silent candidate lacks these signals; it is not a verified transcription. Confidence scales and line definitions differ across models. Missing ink without a crop has no OCR evidence. Full distributions, density ranges, text, Greek sets and detected languages are in metrics/summary JSON.', '',
        '## Treatment by failure type', '',
        '| Type | DocAI n; lines; empty; exposed / silent | Vision n; lines; empty; exposed / silent | DocAI mean / min confidence median | Vision mean / min confidence median | DocAI / Vision chars per 100px median | NFD equal / paired |',
        '| --- | --- | --- | --- | --- | --- | --- |']
    for kind in effects:
        d, v = ds['types'][kind], summary['types'][kind]
        ag = comp['failure_types'][kind]
        lines.append(f"| `{kind}` | {d['n_measured']}; `{d['lines_returned_distribution']}`; {d['empty_count']}; {d['exposed_count']} / {d['silent_candidate_count']} | {v['n_measured']}; `{v['lines_returned_distribution']}`; {v['empty_count']}; {v['exposed_count']} / {v['silent_candidate_count']} | {fmt(d['mean_symbol_confidence']['median'])} / {fmt(d['min_symbol_confidence']['median'])} | {fmt(v['mean_symbol_confidence']['median'])} / {fmt(v['min_symbol_confidence']['median'])} | {fmt(d['characters_per_100px_width']['median'])} / {fmt(v['characters_per_100px_width']['median'])} | {ag['nfd_equal']} / {ag['n_paired']} |")
    lines += ['', '### Full T10-style treatment metrics for both engines', '',
        '| Type | Engine | Measured / withheld | Page comments / bound | Empty rate | Mean conf median (p05) | Min conf median | Chars/100px median (p05–p95) | Density below / above controls p05–p95 | Exposed / silent candidates | Treatment |',
        '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for kind in ['control_owner_verified', *effects]:
        for engine, s in [('Document AI', ds), ('Cloud Vision', summary)]:
            b = s['types'][kind]
            associated = [c for c in comments if kind in c['failure_types']]
            bound = sum(any(x['failure_type'] == kind for x in c['bindings']) for c in associated)
            verdict = ('No crop evidence' if not b['n_measured'] else
                       'Google absorbs it silently — candidates' if b['silent_candidate_count'] else 'Google exposes it')
            lines.append(f"| `{kind}` | {engine} | {b['n_measured']} / {b['withheld_anemi']} | {len(associated)} / {bound} | {fmt(b['empty_rate'])} | {fmt(b['mean_symbol_confidence']['median'])} ({fmt(b['mean_symbol_confidence']['p05'])}) | {fmt(b['min_symbol_confidence']['median'])} | {fmt(b['characters_per_100px_width']['median'])} ({fmt(b['characters_per_100px_width']['p05'])}–{fmt(b['characters_per_100px_width']['p95'])}) | {b['density_below_controls_p05']} / {b['density_above_controls_p95']} | {b['exposed_count']} / {b['silent_candidate_count']} | {verdict} |")
    lines += ['', '### Controls density distribution', '',
        '| Engine | Min | p05 | p25 | Median | p75 | p95 | Max |',
        '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for engine, s in [('Document AI', ds), ('Cloud Vision', summary)]:
        d = s['types']['control_owner_verified']['characters_per_100px_width']
        lines.append('| ' + engine + ' | ' + ' | '.join(fmt(d[k]) for k in ('min', 'p05', 'p25', 'median', 'p75', 'p95', 'max')) + ' |')
    lines += ['', '### Page-comment coverage', '', '| Comment | Page | Types | Binding / scope | Crop IDs |', '| --- | --- | --- | --- | --- |']
    for c in comments:
        lines.append(f"| {c['comment_id']} | `{c['page']}` | {', '.join(c['failure_types'])} | {c['status']} | {len(c['crop_ids'])} |")
    lines += ['', '## Rare glyphs and requested characters', '', '| Source | Glyph | Code point | DocAI raw / NFD | Vision raw / NFD |', '| --- | --- | --- | --- | --- |']
    char_comparison = []
    for source in ('ALL', 'Anemi', 'Vouli'):
        for c in SPECIAL:
            d = dc.get(source, {}).get('requested_characters', {}).get(c, dict(raw_count=0, nfd_count=0))
            v = chars.get(source, {}).get('requested_characters', {}).get(c, dict(raw_count=0, nfd_count=0))
            lines.append(f"| {source} | {c} | U+{ord(c):04X} | {d['raw_count']} / {d['nfd_count']} | {v['raw_count']} / {v['nfd_count']} |")
            char_comparison.append(dict(source=source, character=c, codepoint=f'U+{ord(c):04X}', docai_raw=d['raw_count'], docai_nfd=d['nfd_count'], vision_raw=v['raw_count'], vision_nfd=v['nfd_count']))
    write_csv(output / 'rare_glyph_comparison.csv', char_comparison)
    lines += ['', '## Crops emitting rare glyphs or disagreeing only at rare positions', '',
        f"{len(selected)} selected crop IDs. Rare-only disagreement means every edit in at least one minimum NFD alignment touches an actual `{RARE}` code point on either side; look-alike substitutions where neither engine emitted a rare glyph cannot be identified without gold text. [Complete selected-crop CSV](vision_failed_lines/rare_glyph_crops.csv).", '']
    for pair in selected[:30]:
        lines.append(f"- [{pair['crop_id']}](vision_vs_docai_review.html#{pair['crop_id']}): Vision glyphs `{pair['rare_glyphs_vision']}`; rare-only disagreement `{pair['rare_only_disagreement']}`.")
    if not selected:
        lines.append('None observed.')
    elif len(selected) > 30:
        lines.append(f'{len(selected)-30} additional IDs are listed in the selected-crop CSV.')
    lines += ['', '## Cost receipt', '',
        f"**{rec['calls']} Vision API calls**: {rec['successful_calls']} successful; {rec['error_calls']} errors; {rec['images_billed_known']} known image-feature units; {rec['images_billing_unknown']} outcomes unknown. Base list-price estimate **US${rec['estimated_cost_usd']:.4f}** at US$1.50/1,000 images. [Official Vision pricing](https://cloud.google.com/vision/pricing), checked 11 October 2026. The first 1,000 monthly units are free; remaining allowance, credits, discounts and taxes are not assumed. This is not an invoice. No new DocAI charges. Calls are cumulative across resumptions; cache hits cost zero.", '',
        '[Receipt](vision_failed_lines/receipt.json) · [Both readings, raw CSV](vision_failed_lines/comparison.csv) · [Per-engine crop metrics](vision_failed_lines/crops.csv) · [Comparison summary](vision_failed_lines/comparison_summary.json) · [Characters](vision_failed_lines/characters.csv) · [Rare comparison CSV](vision_failed_lines/rare_glyph_comparison.csv) · [Review page](vision_vs_docai_review.html)', '']
    if rec['error']:
        lines += ['## Stopped request', '', md_text(rec['error']), '', 'No later crop was sent. There are no automatic retries.', '']
    validation_path = output / 'validation.json'
    if validation_path.exists():
        validation = json.loads(validation_path.read_text())
        lines += ['## Verification and layout limit', '',
            f"**{validation['tests']['passed']} offline tests passed.** The [artifact validator](../../scripts/harvest/validate_vision_comparison.py) recomputed every crop metric and comparison from saved raw responses, checked every local image/card/link and CSV ID, and verified one call per unique SHA. Cache validation and offline regeneration added zero Vision or DocAI calls. [Validation receipt](vision_failed_lines/validation.json).", '',
            'Responsive CSS constrains images to available width and wraps all text, with a phone-width media query. Actual desktop/phone viewport rendering remains unverified: the installed headless Firefox could not launch in the sandbox; automatic approval review rejected native Firefox computer use because Firefox was not approved, and the in-app browser was unavailable. [Layout-check record](vision_failed_lines/layout_validation.json).', '']
    lines += ['## Every crop: readings side by side', '',
        '| Crop | Source / type | Document AI raw text | Vision raw text | Strict NFD CER (DocAI reference) |',
        '| --- | --- | --- | --- | --- |']
    for pair in pairs:
        lines.append(f"| [{pair['crop_id']}](vision_vs_docai_review.html#{pair['crop_id']}) | {pair['source']} / `{pair['failure_type']}` | {md_text(pair['docai_text'])} | {md_text(pair['vision_text'])} | {fmt(pair['nfd_cer_docai_reference'])} |")
    (out / 'VISION_VS_DOCAI_v1.md').write_text('\n'.join(lines) + '\n')
    build_review(rows, summary, comments, out, rec, engine='vision', comparison={r['crop_id']: r for r in pairs})
    return comp
