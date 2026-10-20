#!/usr/bin/env python3
"""Build the full 100-card NLG final-syllable acute/grave stratum, offline."""
import unicodedata as U
from common_full import *
from PIL import Image
DIPHTHONGS = {'αι','ει','οι','υι','αυ','ευ','ηυ','ου'}
HYPHENS = '-‐‑‒–'

def accent_anchor(token):
    ll = g1.letters(token)
    accented = [(i,c) for i,c in enumerate(ll) if c[0].lower() in 'αεηιουω' and any(a in c for a in '\u0300\u0301\u0342')]
    if not accented: return None
    i,c = accented[-1]
    marks = [a for a in c if a in '\u0300\u0301\u0342']
    if len(marks)!=1 or marks[0] not in '\u0300\u0301': return None
    after = [j for j in range(i+1,len(ll)) if ll[j][0].lower() in 'αεηιουω']
    if after:
        if len(after)!=1 or after[0]!=i+1: return None
        nxt=ll[i+1]
        if c[0].lower()+nxt[0].lower() not in DIPHTHONGS or '\u0308' in nxt: return None
    return i, 'acute' if marks[0]=='\u0301' else 'grave'

def hyphen_fragment(text, wi):
    tokens=text.split(); token=tokens[wi-1]
    # Attached trailing hyphens, or a separate final hyphen following the word.
    return bool(re.search('['+HYPHENS+']+[»”\"\')]*$', token)) or (wi==len(tokens)-1 and tokens[-1] in HYPHENS)

