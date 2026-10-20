"""Read-only local source snapshot; writes only this workspace, never git state."""
from __future__ import annotations
import ast
import hashlib
import json
import pathlib
import re
import subprocess

DEST = pathlib.Path(__file__).resolve().parents[1]
SOURCE = pathlib.Path('/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr')
GLOSS = pathlib.Path('/Users/foivoskarounos-zamparloukos/Projects/glossapi-development')
PODS = pathlib.Path('/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local')
PREFIX = 'greekocr._vendor.'
ROOTS = ['train/mix.py', 'train/model.py', 'train/train.py', 'train/eval_cer.py',
         'bench/e1_eval.py', 'bench/e1_readout.py', 'bench/o4b_textlayer_lines.py',
         'bench/o4b_adjudicate.py', 'bench/o4b_common.py', 'bench/o4b_import_datasets.py',
         'bench/o4b_partition.py', 'bench/o4b_fetch.py', 'bench/line_categories.py',
         'bench/e2_teachers.py', 'bench/e2_native.py', 'bench/e2_cllg_contract.py',
         'bench/e2_reader_parity.py', 'bench/e2_bakeoff.py', 'bench/e2_warmstart.py',
         'bench/e2_models.py', 'bench/e2_parity.py']


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def local_module(name: str) -> str | None:
    if name in ('bench','train','rec','pipeline','scripts') and (SOURCE/name).is_dir():
        return name
    if (SOURCE / (name.replace('.', '/') + '.py')).is_file():
        return name
    if (SOURCE / 'train' / (name + '.py')).is_file():
        return 'train.' + name
    if (SOURCE / 'scripts/fetch' / (name + '.py')).is_file():
        return 'scripts.fetch.' + name
    if name.split('.')[0] in ('bench','train','rec','pipeline','scripts') and (SOURCE/name.replace('.', '/')).is_dir():
        return name
    return None


def relocate(text: str) -> str:
    """Edit imports and import-hook strings only; retain all other source bytes."""
    tree = ast.parse(text)
    lines = text.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    def pos(line: int, byte: int) -> int:
        return offsets[line - 1] + len(lines[line - 1].encode()[:byte].decode())
    edits = []
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    for n in ast.walk(tree):
        replacement = None
        if isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
            module = local_module(n.module)
            if module:
                replacement = 'from ' + PREFIX + module + ' import ' + ', '.join(
                    a.name + (' as ' + a.asname if a.asname else '') for a in n.names)
        elif isinstance(n, ast.Import):
            pieces = []
            changed = False
            for a in n.names:
                module = local_module(a.name)
                if module:
                    changed = True
                    if a.asname:
                        pieces.append('import ' + PREFIX + module + ' as ' + a.asname)
                    elif '.' not in a.name:
                        parent, leaf = module.rsplit('.', 1) if '.' in module else ('', module)
                        pieces.append('from ' + PREFIX.rstrip('.') + ('.' + parent if parent else '') + ' import ' + leaf)
                    else:
                        raise ValueError('review dotted import without alias: ' + a.name)
                else:
                    pieces.append('import ' + a.name + (' as ' + a.asname if a.asname else ''))
            if changed:
                replacement = '; '.join(pieces)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str):
            # Contract hooks, importlib and python -m commands are import paths too.
            if re.fullmatch(r'(?:bench|train|pipeline|rec)\.[\w.]+(?::\w+)?', n.value):
                replacement = repr(PREFIX + n.value)
            elif n.value in ('model', 'data', 'cer', 'ckpt_io', 'eval_cer') and isinstance(parents.get(n), ast.Call) and isinstance(parents[n].func, ast.Attribute) and parents[n].func.attr == 'import_module':
                replacement = repr(PREFIX + 'train.' + n.value)
        if replacement is not None:
            edits.append((pos(n.lineno, n.col_offset), pos(n.end_lineno, n.end_col_offset), replacement))
    for start, end, replacement in sorted(edits, reverse=True):
        text = text[:start] + replacement + text[end:]
    return text


