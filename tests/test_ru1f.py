"""Conservative W1-label to retained Google symbol offset mapping."""
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts/secondary'))
from ru1_owner_sheet import google_offset, proposed


@pytest.mark.parametrize('label,google', [
    ('XIV. старый домь стоялъ.', 'ХIV. старый домь стоялъ.'),
    ('Глава - старый домь стоялъ.', 'Глава — старый домь стоялъ.'),
    ('старый домь стоялъ.', '12 старый домь стоялъ.'),
])
def test_convention_elsewhere(label, google):
    assert google_offset(label, google, label.index('ь')) == google.index('ь')


@pytest.mark.parametrize('label,google', [
    ('Это мірь стоялъ.', 'Это мирь стоялъ.'),
    ('Это домь стоялъ.', 'Это домъ стоялъ.'),
    ('Это домь стоялъ.', 'Это надомь стоялъ.'),
])
def test_word_changed_no_zoom(label, google):
    assert google_offset(label, google, label.index('ь')) is None


def test_ambiguous_repeated_word():
    label, google = 'домь домь', 'домь'
    assert google_offset(label, google, 3) is None
    assert google_offset(label, google, 8) is None


def test_repeated_word_identity_is_unambiguous():
    assert google_offset('домь домь', 'домь домь', 8) == 8


def test_proposal_uses_current_label():
    label = 'XIV. домь'
    assert proposed(label, [dict(offset=8, google='ь', kind='final', decision='edit_hard')]) == 'XIV. домъ'
