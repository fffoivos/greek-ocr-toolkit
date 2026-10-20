"""SYNTHETIC ONLY: SR-B2 fixtures never enter experimental answers/results."""
import base64,copy,io,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import ROOT,PACK_ROOT,EFF,dump,jsonl,sha,rows,itemfile,idfield
from PIL import Image
from scan_rollout import inspect
from b2_common import disagreements,resolve_records,change_accounting,load_run,HEADS
from build_tiebreak import submask,build
from map_answers import map_records
from score_all import run,load_scorer,official_score,accuracy_metrics
VALIDATION=ROOT/'validation'
def temp():return Path(tempfile.mkdtemp(prefix='SYNTHETIC-B2-',dir=VALIDATION))
def bsb(i='c1',**kw):return dict(card_id=i,letters='y',marks='y',crop_ok='y',errors=[],detail='SYNTHETIC',**kw)
def yer(i='a1',slots=None):return dict(item_id=i,slots=slots or {},confidence={s:'high' for s in slots or {}},unmarked_final_hard_signs=[],pre1918='unclear',note='SYNTHETIC')
def owner(i='o1',choice='A',head='acute'):
 return dict(card_id=i,choice=choice,anchor_heads=dict(breathing='none',accent=head,diaeresis='none',subscript='none'),letter_heads=[],readability='readable',ownership_ok=True,confidence='high',note='SYNTHETIC',usage={'input_tokens':0,'output_tokens':0})
class ScannerV2(unittest.TestCase):
 def fixture(self,code='',image=None):
  root=temp();d=root/'r1';(d/'img').mkdir(parents=True);(d/'img/a.png').write_bytes(self.png(Image.new('RGB',(3372,292),'white')))
  dump(root/'MANIFEST.r1.json',{'files':{'img/a.png':sha(d/'img/a.png')}})
  events=[{'payload':{'type':'custom_tool_call','name':'exec','input':code}}]
  if image is not None:events.append({'payload':{'type':'function_call_output','output':[{'type':'input_image','image_url':'data:image/png;base64,'+base64.b64encode(image).decode()}]}})
  r=root/'rollout.jsonl';jsonl(r,events);return r,d
 def png(self,im):
  b=io.BytesIO();im.save(b,format='PNG');return b.getvalue()
 def test_downscale(self):
  im=Image.new('RGB',(3372,292),'white')
  for x in range(0,3372,10):im.paste((x%256,20,30),(x,30,x+5,260))
  r,d=self.fixture(image=self.png(im.resize((2048,177),Image.Resampling.LANCZOS)));(d/'img/a.png').write_bytes(self.png(im));dump(d.parent/'MANIFEST.r1.json',{'files':{'img/a.png':sha(d/'img/a.png')}})
  result=inspect(r,d);self.assertTrue(result['ok'],result);self.assertEqual(result['image_matches'][0]['match'],'downscale')
 def test_outside_image(self):
  r,d=self.fixture(image=self.png(Image.new('RGB',(20,30),'red')));self.assertFalse(inspect(r,d)['ok'])
 def test_keys_idiom_and_computed_path(self):
  r,d=self.fixture('for (const key of x.keys()) image((await tools.view_image({path:`img/${key}.png`})).image_url);');self.assertTrue(inspect(r,d)['ok'])
 def test_template_outside(self):
  r,d=self.fixture('await tools.exec_command({cmd:`cat /private/tmp/outside/${p}.txt`})');self.assertFalse(inspect(r,d)['ok'])
 def test_components(self):
  for code in ['cat ../x','cat ~/x','cat $HOME/x','cat keys/a','cat monkey.json','cat truth','cat verdict','cat opus_reference/x','cat MANIFEST','cat sol_reading_packs/x','cat r2/x']:
   r,d=self.fixture('await tools.exec_command({cmd:'+json.dumps(code)+'})');self.assertFalse(inspect(r,d)['ok'],code)
