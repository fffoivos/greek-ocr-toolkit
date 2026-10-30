"""Page-local ownership IDs and ink generations for final-footprint rechecks.

Tokens survive dictionary copies. A geometry or source-owner change creates a
new generation. Polygon coordinates are compared to immutable records, never
serialized as cache identities; tokens have meaning only inside this ledger.
"""
import numpy as np


class Footprints:
    def __init__(self):
        self.records={};self.revisions={};self.next_owner=0

    def stamp(self,item):
        previous=tuple(item.get('ink_token',()))
        polygon=np.asarray(item['polygon'],float);sources=tuple(item.get('source_ids',()))
        if previous in self.records:
            old_sources,old_polygon=self.records[previous]
            if sources==old_sources and np.array_equal(polygon,old_polygon):return previous
            owner=previous[0]
        else:
            owner=self.next_owner;self.next_owner+=1;self.revisions[owner]=-1
        self.revisions[owner]+=1;token=(owner,self.revisions[owner])
        self.records[token]=(sources,polygon.copy());item['ink_token']=token
        return token

    def stamp_all(self,items):return {self.stamp(q) for q in items}

    def changed_indices(self,items,judged):
        return {i for i,q in enumerate(items) if self.stamp(q) not in judged}
