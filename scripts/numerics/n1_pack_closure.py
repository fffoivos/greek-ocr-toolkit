"""N1 schema adapter reusing the existing sol-reading closure checker."""
import importlib.util
import sys
from pathlib import Path


def scan(directory, key_root, completed=False, meanings=None):
    expected_meanings = set(meanings or ('raised dot','baseline dot','comma','hyphen or dash','space','nothing','other','unreadable'))
    letters = set('ABCDEFGHIJ'[:len(expected_meanings)])
    base = Path(__file__).resolve().parents[1]/'secondary/reading'
    sys.path.insert(0, str(base))
    spec = importlib.util.spec_from_file_location('n1_reused_scanner', base/'scan_packs.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.ROOT = Path(key_root)
    module.FIELDS = dict(module.FIELDS, n1={'item_id','crop','word_image','options'})
    original = module.rows
    def adapted(path):
        data = original(path)
        return [dict(item_id=r['item_id'], crop=r['line'], word_image=r['zoom'], options=r['options']) for r in data]
    module.rows = adapted
    module.itemfile = lambda bed: 'items.jsonl'
    module.idfield = lambda bed: 'item_id'
    result = module.scan(directory, 'n1', write_manifest=False, allow_runtime=completed, compare_option_maps=False)
    import json
    for item in original(Path(directory)/'items.jsonl'):
        if set(item) != {'item_id','line','zoom','options'} or set(item['options']) != letters:
            result['violations'].append('invalid N1 item fields/options')
    result['ok'] = not result['violations']
    if completed:
        import hashlib
        manifest = Path(directory).parent/('MANIFEST.'+Path(directory).name+'.json')
        if not manifest.is_file(): result['violations'].append('missing sealed manifest')
        else:
            sealed = json.loads(manifest.read_text())['files']
            if result['files'] != sealed: result['violations'].append('sealed manifest mismatch')
            result['manifest_sha256'] = hashlib.sha256(manifest.read_bytes()).hexdigest()
    # Private maps bind both order and the independently permuted public options.
    suffix = '' if Path(directory).name=='r1' else '.'+Path(directory).name
    key = json.loads((Path(key_root)/'keys'/(Path(directory).parent.name+suffix+'.json')).read_text())
    for item in original(Path(directory)/'items.jsonl'):
        if item['options'] != key['items'][item['item_id']]['option_map']:
            result['violations'].append('public/private option mismatch')
        if set(item['options'].values()) != expected_meanings:
            result['violations'].append('invalid option meanings')
    other_reader = 'r2' if Path(directory).name=='r1' else 'r1'
    other_keypath = Path(key_root)/'keys'/(Path(directory).parent.name+('' if other_reader=='r1' else '.r2')+'.json')
    if other_keypath.exists():
        other = json.loads(other_keypath.read_text())
        current_items = [key['items'][iid] for iid in key['readers'][Path(directory).name]]
        other_items = [other['items'][iid] for iid in reversed(other['readers'][other_reader])]
        if len(current_items) != len(other_items): result['violations'].append('reader item counts differ')
        for a,b in zip(current_items,other_items):
            if {k:v for k,v in a.items() if k!='option_map'} != {k:v for k,v in b.items() if k!='option_map'}:
                result['violations'].append('private slots not exact reverse')
            if any(a['option_map'][k]==b['option_map'][k] for k in a['option_map']):
                result['violations'].append('option letters not freshly permuted')
    result['ok'] = not result['violations']
    if result['ok'] and not completed:
        import hashlib
        manifest = Path(directory).parent/('MANIFEST.'+Path(directory).name+'.json')
        manifest.write_text(json.dumps(dict(bed='n1',reader=Path(directory).name,files=result['files']),ensure_ascii=False,indent=2)+'\n')
        result['manifest_sha256'] = hashlib.sha256(manifest.read_bytes()).hexdigest()
    return result
