"""Foreground diagnostic of negative motif costs; never a runtime gate."""
import argparse
from time import perf_counter
import cv2
from ..round2 import manifest, get_baseline, ROOT
from ..layout_barriers.fast import run as separators
from ..shared.ink_ownership import analyze
from ..shared.ink_motif_gate import coarse_scout, inspect
from ..shared.timing import dump


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--page',default='an-778126cc8c2b-p000011');a=ap.parse_args()
    row=next(r for r in manifest()['pages'] if r['page']==a.page)
    cv2.setNumThreads(1);g=cv2.imread(str(ROOT/row['path']),0);items=separators(g,get_baseline(row))['items']
    out=[]
    for repeat in range(2):
        own=analyze(g,items);details=[]
        for i,q in enumerate(items):
            if i in own['suppress_indices']:continue
            t=perf_counter();sc=coarse_scout(g,q,own['height']);sc_s=perf_counter()-t
            t=perf_counter();m,_=inspect(g,q,own['height'],scouted=sc);sec=perf_counter()-t
            details.append(dict(line=i,scout_s=sc_s,inspect_s=sec,scouted=sc,**m))
        out.append(dict(repeat=repeat,ownership_s=own['seconds'],lines=details))
    dest=ROOT/'.astra/fast_lines/out/stack'/('ink-profile-'+a.page+'.json');dump(dest,out)
    for r in out:print(r['repeat'],r['ownership_s'],[(x['line'],round(x['inspect_s']*1000,3),x['reason']) for x in sorted(r['lines'],key=lambda x:-x['inspect_s'])[:5]])

if __name__=='__main__':main()
