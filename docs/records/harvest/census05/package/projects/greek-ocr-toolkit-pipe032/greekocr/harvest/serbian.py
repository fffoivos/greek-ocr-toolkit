"""Exact source/document-scoped Serbian extension, never a global codec edit.

Atom order: collect_v3/vendor/classify.py (ADM5c ruling).
Documents: CENSUS2 catalogue-language ruling, commit 3f93d204.
"""
import hashlib
import json

SERBIAN_EXTENSION_ATOMS = tuple('јћњљђџЈЋЊЉЂЏ')
SERBIAN_DOCUMENTS = ('cyrillic:7235f8d0', 'cyrillic:975289f3')


def serbian_extension_sha256():
    return hashlib.sha256(''.join(SERBIAN_EXTENSION_ATOMS).encode('utf-8')).hexdigest()


def serbian_documents_sha256():
    return hashlib.sha256(json.dumps(sorted(SERBIAN_DOCUMENTS),
                                    separators=(',', ':')).encode()).hexdigest()
