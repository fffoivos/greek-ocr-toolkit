"""N1 CPU renderer. Run image operations with the prescribed x86_64 Python."""
import hashlib
import io
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from PIL import Image, ImageDraw
from greekocr.glyphs.components import line_glyphs

SCRATCH = Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad')
COLLECT = Path.home()/'Projects/greek-ocr-toolkit-sol-collect'


def clean_png(image):
    fresh = Image.new('RGB', image.size)
    fresh.paste(image.convert('RGB'))
    buf = io.BytesIO(); fresh.save(buf, format='PNG')
    return buf.getvalue()


def cached_crop(row):
    sys.path.insert(0, str(COLLECT))
    from collect_v3.storage import ensure_crop
    copy = dict(row, crop=str(SCRATCH/'n1_cache/crops'/ (row['crop_sha256']+'.png')))
    return ensure_crop(copy)


def render(crop, geom, destination, *, glyphs=None):
    """Triangles lie wholly in new margins, disjoint from ALL original pixels."""
    destination = Path(destination); destination.mkdir(parents=True, exist_ok=True)
    with Image.open(crop) as opened: image = opened.convert('RGB')
    margin = 12
    line = Image.new('RGB', (image.width, image.height+2*margin), 'white')
    line.paste(image, (0, margin))
    x = min(max(round(geom['gap_center']), 3), image.width-4)
    draw = ImageDraw.Draw(line)
    draw.polygon([(x-3, 2), (x+3, 2), (x, 8)], fill=(128,)*3)
    y = margin+image.height
    draw.polygon([(x, y+3), (x-3, y+9), (x+3, y+9)], fill=(128,)*3)
    bbox = geom['zoom_bbox']
    # White extension retains requested padding even at crop boundaries.
    zoom = Image.new('RGB', (max(1,bbox[2]-bbox[0]), max(1,bbox[3]-bbox[1])), 'white')
    zoom.paste(image, (-bbox[0], -bbox[1]))
    zoom = zoom.resize((zoom.width*3, zoom.height*3), Image.Resampling.LANCZOS)
    # Add markers AFTER scaling, preserving every pixel of the previous zoom.
    marked_zoom = Image.new('RGB', (zoom.width, zoom.height+2*margin), 'white')
    marked_zoom.paste(zoom, (0, margin))
    zx = round((geom['gap_center']-bbox[0])*3)
    draw = ImageDraw.Draw(marked_zoom)
    draw.polygon([(zx-3, 2), (zx+3, 2), (zx, 8)], fill=(128,)*3)
    zy = margin+zoom.height
    draw.polygon([(zx, zy+3), (zx-3, zy+9), (zx+3, zy+9)], fill=(128,)*3)
    zoom = marked_zoom
    out = {}
    for name, im in [('line', line), ('zoom', zoom)]:
        data = clean_png(im); digest = hashlib.sha256(data).hexdigest()
        path = destination/(digest+'.png')
        if not path.exists(): path.write_bytes(data)
        out[name] = str(path); out[name+'_sha256'] = digest
    if glyphs is None: glyphs = line_glyphs(image)
    g0,g1 = geom['gap']; h = geom['digit_height']; top = geom['digit_top']
    # Preserve full components crossing the gap as well as wholly contained marks.
    components = [dict(bbox=[c.x0,c.y0,c.x1,c.y1], height=c.h, width=c.w,
                       centre_y_relative_band=((c.y0+c.y1)/2-top)/h,
                       wholly_inside_gap=(c.x0>=g0 and c.x1<=g1))
                  for c in glyphs.components if c.x1>g0 and c.x0<g1]
    out['measurements'] = dict(digit_top=top, baseline=geom['baseline'], digit_height=h,
        gap_width=geom['gap_width'], components=components, helper_band=glyphs.band.at(geom['gap_center']))
    return out
