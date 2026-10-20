    @lru_cache(maxsize=128)
    def get(self,ctx,iid,offset):
        if ctx=='retained':
            rid=iid;r=self.admitted[rid];path=bind(m.SOURCE.parents[4]/r['crop_path'])
            meta=dict(book=m.book_id(self.parent[rid]),source_crop_sha256=r['crop_sha256'])
        else:
            item,meta=self.lookup[ctx,iid];rid=meta['row_id'];r=self.admitted[rid]
            path=bind(m.PACK/ctx/'r1'/item['crop'])
        record=self.records[rid]
        if m.sha(path)!=meta['source_crop_sha256'] or m.sha(path)!=r['crop_sha256']:raise ValueError('crop custody mismatch')
        if r['label']!=self.parent[rid]['label']:raise ValueError('parent/admission text mismatch')
        doc=self.doc(r['page_id']);line=doc['pages'][0]['lines'][record['docai_index']]
        with Image.open(path) as im:image=im.convert('RGB')
        if image.size!=(r['crop_width'],r['crop_height']):raise ValueError('crop dimensions differ')
        word,final,geo=symbol_crops(image,r['label'],offset,doc,line,r['crop_bbox'][:2])
        return dict(line=image,word=word,final=final,geometry=geo,crop=str(path),crop_sha256=m.sha(path),book=meta['book'])
