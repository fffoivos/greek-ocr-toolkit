"""Restore the frozen logical file only after validating both archived and raw bytes."""
import gzip
import hashlib
from pathlib import Path
SEG=Path(__file__).resolve().parents[1]
RAW='cc5131461ce6fa43a5f5be67fe74a5638b5d7226145dee2883ab1632c6a26731'
ARCHIVE='faf5ae07adef089539acdc69d12ab59ccb0261ea3c846c772e296af13a7ec701'
def restore():
    archive=(SEG/'CP5_verification.json.gz').read_bytes()
    assert hashlib.sha256(archive).hexdigest()==ARCHIVE
    data=gzip.decompress(archive)
    assert len(data)==119720892 and hashlib.sha256(data).hexdigest()==RAW
    target=SEG/'CP5_verification.json'
    if target.exists(): assert target.read_bytes()==data
    else:
        temporary=target.with_suffix('.json.restore.tmp')
        temporary.write_bytes(data);temporary.replace(target)
    return RAW
if __name__=='__main__':print(restore())
