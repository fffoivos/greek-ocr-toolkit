"""Locate receipted repository data after CLEAN3B's mirrored data move.

Set GREEK_OCR_DATA_ROOT to the directory containing docs/, artifacts/, etc.
Repository files always take precedence. CLEAN4L aliases preserve historical
receipt/mirror paths. Resolution does not copy or modify data.
"""
from __future__ import annotations

import csv
from functools import lru_cache
import os
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parents[2]
RECEIPTS = Path('docs/cleanup_20261019/data_out/RECEIPTS')


# CLEAN4L retrieval aliases. Historical receipts and mirrored data retain their
# original identities; the paths below come from LAYOUT_REPORT.md's move table.
_LAYOUT_MOVES = (
    ('docs/harvest/seg_census/mock_split_stage_results.json', 'docs/records/harvest/seg_census/mock_split_stage_results.json'),
    ('docs/harvest/seg_census/full_tests_1c_deselected.log', 'docs/records/harvest/seg_census/full_tests_1c_deselected.log'),
    ('docs/harvest/seg_census/verifier_allow_untracked.txt', 'docs/records/harvest/seg_census/verifier_allow_untracked.txt'),
    ('docs/harvest/seg_census/pristine_collection_1c3.log', 'docs/records/harvest/seg_census/pristine_collection_1c3.log'),
    ('docs/harvest/seg_census/remote_snapshot_hashes.json', 'docs/records/harvest/seg_census/remote_snapshot_hashes.json'),
    ('docs/harvest/seg_census/package_tests_complete.log', 'docs/records/harvest/seg_census/package_tests_complete.log'),
    ('docs/harvest/seg_census/pristine_collection_1c.log', 'docs/records/harvest/seg_census/pristine_collection_1c.log'),
    ('docs/harvest/seg_census/package_tests_correct.log', 'docs/records/harvest/seg_census/package_tests_correct.log'),
    ('docs/harvest/seg_census/package_composition.json', 'docs/records/harvest/seg_census/package_composition.json'),
    ('docs/harvest/seg_census/final_package_tests.log', 'docs/records/harvest/seg_census/final_package_tests.log'),
    ('docs/harvest/seg_census/mock_batch_results.json', 'docs/records/harvest/seg_census/mock_batch_results.json'),
    ('docs/harvest/seg_census/mock_stage_results.json', 'docs/records/harvest/seg_census/mock_stage_results.json'),
    ('docs/harvest/seg_census/package_tests_final.log', 'docs/records/harvest/seg_census/package_tests_final.log'),
    ('docs/harvest/seg_census/split_input.schema.json', 'docs/records/harvest/seg_census/split_input.schema.json'),
    ('docs/cleanup_20261019/drafts/B_ac/a_google_ocr', 'docs/B_training_data/a_google_ocr'),
    ('docs/harvest/seg_census/capture_inventory.json', 'docs/records/harvest/seg_census/capture_inventory.json'),
    ('docs/harvest/seg_census/source_conflicts.patch', 'docs/records/harvest/seg_census/source_conflicts.patch'),
    ('docs/harvest/SOL_ROUTING_sourcing_20261017.md', 'docs/records/harvest/SOL_ROUTING_sourcing_20261017.md'),
    ('docs/harvest/seg_census/HANDOFF_SEGCENSUS1.md', 'docs/records/harvest/seg_census/HANDOFF_SEGCENSUS1.md'),
    ('docs/harvest/seg_census/OUT_OF_GIT_RECEIPT.md', 'docs/records/harvest/seg_census/OUT_OF_GIT_RECEIPT.md'),
    ('docs/harvest/seg_census/byte_identity_1c.json', 'docs/records/harvest/seg_census/byte_identity_1c.json'),
    ('docs/harvest/seg_census/integration_tests.log', 'docs/records/harvest/seg_census/integration_tests.log'),
    ('docs/harvest/seg_census/package_changes.patch', 'docs/records/harvest/seg_census/package_changes.patch'),
    ('docs/harvest/seg_census/suite_comparison.json', 'docs/records/harvest/seg_census/suite_comparison.json'),
    ('docs/cleanup_20261019/drafts/B_ac/c_pipeline', 'docs/B_training_data/c_pipeline'),
    ('docs/harvest/seg_census/census04_config.json', 'docs/records/harvest/seg_census/census04_config.json'),
    ('docs/harvest/seg_census/mock_segmentation.py', 'docs/records/harvest/seg_census/mock_segmentation.py'),
    ('docs/harvest/seg_census/mock_split_stage.log', 'docs/records/harvest/seg_census/mock_split_stage.log'),
    ('docs/harvest/docai_failed_lines_review.html', 'docs/records/harvest/docai_failed_lines_review.html'),
    ('docs/harvest/seg_census/finalize_package.py', 'docs/records/harvest/seg_census/finalize_package.py'),
    ('docs/harvest/seg_census/mock_split_stage.py', 'docs/records/harvest/seg_census/mock_split_stage.py'),
    ('docs/harvest/seg_census/source_capture.json', 'docs/records/harvest/seg_census/source_capture.json'),
    ('docs/harvest/seg_census/mock_stage_1c3.log', 'docs/records/harvest/seg_census/mock_stage_1c3.log'),
    ('docs/harvest/seg_census/DEPLOY_SHA256SUMS', 'docs/records/harvest/seg_census/DEPLOY_SHA256SUMS'),
    ('docs/harvest/seg_census/SOURCE_CAPTURE.md', 'docs/records/harvest/seg_census/SOURCE_CAPTURE.md'),
    ('docs/harvest/seg_census/capture_paths.txt', 'docs/records/harvest/seg_census/capture_paths.txt'),
    ('docs/harvest/seg_census/compare_suites.py', 'docs/records/harvest/seg_census/compare_suites.py'),
    ('docs/harvest/seg_census/full_baseline.log', 'docs/records/harvest/seg_census/full_baseline.log'),
    ('docs/harvest/seg_census/full_baseline.xml', 'docs/records/harvest/seg_census/full_baseline.xml'),
    ('docs/harvest/seg_census/full_tests_1c.log', 'docs/records/harvest/seg_census/full_tests_1c.log'),
    ('docs/harvest/seg_census/package_paths.txt', 'docs/records/harvest/seg_census/package_paths.txt'),
    ('docs/harvest/seg_census/package_tests.log', 'docs/records/harvest/seg_census/package_tests.log'),
    ('docs/harvest/seg_census/prepare_config.py', 'docs/records/harvest/seg_census/prepare_config.py'),
    ('docs/harvest/seg_census/DEPLOY_PATHS.txt', 'docs/records/harvest/seg_census/DEPLOY_PATHS.txt'),
    ('docs/harvest/seg_census/full_current.log', 'docs/records/harvest/seg_census/full_current.log'),
    ('docs/harvest/seg_census/full_current.xml', 'docs/records/harvest/seg_census/full_current.xml'),
    ('docs/harvest/seg_census/package_id.json', 'docs/records/harvest/seg_census/package_id.json'),
    ('docs/harvest/seg_census/parity_check.py', 'docs/records/harvest/seg_census/parity_check.py'),
    ('docs/harvest/seg_census/receipt_b2.json', 'docs/records/harvest/seg_census/receipt_b2.json'),
    ('docs/harvest/seg_census/remote_evidence', 'docs/records/harvest/seg_census/remote_evidence'),
    ('docs/harvest/line_pipeline/pipeline.mmd', 'docs/records/harvest/line_pipeline_legacy/pipeline.mmd'),
    ('docs/harvest/seg_census/COMMIT_LIST.md', 'docs/records/harvest/seg_census/COMMIT_LIST.md'),
    ('docs/harvest/seg_census/mock_batch.log', 'docs/records/harvest/seg_census/mock_batch.log'),
    ('docs/harvest/seg_census/mock_stage.log', 'docs/records/harvest/seg_census/mock_stage.log'),
    ('docs/harvest/seg_census/snapshot_diffs', 'docs/records/harvest/seg_census/snapshot_diffs'),
    ('docs/harvest/seg_census/source_capture', 'docs/records/harvest/seg_census/source_capture'),
    ('docs/harvest/DOCAI_FAILED_LINES_v1.md', 'docs/records/harvest/DOCAI_FAILED_LINES_v1.md'),
    ('docs/harvest/seg_census/mock_batch.py', 'docs/records/harvest/seg_census/mock_batch.py'),
    ('docs/harvest/transkribus_failed_lines', 'docs/records/harvest/transkribus_failed_lines'),
    ('docs/harvest/seg_census/FOLLOW_UP.md', 'docs/records/harvest/seg_census/FOLLOW_UP.md'),
    ('docs/harvest/seg_census/JOB_KINDS.md', 'docs/records/harvest/seg_census/JOB_KINDS.md'),
    ('docs/harvest/seg_census/receipt.json', 'docs/records/harvest/seg_census/receipt.json'),
    ('docs/harvest/line_pipeline/README.md', 'docs/records/harvest/line_pipeline_legacy/README.md'),
    ('docs/harvest/seg_census/b2_evidence', 'docs/records/harvest/seg_census/b2_evidence'),
    ('docs/harvest/COLLECTION_PLAN_v1.md', 'docs/records/harvest/COLLECTION_PLAN_v1.md'),
    ('docs/harvest/VISION_VS_DOCAI_v1.md', 'docs/records/harvest/VISION_VS_DOCAI_v1.md'),
    ('docs/harvest/seg_census/.gitignore', 'docs/records/harvest/seg_census/.gitignore'),
    ('docs/review/HUMAN_REVIEW_SHEETS.md', 'docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md'),
    ('docs/harvest/collect_v3_admission', 'docs/records/harvest/collect_v3_admission'),
    ('docs/t6-scoped-pytest-results.xml', 'docs/records/verify_20261008/t6-scoped-pytest-results.xml'),
    ('docs/cleanup_20261019/drafts/B_b', 'docs/B_training_data/b_tools'),
    ('docs/cleanup_20261019/drafts/B_d', 'docs/B_training_data/d_review'),
    ('docs/harvest/THREE_ENGINES_v1.md', 'docs/records/harvest/THREE_ENGINES_v1.md'),
    ('docs/harvest/montage_review.html', 'docs/records/harvest/montage_review.html'),
    ('docs/harvest/vision_failed_lines', 'docs/records/harvest/vision_failed_lines'),
    ('docs/harvest/docai_failed_lines', 'docs/records/harvest/docai_failed_lines'),
    ('docs/glyphs_fixture_labels.json', 'docs/records/glyphs/glyphs_fixture_labels.json'),
    ('docs/cleanup_20261019/drafts/A', 'docs/A_ocr_development'),
    ('docs/O4D_G1_validation_v2.json', 'docs/records/glyphs/O4D_G1_validation_v2.json'),
    ('docs/O4D_G1_validation_v3.json', 'docs/records/glyphs/O4D_G1_validation_v3.json'),
    ('docs/glyphs_shown_batches.json', 'docs/records/glyphs/glyphs_shown_batches.json'),
    ('docs/harvest/PAGE_READS_v1.md', 'docs/records/harvest/PAGE_READS_v1.md'),
    ('docs/harvest/seg_census/tests', 'docs/records/harvest/seg_census/tests'),
    ('docs/harvest/blind_checks_v1', 'docs/records/harvest/blind_checks_v1'),
    ('docs/harvest/seg_census/jobs', 'docs/records/harvest/seg_census/jobs'),
    ('docs/O4D_G1_measure_v1.json', 'docs/records/glyphs/O4D_G1_measure_v1.json'),
    ('docs/O4D_G1_measure_v2.json', 'docs/records/glyphs/O4D_G1_measure_v2.json'),
    ('docs/harvest/MONTAGE_v1.md', 'docs/records/harvest/MONTAGE_v1.md'),
    ('docs/harvest/page_reads_v1', 'docs/records/harvest/page_reads_v1'),
    ('docs/harvest/wikisource_r0', 'docs/records/harvest/wikisource_r0'),
    ('docs/GLYPHS_CALIBRATION.md', 'docs/records/glyphs/GLYPHS_CALIBRATION.md'),
    ('docs/T6_VENDOR_UPDATE.json', 'docs/records/verify_20261008/T6_VENDOR_UPDATE.json'),
    ('docs/t4-pytest-results.xml', 'docs/records/verify_20261008/t4-pytest-results.xml'),
    ('docs/t6-pytest-results.xml', 'docs/records/verify_20261008/t6-pytest-results.xml'),
    ('docs/t8-pytest-results.xml', 'docs/records/verify_20261008/t8-pytest-results.xml'),
    ('docs/harvest/inventory_v2', 'docs/records/harvest/inventory_v2'),
    ('docs/harvest/oa_rebind_v1', 'docs/records/harvest/oa_rebind_v1'),
    ('docs/harvest/openarchives', 'docs/records/harvest/openarchives'),
    ('docs/harvest/PILOT_v1.md', 'docs/records/harvest/PILOT_v1.md'),
    ('docs/harvest/sol_reading', 'docs/records/harvest/sol_reading'),
    ('docs/harvest/collect_v3', 'docs/records/harvest/collect_v3'),
    ('docs/harvest/collection', 'docs/records/harvest/collection'),
    ('docs/harvest/montage_v1', 'docs/records/harvest/montage_v1'),
    ('docs/harvest/parliament', 'docs/records/harvest/parliament'),
    ('docs/harvest/wikisource', 'docs/records/harvest/wikisource'),
    ('docs/pytest-results.xml', 'docs/records/verify_20261008/pytest-results.xml'),
    ('docs/harvest/funnel_v1', 'docs/records/harvest/funnel_v1'),
    ('docs/harvest/pilots_v2', 'docs/records/harvest/pilots_v2'),
    ('docs/harvest/sample_v1', 'docs/records/harvest/sample_v1'),
    ('docs/harvest/screen_v1', 'docs/records/harvest/screen_v1'),
    ('docs/harvest/seg_steps', 'docs/records/harvest/seg_steps'),
    ('docs/GLYPHS_STATE.json', 'docs/records/glyphs/GLYPHS_STATE.json'),
    ('docs/harvest/analysis', 'docs/records/harvest/analysis'),
    ('docs/harvest/cyrillic', 'docs/records/harvest/cyrillic'),
    ('docs/harvest/pilot_v1', 'docs/records/harvest/pilot_v1'),
    ('docs/harvest/recut_v1', 'docs/records/harvest/recut_v1'),
    ('docs/validation.json', 'docs/records/verify_20261008/validation.json'),
    ('docs/harvest/round1', 'docs/records/harvest/round1'),
    ('docs/harvest/round2', 'docs/records/harvest/round2'),
    ('docs/GLYPHS_PLAN.md', 'docs/records/glyphs/GLYPHS_PLAN.md'),
    ('docs/harvest/mixed', 'docs/records/harvest/mixed'),
    ('docs/harvest/vouli', 'docs/records/harvest/vouli'),
    ('docs/harvest/fix1', 'docs/records/harvest/fix1'),
    ('docs/harvest/fix2', 'docs/records/harvest/fix2'),
    ('docs/review/demo', 'docs/B_training_data/d_review/demo'),
    ('docs/labelfix', 'docs/records/labelfix'),
    ('docs/research', 'docs/records/research'),
    ('docs/reviews', 'docs/records/reviews'),
    ('docs/briefs', 'docs/records/briefs'),
    ('docs/tables', 'docs/records/tables'),
)


