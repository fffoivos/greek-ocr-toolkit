"""CP7 offline constants, deterministic sampling and public-pack validation."""
import hashlib,json,random,re,sys,unicodedata
from pathlib import Path
HERE=Path(__file__).resolve().parent
SEG=HERE.parent
ROOT=SEG.parents[3]
PROJECTS=ROOT.parent
COLLECTOR=PROJECTS/'greek-ocr-toolkit-sol-collect'
REFERENCE=PROJECTS/'greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading'
SNAPSHOTS=PROJECTS/'collect-v3-data/snapshots'
LIVE=PROJECTS/'collect-v3-data/run'
PACK_ROOT=Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs')
SCANNER='dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547'
SEED='seg-cp7:fresh100'
BEDS=('segcp7_a','segcp7_b')
CONTROL_IDS={'c057','c009','c013','c026','c046','c041','c029','c072','c035','c066'}
PUBLIC_FIELDS={'card_id','crop','google_text','word_scripts'}
# Exactly the registered locked/evaluation classes. Crop rejection classes are
# deliberately eligible; benchmark truth classes are evaluation exclusions.
EVAL_CLASSES={'locked_eval','eval_only_dev','locked_eval_ia_wikisource',
              'locked_eval_ib_wikisource','n1_locked_eval','lqb_truth_v1','lqb_truth_v1_1'}
C1={('bsb_poly1850','poly1850'),('ia_poly1850','poly1850'),('nlg','poly1850'),
    ('nlg','poly1900'),('nlg','greek_poly'),('serbia','cyrillic'),('elstat','numerics_tables')}
QUALIFIED={('kosmopolis','poly1900'),('lekythos','poly1900'),('kosmopolis','poly1850')}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with Path(p).open() as f:return [json.loads(l) for l in f if l.strip()]
def read(p):return json.loads(Path(p).read_text())
def dump(p,obj,exclusive=False):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x' if exclusive else 'w') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
def jsonl(p,items):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(''.join(json.dumps(i,ensure_ascii=False)+'\n' for i in items))
def included(r):
    pair=(r['source'],r['primary_class'])
    return r.get('candidate_usable') is True and (pair in C1 or pair in QUALIFIED or
        r['primary_class']=='headings_caps' or (pair==('gazette_modern','modern_scanned') and
        r.get('gazette_stratum')=='measured_1986_1990'))
def select(pool):
    ordered=sorted(pool,key=lambda r:r['id'])
    if len({r['id'] for r in ordered})!=len(ordered):raise ValueError('duplicate population id')
    return random.Random(SEED).sample(ordered,100)
def population(records,excluded,fresh):
    return [r for r in records if included(r) and r['id'] not in excluded|fresh]
def scripts(text):
    result=[]
    for w in text.split():
        s={next((s for s in ('Greek','Latin','Cyrillic') if s.upper() in unicodedata.name(c,'')),'Other') for c in w if c.isalpha()}
        result.append([w,next(iter(s)) if len(s)==1 else 'Mixed' if s else 'none'])
    return result
def closure(directory,expected_ids):
    directory=Path(directory);cards=rows(directory/'cards.jsonl')
    assert [r['card_id'] for r in cards]==expected_ids and len(cards)==55
    assert len(set(expected_ids))==55
    expected={'cards.jsonl'}
    for c in cards:
        assert set(c)==PUBLIC_FIELDS and re.fullmatch(r'k[0-9a-f]{10}',c['card_id'])
        assert re.fullmatch(r'crops/[0-9a-f]{64}\.png',c['crop'])
        assert sha(directory/c['crop'])==Path(c['crop']).stem
        from PIL import Image
        with Image.open(directory/c['crop']) as im:
            im.load();assert im.format=='PNG' and not im.info
        expected.add(c['crop'])
    actual={str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
    assert actual==expected
    assert all(not p.is_symlink() and (p.is_dir() or p.stat().st_nlink==1) for p in directory.rglob('*'))
    return {p:sha(directory/p) for p in sorted(expected)}


def offline_guard():
    """Fail on network, subprocess, detectors, live-feature reads or live writes."""
    import os
    import greekocr.pages
    from greekocr.glyphs import orientation
    def forbidden(*args,**kwargs):raise AssertionError('CP7: detector/reader/network forbidden')
    greekocr.pages.process_page=forbidden
    orientation._osd=orientation.recognizer_polarity=forbidden
    def audit(event,args):
        if event.startswith('socket.') or event=='subprocess.Popen':forbidden(event)
        if event=='open':
            path,mode,flags=args
            if isinstance(path,int):return
            p=Path(path).resolve()
            if p.is_relative_to(LIVE) and p.name=='features.jsonl':raise AssertionError('CP7 never reads live features')
            if flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
                allowed=p.is_relative_to(HERE) or p.is_relative_to(PACK_ROOT/'segcp7_a') or p.is_relative_to(PACK_ROOT/'segcp7_b') or p in {SEG/'CP7_FREEZE.json',SEG/'CP7_frozen_verification.json'}
                if not allowed:raise AssertionError('CP7 output outside isolated scope: '+str(p))
        if event in ('os.remove','os.rmdir','os.mkdir','os.chmod','os.truncate','os.rename','os.link','os.symlink'):
            paths=args[:2] if event in ('os.rename','os.link','os.symlink') else args[:1]
            for value in paths:
                p=Path(value).resolve()
                # mkdir(parents=True,exist_ok=True) may stat/mkdir existing ancestors.
                if event=='os.mkdir' and p.is_dir():continue
                if not any(p.is_relative_to(root) for root in (HERE,PACK_ROOT/'segcp7_a',PACK_ROOT/'segcp7_b')):raise AssertionError('CP7 mutation outside isolated scope: '+str(p))
    sys.addaudithook(audit)
