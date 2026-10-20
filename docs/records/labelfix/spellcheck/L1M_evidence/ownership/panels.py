"""Native-pixel L1M2 panels, tinted by the supplied aligned ownership labels."""
from collections import defaultdict
from functools import lru_cache
import gzip
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
COLORS = {1: (0, 133, 84), 2: (218, 48, 54), 3: (226, 118, 16),
          4: (148, 66, 181), 5: (26, 112, 219)}
FONT = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 18)
SMALL = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 15)


def load(name):
    return [json.loads(s) for s in gzip.open(HERE / name, 'rt')]


@lru_cache(maxsize=2)
def sample_context(sample):
    lines = {r['id']: r for r in map(json.loads, gzip.open(HERE.parent / sample / 'lines.jsonl.gz', 'rt'))}
    tree = 'l1e_sample_vouli_r2' if sample == 'vouli' else 'l1e_sample_r4'
    root = Path('/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/v2_masked') / tree
    sources = {r['id']: r for r in map(json.loads, (root / 'lines.jsonl').open())}
    return lines, root, sources


def context(flag):
    sample = flag['sample']
    lines, root, sources = sample_context(sample)
    s = sources[flag['id']]
    a = np.array(Image.open(s['original_path']).convert('L'))
    b = np.array(Image.open(root / s['masked_path']).convert('L'))
    omap = np.array(Image.open(root / s['ownership_path']))
    with np.load(HERE.parent / sample / 'pixels' / (flag['id'] + '.npz')) as p:
        oi, mi = p['original_ink'], p['masked_ink']
    return a, b, omap, oi, mi, None


def tinted(gray, omap, visible):
    out = np.repeat(gray[..., None], 3, axis=2).astype(float)
    for label, color in COLORS.items():
        pick = (omap == label) & visible
        out[pick] = .18 * out[pick] + .82 * np.array(color)
    # Detector ink outside the ownership foreground remains black/gray.
    return Image.fromarray(out.astype('uint8'))


