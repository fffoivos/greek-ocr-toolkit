"""Acceptance requirements resolved from the packaged, frozen source contract.

Candidate/rejected probe coverage is evidence, never a required FK denominator.
Package invariants use the selected inputs/features/counts as resolved bindings;
only an explicit binding decision can relax a provenance requirement.
"""
from collections import Counter, defaultdict

from .relations import failure


A12_FIELDS = {
    'font_file_sha256': 'a12.font_file_sha256',
    'text_source_locator': 'a12.text_origin_locator',
    'text_sha256': 'a12.text_origin_sha256',
    'generator_code_sha256': 'a12.historical_generator_code_sha256',
    'generator_binary_sha256': 'a12.historical_generator_binary_sha256',
    'per_line_seed': 'a12.per_line_seed',
    'operation_parameters': 'a12.operation_parameters',
}

# This inventory is also emitted in every successful acceptance report. A
# binding path without a decision entry is an executable part of the spec.
CHECK_BINDINGS = {
    'package bytes, cap, paths, checksums, sanitization': ['hf_pins', 'inputs', 'assets'],
    'HF configs, projection, keys, uniqueness, logical digests, counts, split': ['inputs', 'expected_counts'],
    'embedded hashes, portability, dimensions, consumer decoding': ['inputs', 'assets.original_crops'],
    'pages table and every logical-page FK': ['tables.pages'],
    'native frames, frame FKs, qualified transforms/positions': ['tables.page_frames', 'features'],
    'segmenter page/run table, FK, outcomes/reasons': ['tables.segmenter_page_results'],
    'row to box/page identity and chain': ['joins.rows_to_boxes_pages_books', 'tables.pages'],
    'page/book and book_sources/registry FKs': ['inputs'],
    'row/synthetic book FK, split, protected/exportable assignment': ['bibliography.book_bridge', 'inputs'],
    'original tuple, row key, decisions/reasons, real view, text hashes': ['inputs'],
    'required source/trainer image variants': ['assets.original_crops', 'inputs'],
    'real/synthetic prepared FKs, variants, labels, codec, multiplicity, model/role': ['validation.original_tuple_bridge', 'inputs', 'models', 'run_bindings'],
    'label/row, feature/row/label FKs, label hashes': ['inputs', 'features'],
    'reference/row/real/label FKs and image/label hashes': ['seal04.original_rows_and_references', 'inputs'],
    'row instrument FK, exact original IDs, list hashes and flags': ['tables.row_instruments', 'book_bridge'],
    'source bibliography fields, reasons, source-record hash and coverage': ['bibliography.exact_source_locators', 'bibliography.book_bridge'],
    'parsed provider fields, nested selectors and coverage': ['staging.boxes.parsed_provider_fields'],
    'book bridge candidates, registry/source/instrument hashes, observation coverage': ['bibliography.book_bridge', 'book_bridge'],
    'synthetic observation key, native fingerprint, operations, severity, NFC, images': ['inputs'],
    'synthetic collision groups/sizes, consumed group multiplicity and coverage': ['inputs'],
    'synthetic provenance nulls, seed, parameters, search receipts': list(A12_FIELDS.values()),
    'keyset membership, unions, tuple bridges, directional witnesses/counts': ['reconciliations', 'keyset_bridges', 'census_old_seven_key_reconciliation'],
    'historical audit removal/repeat witnesses': ['audit.removal_and_repeat_witnesses'],
    'population and filtered expected counts': ['population_counts', 'expected_counts'],
    'source key/label/image/relation replay, prepared order, source completeness': ['inputs', 'features', 'assets', 'book_bridge'],
    'independent feature replay, Unicode, buckets, language, crop aspect/position': ['features', 'tables.page_frames'],
    'smoke missing-target witnesses, exact counts, subset-only exception': ['smoke_rows_per_source', 'inputs'],
}


