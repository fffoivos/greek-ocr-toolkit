#!/usr/bin/env python3
"""Verify accessible scan-file signatures with 512-byte HTTP Range probes only."""
from greekocr._vendor.scripts.fetch.o4c_common import *

def classify_prefix(data):
    if data.startswith(b'%PDF-'):return 'PDF'
    if data.startswith(b'AT&TFORM') and data[12:16] in (b'DJVU',b'DJVM'):return 'DjVu'
    return None

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--item');p.add_argument('--all-reviewed',action='store_true')
    p.add_argument('--offline',action='store_true');args=p.parse_args()
    if not args.item and not args.all_reviewed:p.error('--item or --all-reviewed required')
    reviews={r['document_id']:r for r in read_rows(EVIDENCE/'print_reviews.jsonl') if r['source']=='archive'}
    records=[r for r in read_rows(EVIDENCE/'discovery_merged.jsonl') if r['source']=='archive' and r['rights']['compatible'] and r.get('download_url')]
    out=EVIDENCE/'media_probes.jsonl';rows={r['document_id']:r for r in read_rows(out)};h=HTTP('archive_media',offline=args.offline)
    for r in records:
        ident=r['document_id']
        if args.item and ident!=args.item:continue
        if args.all_reviewed and reviews.get(ident,{}).get('status')!='verified-target-sample':continue
        if rows.get(ident,{}).get('status')=='verified-file-prefix' and rows[ident].get('probe_url')==r['download_url']:continue
        probe={'source':'archive','document_id':ident,'probe_url':r['download_url'],'range':'bytes=0-511','status':'unverified'}
        try:
            m,data=h.get(r['download_url'],range_header='bytes=0-511',limit=512)
            kind=classify_prefix(data)
            if m['status']!=206 or len(data)>512 or not kind:raise ProbeError('no bounded PDF/DjVu file signature')
            probe.update(status='verified-file-prefix',format=kind,resolved_url=m['url'],prefix_sha256=m['sha256'],bytes=len(data),
              fetched_at=m['fetched_at'],content_range=m['headers'].get('content-range'),content_type=m['headers'].get('content-type'))
        except Exception as e:probe['error']=str(e)
        rows[ident]=probe;save_rows(out,rows.values());print(ident,probe['status'],flush=True)
if __name__=='__main__':main()
