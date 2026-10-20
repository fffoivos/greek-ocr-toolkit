"""Unique-slot overlays on frozen extraction. Unknown tuples are quarantined whole."""
from collections import Counter, defaultdict
from pathlib import Path
import json
import math
import numpy as np
from scripts.labelfix.clariden.r1_common import HEADS, rows, sha256, verify_receipt

PROVENANCE = ('old', 'native_print', 'pseudo', 'override')


def identity(value):
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError('slot_id must be [crop sha256, recogniser NFD start]')
    digest, start = value
    if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest) or not isinstance(start, int) or start < 0:
        raise ValueError('invalid slot identity')
    return digest, start


def inventory_ids(dataset, inventory):
    crops = {r['crop']: r['sha256'] for r in rows(inventory)}
    lines = {r['line']: r for r in rows(dataset.path/'lines.jsonl.gz')}
    meta = []
    for r in dataset.index:
        line = lines[int(r['line'])]
        meta.append(dict(slot_id=[crops[line['crop']], int(r['start'])], line_id=line['id'],
                         doc=line['doc'], source=line.get('source', line['doc'].split(':')[0]), crop=line['crop'], line=int(r['line'])))
    return meta


class ManifestPool:
    """Keep old order; replace in place; new identities append exactly once."""
    def __init__(self, old, manifest, inventory, extra_factory=None, native_pool=None):
        self.path=old.path; self.arm=old.arm
        meta=inventory_ids(old, inventory)
        keys=[identity(m['slot_id']) for m in meta]
        self.old_indices=defaultdict(list)
        for i,k in enumerate(keys): self.old_indices[k].append(i)
        duplicate_classes=Counter()
        for k,indices in self.old_indices.items():
            if len(indices)<2: continue
            mm=[meta[i] for i in indices]
            if len({(m['crop'],m['line_id']) for m in mm})>1: cls='a'
            elif all(old.index[i]['letter']==old.index[indices[0]]['letter'] and
                     np.array_equal(old.index[i]['mask'],old.index[indices[0]]['mask']) for i in indices): cls='b'
            else: cls='c'
            duplicate_classes[cls]+=1
        if duplicate_classes['c']: raise ValueError('distinct old slots share identity')
        entries={i:dict(dataset=old, index=i, meta=m, provenance='old', weight=1., target=old.index[i]['target'].copy())
                 for i,m in enumerate(meta)}
        # Integer handles preserve every old row, including repeated identities.
        old_lookup={k:ii[0] for k,ii in self.old_indices.items() if len(ii)==1}
        order=list(range(len(keys))); touched=set(); pools={}; self.quarantined=[]
        overlay_duplicate_hits=0
        for row in rows(manifest):
            if row.get('role','train')!='train': raise ValueError('manifest requires train role')
            key=identity(row['slot_id'])
            target_key=identity(row.get('replaces', row.get('removes', row['slot_id'])))
            ambiguous=any(len(self.old_indices.get(k,[]))>1 for k in (key,target_key))
            overlay_duplicate_hits+=int(ambiguous)
            if ambiguous:
                raise ValueError('ambiguous old identity for replacement')
            handle=old_lookup.get(key,key); target_handle=old_lookup.get(target_key,target_key)
            if target_key in touched or key in touched: raise ValueError('slot modified more than once')
            touched.update((key,target_key))
            if 'removes' in row:
                if target_handle not in entries: raise ValueError('removal target missing')
                del entries[target_handle]; continue
            for field in ('line_id','doc','source','provenance','targets','loss_weight'):
                if field not in row: raise ValueError('missing manifest field '+field)
            prov=row['provenance']; weight=float(row['loss_weight'])
            if prov not in PROVENANCE or not math.isfinite(weight) or weight<=0: raise ValueError('invalid provenance/weight')
            if weight != (.5 if prov=='pseudo' else 1.): raise ValueError('recipe provenance weight mismatch')
            unknown=row.get('unknown',[])
            if set(unknown)-set(HEADS): raise ValueError('unknown head name')
            y=row['targets']
            if len(y)!=4 or any(not isinstance(v,int) or not 0<=v<len(c) for (h,c),v in zip(HEADS.items(),y) if h not in unknown):
                raise ValueError('invalid four-head targets')
            if unknown:
                self.quarantined.append(row)
                entries.pop(target_handle,None)
                continue
            if 'replaces' in row and target_handle not in entries: raise ValueError('replacement target missing')
            if handle in entries:
                if target_key!=key: raise ValueError('replacement collides with existing slot')
                e=entries[handle]
                if any(row[f]!=e['meta'][f] for f in ('line_id','doc','source')): raise ValueError('old metadata mismatch')
                if prov=='old' and (list(y)!=list(e['target']) or weight!=1): raise ValueError('old row changed labels')
                if prov!='old' and 'replaces' not in row: raise ValueError('existing slot requires replaces')
            else:
                if extra_factory is None or 'pool' not in row: raise ValueError('new slot requires extracted pool')
                path=str(Path(native_pool if row['pool']=='native' and native_pool else row['pool']).resolve())
                if path not in pools:
                    verify_receipt(path); ds=extra_factory(path)
                    mm=inventory_ids(ds,inventory); lookup={identity(m['slot_id']):(i,m) for i,m in enumerate(mm)}
                    if len(lookup)!=len(mm): raise ValueError('duplicate extra slot identity')
                    pools[path]=(ds,lookup)
                ds,lookup=pools[path]
                if key not in lookup: raise ValueError('new slot absent from pool')
                i,m=lookup[key]
                if any(row[f]!=m[f] for f in ('line_id','doc','source')): raise ValueError('new metadata mismatch')
                e=dict(dataset=ds,index=i,meta=m)
                if 'replaces' in row:
                    pos=order.index(target_handle); order[pos]=handle; del entries[target_handle]
                else: order.append(handle)
            entries[handle]=dict(e,teacher_seen_document=row.get('teacher_seen_document',False),provenance=prov,weight=weight,target=np.asarray(y,dtype=np.int8))
        self.entries=[entries[k] for k in order if k in entries]
        self.index=np.array([e['dataset'].index[e['index']] for e in self.entries],dtype=old.index.dtype)
        for r,e in zip(self.index,self.entries): r['target']=e['target']
        self.loss_weights=np.asarray([e['weight'] for e in self.entries],dtype=np.float32)
        self.provenances=[e['provenance'] for e in self.entries]
        self.identity=bool(len(self.entries)==len(old) and all(e['dataset'] is old and e['index']==i and e['weight']==1 and
            np.array_equal(e['target'],old.index[i]['target']) for i,e in enumerate(self.entries)))
        self.binding=dict(manifest_sha256=sha256(manifest),inventory_sha256=sha256(inventory),
            old_rows=len(old),old_unique_keys=len(self.old_indices),
            old_duplicate_rows=sum(len(ii) for ii in self.old_indices.values() if len(ii)>1),
            old_excess_rows=len(old)-len(self.old_indices),
            old_duplicate_groups={c:duplicate_classes[c] for c in 'abcd'},
            overlay_hits_on_duplicated_keys=overlay_duplicate_hits,
            unique_counts=dict(Counter(self.provenances)),quarantined=len(self.quarantined),old_pool_identity=self.identity)

    def __len__(self): return len(self.entries)

    def __getitem__(self,i):
        e=self.entries[i]; grey,letter,_,mask,_=e['dataset'][e['index']]
        return grey,letter,e['target'].astype(np.int64),mask,i
