"""Loaded-keyset policy shared by the builder and offline smoke readback.

Only absent, non-null partner keys qualify. Null identities, ambiguity and
conflicts between present records are defects in either mode.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
import json

from .common import canonical, get, row_key

_context = ContextVar('release_record', default=('release', 'build', 'release'))
_consumer_record = ContextVar('release_consumer_record', default=None)


def consumer_record(source=None, adapter=None, key=None):
    """Remember a yielded record even if unwinding closes its generator."""
    _consumer_record.set((source, adapter, key) if source is not None else None)


def describe(source, adapter, key):
    value = key if isinstance(key, str) else canonical(key)
    return f'source={source} adapter={adapter} key={value[:160]}'


@contextmanager
def diagnostic(source, adapter, key):
    token = _context.set((source, adapter, key))
    try:
        yield
    except Exception as exc:
        if 'source=' in str(exc) and 'adapter=' in str(exc) and 'key=' in str(exc):
            raise
        message = f'{exc} [{describe(source, adapter, key)}]'
        try:
            annotated = type(exc)(message)
        except Exception:
            # JSONDecodeError and similar exceptions require constructor
            # arguments beyond the diagnostic message.
            annotated = ValueError(message)
        raise annotated from exc
    finally:
        _context.reset(token)


def contextual(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        token = _consumer_record.set(None)
        try:
            with diagnostic('release', fn.__name__, kwargs.get('key', fn.__name__)):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    record = _consumer_record.get()
                    if record is not None:
                        with diagnostic(*record):
                            raise
                    raise
        finally:
            _consumer_record.reset(token)
    return wrapped


def source_record(fn):
    @wraps(fn)
    def wrapped(self, original, source, *args, **kwargs):
        key = {k: original.get(k) for k in ('row_key', 'parent_id', 'row_id', 'line_id', 'page_id', 'book_id')
               if original.get(k) is not None}
        key = key or original.get('binding') or (args[0] if args else fn.__name__)
        with diagnostic(source['name'], source['adapter'], key):
            return fn(self, original, source, *args, **kwargs)
    return wrapped


def failure(reason):
    return ValueError(f'{reason} [{describe(*_context.get())}]')


def origin(lock, row, table):
    locator = row.get('source_locator')
    if isinstance(locator, str):
        try:
            locator = json.loads(locator)
        except ValueError:
            locator = None
    path = (locator or {}).get('path') if isinstance(locator, dict) else None
    path = path or row.get('source_shard')
    for source in lock['inputs']:
        if path and any(f['path'] == path for f in source['files']):
            return source['name'], source['adapter']
    return table, table


# These tables are entities. All other tables with dependencies are relations.
# Smoke retains entities and skips only the absent enrichment/check; relations
# to unloaded entities are omitted, so labels cannot reach feature computation.
ENTITIES = {'rows', 'real', 'pages', 'page_images', 'page_frames', 'boxes',
            'segmenter_page_results', 'synthetic', 'book_registry'}


def dependencies(table, row):
    if table in ('pages', 'book_sources'):
        yield 'book_registry', [row.get('book_id')]
    if table in ('boxes', 'page_frames', 'segmenter_page_results'):
        yield 'pages', [row.get('page_id')]
    if table == 'page_images' and row.get('page_id') is not None:
        yield 'pages', [row['page_id']]
    if table == 'pages' and row.get('page_object_id') is not None:
        yield 'page_images', [row['page_object_id']]
    if table == 'boxes' and row.get('page_frame_id') is not None:
        yield 'page_frames', [row['page_frame_id']]
    if table == 'rows':
        used = bool(row.get('trained_in'))
        for field, target in (('box_id', 'boxes'), ('page_id', 'pages'), ('book_id', 'book_registry')):
            if used or row.get(field) is not None:
                yield target, [row.get(field)]
    if table in ('label_versions', 'row_features', 'row_instruments', 'references', 'real'):
        yield 'rows', [row.get('row_key')]
    if table == 'row_features':
        yield 'label_versions', [row.get('label_variant')]
    if table == 'references':
        if row.get('image_sha256'):
            yield 'real', [row.get('row_key')]
        if row.get('label_version'):
            yield 'label_versions', [row['label_version']]
    if table == 'training_membership':
        if row.get('membership_kind') == 'reference_image':
            yield 'references', [row.get('reference_id')]
            return
        if row.get('row_key'):
            yield 'real', [row['row_key']]
        else:
            yield 'synthetic_group', [row.get('synthetic_match_group')]
            if row.get('synthetic_candidate_count') is not None:
                yield 'synthetic_group_count', [row.get('synthetic_match_group'), row['synthetic_candidate_count']]
            if row.get('synthetic_key'):
                yield 'synthetic', json.loads(row['synthetic_key'])
    if table == 'decisions':
        record = row.get('record') or {}
        key = row.get('row_key') or record.get('row_key')
        parent = record.get('parent_id', get(record, 'binding.parent_id'))
        ident = record.get('row_id', get(record, 'binding.id'))
        if not key and parent is not None and ident is not None:
            key = row_key(parent, ident)
        if key:
            yield 'rows', [key]


def check_partners(table, row, lookup, smoke, skip, recorded_only=False, binding_policy=None):
    """Return False only for a smoke-unloaded partner, counting each absent partner once."""
    partners = []
    for target, key in dependencies(table, row):
        binding = binding_policy.fk_binding(table, target) if binding_policy else None
        if binding_policy and binding in binding_policy.entries:
            if not binding_policy.value(binding, table + ' → ' + target + ' FK',
                                        key if all(k is not None for k in key) else None, count=False):
                continue
        if not recorded_only or all(k is not None for k in key):
            partners.append((target, key))
    for target, key in partners:
        if any(k is None for k in key):
            raise failure(f'{table} → {target} FK fails: null partner key {key}')
    valid = True
    for target, key in partners:
        if lookup(target, key) is None:
            allowed = smoke(target, key) if callable(smoke) else smoke
            if allowed:
                skip(target, key)
                valid = False
                continue
            raise failure(f'{table} → {target} FK fails: target missing {canonical(key)[:160]}')
    return valid
