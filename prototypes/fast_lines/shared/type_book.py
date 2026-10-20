"""Descriptive page/book-relative type geometry, with leave-one-page-out support.

Supplied page identities are metadata, never algorithmic thresholds. No font
family names, script identification, point sizes, or damaged-print verdicts.
"""
import numpy as np


def summarize(pages):
    summaries=[]
    for page in pages:
        lines=[r for r in page['lines'] if not r.get('uncertain',False)]
        heights=[r['xheight']/page['width'] for r in lines]
        # Median of supported lines avoids overcounting long rows as more pages.
        value=float(np.median(heights)) if heights else None
        summaries.append(dict(page=page['page'],support=len(lines),body_page_width=value,
            stroke_xh=float(np.median([r['stroke_xh'] for r in lines if r.get('stroke_xh') is not None])) if any(r.get('stroke_xh') is not None for r in lines) else None,
            gap_xh=float(np.median([r['gap_xh'][1] for r in lines if r.get('gap_xh') is not None])) if any(r.get('gap_xh') is not None for r in lines) else None))
    for i,row in enumerate(summaries):
        others=[r for j,r in enumerate(summaries) if j!=i and r['body_page_width'] is not None]
        ref=float(np.median([r['body_page_width'] for r in others])) if others else None
        row.update(reference_pages=[r['page'] for r in others],other_page_body=ref,
                   relative_to_other_pages=row['body_page_width']/ref if ref and row['body_page_width'] else None)
    return dict(pages=summaries,method='leave-one-page-out median of supported page contact sizes',
                caveat='page-width normalization depends on scan framing; size, spacing and stroke are not font identity')
