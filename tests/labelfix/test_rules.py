"""Rule-engine accept/reject cases for every labelfix rule (no pixels, no model)."""
import unicodedata as ud

import pytest

from greekocr.labelfix.rules import Candidate, InkSummary, decide, rule_for
from greekocr.labelfix.text import classify_diff, clusters, nfd, strip_marks, tokenize


def N(s):
    return ud.normalize('NFD', s)


def cand(google, model, *, mf=100, gf=0, ink=None, trail='', abbr=False, hyphen=False, uncertain=False, gkey=0,
         regime='poly19', gviol=(), mviol=()):
    return Candidate(google_core=N(google), model_core=N(model), diff=None, trailing_punct=trail, leading_punct='',
                     is_abbreviation=abbr, hyphen_line_end=hyphen, regime=regime, regime_uncertain=uncertain,
                     model_freq=mf, google_freq=gf, google_key_freq=gkey, google_violations=list(gviol),
                     model_violations=list(mviol), ink=ink or InkSummary())


def ink(above=1, below=0, obliques=(), dots=False, localised=True, neighbour=0, faint=False, clipped_top=False):
    return InkSummary(True, above, below, list(obliques), dots, above - len(obliques), localised=localised,
                      neighbour_marks=neighbour, faint=faint, clipped_top=clipped_top)


# ----------------------------------------------------------------------------- diff classes

def test_marks_only_one_cluster_is_a_candidate():
    d = classify_diff(N('βήμα'), N('βῆμα'))
    assert d.kind == 'marks' and d.categories == {'accent'} and d.cluster_index == 1


def test_marks_on_two_clusters_is_not_a_candidate():
    assert classify_diff(N('ἀνθρώπου'), N('ἄνθρωπου')) is None


def test_insertion_or_deletion_is_not_a_candidate():
    assert classify_diff(N('χρόνος'), N('χρόνο')) is None
    assert classify_diff(N('τότητα'), N('ποσότητα')) is None


def test_single_base_substitution_from_confusion_list():
    d = classify_diff(N('πάλης'), N('πάλην'))
    assert d is None   # ς/ν is not in the list
    d = classify_diff(N('τέλος'), N('τέλας'))
    assert d.kind == 'base' and d.categories == {'base_sub'}


def test_two_base_substitutions_rejected():
    assert classify_diff(N('ΥΠΟΧΙΛΙΑΡΧΟΣ'), N('ΥΠΟΧΙΑΙΑΡΧΟΣ')) is None   # λ/ι is not in the list
    assert classify_diff(N('ποτε'), N('τοπε')) is None


def test_final_sigma_only_at_word_end():
    assert classify_diff(N('λόγοσ'), N('λόγος')).categories == {'final_sigma'}
    assert classify_diff(N('λόςος'), N('λόσος')) is None


def test_base_change_with_mark_change_is_rejected():
    assert classify_diff(N('βήμε'), N('βῆμι')) is None


# ----------------------------------------------------------------------------- lexicon rule

def test_accept_mark_change_when_google_form_unattested_and_ink_agrees():
    d = decide(cand('βήμα', 'βῆμα', mf=400, gf=0, ink=ink(above=1)))
    assert d.rule == 'accent' and d.accept and d.lexicon_ok and d.ink_ok


def test_both_forms_attested_leaves_google():
    d = decide(cand('ἡ', 'ᾑ', mf=5000, gf=40, ink=ink(above=1, below=1)))
    assert d.rule == 'subscript' and not d.accept and 'both_attested' in d.reason


def test_model_form_below_threshold_rejected():
    d = decide(cand('βήμα', 'βῆμα', mf=4, gf=0, ink=ink(above=1)))
    assert not d.accept and 'model_form_unattested' in d.reason


def test_ratio_policy_accepts_twenty_fold_margin_and_rejects_less():
    assert decide(cand('βήμα', 'βῆμα', mf=400, gf=20, ink=ink(above=1)), policy='ratio').accept
    assert not decide(cand('βήμα', 'βῆμα', mf=300, gf=20, ink=ink(above=1)), policy='ratio').accept


def test_strict_policy_tolerates_corpus_noise_below_attestation():
    d = decide(cand('βήμα', 'βῆμα', mf=400, gf=2, ink=ink(above=1)))
    assert d.accept and 'margin_ok' in d.reason