class Units(unittest.TestCase):
 def test_disagreements_exclude_metadata(self):
  a=bsb();b=copy.deepcopy(a);b['detail']='changed';self.assertEqual(disagreements('bsb',{'c1':a},{'c1':b},{}),{})
  b['marks']='n';self.assertEqual(disagreements('bsb',{'c1':a},{'c1':b},{}),{'c1':['marks']})
  self.assertEqual(disagreements('yer',{'a1':yer(slots={'1':'ъ','2':'ь'})},{'a1':yer(slots={'1':'ь','2':'ь'})},{}),{'a1':['1']})
 def test_owner_tuple_transcription_and_unknown(self):
  item={'anchor_index':0,'options':{'A':'ά','B':'ὰ','C':'έ'}};a=owner();b=owner(choice='C')
  self.assertEqual(disagreements('owner39',{'o1':a},{'o1':b},{'o1':item}),{'o1':['anchor']})
  b=owner();b['anchor_heads']['accent']='unknown';self.assertTrue(disagreements('owner39',{'o1':a},{'o1':b},{'o1':item}))
 def test_yer_submask_round_trip(self):
  masked,mapping=submask('дом⟦1⟧ кон⟦2⟧ стол⟦3⟧','домъ конь столъ',['3','2']);self.assertEqual(masked,'домъ кон⟦1⟧ стол⟦2⟧');self.assertEqual(mapping,{'1':'2','2':'3'})
  key={'readers':{'r3':['k1']},'items':{'k1':{'source_id':'a1','control':False,'slot_to_source':mapping}}};item={'item_id':'k1','slots':2};answer=yer('k1',{'1':'ь','2':'ъ'})
  mapped,_=map_records('yer','r3',[answer],key,[item]);self.assertEqual(mapped[0]['slots'],{'2':'ь','3':'ъ'});self.assertEqual(set(mapped[0]['confidence']),{'2','3'})
 def test_per_field_resolution_and_unresolved(self):
  a=bsb();b=bsb();c=bsb();b.update(letters='n',marks='n');c.update(letters='n',marks='na')
  out,u=resolve_records('bsb',{'c1':a},{'c1':b},{'c1':c},{})
  self.assertEqual((out[0]['letters'],out[0]['marks'],out[0]['crop_ok']),('n','u','y'));self.assertEqual(u[0]['unit'],'marks')
 def test_yer_missing_third(self):
  out,u=resolve_records('yer',{'a1':yer(slots={'1':'ъ','2':'ь'})},{'a1':yer(slots={'1':'ь','2':'ь'})},{},{})
  self.assertEqual(out[0]['slots'],{'1':'u','2':'ь'});self.assertEqual(len(u),1)
 def test_owner_full_winner_and_unresolved(self):
  items={'o1':{'anchor_index':0,'options':{'A':'ά','B':'ὰ','C':'έ'}}};a=owner();b=owner(choice='B',head='grave');c=copy.deepcopy(b);c['note']='third'
  out,u=resolve_records('owner39',{'o1':a},{'o1':b},{'o1':c},items);self.assertEqual(out[0],b);self.assertEqual(u,[])
  c=owner(choice='C');out,u=resolve_records('owner39',{'o1':a},{'o1':b},{'o1':c},items);self.assertEqual(out[0]['choice'],'unreadable');self.assertEqual(set(out[0]['anchor_heads'].values()),{'unknown'})
 def test_change_accounting(self):
  a=dict(a='n',b='y',c='u',d='y');b=dict(a='y',b='n',c='n',d='y');t=dict.fromkeys(a,'y');r=change_accounting(a,b,t)
  self.assertEqual([r[k] for k in ('changed_to_correct','changed_to_wrong','changed_between_wrong','net_correct','compared')],[1,1,1,0,4])
 def test_void_exclusion_and_dependency(self):
  root=temp();d=root/'answers/bsb';jsonl(d/'r1.mapped.jsonl',[bsb()]);dump(d/'r1.scan.json',{'ok':False});jsonl(d/'S2.mapped.jsonl',[bsb()]);dump(d/'S2.unresolved.json',{'used_readers':['r1']})
  with patch('b2_common.ROOT',root):
   self.assertEqual(load_run('bsb','r1'),({},'VOID'));self.assertEqual(load_run('bsb','S2'),({},'VOID dependency r1'))
 def test_official_scorer_yer_r3_partial(self):
  truth={'bsb':{'c1':bsb()},'yer':{'a1':yer(slots={'1':'ъ','2':'ь'})}}
  result=official_score(load_scorer(),'yer','Sol r3',{'a1':yer(slots={'2':'ь'})},truth)
  self.assertEqual(result['agreement_with_truth']['slots']['compared'],1);self.assertEqual(result['agreement_with_truth']['slots']['agree'],1)
class TieBuild(unittest.TestCase):
 def test_synthetic_bsb_build_closure_and_controls(self):
  root=temp();packs=root/'packs';dest=packs/'bsb/r1';(dest/'crops').mkdir(parents=True)
  im=Image.new('RGB',(30,30),'white');bio=io.BytesIO();im.save(bio,format='PNG');data=bio.getvalue();import hashlib
  image='crops/'+hashlib.sha256(data).hexdigest()+'.png';(dest/image).write_bytes(data)
  public=[dict(card_id='k0000000001',crop=image,google_text='δοκιμή',word_scripts=[]),dict(card_id='k0000000002',crop=image,google_text='δοκιμή',word_scripts=[])]
  jsonl(dest/'cards.jsonl',public);key={'readers':{'r1':['k0000000001','k0000000002']},'items':{'k0000000001':dict(source_id='c1',control=False),'k0000000002':dict(source_id='ctl',control=True,expected={'marks':'n'})}};dump(root/'keys/bsb.json',key)
  left={'c1':bsb()};right=copy.deepcopy(left);right['c1']['marks']='n'
  with patch('build_tiebreak.ROOT',root),patch('build_tiebreak.PACK_ROOT',packs),patch('scan_packs.ROOT',root),patch('scan_packs.PACK_ROOT',packs),patch('build_tiebreak.source_items',return_value={'c1':public[0]}),patch('build_tiebreak.load_run',side_effect=[(left,'OK'),(right,'OK')]):
   receipt=build('bsb')
  self.assertTrue(receipt['scan_ok']);self.assertEqual(receipt['controls'],1);self.assertTrue((packs/'bsb/MANIFEST.r3.json').exists());k=json.loads((root/'keys/bsb_r3.json').read_text());self.assertEqual(len(k['items']),2);self.assertTrue(set(k['items']).isdisjoint(key['items']))
 def test_no_pack_missing_or_zero(self):
  root=temp();a={'c1':bsb()}
  with patch('build_tiebreak.PACK_ROOT',root),patch('build_tiebreak.source_items',return_value=a),patch('build_tiebreak.load_run',side_effect=[(a,'OK'),(a,'OK')]):r=build('bsb')
  self.assertIn('zero',r['status']);self.assertFalse((root/'bsb/r3').exists())
