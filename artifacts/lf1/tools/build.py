"""Offline LF1 build. Copies/re-encodes crops; does not judge any pixels."""
import collections
import gzip
import io
import json
import random
import unicodedata
from pathlib import Path
from PIL import Image
from lf1 import BASE, PACK_ROOT, SCANNER_SHA, CROP_TABLE, sha, rows, dump, jsonl

PROJECTS = BASE.parents[2]
MAIN = PROJECTS/'greek-ocr-toolkit-main-next'
SOL = PROJECTS/'greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading'
SITE = PROJECTS/'ocr-review-sites-20261018'
SEG = MAIN/'docs/records/harvest/collect_v3_admission/segeval1'
SEED = 20261019
INPUTS = {}

def read(p, zipped=False):
    INPUTS[str(p)] = sha(p)
    return json.loads(gzip.decompress(p.read_bytes()) if zipped else p.read_bytes())

def readrows(p):
    INPUTS[str(p)] = sha(p)
    return rows(p)

def png(im):
    # Re-encoding deliberately removes text, EXIF, ICC, DPI and other metadata.
    if im.mode == 'P':
        im = im.convert('RGBA' if 'transparency' in im.info else 'RGB')
    clean = Image.frombytes(im.mode, im.size, im.tobytes())
    b = io.BytesIO(); clean.save(b, format='PNG'); return b.getvalue()

def native(path, expected):
    assert sha(path) == expected, ('source crop changed', str(path))
    INPUTS[str(path)] = expected
    with Image.open(path) as im:
        return png(im)

QUOTAS = [
    'greek_monotonic_ordinary', 'greek_polytonic_ordinary', 'greek_polytonic_dictionary_journal',
    'latin', 'greek_latin', 'cyrillic_historical_russian', 'cyrillic_modern_languages',
    'numeric_table_cells', 'short_noncell', 'long', 'vertical_turned', 'caps_headings',
    'leaders_dashes_punctuation', 'small_large_fonts', 'degraded_faint_showthrough', 'curved_skewed',
]

def quota_memberships(row, meta, label, content_class):
    """Only directly available plan tags. No primary-class precedence invented.

    Missing genre/language/physical evidence stays missing, not inferred from source.
    These are sampling/report facets, never verdict/selection acceptance criteria.
    """
    tags = []
    script = row['script']
    if script == 'greek_mono': tags.append('greek_monotonic_ordinary')
    if script == 'greek_poly': tags.append('greek_polytonic_ordinary')
    if content_class == 'poly1850' and row['id'].split('--')[0] in ('bsb_poly1850', 'ia_poly1850'):
        tags.append('greek_polytonic_dictionary_journal')
    if script == 'latin': tags.append('latin')
    # The calibration script code alone does not prove mixed-word gate acceptance.
    frame = meta.get('frame', {})
    w, h = frame.get('source_width'), frame.get('source_height')
    is_cell = content_class == 'numerics_tables' and w and h and max(w,h)/min(w,h) <= 6 and sum(c.isalnum() for c in label) > 1
    if is_cell: tags.append('numeric_table_cells')
    if sum(unicodedata.category(c).startswith('L') for c in label) <= 12 and not is_cell:
        tags.append('short_noncell')
    if row['characters'] >= 60: tags.append('long')
    if w and h and h > w and frame.get('normalization_cw') in (90,270): tags.append('vertical_turned')
    if content_class == 'headings_caps': tags.append('caps_headings')
    if content_class == 'leaders_indices': tags.append('leaders_dashes_punctuation')
    return sorted(tags)

def calibration():
    source = SITE/'review-data/box-length-experiment.json'
    report = read(source)['rows']; assert len(report) == 888
    metas = {x['id']: x for x in read(SITE/'review-data/font-normalized/predicted-rows.json.gz', True)}
    pop = read(SITE/'review-data/population.json'); chunks = {}; output = []
    bindings = {x['line_id']: x for x in readrows(MAIN/'docs/records/harvest/seg_steps/s1/crop_bindings.jsonl') if x['cohort']=='calibration'}
    assert len(bindings) == 888
    for r in report:
        m = metas[r['id']]; label = m.get('google_text'); content = m.get('content_class')
        if label is None or content is None:
            n = r['index']//pop['detail_chunk_size']
            if n not in chunks: chunks[n] = read(SITE/f'population-data/details/{n:05d}.json.gz', True)
            detail = chunks[n][r['index']%pop['detail_chunk_size']]
            assert detail[0] == r['id'] and detail[4] == r['image_sha256']
            label = detail[2]
            content = pop['codebooks']['classes'][int(dict(c.split(':') for c in detail[8].split('|'))['class'])]
        assert bindings[r['id']]['sha256'] == r['image_sha256']
        path = SITE/'population-images'/(r['image_sha256']+'.png')
        tags = quota_memberships(r, m, label, content)
        output.append(dict(line_id=r['id'], source=r['id'].split('--')[0], script=r['script'],
                           stored_content_class=content, quota_classes=tags,
                           **{'class': '|'.join(tags) or 'UNASSIGNED'},
                           primary_quota_class=None, class_assignment='available quota facets; primary precedence not specified',
                           label=label, source_crop=str(path), source_sha256=r['image_sha256'],
                           owner_rating=r['owner_rating'], parent='accepted-calibration-888'))
    assert sum(bool(r['owner_rating']) for r in output) == 135
    return output

