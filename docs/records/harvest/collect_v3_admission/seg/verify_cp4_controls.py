"""Reproduce test controls and report both composed and standalone decisions."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
import test_seg_cp4 as t
import test_seg_cp3 as cp3
from greekocr.harvest import geometry_observations as g

def main():
    observed=[]; original=t.observe
    def capture(*a,**kw):
        r=original(*a,**kw); observed.append(r); return r
    t.observe=capture
    for edge in ('top','bottom'):
        for fraction in (.5,.6): t.test_edge_halves_and_sixty_percent(edge,fraction)
    t.test_separated_partial_word_cannot_become_complete_substring()
    for kind in ('marks','noise','rule'): t.test_cc_inflation_never_supplies_bodies(kind)
    t.test_separated_fragment_only_runs_do_not_accumulate()
    original_nine=list(observed)
    for outside in (False,True):t.test_connected_top_stroke_full_native_extent(outside)
    t.test_shared_parent_split_conserves_full_native_ink()
    fragments=list(observed);observed.clear()
    for n in range(1,10):t.test_complete_short_body_runs(n)
    t.test_resolved_joined_letters_keep_native_parent()
    positives=list(observed)
    def counts(rows):
        return dict(required=len(rows),neighbour_drops=sum(r['neighbour_drop'] is True for r in rows),
                    union_drops=sum(r['union_drop'] is True for r in rows),
                    neighbour_unresolved=sum(r['neighbour_drop'] is None for r in rows),
                    union_unresolved=sum(r['union_drop'] is None for r in rows))
    # Reproduce CP3's planted negative acceptance population as well.
    structural = []; original_support = cp3.supported_rows
    def capture_support(*a, **kw):
        r = original_support(*a, **kw); structural.append(r); return r
    cp3.supported_rows = capture_support
    try:
        cp3.test_rows_count_before_owner_fraction(1)
        cp3.test_split_delivery_pieces_one_physical_row()
        cp3.test_short_heading()
        for box in ([0,25,160,55], [0,26,160,54], [0,24,160,56]):
            cp3.test_top_bottom_half_or_sixty_percent_only(box)
        cp3.test_full_row_plus_edge_halves()
        cp3.test_adjacent_columns_do_not_make_multiline()
        for vertical in (False, True): cp3.test_native_rule_cannot_support_row(vertical)
        cp3.test_envelope_without_assigned_body_not_positive()
    finally:
        cp3.supported_rows = original_support
    assert len(structural) == 11 and not any(r['merged'] for r in structural)
    print(json.dumps(dict(cp3_planted=dict(required=len(structural),
                         false_positives=sum(r['merged'] for r in structural),
                         tests_sha256=g.sha(ROOT/'tests/test_seg_cp3.py')),
                         binding=g.implementation_binding(),tests_sha256=g.sha(ROOT/'tests/test_seg_cp4.py'),
                         verifier_sha256=g.sha(__file__),original_fragments=counts(original_nine),fragments=counts(fragments),
                         mechanics=counts(positives),fragment_cases=fragments),indent=2))

if __name__=='__main__':main()
