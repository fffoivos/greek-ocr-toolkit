"""Printed-line alignment, with explicit source and cached-reader ownership.

Matching projections are disposable coordinates: labels always use the source's
literal NFD atoms, including U+0223. No codec fold is applied to a label.
"""
from collections import Counter
from difflib import SequenceMatcher
import re
import unicodedata as ud

HYPHENS = '-‐‑'
EDGES = '-‐‑–—\'"‘’‚‛“”„«»‹›ʼ᾽᾿'


def normal(s):
    return ' '.join(ud.normalize('NFD', s).split())


def wordchar(c):
    return c not in EDGES and (c.isalpha() or ud.category(c).startswith('M'))


def projection(s):
    positions = [i for i, c in enumerate(s) if wordchar(c) or c.isdigit()]
    return ''.join(s[i] for i in positions), positions


def repair_tei_node(text):
    """Only the three adjudicated name families; other ?? remain unresolved.

    The pinned upstream TEI itself is damaged. Never claim these substitutions
    were literal TEI glyphs. Each output atom keeps its raw node interval.
    """
    raw = ud.normalize('NFD', text or '')
    pattern = re.compile(r'(?:(?<=Σε)|(?<=Ῥα)|(?<=Ἀδ))̔\?\?ʼ')
    out = []; mapping = []; changes = []; cursor = 0
    for m in pattern.finditer(raw):
        out.extend(raw[cursor:m.start()]); mapping.extend((i, i+1, None) for i in range(cursor, m.start()))
        change = dict(rule='adjudicated_ou_ligature', raw=raw[m.start():m.end()], emitted='ȣ', start=m.start(), end=m.end())
        changes.append(change); out.append('ȣ'); mapping.append((m.start(), m.end(), change)); cursor = m.end()
    out.extend(raw[cursor:]); mapping.extend((i, i+1, None) for i in range(cursor, len(raw)))
    return ''.join(out), mapping, changes


def token_text(document, token):
    return ''.join(document['text'][int(s.get('startIndex', 0)):int(s['endIndex'])]
                   for s in token['layout'].get('textAnchor', {}).get('textSegments', []))


def token_bbox(token, width, height):
    poly = token['layout']['boundingPoly']
    if poly.get('normalizedVertices'):
        vs = [(v.get('x', 0)*width, v.get('y', 0)*height) for v in poly['normalizedVertices']]
    else:
        vs = [(v.get('x', 0), v.get('y', 0)) for v in poly.get('vertices', [])]
    return [min(v[0] for v in vs), min(v[1] for v in vs), max(v[0] for v in vs), max(v[1] for v in vs)]


def margin_numerals(line, tokens):
    """Conservatively withhold a crop containing a separate narrow edge numeral.

    The text block for this row is the union of letter-bearing token extents.
    This also catches a numeral recognized as a different provider line but
    physically included in the current crop. Internal prose numerals stay.
    No pixels or G1b results are changed by this rule.
    """
    box = line.get('crop_bbox', line['bbox']); xh = line.get('row_xheight') or (box[3]-box[1])*.5
    inside = []
    for t in tokens:
        b = t['bbox']; overlap = max(0, min(b[3], box[3])-max(b[1], box[1]))
        if overlap < .55*max(1, b[3]-b[1]): continue
        if min(b[2], box[2])-max(b[0], box[0]) < .8*max(1, b[2]-b[0]): continue
        inside.append(t)
    letters = [t['bbox'] for t in inside if any(c.isalpha() for c in t['text'])]
    if not letters: return []
    left = min(b[0] for b in letters); right = max(b[2] for b in letters)
    result = []
    for t in inside:
        b = t['bbox']; s = t['text'].strip()
        if not re.fullmatch(r'\d{1,2}', s): continue
        gap = max(left-b[2], b[0]-right)
        if gap >= .6*xh and b[2]-b[0] <= 2.8*xh:
            result.append(dict(text=s, bbox=b, text_extent=[left, right], separation_px=gap,
                               row_xheight=xh, evidence='separate narrow numeric token outside row text extent'))
    return result


def clean_query(line, pilot):
    query = normal(line['docai_raw_text'])
    if pilot == 'perseus':
        # Alignment ignores apparatus; crop contamination remains a release veto.
        query = re.sub(r'^\d{1,2}\s+(?=\D)', '', query)
        query = re.sub(r'\s+\d{1,2}$', '', query)
    return query.strip()


