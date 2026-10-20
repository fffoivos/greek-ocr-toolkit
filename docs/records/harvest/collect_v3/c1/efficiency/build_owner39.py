#!/usr/bin/env python3
"""Offline owner39 extension. All source worktrees are read-only; serial build."""
from __future__ import annotations

from collections import Counter
import hashlib
import io
import json
import math
import os
from pathlib import Path
import random
import shutil
import socket
import sys
import time

sys.dont_write_bytecode = True
from PIL import Image
from owner39_common import HEADS, clusters, is_letter, options, skeleton

ROOT = Path(__file__).resolve().parent
PROJECTS = ROOT.parents[5]
EVIDENCE = PROJECTS/'greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/R2_evidence'
R2 = PROJECTS/'greek-ocr-toolkit-spellcheck-r2cards'
BLIND = R2/'docs/labelfix/spellcheck/R2/decks/T2/blind'
RENDERER = R2/'scripts/labelfix/r2_cards_prepare.py'
SPECIAL = '384c3f89-p000059-l0013:s33'
ARMS = ('E0a', 'E0b', 'E2', 'E3')
OLD_IMAGE_SENTENCE = ('Open img/<line_image> (the full native line) whenever mark ownership, a cut, or context is unclear; also\n'
                      'open any paired view images listed (they are repeated views of the same word).')
NEW_IMAGE_SENTENCE = ('Open img/<letter_image> (the 8x NEAREST letter close-up) as well as img/<word_image> (the 3x LANCZOS word crop); '
                      'these are the only images, so you lose the full native line, neighbouring words beyond the word-crop margin, '
                      'and line-wide evidence for mark ownership, cuts and context.')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    path = Path(path)
    assert path.resolve().is_relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def reader_prompt():
    text = (EVIDENCE/'READER_PROTOCOL_R2.md').read_text()
    return text.split('## Reader prompt (verbatim, T4 version, which adds two rules learned on T2)\n\n', 1)[1].split('\n## Resolver', 1)[0].strip()+'\n'


def compact_prompt():
    return '''Blind literal Greek ink reading. Work ONLY in <BATCH_DIR>; open only README.md, answer_schema.json, cards.jsonl and card-named PNGs in img/. Never open/list/search any other file/folder, parents, batches, keys, answers or private files; no web search. Temporary enlargements/helper scripts go only in a new zoom/ subfolder here, nowhere else. Reader 2: cards.jsonl is already assigned in reverse order; ignore README's cards_reverse.jsonl reference.
Read README.md and answer_schema.json first; process cards.jsonl IN GIVEN ORDER. Inspect each word_image, reading the central word; open its full native line_image when ownership, cuts or context are unclear, plus any paired views (same word). Transcribe PRINTED ink, including misprints; never correct spelling or infer a mark from grammar. Options vary one anchor head and usually omit other marks: choose literal and the complete exact word whenever no option is exact. anchor_index counts letters only from 0; give all four anchor heads and letter_heads for every other decidable letter.
Every valued head must match transcription; undecidable ink = unknown, even if transcription supplies an unconfirmed form. ownership_ok = true/false only for a marked anchor (ink belongs here rather than a neighbour line, speck or show-through), null for an unmarked anchor. none requires clearly visible blank area.
Write answers.jsonl here incrementally, exactly one JSON object/card in card order, following answer_schema.json: card_id, choice, transcription when literal, anchor_heads, letter_heads, readability, ownership_ok, confidence, note, usage={"input_tokens":0,"output_tokens":0}. Treat every card alike, including planted checks. Finally verify count/order and report cards answered, literal count, unreadable count, hard cards.
'''


def word_box(meta, size):
    """Saved word-slot union, six native pixels of context, full line height."""
    return (max(0, meta['word_bbox'][0]-6), 0,
            min(size[0], meta['word_bbox'][2]+6), size[1])


def r2_images(line, box):
    """Port of render_deck's RGB/native + integer <=3x LANCZOS block."""
    crop = line.crop(box)
    scale = min(3., 1200/crop.width)
    scale = max(1, min(3, math.floor(scale)))
    zoom = crop.resize((crop.width*scale, crop.height*scale), Image.Resampling.LANCZOS)
    return zoom, line, scale


