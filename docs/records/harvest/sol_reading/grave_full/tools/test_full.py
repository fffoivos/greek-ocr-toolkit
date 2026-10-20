#!/usr/bin/env python3
"""Synthetic SR-G3 tests. No synthetic observations enter the live reports."""
import contextlib, io, shutil, unittest, tempfile
from common_full import *
import common_full as common
import build_full as build
import flag_full as flag
import confirm_full as confirm
from PIL import Image
LIVE_ROOT=ROOT; LIVE_BED=BED

class AccentTests(unittest.TestCase):
    def test_acute(self): self.assertEqual(build.accent_anchor('καί'),(2,'acute'))
    def test_grave(self): self.assertEqual(build.accent_anchor('καὶ'),(2,'grave'))
    def test_monosyllable(self): self.assertEqual(build.accent_anchor('ἤ'),(0,'acute'))
    def test_long_word(self): self.assertIsNotNone(build.accent_anchor('κοινωνιολογικὴ'))
    def test_consonant_final(self): self.assertEqual(build.accent_anchor('καθώς'),(3,'acute'))
    def test_penult(self): self.assertIsNone(build.accent_anchor('λέγει'))
    def test_antepenult(self): self.assertIsNone(build.accent_anchor('ἄνθρωπος'))
    def test_circumflex(self): self.assertIsNone(build.accent_anchor('αὐτοῦ'))
    def test_unaccented(self): self.assertIsNone(build.accent_anchor('και'))
    def test_last_accent(self): self.assertEqual(build.accent_anchor('ἄνθρωπός'),(6,'acute'))
    def test_diphthong_first(self): self.assertEqual(build.accent_anchor('άι'),(0,'acute'))
    def test_hiatus(self): self.assertIsNone(build.accent_anchor('άϊ'))
    def test_later_vowel(self): self.assertIsNone(build.accent_anchor('κάτι'))
    def test_punct(self): self.assertEqual(build.accent_anchor('«καλή,»'),(3,'acute'))
    def test_nfd(self): self.assertEqual(build.accent_anchor(build.U.normalize('NFD','καὶ')),build.accent_anchor('καὶ'))
    def test_hyphen(self): self.assertTrue(build.hyphen_fragment('τὴν καλὴ-',2))
    def test_separate_hyphen(self): self.assertTrue(build.hyphen_fragment('τὴν καλὴ -',2))
    def test_nonfragment(self): self.assertFalse(build.hyphen_fragment('τὴν καλὴ',2))
    def test_touches(self): self.assertTrue(g2.touches_punctuation('καὶ καλή,',2,'καλή'))
    def test_bare_end(self): self.assertFalse(g2.touches_punctuation('καλή',1,'καλή'))