class BindingPolicy:
    def __init__(self, lock, smoke):
        self.lock, self.smoke = lock, smoke
        self.measure = bool(smoke and lock.get('_measure'))
        self.slice_comparisons = {}
        self.entries = {}
        self.nulls = defaultdict(Counter)
        for group, default in (('resolved_bindings', 'resolved'), ('partial_bindings', 'partial'),
                               ('unresolved_bindings', None)):
            for entry in lock.get(group, []):
                field = entry['field']
                status = entry.get('status', 'historical_unknown' if entry.get('historical_unknown') else default)
                if field in self.entries or status not in ('resolved', 'partial', 'historical_unknown', 'pending_resolve: original_crops'):
                    raise failure('duplicate or undecided acceptance binding: ' + field)
                if status != 'resolved' and not (entry.get('reason') and entry.get('evidence')):
                    raise failure('binding null lacks recorded reason/evidence: ' + field)
                if status == 'historical_unknown' and entry.get('value') is not None:
                    raise failure('historical_unknown binding has a fabricated value: ' + field)
                if status == 'pending_resolve: original_crops' and field != 'assets.original_crops':
                    raise failure('original crop pending status on unrelated binding: ' + field)
                self.entries[field] = {**entry, 'status': status}

    def status(self, binding):
        return self.entries.get(binding, {}).get('status', 'resolved')

    def reason(self, binding):
        return self.entries.get(binding, {}).get('reason')

    def value(self, binding, field, value, reason=None, count=True):
        status = self.status(binding)
        if status == 'historical_unknown' and value is not None:
            raise failure(f'{field}: non-null value fabricated under {binding} (historical_unknown)')
        if value is None:
            if status == 'resolved':
                raise failure(f'{field}: required value is null under {binding} (resolved)')
            recorded = self.reason(binding)
            if not recorded or reason is not None and not reason:
                raise failure(f'{field}: null lacks recorded reason under {binding}')
            if count:
                self.nulls[binding + ':' + field][reason or recorded] += 1
        return value is not None

    def original(self, field, value, custody, expected=None, count=True):
        from .original_crops import REASONS, custody_kind
        binding = 'assets.original_crops'
        custody = custody or {}
        if self.status(binding) == 'historical_unknown':
            return self.value(binding, field, value, count=count)
        if value is not None:
            kind = custody_kind(custody)
            valid_kind = (kind == 'recorded_path' and custody.get('recorded_path') or
                          kind == 'embedded_original' and custody.get('embedded_original') or
                          kind == 'index' and custody.get('via_index') and custody.get('index_root') and
                          custody.get('custody_basis') == 'recorded_sha256_in_declared_root_index')
            if not (custody.get('hash_match') and custody.get('recorded_sha256') == expected == value
                    and custody.get('measured_sha256') == value
                    and valid_kind):
                raise failure(field + ': original image lacks recorded-hash custody')
        else:
            reason = custody.get('reason')
            smoke_target = (self.smoke and reason == 'smoke_unloaded_target' and custody.get('smoke_target'))
            if custody.get('hash_match') or reason not in REASONS and not smoke_target:
                raise failure(field + ': missing original image lacks exact custody reason')
            if count:
                self.nulls[binding + ':' + field][reason] += 1
        return value is not None

    def fk_binding(self, table, target):
        if target in ('pages', 'page_frames', 'segmenter_page_results'):
            if (table in ('rows', 'real') and target == 'pages' and
                    self.status('tables.pages') == 'resolved' and
                    self.status('joins.rows_to_boxes_pages_books') != 'resolved'):
                return 'joins.rows_to_boxes_pages_books'
            return 'tables.' + target
        if table in ('rows', 'real') and target == 'boxes':
            return 'joins.rows_to_boxes_pages_books'
        if table in ('rows', 'real', 'synthetic') and target == 'book_registry':
            return 'bibliography.book_bridge' if self.lock.get('book_bridge') else 'joins.rows_to_boxes_pages_books'
        if table == 'references':
            return 'seal04.original_rows_and_references'
        if table == 'row_instruments':
            return 'tables.row_instruments'
        if table == 'training_membership':
            return 'validation.original_tuple_bridge'
        return 'inputs'

    def original_coverage(self, observed):
        """Enforce the measured population decision, using like source-row units."""
        for pop, expected in self.entries.get('assets.original_crops', {}).get('coverage', {}).items():
            actual = observed.get(pop, {})
            extent = dict(selected=actual.get('rows', 0), total=expected['rows'])
            for field in ('rows', 'custody_established'):
                self.coverage('original_crops.' + pop + '.' + field,
                              actual.get(field, 0), expected[field], **extent,
                              unloaded=actual.get('smoke_unloaded_target', 0) if field != 'rows' else 0)
            for reason in set(expected['reasons']) | set(actual.get('reasons', {})):
                self.coverage('original_crops.' + pop + '.' + reason,
                              actual.get('reasons', {}).get(reason, 0), expected['reasons'].get(reason, 0),
                              **extent, unloaded=actual.get('smoke_unloaded_target', 0))

    def original_published_coverage(self, published, observed):
        for pop in self.entries.get('assets.original_crops', {}).get('coverage', {}):
            actual = observed.get(pop, {})
            public = published.get(pop, {})
            if (public.get('rows') != actual['rows'] or
                    sum(public.get(k, 0) for k in ('images', 'null', 'unselected')) != actual['rows'] or
                    not self.smoke and public.get('unselected')):
                raise failure('published original population selection differs: ' + pop)
            expected = self.entries.get('assets.original_crops', {}).get('coverage', {}).get(pop)
            if expected:
                self.coverage('original_crops.' + pop + '.published_images', public['images'],
                              expected['custody_established'], selected=actual['rows'], total=expected['rows'],
                              unloaded=public['unselected'] + public.get('smoke_unloaded_target', 0))
                if expected['custody_established'] == expected['rows']:
                    self.coverage('original_crops.' + pop + '.selected_images', public['images'],
                                  actual['rows'] - public['unselected'] - public.get('smoke_unloaded_target', 0),
                                  exact=True)

    def columns(self, table):
        """Public columns governed by explicit binding decisions, in both writers/readers."""
        fields = {}
        if table in ('rows', 'real', 'boxes', 'page_images', 'page_frames', 'segmenter_page_results'):
            fields['page_id'] = self.fk_binding(table, 'pages')
        if table in ('rows', 'real'):
            fields['box_id'] = self.fk_binding(table, 'boxes')
        if table in ('rows', 'real', 'boxes'):
            fields['page_frame_id'] = 'tables.page_frames'
            fields['segmenter_run_id'] = 'tables.segmenter_page_results'
        if table in ('rows', 'real', 'row_features'):
            fields.update({f: 'tables.page_frames' for f in ('x_center_norm', 'y_center_norm')})
        if table in ('rows', 'real', 'synthetic'):
            fields.update({f: self.fk_binding(table, 'book_registry') for f in ('book_id', 'canonical_book_id')})
            if self.lock.get('book_bridge'):
                from .common import SOURCE_FIELDS
                fields.update({f: 'bibliography.book_bridge' for f in SOURCE_FIELDS})
                fields.update({f: 'bibliography.book_bridge' for f in ('lqb_row', 'release_excluded_row')})
        if table == 'synthetic':
            fields.update(A12_FIELDS)
        if table in ('references', 'row_instruments'):
            fields['row_key'] = self.fk_binding(table, 'rows')
        if table in ('rows', 'real') and not self.lock.get('book_bridge'):
            fields.update({f: 'bibliography.exact_source_locators' for f in
                self.entries.get('bibliography.exact_source_locators', {}).get('coverage', {})})
        if table == 'boxes':
            fields.update({{'detectedLanguages': 'detected_languages'}.get(f, f):
                           'staging.boxes.parsed_provider_fields'
                           for f in self.entries.get('staging.boxes.parsed_provider_fields', {}).get('coverage', {})
                           if f != 'languageCode'})
        return {f: b for f, b in fields.items() if b in self.entries}

    def coverage(self, name, observed, expected, exact=None, *, selected=None, total=None, unloaded=0,
                 comparable=True, enforce=True):
        """Count only like units. Smoke counts are bounded by the full probe.

        Complete denominators are exact, except for the explicitly witnessed
        unloaded portion of a dependent count. Real counts never exceed the
        frozen bound. Full mode cannot be relaxed by any caller flag.
        """
        if unloaded < 0 or not self.smoke and unloaded:
            raise failure(name + ': unloaded targets outside smoke')
        if self.measure:
            # Measure rewrites input files to independent prefixes. Even a
            # complete selected denominator cannot establish that its binding
            # partners survived that rewrite (including zero-count reasons).
            self.slice_comparisons[name] = {
                'status': 'not_measurable_on_slice', 'observed': observed,
                'expected': expected, 'selected': selected, 'total': total,
                'unloaded': unloaded,
                'reason': 'independently sliced inputs do not retain full binding sources',
            }
            return observed == expected
        if self.smoke and not comparable:
            # Set differences against independently selected partners are not
            # subsets of the full difference. Keep the diagnostic only.
            return observed == expected
        complete = selected is not None and selected == total
        exact = not self.smoke or exact is True or complete and not unloaded
        if isinstance(expected, dict):
            if set(observed) - set(expected):
                raise failure('unrecorded coverage values: ' + name)
            for field, value in expected.items():
                if isinstance(value, (int, dict)) and not isinstance(value, bool):
                    self.coverage(name + '.' + field, observed.get(field, {} if isinstance(value, dict) else 0),
                                  value, exact=exact, selected=selected, total=total, unloaded=unloaded)
            return
        passed = not (observed != expected if exact else observed > expected or complete and expected > observed + unloaded)
        if not passed and enforce:
            comparison = '!=' if exact else 'outside frozen bound'
            raise failure(f'{name}: binding coverage count differs: {observed} {comparison} {expected}'
                          + (f' (unloaded={unloaded})' if unloaded else ''))
        return passed

    def report(self):
        return {
            **({'frozen_count_comparisons': dict(sorted(self.slice_comparisons.items()))}
               if self.measure else {}),
            'bindings': {k: {'status': v['status'], 'reason': v.get('reason'), 'evidence': v.get('evidence')}
                         for k, v in sorted(self.entries.items())},
            'checks': {k: [{'binding': b, 'status': self.status(b)} for b in bindings]
                       for k, bindings in CHECK_BINDINGS.items()},
            'reasoned_nulls': {k: {'count': sum(v.values()), 'reasons': dict(v)}
                              for k, v in sorted(self.nulls.items())},
            'reasoned_null_count': sum(sum(v.values()) for v in self.nulls.values()),
            'reasoned_null_units': 'Counts by published field/view, selected source observation, and explicit absent binding; not distinct release rows.',
            'coverage_extent': ('measure slice; frozen comparisons not_measurable_on_slice' if self.measure else
                'bounded loaded subset (exact on complete loaded denominators; witnessed unloaded custody separate)' if self.smoke else 'full exact'),
        }
