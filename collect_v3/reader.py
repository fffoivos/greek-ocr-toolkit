"""Pinned F2 Document AI, launch-time credentials only; no provider retries."""
import base64,json,os,urllib.request,urllib.error
from pathlib import Path
from .common import TOKEN_ENV,read_json,write_json
from .ledger import UncertainRead

BINDING=read_json(Path(__file__).with_name('processor_binding.json'))

def strip_response(raw):
    # Never retain headers/request/auth objects or embedded page rasters.
    document=raw['document'];document.pop('content',None)
    for page in document.get('pages',[]):page.pop('image',None)
    return {'document':document}

class DocumentAI:
    def __init__(self,bucket):self.bucket=bucket;self.calls=0;self.credentials=None
    def token(self):
        if os.environ.get(TOKEN_ENV):return os.environ[TOKEN_ENV]
        if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
            raise ValueError('credentials require COLLECT_V3_ACCESS_TOKEN or GOOGLE_APPLICATION_CREDENTIALS in the environment')
        import google.auth,google.auth.transport.requests,requests
        from urllib.parse import urlsplit
        from .transport import retry_seconds
        bucket=self.bucket
        class LimitedSession(requests.Session):
            # requests follows redirects via send(), so every auth hop shares
            # the same limiter; transport retries (if any) do too.
            def send(self,request,**kwargs):
                from .egress import check_url
                host=check_url(request.url)
                bucket.acquire(host)
                response=super().send(request,**kwargs)
                if response.status_code in (429,503):bucket.defer(host,retry_seconds(response.headers.get('Retry-After')))
                return response
        with LimitedSession() as session:
            session.trust_env=False
            request=google.auth.transport.requests.Request(session=session)
            if self.credentials is None:
                self.credentials,_=google.auth.load_credentials_from_file(os.environ['GOOGLE_APPLICATION_CREDENTIALS'],scopes=['https://www.googleapis.com/auth/cloud-platform'],request=request)
            if not self.credentials.valid:self.credentials.refresh(request)
        return self.credentials.token
    def read(self,image):
        b=BINDING;host=b['location']+'-documentai.googleapis.com'
        url=f'https://{host}/v1/projects/{b["project"]}/locations/{b["location"]}/processors/{b["processor"]}/processorVersions/{b["version"]}:process'
        # Credential refresh precedes the paid request; never persisted.
        token=self.token();payload={'rawDocument':{'content':base64.b64encode(Path(image).read_bytes()).decode(),'mimeType':'image/jpeg'},'processOptions':b['options'],'skipHumanReview':True}
        self.bucket.acquire(host)
        request=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+token,'Content-Type':'application/json','x-goog-user-project':b['user_project'],'User-Agent':'greek-ocr-research/0.1 (foivos.karounos@gmail.com)'},method='POST')
        self.calls+=1
        try:
            with urllib.request.build_opener(urllib.request.ProxyHandler({}),__import__('collect_v3.transport',fromlist=['NoRedirect']).NoRedirect()).open(request,timeout=180) as response:return strip_response(json.loads(response.read()))
        except urllib.error.HTTPError as e:
            if e.code in (429,503):
                from .transport import retry_seconds
                self.bucket.defer(host,retry_seconds(e.headers.get('Retry-After')))
            # Suppress provider error bodies, request headers and credentials.
            raise UncertainRead(f'Document AI HTTP {e.code}; no automatic paid retry') from None

def read_once(ledger,reader,page,tranche,rawroot,after_response=None):
    key=page['image_sha256'];path=Path(rawroot)/(key+'.json')
    reservation,fresh=ledger.reserve(key,page['id'],tranche)
    if path.exists():
        raw=read_json(path);ledger.complete(key);return raw
    if reservation['state']!='reserved':raise UncertainRead('paid request has no durable response; reconcile without re-reading')
    ledger.start(key)
    raw=strip_response(reader.read(page['image']))
    write_json(path,raw)
    if after_response:after_response()
    ledger.complete(key);return raw
