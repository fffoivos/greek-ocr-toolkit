"""CQ4c current inventory entry point; historical CQ4b code is in prior_cq4b/."""
import argparse,json
from build import OUT,load,intake
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--refresh-intake',action='store_true');args=p.parse_args()
 if args.refresh_intake:
  pools=intake();print(json.dumps({k:dict(slots=len(v),documents=len({x['doc'] for x in v})) for k,v in pools.items()},indent=2))
 else:print(json.dumps(load(OUT/'inventory.json'),ensure_ascii=False,indent=2))
