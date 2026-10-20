import pathlib,json,hashlib,collections
D=pathlib.Path(__file__).parent;ns={'require':lambda ok,msg:None if ok else (_ for _ in ()).throw(ValueError(msg))};exec((D/'mix1_text_exposure.py').read_text(),ns)
refs=[json.loads(l)['reference'] for l in (D/'benchmark_metadata.jsonl').read_text().splitlines()];idx=ns['TextExposure'](refs)
p=pathlib.Path('/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/out/o5/synth_corpus.jsonl');b=p.read_bytes();h=hashlib.sha256(b).hexdigest();details=json.loads((D/'remote_details.json').read_text());binding=next(x for x in details if 'keys' in x)['inputs'];expected=binding['/home/ubuntu/work/greek-page-ocr/out/o5/synth_corpus.jsonl'];assert h==expected
stats=collections.defaultdict(collections.Counter);witness=[]
for i,line in enumerate(b.decode().splitlines(),1):
 r=json.loads(line);s=r['source_dataset'];stats[s]['rows']+=1;kind=idx.hit(r['text'])
 if kind:stats[s][kind]+=1;witness.append(dict(line=i,source=s,source_doc_id=r['source_doc_id'],kind=kind,text_sha256=hashlib.sha256(r['text'].encode()).hexdigest(),text=r['text']))
a=dict(path=str(p),bytes=len(b),sha256=h,binding_match=True,scope='complete upstream O5 input before E1 train/heldout filtering; not the assembled corpus',per_source=stats,hits=witness)
(D/'o5_source_exposure.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(bytes=len(b),per_source=stats,hits=len(witness))))