# ----------------------------------------------------------------------------- ink rule

def test_mark_added_needs_ink_above():
    base = dict(mf=500, gf=0)
    assert decide(cand('εαρος', 'ἔαρος', ink=ink(above=2, obliques=['acute']), **base)).accept
    d = decide(cand('εαρος', 'ἔαρος', ink=ink(above=1, obliques=['acute']), **base))
    assert not d.accept and d.lexicon_ok and not d.ink_ok
    # two blobs but no readable slope: abstain, never accept on count alone
    assert 'abstain:needs_one_oblique' in decide(cand('εαρος', 'ἔαρος', ink=ink(above=2), **base)).reason


def test_no_ink_means_no_correction():
    d = decide(cand('βήμα', 'βῆμα', mf=500, gf=0))
    assert not d.accept and d.reason.endswith('no_ink')


def test_accent_slope_must_agree_with_model():
    d = decide(cand('βῆμα', 'βήμα', mf=500, gf=0, ink=ink(above=1, obliques=['grave'])))
    assert not d.accept and 'slope_disagrees' in d.reason
    assert decide(cand('βῆμα', 'βήμα', mf=500, gf=0, ink=ink(above=1, obliques=['acute']))).accept


def test_circumflex_rejected_when_ink_is_a_single_oblique():
    d = decide(cand('βήμα', 'βῆμα', mf=500, gf=0, ink=ink(above=1, obliques=['acute'])))
    assert not d.accept and 'oblique_but_model_has_circumflex' in d.reason


def test_subscript_needs_blob_below():
    assert decide(cand('ὠδή', 'ᾠδή', mf=200, gf=0, ink=ink(above=1, below=1))).accept
    d = decide(cand('ὠδή', 'ᾠδή', mf=200, gf=0, ink=ink(above=1, below=0)))
    assert not d.accept and 'no_blob_below' in d.reason


def test_subscript_removal_needs_clean_baseline():
    d = decide(cand('ᾠδή', 'ὠδή', mf=200, gf=0, ink=ink(above=1, below=1)))
    assert not d.accept and 'blob_below_but_model_has_none' in d.reason


def test_dialytika_needs_two_dots():
    assert decide(cand('παιδιά', 'παϊδιά', mf=50, gf=0, ink=ink(above=2, dots=True))).rule == 'dialytika'
    assert decide(cand('παιδιά', 'παϊδιά', mf=50, gf=0, ink=ink(above=2, dots=True))).accept
    assert not decide(cand('παιδιά', 'παϊδιά', mf=50, gf=0, ink=ink(above=2, dots=False))).accept


def test_breathing_change_count_match():
    d = decide(cand('ὀ', 'ὁ', mf=90000, gf=3, ink=ink(above=1)))
    assert d.rule == 'breathing' and d.accept


def test_marks_multi_rule_counts():
    d = decide(cand('ωδὴ', 'ᾠδὴ', mf=20, gf=0, ink=ink(above=1, below=1)))
    assert d.rule == 'marks_multi' and d.accept


# ----------------------------------------------------------------------------- final grave

def test_final_grave_uses_slope_not_lexicon():
    c = cand('εὐρύ', 'εὐρὺ', mf=0, gf=1000, ink=ink(above=1, obliques=['grave']))
    d = decide(c)
    assert d.rule == 'final_grave' and d.accept and d.lexicon_ok is None


def test_final_grave_rejects_wrong_slope_and_punctuation():
    assert not decide(cand('εὐρύ', 'εὐρὺ', ink=ink(above=1, obliques=['acute']))).accept
    d = decide(cand('εὐρύ', 'εὐρὺ', ink=ink(above=1, obliques=['grave']), trail=','))
    assert not d.accept and 'before_punctuation' in d.reason


def test_final_grave_needs_exactly_one_oblique():
    assert not decide(cand('εὐρύ', 'εὐρὺ', ink=ink(above=2, obliques=['grave', 'acute']))).accept


def test_acute_grave_swap_not_on_final_syllable_is_accent_rule():
    assert rule_for(classify_diff(N('πὰντα'), N('πάντα'))) == 'accent'


# ----------------------------------------------------------------------------- base letters

