"""Additional release gates, never a replacement for inherited acceptance."""
from collections import Counter, defaultdict
import json

from .common import digest


def binding_coverage(builder):
    result = []
    for entry in builder.lock.get('unresolved_bindings', []):
        populations = {}
        governed_tables = {}
        for table in ('rows', 'boxes', 'pages', 'page_frames', 'segmenter_page_results', 'row_features', 'references'):
            fields = [f for f, binding in builder.policy.columns(table).items() if binding == entry['field']]
            if not fields:
                continue
            values = {f: {'null': 0, 'nonnull': 0} for f in fields}
            denominator = 0
            for _, row in builder.store.rows(table):
                denominator += 1
                for field in fields:
                    values[field]['null' if row.get(field) is None else 'nonnull'] += 1
            governed_tables[table] = {'denominator': denominator, 'unit': 'public relation rows', 'fields': values}
        for source in builder.lock['inputs']:
            n = builder.store.db.execute('SELECT COUNT(*) FROM source_witness WHERE s=?', (source['name'],)).fetchone()[0]
            populations[source['name']] = {'denominator': n, 'unit': 'source witnesses (overlapping observations)'}
        result.append({**entry, 'release_consequence': {'value': None, 'reason': entry['reason']},
                       'populations': populations, 'governed_tables': governed_tables,
                       'denominator': sum(p['denominator'] for p in populations.values()),
                       'denominator_unit': 'all selected source witnesses; populations overlap'})
    return result


def raw_coverage(builder):
    groups = defaultdict(lambda: {'rows': 0, 'recovered_raw': 0, 'nulls_by_reason': Counter(), 'responses_present': False})
    responses = builder.lock.get('raw_text_responses', {})
    for _, row in builder.store.rows('rows'):
        if row.get('release') != 'harvest-20261025':
            continue
        wave = str(row.get('wave'))
        group = groups[wave]
        group['rows'] += 1
        group['responses_present'] = bool(responses.get(wave))
        labels = [json.loads(j) for j, in builder.store.db.execute("SELECT j FROM records WHERE t='label_versions' AND json_extract(j,'$.row_key')=? AND json_extract(j,'$.label_variant')='raw'", (row['row_key'],))]
        verified = [r for r in labels if r['text'] is not None and digest(r['text']) == r['text_sha256']]
        if verified:
            group['recovered_raw'] += 1
        else:
            group['nulls_by_reason'][next((r.get('reason') for r in labels if r.get('reason')), 'raw adapter output absent')] += 1
    return groups


def raw_acceptance(acceptor):
    from .accept_dataset import require
    coverage = acceptor.coverage.get('raw_text', {})
    observed = defaultdict(lambda: [0, 0])
    for _, row in acceptor.items('rows'):
        if row.get('release') != 'harvest-20261025':
            continue
        wave = str(row.get('wave'))
        observed[wave][0] += 1
        labels = [json.loads(j) for j, in acceptor.db.execute("SELECT j FROM r WHERE t='label_versions' AND json_extract(j,'$.row_key')=? AND json_extract(j,'$.label_variant')='raw'", (row['row_key'],))]
        valid = [r for r in labels if r['text'] is not None and digest(r['text']) == r['text_sha256']]
        for label in valid:
            if label.get('row_source_locator') is not None:
                require(label['text_sha256'] == row.get('raw_text_sha256') and label['row_source_locator'] == row.get('source_locator'), 'recovered raw value differs from recorded row hash/locator')
        observed[wave][1] += bool(valid)
        if not valid:
            require(any(r['text'] is None and r.get('reason') for r in labels), 'missing harvest raw text without per-row null reason')
    for wave, (rows, recovered) in observed.items():
        group = coverage.get(wave, {})
        require(group.get('rows') == rows and group.get('recovered_raw') == recovered, 'raw coverage denominator differs')
        response_binding = acceptor.lock.get('raw_text_responses', {})
        if not acceptor.policy.smoke and acceptor.manifest.get('frozen_trained', {}).get('files'):
            require(wave in response_binding, 'missing explicit wave response-presence binding: ' + wave)
        present = bool(response_binding.get(wave))
        require(group.get('responses_present') == present, 'raw response presence differs from lock')
        require(not present or recovered > 0, 'wave has responses but zero recovered raw values: ' + wave)
    require(len(acceptor.coverage.get('unresolved_binding_consequences', [])) == len(acceptor.lock.get('unresolved_bindings', [])), 'unresolved binding coverage omitted')
