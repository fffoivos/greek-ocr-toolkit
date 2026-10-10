"""Short, repeated on-demand feature timings, excluding decode and image writing."""
import json
import cv2
from ..round2 import manifest,get_baseline
from ..shared.manifest import ROOT
from ..shared.type_profiles import analyze as type_analyze
from ..shared.type_tables import analyze as table_analyze
from ..shared.timing import dump
from .reference import DEST
from .tables import names


def run():
    typ=ROOT/json.loads((DEST/'active-type.json').read_text())['directory'];named={p.stem for p in typ.glob('*.json')};out=[]
    for repeat in [1,2]:
        for row in manifest()['pages']:
            if row['page'] not in named and row['page'] not in names():continue
            gray=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row)
            for feature,fn,version in [('typography',type_analyze,3),('tables',table_analyze,5)]:
                if row['page'] not in (named if feature=='typography' else names()):continue
                for route in ['slow','explicit','heuristic']:
                    r=fn(gray,items,route=route,version=version);out.append(dict(page=row['page'],feature=feature,route=route,repeat=repeat,seconds=r['seconds']))
    dump(DEST/'feature-timings.json',out);print(len(out))

if __name__=='__main__':cv2.setNumThreads(1);run()
