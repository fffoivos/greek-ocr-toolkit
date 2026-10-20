"""Census_04 input joins and output-only diagnostics around the frozen census_03.

The owner segmenter and the baseline pipeline are unchanged. Split inputs change
observation identity; correction evidence is checked against its original identity
before an audited split-only rebind. No reader or admission rule is added.
"""
from contextlib import contextmanager
from copy import deepcopy
import argparse
import gzip
import json
import time
from pathlib import Path

from . import line_pipeline_census as census
from .line_pipeline import canonical, digest, identity, validate_result
from .numeric_cells import classify_cell


def pinned_records(spec):
    """Read a hash-pinned JSONL or JSONL.gz input without changing it."""
    if census.file_sha(spec['path']) != spec['sha256']:
        raise ValueError('pinned input SHA mismatch: ' + spec['path'])
    opener = gzip.open if str(spec['path']).endswith('.gz') else open
    with opener(spec['path'], 'rt', encoding='utf-8') as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)
    if census.file_sha(spec['path']) != spec['sha256']:
        raise ValueError('pinned input changed while reading')


def load_split(spec):
    """Consume finalized SPLIT1 row assignments; proposals are not allocations."""
    assignments, editions = {}, {}
    if spec is None:
        return assignments
    for value in pinned_records(spec):
        parent, rid, edition, split = (value[k] for k in ('parent_id', 'row_id', 'edition_id', 'split'))
        if not all(isinstance(v, str) and v for v in (parent, rid, edition)) or split not in {'train', 'dev', 'test'}:
            raise ValueError('invalid split-input schema')
        key = (parent, rid)
        if key in assignments:
            raise ValueError('duplicate split-input row')
        if edition in editions and editions[edition] != split:
            raise ValueError('split-input edition has conflicting splits')
        editions[edition] = split
        assignments[key] = dict(edition_id=edition, split=split)
    return assignments


def load_frozen(spec):
    """Retain only frozen 0.5 segmentation and identity from the census_03 export."""
    result = {}
    if spec is None:
        return result
    for decision in pinned_records(spec):
        seg = next((s['result'] for s in decision.get('stages', []) if s['stage'] == 'segmentation'), None)
        bound = decision['binding']
        key = (bound['parent_id'], bound['id'])
        if key in result:
            raise ValueError('duplicate frozen decision identity')
        result[key] = dict(crop_sha256=bound['crop_sha256'], raw_text_sha256=decision['raw_text_sha256'],
                           verdict=seg['verdict'] if seg else None,
                           reason=seg['reason'] if seg else 'not_run_due_to_prior_exclusion')
    return result


def diagnostics(row, decision, frozen):
    """Build descriptive evidence only after the complete admission decision."""
    seg = next((s['result'] for s in decision.get('stages', []) if s['stage'] == 'segmentation'), {})
    evidence, frame = seg.get('evidence', {}), seg.get('frame', {})
    box = evidence.get('box_evidence', {})
    rf = box.get('row_frame', {})
    length, height = rf.get('length'), rf.get('height')
    prediction = box.get('prediction', {}).get('expected')
    chars = evidence.get('characters')
    old = frozen.get((row['parent_id'], row['id']))
    if old is not None and (old['crop_sha256'] != row['crop_sha256'] or old['raw_text_sha256'] != digest(row['raw_text'])):
        raise ValueError('frozen diagnostic input identity mismatch')
    return dict(schema='census04-diagnostics-v1',
                box_long_side=max(length, height) if length is not None and height is not None else None,
                box_height=height,
                box_aspect_ratio=max(length, height)/height if length is not None and height else None,
                length_ratio=(chars+1)/(prediction+1) if chars is not None and prediction is not None else None,
                saved_characters=chars,
                **classify_cell(row['raw_text'], frame.get('source_width'), frame.get('source_height')),
                frozen_05=dict(available=old is not None, verdict=old['verdict'] if old else None,
                               reason=old['reason'] if old else 'frozen row unavailable'))