def build():
    s='nlg__poly1900'
    cards=g1.rows(g1.RUN/'c1'/s/'cards.jsonl'); source_key=g1.read(g1.RUN/'c1'/f'{s}_key.json')
    assert len(cards)==100 and len({c['card_id'] for c in cards})==100
    old=g1.read(SR/'grave/keys/key.json')
    overlap={(m['line_id'],m['word_index']):i for i,m in old.items()}
    wanted={source_key[c['card_id']]['line_id'] for c in cards}; features={}
    with g1.bind(g1.RUN/'features.jsonl').open() as f:
        for line in f:
            r=json.loads(line)
            if r['id'] in wanted:
                if r['id'] in features: raise ValueError('Duplicate feature')
                features[r['id']]=r
    dropped=[]; excluded=collections.Counter(); entries=[]; covered=[]
    render_dir=ROOT/'keys/rendered'; render_dir.mkdir(parents=True,exist_ok=True)
    for card in cards:
        cid=card['card_id']; sk=source_key[cid]; text=card['google_text']; line_id=sk['line_id']
        if U.normalize('NFC',text)!=U.normalize('NFC',sk['literal_label']): raise ValueError('Literal label differs')
        covered.append(dict(card_id=cid,line_id=line_id,words=len(text.split())))
        candidates=[]
        for wi,token in enumerate(text.split(),1):
            a=accent_anchor(token)
            if a is None: excluded['not_final_syllable_acute_or_grave']+=1; continue
            i,accent=a
            m=dict(role='bed',stratum=s,card_id=cid,line_id=line_id,word_index=wi,
                   word_labelled=token,label_token=token,printed_word=U.normalize('NFC',''.join(g1.letters(token))),
                   label_accent=accent,anchor_index=i,anchor_base=g1.bare(token)[i],
                   touches_punct=g2.touches_punctuation(text,wi,token),g1_id=overlap.get((line_id,wi)),
                   c1_line_text=text)
            if hyphen_fragment(text,wi):
                dropped.append(dict(m,reason='hyphen_split_fragment')); continue
            if any(c in token for c in HYPHENS):
                dropped.append(dict(m,reason='hyphenated_non_single_word')); continue
            candidates.append(m)
        if not candidates: continue
        reason=None; words=[]; meta=None
        if line_id not in features: reason='missing_source_feature'
        else:
            r=features[line_id]; page=g1.read(g1.RUN/'pages'/f'{r["page_id"]}.json')
            meta=dict(row=r,source_crop=g1.bind(g1.RUN/'c1'/s/card['crop']),response=page['response'],
                      native_size=[page['analysis_page']['width'],page['analysis_page']['height']])
            try: words,reason=g1.geometry.word_geometry(meta,text)
            except (ValueError,KeyError,IndexError) as e: reason='geometry_exception:'+type(e).__name__+':'+str(e)
        for m in candidates:
            why=reason; word=None; anchor=None
            matches=[w for w in words if w['word_index']==m['word_index']]
            if not why:
                if len(matches)!=1: why='word_not_uniquely_aligned'
                else:
                    word=matches[0]
                    ll=[l for l in word['letters'] if any(c.isalpha() for c in l['text'])]
                    if U.normalize('NFC',word['text'])!=U.normalize('NFC',m['label_token']): why='label_word_mismatch'
                    elif len(ll)!=len(g1.letters(m['label_token'])): why='letter_count_mismatch'
                    else:
                        anchor=ll[m['anchor_index']]
                        if anchor['approx_letter_box'] or g1.bare(anchor['text'])!=m['anchor_base']: why='no_exact_anchor_symbol'
            if why:
                dropped.append(dict(m,reason=why)); continue
            with Image.open(meta['source_crop']) as line:
                w,l,wb,lb=g1.render(line.convert('RGB'),word['box'],anchor['box'])
            m['bed_id']=opaque(f'sol-grave-full:bed:{line_id}:{m["word_index"]}')
            m['geometry']=dict(word=word,anchor=anchor,source_crop=str(meta['source_crop']),source_crop_sha256=sha(meta['source_crop']),
                               crop_bbox=meta['row']['crop_bbox'],response=str(meta['response']),native_size=meta['native_size'],
                               render_word_box=wb,render_letter_box=lb,approx_word_box=False,approx_letter_box=False,
                               word_scale=3,letter_scale=8,word_resampling='LANCZOS',letter_resampling='NEAREST')
            p=dict(item_id=m['bed_id'],word_bare=g1.bare(m['label_token']),anchor_index=m['anchor_index'],anchor_base=m['anchor_base'])
            for field,im in [('word_image',w),('letter_image',l)]:
                data=g1.encode(im); rel='img/'+hashlib.sha256(data).hexdigest()+'.png'
                dest=render_dir/rel; dest.parent.mkdir(exist_ok=True); dest.write_bytes(data); p[field]=rel
            entries.append((m,p,render_dir))
    random.Random('sol-grave-full:p1').shuffle(entries)
    pool=control_pool(); key={}; contexts=[]
    for start in range(0,len(entries),90):
        name=f'p1c{start//90+1}'; chunk=entries[start:start+90]
        controls=choose_controls(pool,math.ceil(len(chunk)/9),'sol-grave-full:'+name+':controls')
        all_entries=chunk+control_entries(controls); random.Random('sol-grave-full:'+name+':mix').shuffle(all_entries)
        part,receipt=write_context(name,all_entries); key.update(part); contexts.append(receipt)
    dump(ROOT/'keys/key.json',key)
    for path in (Path(__file__),ROOT/'tools/common_full.py',SR/'grave/tools/build_grave.py',SR/'grave/tools/score_grave.py',SR/'tools/geometry.py',ROOT/'keys/CONTROL_VERIFICATION.json'):
        g1.bind(path)
    for path in sorted((ROOT/'tools').glob('*.py')): g1.bind(path)
    g1.bind(ROOT/'README.md')
    g1.bind(SR/'answers/grave/r1.jsonl')
    g1.bind(PACK_ROOT/'grave/r1/items.jsonl')
    receipt=dict(task='SR-G3',status='built; reader passes pending',cards=100,card_coverage=covered,
                 items=len(entries),candidate_items=len(entries)+len(dropped),dropped=len(dropped),
                 drops_by_reason=dict(collections.Counter(m['reason'] for m in dropped)),drops=dropped,
                 excluded_tokens=dict(excluded),contexts=contexts,controls=sum(c['controls'] for c in contexts),
                 label_accents=dict(collections.Counter(m['label_accent'] for m,_,_ in entries)),
                 overlap_G1=sum(bool(m['g1_id']) for m,_,_ in entries),key_sha256=sha(ROOT/'keys/key.json'),
                 inputs=g1.INPUTS,seeds=dict(p1='sol-grave-full:p1',p2='sol-grave-full:p2'),
                 scope_policy='Last accent-bearing vowel is acute/grave; no later vowel except one adjacent diphthong member (αι ει οι υι αυ ευ ηυ ου), excluding diaeresis. Hyphen fragments excluded. No word-length restriction.',
                 geometry_policy='Imported SR-G1 exact word alignment and exact anchor symbol, no approximations; identical rendering and closure.',
                 controls_policy='Pixel-reviewed G1 Lekythos/Kosmopolis only; copied original RGB PNG bytes; balanced four accent types with fresh IDs.',
                 touches_punct_method=g2.FLAG_METHOD)
    dump(ROOT/'BUILD_RECEIPT.json',receipt)
    print(json.dumps({k:receipt[k] for k in ('items','dropped','drops_by_reason','contexts','controls','overlap_G1')},indent=2))

if __name__=='__main__': build()
