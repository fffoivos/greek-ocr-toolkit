"""Post-reading combiner only; never launches readers or consumes old r2 data."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from greekocr.ops.data_root import input_path as _data_input
from greekocr.numerics.combine_v2 import decode_and_gate, decide
from n1t_packs import rows, dump
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifacts/n1/n1t2'


def load_reads(out=OUT):
    reads={};gates={}
    for kp in sorted((out/'keys').glob('ctx*.json')):
        key=json.loads(kp.read_text());reader=next(iter(key['readers']));ctx=kp.name.split('.')[0]
        from n1_map_answers import output_stem
        stem=output_stem(out.parent,out.name,ctx,reader)
        try:
            gate,decoded=decode_and_gate(key,rows(Path(str(stem)+'.jsonl')))
            scan=json.loads(Path(str(stem)+'.scan.json').read_text());run=json.loads(Path(str(stem)+'.run.json').read_text())
            gate['control_status']=gate['status']
            gate['provenance_ok']=bool(scan['ok'] and scan['scanner_version'] in (4, 'v4.4-canonical') and run['rc']==0 and run['model']=='gpt-6.1-sol')
            gate['provenance_violations']=scan.get('violations',[])
            if not gate['provenance_ok']: gate['status']='INVALID'
        except (OSError,ValueError,KeyError,TypeError) as exc:
            raise ValueError('complete readings required before combining: '+str(stem)+': '+str(exc)) from exc
        gates[f'{ctx}.{reader}']=gate
        for d in decoded:
            if not d['control']:
                reads.setdefault(d['slot_id'],[]).append(dict(reader=reader,context=ctx,item_id=d['item_id'],
                    meaning=d['meaning'],confidence=d['confidence'],context_status=gate['status'],read_status='ok'))
    return reads,gates


def main():
    slots=rows(_data_input(OUT/'slots.jsonl'));reads,gates=load_reads()
    require_complete(slots,reads)
    decisions=[decide(s,reads.get(s['slot_id'],[])) for s in slots]
    dump(OUT/'decisions.json',dict(decisions=decisions,gates=gates))


def require_complete(slots, reads):
    expected={s['slot_id'] for s in slots if s.get('read_reason')!='geometry-only'}
    if set(reads)!=expected or any(len(r)!=2 or {v['reader'] for v in r}!={'r1','r2'} for r in reads.values()):
        raise ValueError('both complete independent readings required')
if __name__=='__main__':main()
