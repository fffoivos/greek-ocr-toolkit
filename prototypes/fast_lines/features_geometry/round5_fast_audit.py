"""Check arithmetic optimization at every native traced sample and alternative."""
import cv2
from .round5_data import rows,load,DEST
from ..shared.geometry_fragments import candidates
from ..shared.geometry_contacts import render_contacts
from ..shared.timing import dump

def main():
    cv2.setNumThreads(1);out=DEST/'fast-tangent-audit';out.mkdir(exist_ok=True)
    for row in rows():
        dst=out/(row['page']+'.json')
        if dst.exists():raise RuntimeError(dst)
        gray,o,_=load(row);w=candidates(o['original'],row['image_size']);selected={p['line'] for p in w['pairs']}
        if not selected or row['parked']:
            dump(dst,dict(lines=[],pairs=len(w['pairs']),parked=row['parked']));continue
        slow=render_contacts(gray,o['original'],'explicit_fast',7,selected,fast_fit=False)
        fast=render_contacts(gray,o['original'],'explicit_fast',7,selected,fast_fit=True)
        ledger=[]
        for a,b in zip(slow['lines'],fast['lines']):
            ledger.append(dict(line=a['line'],equal=a==b,samples=len(a['path']),alternatives=len(a['alternatives'])))
        dump(dst,dict(lines=ledger,slow_seconds=slow['seconds'],fast_seconds=fast['seconds']))
        assert slow['lines']==fast['lines'],row['page']
        print(row['page'],len(ledger),round(slow['seconds']*1000,2),round(fast['seconds']*1000,2),flush=True)
if __name__=='__main__':main()
