from pathlib import Path
import hashlib
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def atomic_bytes(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+".tmp");temp.write_bytes(data);temp.replace(path)
def ensure_crop(row):
    """Render only a requested review crop from its retained source raster."""
    from PIL import Image
    import io

    path=Path(row['crop'])
    if path.exists():
        if sha(path)!=row['crop_sha256']:raise ValueError('crop hash mismatch')
        return path
    with Image.open(row['crop_source_image']) as image:
        if sha(row['crop_source_image'])!=row['crop_source_sha256']:raise ValueError('crop source hash mismatch')
        crop=image.convert('L').crop(row['crop_bbox']);buf=io.BytesIO();crop.save(buf,format='PNG',compress_level=3)
    data=buf.getvalue()
    if sha_bytes(data)!=row['crop_sha256']:raise ValueError('regenerated crop hash mismatch')
    atomic_bytes(path,data);return path
