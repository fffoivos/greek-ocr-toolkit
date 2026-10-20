"""CP7c isolated r2 bindings and offline scope."""
import os, sys
from cp7_common import *
sys.path.insert(0,str(ROOT))
BASE=HERE
R2=BASE/'r2'
FREEZE=SEG/'CP7_FREEZE_r2.json'
SEED_R2='seg-cp7:fresh100-r2'
BEDS_R2=('segcp7r2_a','segcp7r2_b')

def guard():
    def audit(event,args):
        if event.startswith('socket.') or event=='subprocess.Popen':raise AssertionError('network/subprocess OFF')
        if event=='open':
            path,mode,flags=args
            if isinstance(path,int):return
            p=Path(path).resolve()
            if p.is_relative_to(LIVE) and (p.name=='features.jsonl' or flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)):raise AssertionError('live root forbidden')
    sys.addaudithook(audit)

def verify():
    f=read(FREEZE)
    for section in ('files','geometry_files'):
        for p,h in f[section].items():assert sha(ROOT/p)==h,'freeze drift: '+p
    from greekocr.harvest import geometry_observations as g, admission as a
    from greekocr.harvest.serbian import serbian_extension_sha256,serbian_documents_sha256
    from greekocr.harvest.lookalikes import lookalike_table_sha256
    assert f['geometry_implementation']==g.implementation_binding()
    assert f['ledger_sha256']==sha(SEG/'calibration_ledger.json')=='76ea2d35f374b20326db3ab434e94d57d942d3d610128551e1475b1c8f172f0f'
    assert f['codec_sha256']==a.load_codec()['sha256']
    assert f['serbian_extension_sha256']==serbian_extension_sha256()
    assert f['serbian_documents_sha256']==serbian_documents_sha256()
    assert f['lookalike_table_sha256']==lookalike_table_sha256()
    assert f['expected_table_sha256']==a.expected_table_sha256()
    assert sha(BASE/'tools/scan_rollout.py')==SCANNER
    return f
