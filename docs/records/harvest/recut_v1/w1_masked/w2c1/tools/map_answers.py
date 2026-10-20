#!/usr/bin/env python3
"""Validate complete ordered answers, remove controls and undo private mapping."""
import argparse,json,sys
from pathlib import Path
from common import *
from owner39_validate import normalize
from owner39_common import literal_normalize
ERRORS={'wrong_letter','lookalike_script_letter','missing_word_or_span','extra_text','wrong_mark','missing_mark','extra_mark','punctuation','hyphen','digits','merged_two_lines','crop_clipped','crop_overrun'}

def validate(row,item,bed):
    if not isinstance(row,dict):raise ValueError('answer must be an object')
    if row.get(idfield(bed))!=item[idfield(bed)]:raise ValueError('answer order/id mismatch')
    if bed=='owner39':return normalize(row,item)
    if bed=='bsb':
        if not {'card_id','letters','marks','crop_ok','errors','detail'}<=row.keys():raise ValueError('missing BSB fields')
        for f,allowed in [('letters',{'y','n','u'}),('marks',{'y','n','na','u'}),('crop_ok',{'y','n','u'})]:
            if not isinstance(row[f],str) or row[f] not in allowed:raise ValueError('invalid '+f)
        if not isinstance(row['errors'],list) or any(not isinstance(x,str) or x not in ERRORS for x in row['errors']) or not isinstance(row['detail'],str):raise ValueError('invalid errors/detail')
    else:
        if not {'item_id','slots','confidence','unmarked_final_hard_signs','pre1918','note'}<=row.keys():raise ValueError('missing yer fields')
        slots={str(i+1) for i in range(item['slots'])}
        if not isinstance(row['slots'],dict) or set(row['slots'])!=slots or any(not isinstance(v,str) or v not in {'ъ','ь','other','u'} for v in row['slots'].values()):raise ValueError('invalid slot coverage/call')
        if not isinstance(row['confidence'],dict) or set(row['confidence'])!=slots or any(not isinstance(v,str) or v not in {'high','low'} for v in row['confidence'].values()):raise ValueError('invalid yer confidence coverage')
        if not isinstance(row['unmarked_final_hard_signs'],list) or any(not isinstance(v,str) for v in row['unmarked_final_hard_signs']):raise ValueError('invalid unmarked words')
        if row['pre1918'] not in ('yes','no','unclear') or not isinstance(row['note'],str):raise ValueError('invalid yer metadata')

def map_records(bed,reader,answers,key,items):
    if len(answers)!=len(items):raise ValueError('answer count differs from assignment')
    if [r[idfield(bed)] for r in items]!=key['readers'][reader]:raise ValueError('pack differs from key order')
    mapped=[];controls=[]
    for row,item in zip(answers,items):
        normalized=validate(row,item,bed);iid=item[idfield(bed)];meta=key['items'][iid]
        if meta['control']:
            expected=meta['expected']
            if bed=='owner39':
                form=row.get('transcription') if row['choice']=='literal' else item['options'].get(row['choice'],'')
                checks=dict(form=literal_normalize('NFC',form)==literal_normalize('NFC',expected['form']),choice=row['choice']==expected['choice'],heads=normalized['heads']==expected['heads'])
            else:checks={k:row.get(k)==v for k,v in expected.items()}
            controls.append(dict(id=iid,passed=all(checks.values()),checks=checks,expected=expected,answer=row));continue
        mapped_row=dict(row);mapped_row[idfield(bed)]=meta['source_id']
        if bed=='owner39' and row['choice'] in meta['option_to_source']:mapped_row['choice']=meta['option_to_source'][row['choice']]
        if bed=='yer' and meta.get('slot_to_source'):
            for f in ('slots','confidence'):mapped_row[f]={meta['slot_to_source'][s]:v for s,v in row[f].items()}
        mapped.append(mapped_row)
    # Source scorer accepts arbitrary order; deterministic output follows reader order.
    errors=sum(not c['passed'] for c in controls)
    return mapped,dict(bed=bed,reader=reader,controls=controls,control_errors=errors,flagged=errors>1)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bed',choices=FIELDS);p.add_argument('reader',choices=['r1','r2','r3']);p.add_argument('answers',type=Path);a=p.parse_args()
    key=json.loads((ROOT/(f'keys/{a.bed}_r3.json' if a.reader=='r3' else f'keys/{a.bed}.json')).read_text());items=rows(PACK_ROOT/a.bed/a.reader/itemfile(a.bed))
    mapped,controls=map_records(a.bed,a.reader,rows(a.answers),key,items)
    dest=ROOT/'answers'/a.bed;jsonl(dest/f'{a.reader}.mapped.jsonl',mapped);dump(dest/f'{a.reader}.controls.json',controls)
    print(json.dumps({'mapped':len(mapped),'control_errors':controls['control_errors'],'flagged':controls['flagged']}))
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError,OSError) as exc:print(str(exc),file=sys.stderr);sys.exit(2)
