#!/usr/bin/env python3
"""Portable offline planner and explicitly enabled live collector."""
from __future__ import annotations
import argparse,json,logging,os,sys
from pathlib import Path
if __package__ in (None,''):sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collect_v3.common import ScrubFilter,read_json,rows,scrub,lock
from collect_v3.config import SPECS,config

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config');p.add_argument('--output-root');p.add_argument('--cache')
    sub=p.add_subparsers(dest='command',required=True)
    plan=sub.add_parser('plan');plan.add_argument('--projects-root',default=str(Path.home()/'Projects'));plan.add_argument('--seed',type=int)
    run=sub.add_parser('run');run.add_argument('--tranche',choices=['W1','W2'],required=True);run.add_argument('--sources',nargs='+',required=True,help='source IDs, space- or comma-separated');run.add_argument('--execution-host',choices=['worker','owner_mac']);run.add_argument('--enable-network',action='store_true',default=None);run.add_argument('--serbian-codec',action='store_true',default=None);run.add_argument('--keep-images',action='store_true')
    for operation in ('materialize','clean-work'):
        op=sub.add_parser(operation);op.add_argument('--tranche',choices=['W1','W2'],required=True)
    status=sub.add_parser('status');status.add_argument('--tranche',choices=['W1','W2'])
    cards=sub.add_parser('cards');cards.add_argument('--tranche',choices=['W1','W2'],required=True);cards.add_argument('--phase',choices=['C1','C2'])
    audit=sub.add_parser('audit');audit.add_argument('--tranche',choices=['W1','W2'],required=True);audit.add_argument('--phase',choices=['C1','C2'],default='C1');audit.add_argument('--verdict-root');audit.add_argument('--previous')
    args=p.parse_args(argv);c=config(args.config,output_root=args.output_root,cache=args.cache)
    if args.output_root and not args.cache:c['cache']=str(Path(args.output_root)/'cache')
    handler=logging.StreamHandler();handler.addFilter(ScrubFilter());logging.basicConfig(level=logging.INFO,handlers=[handler],format='%(asctime)s %(message)s')
    if args.command=='plan':
        from collect_v3.planner import plan
        if args.seed is not None:c['seed']=args.seed
        result=plan(c,args.projects_root);print(json.dumps({k:result[k] for k in ('W1_pages','W1_projected_usd','W1_cap_usd','W2_projected_usd')}))
    elif args.command=='run':
        from collect_v3.runner import run
        if args.enable_network is not None:c['network_enabled']=args.enable_network
        if args.execution_host:c['execution_host']=args.execution_host
        if args.serbian_codec is not None:c['serbian_codec']=args.serbian_codec
        if args.keep_images:c['prune_images']=False
        sources=[s for group in args.sources for s in group.split(',')];result=run(c,args.tranche,sources);print(json.dumps(result))
    elif args.command in ('materialize','clean-work'):
        from collect_v3.storage import materialize,compact
        with lock(Path(c['output_root'])/'run.lock',blocking=False):
            result=materialize(c['output_root'],args.tranche,c['cache'],c['serbian_codec']) if args.command=='materialize' else compact(c['output_root'],c['cache'],args.tranche)
        print(json.dumps({'rows':len(result)} if isinstance(result,list) else result))
    elif args.command=='audit':
        from collect_v3.review import summarize
        with lock(Path(c['output_root'])/'run.lock',blocking=False):
            result=summarize(c['output_root'],args.tranche,args.phase,args.verdict_root,args.previous)
        print(json.dumps(result))
    elif args.command=='cards':
        from collect_v3.cards import cards
        with lock(Path(c['output_root'])/'run.lock',blocking=False):
            result=cards(c,args.tranche,args.phase)
        print(json.dumps({'strata':len(result),'shortfall_strata':sum(r['shortfall']>0 for r in result)}))
    else:
        result={}
        for t in ([args.tranche] if args.tranche else ['W1','W2']):
            state=Path(c['output_root'])/t/'state.json';result[t]=read_json(state) if state.exists() else {'status':'not_started','pages_planned':len(rows(Path(c['output_root'])/(t+'_manifest.jsonl')))}
            receipt=Path(c['output_root'])/t/'receipt.json'
            if receipt.exists():result[t]['receipt']=read_json(receipt)
        print(json.dumps(result,indent=2))

if __name__=='__main__':
    try:main()
    except Exception as e:
        print(f'{type(e).__name__}: {scrub(e)}',file=sys.stderr);raise SystemExit(1)