def align_page(page, lines, proof, ownership, inventory, script_class):
    source = proof['text']; sp, smap = projection(source)
    queries = [clean_query(r, page['pilot']) for r in lines]
    qpairs = [projection(q) for q in queries]; joined = ''.join(q[0] for q in qpairs)
    mapping = {}
    for tag, a, b, c, d in SequenceMatcher(None, joined, sp, autojunk=False).get_opcodes():
        if tag == 'equal': mapping.update((a+i, c+i) for i in range(b-a))
    verified = True
    if page['pilot'] in ('perseus', 'gutenberg'):
        verified = any(re.search(r'(?<!\d)'+re.escape(page['printed_page'])+r'(?!\d)', r['text'])
                       for r in lines if r['bbox'][1] < page['height']*.16)
    output = []; claimed = []; cursor = 0; previous = None
    for r, query, (qproj, qmap) in zip(lines, queries, qpairs):
        a = cursor; b = a+len(qproj); cursor = b
        hits = [(i-a, mapping[i]) for i in range(a, b) if i in mapping]
        reasons = []; flags = []; start = end = None; candidate = None; owners = None
        edge = []; corrections = []; diff = []; score = None; segments = []; inside_start = inside_end = False
        if not hits: reasons.append('no_source_span')
        else:
            # Project the unmatched edge atoms, bounded to the same source word.
            first, last = hits[0], hits[-1]
            ps = max(0, first[1]-first[0]); pe = min(len(sp), last[1]+len(qproj)-last[0])
            start = smap[ps]; end = smap[pe-1]+1
            # Never borrow a neighbouring word just to account for an OCR error.
            wstart = start
            while wstart > 0 and wordchar(source[wstart-1]): wstart -= 1
            wend = end
            while wend < len(source) and wordchar(source[wend]): wend += 1
            # Whole first/last proofread words unless there is printed split evidence.
            firstword = query[qmap[0]:].split()[0].strip(EDGES+',.;:!?') if qmap else ''
            lastword = query[:qmap[-1]+1].split()[-1].strip(EDGES+',.;:!?') if qmap else ''
            printed_split = bool(query.rstrip(EDGES.replace('-', '').replace('‐', '').replace('‑', '')+' ').endswith(tuple(HYPHENS)))
            prev_split = previous and previous['query'].endswith(tuple(HYPHENS)) and abs(previous['end']-start)<=2
            if prev_split and previous['end'] < len(source) and wordchar(source[previous['end']]):
                start=previous['end']; wstart=start
                while wstart>0 and wordchar(source[wstart-1]): wstart-=1
            page_carry = start < proof.get('body_start', 0) and not claimed
            suffix = source[start:end].split()[0] if start < end else ''
            continuation = bool((prev_split or page_carry) and firstword and SequenceMatcher(None, normal(suffix).strip(',.;:!?'), firstword.strip(',.;:!?'), autojunk=False).ratio()>=.7)
            if wstart < start and not continuation:
                if source[wstart:end].split()[0].endswith(firstword) and firstword:
                    reasons.append('starts_inside_proofread_word_without_carry')
                start = wstart
            inside_start = wstart < start
            if not printed_split:
                partial = source[start:end].split()[-1] if start < end else ''
                if wend > end and partial == lastword: reasons.append('ends_inside_proofread_word_without_printed_edge')
                end = wend
            inside_end = end < len(source) and wordchar(source[end])
            if inside_end and not printed_split: reasons.append('ends_inside_proofread_word_without_printed_edge')
            body = source[start:end].strip(); start += len(source[start:end])-len(source[start:end].lstrip()); end = start+len(body)
            prefix = query[:qmap[0]] if qmap else ''; suffix = query[qmap[-1]+1:] if qmap else ''
            # Proofread punctuation remains literal, except adjudicated printed ano teleia.
            body_chars = list(body)
            for tag, i, j, k, l in SequenceMatcher(None, query, body, autojunk=False).get_opcodes():
                if tag == 'replace' and ((query[i:j] == '·' and body[k:l] == ':') or (query[i:j] in EDGES and body[k:l]=='̓' and k>0 and body[k-1] not in 'αεηιουωΑΕΗΙΟΥΩ')):
                    body_chars[k] = query[i:j]; corrections.append(dict(rule='printed_ano_teleia' if query[i:j]=='·' else 'printed_elision_apostrophe', source_nfd=[start+k, start+l], raw=body[k:l], emitted=query[i:j], google_nfd=[i,j]))
            body = ''.join(body_chars)
            candidate = prefix+body+suffix
            for side, glyphs, interval in [('left', prefix, [0, qmap[0]]), ('right', suffix, [qmap[-1]+1, len(query)])]:
                if glyphs:
                    edge.append(dict(side=side, text=glyphs, query_nfd=interval, origin='cached_page_read', docai_text_anchors=r.get('docai_text_anchors')))
            owners, failure = ownership(proof, start, end, source[start:end])
            if failure: reasons.append(failure)
            segments = [dict(origin='cached_page_read', text=prefix), dict(origin='proofread', text=body, source_span_nfd=[start,end]), dict(origin='cached_page_read', text=suffix)]
            local = SequenceMatcher(None, query, candidate, autojunk=False); score = local.ratio()
            diff = [dict(op=t, google=[i,j], proof=[k,l], google_text=query[i:j], label_text=candidate[k:l]) for t,i,j,k,l in local.get_opcodes() if t != 'equal']
            if score < .92: reasons.append('alignment_similarity_below_0.92')
            # Count matching letters; punctuation is accounted for by reader ownership.
            support = SequenceMatcher(None, qproj, projection(candidate)[0], autojunk=False)
            if sum(m.size for m in support.get_matching_blocks())/max(1,len(qproj)) < .9: reasons.append('matched_atom_coverage_below_0.90')
            if len(candidate) < 6 or sum(c.isalpha() for c in candidate) < 3: reasons.append('span_too_short')
            if re.search(r'⟦|⟧|\?\?', candidate): reasons.append('editorial_or_unresolved_source_region')
            if source.count(source[start:end]) != 1: reasons.append('repeated_source_span')
            if any(max(start,x)<min(end,y) for x,y in claimed): reasons.append('duplicate_span_ownership')
            if inside_start: flags.append('carried_word_fragment')
            if page_carry: flags.append('cross_page_tei_fragment')
            if 'ȣ' in candidate: flags.append('codec_v2_ou_ligature')
            if page['pilot']=='wikisource':
                letter_diff=any(any(wordchar(c) for c in e['google_text']+e['label_text']) for e in diff)
                # A page-final expanded word followed by its literal printed prefix
                # (e.g. ἐδύναντο ἐδύ-) is a source/read disagreement even when
                # alignment can correctly own just the printed prefix.
                remaining=source[end:]
                duplicated_prefix=bool(printed_split and lastword and re.match(r'[^ ]* '+re.escape(lastword)+r'[-‐‑]',remaining))
                if letter_diff or duplicated_prefix: flags.append('disagrees_with_page_read')
                if duplicated_prefix: flags.append('expanded_hyphenation_disagreement')
        margin = r.get('margin_numerals', [])
        if margin: reasons.append('margin_numeral_in_crop'); flags.append('margin_numeral_in_crop')
        # OCR edge numerals without sufficient geometric evidence abstain as unresolved.
        if page['pilot']=='perseus' and clean_query(r,'perseus') != normal(r['docai_raw_text']) and not margin:
            reasons.append('edge_numeral_geometry_unresolved')
        if not verified: reasons.append('printed_page_header_not_verified')
        if r['geometry_positive'] is not False: reasons.append('geometry_positive_or_unresolved')
        reasons = list(dict.fromkeys(reasons)); accepted = not reasons
        if accepted: claimed.append((start,end))
        if candidate: previous = dict(query=query, end=end)
        inv = inventory(ud.normalize('NFC', candidate or '')); greek = inv['greek_letters'] > 0
        output.append(dict(id=r['id'], page_id=page['id'], pilot=page['pilot'], item=page['item'], accepted=accepted,
            accepted_for_target_reference=accepted and greek, human_script_class=script_class(candidate,inv) if inv['letter_count'] else 'nonletter',
            human_mixed_line=greek and bool(inv['latin_words']), target_rejection_reasons=reasons+([] if greek else ['outside_Greek_bearing_target']),
            release_status='proposal_only_pending_second_blind_pixel_adjudication', human_label=ud.normalize('NFC',candidate) if accepted else None,
            candidate_text=ud.normalize('NFC',candidate) if candidate else None, google_text=r['text'], alignment_query=ud.normalize('NFC',query),
            source_span_nfd=[start,end] if start is not None else None, literal_source_ownership=owners, edge_glyph_ownership=edge,
            label_segments=segments, printed_corrections=corrections, flags=flags, disagrees_with_page_read='disagrees_with_page_read' in flags,
            margin_numerals=margin, reasons=reasons, similarity=score, alignment_edits=diff, crop_path=r['crop_path'], crop_sha256=r['crop_sha256'],
            bbox=r['bbox'], geometry_positive=r['geometry_positive'], text_revision=page['text_revision'], text_sha256=page['text_sha256'],
            page_image_sha256=page['image_sha256'], proofreading_status=proof['status'], script_class=r['script_class'], mixed_line=r['mixed_line'], line_tags=r['line_tags']))
    return output, dict(page_id=page['id'], pilot=page['pilot'], item=page['item'], page=page['page'], read=True,
        google_lines=len(lines), google_nfd_characters=sum(len(normal(r['docai_raw_text'])) for r in lines),
        proofread_nfd_characters=proof.get('body_nfd_characters',len(source)), retained_lines=sum(r['accepted'] for r in output),
        retained_nfd_characters=sum(e-s for s,e in claimed), rejected_lines=sum(not r['accepted'] for r in output),
        rejection_reasons=dict(Counter(x for r in output for x in r['reasons'])), printed_page_verified=verified,
        transformations=proof['transformations'])
