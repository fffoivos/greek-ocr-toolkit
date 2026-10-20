#!/usr/bin/env python3
"""Inventory pool characters/NFD atoms against the Rust v1 source of record."""
import argparse
import json
import re
import unicodedata as ud
from collections import Counter,defaultdict
from pathlib import Path
from greekocr._vendor.bench.common import ROOT, read_rows, sha256, write_json, script


def rust_string(raw):
    raw=re.sub(r'\\u\{([0-9a-fA-F]+)\}',lambda m:chr(int(m[1],16)),raw)
    return json.loads('"'+raw+'"')


def load_v1(path=ROOT/'factory/src/codec.rs'):
    source=Path(path).read_text();atoms=set(' 0123456789')
    for name in ('GREEK_BASES','LATIN_BASES','CYRILLIC_BASES','PUNCT','SYMS'):
        match=re.search(r'const '+name+r': &str = "((?:\\.|[^"\\])*)";',source)
        if not match:raise ValueError('codec source changed: missing '+name)
        atoms.update(rust_string(match[1]))
    marks=re.search(r'const MARKS: &\[char\] = &\[(.*?)\];',source,re.S)[1]
    atoms.update(chr(int(h,16)) for h in re.findall(r"'\\u\{([0-9a-fA-F]+)\}'",marks))
    # Read the actual Rust fold match arms instead of a second inventory/normalization table.
    block=re.search(r'let c = match c \{(.*?)other => other,',source,re.S)[1]
    folds={}
    for line in block.splitlines():
        if '=>' not in line:continue
        left,right=line.split('=>',1)
        src=re.findall(r"'\\u\{([0-9a-fA-F]+)\}'",left)
        dest=re.search(r"'\\u\{([0-9a-fA-F]+)\}'",right)
        if not src or not (dest or 'continue' in right):raise ValueError('unparsed Rust codec fold')
        for h in src:folds[chr(int(h,16))]=chr(int(dest[1],16)) if dest else ''
    return atoms,folds


def normalize_v1(text,folds):
    return ' '.join(''.join(folds.get(c,c) for c in ud.normalize('NFD',text)).split())


def inventory(rows,atoms,folds):
    chars=Counter();nfd=Counter();groups=defaultdict(Counter);strict_bad=fold_bad=0
    for r in rows:
        text=r['text'];chars.update(text);expanded=ud.normalize('NFD',text);nfd.update(expanded)
        strict_bad+=any(c not in atoms for c in ' '.join(expanded.split()))
        fold_bad+=any(c not in atoms for c in normalize_v1(text,folds))
        group='other'
        for c in expanded:
            sc=script(c)
            if sc:group={'greek':'Greek polytonic','latin':'Latin marks','cyrillic':'Cyrillic'}.get(sc,'other')
            if c not in atoms:groups[group][c]+=1
    def table(counter):
        return [dict(cp=f'U+{ord(c):04X}',character=c,name=ud.name(c,'UNNAMED'),count=n,
                    atomic_in_v1=c in atoms,encodable_nfd=all(x in atoms for x in ud.normalize('NFD',c)))
                for c,n in sorted(counter.items(),key=lambda x:ord(x[0]))]
    return dict(lines=len(rows),strict_nfd_rejected_lines=strict_bad,v1_normalized_rejected_lines=fold_bad,
                precomposed_characters=table(chars),nfd_atoms=table(nfd),
                missing_by_language_group={g:table(c) for g,c in groups.items()})


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('pools',type=Path);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--codec-source',type=Path,default=ROOT/'factory/src/codec.rs');a=ap.parse_args()
    atoms,folds=load_v1(a.codec_source);rows={};supplies={};bystratum={}
    for p in sorted(a.pools.glob('*.jsonl')):
        rs=list(read_rows(p));bystratum[p.stem]=inventory(rs,atoms,folds)
        for r in rs:(supplies if '.supply.' in p.name else rows).setdefault(r['id'],r)
    probes={'Greek polytonic':'ᾧἅΐΰϲ', 'Latin marks':'ėőșąłøðþđıŀŋ',
            'Cyrillic incl Serbian Macedonian':'ЂђЈјЉљЊњЋћЏџЅѕЃѓЌќЇїЁёй'}
    probe_rows={g:inventory([{'text':t}],atoms,folds) for g,t in probes.items()}
    report=dict(codec_source=str(a.codec_source),codec_source_sha256=sha256(a.codec_source),codec_version='v1',
                atom_count=len(atoms),pools=inventory(list(rows.values()),atoms,folds),
                sparse_supply_diagnostic=inventory(list(supplies.values()),atoms,folds),per_stratum=bystratum,
                target_probes_not_corpus_counts=probe_rows)
    write_json(a.out,report)
    md=['| Group | Raw NFD atoms absent (capped pools) | Probe raw atoms absent (before v1 folds; not corpus) |','|---|---|---|']
    for g,p in probe_rows.items():
        key='Cyrillic' if g.startswith('Cyrillic') else g
        observed=report['pools']['missing_by_language_group'].get(key,[])
        probed=[c for cs in p['missing_by_language_group'].values() for c in cs]
        fmt=lambda xs:', '.join(c['cp']+' '+c['character'] for c in xs) or 'none'
        md.append(f'| {g} | {fmt(observed)} | {fmt(probed)} |')
    a.out.with_suffix('.md').write_text('\n'.join(md)+'\n')
    print('unique capped pool lines',len(rows),'v1-rejected',report['pools']['v1_normalized_rejected_lines'])

if __name__=='__main__':main()
