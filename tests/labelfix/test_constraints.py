"""Positive / negative cases for every orthographic constraint."""
import unicodedata as ud

from greekocr.labelfix.constraints import normalise, possible, syllables, violations
from greekocr.labelfix.text import clusters


def N(s):
    return ud.normalize('NFD', s)


def V(s, nxt=None):
    return violations(N(s), N(nxt) if nxt else None)


# C1 initial breathing
def test_c1_initial_vowel_needs_exactly_one_breathing():
    assert possible(N('ἄνθρωπος')) and possible(N('ὁ')) and possible(N('εἰς')) and possible(N('αὐτός'))
    assert 'C1:missing_initial_breathing' in V('ανθρωπος')
    assert 'C1:several_breathings' in V('ἀνἀγκη')
    assert possible(N('αἴ'))                      # diphthong: breathing on the second vowel is the rule
    assert 'C1:breathing_not_initial' in V('αιτἰα')


def test_c1_non_initial_vowel_never_carries_a_breathing():
    assert 'C1:breathing_after_consonant_start' in V('συνεἶχον')
    assert possible(N('συνεῖχον'))
    assert 'C1:breathing_not_initial' in V('ἡδυνἠθην') or 'C1:several_breathings' in V('ἡδυνἠθην')


def test_c1_exceptions_from_the_census():
    assert possible(N('Τυῤῥηνῶν')) and possible(N('ἐῤῥίφθησαν'))      # medial double rho with breathings
    assert possible(N('νἄχω')) and possible(N('ποὖναι')) and possible(N('κἀγώ'))   # coronis after a consonant
    assert 'C1:breathing_after_consonant_start' in V('συνεἶχον')     # a breathing deep inside the word is still impossible
    assert possible(N('ΥΠΟΧΙΛΙΑΡΧΟΣ')) and possible(N('ΕΝ'))          # all-caps: not checked
    assert possible(N('Δίπλα-Μαλάμου'))                                # hyphenated compound: part by part
    assert possible(N('ἀνάμνησή'))                                     # line-final: enclitic may follow on the next line
    assert 'C3:two_accents' in V('ἀνάμνησή', 'καί')
    assert 'C4:accent_before_antepenult' in V('ἀταίριαστο')
    assert possible(N('ἀταίριαστο'), hard_only=True)                   # soft: never used for a correction


def test_c1_initial_rho_and_consonants():
    assert possible(N('ῥήτωρ')) and possible(N('ρήτωρ'))        # absence tolerated on ρ (relaxation)
    assert 'C1:smooth_breathing_on_rho' in V('ῤήτωρ')
    assert possible(N('καί')) and 'C1:breathing_after_consonant_start' in V('κἁί')   # a rough breathing is no coronis


# C2 marks per letter
def test_c2_marks_per_letter():
    assert possible(N('ᾅδης'))                                  # breathing + accent + subscript is legal
    assert 'C2:two_accents_one_letter' in V('χεί͂λος')
    assert 'C2:breathing_with_dialytika' in V('ἰ̈σος')
    assert 'C2:mark_on_consonant' in V('κ̓αί')


# C3 one accent per word, enclitic exception
def test_c3_two_accents_only_before_enclitic():
    assert 'C3:two_accents' in V('ἄνθρωπός', 'λέγει')
    assert possible(N('ἄνθρωπός'))                 # line-final: the enclitic may follow on the next line
    assert possible(N('ἄνθρωπός'), N('τις'))
    assert possible(N('ἄνθρωπός'), N('μου'))
    assert 'C3:two_accents' in V('ἄνθρωπός', 'καί')
    assert 'C3:two_accents' in V('ὅτὲ', 'δὲ')


# C4 accent position
def test_c4_accent_position():
    assert possible(N('ἄνθρωπος'))                               # antepenult
    assert 'C4:accent_before_antepenult' in V('ἄνθρωποισι')
    assert possible(N('καλὸς')) and 'C4:grave_not_final' in V('κὰλος')
    assert possible(N('βῆμα')) and possible(N('ποιεῖν')) and possible(N('τιμῶ')) and possible(N('ᾠδῇ'))
    assert 'C4:circumflex_before_penult' in V('βῆματος')
    assert 'C4:circumflex_on_short_vowel' not in V('τῶλος')
    assert 'C4:circumflex_on_short_vowel' in V('λ' + 'ο\u0342' + 'γος')
    assert 'C4:circumflex_on_short_vowel' in V('τ' + 'ε\u0342' + 'λος')
    assert possible(N('τοῦ')) and possible(N('εὖ'))


# C5 dialytika
def test_c5_dialytika():
    assert possible(N('ἀϋπνία')) and possible(N('παϊδάκι'))
    assert 'C5:dialytika_not_on_iota_upsilon' in V('πα̈ρα')
    assert 'C2:breathing_with_dialytika' in V('ἀϊ̓δής'.replace('ϊ̓', 'ἰ̈'))


# C6 subscript
def test_c6_subscript():
    assert possible(N('ᾠδή')) and possible(N('τῇ')) and possible(N('λόγῳ'))
    assert 'C6:subscript_not_under_alpha_eta_omega' in V('τῃ'.replace('ῃ', 'ι' + 'ͅ'))


# C7 normalisation
def test_c7_mark_order_is_normalised_not_rejected():
    wrong = 'α' + '́' + '̓'      # accent before breathing
    assert normalise(wrong) == 'α' + '̓' + '́'
    assert possible(wrong + 'νθρωπος')


def test_syllables_count_diphthongs_as_one():
    assert len(syllables(clusters(N('ποιεῖν')))) == 2
    assert len(syllables(clusters(N('ἄυλος')))) == 3       # breathing on the first vowel: not a diphthong
    assert len(syllables(clusters(N('ἀϋπνία')))) == 4