def logic_hash(text: str) -> str:
    """AST binding of every non-import statement (normalize relocated hooks only)."""
    class Normalize(ast.NodeTransformer):
        def visit_Import(self, node):
            return None
        def visit_ImportFrom(self, node):
            return None
        def visit_Constant(self, node):
            if isinstance(node.value, str) and node.value.startswith(PREFIX):
                value = node.value[len(PREFIX):]
                if value.startswith('train.') and value[6:] in ('model','data','cer','ckpt_io','eval_cer'):
                    value = value[6:]
                node.value = value
            return node
    def stable(node):
        if isinstance(node, ast.AST):
            return {'node': type(node).__name__, 'fields': {
                name: stable(value) for name, value in ast.iter_fields(node)
                if name != 'type_params' or value}}
        if isinstance(node, list): return [stable(value) for value in node]
        if isinstance(node, bytes): return {'bytes': node.hex()}
        if isinstance(node, complex): return {'complex': repr(node)}
        if node is Ellipsis: return {'ellipsis': True}
        return node
    # ast.dump changed its empty-field rendering in Python 3.13; receipts must
    # be reproducible on supported Python 3.11 as well as the snapshot host.
    return sha(json.dumps(stable(Normalize().visit(ast.parse(text))), sort_keys=True).encode())


