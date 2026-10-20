"""Lexicon admission, regime purity, inflection-aware lookup, proper-name evidence, held-out exclusion."""
import json
import unicodedata as ud

from greekocr.labelfix.lexicon import (Lexicon, admissible_tokens, build_regime, capitalised_mid_sentence,
                                       line_regime_ok, lookup_variants, shingles)


def N(s):
    return ud.normalize('NFD', s)


def C(s):
    return ud.normalize('NFC', s)


def test_admissible_tokens_drop_caps_latin_digits_and_lowercase_initials():
    toks = [C(t) for t in admissible_tokens(N('Ὁ ΝΟΜΟΣ τοῦ 1864 Abc ἔτους, εἶπε.'))]
    # a one-letter capital ('Ὁ') is indistinguishable from an all-caps word and is dropped too
    assert toks == ['τοῦ', 'ἔτους', 'εἶπε']
    assert [C(t) for t in admissible_tokens(N('Καὶ ὁ νόμος'))] == ['καὶ', 'ὁ', 'νόμος']


def test_regime_purity():
    assert line_regime_ok(N('καὶ τὸ βῆμα'), 'poly19') and not line_regime_ok(N('καὶ τὸ βῆμα'), 'mono')
    assert line_regime_ok(N('και το βήμα'), 'mono') and not line_regime_ok(N('και το βήμα'), 'poly19')


def test_lookup_variants_grave_and_enclitic_accent():
    assert [C(v) for v in lookup_variants(N('καλὸς'))] == ['καλὸς', 'καλός']
    assert [C(v) for v in lookup_variants(N('ἄνθρωπός'))] == ['ἄνθρωπός', 'ἄνθρωπος']
    lex = Lexicon('poly19', {N('ἄνθρωπος'): 40, N('καλός'): 7})
    lex.finalize()
    assert lex.freq(N('ἄνθρωπός')) == 40 and lex.freq(N('καλὸς')) == 7 and lex.freq_exact(N('καλὸς')) == 0


def test_capitalised_mid_sentence_is_name_evidence():
    assert [C(v) for v in capitalised_mid_sentence(N('Ὁ Σωκράτης εἶπε. Καὶ ὁ Πλάτων ἀπῆλθεν'))] == ['σωκράτης', 'πλάτων']


def test_build_regime_holds_out_overlapping_documents(tmp_path):
    raw = tmp_path / 'raw'
    raw.mkdir()
    eval_text = N('ὁ νέος ἐλυπήθη σφόδρα καὶ ἀπῆλθεν εἰς τὴν οἰκίαν')
    excl = shingles(eval_text)
    rows = []
    for k in range(25):   # a document whose lines overlap the eval text 25 times -> held out whole
        rows.append(dict(text=eval_text + f' {k}', source_doc_id='held-out-work'))
        rows.append(dict(text=N('ἄλλο κείμενον τοῦ αὐτοῦ ἔργου ') + f'{k}', source_doc_id='held-out-work'))
    rows.append(dict(text=N('ἕτερον βιβλίον μὲ λέξεις ἰδικάς του'), source_doc_id='other-work'))
    (raw / 'src.jsonl').write_text('\n'.join(json.dumps(r, ensure_ascii=False) for r in rows))
    import greekocr.labelfix.lexicon as mod
    old = mod.SOURCES['poly19']
    mod.SOURCES['poly19'] = [('src', 'src.jsonl', 'test')]
    try:
        lex = build_regime('poly19', raw, exclude_shingles=excl, log=lambda s: None)
    finally:
        mod.SOURCES['poly19'] = old
    assert lex.freq(N('κείμενον')) == 0          # the whole held-out document is gone, not only overlapping lines
    assert lex.freq(N('ἕτερον')) == 1
    assert lex.meta['sources'][0]['docs_excluded_by_overlap'] == 1
