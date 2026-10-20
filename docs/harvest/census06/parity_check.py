"""Census_04 policy replay shape, bound to SEG10's saved evidence and exact reasons."""
import argparse,gzip,hashlib,json
from pathlib import Path
from greekocr.harvest.line_pipeline_native import ASSETS, JsonService, file_sha
D=Path(__file__).resolve().parent

def check():
    receipt=json.loads((D/'parity/source_receipt.json').read_text());h=hashlib.sha256();counts={}
    service=JsonService(['node',str(ASSETS/'service.mjs')])
    try:
        for chunk in receipt['chunks']:
            path=D/'parity'/chunk['path'];assert file_sha(path)==chunk['sha256']
            data=gzip.decompress(path.read_bytes());h.update(data)
            for line in data.splitlines():
                r=json.loads(line)
                if r['cohort'] not in ('segeval1','calibration'):continue
                result=service.call(dict(operation='decide',policy_sha256=file_sha(ASSETS/'segmentation-policy.js'),evidence=r['after']['evidence']))
                assert result=={k:r['after'][k] for k in ('verdict','reason')},r['line_id']
                counts[r['cohort']]=counts.get(r['cohort'],0)+1
    finally:service.close()
    assert h.hexdigest()==receipt['sha256']
    assert counts==dict(segeval1=150,calibration=888)
    return dict(status='PASS',counts=counts,expectation_sha256=h.hexdigest(),verdict_and_reason_exact=True,native_images_processed=0)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args();result=check();a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