def e2_images(line, meta):
    """Port of build_r1a_errors.py lines 53-57; no decorated line view."""
    box = word_box(meta, line.size)
    word = line.crop(box)
    word = word.resize((word.width*3, line.height*3), Image.Resampling.LANCZOS)
    x0, _, x1, _ = meta['letter_bbox']
    pad = max(6, (x1-x0)//2)
    letter_box = (max(0, x0-pad), 0, min(line.width, x1+pad), line.height)
    letter = line.crop(letter_box)
    letter = letter.resize((letter.width*8, line.height*8), Image.Resampling.NEAREST)
    return word, letter, box, letter_box


def pixels(directory, image):
    # The R2 leak boundary excludes metadata. PIL's convert/crop can retain an
    # input ICC profile, so discard encoding metadata without altering pixels.
    image.info.clear()
    stream = io.BytesIO(); image.save(stream, format='PNG')
    data = stream.getvalue(); name = hashlib.sha256(data).hexdigest()+'.png'
    (directory/name).write_bytes(data)
    return name


def build():
    started = time.monotonic()
    def deny(*a, **kw):
        raise RuntimeError('E-build2 network OFF')
    socket.create_connection = deny; socket.socket.connect = deny; socket.getaddrinfo = deny
    manifest = json.loads((ROOT/'MANIFEST.json').read_text())
    if any(p['bed']=='owner39' for p in manifest['packs']) or (ROOT/'packs/owner39').exists():
        raise ValueError('owner39 already exists; refuse implicit rebuild')
    sources = [EVIDENCE/'reader_errors_39_owner_final.json', EVIDENCE/'reader_errors_39_card_inputs.json',
               EVIDENCE/'READER_PROTOCOL_R2.md', EVIDENCE/'page_builders/build_r1a_errors.py',
               BLIND/'README.md', BLIND/'answer_schema.json', RENDERER]
    source_hashes = {str(p): sha(p) for p in sources}
    owner = json.loads(sources[0].read_text())
    inputs = json.loads(sources[1].read_text())
    assert len(owner['cards'])==len(inputs)==39
    assert Counter(r['owner_status'] for r in owner['cards'])=={'left_as_shown':38, 'noted':1}
    by_source = {r['db_id']:r for r in inputs}
    assert set(by_source)=={r['db_id'] for r in owner['cards']}
    prompt = reader_prompt(); assert prompt.count(OLD_IMAGE_SENTENCE)==1
    cache = ROOT/'.work/owner39'; cache.mkdir(parents=True)
    truth = {}; public = {}; mappings = {}
    for row in owner['cards']:
        dbid = row['db_id']; meta = by_source[dbid]
        cid = hashlib.sha256(('eff:owner39:card:'+dbid).encode()).hexdigest()[:24]
        anchor = meta['letter_in_word']; base = skeleton(row['google_word'])
        assert base[anchor]==row['base']
        # Options depend only on stripped source base letters, punctuation and
        # a fixed accent head for EVERY card; never select a head from truth.
        opts = options(row['google_word'], anchor, 'accent', 'eff:owner39:options:'+cid)
        heads = dict(breathing='none', accent='none', diaeresis='none', subscript='none')
        for mark in row['truth_marks']:
            if mark in ('psili','dasia'): heads['breathing']=mark
            elif mark in ('acute','grave','circumflex'): heads['accent']=mark
            elif mark in ('dialytika','diaeresis'): heads['diaeresis']='present'
            elif mark=='subscript': heads['subscript']='present'
            else: raise ValueError('Unrecognized owner mark: '+mark)
        scored = list(HEADS)
        if dbid==SPECIAL:
            assert row['owner_status']=='noted'
            heads['accent']='circumflex'; heads['breathing']='unknown'; scored.remove('breathing')
        truth[cid] = dict(card_id=cid, db_id=dbid, anchor_index=anchor, base=row['base'], heads=heads,
                          scored_heads=scored, truth_word=row['truth_word'], owner_status=row['owner_status'],
                          owner_note=row['owner_note'], slot=meta['slot'])
        source = Path(meta['crop']); source_hashes[str(source)]=sha(source)
        with Image.open(source) as im: line=im.convert('RGB')
        zoom, native, scale = r2_images(line, word_box(meta,line.size))
        w2, l2, wb, lb = e2_images(line,meta)
        names = {k:pixels(cache,im) for k,im in [('word',zoom),('line',native),('e2word',w2),('letter',l2)]}
        pub = dict(card_id=cid,word_image=names['word'],line_image=names['line'],anchor_index=anchor,
                   anchor_base=base[anchor],options=opts,
                   extra_options={'literal':'none of these: transcribe the word exactly as printed','unreadable':'unreadable / cut'})
        public[cid]=pub
        mappings[cid]=dict(**meta,source_sha256=sha(source),native_size=list(line.size),word_box=list(wb),
                           letter_box=list(lb),zoom_scale=scale,images=names)
    packs=[]
    for arm in ARMS:
        order=sorted(public); seed=f'eff:owner39:{arm}'; random.Random(seed).shuffle(order)
        assignments={}
        for reader, ids in [('r1',order),('r2',list(reversed(order)))]:
            d=ROOT/'packs/owner39'/arm/reader; (d/'img').mkdir(parents=True)
            items=[]; copies={}
            for cid in ids:
                item=dict(public[cid]); m=mappings[cid]
                if arm=='E2':
                    del item['line_image']; item['word_image']=m['images']['e2word'];item['letter_image']=m['images']['letter']
                items.append(item)
                for field in ('word_image','line_image','letter_image'):
                    if field not in item: continue
                    name=item[field]; dest=d/'img'/name
                    if not dest.exists(): shutil.copyfile(cache/name,dest)
                    copies['img/'+name]={'path':'img/'+name,'sha256':sha(dest),'derived_from_sha256':m['source_sha256']}
            compact=arm=='E3'
            (d/'cards.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':') if compact else None)+'\n' for r in items))
            text=compact_prompt() if compact else prompt.replace(OLD_IMAGE_SENTENCE,NEW_IMAGE_SENTENCE) if arm=='E2' else prompt
            (d/'PROTOCOL.md').write_text(text)
            for name in ('README.md','answer_schema.json'): shutil.copyfile(BLIND/name,d/name)
            packs.append(dict(bed='owner39',arm=arm,reader=reader,path=str(d.relative_to(ROOT)),
                              factor=manifest['arms'][arm],items_file='cards.jsonl',items_per_reader=39,item_ids=ids,
                              files=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(d.rglob('*')) if p.is_file()],
                              copied_crops=list(copies.values()),reads_per_card=2))
            assignments[reader]=ids
        dump(ROOT/f'keys/owner39/{arm}.json',dict(seed=seed,order=order,readers=assignments,
             random_algorithm='random.Random(seed).shuffle(sorted(opaque_card_ids)); r2=reverse(r1)',reads_per_card=2))
    dump(ROOT/'keys/owner39/truth.json',truth)
    dump(ROOT/'keys/owner39/input_mapping.json',mappings)
    dump(ROOT/'keys/owner39/source_hashes.json',source_hashes)
    manifest['packs'].extend(packs);manifest['reader_counts']['owner39']=8
    manifest['owner39']=dict(cards=39,readers=8,arms=list(ARMS),per_item_reads_per_arm=2,
                            excluded_arms={'E1':'smaller than one practice batch','E4':'smaller than one practice batch'},
                            truth='keys/owner39/truth.json',protocol='R2 T4 verbatim for E0a/E0b',
                            renderer='ported render_deck block; input word_bbox x-range +/-6 px at full height',
                            e2_renderer='ported build_r1a_errors.py word and letter blocks',
                            source_hashes='keys/owner39/source_hashes.json',elapsed_build_seconds=time.monotonic()-started)
    # The former global value 1 no longer describes all beds.
    manifest['schema_version']=2
    manifest['per_item_reads_per_arm']={'bsb':1,'yer':1,'owner39':2}
    dump(ROOT/'MANIFEST.json',manifest)
    for name in ('usage','verdicts'):
        path=ROOT/f'keys/{name}.template.json'; template=json.loads(path.read_text())
        for p in packs:
            record={k:p[k] for k in ('bed','arm','reader')}
            if name=='usage': record.update(total_tokens=None,tool_uses=None,duration_ms=None)
            else: record['path']=f'../results/owner39/{p["arm"]}/{p["reader"]}.jsonl'
            template['readers'].append(record)
        dump(path,template)
    assert all(sha(p)==h for p,h in source_hashes.items()), 'Read-only source changed during build'
    shutil.rmtree(cache)
    print(json.dumps(dict(cards=39,readers=8,images=sum(len(p['copied_crops']) for p in packs),nice=os.getpriority(os.PRIO_PROCESS,0),seconds=time.monotonic()-started)))


if __name__=='__main__':
    build()
