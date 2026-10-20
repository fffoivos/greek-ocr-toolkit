"""Ingestion of owner decisions, on a synthetic deck and decisions file."""
import json

from greekocr.labelfix.ingest_decisions import main, summarise


def make_deck(tmp_path):
    cards = [
        dict(id='accent-000', rule='accent', kind='sample', shown_is_model=True, line_id='l1', word_index=0, google='βήμα', model='βῆμα'),
        dict(id='accent-001', rule='accent', kind='sample', shown_is_model=True, line_id='l2', word_index=1, google='τελετής', model='τελετῆς'),
        dict(id='accent-002', rule='accent', kind='sample', shown_is_model=False, line_id='l3', word_index=0, google='χώμα', model='χῶμα'),
        dict(id='accent-003', rule='accent', kind='neg', shown_is_model=True, line_id='l4', word_index=2, google='ἔαρος', model='ἐαρος'),
        dict(id='accent-004', rule='accent', kind='pos', shown_is_model=True, line_id='l5', word_index=0, google='βήμα', model='βῆμα'),
        dict(id='final_grave-000', rule='final_grave', kind='sample', shown_is_model=True, line_id='l6', word_index=3, google='καλή', model='καλὴ'),
    ]
    deck = tmp_path / 'deck'
    deck.mkdir()
    (deck / 'deck_data.js').write_text('window.DECK = ' + json.dumps(dict(batches=[dict(rule='accent', cards=cards[:5]),
                                                                                   dict(rule='final_grave', cards=cards[5:])])) + ';\n')
    decisions = [dict(id='accent-000', line_id='l1', word_index=0, decision='y'),
                 dict(id='accent-001', line_id='l2', word_index=1, decision='n'),
                 dict(id='accent-002', line_id='l3', word_index=0, decision='y'),
                 dict(id='accent-003', line_id='l4', word_index=2, decision='y'),    # false yes on a negative control
                 dict(id='accent-004', line_id='l5', word_index=0, decision='u'),
                 dict(id='final_grave-000', line_id='l6', word_index=3, decision='u'),
                 dict(id='ghost-000', line_id='zz', word_index=0, decision='y')]
    dec = tmp_path / 'labelfix_decisions.json'
    dec.write_text(json.dumps(decisions))
    return deck, dec


def test_summary_counts(tmp_path):
    deck, dec = make_deck(tmp_path)
    from greekocr.labelfix.ingest_decisions import load_deck
    per, lines = summarise(load_deck(deck), json.loads(dec.read_text()))
    a = per['accent']
    assert (a['shown'], a['y'], a['n'], a['u']) == (5, 3, 1, 1)
    assert (a['corr_y'], a['corr_n']) == (1, 1)          # precision 50 % on correction cards
    assert a['label_y'] == 1 and a['neg_y'] == 1 and a['pos_u'] == 1
    assert per['final_grave']['u'] == 1
    text = '\n'.join(lines)
    assert 'ignored: 1' in text and '50.0%' in text
    assert 'final_grave: accent ή→ὴ' in text or 'final_grave: accent' in text


def test_main_writes_copy_and_summary(tmp_path):
    deck, dec = make_deck(tmp_path)
    out = tmp_path / 'out'
    assert main(['--deck', str(deck), '--decisions', str(dec), '--out', str(out), '--date', '20261016']) == 0
    assert (out / 'owner_decisions_20261016.json').exists()
    s = (out / 'owner_review_summary.md').read_text()
    assert '| accent | 5 |' in s and 'Most common patterns' in s


def test_main_reports_pending_without_file(tmp_path, monkeypatch):
    import greekocr.labelfix.ingest_decisions as mod
    monkeypatch.setattr(mod, 'find_decisions', lambda: None)
    assert main(['--deck', str(tmp_path), '--out', str(tmp_path / 'o')]) == 3