class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key=load(LIVE_ROOT/'keys/key.json'); cls.receipt=load(LIVE_ROOT/'BUILD_RECEIPT.json')
    def test_cards(self): self.assertEqual(len(self.receipt['card_coverage']),100)
    def test_unique_bed(self):
        bed=[m['bed_id'] for m in self.key.values() if m['role']=='bed']
        self.assertEqual(len(bed),len(set(bed)))
    def test_counts(self):
        self.assertEqual(sum(c['bed'] for c in self.receipt['contexts']),self.receipt['items'])
        self.assertEqual(sum(self.receipt['drops_by_reason'].values()),self.receipt['dropped'])
    def test_context_limits(self):
        for c in self.receipt['contexts']:
            self.assertLessEqual(c['bed'],90); self.assertEqual(c['controls'],math.ceil(c['bed']/9))
    def test_all_closures(self):
        for c in self.receipt['contexts']:
            key={i:m for i,m in self.key.items() if m['context']==c['name']}
            # Live readers may contain answers/zoom; closure covers original payload.
            with tempfile.TemporaryDirectory(prefix='g4-original-',dir=flag.scan_rollout.REPLAY_TMP) as tmp:
                folder=Path(tmp)
                for rel in load(LIVE_BED/f'MANIFEST.{c["name"]}.json')['files']:
                    dest=folder/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(LIVE_BED/c['name']/rel,dest)
                result=g1.scan(folder,key)
            self.assertEqual(result['files'],load(LIVE_BED/f'MANIFEST.{c["name"]}.json')['files'])
            self.assertEqual(sha(LIVE_BED/f'MANIFEST.{c["name"]}.json'),c['manifest_sha256'])
    def test_no_approximation(self):
        for m in self.key.values():
            if m['role']=='bed':
                self.assertFalse(m['geometry']['approx_letter_box']); self.assertFalse(m['geometry']['anchor']['approx_letter_box'])
    def test_scope(self):
        for m in self.key.values():
            if m['role']=='bed':
                self.assertEqual(build.accent_anchor(m['word_labelled']),(m['anchor_index'],m['label_accent']))
                self.assertFalse(build.hyphen_fragment(m['c1_line_text'],m['word_index']))
    def test_control_pool(self):
        pool=control_pool(); self.assertEqual({m['truth_accent'] for _,m,_ in pool},set(ACCENTS[:-1]))
        self.assertTrue(all(m['stratum']!='nlg__poly1900' for _,m,_ in pool))
    def test_control_bytes(self):
        old={p['item_id']:p for p in public_rows(PACK_ROOT/'grave/r1')}
        for i,m in self.key.items():
            if m['role']=='control':
                p=next(p for p in public_rows(LIVE_BED/m['context']) if p['item_id']==i)
                for f in ('word_image','letter_image'):
                    self.assertEqual(sha(LIVE_BED/m['context']/p[f]),sha(PACK_ROOT/'grave/r1'/old[m['g1_id']][f]))
    def test_render_pixels(self):
        m=next(m for m in self.key.values() if m['role']=='bed'); g=m['geometry']
        with Image.open(g['source_crop']) as im: w,l,_,_=g1.render(im.convert('RGB'),g['word']['box'],g['anchor']['box'])
        self.assertTrue((LIVE_ROOT/'keys/rendered/img'/(hashlib.sha256(g1.encode(w)).hexdigest()+'.png')).exists())
        self.assertTrue((LIVE_ROOT/'keys/rendered/img'/(hashlib.sha256(g1.encode(l)).hexdigest()+'.png')).exists())
    def test_avoid_controls(self):
        pool=control_pool(); excluded={pool[0][0]}
        picked=choose_controls(pool,4,'test',excluded)
        self.assertNotIn(pool[0][0],{i for i,_,_ in picked})

class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.key={'k1234567890':dict(role='bed',stratum='nlg__poly1900',card_id='c001',line_id='line',label_accent='acute',touches_punct=False)}
        self.a=[dict(item_id='k1234567890',accent='grave',confidence='high',note='')]
    def test_valid(self): self.assertEqual(len(validate(self.a,self.key)),1)
    def test_missing(self):
        with self.assertRaises(ValueError): validate([],self.key)
    def test_order(self):
        self.a[0]['item_id']='k0000000000'
        with self.assertRaises(ValueError): validate(self.a,self.key)
    def test_extra_field(self):
        self.a[0]['truth']='grave'
        with self.assertRaises(ValueError): validate(self.a,self.key)
    def test_bad_accent(self):
        self.a[0]['accent']='maybe'
        with self.assertRaises(ValueError): validate(self.a,self.key)
    def test_confidence(self):
        self.a[0]['confidence']=True
        with self.assertRaises(ValueError): validate(self.a,self.key)
    def test_note(self):
        self.a[0]['note']=None
        with self.assertRaises(ValueError): validate(self.a,self.key)
    def test_duplicate_json(self):
        p=LIVE_ROOT/'keys/synthetic/duplicate.jsonl'; p.parent.mkdir(parents=True,exist_ok=True); p.write_text('{"item_id":"x","item_id":"y"}\n')
        with self.assertRaises(ValueError): g2.load_answers(p)

