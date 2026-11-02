"""Write-time application of the acceptor's frozen binding status rules."""
import json

from .accept_bindings import BindingPolicy
from .common import get
from .relations import failure

SOURCE_BINDINGS = ('staging.boxes.parsed_provider_fields', 'bibliography.exact_source_locators')


class WriteBindings(BindingPolicy):
    def validate(self, table, row, final=False, count=False):
        if final and table == 'real' and row.get('trained_in'):
            from .common import digest
            binary = (row.get('trainer_image') or {}).get('bytes')
            if binary is None or digest(binary) != row.get('training_image_sha256'):
                raise failure('trained real row lacks exact trainer_image/training_image_sha256')
        binding = 'tables.' + table
        if self.status(binding) == 'historical_unknown':
            raise failure('fabricated historical_unknown table: ' + table)
        columns = self.columns(table)
        if not columns and not (table == 'real' and 'assets.original_crops' in self.entries):
            return row
        reasons = row.setdefault('binding_missing_reasons_json', {})
        for field, binding in columns.items():
            status = self.status(binding)
            # Book enrichment has its own write. Native book/source metadata is
            # not yet a canonical bridge result during the initial observation.
            enriched = field in ('book_id', 'canonical_book_id') or binding == 'bibliography.book_bridge'
            if status != 'historical_unknown' and not final:
                if field not in row or enriched and not row.get('book_bridge_status'):
                    continue
            value = row.get(field)
            reason = (row.get('source_missing_reasons_json') or {}).get(field, {}).get('reason')
            if field in ('lqb_row', 'release_excluded_row'):
                reason = row.get('row_instrument_missing_reason')
            self.value(binding, table + '.' + field, value, reason=reason, count=count)
            if value is None:
                row[field] = None
                reasons[field] = {'binding': binding, 'reason': reason or self.reason(binding),
                                  'evidence': self.entries[binding]['evidence']}
            else:
                reasons.pop(field, None)
        if table == 'real' and 'assets.original_crops' in self.entries:
            image = (row.get('image') or {}).get('bytes')
            from .common import digest
            custody = row.get('original_crop_custody') or {}
            self.original('real.original_image', digest(image) if image is not None else None,
                          custody, row.get('crop_sha256'), count=count)
            if image is None:
                reasons['image'] = {'binding': 'assets.original_crops',
                    'reason': custody.get('reason') or self.reason('assets.original_crops'),
                    'evidence': self.entries['assets.original_crops']['evidence']}
            else:
                reasons.pop('image', None)
        return row


def native_page_fields(row, source, original=None):
    """Keep native page references separate from the release's logical-page FK.

    Indices remain indices. Only explicit source page-number fields populate
    section 3 field 8; no number is parsed from a page identifier.
    """
    refs = list(row.get('source_page_references_json') or [])
    for selector in ('source_page_id', 'page_id', 'observation_page_id', 'source_page',
                     'binding.page_id', 'analysis_page.id',
                     'raw_page_record_json.analysis_page.id', 'raw_page_index'):
        value = get(row, selector, get(original or {}, selector))
        if value is None:
            continue
        namespace = row.get('source_page_namespace') if selector == 'source_page_id' else None
        namespace = namespace or ':'.join(str(v) for v in
            (source['name'], row.get('wave'), row.get('source_object_id'), selector) if v is not None)
        ref = {'id': str(value), 'namespace': namespace, 'selector': selector}
        if ref not in refs:
            refs.append(ref)
    if refs:
        row['source_page_id'] = refs[0]['id']
        row['source_page_namespace'] = refs[0]['namespace']
    row['source_page_references_json'] = refs
    if row.get('page') is None:
        for field in ('page_number', 'physical_page_number'):
            if row.get(field) is not None:
                row['page'] = row[field]
                break
    return row


def source_values(entry, original, row):
    for field in entry.get('coverage', {}):
        dest = {'detectedLanguages': 'detected_languages'}.get(field, field)
        selector = entry.get('value', {}).get('fields', {}).get(dest)
        value = get(original, selector) if selector else row.get(dest)
        if field == 'languageCode':
            languages = row.get('detected_languages') or []
            if isinstance(languages, str):
                languages = json.loads(languages)
            value = next((v['languageCode'] for v in languages if v.get('languageCode')), None)
        yield field, value
