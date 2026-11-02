"""Approved P2n native harvest link; this does not assign pinned-v2 identities."""
import json

from .common import row_key

POLICY = 'harvest-explicit-decision-book-id-v1'
REASON = 'release metadata explicitly links the historical decision book ID to its release book ID'


def observation(row, lock):
    """Bind the writer to its selected input, rather than trusting source fields."""
    try:
        locator = json.loads(row['source_locator'])
    except (KeyError, TypeError, ValueError):
        return None
    if not isinstance(locator, dict):
        return None
    for source in lock['inputs']:
        if any(f['path'] == locator.get('path') and f['sha256'] == locator.get('sha256')
               == row.get('source_sha256') for f in source['files']):
            return {'source': source['name'], 'adapter': source['adapter'], 'locator': locator,
                    'book_id': row.get('book_id'), 'canonical_book_id': row.get('canonical_book_id'),
                    'decision_book_id': row.get('decision_book_id'),
                    'decision_sha256': row.get('decision_sha256')}
    return None


def resolve(prior, value, lock):
    """Return evidence only for decisions -> release metadata on the same tuple.

    The Store still checks all six other guarded fields before accepting this
    result. No reverse merge, third writer or inferred book alias is admitted.
    """
    left, right = observation(prior, lock), observation(value, lock)
    if not left or not right or (left['source'], left['adapter'], right['source'], right['adapter']) != (
            'harvest_decisions', 'harvest', 'harvest', 'harvest'):
        return None
    if any(prior.get(f) is None or prior[f] != value.get(f) for f in ('row_key', 'parent_id', 'row_id', 'wave')):
        return None
    if value['row_key'] != row_key(value['parent_id'], value['row_id']):
        return None
    if (not prior.get('book_id') or not value.get('book_id') or
            value.get('decision_book_id') != prior['book_id'] or
            value.get('canonical_book_id') != value['book_id']):
        return None
    return {'source_decision_book_id': prior['book_id'], 'book_id_conflict': True,
            'book_id_conflict_reason': REASON,
            'book_id_resolution_json': {'policy': POLICY, 'field': 'book_id',
                'row_key': value['row_key'], 'wave': value['wave'], 'native_source': value.get('source'),
                'selected_book_id': value['book_id'], 'decision': left, 'metadata': right}}


def coverage(rows):
    """Distinct stored rows make counts durable and independent of replay writes."""
    from collections import Counter
    waves, sources, pairs = Counter(), Counter(), Counter()
    count = 0
    for row in rows:
        if not row.get('book_id_conflict'):
            continue
        evidence = row['book_id_resolution_json']
        count += 1
        waves[evidence['wave']] += 1
        sources[evidence['wave'], evidence['native_source']] += 1
        a, b = evidence['decision'], evidence['metadata']
        pairs[evidence['wave'], a['source'], a['adapter'], b['source'], b['adapter']] += 1
    return {'policy': POLICY, 'field': 'book_id', 'linked_conflicting_rows': count,
            'unit': 'distinct native rows; replay writes are not additional conflicts',
            'by_wave': dict(sorted(waves.items())),
            'by_wave_native_source': [dict(wave=w, native_source=s, rows=n)
                for (w, s), n in sorted(sources.items(), key=lambda item: repr(item[0]))],
            'by_wave_source_adapter_pair': [dict(wave=w, left_source=ls, left_adapter=la,
                right_source=rs, right_adapter=ra, rows=n)
                for (w, ls, la, rs, ra), n in sorted(pairs.items())],
            'uncovered_conflicts': 'fatal; no successful build reports an uncovered conflict'}