class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture=LIVE_ROOT/'keys/synthetic/pipeline'; cls.packs=cls.fixture/'packs'; cls.answers=cls.fixture/'answers'
        if cls.fixture.exists(): shutil.rmtree(cls.fixture)
        (cls.fixture/'keys').mkdir(parents=True); cls.answers.mkdir()
        for name in ('key.json','CONTROL_VERIFICATION.json'):
            shutil.copyfile(LIVE_ROOT/'keys'/name,cls.fixture/'keys'/name)
        cls.key=load(cls.fixture/'keys/key.json')
        for name in dict.fromkeys(m['context'] for m in cls.key.values()):
            shutil.copytree(LIVE_BED/name,cls.packs/name)
            shutil.copyfile(LIVE_BED/f'MANIFEST.{name}.json',cls.packs/f'MANIFEST.{name}.json')
        cls.old=[(mod,mod.ROOT,mod.BED) for mod in (common,flag,confirm)]
        for mod,_,_ in cls.old: mod.ROOT=cls.fixture; mod.BED=cls.packs
        # Flag every bed item with all five types; controls use correct references except two in c1.
        types=list(ACCENTS); index=0; ctrl_errors=0
        for name in dict.fromkeys(m['context'] for m in cls.key.values()):
            aa=[]
            for iid,m in cls.key.items():
                if m['context']!=name: continue
                if m['role']=='control':
                    a=m['truth_accent']
                    if name=='p1c1' and ctrl_errors<2: a='unreadable'; ctrl_errors+=1
                else:
                    a=types[index%5]; index+=1
                    if a==m['label_accent']: a='grave' if a=='acute' else 'acute'
                aa.append(dict(item_id=iid,accent=a,confidence='high',note='SYNTHETIC fixture'))
            (cls.answers/(name+'.jsonl')).write_text(''.join(json.dumps(a)+'\n' for a in aa))
            (cls.answers/(name+'.scan.json')).write_text(json.dumps(dict(scanner_version=4,ok=True,violations=[],synthetic=True)))
        cls.result=flag.run(True,cls.answers)
        cls.p2=load(cls.fixture/'keys/p2_key.json')
        for name in dict.fromkeys(m['context'] for m in cls.p2.values()):
            aa=[]
            for iid,m in cls.p2.items():
                if m['context']==name:
                    a=m['truth_accent'] if m['role']=='control' else m['label_accent']
                    aa.append(dict(item_id=iid,accent=a,confidence='high',note='SYNTHETIC reread'))
            (cls.answers/(name+'.jsonl')).write_text(''.join(json.dumps(a)+'\n' for a in aa))
        cls.rows=confirm.run(answer_root=cls.answers)
        cls.lead=[dict(item_id=r['item_id'],printed=r['label'] if j%2 else r['p1']) for j,r in enumerate(cls.rows)]
        dump(cls.fixture/'LEAD_EYE.SYNTHETIC.json',cls.lead)
        confirm.run(cls.fixture/'LEAD_EYE.SYNTHETIC.json',cls.answers)
    @classmethod
    def tearDownClass(cls):
        for mod,root,bed in cls.old: mod.ROOT=root; mod.BED=bed
    def test_flags_all_types(self):
        self.assertEqual(self.result['flagged'],self.result['items'])
        self.assertTrue(all(self.result['flagged_counts_by_answer'][a]>0 for a in ACCENTS))
    def test_control_threshold(self):
        self.assertTrue(self.result['controls']['p1c1']['flagged'])
        self.assertFalse(self.result['controls']['p1c2']['flagged'])
    def test_overlap(self): self.assertEqual(len(self.result['overlap']),load(LIVE_ROOT/'BUILD_RECEIPT.json')['overlap_G1'])
    def test_p2_split(self):
        names={m['context'] for m in self.p2.values()}; self.assertGreater(len(names),1)
        for name in names:
            part={i:m for i,m in self.p2.items() if m['context']==name}
            self.assertLessEqual(len(part),90); self.assertTrue(g1.scan(self.packs/name,part)['ok'])
    def test_p2_fresh(self): self.assertFalse(set(self.key)&set(self.p2))
    def test_reread_coverage(self): self.assertEqual(len(self.rows),self.result['flagged'])
    def test_p2_controls(self):
        rr=load(self.fixture/'keys/CONFIRM_RECEIPT.json')
        self.assertTrue(all(c['passes']==c['total'] for c in rr['controls'].values()))
    def test_review_dimensions(self):
        sheets=list((self.fixture/'keys/review').glob('flags_*.png')); self.assertEqual(len(sheets),math.ceil(len(self.rows)/30))
        for p in sheets:
            with Image.open(p) as im: self.assertEqual(im.width,1600); self.assertLessEqual(im.height,2700)
    def test_template(self): self.assertTrue(all(r['printed'] is None for r in load(self.fixture/'LEAD_EYE.template.json')))
    def test_final_counts(self):
        m=confirm.final_metrics(self.result,self.rows,self.lead)
        self.assertEqual(m['confirmed'],math.ceil(len(self.rows)/2)); self.assertEqual(m['confirmed']+m['false_flags'],len(self.rows))
        self.assertEqual(m['p2_accuracy']['count'],len(self.rows)//2)
        self.assertEqual(m['label_acute_printed_grave_per_card']['total'],100)
    def test_final_coverage(self):
        with self.assertRaises(ValueError): confirm.final_metrics(self.result,self.rows,self.lead[:-1])
    def test_final_duplicate(self):
        with self.assertRaises(ValueError): confirm.final_metrics(self.result,self.rows,self.lead+[self.lead[0]])
    def test_final_invalid(self):
        with self.assertRaises(ValueError): confirm.final_metrics(self.result,self.rows,[dict(item_id=r['item_id'],printed=None) for r in self.rows])
    def test_missing_answers(self):
        with self.assertRaises(ValueError): read_contexts(self.key,'p1c',self.fixture/'absent')
    def test_stale_p2(self):
        p=self.fixture/'PASS1.json'; original=p.read_bytes(); p.write_bytes(original+b' ')
        try:
            with self.assertRaises(ValueError): confirm.run(answer_root=self.answers)
        finally: p.write_bytes(original)
    def test_one_control_error_not_flagged(self):
        answers={i:dict(item_id=i,accent=m['truth_accent'] if m['role']=='control' else m['label_accent'],confidence='high',note='') for i,m in self.key.items()}
        iid=next(i for i,m in self.key.items() if m['role']=='control')
        answers[iid]['accent']='unreadable'
        self.assertFalse(control_report(self.key,answers)[self.key[iid]['context']]['flagged'])
    def test_zero_flags_min_controls(self):
        before={p.name for p in self.packs.iterdir()}
        rec=flag.build_reread(dict(flags=[]),self.key)
        self.assertEqual(rec[0]['bed'],0); self.assertEqual(rec[0]['controls'],2)
        for m in load(self.fixture/'keys/p2_key.json').values(): self.assertEqual(m['role'],'control')
        # Restore full synthetic reread output for following tests and review artifacts.
        flag.build_reread(self.result,self.key)
        for p in self.packs.iterdir():
            if p.name not in before:
                if p.is_dir(): shutil.rmtree(p)
                else: p.unlink()
    def test_final_zero_denominator(self):
        metrics=confirm.final_metrics(dict(items=0,bed=[]),[],[])
        self.assertIsNone(metrics['p2_accuracy']['rate']); self.assertIsNone(metrics['stratum_grave_base_rate']['rate'])
    def test_closure_leak(self):
        folder=self.packs/'p2a'; extra=folder/'truth.txt'; extra.write_text('grave')
        try:
            with self.assertRaises(ValueError): g1.scan(folder,{i:m for i,m in self.p2.items() if m['context']=='p2c1'})
        finally: extra.unlink()

if __name__=='__main__':
    stream=io.StringIO(); suite=unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    text=stream.getvalue()+f'\nSynthetic and build checks: {result.testsRun-len(result.failures)-len(result.errors)}/{result.testsRun}\n'
    (LIVE_ROOT/'TEST_RESULTS.txt').write_text(text); print(text)
    dump(LIVE_ROOT/'keys/TEST_SUMMARY.json',dict(passed=result.testsRun-len(result.failures)-len(result.errors),total=result.testsRun,ok=result.wasSuccessful()))
    sys.exit(0 if result.wasSuccessful() else 1)
