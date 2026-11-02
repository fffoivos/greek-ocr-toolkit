"""Versioned, codec-aware features; labels and source coordinates never change."""
from bisect import bisect_right
from collections import Counter
import json
import math
from pathlib import Path
import unicodedata as ud

from .common import canonical, digest, info

FEATURE_VERSION = 'release-lines-v1'
BUCKETS = ('greek', 'latin', 'cyrillic', 'digits', 'punctuation', 'other')


class Features:
    def __init__(self, codec, scripts, unicode_version):
        if unicode_version != ud.unidata_version:
            raise ValueError('Python Unicode database differs from pinned Scripts.txt version')
        self.atoms = {a['ch']: a for a in json.loads(Path(codec).read_text())['atoms']}
        self.excluded = {c for c, a in self.atoms.items() if a['kind'] in ('punct', 'sym', 'space', 'digit')}
        self.punctuation = {c for c, a in self.atoms.items() if a['kind'] == 'punct'}
        self.ranges = []
        for line in Path(scripts).read_text().splitlines():
            line = line.split('#')[0].strip()
            if line:
                span, name = map(str.strip, line.split(';'))
                edges = span.split('..')
                self.ranges.append((int(edges[0], 16), int(edges[-1], 16), name))
        self.ranges.sort()
        self.starts = [r[0] for r in self.ranges]
        self.provenance = {'feature_version': FEATURE_VERSION, 'unicode_version': unicode_version,
                           'codec': info(codec), 'scripts': info(scripts), 'code': info(__file__),
                           'letter_method': 'codec-aware NFD-base/name; Unicode Script for other letters'}

    def letter(self, c):
        if c in self.excluded or not ud.category(c).startswith('L'):
            return None, None
        for base in ud.normalize('NFD', c):
            if ud.category(base).startswith('M'):
                continue
            atom = self.atoms.get(base)
            if atom is not None:
                if atom['kind'] != 'base':
                    return None, None
                bucket = {'grek': 'greek', 'latn': 'latin', 'cyrl': 'cyrillic'}.get(atom['script'], 'other')
            else:
                bucket = next((s.lower() for s in ('GREEK', 'LATIN', 'CYRILLIC') if s in ud.name(base, '')), 'other')
            if bucket != 'other':
                return bucket, bucket.capitalize()
            i = bisect_right(self.starts, ord(base)) - 1
            script = self.ranges[i][2] if i >= 0 and ord(base) <= self.ranges[i][1] else 'Unknown'
            return bucket, script if script not in ('Common', 'Inherited') else None
        return None, None

    def compute(self, text, row, variant):
        nfc = ud.normalize('NFC', text)
        counts, scripts = Counter(), set()
        for c in nfc:
            if c.isspace():
                continue
            if ud.category(c) == 'Nd':
                bucket, script = 'digits', None
            elif ud.category(c).startswith('P') or c in self.punctuation:
                bucket, script = 'punctuation', None
            else:
                bucket, script = self.letter(c)
            counts[bucket or 'other'] += 1
            if script:
                scripts.add(script)
        polytonic, greek = False, False
        for c in ud.normalize('NFD', text):
            if ud.category(c).startswith('M'):
                polytonic |= greek and ord(c) in (0x313, 0x314, 0x342, 0x345, 0x300)
            else:
                greek = self.letter(c)[0] == 'greek'
        denom = sum(counts.values())
        result = {'row_key': row['row_key'], 'label_variant': variant, 'feature_version': FEATURE_VERSION,
                  'label_sha256': digest(text), 'length_chars': len(nfc), 'length_raw_codepoints': len(text),
                  'nonspace_chars': denom, 'polytonic_marks_present': polytonic,
                  'numbers_present': counts['digits'] > 0, 'named_scripts': sorted(scripts),
                  'mixed_script': len(scripts) > 1, 'has_capitals': any(ud.category(c) in ('Lu', 'Lt') for c in text),
                  'all_caps': any(c.lower() != c.upper() for c in text) and not any(c.islower() for c in text)}
        for bucket in BUCKETS:
            result[bucket + '_count'] = counts[bucket]
            result[bucket + '_pct'] = 100 * counts[bucket] / denom if denom else 0.0
        languages = row.get('provider_languages') or []
        if isinstance(languages, str):
            languages = json.loads(languages)
        candidates = []
        for language in languages:
            conf = language.get('confidence')
            conf = float(conf) if conf is not None and math.isfinite(float(conf)) else None
            if language.get('languageCode'):
                candidates.append((language['languageCode'], conf))
        heuristic = 'mul' if len(scripts) > 1 else {'Greek': 'el', 'Latin': 'und-Latn', 'Cyrillic': 'und-Cyrl'}.get(next(iter(scripts), ''), 'und')
        if candidates:
            code, conf = sorted(candidates, key=lambda x: (-(x[1] if x[1] is not None else -math.inf), x[0]))[0]
        else:
            code, conf = heuristic, None
        result.update(language_guess=code, language_guess_confidence=conf,
                      language_guess_method='google_detectedLanguages' if candidates else 'script-tag-v1',
                      provider_languages=languages, language_scope=row.get('language_scope'),
                      ocr_confidence=row.get('ocr_confidence'), ocr_confidence_scope=row.get('ocr_confidence_scope'))
        width, height = row.get('width'), row.get('height')
        result.update(crop_width_px=width, crop_height_px=height,
                      crop_aspect=width / height if width is not None and height else None,
                      crop_variant='source', pixel_variant='original_image',
                      coordinate_frame=row.get('coordinate_frame'), line_index_from_top=row.get('top_index'),
                      x_center_norm=None, y_center_norm=None,
                      census_primary_class=row.get('primary_class'), source_script_class=row.get('script_class'))
        # Only an explicitly qualified normalized source polygon supplies a centre.
        polygon = row.get('polygon_norm')
        if isinstance(polygon, str):
            polygon = json.loads(polygon)
        if row.get('frame_status') == 'verified' and polygon:
            xs = [p['x'] if isinstance(p, dict) else p[0] for p in polygon]
            ys = [p['y'] if isinstance(p, dict) else p[1] for p in polygon]
            result.update(x_center_norm=(min(xs) + max(xs)) / 2, y_center_norm=(min(ys) + max(ys)) / 2)
        result['feature_provenance_json'] = canonical(self.provenance)
        return result
