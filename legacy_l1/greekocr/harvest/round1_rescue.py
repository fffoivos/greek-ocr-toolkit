"""Offline owner-rescue allocation and accepted-only round-1 union."""
from __future__ import annotations

import copy
import re

from .round1 import positions, replacement_candidates


def rescue_selection(selection, rescues):
    """Resolve only explicit rescues; retain T16 evidence and position policy."""
    bykey = {b['key']: b for b in selection['books']}
    keys = [r['key'] for r in rescues['rescued']]
    blocked = {r['key'] for group in ('stay_out', 'pending_owner_look_1880s')
               for r in rescues.get(group, [])}
    if len(keys) != len(set(keys)) or set(keys) & blocked:
        raise ValueError('duplicate or excluded rescue key')
    books = []
    for rescue in rescues['rescued']:
        original = bykey[rescue['key']]
        if original['decision'] != 'OUT_TYPE':
            raise ValueError('rescue must resolve to a T16 strange-type removal')
        if any(rescue[k] != original[k] for k in ('year', 'decade')):
            raise ValueError('rescue metadata differs from T16')
        b = copy.deepcopy(original)
        b['prior_decision'] = b['decision']
        b['decision'] = 'RESCUED'
        b['reason'] = ['explicit owner rescue; unchanged physical page gate']
        b['allocation'] = 16 if b['decade'] in (1860, 1870) else 13
        b['positions'] = positions(b['pages'], b['allocation'], b['pilot_pages'],
                                   book=b['book'], seed=selection['seed'])
        for pos in b['positions']:
            pos['candidates'] = replacement_candidates(
                pos['page'], b['pages'], b['pilot_pages'],
                [p['page'] for p in b['positions'] if p != pos])
        books.append(b)
    result = {k: copy.deepcopy(selection[k]) for k in
              ('seed', 'quality_limits', 'pilot_gate_sha256', 'pilot_gate_commit', 'stack_commit')}
    result.update(schema='t18-round1-rescue-selection-1', books=books,
                  owner_decision=rescues['owner_decision'], allocation_policy={
                      'policy': 'owner rescue: 13 pages; 16 in 1860s and 1870s',
                      'thin_decades': [1860, 1870], 'default_pages': 13,
                      'thin_pages': 16, 'pilot_pages_excluded': True})
    return result


def combined_manifest(t16, rescue):
    """One accepted-only list, preserving every source row plus its origin."""
    result, seen = [], set()
    for origin, manifest in (('t16', t16), ('rescue', rescue)):
        for page in manifest['pages']:
            if not page['harvest_accepted']:
                continue
            if not page['gate']['accepted'] or not page['selected']:
                raise ValueError('accepted row lacks physical gate or selection')
            identity = (page['book'], page['page'])
            if identity in seen:
                raise ValueError('duplicate accepted book/page')
            seen.add(identity)
            result.append(dict(copy.deepcopy(page), origin=origin))
    return result


def look_relative(book, page):
    # Match all 79 original Finder names: remove filesystem-reserved characters,
    # preserve Greek/punctuation, collapse whitespace, then truncate to 40 chars.
    title = re.sub(r'[/\\:*?"<>|\x00-\x1f]', ' ', book['title'])
    title = re.sub(r'\s+', ' ', title).strip()[:40].strip()
    folder = f"RESCUED_{book['year']}_{title}_{book['key'][:6]}"
    suffix = '_REPL' if page['replacement'] else ''
    return f"accepted/{book['decade']}s/{folder}/p{page['page']:04d}{suffix}.png"
