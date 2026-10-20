"""Read HF metadata with per-command env credentials; never persist secrets."""
import datetime, hashlib, json, os, pathlib, sys, urllib.request
BASE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from fetch_inventory import http_client, write
folder=BASE/'receipts/openarchives'
url='https://huggingface.co/api/datasets/glossAPI/openarchives.gr/tree/main/data?recursive=false&expand=true'
client=http_client('archive',folder,offline=False,interval=2,budget=50_000_000)
result={'url':url,'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authentication':'HF_TOKEN from per-command environment; not recorded'}
try:
    token=os.environ.get('HF_TOKEN')
    if not token:raise RuntimeError('Keychain token unavailable; authenticated table check not performed')
    client.check_robots(url)
    request=urllib.request.Request(url,headers={'User-Agent':__import__('fetch_inventory').transport.UA,'Authorization':'Bearer '+token,'Accept-Encoding':'identity'})
    with urllib.request.urlopen(request,timeout=35) as r:
        body=r.read(2_000_001)
        if len(body)>2_000_000:raise RuntimeError('metadata limit exceeded')
        result.update(status=r.status,bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),ok=True)
    # Only dataset-file metadata, no text shards, is retained.
    write(folder/'hf-authenticated-tables.json',json.loads(body))
except Exception as e:result.update(ok=False,error=type(e).__name__+': '+str(e))
write(folder/'hf-authenticated-result.json',result)
print('HF authenticated metadata check:',result['ok'])
