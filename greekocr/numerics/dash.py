"""Unfitted dash geometry. Thresholds are proposals, never printed truth."""
from statistics import median


def geometric_type(ratio):
    return 'hyphen' if ratio < .75 else 'en dash' if ratio < 1.45 else 'em dash'


def digit_widths(row, token, document):
    # Reuse exact anchor validation for every digit, including repeated digits.
    from .slots_geom import locate_slot
    widths = []
    for p in range(token.start, token.end):
        if row['text'][p] in '0123456789':
            g = locate_slot(row, dict(start=p,end=p,glyph='',boundary='left'), document)
            if g['geom_status'] != 'ok':
                return dict(status=g['geom_status'], reason=g.get('reason'), median_digit_width=None)
            box = g['right_digit']; widths.append(box[2]-box[0])
    return dict(status='ok', widths=widths, median_digit_width=median(widths))


def measure_dash(measurements, width_record):
    """Whole, gap-contained components only; crossing digit ink is not a dash.

    Horizontal component criterion is width >= 2*height, width >= 3 native
    pixels. It is fixed a priori, not fitted. Preserve all qualifying strokes;
    multi-stroke slots remain ambiguous for the combiner.
    """
    strokes = []
    for c in measurements.get('components', []):
        if c['wholly_inside_gap'] and c['width'] >= max(3, 2*c['height']):
            w = width_record.get('median_digit_width')
            ratio = c['width']/w if w else None
            strokes.append(dict(bbox=c['bbox'],stroke_length=c['width'],height=c['height'],
                height_relative_band=c['height']/measurements['digit_height'],
                centre_y_relative_band=c['centre_y_relative_band'],dash_len_ratio=ratio,
                geometric_type=geometric_type(ratio) if ratio is not None else None))
    return dict(**width_record, strokes=strokes,
        dash_len_ratio=strokes[0]['dash_len_ratio'] if len(strokes)==1 else None,
        geometric_type=strokes[0]['geometric_type'] if len(strokes)==1 else None,
        thresholds=[.75,1.45], fitted=False)
