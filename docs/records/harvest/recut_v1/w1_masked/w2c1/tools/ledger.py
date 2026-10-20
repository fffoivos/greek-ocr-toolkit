#!/usr/bin/env python3
"""Append measured launcher usage with two explicit limit snapshots."""
import argparse,json,math,re,sys
from pathlib import Path
from common import ROOT,dump

def weekly(line):
    # The baseline account reports its 10080-minute bucket as primary.
    found=re.findall(r'(?:primary|secondary)=([0-9.]+)%/10080m',line)
    if len(found)!=1:raise ValueError('need exactly one measured weekly (10080m) bucket')
    value=float(found[0])
    if not 0<=value<=100:raise ValueError('weekly percentage out of range')
    return value

def balances(obj):
    result=[]
    if isinstance(obj,dict):
        credits=obj.get('credits')
        if isinstance(credits,dict) and credits.get('balance') is not None:
            try:result.append(float(str(credits['balance']).replace(',','')))
            except ValueError:raise ValueError('invalid credits balance')
        for k,v in obj.items():
            if k!='credits':result.extend(balances(v))
    elif isinstance(obj,list):
        for v in obj:result.extend(balances(v))
    return result

def record(run,before,after,bed,reader,items):
    if items<=0:raise ValueError('items must be positive')
    if not run.get('rollout'):raise ValueError('run must identify rollout')
    usage=run.get('usage'); wall=run.get('wall_s')
    if not isinstance(usage,dict):raise ValueError('missing measured usage')
    names={'input':'input_tokens','cached_input':'cached_input_tokens','output':'output_tokens','reasoning':'reasoning_output_tokens','total':'total_tokens'}
    tokens={}
    for short,long in names.items():
        value=usage.get(long)
        if type(value) is not int or value<0:raise ValueError('missing/invalid measured '+long)
        tokens[short]=value
    if not isinstance(wall,(int,float)) or not math.isfinite(wall) or wall<0:raise ValueError('invalid wall_s')
    w0,w1=weekly(before),weekly(after);delta=w1-w0
    # Launcher only retains the last rate-limit snapshot. Never invent a
    # before balance from that final snapshot. Accept explicit before/after
    # snapshots if a future launcher supplies them; otherwise before is null.
    rl=run.get('rate_limits_in_rollout');end=balances(rl)
    initial=balances(run.get('rate_limits_before'))
    if isinstance(rl,list):
        initial=balances(rl[0]) if len(rl)>1 else initial;end=balances(rl[-1]) if rl else []
    tc=run.get('tool_calls')
    if not isinstance(tc,dict) or any(type(v) is not int or v<0 for v in tc.values()):raise ValueError('invalid tool calls')
    return dict(bed=bed,reader=reader,items=items,label=run.get('label'),rc=run.get('rc'),wall_seconds=wall,wall_seconds_per_item=wall/items,tokens=tokens,tokens_per_item={k:v/items for k,v in tokens.items()},tool_calls=tc,total_tool_calls=sum(tc.values()),weekly_used_before=w0,weekly_used_after=w1,weekly_delta=delta,weekly_points_per_100_items=delta*100/items,credits_balance_before=initial[0] if initial else None,credits_balance_after=end[-1] if end else None,credits_before_unavailable=not bool(initial),rate_limits_in_rollout=rl,rollout=str(Path(run['rollout']).expanduser().resolve()),limit_probe_before=before,limit_probe_after=after)

def append(path,entry):
    path=Path(path);data=json.loads(path.read_text()) if path.exists() else []
    if not isinstance(data,list):raise ValueError('ledger must be an array')
    if any(r['rollout']==entry['rollout'] or (r['bed'],r['reader'])==(entry['bed'],entry['reader']) for r in data):raise ValueError('duplicate rollout or bed/reader')
    data.append(entry);dump(path,data)

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True);a=sub.add_parser('add')
    for arg in ('run','before','after','bed','reader'):a.add_argument('--'+arg,required=True)
    a.add_argument('--items',type=int,required=True);a=p.parse_args()
    entry=record(json.loads(a.run),a.before,a.after,a.bed,a.reader,a.items);append(ROOT/'usage_ledger.json',entry);print(json.dumps(entry))
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError) as exc:print(str(exc),file=sys.stderr);sys.exit(2)
