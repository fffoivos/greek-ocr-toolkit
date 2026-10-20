"""Merge independently completed page observations only with identical bindings."""
import json
from pathlib import Path
BASE=Path(__file__).resolve().parent
merged=0
for source in (BASE/'cache_tail').glob('*.json'):
    fresh=json.loads(source.read_text());destination=BASE/'cache'/source.name
    if destination.exists():
        old=json.loads(destination.read_text())
        assert old['binding']==fresh['binding'], 'cache binding mismatch'
        for key,value in old['measurements'].items():
            if key in fresh['measurements']:
                assert value==fresh['measurements'][key], 'measurement disagreement'
            else:
                fresh['measurements'][key]=value
    data=json.dumps(fresh,sort_keys=True)+'\n'
    if not destination.exists() or destination.read_text()!=data:
        temporary=destination.with_suffix('.merge.tmp');temporary.write_text(data);temporary.replace(destination)
        merged+=1
print(f'merged {merged} page caches with identical bindings')
