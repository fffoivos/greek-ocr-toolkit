#!/usr/bin/env python3
"""Create (or reuse) the GPU node for E3/E4 on Prime Intellect and wait for ACTIVE. State in pi_pod_state.json."""
import json, os, sys, time, urllib.request, urllib.error, pathlib
API="https://api.primeintellect.ai"; KEY=open(os.path.expanduser("~/.config/prime/key")).read().strip()
D=pathlib.Path(__file__).resolve().parent; STATE=D/"pi_pod_state.json"
PUB=open(os.path.expanduser("~/.ssh/prime_intellect_key.pub")).read().strip()
PREFS=[("A100_80GB","massedcompute"),("A100_80GB","runpod"),("L40S_48GB","massedcompute"),("L40S_48GB","runpod"),("L40_48GB","runpod"),("RTX6000Ada_48GB","massedcompute"),("RTX6000Ada_48GB","runpod"),("A6000_48GB","massedcompute"),("A100_40GB","lambdalabs")]
def req(method,path,body=None,params=None):
    url=API+path+("?"+"&".join(f"{k}={v}" for k,v in params.items()) if params else "")
    r=urllib.request.Request(url,method=method,headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"},data=(json.dumps(body).encode() if body else None))
    try:
        with urllib.request.urlopen(r,timeout=60) as resp: return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e: raise SystemExit(f"HTTP {e.code} {path}: {e.read()[:400]!r}")
def log(*a): print(time.strftime("%H:%M:%S"),*a,flush=True)
def offers():
    d=req("GET","/api/v1/availability/gpus",params={"gpu_count":1}); out=[]
    def walk(x):
        if isinstance(x,dict):
            if "gpuType" in x and "cloudId" in x: out.append(x)
            for v in x.values(): walk(v)
        elif isinstance(x,list):
            for v in x: walk(v)
    walk(d); return out
def pick():
    offs=offers()
    for gpu,prov in PREFS:
        c=[o for o in offs if o.get("gpuType")==gpu and o.get("provider")==prov and str(o.get("stockStatus","")).lower() not in ("unavailable","none","")]
        c.sort(key=lambda o: float((o.get("prices") or {}).get("onDemand") or 99))
        if c: return c[0]
    raise SystemExit("no offer matched")
def ssh_key_id():
    for k in (req("GET","/api/v1/ssh_keys/",params={"offset":0,"limit":100}).get("data") or []):
        if (k.get("publicKey") or "").strip()==PUB: return k.get("id")
    return None
def status(p): return str(p.get("status") or (p.get("pod") or {}).get("status") or "").upper()
cmd=sys.argv[1] if len(sys.argv)>1 else "ensure"
if cmd=="status":
    s=json.load(open(STATE)); p=req("GET",f"/api/v1/pods/{s['pod_id']}"); print(json.dumps({k:p.get(k) for k in ("id","name","status","sshConnection","ip","gpuType","provider","priceHr","installationStatus","installationProgress")},indent=1)); sys.exit()
if cmd=="terminate":
    s=json.load(open(STATE)); print(req("DELETE",f"/api/v1/pods/{s['pod_id']}")); sys.exit()
if STATE.exists():
    s=json.load(open(STATE)); p=req("GET",f"/api/v1/pods/{s['pod_id']}")
    if status(p) not in ("TERMINATED","ERROR","DELETING",""): log("reusing pod",s["pod_id"],status(p)); created=p
    else: created=None
else: created=None
if created is None:
    o=pick(); img=next((i for i in (o.get("images") or []) if "cuda" in str(i).lower()),(o.get("images") or ["ubuntu_22_cuda_12"])[0])
    log("offer:",o.get("gpuType"),o.get("provider"),o.get("dataCenter"),o.get("socket"),"price",(o.get("prices") or {}).get("onDemand"),"image",img,"stock",o.get("stockStatus"))
    pod={"name":"greek-ocr-e2-20261008","cloudId":o["cloudId"],"gpuType":o["gpuType"],"socket":o.get("socket") or "PCIe","gpuCount":1,"image":img,"security":o.get("security") or "secure_cloud","autoRestart":False,"diskSize":100}
    if o.get("dataCenterId") or o.get("dataCenter"): pod["dataCenterId"]=o.get("dataCenterId") or o.get("dataCenter")
    if o.get("country"): pod["country"]=o["country"]
    kid=ssh_key_id()
    if kid: pod["sshKeyId"]=kid
    log("ssh key id:",kid)
    created=req("POST","/api/v1/pods/",body={"pod":pod,"provider":{"type":o["provider"]}})
    json.dump({"pod_id":created.get("id"),"created":created,"offer":o},open(STATE,"w"),indent=1)
    log("created pod",created.get("id"),status(created))
pid=created.get("id") or json.load(open(STATE))["pod_id"]
deadline=time.time()+1500
while True:
    p=req("GET",f"/api/v1/pods/{pid}"); st=status(p)
    log("status",st,"install",p.get("installationStatus"),p.get("installationProgress"),"ssh",p.get("sshConnection"),"ip",p.get("ip"))
    json.dump({"pod_id":pid,"pod":p,"offer":json.load(open(STATE)).get("offer")},open(STATE,"w"),indent=1)
    if st=="ACTIVE" and (p.get("sshConnection") or p.get("ip")): log("POD_ACTIVE",pid); break
    if st in ("ERROR","TERMINATED","DELETING"): log("POD_FAILED",st); sys.exit(1)
    if time.time()>deadline: log("POD_TIMEOUT"); sys.exit(2)
    time.sleep(20)
