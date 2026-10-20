"""Bind non-media F2 files before the single guarded worker commit attempt."""
from f2lib import *
import subprocess,os
def main():
 validation=json.loads((BASE/'receipts/validation.json').read_text())
 if not validation['artifact_checks_passed']:raise SystemExit('Refuse: artifact validation has errors')
 status=subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--',str(BASE.relative_to(ROOT))],cwd=ROOT,text=True)
 files=subprocess.check_output(['git','ls-files','--others','--cached','--exclude-standard','--',str(BASE.relative_to(ROOT))],cwd=ROOT,text=True).splitlines();bound=[];secret_matches=[]
 secret=os.environ.get('ANEMI_PASS','').encode()
 for name in sorted(set(files)):
  p=ROOT/name
  if not p.is_file() or name.endswith('/receipts/commit-inputs.json'):continue
  if any(x in p.relative_to(BASE).parts for x in ['bulk','cache','blind_pages','contact_sheets','crops','docai','parsed','__pycache__']):raise SystemExit('Refuse: bulk path '+name)
  if p.suffix.lower() in ['.jpg','.png','.pdf','.jpeg','.tif','.tiff']:raise SystemExit('Refuse: media path '+name)
  data=p.read_bytes()
  if secret and secret in data:secret_matches.append(name)
  bound.append(dict(path=name,bytes=len(data),sha256=digest(data)))
 if secret_matches:raise SystemExit('Refuse: credential match in '+str(len(secret_matches))+' files; no values printed')
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 write(BASE/'receipts/commit-inputs.json',dict(base_HEAD=head,branch='sol/funnel-gr',files=bound,total_bytes=sum(x['bytes'] for x in bound),media_files=0,provider_response_payloads=0,credential_value_matches=0,at=stamp(),worker_permission='user explicitly authorised a commit on this branch; no push'))
 print('Bound',len(bound),'files;',round(sum(x['bytes'] for x in bound)/1e6,2),'MB; base',head)
if __name__=='__main__':main()
