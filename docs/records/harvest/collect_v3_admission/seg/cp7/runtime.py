"""Launcher helpers: validate/map answers and record usage; no decision scoring."""
import sys
from cp7_common import *
RUBRIC=('neighbour_whole_word','multi_line','rotated','horizontally_missegmented')
ERRORS={'wrong_letter','lookalike_script_letter','missing_word_or_span','extra_text','wrong_mark','missing_mark','extra_mark','punctuation','hyphen','digits','merged_two_lines','crop_clipped','crop_overrun'}


def limit(line):
    if 'limit_id=codex ' not in line:raise ValueError('No Codex limit snapshot')
    found=re.findall(r'(?:primary|secondary)=([0-9.]+)%/10080m',line)
    if len(found)!=1:raise ValueError('Need exactly one weekly bucket')
    value=float(found[0])
    if not 0<=value<78:raise ValueError('STOP: weekly used >= 78% or invalid')
    return value


def map_records(answers,items,key):
    if len(answers)!=55 or len(items)!=55:raise ValueError('Context must have 55 complete answers')
    if [i['card_id'] for i in items]!=key['readers']['r1']:raise ValueError('Pack/key mismatch')
    mapped=[];controls=[]
    for answer,item in zip(answers,items):
        if answer.get('card_id')!=item['card_id']:raise ValueError('Answer order/id mismatch')
        for field,allowed in [('letters',{'y','n','u'}),('marks',{'y','n','na','u'}),('crop_ok',{'y','n','u'})]:
            if answer.get(field) not in allowed:raise ValueError('Invalid '+field)
        if not isinstance(answer.get('detail'),str) or not isinstance(answer.get('errors'),list) or any(e not in ERRORS for e in answer['errors']):raise ValueError('Invalid detail/errors')
        for field in RUBRIC:
            if answer.get(field) not in ('yes','no'):raise ValueError('Invalid '+field)
            reason=answer.get(field+'_reason')
            if not isinstance(reason,str) or not reason.strip() or '\n' in reason:raise ValueError('Missing one-line reason: '+field)
        meta=key['items'][item['card_id']]
        out=dict(answer,line_id=meta['line_id'])
        (controls if meta['control'] else mapped).append(out)
    if len(mapped)!=50 or len(controls)!=5:raise ValueError('Wrong control/bed mapping')
    return mapped,controls


def main():
    action,*args=sys.argv[1:]
    if action=='limit':print(limit(args[0]));return
    if action=='verify':
        from freeze import verify_freeze
        verify_freeze();assert read(HERE/'build_receipt.json')['mapping_prepared']==100
        for bed in BEDS:
            key=read(HERE/'keys'/(bed+'.json'))
            expected=read(PACK_ROOT/bed/'MANIFEST.r1.json')['files']
            for path,digest in expected.items():assert sha(PACK_ROOT/bed/'r1'/path)==digest
        return
    bed=args[0];assert bed in BEDS
    if action=='map':
        key=read(HERE/'keys'/(bed+'.json'));items=rows(PACK_ROOT/bed/'r1/cards.jsonl')
        mapped,controls=map_records(rows(HERE/'answers'/bed/'r1.jsonl'),items,key)
        jsonl(HERE/'answers'/bed/'r1.mapped.jsonl',mapped)
        jsonl(HERE/'answers'/bed/'r1.controls.jsonl',controls)
        print(json.dumps(dict(mapped=50,controls=5,scored=False)))
    elif action=='receipt':
        run,before,after,sc,mc=args[1:];run=json.loads(run)
        result=dict(bed=bed,reader='r1',run=run,limit_before=before,limit_after=after,
            canonical_scanner_sha256=SCANNER,scanner_rc=int(sc),mapping_rc=int(mc),
            weekly_before=limit(before),weekly_after=None,status='audit pending',
            freeze_sha256=sha(SEG/'CP7_FREEZE.json'),scoring='Part B pending')
        if run.get('model')!='gpt-6.1-sol' or run.get('rc')!=0:result['status']='VOID: model or reader failure'
        elif int(sc) or int(mc):result['status']='VOID: leak or incomplete answers'
        else:result['status']='scan clean and mapped; adjudication pending'
        try:result['weekly_after']=limit(after)
        except ValueError:result['weekly_stop']=True
        dump(HERE/'receipts'/(bed+'.json'),result)
        if result['status'].startswith('VOID'):raise ValueError(result['status'])
    else:raise ValueError(action)

if __name__=='__main__':main()
