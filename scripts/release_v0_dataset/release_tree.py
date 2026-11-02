"""Reviewed disposition of every non-shard path at the frozen public revision.

Retained metadata is outside C, like the 264 frozen trainer files. Its original
bytes are uploaded alongside C and checked on the complete staging download.
"""
from .build_locks import REVISION

# Read-only pinned HTTP reads through clariden2; Git blob IDs independently
# matched p1/PUBLIC_TREE.json. See p2/RELEASE_TREE_P2l.md for the full inventory.
METADATA = [
    ('.gitattributes', 2504, '9e75dd981de037ec3769f24f790e126bc5a160b6871f510214e68dc70649aeeb', 'bed0738c7eeb449bca98b5d2f33c89a1ee56349a', 'replace'),
    ('COUNTS.json', 189, '2e208af7a2f65612d67e655247fe6625567329f8761f781ec1c26f674bc2f734', '95b684c06080fd4ba0970f394362a22ddefa79e9', 'retain'),
    ('README.md', 4612, 'bc413ea51c7f4b772e05cfe99a41f5dc08643ca010a40a6feab7d51384239bbd', 'f275d7553fe4c13908ac6635dae1a907b35f3127', 'replace'),
    ('SOURCES_BY_SPLIT.json', 3446, '3777cdf8feca0e57d5a1bc8000707823ebcb2ca115ddc0a2d20f45c3275a0495', 'b69b93f6bf30bfee85cc5b606a80f0ce292d4923', 'retain'),
    ('synthetic/DISTRIBUTION.json', 3262, '70865e7f0703da093a87b25d503541337705f8b76d673f270f1e1e10adcdec39', 'd84141fa3fa6de33933f0b7fa985f901cab6a578', 'retain'),
    ('synthetic/RECIPE.json', 24145, '7af225a30f19b83eacc5b129635a2f0995e934cb16ef96e24644f77a8f8cc74c', 'a7ec4bfef3f9eb3b7e77f08b363050378addf91d', 'replace'),
    ('synthetic/factory_audit_report.json', 1111304, '1d4ea8a360313d9f44341586619b12acc5e7979691268aa018fff1686cd9ef2a', 'd8d611fd7f0219f9af60e4b7926e2d70eb6fff54', 'retain'),
    ('synthetic/factory_select_report.json', 41, 'ec591f3b531634a2ba2017745f6e58e7cdaf6650bffc4df7d794e79c8fdd02c7', 'd7fb3a1a446511f519297897a761c7fc335a6cb8', 'retain'),
]
RETAINED = [dict(path=p, bytes=n, sha256=h) for p, n, h, _, action in METADATA if action == 'retain']

# Exactly the existing public .gitattributes, including HF's default patterns.
GITATTRIBUTES = ''.join(p + ' filter=lfs diff=lfs merge=lfs -text\n' if not p.startswith('#') else p + '\n'
    for p in '''*.7z *.arrow *.avro *.bin *.bz2 *.ckpt *.ftz *.gz *.h5 *.joblib *.lfs.* *.lz4 *.mds *.mlmodel *.model *.msgpack *.npy *.npz *.onnx *.ot *.parquet *.pb *.pickle *.pkl *.pt *.pth *.rar *.safetensors saved_model/**/* *.tar.* *.tar *.tflite *.tgz *.wasm *.xz *.zip *.zst *tfevents*'''.split())
for comment, patterns in [
    ('Audio files - uncompressed', '*.pcm *.sam *.raw'),
    ('Audio files - compressed', '*.aac *.flac *.mp3 *.ogg *.wav'),
    ('Image files - uncompressed', '*.bmp *.gif *.png *.tiff'),
    ('Image files - compressed', '*.jpg *.jpeg *.webp'),
    ('Video files - compressed', '*.mp4 *.webm'),
]:
    GITATTRIBUTES += '# ' + comment + '\n'
    GITATTRIBUTES += ''.join(p + ' filter=lfs diff=lfs merge=lfs -text\n' for p in patterns.split())


def retained_public(frozen):
    if frozen.get('schema') != 'hfd-frozen-trained-v1':
        return []  # Historical miniature fixtures have no public metadata tree.
    if frozen.get('revision') != REVISION:
        raise ValueError('release metadata revision differs')
    return RETAINED


def inventory(frozen):
    return dict(schema='hfd-release-tree-v1', revision=REVISION,
        frozen_trained=frozen.get('files', []),
        metadata=[dict(path=p, bytes=n, sha256=h, git_blob=b, action=a)
                  for p, n, h, b, a in METADATA], deleted=[])