def _layout_candidates(relative: PurePosixPath) -> tuple[PurePosixPath, ...]:
    value = relative.as_posix()
    for old, new in _LAYOUT_MOVES:
        for source, target in ((old, new), (new, old)):
            if value == source or value.startswith(source + '/'):
                return relative, PurePosixPath(target + value[len(source):])
    return (relative,)


@lru_cache(maxsize=4)
def _receipt_paths(root: Path) -> dict[str, Path]:
    paths = {}
    for shard in sorted((root / RECEIPTS).glob('receipt_*.tsv')):
        with shard.open(newline='') as stream:
            for row in csv.DictReader(stream, delimiter='\t'):
                paths[row['path']] = shard
    return paths


def resolve(repo_relative_path: str | os.PathLike[str]) -> Path:
    """Return the existing repo path, else its mirror under the data root.

    Missing data errors identify the exact receipt shard when known, otherwise
    RECEIPTS/INDEX.md. Absolute and escaping paths are rejected. A dangling
    symlink counts as missing data, since it cannot be loaded by a reader.
    """
    relative = PurePosixPath(os.fspath(repo_relative_path))
    if relative.is_absolute() or '..' in relative.parts or not relative.parts:
        raise ValueError(f'Expected a repo-relative data path: {repo_relative_path!s}')
    candidates = _layout_candidates(relative)
    local = REPO_ROOT / relative
    for candidate in candidates:
        available = REPO_ROOT / candidate
        if available.exists():
            return available
    data_root = os.environ.get('GREEK_OCR_DATA_ROOT')
    external = Path(data_root).expanduser() / relative if data_root else None
    if data_root:
        for candidate in candidates:
            available = Path(data_root).expanduser() / candidate
            if available.exists():
                return available
    receipts = _receipt_paths(REPO_ROOT)
    receipt = next((receipts[p.as_posix()] for p in candidates if p.as_posix() in receipts),
                   REPO_ROOT / RECEIPTS / 'INDEX.md')
    location = str(external) if external is not None else 'GREEK_OCR_DATA_ROOT is unset'
    raise FileNotFoundError(
        f'Missing Greek OCR data: {relative}; tried {local}; {location}. '
        f'Custody receipt: {receipt}. Set GREEK_OCR_DATA_ROOT to the mirrored data directory.'
    )


def input_path(path: str | os.PathLike[str]) -> Path:
    """Adapt existing readers while preserving explicit non-repository inputs.

    Keep a present path exactly as supplied (including cwd-relative paths and
    temporary test inputs). Only missing repo-local paths are sent to resolve;
    an absolute path in another checkout is never silently rebound here.
    """
    original = Path(path)
    if original.exists():
        return original
    try:
        relative = original.absolute().relative_to(REPO_ROOT)
    except ValueError:
        return original
    return resolve(relative)
