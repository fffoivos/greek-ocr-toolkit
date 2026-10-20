"""Exact runtime hosts from frozen source routes; never discover hosts via HTTP."""
import re
from urllib.parse import urlsplit

HOSTS = (
    'archive.org',
    'api.digitale-sammlungen.de',
    'digitalcollections.nlg.gr',
    'kosmopolis.library.upatras.gr',
    'lekythos.library.ucy.ac.cy',
    'et.gr',
    'search.et.gr',
    'ia37rg02wpsa01.blob.core.windows.net',
    'dlib.statistics.gr',
    'digitalna.nb.rs',
    'eu-documentai.googleapis.com',
    'oauth2.googleapis.com',
)

# Internet Archive serves /download/ via redirects to numbered data nodes: US iaNNNNNN (F2 receipts: ia600100…ia903208)
# and regional dnNNNNNN.<cc> nodes seen in W1 (dn710706.ca, dn760003.eu …).
IA_DATA_NODE = re.compile(r'^(ia\d{6}\.us|dn\d{6}\.[a-z]{2})\.archive\.org$')

def allowed_host(host):
    return host in HOSTS or bool(host and IA_DATA_NODE.match(host))

# ELSTAT's digital library serves no TLS at all (F2 fetched it over http): public PDFs, no credentials sent.
HTTP_ONLY_HOSTS = ('dlib.statistics.gr',)

def check_url(url):
    parsed=urlsplit(url)
    scheme_ok = parsed.scheme=='https' or (parsed.scheme=='http' and parsed.hostname in HTTP_ONLY_HOSTS)
    if (not scheme_ok or not allowed_host(parsed.hostname) or
            parsed.port not in ((None,443) if parsed.scheme=='https' else (None,80)) or parsed.username or parsed.password):
        raise ValueError(f'runtime egress outside HTTPS host allowlist: {parsed.scheme}://{parsed.hostname}')
    return parsed.hostname
