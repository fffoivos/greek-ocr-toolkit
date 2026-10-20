"""Read-only geometry port from efficiency/build.py, bound by build receipt."""
import base64,math,re,struct,unicodedata as ud
from pathlib import Path
from PIL import Image
def png_size(path):
    with Image.open(path) as im:return im.size
def normal(text):
    return ''.join(ud.normalize('NFC', text).split())


def spans(node):
    return [(int(s.get('startIndex', 0)), int(s['endIndex']))
            for s in node.get('layout', {}).get('textAnchor', {}).get('textSegments', [])]


def anchor_text(doc, node):
    return ''.join(doc['text'][a:b] for a, b in spans(node))


def frame(page, native_size):
    matrix = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
    returned = (page['dimension']['width'], page['dimension']['height'])
    for m in page.get('transforms', []):
        if m['type'] not in (5, 6):
            raise ValueError('Unsupported response transform')
        raw = base64.b64decode(m['data'])
        values = struct.unpack('<' + ('f' if m['type'] == 5 else 'd')*(m['rows']*m['cols']), raw)
        a = [list(values[i*m['cols']:(i+1)*m['cols']]) for i in range(m['rows'])]
        if m['rows'] == 2:
            a.append([0., 0., 1.])
        matrix = [[sum(a[i][k]*matrix[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    if not page.get('transforms') and tuple(returned) != tuple(native_size):
        raise ValueError(f'Unmapped response frame: {returned} vs {native_size}')
    augmented = [matrix[i] + [float(i == j) for j in range(3)] for i in range(3)]
    for col in range(3):
        pivot = max(range(col, 3), key=lambda i: abs(augmented[i][col]))
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        divisor = augmented[col][col]
        if abs(divisor) < 1e-15:
            raise ValueError('Singular response transform')
        augmented[col] = [v/divisor for v in augmented[col]]
        for i in range(3):
            if i != col:
                factor = augmented[i][col]
                augmented[i] = [a-factor*b for a,b in zip(augmented[i], augmented[col])]
    return [row[3:] for row in augmented], returned


def box(node, inverse, returned):
    poly = node.get('layout', {}).get('boundingPoly', {})
    points = poly.get('vertices') or [dict(x=v.get('x', 0)*returned[0], y=v.get('y', 0)*returned[1]) for v in poly.get('normalizedVertices', [])]
    if not points:
        return None
    a = [[sum(inverse[i][j]*[v.get('x', 0), v.get('y', 0), 1][j] for j in range(3)) for i in range(3)] for v in points]
    a = [[p[0]/p[2], p[1]/p[2]] for p in a]
    if not all(math.isfinite(v) for p in a for v in p):
        raise ValueError('Nonfinite response geometry')
    return [min(p[0] for p in a), min(p[1] for p in a), max(p[0] for p in a), max(p[1] for p in a)]


def union(boxes):
    return [min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)]


def inside(b, row_box):
    return b is not None and all([b[0] >= row_box[0], b[1] >= row_box[1], b[2] <= row_box[2], b[3] <= row_box[3]])


def local_box(b, crop_box, size, padding=1):
    sx, sy = size[0]/(crop_box[2]-crop_box[0]), size[1]/(crop_box[3]-crop_box[1])
    out = [max(0, math.floor((b[0]-crop_box[0])*sx)-padding),
           max(0, math.floor((b[1]-crop_box[1])*sy)-padding),
           min(size[0], math.ceil((b[2]-crop_box[0])*sx)+padding),
           min(size[1], math.ceil((b[3]-crop_box[1])*sy)+padding)]
    if out[2] <= out[0] or out[3] <= out[1]:
        raise ValueError(f'Empty mapped box: {out}')
    return out


def graphemes(text):
    out = []
    for i, c in enumerate(text):
        if ud.combining(c) and out:
            out[-1][1] = i+1
        elif not c.isspace():
            out.append([i, i+1])
    return out


def word_geometry(meta, text):
    """Align exact OCR nonspace characters to the supplied (unmasked) text."""
    r = meta['row']; cb = r['crop_bbox']; size = png_size(meta['source_crop'])
    words = list(re.finditer(r'\S+', text))
    response = meta.get('response')
    selected = []; symbols = []; reason = None
    if response:
        doc = read_json(response)['document']; page = doc['pages'][0]
        inverse, returned = frame(page, meta['native_size'])
        for i, token in enumerate(page.get('tokens', [])):
            b = box(token, inverse, returned)
            if inside(b, cb) and i not in r.get('dropped_token_ids', []):
                selected.append({'token_id': i, 'text': anchor_text(doc, token), 'box': b, 'spans': spans(token)})
        selected.sort(key=lambda t: t['spans'][0][0] if t['spans'] else -1)
        owned = [s for t in selected for s in t['spans']]
        for symbol in page.get('symbols', []):
            ss = spans(symbol); b = box(symbol, inverse, returned)
            if b and ss and all(any(a <= x < y <= z for a, z in owned) for x, y in ss):
                symbols.append({'text': anchor_text(doc, symbol), 'box': b, 'spans': ss})
        symbols.sort(key=lambda s: s['spans'][0][0])
        if not selected:
            reason = 'no_token_boxes_inside_crop'
        elif normal(''.join(t['text'] for t in selected)) != normal(text):
            reason = 'token_text_does_not_align_with_supplied_line'
    else:
        reason = 'earlier_v2_response_or_token_boxes_missing'
    geometry = []
    # NFC character offsets excluding whitespace, preserving all word punctuation.
    offset = 0; token_chars = []
    for token in selected:
        token_chars += [(c, token['box'], token['token_id']) for c in normal(token['text'])]
    symbol_chars = []
    for symbol in symbols:
        symbol_chars += [(c, symbol['box']) for c in normal(symbol['text'])]
    symbols_exact = normal(''.join(s['text'] for s in symbols)) == normal(text)
    n = max(1, len(text))
    for widx, match in enumerate(words, 1):
        word = match.group(); chars = normal(word); length = len(chars)
        if reason:
            b = [cb[0]+(cb[2]-cb[0])*match.start()/n, cb[1], cb[0]+(cb[2]-cb[0])*match.end()/n, cb[3]]
            token_ids = []
        else:
            b = union([t[1] for t in token_chars[offset:offset+length]])
            token_ids = sorted({t[2] for t in token_chars[offset:offset+length]})
        word_box = local_box(b, cb, size)
        letters = []
        # Symbol close-ups, otherwise character-count subdivisions of this word.
        for j, (start, end) in enumerate(graphemes(ud.normalize('NFC', word))):
            if not reason and symbols_exact:
                lb = union([s[1] for s in symbol_chars[offset+start:offset+end]])
                approx_letter = False
            else:
                lb = [b[0]+(b[2]-b[0])*start/max(1,length), b[1], b[0]+(b[2]-b[0])*end/max(1,length), b[3]]
                approx_letter = True
            letters.append({'glyph_index': j+1, 'text': ud.normalize('NFC', word)[start:end],
                            'box': local_box(lb, cb, size, padding=2), 'approx_letter_box': approx_letter})
        geometry.append({'word_index': widx, 'text': word, 'box': word_box, 'token_ids': token_ids, 'letters': letters})
        offset += length
    return geometry, reason


