"""Freeze metadata exclusions and a 192-C1-line mock; no crop decoding."""
import argparse
import json
from pathlib import Path
import random
from scripts.labelfix.clariden.r1_common import (SEED, canonical_doc, canonical_line, check_disjointness,
    crop_key, document_split, rows, sha256, write_json, write_rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--selection', type=Path, default=Path('.cache/labelfix/clariden/C1_selection.jsonl'))
    ap.add_argument('--out', type=Path, default=Path('artifacts/labelfix_r1/binding'))
    ap.add_argument('--e3', type=Path, default=Path.home()/'Projects/greek-page-ocr/out/e3b/predictions')
    a = ap.parse_args(); a.out.mkdir(parents=True, exist_ok=False)
    selection = list(rows(a.selection)); split = document_split(selection)
    summary_path = Path('docs/labelfix/spellcheck/clariden/C1_selection.summary.json')
    summary = json.loads(summary_path.read_text())
    frozen_path = Path('docs/labelfix/spellcheck/S4_lines.jsonl.gz')
    frozen = list(rows(frozen_path)); held = [l for l in frozen if not l['dev']]
    assert len(held) == 666 and len({l['doc'] for l in held}) == 14
    sets = {}
    for name, docs in [('heldout_14', sorted({l['doc'] for l in held})),
                       ('DEV_3', summary['dev_wikisource_books']),
                       ('summary_heldout_27', summary['held_out_wikisource_books'])]:
        sets[name] = dict(documents=docs, line_ids=[l['line_id'] for l in frozen if l['doc'] in docs])
    sources = [summary_path, frozen_path]
    for name, path in [('import_real_v2_test', Path('docs/harvest/collection/v2/import_real_v2_test.jsonl'))] + [
            (n, a.e3/f'full_s0_{n}.jsonl') for n in ('v2_test','wikisource_human','e1_real_test')]:
        ds, ids = set(), set()
        for r in rows(path):
            ds.add(canonical_doc(r.get('doc', r.get('source_doc_id', ''))))
            ids.add(canonical_line(r.get('id', r.get('line_id', ''))))
        if '' in ds or '' in ids:
            raise ValueError(f'missing identity: {path}')
        sets[name] = dict(documents=sorted(ds), line_ids=sorted(ids)); sources.append(path)
    exclusions = dict(schema='r1-exclusions-v1', sets=sets,
                      sources={str(p):sha256(p) for p in sources}, selection_sha256=sha256(a.selection))
    disjoint = check_disjointness(selection, exclusions)
    write_json(a.out/'exclusions.json', exclusions); write_json(a.out/'disjointness.json', disjoint)
    write_json(a.out/'document_split.json', split)
    # At least one line from each validation document; the remaining lines are C1-only.
    rng = random.Random(SEED)
    chosen = [rng.choice([r for r in selection if r['doc'] == d]) for d in split['validation']]
    seen = {r['id'] for r in chosen}
    chosen += rng.sample([r for r in selection if r['id'] not in seen], 192-len(chosen))
    write_rows(a.out/'mock_selection.jsonl', chosen)
    write_rows(a.out/'heldout_lines.jsonl.gz', [dict(id=l['line_id'], doc=l['doc'], crop=crop_key(l['crop']),
               recogniser_text=l['recogniser_text']) for l in held])
    # Full owner-note checks need some DEV lines. Extract these ONLY on the node, never on the Mac.
    note_files = ['owner_notes_examples_20261016.jsonl','owner_slot_expectations.jsonl','S4_owner_notes_snapshot.jsonl']
    owner_ids = {r['line_id'] for n in note_files for r in rows(Path('docs/labelfix/spellcheck')/n)}
    extra = [l for l in frozen if l['line_id'] in owner_ids and l['dev']]
    write_rows(a.out/'owner_extra_lines.jsonl.gz', [dict(id=l['line_id'],doc=l['doc'],crop=crop_key(l['crop']),
               recogniser_text=l['recogniser_text']) for l in extra])
    write_json(a.out/'prepare_receipt.json',dict(selection_lines=len(selection), selection_documents=len(split['train'])+len(split['validation']),
               heldout_lines=len(held), owner_extra_node_only_lines=len(extra),
               files={str(p.relative_to(a.out)):sha256(p) for p in a.out.iterdir() if p.is_file()}))
    print(json.dumps(dict(disjointness=disjoint,heldout_lines=len(held),owner_extra_node_only_lines=len(extra))), flush=True)


if __name__ == '__main__':
    main()