def panel(flag, number, category, width=1200):
    a, b, omap, oi, mi, d = context(flag)
    h, w = a.shape
    lo, hi = flag['window']
    margin = max(32, int((hi - lo) * 1.8))
    x0, x1 = max(0, lo - margin), min(w, hi + margin)
    focus = [x0, 0, x1, h]
    scale = min(5, max(2, (width - 90) // (3 * (x1 - x0))))
    zooms = [Image.fromarray(a).convert('RGB'), tinted(a, omap, np.ones_like(oi)), tinted(b, omap, mi)]
    zooms = [im.crop(focus).resize(((x1 - x0) * scale, h * scale), Image.Resampling.NEAREST) for im in zooms]
    zheight = max(im.height for im in zooms)
    canvas = Image.new('RGB', (width, zheight + 225), 'white')
    draw = ImageDraw.Draw(canvas)
    state = 'persists' if flag['persists'] else 'cleared'
    draw.text((15, 10), f'{number:02d}  {category} | {flag["wave"]} {flag["edge"]} | {flag["attribution"]} | {state}', font=FONT, fill='black')
    draw.text((15, 38), f'{flag["id"]}  start={flag["start"]} base={flag["base"]}  blobs={",".join(flag["blob_keys"])}', font=SMALL, fill='black')
    draw.text((15, 62), f'Original border pixels: {flag["border_split"]["class_pixels"]}', font=SMALL, fill='black')
    for i, (im, caption) in enumerate(zip(zooms, ['original gray', 'original + ownership classes', 'masked + surviving ownership'])):
        ox = 15 + i * (width // 3)
        oy = 115
        canvas.paste(im, (ox, oy))
        draw.text((ox, 89), caption, font=FONT, fill='black')
        yy = oy if flag['edge'] == 'top' else oy + im.height - 1
        draw.line([(ox + (lo - x0) * scale, yy), (ox + (hi - x0) * scale - 1, yy)], fill=(0, 180, 230), width=3)
        draw.rectangle([ox, oy, ox + im.width - 1, oy + im.height - 1], outline=(120, 120, 120), width=1)
    y = zheight + 132
    draw.text((15, y), f'Native focus x={x0}:{x1}, y=0:{h}; nearest-neighbour {scale}x. Cyan segment: original clipping window.', font=SMALL, fill='black')
    labels = ['1 own', '2 above', '3 below', '4 unowned', '5 ring abstained']
    for i, label in enumerate(labels, 1):
        x = 15 + (i - 1) * 222
        draw.rectangle([x, y + 29, x + 17, y + 46], fill=COLORS[i])
        draw.text((x + 23, y + 27), label, font=SMALL, fill='black')
    draw.text((15, y + 57), 'Untinted detector ink has ownership label 0. Cropped pixels outside this image are unknown.', font=SMALL, fill='black')
    return canvas, focus


def main():
    flags = load('border_flags.jsonl.gz')
    after = {(f['id'], f['start'], f['edge']): f for f in load('masked_border_flags.jsonl.gz')}
    bykey = {(f['id'], f['start'], f['edge']): f for f in flags}
    selected = []
    used = set()
    # One unambiguous cleared neighbour per wave; alternate edges if possible.
    for wave, edge in [('round1', 'top'), ('round2', 'bottom'), ('mixed', 'top'), ('vouli', 'bottom')]:
        f = next(f for f in flags if f['wave'] == wave and f['edge'] == edge and not f['persists']
                 and f['attribution'].startswith('neighbour') and f['original_sf4_relevant'])
        selected.append((f, 'neighbour-cleared'))
        used.add(f['id'])
    # Bind the three originally requested physical witnesses explicitly.
    old = json.loads((HERE.parent / 'visual_selection.json').read_text())
    for n in (8, 10, 12):
        prior = old[n - 1]
        f = bykey[(prior['id'], prior['start'], prior['edge'])]
        assert f['persists'] and after[(f['id'], f['start'], f['edge'])]['own_ink_clipping']
        selected.append((f, 'own-persistent'))
        used.add(f['id'])
    f = next(f for f in flags if f['wave'] == 'vouli' and f['persists'] and f['id'] not in used
             and f['attribution'] == 'own' and after[(f['id'], f['start'], f['edge'])]['own_ink_clipping']
             and f['ownership_export_status'] != 'identity_ambiguous')
    selected.append((f, 'own-persistent'))
    used.add(f['id'])
    # There are no class-5 blobs: show mixed cases, two surviving/two cleared.
    for wave, persists in [('round1', True), ('round2', True), ('mixed', False), ('vouli', False)]:
        candidates = [f for f in flags if f['wave'] == wave and f['id'] not in used
                      and f['attribution'] == 'mixed' and f['persists'] == persists and f['original_sf4_relevant']]
        # Persistent examples foreground threshold/background residual exceptions.
        candidates.sort(key=lambda f: (-f['border_split']['class_pixels']['background'], f['id'], f['start']))
        f = candidates[0]
        selected.append((f, 'mixed-persistent' if persists else 'mixed-cleared'))
        used.add(f['id'])
    out = HERE / 'panels'
    out.mkdir(exist_ok=True)
    meta, images = [], []
    for n, (f, cat) in enumerate(selected, 1):
        im, focus = panel(f, n, cat)
        path = f'panels/{n:02d}.png'
        im.save(HERE / path)
        meta.append(dict(**f, panel=n, category=cat, path=path, focus=focus))
        images.append(im)
    for group in range(4):
        ims = images[group * 3:group * 3 + 3]
        sheet = Image.new('RGB', (1200, sum(im.height for im in ims) + 20), (235, 235, 235))
        y = 0
        for im in ims:
            sheet.paste(im, (0, y))
            y += im.height + 6
        sheet.save(out / f'sheet_{group + 1}.png')
    (HERE / 'visual_selection.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    # One maximum-extent own flag per candidate line for an exhaustive physical
    # check of the class-1 census; not part of the requested twelve-panel sample.
    own = [f for f in after.values() if f['own_ink_clipping']]
    records = []
    for l in load('lines.jsonl.gz'):
        if not l['own_ink_clipping']:
            continue
        choices = [f for f in own if f['id'] == l['id']]
        choices.sort(key=lambda f: (f['new'], -len(f['own_border_x']), f['start']))
        f = choices[0]
        a, b, omap, oi, mi, d = context(f)
        lo, hi = f['window']
        x0, x1 = max(0, lo - 22), min(a.shape[1], hi + 22)
        focus = [x0, 0, x1, a.shape[0]]
        im = tinted(b, omap, mi).crop(focus)
        scale = min(4, max(2, 350 // im.width))
        im = im.resize((im.width * scale, im.height * scale), Image.Resampling.NEAREST)
        tile = Image.new('RGB', (600, max(175, im.height + 65)), 'white')
        draw = ImageDraw.Draw(tile)
        draw.text((6, 4), f'{len(records)+1:02d} {l["wave"]} {l["id"]}', font=SMALL, fill='black')
        draw.text((6, 24), f'{f["edge"]} start={f["start"]} own={len(f["own_border_x"])} px; sole={l["sole_remaining_AB_hold"]}; {l["extent_xh"]:.3f} xh', font=SMALL, fill='black')
        tile.paste(im, (6, 50))
        records.append((tile, dict(id=l['id'], wave=l['wave'], start=f['start'], edge=f['edge'], focus=focus)))
    review = HERE / 'own_census'
    review.mkdir(exist_ok=True)
    metadata = []
    for group in range((len(records) + 7) // 8):
        chunk = records[group * 8:group * 8 + 8]
        heights = [max(tile.height for tile, _ in chunk[i:i+2]) for i in range(0, len(chunk), 2)]
        sheet = Image.new('RGB', (1200, sum(heights) + 10 * len(heights)), (230, 230, 230))
        y = 0
        for j in range(0, len(chunk), 2):
            for col, (tile, data) in enumerate(chunk[j:j+2]):
                sheet.paste(tile, (col * 600, y))
                metadata.append(dict(**data, sheet=f'own_census/sheet_{group + 1:02d}.png'))
            y += heights[j // 2] + 10
        sheet.save(review / f'sheet_{group + 1:02d}.png')
    (HERE / 'own_census_selection.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
    print(f'Wrote 12 panels and {len(records)} own-line census thumbnails.')


if __name__ == '__main__':
    main()
