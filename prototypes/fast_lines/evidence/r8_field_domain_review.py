"""Offline audit of actual M15 inverse-domain observations, never a runtime import."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from ..shared import detector, geometry_page_field as field
from ..stack import Stack


def run(inputs, out):
    rows = json.loads(Path(inputs).read_text())['pages']
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    original_inverse = field.invert_points
    records = []
    page_records = []
    current = None

    def observe(xs, knots, mesh, points):
        result = original_inverse(xs, knots, mesh, points)
        caller = sys._getframe(1)
        if caller.f_code.co_name != 'render':
            return result
        local = caller.f_locals
        components = {tuple(q['centre']): q for q in local['local_bodies']}
        for point in points[~np.isfinite(result)]:
            x, y = point
            delta = np.array([np.interp(x, xs, row) for row in mesh])
            warped = knots + delta
            old_phase = float(np.interp(y, warped, knots))
            records.append(dict(page=current['page'], input_sha256=current['sha256'],
                component=components[tuple(point)], scale=local['source']['scale'],
                native_region=list(local['region']), engineering_height=local['h'],
                point_native=point.tolist(), inverse_phase=None,
                old_clamped_phase=old_phase, xs=xs.tolist(),
                first_curve=(knots[0] + mesh[0]).tolist(),
                last_curve=(knots[-1] + mesh[-1]).tolist(),
                observation='M14 component in actual M15 working raster; not a semantic glyph/row class',
                raster='exclusion-painted copy' if local['working'] is not local['gray'] else 'native gray',
                exclusions=len(local['excluded_regions'])))
        return result

    field.invert_points = observe
    old_model = detector.MODEL
    detector.MODEL = Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/onnx/PP-OCRv6_small_det.onnx')
    try:
        stack = Stack()
        for current in rows:
            assert hashlib.sha256(Path(current['path']).read_bytes()).hexdigest() == current['sha256']
            first = len(records)
            result = stack(current['path'], parked=current.get('parked', False))
            gray = cv2.imread(current['path'], 0)
            for i, r in enumerate(records[first:], start=first):
                x, y = r['point_native']; h = r['engineering_height']
                a, b = np.maximum(0, np.floor([x-4*h, y-3*h])).astype(int)
                c, d = np.minimum(gray.shape[::-1], np.ceil([x+4*h, y+3*h])).astype(int)
                raw = Image.fromarray(gray[b:d, a:c]).convert('RGB'); view = raw.copy()
                dr = ImageDraw.Draw(view)
                for name in ('first_curve', 'last_curve'):
                    dr.line([(xx-a, yy-b) for xx, yy in zip(r['xs'], r[name])], fill='red', width=2)
                l,t,z,w = r['component']['bbox']
                dr.rectangle((l-a,t-b,z-a,w-b), outline='blue', width=1)
                dr.ellipse((x-a-3,y-b-3,x-a+3,y-b+3), fill='magenta')
                sheet=Image.new('RGB',(raw.width,2*raw.height+24),'white')
                sheet.paste(raw,(0,24));sheet.paste(view,(0,24+raw.height))
                ImageDraw.Draw(sheet).text((3,3),f"{r['page']} M14 label {r['component']['id']} unknown phase",fill='black')
                name=f'point-{i:03}.png';sheet.save(out/name)
                r.update(image=name,native_crop=[int(a),int(b),int(c),int(d)],review='pending')
            page_records.append(dict(page=current['page'],outside_selected_components=len(records)-first,items=len(result['items'])))
            print(current['page'],len(records)-first,flush=True)
    finally:
        field.invert_points=original_inverse
        detector.MODEL=old_model
    (out/'observations.json').write_text(json.dumps(records,indent=2)+'\n')
    (out/'receipt.json').write_text(json.dumps(dict(pages=page_records,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),runtime_sha256=hashlib.sha256(Path(field.__file__).read_bytes()).hexdigest(),input_sha256=hashlib.sha256(Path(inputs).read_bytes()).hexdigest(),scope='Offline instrumented actual Stack; timings not used'),indent=2)+'\n')


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('inputs');p.add_argument('out');a=p.parse_args();run(a.inputs,a.out)