class Integration(unittest.TestCase):
 def test_void_is_absent_from_all_result_tables(self):
  root=temp();d=root/'answers/bsb';jsonl(d/'r1.mapped.jsonl',[bsb('c001')]);dump(d/'r1.scan.json',{'ok':False});dump(d/'r1.controls.json',{'controls':[],'flagged':False,'control_errors':0})
  dump(root/'usage_ledger.json',[{'bed':'bsb','reader':'r1'}])
  with patch('b2_common.ROOT',root),patch('score_all.ROOT',root):result=run()
  self.assertEqual(result['status']['bsb']['Sol r1'],'VOID');self.assertNotIn('Sol r1',result['beds']['bsb']['readers']);self.assertNotIn('Sol r1',result['beds']['bsb']['controls']);self.assertEqual(result['cost']['sol'],[])
  self.assertFalse(result['beds']['bsb']['disagreements']);self.assertFalse(result['beds']['bsb']['agreement_matrix'])
 def test_yer_and_owner_pack_mapping_integration(self):
  import shutil
  from b2_common import source_items
  from owner39_validate import normalize
  from owner39_common import clusters,is_letter,tuple_heads
  for bed in ('yer','owner39'):
   root=temp();packs=root/'packs';source=PACK_ROOT/bed/'r1';dest=packs/bed/'r1'
   manifest=json.loads((source.parent/'MANIFEST.r1.json').read_text())
   for rel in manifest['files']:
    target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/rel,target)
   key=json.loads((ROOT/f'keys/{bed}.json').read_text());dump(root/f'keys/{bed}.json',key);items=source_items(bed)
   if bed=='yer':
    iid=next(i for i,r in items.items() if r['slots']>=2);a=yer(iid,{str(j+1):'ъ' for j in range(items[iid]['slots'])});b=copy.deepcopy(a);b['slots']['2']='ь'
   else:
    iid=next(iter(items));item=items[iid]
    def answer(choice):
     r=owner(iid,choice);ls=[c for c in clusters(item['options'][choice]) if is_letter(c[0])];r['anchor_heads']=tuple_heads(ls[item['anchor_index']]);r['ownership_ok']=True if any(v!='none' for v in r['anchor_heads'].values()) else None;return r
    a=answer('A');b=answer('B')
   with patch('build_tiebreak.ROOT',root),patch('build_tiebreak.PACK_ROOT',packs),patch('scan_packs.ROOT',root),patch('scan_packs.PACK_ROOT',packs),patch('build_tiebreak.source_items',return_value={iid:items[iid]}),patch('build_tiebreak.load_run',side_effect=[({iid:a},'OK'),({iid:b},'OK')]):receipt=build(bed)
   self.assertTrue(receipt['scan_ok']);r3key=json.loads((root/f'keys/{bed}_r3.json').read_text());r3items=rows(packs/bed/'r3'/itemfile(bed));answers=[]
   for item in r3items:
    oid=item[idfield(bed)];meta=r3key['items'][oid]
    if bed=='yer':
     slots=meta['expected']['slots'] if meta['control'] else {s:'ь' for s in meta['slot_to_source']};answers.append(yer(oid,slots))
    else:
     if meta['control']:
      e=meta['expected'];r=owner(oid,e['choice']);r['anchor_heads']=e['heads'];r['ownership_ok']=True if any(v!='none' for v in e['heads'].values()) else None
      if e['choice']=='literal':r['transcription']=e['form']
     else:
      choice=next(k for k,v in meta['option_to_source'].items() if v==a['choice']);r=copy.deepcopy(a);r.update(card_id=oid,choice=choice)
     answers.append(r)
   mapped,controls=map_records(bed,'r3',answers,r3key,r3items);self.assertEqual(controls['control_errors'],0);self.assertEqual(len(mapped),1);self.assertEqual(mapped[0][idfield(bed)],iid)
   if bed=='yer':self.assertEqual(mapped[0]['slots'],{'2':'ь'});self.assertEqual(next(r for r in r3items if not r3key['items'][r['item_id']]['control'])['slots'],1)
   else:self.assertEqual(mapped[0]['choice'],a['choice']);normalize(mapped[0],items[iid])
if __name__=='__main__':unittest.main()