@contextmanager
def integration(config, out, assignments, frozen, diagnostic_builder):
    """Scope additive input/output adapters to a single census invocation."""
    original_canonicalize, original_ledger, original_corrector = census.canonicalize, census.Ledger, census.ArtifactCorrector

    def canonicalize(record, parent, metadata):
        row = original_canonicalize(record, parent, metadata)
        assignment = assignments.get((parent['id'], row['id']))
        if assignment is not None and parent.get('format') == 'collect-v3-features':
            row['split_input'] = dict(original_split=row['split'], original_edition_id=row['edition_id'],
                                      sha256=config['split_input']['sha256'])
            row.update(assignment, edition_identity_status='bound')
        return row

    class Ledger(original_ledger):
        def save_decision(self, row, decision):
            # This runs after Pipeline.evaluate, and is never fed back to it.
            decision = dict(decision, diagnostics=diagnostic_builder(row, decision, frozen))
            return super().save_decision(row, decision)

    class Corrector(original_corrector):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.allow_unregistered_sf7 = config.get('census06_smoke', False)
            if self.allow_unregistered_sf7:
                # Keep the reported smoke inventory at 40/parent, but validate
                # every SF7 record against the full pinned source observations.
                start = time.monotonic()
                self.ledger.db.execute('CREATE TEMP TABLE sf7_observations(parent TEXT,id TEXT,payload TEXT,PRIMARY KEY(parent,id))')
                metadata = json.loads(Path(config['metadata']).read_text())
                for parent in config['parents']:
                    original = parent['source_input']
                    for record in pinned_records(original):
                        row = canonicalize(record, original, metadata)
                        self.ledger.db.execute('INSERT INTO sf7_observations VALUES (?,?,?)',
                            (row['parent_id'], row['id'], canonical(row)))
                self.ledger.db.commit()
                self.ledger.census_timing['sf7_load']['seconds'] += time.monotonic()-start

        def __call__(self, row, tool, expected):
            start = time.monotonic()
            try:
                return super().__call__(row, tool, expected)
            finally:
                if tool == 'polytonic':
                    self.ledger.census_timing['sf7_lookup']['seconds'] += time.monotonic()-start
                    self.ledger.census_timing['sf7_lookup']['calls'] += 1

        def load(self, release):
            start = time.monotonic()
            try:
                return self._load(release)
            finally:
                if release['tool'] == 'polytonic':
                    t = self.ledger.census_timing['sf7_load']
                    t['seconds'] += time.monotonic()-start
                    t['bytes'] += Path(release['path']).stat().st_size
                    t['records'] += self.ledger.db.execute(
                        'SELECT count(*) FROM corrections WHERE tool=? AND parent=?',
                        ('polytonic', release['parent_id'])).fetchone()[0]

        def _load(self, release):
            if not assignments or release.get('format') != 'line-tool-result-v1':
                return super().load(release)
            # Preserve source artifacts, validate their old bindings, then derive
            # new bindings only for assigned rows. All status/edits remain intact.
            target = Path(out)/'split-bound-corrections'/f'{digest(canonical(release))}.jsonl'
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('w') as stream:
                for record in pinned_records(release):
                    bound = record['binding']
                    found = self.ledger.db.execute('SELECT payload FROM observations WHERE parent=? AND id=?',
                                                  (bound['parent_id'], bound['id'])).fetchone()
                    if found is None and self.allow_unregistered_sf7 and release['tool'] == 'polytonic':
                        found = self.ledger.db.execute('SELECT payload FROM sf7_observations WHERE parent=? AND id=?',
                            (bound['parent_id'], bound['id'])).fetchone()
                    if found is None:
                        raise ValueError('correction ID not in registered parent')
                    row = json.loads(found[0])
                    previous = row.get('split_input')
                    original = dict(row, split=previous['original_split']) if previous else row
                    validate_result(record, original, release['tool'], self.versions)
                    if previous:
                        record = deepcopy(record)
                        source_hash = digest(canonical(record))
                        record['binding'] = identity(row)
                        record['evidence'] = dict(record.get('evidence', {}), split_input_binding=dict(
                            source_record_sha256=source_hash, source_artifact_sha256=release['sha256'],
                            original_binding=identity(original), split_input_sha256=config['split_input']['sha256']))
                    stream.write(canonical(record)+'\n')
            return super().load(dict(release, path=str(target), sha256=census.file_sha(target),
                                     source_artifact_sha256=release['sha256']))

    census.canonicalize, census.Ledger, census.ArtifactCorrector = canonicalize, Ledger, Corrector
    try:
        yield
    finally:
        census.canonicalize, census.Ledger, census.ArtifactCorrector = original_canonicalize, original_ledger, original_corrector


def run(config, out, *, diagnostic_builder=diagnostics, **kwargs):
    """Run both split modes through the same unchanged census implementation."""
    if not kwargs.get('execute'):
        return census.run(config, out, **kwargs)
    assignments = load_split(config.get('split_input'))
    frozen = load_frozen(config.get('frozen_05'))
    with integration(config, out, assignments, frozen, diagnostic_builder):
        return census.run(config, out, **kwargs)


def main(*, segmenter_factory=None):
    """CLI used by the real batch script; factory injection is for offline tests."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--allow-local', action='store_true')
    args = parser.parse_args()
    result = run(json.loads(args.config.read_text()), args.out, execute=args.execute,
                 allow_local=args.allow_local, segmenter_factory=segmenter_factory)
    print(canonical({k: v for k, v in result.items() if k not in {'by_stratum', 'outputs'}}))


if __name__ == '__main__':
    main()
