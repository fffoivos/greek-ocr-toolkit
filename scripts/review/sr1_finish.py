"""Regenerate SR1 API inventory and produce a reviewable, unapplied R2 scorer patch."""
from __future__ import annotations
import difflib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]


def main() -> None:
    from scripts import generate_api_docs as api
    api.CALLS.update({
        'greekocr.adjudicate.artifact_custody.copy_artifacts': 'receipt = copy_artifacts(source_root, new_destination, selected_relative_paths)',
        'greekocr.adjudicate.artifact_custody.verify': 'result = verify(destination, receipt["manifest"])',
        'greekocr.adjudicate.batch_check.batch_check': 'result = batch_check(folder, assignment, answers, private_keys)',
        'greekocr.adjudicate.controls_review_sheets.controls_review_sheets': 'receipt = controls_review_sheets(verified_controls, private_review_dir)',
        'greekocr.adjudicate.deal_batches.deal_batches': 'receipt = deal_batches(blind_deck, isolated_assignments, batch_size=110)',
        'greekocr.adjudicate.edit_evidence_crosstab.edit_evidence_crosstab': 'table = edit_evidence_crosstab(saved_release_records, explicit_print_verdicts)',
        'greekocr.adjudicate.mark_profile.mark_views': 'views = mark_views(native_line_image, word_box, letter_box)',
        'greekocr.adjudicate.owner_notes_export.owner_notes_export': 'receipt = owner_notes_export(db_dump, cards, sheet_conventions, new_jsonl_path)',
        'greekocr.adjudicate.page_specs.load_spec': 'spec = load_spec(local_json_path)',
        'greekocr.adjudicate.page_specs.render_spec': 'html = render_spec(local_json_path)',
        'greekocr.adjudicate.release_census.release_census': 'census = release_census(local_release_rows, selection_by_id, seed=20261017)',
        'greekocr.adjudicate.release_census.evidence_dump': 'evidence = evidence_dump(local_release_rows, requested_line_id)',
        'greekocr.adjudicate.score.named_slices': 'slices = named_slices(truth_context_rows)',
        'greekocr.adjudicate.truth_overlay.add': 'receipt = add(parent_overlay, adjudicated_entry, version="v1.1", evidence_paths=local_evidence, expected_parent="v1")',
        'greekocr.adjudicate.truth_overlay.symmetric_rescore': 'result = symmetric_rescore(frozen_lines, overlay, predictions_by_arm, local_scorer)',
    })
    # Persist the new CALLS entries so the standard generator works on its own.
    generator=ROOT/'scripts/generate_api_docs.py'
    source=generator.read_text()
    marker='\n\ndef api_entries():'
    start='# SR1 operational APIs\nCALLS.update('
    addition=start+repr({k:v for k,v in api.CALLS.items() if k.startswith('greekocr.adjudicate.') and k.rsplit('.',1)[-1] in {'copy_artifacts','verify','batch_check','controls_review_sheets','deal_batches','edit_evidence_crosstab','mark_views','owner_notes_export','load_spec','render_spec','release_census','evidence_dump','named_slices','add','symmetric_rescore'}})+')\n'
    if start not in source:
        generator.write_text(source.replace(marker,'\n\n'+addition+marker))
    api.generate()
    scorer=ROOT.parent/'greek-ocr-toolkit-spellcheck-r2prep/scripts/labelfix/r2_score.py'
    before=scorer.read_text()
    after=before.replace('from collections import Counter, defaultdict','from greekocr.adjudicate.score import named_slices\nfrom collections import Counter, defaultdict',1)
    old="                    base=(ts or ps)['base'],"
    new=old+"\n                    **{k:ts[k] for k in ('word','orthography','numeral','exact_name') if ts and k in ts},"
    assert old in after
    after=after.replace(old,new,1)
    old='    return dict(micro=summarize(records),groups=groups),records'
    new='    slices = {name:summarize(selected) for name,selected in named_slices(records).items()}\n    return dict(micro=summarize(records),groups=groups,slices=slices),records'
    assert old in after
    after=after.replace(old,new,1)
    patch=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/scripts/labelfix/r2_score.py',tofile='b/scripts/labelfix/r2_score.py'))
    (ROOT/'artifacts/cleanup_sr1/r2_score_slices.patch').write_text(patch)
    from greekocr.adjudicate._files import sha,dump
    dump(ROOT/'artifacts/cleanup_sr1/r2_score_patch_receipt.json',dict(source=str(scorer),source_sha256=sha(scorer),patch_sha256=sha(ROOT/'artifacts/cleanup_sr1/r2_score_slices.patch'),applied=False))


if __name__=='__main__':main()
