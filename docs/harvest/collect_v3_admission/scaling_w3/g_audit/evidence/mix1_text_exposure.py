def normalize_text(text):
    import unicodedata
    require(isinstance(text,str),'missing text label')
    return ' '.join(unicodedata.normalize('NFC',text).split())

class TextExposure:
    def __init__(self,references):
        normalized=[normalize_text(x) for x in references]
        self.exact=set(normalized)
        self.windows={s[i:i+30] for s in normalized for i in range(len(s)-29)}
    def hit(self,text):
        s=normalize_text(text)
        if s in self.exact:return 'exact'
        if any(s[i:i+30] in self.windows for i in range(len(s)-29)):return 'substring30'
        return None
