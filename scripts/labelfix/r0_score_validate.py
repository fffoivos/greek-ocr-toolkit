import json,pathlib,re,base64,io,unicodedata as U,subprocess,collections
from PIL import Image
from html.parser import HTMLParser
root=pathlib.Path.cwd();out=root/'docs/records/labelfix/spellcheck';ev=out/'R0_evidence/scoring'
def ed(a,b):
 if not a:return len(b)
 peq=collections.defaultdict(int);unk=0
 for i,c in enumerate(a):
  if c=='?':unk|=1<<i
  else:peq[c]|=1<<i
 pv=~0;mv=0;score=len(a);top=1<<(len(a)-1)
 for c in b:
  eq=peq[c]|unk;xv=eq|mv;xh=(((eq&pv)+pv)^pv)|eq
  ph=mv|~(xh|pv);mh=pv&xh
  score+=bool(ph&top)-bool(mh&top)
  ph=(ph<<1)|1;mh<<=1
  pv=mh|~(xv|ph);mv=ph&xv
 return score
signs="'’ʼ᾽`´‘“”«»„\"‟‹›′″"
def letters(s,unknown=False):
 return ''.join(c for c in U.normalize('NFD',s) if ((c.isalpha() and c not in signs) or (unknown and c=='?')) and not U.category(c).startswith('M'))
u=[json.loads(s) for s in (ev/'letter_units.jsonl').read_text().splitlines()]
for x in u:
 a=letters(x['truth'],True);b=letters(x['recogniser'])
 assert sum(c!='?' for c in a)==x['truth_slots']
 assert ed(a,b)==x['errors'],x
 assert ed(a.casefold(),b.casefold())==x['errors_case_folded'],x
class Parse(HTMLParser):
 def __init__(self):super().__init__();self.articles=[];self.current=None;self.external=[]
 def handle_starttag(self,tag,at):
  a=dict(at)
  if tag=='article':self.current=dict(id=a['id'],images=[],rects=0,notes=0,labels=0,svg=[]);self.articles.append(self.current)
  if tag in ['script','link','img','iframe']:
   src=a.get('src',a.get('href',''))
   if src:self.external.append(src)
  if self.current:
   if tag=='image':self.current['images'].append(a)
   if tag=='rect':self.current['rects']+=1
   if tag=='textarea':self.current['notes']+=1
   if tag=='svg':self.current['svg'].append(a)
 def handle_endtag(self,tag):
  if tag=='article':self.current=None
h=(out/'R0_review_failures.html').read_text();parser=Parse();parser.feed(h)
sel=[json.loads(s) for s in (ev/'review_selection_60.jsonl').read_text().splitlines()]
assert len(parser.articles)==len(sel)==60
assert len({a['id'] for a in parser.articles})==60
assert not parser.external
for a,s in zip(parser.articles,sel):
 assert a['id']==s['line_id']
 assert a['notes']==1 and len(a['images'])==len(a['svg'])==1
 assert a['rects']==sum(c.isalpha() and c not in signs for c in s['native_prediction'])
 data=base64.b64decode(a['images'][0]['href'].split(',',1)[1]);im=Image.open(io.BytesIO(data));im.load()
 assert im.width==int(a['images'][0]['width']) and im.height==int(a['images'][0]['height'])
 assert im.height+23==int(a['svg'][0]['height'])
 article=re.search(r'<article id="'+re.escape(a['id'])+r'".*?</article>',h,re.S).group()
 assert '<p>Google</p>' in article
 assert 'Recogniser — native cached CTC' in article
script=re.search(r'<script>(.*?)</script>',h,re.S).group(1);pathlib.Path('/tmp/r0c-owner.js').write_text(script)
subprocess.run(['node','--check','/tmp/r0c-owner.js'],check=True)
for p in ['scripts/labelfix/r0_score.py','scripts/labelfix/r0_score_report.py']:
 compile((root/p).read_text(),p,'exec')
d=json.loads((out/'R0_metrics.json').read_text());fs=[json.loads(s) for s in (out/'R0_failures.jsonl').read_text().splitlines()]
for row in d['letters']['by_stratum']:
 rr=[f for f in fs if f['stratum']==row['stratum'] and f['prediction_stream']=='stored_instrument' and f['type'] in ['substitution','insertion','deletion','case','script_mixup']]
 assert len(rr)==row['errors']
 assert sum(f['type']!='case' for f in rr)==row['errors_case_folded']
for f in fs:
 assert f['DATA_MODEL'] in ['DATA','MODEL'] and f['stratum_label'] and f['slot'] is not None
 assert f.get('evidence')
# No UNKNOWN input card can be a confirmed error witness; boundary overlap is masked too.
assert all(f.get('card_id') not in ['item00171','item00564'] and not set(f.get('card_ids',[]))&{'item00171','item00564'} for f in fs)
ps=[json.loads(s) for s in (ev/'punctuation_sites.jsonl').read_text().splitlines()]
assert next(e for e in ps if e['line_id']=='51fe7386-p000024-l0022' and e['letter_boundary']==1)['status']=='UNKNOWN_UNRESOLVED_CARD'
v=json.loads((ev/'validation.json').read_text());v.update(independent_bit_parallel_edit_count_agreement=len(u),
 embedded_PNGs_decoded=60,native_letter_box_counts_verified=60,one_note_per_line=True,
 google_and_native_recogniser_on_every_row=True,page_external_resources=0,javascript_syntax='PASS node --check',
 metric_failure_ledger_reconciliation=True,unresolved_overlap_exclusion=True,
 browser_visual_interaction_QA='UNVERIFIED: cached headless Firefox aborts; computer-use access to Firefox was not approved',
 native_card_visual_inspection=['item00174 clipped UNKNOWN','item00834 opening quote','item00847 smooth breathing'])
(ev/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps(v,indent=2))