def head(repo: pathlib.Path) -> str | None:
    result = subprocess.run(['git', '--no-optional-locks', '-C', str(repo), 'rev-parse', 'HEAD'], text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else None


def snapshot() -> None:
    entries = []
    heads = {r: head(r) for r in (SOURCE, GLOSS, PODS, DEST)}
    def copy(src: pathlib.Path, target: pathlib.Path, repo: pathlib.Path | None, rewrite: bool = False, fixture_root: bool = False) -> None:
        raw = src.read_bytes()
        data = relocate(raw.decode()).encode() if rewrite and src.suffix == '.py' else raw
        if fixture_root:
            data = data.replace(b"F=c.EVIDENCE/'fixtures'", b"F=Path(__file__).resolve().parent/'fixtures/o4c'")
            data = data.replace(b"c.EVIDENCE/'print_reviews.jsonl'", b"F/'print_reviews.jsonl'")
            data = data.replace(b"c.ROOT/probe['local_path']", b"F/'review_pages'/Path(probe['local_path']).name")
        path = DEST / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        blob_sha = None
        if repo is not None and heads.get(repo):
            p = subprocess.run(['git', '--no-optional-locks', '-C', str(repo), 'cat-file', 'blob',
                                'HEAD:' + str(src.relative_to(repo))], capture_output=True)
            if p.returncode == 0:
                blob_sha = sha(p.stdout)
        entry = dict(path=str(target), origin=str(src), commit=heads.get(repo),
                     source_sha256=sha(raw), vendored_sha256=sha(data), head_blob_sha256=blob_sha,
                     source_state=('unversioned' if not heads.get(repo) else 'untracked' if blob_sha is None
                                   else 'HEAD' if blob_sha == sha(raw) else 'modified working copy'),
                     transform='Imports/hooks and fixture resource root relocated' if fixture_root else 'Python import paths and hook strings relocated' if data != raw else 'byte-identical')
        if rewrite and src.suffix == '.py':
            if not fixture_root:
                assert logic_hash(raw.decode()) == logic_hash(data.decode()), str(src)
            entry['logic_sha256'] = logic_hash(data.decode())
        entries.append(entry)
    queue = list(map(pathlib.Path, ROOTS)) + list(SOURCE.glob('scripts/fetch/o4c_*.py'))
    queue = [p.relative_to(SOURCE) if p.is_absolute() else p for p in queue]
    seen = set()
    while queue:
        p = queue.pop()
        if p in seen or not (SOURCE / p).is_file():
            continue
        seen.add(p)
        tree = ast.parse((SOURCE / p).read_text())
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom) and n.level:
                base = p.parent
                for _ in range(n.level - 1): base = base.parent
                relatives = ([n.module] if n.module else []) + [((n.module + '.') if n.module else '') + a.name for a in n.names]
                for relative in relatives:
                    candidate = base / (relative.replace('.', '/') + '.py')
                    if (SOURCE / candidate).is_file(): queue.append(candidate)
            mods = [n.module] if isinstance(n, ast.ImportFrom) and n.level == 0 else [a.name for a in n.names] if isinstance(n, ast.Import) else []
            if isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
                mods += [n.module + '.' + a.name for a in n.names]
            for mod in mods:
                module = local_module(mod) if mod else None
                if module:
                    candidate = pathlib.Path(module.replace('.', '/') + '.py')
                    if (SOURCE / candidate).is_file(): queue.append(candidate)
    for p in sorted(seen): copy(SOURCE / p, pathlib.Path('greekocr/_vendor') / p, SOURCE, True)
    for src in sorted(SOURCE.glob('scripts/fetch/o4c_*.py')):
        copy(src, pathlib.Path('greekocr/_vendor/source_clis')/src.relative_to(SOURCE), SOURCE)
    for parent in sorted({ancestor for p in seen for ancestor in p.parents if str(ancestor) != '.'}):
        if (SOURCE/parent/'__init__.py').is_file() and parent/'__init__.py' not in seen:
            copy(SOURCE/parent/'__init__.py', pathlib.Path('greekocr/_vendor')/parent/'__init__.py', SOURCE, True)
    for pattern in ('factory/src/*.rs', 'factory/*.json', 'factory/Cargo.toml', 'factory/Cargo.lock',
                    'factory/exclusions/*', 'codec/v1.json', 'train/mix.schema.json',
                    'scripts/fetch/r2_cllg*', 'scripts/fetch/parliament_pdf_cache.py', 'scripts/fetch/o4b_*.sh',
                    'rec/openocr_vendored/*.yml', 'rec/openocr_vendored/LICENSE', 'rec/openocr_vendored/PROVENANCE.md'):
        for src in sorted(SOURCE.glob(pattern)):
            if src.is_file(): copy(src, pathlib.Path('greekocr/_vendor') / src.relative_to(SOURCE), SOURCE)
    for name in ('docs/data_contracts.md', 'docs/ocr_program_2026-10-06/R01_native_preprocess_review.md',
                 'docs/ocr_program_2026-10-06/E2_NOTES.md'):
        copy(SOURCE/name, pathlib.Path('docs/origins/greek-page-ocr')/name, SOURCE)
    for src in sorted((GLOSS/'src/glossapi/ocr/plugin').rglob('*')):
        if src.is_file() and '__pycache__' not in src.parts:
            copy(src, pathlib.Path('greekocr/deploy/docling_plugin')/src.relative_to(GLOSS/'src/glossapi/ocr/plugin'), GLOSS)
    copy(GLOSS/'tests/test_docling_plugin_c1.py', pathlib.Path('docs/origins/test_docling_plugin_c1.py'), GLOSS)
    src = GLOSS/'tests/test_docling_plugin_c1.py'
    selected = {'test_factory_registration','test_page_replacement_boundary',
                'test_raster_body_keeps_native_cells_and_records_recognition',
                'test_checkpoint_failure_instructions_reference_available_export',
                'test_conflicting_sidecar_support_metadata_fails_closed','test_checkpoint_pin_rejects_changed_artifact'}
    source = src.read_text(); lines = source.splitlines(keepends=True)
    port = '"""Ported offline Docling contracts; full original archived in docs/origins."""\nfrom pathlib import Path\nfrom types import SimpleNamespace\nimport json\nimport pytest\n\n'
    for node in ast.parse(source).body:
        if isinstance(node, ast.FunctionDef) and node.name in selected:
            start = min([node.lineno]+[d.lineno for d in node.decorator_list])-1
            port += ''.join(lines[start:node.end_lineno]).replace('glossapi.ocr.plugin','greekocr.deploy.docling_plugin')+'\n\n'
    target = pathlib.Path('tests/test_docling_contract.py')
    (DEST/target).write_text(port)
    entries.append(dict(path=str(target),origin=str(src),commit=heads[GLOSS],source_sha256=sha(src.read_bytes()),
                        vendored_sha256=sha(port.encode()),source_state='selected offline contract tests',
                        transform='six preserved test functions, plugin imports relocated'))
    for name in ('test_o4c.py', 'test_o4c_anemi.py', 'test_r2_cllg.py'):
        copy(SOURCE/'bench/tests'/name, pathlib.Path('tests')/name.replace('test_', 'test_vendor_'), SOURCE, True, name != 'test_r2_cllg.py')
    for src in sorted((SOURCE/'docs/evidence/o4c/fixtures').glob('*')):
        if src.is_file():
            copy(src, pathlib.Path('tests/fixtures/o4c')/src.name, SOURCE)
    copy(SOURCE/'docs/evidence/o4c/print_reviews.jsonl', pathlib.Path('tests/fixtures/o4c/print_reviews.jsonl'), SOURCE)
    reviews = [json.loads(s) for s in (SOURCE/'docs/evidence/o4c/print_reviews.jsonl').read_text().splitlines()]
    for name in sorted({p['local_path'] for row in reviews if row['status'] == 'unverified-conflict' for p in row['page_probes']}):
        copy(SOURCE/name, pathlib.Path('tests/fixtures/o4c/review_pages')/pathlib.Path(name).name, SOURCE)
    copy(PODS/'experiments/ocr_program_review_20261006/pod_e2/pi_pod.py', pathlib.Path('greekocr/_vendor/pods/pi_pod.py'), PODS)
    for src in sorted((DEST/'seed/node_scripts').glob('*')):
        if src.is_file(): copy(src, pathlib.Path('greekocr/_vendor/seed/node_scripts')/src.name, DEST)
    skill = pathlib.Path('/Users/foivoskarounos-zamparloukos/.claude/skills/checkpoint')
    copy(skill/'SKILL.md', pathlib.Path('docs/origins/checkpoint/SKILL.md'), None)
    for src in sorted((skill/'scripts').glob('watch_*.sh')):
        copy(src, pathlib.Path('greekocr/_vendor/ops')/src.name, None)
    for directory in [DEST/'greekocr/_vendor', *(DEST/'greekocr/_vendor').rglob('*')]:
        if directory.is_dir() and '__pycache__' not in directory.parts and any(directory.glob('*.py')):
            init = directory/'__init__.py'
            if not init.exists(): init.write_text('"""Preserved implementation detail; use greekocr public APIs."""\n')
    (DEST/'greekocr/_vendor/origins.json').write_text(json.dumps(entries, indent=2)+'\n')
    docs = ['# Vendored source inventory', '',
            'Snapshot: 8 October 2026. Origin commit is repository HEAD at capture. Modified and untracked files are explicitly identified; their source SHA-256 binds the exact captured bytes, not an invented committed version.', '',
            'Implementation Python changes are limited to imports and import-hook strings. Non-import AST hashes were compared before and after relocation. Ported test harnesses additionally relocate recorded fixture roots; the Docling port selects six unchanged offline contract functions and relocates plugin imports. Resources, Rust, shells and Docling plugin are byte-identical. Generated wrappers and namespace initializers are new code.', '',
            'Requested `docs/ocr_program_2026-10-06/data_contracts.md` was absent; the current source is `docs/data_contracts.md`. Seed node scripts originate in this toolkit scaffold. The checkpoint skill has no source commit (unversioned); only Part B informs the new ops API. No Rust was built or moved, no cloud action was performed.', '',
            'Machine-readable file hashes and logic hashes: `greekocr/_vendor/origins.json`.', '',
            '| Vendored path | Absolute origin | Origin commit | Source state | Transform |',
            '| --- | --- | --- | --- | --- |']
    for e in sorted(entries, key=lambda e:e['path']):
        docs.append('| `{path}` | `{origin}` | {commit} | {source_state} | {transform} |'.format(**dict(e, commit=e['commit'] or 'none (unversioned)')))
    docs += ['', 'Word-tag producer: `factory/src/import_real.rs` (lines 142-150, 183, 190), using `factory/src/corpus.rs::classify`. E1 evaluation consumes the bound sidecar; `bench/line_categories.py::word_tags` supplies disclosed diagnostic fallback tags. Recipes carry per-line content marginals; `corpus.rs` carries classifier rules.', '',
             'Historical launch shells contain git resets, hardcoded paths and workload launches. They are reference evidence and are never executed by a toolkit API. The original pod script reads plaintext local key files and has top-level side effects; it is archived only. The new injectable pod client retains offer selection/payload semantics while obtaining secrets from environment variables and explicit state paths.', '']
    (DEST/'docs/INVENTORY.md').write_text('\n'.join(docs))
    print(f'vendored {len(entries)} files; {len(seen)} relocated Python implementations')

if __name__ == '__main__': snapshot()