def stratified(rated, count=100):
    # Proportional allocation by quota-facet signature, largest remainder; no acceptance logic.
    groups = collections.defaultdict(list)
    for r in sorted(rated, key=lambda r:r['line_id']): groups[r['class']].append(r)
    allocation = {c:len(g)*count//len(rated) for c,g in groups.items()}
    remainder = count - sum(allocation.values())
    order = sorted(groups, key=lambda c:(-(len(groups[c])*count % len(rated)), c))
    for c in order[:remainder]: allocation[c] += 1
    rng = random.Random(SEED); result = []
    for c in sorted(groups):
        rng.shuffle(groups[c]); result += groups[c][:allocation[c]]
    rng.shuffle(result)
    return result, allocation

def controls(calibration_ids):
    """Freeze constructed controls from a saved clean SEGEVAL line; lead reviews pixels.

    Construction is explicit, not a new model reading or a claim of owner truth.
    Pool is sealed before pack order/opaque ids are generated.
    """
    old = readrows(SEG/'scored/owner_rows.jsonl')
    rid = 'ia_poly1850--df8f2267db2b7275--s004-l0022'
    base = next(x for x in old if x['line_id'] == rid)
    assert rid not in calibration_ids
    sealed = {x['row_id']:x for x in readrows(SEG/'keys/sealed_decisions.jsonl')}
    path = SEG/'crops'/(rid+'.png')
    if not path.exists():
        path = PROJECTS/'greek-ocr-toolkit-segcensus/docs/harvest/collect_v3_admission/segeval1/crops'/(rid+'.png')
    data = native(path, sealed[rid]['crop_sha256'])
    im = Image.open(io.BytesIO(data)); w,h = im.size; label=base['google_text']
    two = Image.new(im.mode, (w, h*2), 'white'); two.paste(im,(0,0));two.paste(im,(0,h))
    # Two equally placed complete lines: no unique central target, extra full line,
    # and >2 fully visible neighbour words (stored line has >2 words).
    assert len(label.split()) > 2
    cases = [
        ('ok', im, label, dict(verdict='OK'), 'unchanged saved clean line'),
        ('multiline', two, label, dict(verdict='CROP_VIOLATES', reasons=['one_central_line','other_complete_line','gt2_whole_neighbour_words']), 'two full copies appended vertically'),
        ('omitted_span', im, label.rsplit(' ',1)[0], dict(verdict='CROP_VIOLATES', reasons=['text_ne_visible_line']), 'label omits final stored word; pixels unchanged'),
        ('turned', im.transpose(Image.Transpose.ROTATE_90), label, dict(verdict='CROP_VIOLATES', reasons=['turned_or_clipped']), 'native line turned 90 degrees'),
        ('clipped', im.crop((0,h//2,w,h)), label, dict(verdict='CROP_VIOLATES', reasons=['turned_or_clipped']), 'upper half removed through target glyphs'),
        ('textdiff', im, 'X'+label[1:], dict(verdict='TEXT_DIFFERS'), 'first label base letter replaced with X; pixels unchanged'),
    ]
    pooldir = PACK_ROOT/'control_pool'/'img'; pooldir.mkdir(parents=True,exist_ok=True)
    pool = []
    import hashlib
    for name, image, text, expected, construction in cases:
        blob = png(image); digest=hashlib.sha256(blob).hexdigest(); dest=pooldir/(digest+'.png')
        if dest.exists(): assert dest.read_bytes() == blob
        else: dest.write_bytes(blob)
        pool.append(dict(pool_id='lf1-control-'+name, crop=str(dest), sha256=digest,label=text,
                         expected=expected, construction=construction, source_line_id=rid,
                         source_crop_sha256=sealed[rid]['crop_sha256'],
                         evidence=base['reader_answer'], pixel_review='PENDING lead; no LF1 reader run'))
    poolfile = BASE/'keys/control_pool.json'
    if poolfile.exists(): assert json.loads(poolfile.read_text()) == pool, 'frozen pool changed'
    else: dump(poolfile, pool)
    return pool

def word_scripts(label):
    out=[]
    for word in label.split():
        scripts=set()
        for ch in word:
            if not unicodedata.category(ch).startswith('L'):continue
            name=unicodedata.name(ch,'')
            scripts.add(next((s for s in ('Greek','Latin','Cyrillic','Hebrew') if s.upper() in name),'Other'))
        out.append([word, next(iter(scripts)) if len(scripts)==1 else 'Mixed' if scripts else 'none'])
    return out

def pack(name, bed, pool, exact_bytes=False):
    import hashlib
    directory=PACK_ROOT/('candidates' if name.startswith('candidate') else 'dryrun')/name
    if directory.exists(): raise FileExistsError('refuse to overwrite an existing context: '+str(directory))
    (directory/'img').mkdir(parents=True)
    cards=[]; private={}; originals={}
    values=[(False,x) for x in bed]+[(True,x) for x in pool]
    rng=random.Random(f'{SEED}:{name}');rng.shuffle(values)
    for is_control, row in values:
        card_id='k'+format(rng.getrandbits(40),'010x')
        assert card_id not in private
        if is_control:
            blob=Path(row['crop']).read_bytes()
        elif exact_bytes:
            assert sha(row['source_crop'])==row['source_sha256'], 'source crop changed'
            blob=Path(row['source_crop']).read_bytes()
        else:
            blob=native(Path(row['source_crop']),row['source_sha256'])
        digest=hashlib.sha256(blob).hexdigest();rel='img/'+digest+'.png'
        (directory/rel).write_bytes(blob)
        cards.append(dict(card_id=card_id,crop=rel,google_text=row['label'],word_scripts=word_scripts(row['label'])))
        private[card_id]=dict(row,control=is_control,pack_crop_sha256=digest)
    jsonl(directory/'items.jsonl',cards)
    for p in directory.rglob('*'):
        if p.is_file():originals[str(p.relative_to(directory))]=sha(p)
    manifest=directory.parent/f'MANIFEST.{name}.json';dump(manifest,dict(files=originals))
    key=BASE/'keys'/(name+'.json');dump(key,dict(items=private))
    return dict(name=name,directory=str(directory),key=str(key),key_sha256=sha(key),
                manifest=str(manifest),manifest_sha256=sha(manifest),bed=len(bed),controls=len(pool),cards=len(cards))

def prompt():
    source=(BASE/'prompts/source_bsb.md').read_text()
    body=source[source.index('You are a blind label checker'):source.index('# Done when')]
    # Body unchanged, including its cards.jsonl alias and original stricter crop_ok.
    header=source[:source.index('# Environment')]
    environment='''# Environment
- Your working folder holds only items.jsonl and img/ before reading.
- CARDS means ./items.jsonl, OUT means ./answers.jsonl, ZOOM means ./zoom/; cards.jsonl in the preserved protocol is an alias for items.jsonl, not another file to create.
- See every crop with view_image. Use literal relative paths only in every view_image call; write each call explicitly, with no path loops or computed paths. Batch about 5 to 10 explicit calls per tool call.
- ImageMagick (magick) is installed. Write every zoom once under a new name in zoom/; use only -filter point, -resize, montage/append. No -rotate, no font paths.
- Create only answers.jsonl and zoom/**. Write answers with shell commands. No network or web search.
- Input clarification: one stored label word has Hebrew letters; its word_scripts entry is Hebrew. The label is unchanged.

# Protocol
The following qualified protocol body is preserved verbatim. Resolve its CARDS/OUT/ZOOM and cards.jsonl aliases using Environment above.

'''
    addition='''# LF1 owner questions (independent of the historical crop_ok)
Keep all protocol answer fields, but ignore marks for LF1 decisions. Historical crop_ok is evidence only because it is stricter about neighbour ink than the owner standard.
Answer every following question in owner_crop using yes, no, or uncertain. A yes records the named fault, not a replacement label.

## one_central_line
Owner wording: "there is exactly one central line of text".
Question: Does the crop violate this requirement?

## text_ne_visible_line
Owner wording: "the label matches the visible line exactly, neither more nor less (text running past the crop, omitted visible spans, letters cut through, merged lines = fault)".
Question: Does the crop violate this extent/segmentation requirement? Record character substitutions separately in letters/errors/where.

## other_complete_line
Owner wording: "no other line shows completely".
Question: Does another line show completely?

## gt2_whole_neighbour_words
Owner wording: "other lines show at most 2 WHOLE words (100% visible); cut neighbour words and partial letter bodies are allowed".
Question: Do other lines show more than 2 WHOLE words (100% visible)?

## turned_or_clipped
Owner wording: "Turned (rotated) or clipped crops fail."
Question: Is this crop turned (rotated) or clipped?

For a base-letter/digit/script/punctuation/hyphen text difference, add where as a list of {"label": "literal differing label substring", "printed": "what is printed"}. Use an empty string for an insertion/deletion side. Otherwise where is []. Do not use the marks field to decide a verdict.
You may add reading as evidence only; it never replaces google_text and never decides the verdict by itself.
Use segmentation_detail for crop evidence. Do not infer a crop fault solely from a character substitution.

'''
    done='''# Done when
- answers.jsonl has exactly one valid JSON line per items.jsonl card, in the same order, with all preserved protocol fields and owner_crop/where.
- You have checked count and order once with a command.
- Reply with the protocol's short plain-text summary.
'''
    result=header+environment+body+addition+done
    assert body in result
    (BASE/'prompts/lf1.md').write_text(result)
    # Exhaustive line-level provenance, including blank lines, for every changed/added wrapper/addendum line.
    sources={
        'Environment': 'LF1 user brief: Pack and run rules; HANDOVER sections 2-5; CONTEXT spellcheck scanner no path loops',
        'LF1': 'LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4',
        'Done': 'bsb.md GPT-6 wrapper / GUIDE_NOTES.md; LF1 items.jsonl field additions',
        'Protocol': 'bsb.md / GUIDE_NOTES.md verbatim protocol and alias wrapper',
    }
    changes=[];section='Environment'
    for number,line in enumerate(result.splitlines(),1):
        if line=='# LF1 owner questions (independent of the historical crop_ok)':section='LF1'
        if line=='# Done when':section='Done'
        if line=='# Protocol':section='Protocol'
        if line and line not in source.splitlines():changes.append(dict(line=number,text=line,source=sources[section]))
    for change in changes:
        if change['text'].startswith('- Input clarification:'):
            change['source']='bsb Unicode-script input definition; frozen selected label Unicode names (HEBREW LETTER YOD / FINAL NUN); LF1 stored-label rule'
    dump(BASE/'receipts/prompt_lines_added.json',changes)
    dump(BASE/'receipts/prompt_receipt.json',dict(source_sha256=sha(BASE/'prompts/source_bsb.md'),
         prompt_sha256=sha(BASE/'prompts/lf1.md'),protocol_body_sha256=__import__('hashlib').sha256(body.encode()).hexdigest(),
         protocol_body_verbatim=True,guide_sha256=sha(BASE/'prompts/GUIDE_NOTES.md')))

def main():
    assert sha(BASE/'tools/scan_rollout.py') == SCANNER_SHA
    for p in [SOL/'HANDOVER.md',SOL/'GUIDE_NOTES.md',SOL/'prompts/bsb.md',
              MAIN/'docs/programme_20261019/NIGHT_PLAN.md',
              MAIN/'docs/cleanup_20261019/POST_CLEANUP_PROGRAMME.md',
              MAIN/'docs/B_training_data/b_tools/SEGMENTATION_FILTER.md',
              SEG/'prompts/owner_rubric.md',BASE.parents[1]/'docs/CONTEXT_20261019_spellcheck.md']:
        INPUTS[str(p)]=sha(p)
    data=calibration();rated=[x for x in data if x['owner_rating']]
    selected,allocation=stratified(rated)
    assert len(selected)==100 and len({x['line_id'] for x in selected})==100
    pool=controls({x['line_id'] for x in data});prompt()
    contexts=[pack(f'ctx{i+1:02d}',selected[i*50:(i+1)*50],pool) for i in range(2)]
    dump(BASE/'contexts.json',contexts)
    jsonl(BASE/'keys/selected.jsonl',selected)
    jsonl(BASE/'keys/owner_rating_truth.jsonl',[dict(line_id=x['line_id'],owner_rating=x['owner_rating'],expected='OK' if x['owner_rating']['decision']=='KEEP' else 'not OK',quota_classes=x['quota_classes'],**{'class':x['class']}) for x in selected])
    dump(BASE/'keys/quota_scheme.json',dict(source='docs/cleanup_20261019/POST_CLEANUP_PROGRAMME.md section 3.2',
        classes=QUOTAS,primary_precedence='not specified; no primary assignments invented',
        dryrun_stratification='available quota facet signature; UNASSIGNED where none can be bound',
        missing_evidence=['mixed-word gate legitimacy','Cyrillic document language/orthography','degradation thresholds','font/baseline tags not in compact calibration record']))
    dump(BASE/'receipts/build.json',dict(seed=SEED,inputs=INPUTS,scanner_sha256=SCANNER_SHA,
         scanner_dependencies={f:sha(BASE/'tools'/f) for f in ['common.py','replay_literal.py']},
         calibration=888,rated_population=135,selected=100,owner_rated_selected=100,
         allocation=allocation,contexts=contexts,control_pool_sha256=sha(BASE/'keys/control_pool.json'),
         control_pixel_review='PENDING lead',reader_runs=0,network='OFF',git_writes=False))
    print(json.dumps(dict(contexts=[c['cards'] for c in contexts],controls=sum(c['controls'] for c in contexts),owner_rated=100)))

if __name__=='__main__':main()
