"""Remove unneeded session headers and embedded public-site keys from receipts.

Network byte counts and original response hashes remain in the redaction log.
Stored-body hashes bind the sanitised evidence. No user credential is retained.
Run after collection, before the final build and validation.
"""
import hashlib,json,pathlib,re
B=pathlib.Path(__file__).resolve().parent
log=B/'receipts/local/redactions.json'
changes=json.loads(log.read_text()).get('changes',[]) if log.exists() else []
for p in B.glob('receipts/*/http/*.json'):
    r=json.loads(p.read_text());removed=[]
    for k in list(r.get('headers',{})):
        if k.lower() in ['set-cookie','authorization','proxy-authorization','www-authenticate']:
            del r['headers'][k];removed.append(k)
    body=p.with_suffix('.body');raw=body.read_bytes();clean=re.sub(rb'AIza[A-Za-z0-9_-]{25,}',b'PUBLIC_SITE_KEY_REDACTED',raw)
    if clean!=raw:
        original=hashlib.sha256(raw).hexdigest();body.write_bytes(clean)
        r['response_sha256_before_redaction']=original
        r['sha256']=hashlib.sha256(clean).hexdigest();r['stored_bytes']=len(clean)
        r['body_redactions']=['embedded public website API key; not a user credential']
    if removed:r['redacted_header_names']=removed
    if removed or clean!=raw:
        p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
        changes.append(dict(receipt=str(p.relative_to(B)),removed_header_names=removed,body_changed=clean!=raw,response_bytes=r['bytes'],stored_bytes=len(clean),response_sha256=r.get('response_sha256_before_redaction',r['sha256']),stored_sha256=r['sha256']))
for p in B.glob('receipts/*/transfer.jsonl'):
    rows=[json.loads(s) for s in p.read_text().splitlines()];changed=0
    for r in rows:
        removed=[]
        for k in list(r.get('headers',{})):
            if k.lower() in ['set-cookie','authorization','proxy-authorization','www-authenticate']:
                del r['headers'][k];removed.append(k)
        if removed:r['redacted_header_names']=removed;changed+=1
    if changed:
        p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
        changes.append(dict(receipt=str(p.relative_to(B)),ledger_records_with_session_headers_removed=changed))
log.write_text(json.dumps(dict(purpose='No session cookies, authentication challenge headers or embedded public-site keys are needed for this inventory.',changes=changes),ensure_ascii=False,indent=2)+'\n')
print('Sanitised receipt records',len(changes))
