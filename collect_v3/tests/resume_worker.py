"""Subprocess fixture for a real SIGKILL, including the paid-response boundary."""
import os,sys,time
from pathlib import Path
from collect_v3.offline import fixtures,prepare_mock,no_network
from collect_v3.common import write_json,read_json,lock
from collect_v3.config import config
from collect_v3.runner import run

projects,output,mode=sys.argv[1:];output=Path(output)
fs,overrides,_=fixtures(projects);fs=[f for f in fs if f['source']=='ia_poly1850'];manifest,http,reader,routes=prepare_mock(output,fs)
original=reader.read

def read(image):
    result=original(image)
    with lock(output/'mock_reads.lock'):
        with (output/'mock_reads.jsonl').open('a') as f:f.write('{"hash":"'+__import__('collect_v3.common',fromlist=['sha']).sha(image)+'"}\n');f.flush();os.fsync(f.fileno())
    return result
reader.read=read

def hook(stage,page):
    if mode=='pause' and stage=='after_response' and page['id']==fs[1]['page']['id']:
        write_json(output/'kill_ready.json',{'stage':stage,'page_id':page['id']})
        while True:time.sleep(.05)

with no_network():
    r=run(config(output_root=str(output),cache=str(output/'cache'),storage_diet=False),'W1',['ia_poly1850'],http=http,reader=reader,routes=routes,hook=hook,fixture_detector={f['page']['id']:f['detector_cache'] for f in fs},baseline_overrides=overrides)
write_json(output/'worker_receipt.json',r)
