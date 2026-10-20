"""Offline HTML/image validation. Browser layout checks are optional (--browser)."""
from pathlib import Path
import base64
from html.parser import HTMLParser
from io import BytesIO
import json
import sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/labelfix/lqb'


class Sheet(HTMLParser):
    def __init__(self):super().__init__();self.cards=0;self.images=[];self.printed=[];self.intro=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='div' and a.get('class')=='card':self.cards+=1
        if tag=='img':self.images.append(a['src'])
        if tag=='input' and a.get('class')=='printed':self.printed.append(a.get('value',''))
        if tag=='section' and a.get('class')=='lqb-intro':self.intro+=1


def main():
    out=OUT/'validation';out.mkdir(exist_ok=True)
    page=(OUT/'scoreboard.html').read_text();sheet=Sheet();sheet.feed(page)
    for src in sheet.images:
        assert src.startswith('data:image/png;base64,')
        with Image.open(BytesIO(base64.b64decode(src.split(',',1)[1]))) as im:im.verify()
    ledger=json.loads((OUT/'scoreboard_cards.json').read_text())
    assert sheet.cards==len(ledger)==len(sheet.printed)
    assert all(sheet.printed) and sheet.intro==1
    assert 'Label Quality Scoreboard' in page and 'LQB_INTRO_PLACEHOLDER' not in page
    assert 'window.claude' not in page and 'db.doc(' not in page
    assert 'Not measured' in page and 'overflow-x:auto' in page
    is_v2='id="baseline"' in page
    if is_v2:
        assert page.index('id="baseline"') < page.index('id="headline"')
        assert 'SCORE_v2.md' in page and 'UNADOPTED' in page
        assert len(page.encode())<14_000_000
    result=dict(network=False,cards=sheet.cards,decoded_pngs=len(sheet.images),prefilled_printed=len(sheet.printed),intro_html=True,baseline_first=is_v2,remote_notes_disabled=True,bytes=len(page.encode()),browser_layout='not verified; structural checks only',layouts=[])
    if '--browser' in sys.argv:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            if '--firefox' in sys.argv:
                browser=p.firefox.launch(headless=True,executable_path=str(Path.home()/'Library/Caches/ms-playwright/firefox-1488/firefox/Nightly.app/Contents/MacOS/firefox'),firefox_user_prefs={'network.http.speculative-parallel-limit':0,'network.dns.disablePrefetch':True,'network.prefetch-next':False})
            else:
                browser=p.chromium.launch(headless=True,executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args=['--disable-background-networking','--disable-component-update','--no-first-run'])
            context=browser.new_context(offline=True);context.route('**/*',lambda r:r.abort() if r.request.url.startswith(('http:','https:')) else r.continue_())
            tab=context.new_page()
            for name,width,height in [('desktop',1440,1000),('narrow',390,844)]:
                tab.set_viewport_size(dict(width=width,height=height));tab.goto((OUT/'scoreboard.html').as_uri());tab.wait_for_load_state('load')
                data=tab.evaluate('''() => ({images:[...document.images].every(x=>x.complete&&x.naturalWidth>0),overflow:document.documentElement.scrollWidth>innerWidth})''')
                assert data['images'] and not data['overflow'],data
                tab.screenshot(path=str(out/(name+'.png')),full_page=False)
                result['layouts'].append(dict(viewport=name,**data))
            browser.close();result['browser_layout']='verified'
    (out/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__':main()