def test_base_sub_needs_fifty_fold_margin_no_ink():
    assert decide(cand('τέλας', 'τέλος', mf=5000, gf=0)).accept
    d = decide(cand('τέλας', 'τέλος', mf=5000, gf=200))
    assert not d.accept and 'both_attested' in d.reason
    d = decide(cand('τέλας', 'τέλος', mf=5000, gf=200), policy='ratio')
    assert not d.accept and 'margin_below_50x' in d.reason
    assert decide(cand('τέλας', 'τέλος', mf=5000, gf=100), policy='ratio').accept
    d = decide(cand('τέλας', 'τέλος', mf=100, gf=3))
    assert not d.accept and 'margin_below_50x' in d.reason


def test_base_sub_abstains_when_google_letters_spell_a_word_under_other_marks():
    # Google 'ὁποίοι' is unattested but 'ὁποῖοι' is: a base change (ι->υ) could turn a mark error into another word
    d = decide(cand('ὁποίοι', 'ὁποίου', mf=309, gf=0, gkey=500))
    assert not d.accept and 'abstain:google_letters_attested_with_other_marks' in d.reason


def test_polytonic_mark_never_introduced_in_monotonic_regime():
    d = decide(cand('καλή', 'καλὴ', mf=900, gf=0, ink=ink(above=1, obliques=['grave']), regime='mono'))
    assert not d.accept and d.reason == 'rejected:polytonic_mark_in_monotonic_regime'


def test_final_sigma_rule():
    d = decide(cand('λόγοσ', 'λόγος', mf=8000, gf=0))
    assert d.rule == 'final_sigma' and d.accept


# ----------------------------------------------------------------------------- guards

def test_proper_name_guard():
    d = decide(cand('Ἀθήνα', 'Ἀθῆνα', mf=500, gf=0, ink=ink(above=1)))
    assert not d.accept and d.reason == 'excluded:proper_name'


def test_abbreviation_guard():
    d = decide(cand('σελ', 'σἐλ', mf=500, gf=0, abbr=True, ink=ink(above=1)))
    assert d.reason == 'excluded:abbreviation'


def test_latin_digit_guard():
    assert decide(cand('τ1μή', 'τ1μὴ', mf=500, gf=0, ink=ink(above=1))).reason == 'excluded:latin_or_digit'


def test_hyphen_line_end_guard():
    assert decide(cand('ἀνθρώ', 'ἀνθρῶ', mf=500, gf=0, hyphen=True, ink=ink(above=1))).reason == 'excluded:hyphen_line_end'


def test_all_caps_mark_change_guard():
    assert decide(cand('ΑΘΗΝΑ', 'ΑΘΗΝΆ', mf=500, gf=0, ink=ink(above=1))).reason == 'excluded:all_caps_marks'


def test_non_candidate_difference():
    assert decide(cand('χρόνος', 'χρόνο')).rule == 'none'


# ----------------------------------------------------------------------------- abstentions

def test_abstain_when_vowel_not_localised():
    d = decide(cand('βήμα', 'βῆμα', mf=500, gf=0, ink=ink(above=1, localised=False)))
    assert not d.accept and d.reason.endswith('abstain:localisation_uncertain')


def test_abstain_on_faint_or_clipped_ink():
    assert 'abstain:faint_mark' in decide(cand('βήμα', 'βῆμα', mf=500, gf=0, ink=ink(above=1, faint=True))).reason
    # Google has a mark, the model removes it, and the band is clipped at the top: never a "false absence"
    d = decide(cand('ἔαρος', 'ἐαρος', mf=500, gf=0, ink=ink(above=1, clipped_top=True)))
    assert 'abstain:clipped_top_no_false_absence' in d.reason


def test_mark_removal_abstains_on_a_wide_blob():
    i = ink(above=1); i.wide_blob = True
    d = decide(cand('εὔτ', 'εὐτ', mf=500, gf=0, ink=i))
    assert 'abstain:removal_with_wide_blob' in d.reason
    assert decide(cand('εὔτ', 'εὐτ', mf=500, gf=0, ink=ink(above=1))).accept


def test_abstain_on_neighbouring_marks_when_count_changes():
    d = decide(cand('εαρος', 'ἔαρος', mf=500, gf=0, ink=ink(above=2, neighbour=1)))
    assert 'abstain:neighbouring_marks' in d.reason


