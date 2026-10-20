"""C1 selection/statistics helpers; no image processing or model fitting."""
from greekocr.ops.data_root import input_path as _data_input
from collections import Counter
import ast
from functools import lru_cache
import hashlib
import json
from pathlib import Path

from greekocr.labelfix.text import ACCENTS, BREATHINGS, VOWELS, clusters, nfd

COMPOUND_CLASSES = tuple(
    f'{breathing}+{accent}{subscript}'
    for breathing in ('psili', 'dasia')
    for accent in ('acute', 'grave', 'circumflex')
    for subscript in ('', '+subscript')
)


def sha256(path):
    h = hashlib.sha256()
    with _data_input(Path(path)).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def crop_key(path):
    """Canonical cache/output key, independent of Mac/Clariden absolute roots."""
    path = str(path)
    marker = 'docs/harvest/'
    if marker not in path:
        raise ValueError(f'crop is outside docs/harvest: {path}')
    return marker + path.split(marker, 1)[1]


def crop_path(key, root, layout):
    key = crop_key(key)
    if layout == 'toolkit':
        return Path(root) / key
    relative = Path(key).relative_to('docs/harvest/harvest_big')
    wave, crops, *tail = relative.parts
    if crops != 'crops':
        raise ValueError(key)
    return Path(root) / wave / Path(*tail)


def compound_clusters(text):
    """All breathing+accent vowel clusters, including unsupported/malformed ones."""
    return [c for c in clusters(nfd(text)) if c.base in VOWELS
            and set(c.marks) & BREATHINGS and set(c.marks) & ACCENTS]


@lru_cache(maxsize=1)
def text_functions():
    """Load unchanged text-only functions without importing SciPy/ink/model fitting.

    Both complete source files are deployed and hashed. Only these three function
    definitions are compiled; their globals come from the unchanged text module.
    This keeps the E3 inference environment unchanged (it does not contain SciPy).
    """
    from greekocr.labelfix import text
    namespace = dict(vars(text))
    root = Path(text.__file__).parent
    for name, functions in [('candidates.py', ('align_chars', 'pair_tokens')),
                            ('markshape.py', ('mark_class',))]:
        tree = ast.parse((root / name).read_text(encoding='utf-8'))
        nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in functions]
        if {n.name for n in nodes} != set(functions):
            raise ValueError(f'missing expected functions in {name}')
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(root / name), 'exec'), namespace)
    return namespace


def compound_counts(text):
    mark_class = text_functions()['mark_class']
    return Counter(mark_class(c.marks) or 'unsupported' for c in compound_clusters(text))


def agreeing_counts(google, prediction):
    """Use the existing training collector's token pairing and exact NFD core equality."""
    pair_tokens = text_functions()['pair_tokens']
    counts = Counter()
    words = 0
    for g, m in pair_tokens(nfd(google), nfd(prediction)):
        if m is not None and g.core and g.core == m.core:
            words += 1
            counts.update(compound_counts(g.core))
    return words, counts


def read_jsonl(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f]


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
