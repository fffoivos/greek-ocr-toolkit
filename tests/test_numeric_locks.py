from dataclasses import FrozenInstanceError

import pytest

from greekocr.numerics.locks import load_locks


@pytest.fixture
def lock_dir(tmp_path):
    (tmp_path / 'n1_locked_eval_line_ids.txt').write_text('elstat--chosen\n')
    (tmp_path / 'n1_reserved_doc_line_ids.txt').write_text(
        'elstat--chosen\nelstat--other-page\n')
    (tmp_path / 'n1_reserved_docs.txt').write_text('elstat:book\n')
    return tmp_path


def test_membership(lock_dir):
    locks = load_locks(str(lock_dir))
    assert locks.is_locked_line('elstat--chosen')
    assert not locks.is_locked_line('elstat--other-page')
    assert locks.is_reserved_line('elstat--other-page')
    assert not locks.is_reserved_line('dev')
    assert locks.reserved_docs == frozenset({'elstat:book'})


@pytest.mark.parametrize('line', ['elstat--chosen', 'elstat--other-page'])
def test_fit_rejects_selected_and_unselected_reserved_lines(lock_dir, line):
    with pytest.raises(ValueError, match=line):
        load_locks(lock_dir).assert_fit_rows(x for x in ['dev', line, line])


def test_fit_accepts_development_and_empty_batches(lock_dir):
    locks = load_locks(lock_dir)
    assert locks.assert_fit_rows(iter(['dev', 'another-dev'])) is None
    assert locks.assert_fit_rows([]) is None


def test_immutable(lock_dir):
    with pytest.raises(FrozenInstanceError):
        load_locks(lock_dir).reserved_line_ids = frozenset()


def test_missing_exclusion_fails_closed(lock_dir):
    (lock_dir / 'n1_reserved_doc_line_ids.txt').unlink()
    with pytest.raises(FileNotFoundError):
        load_locks(lock_dir)


def test_inconsistent_lock_fails_closed(lock_dir):
    (lock_dir / 'n1_locked_eval_line_ids.txt').write_text('unreserved\n')
    with pytest.raises(ValueError, match='must be reserved'):
        load_locks(lock_dir)


@pytest.mark.parametrize('content', ['', 'id\nid\n', ' id\n', 'id\n\n'])
def test_malformed_lock_fails_closed(lock_dir, content):
    (lock_dir / 'n1_reserved_doc_line_ids.txt').write_text(content)
    with pytest.raises(ValueError):
        load_locks(lock_dir)


def test_document_identity_validation(lock_dir):
    (lock_dir / 'n1_reserved_docs.txt').write_text('book\n')
    with pytest.raises(ValueError, match='source:item'):
        load_locks(lock_dir)