def test_abstain_on_uncertain_regime():
    assert decide(cand('βήμα', 'βῆμα', mf=500, gf=0, ink=ink(above=1), uncertain=True)).reason == 'abstain:regime_uncertain'


def test_acute_to_grave_anywhere_needs_slope():
    d = decide(cand('πὰντα', 'πάντα', mf=900, gf=0, ink=ink(above=1)))
    assert d.rule == 'accent' and not d.accept and 'needs_one_oblique' in d.reason
    assert decide(cand('πὰντα', 'πάντα', mf=900, gf=0, ink=ink(above=1, obliques=['acute']))).accept


# ----------------------------------------------------------------------------- policy defaults

def test_line_initial_capitalised_word_allowed_when_common_and_not_a_name():
    c = cand('Βήμα', 'Βῆμα', mf=500, gf=0, ink=ink(above=1))
    assert decide(c).reason == 'excluded:proper_name'
    c = cand('Βήμα', 'Βῆμα', mf=500, gf=0, ink=ink(above=1))
    c.line_initial, c.model_lower_freq, c.name_count = True, 500, 0
    assert decide(c).accept
    c.name_count = 3                                   # looks like a proper name mid-sentence
    assert decide(c).reason == 'excluded:proper_name'
    c.name_count, c.model_lower_freq = 0, 20           # too rare
    assert decide(c).reason == 'excluded:proper_name'


def test_acute_house_style_suppresses_grave_but_not_acute():
    c = cand('εὐρύ', 'εὐρὺ', ink=ink(above=1, obliques=['grave']))
    c.acute_style = True
    assert decide(c).reason == 'abstain:acute_house_style'
    c = cand('εὐρὺ', 'εὐρύ', ink=ink(above=1, obliques=['acute']))
    c.acute_style = True
    assert decide(c).accept


def test_acute_house_style_detector():
    from greekocr.labelfix.candidates import acute_house_style
    poly = [N('καὶ τὸ βῆμα τοῦ ἀνδρὸς ἦν καλὸν καὶ τὸ φῶς αὐτὸ λαμπρόν')] * 2
    assert acute_house_style(poly)[0] is False
    acute = [N('νά μέλψουν ὠδάς καί νά ψάλλουν παιᾶνας πρός αὐτόν καί τόν θεόν')] * 2
    flag, share, n = acute_house_style(acute)
    assert flag and share == 1.0 and n >= 10


# ----------------------------------------------------------------------------- constraint rule

def test_constraint_rule_bypasses_lexicon_but_not_ink():
    # Google 'συνεἶχον' breaks C1 (breathing after a consonant start); the model's 'συνεῖχον' is possible;
    # the model's form is NOT attested (mf=0) yet the correction is accepted on constraint + ink
    d = decide(cand('συνεἶχον', 'συνεῖχον', mf=0, gf=0, ink=ink(above=1), gviol=['C1:breathing_after_consonant_start']))
    assert d.rule == 'constraint' and d.accept and d.base_rule == 'breathing' and d.lexicon_ok is False
    d = decide(cand('συνεἶχον', 'συνεῖχον', mf=0, gf=0, gviol=['C1:breathing_after_consonant_start']))
    assert d.rule == 'constraint' and not d.accept and 'no_ink' in d.reason


def test_constraint_rule_needs_model_form_possible_and_polytonic_regime():
    d = decide(cand('συνεἶχον', 'συνεἷχον', mf=0, ink=ink(above=1), gviol=['C1:x'], mviol=['C1:x']))
    assert d.rule == 'breathing' and not d.accept
    d = decide(cand('συνεἶχον', 'συνεῖχον', mf=0, ink=ink(above=1), gviol=['C1:x'], regime='mono'))
    assert d.rule == 'breathing'


# ----------------------------------------------------------------------------- text helpers

def test_tokenize_splits_punctuation():
    toks = tokenize('«Ὁ νέος», εἶπε.')
    assert [t.core for t in toks] == [N('Ὁ'), N('νέος'), N('εἶπε')]
    assert toks[1].trail == '»,' and toks[0].lead == '«'


def test_clusters_and_strip():
    cl = clusters(N('ᾠδὴ'))
    assert [c.base for c in cl] == ['ω', 'δ', 'η'] and strip_marks(N('ᾠδὴ')) == 'ωδη'
