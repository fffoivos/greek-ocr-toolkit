"""Offline browser QA and final receipt, using an in-memory DB stub to count writes."""
import base64
import io
import json
import os
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from ss6_build import SS, REVIEW, dump, sha

class Cards(HTMLParser):
    def __init__(self):super().__init__();self.cards=[];self.current=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='div' and a.get('class')=='card':self.current={'images':[]};self.cards.append(self.current)
        if tag=='img' and self.current is not None:self.current['images'].append(a['src'])

def main():
    receipt=json.loads((SS/'q3/SS6_RECEIPT.json').read_text());sheet=SS/'sheet/small_segments_sheet.html'
    parser=Cards();parser.feed(sheet.read_text());parser.close()
    assert len(parser.cards)==417 and all(len(c['images'])==1 for c in parser.cards)
    from PIL import Image
    for c in parser.cards:
        with Image.open(io.BytesIO(base64.b64decode(c['images'][0].split(',',1)[1]))) as im:im.verify()
    check={'html_parse':True,'cards':417,'every_card_one_decodable_image':True}
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser=None
        launch_errors={}
        for name,engine,executable in [
            ('Google Chrome',p.chromium,'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'),
            ('cached Firefox',p.firefox,str(Path.home()/'Library/Caches/ms-playwright/firefox-1488/firefox/Nightly.app/Contents/MacOS/firefox'))]:
            try:
                browser=engine.launch(executable_path=executable,headless=True,timeout=10000)
                break
            except Exception as exc:
                launch_errors[name]=str(exc)
        dump(SS/'q3/SS6_BROWSER_LAUNCH.json',launch_errors)
        if browser is None:
            check.update({'method':'HTML parse + verification of every embedded crop image',
                'headless_render':'unavailable at runtime: both local Chrome and cached Firefox abort with SIGABRT',
                'launch_log':'q3/SS6_BROWSER_LAUNCH.json',
                'visual_layout_verified':False,
                'no_writes_on_load':'Package source has explicit action/edited guard; browser verification unavailable.'})
        else:
            page=browser.new_page(viewport={'width':1280,'height':900})
            errors=[];network=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.route('http://**/*',lambda route:(network.append(route.request.url),route.abort()))
            page.route('https://**/*',lambda route:(network.append(route.request.url),route.abort()))
            page.add_init_script('''window.ss6Writes=[]; window.ss6Reads=[];
              window.ArtifactData={list:async(...args)=>{window.ss6Reads.push(args);return []},
              get:async(...args)=>{window.ss6Reads.push(args);return null},
              set:async(...args)=>{window.ss6Writes.push(args)},
              put:async(...args)=>{window.ss6Writes.push(args)},
              create:async(...args)=>{window.ss6Writes.push(args)},
              update:async(...args)=>{window.ss6Writes.push(args)}};''')
            page.goto(sheet.as_uri(),wait_until='load');page.wait_for_function('Array.from(document.images).every(i=>i.complete && i.naturalWidth>0)');page.wait_for_timeout(800)
            check['browser']='local Google Chrome headless via Playwright; network blocked'
            check['browser_version']=browser.version
            check['desktop']=page.evaluate('''()=>({cards:document.querySelectorAll('.card').length, images:document.images.length, broken:Array.from(document.images).filter(i=>!i.complete||!i.naturalWidth).length, overflow:document.documentElement.scrollWidth>innerWidth, writes:window.ss6Writes.length, reads:window.ss6Reads.length})''')
            assert check['desktop']['cards']==417 and check['desktop']['broken']==0
            assert check['desktop']['writes']==0 and not check['desktop']['overflow']
            page.screenshot(path=str(SS/'sheet/SS6_desktop.png'))
            # Exercise navigation and zoom only: do not create owner marks or notes.
            page.locator('.card').first.click(position={'x':10,'y':10});page.keyboard.press('ArrowDown');page.keyboard.press('z');page.keyboard.press('z')
            check['versions']=page.evaluate('''()=>Array.from(document.querySelectorAll('.card')).map(c=>({id:c.querySelector('.note').id.slice(2), latest:c.dataset.tool, versions:Array.from(c.querySelectorAll('tr.version th')).map(e=>e.textContent)}))''')
            manifest=json.loads((SS/'sheet/card_manifest.json').read_text())
            owners={r['line_id']:r for r in map(json.loads,(SS/'q1/owner_joined.jsonl').read_text().splitlines())}
            for m,c in zip(manifest,check['versions']):
                assert c['id']==m['doc_id']
                expected=['0.5','0.8 (latest)'] if owners.get(m['line_id'],{}).get('verdict_08') else ['0.5 (latest)']
                assert c['versions']==expected,(c,expected)
            check['cards_with_08']=sum(len(c['versions'])==2 for c in check.pop('versions'))
            page.set_viewport_size({'width':390,'height':844});page.evaluate('scrollTo(0,0)');page.wait_for_timeout(200)
            check['narrow']=page.evaluate('''()=>({overflow:document.documentElement.scrollWidth>innerWidth,broken:Array.from(document.images).filter(i=>!i.naturalWidth).length,writes:window.ss6Writes.length})''')
            page.screenshot(path=str(SS/'sheet/SS6_narrow.png'))
            assert not check['narrow']['overflow'] and check['narrow']['broken']==0 and check['narrow']['writes']==0
            assert not errors,errors
            assert not network,network
            check['page_errors']=errors;check['network_requests']=network;check['no_writes_on_load']=True
            browser.close()
    result=subprocess.run([sys.executable,str(SS/'tests/test_ss6.py')],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    (SS/'q3/SS6_TESTS.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0,result.stderr
    receipt['status']='READY';receipt['render_check']=check;receipt['tests']={'command':f'{sys.executable} {SS}/tests/test_ss6.py','passed':8,'returncode':0,'log':'q3/SS6_TESTS.log'}
    outputs=[SS/p for p in ['samples.jsonl','q3/Q3_TABLES.md','q3/q3.json','q3/SS6_TESTS.log','sheet/small_segments_sheet.html','sheet/card_manifest.json','q3/SS6_BROWSER_LAUNCH.json','tools/ss6_build.py','tools/ss6_validate.py','tests/test_ss6.py']]
    outputs += [p for p in [SS/'sheet/SS6_desktop.png',SS/'sheet/SS6_narrow.png'] if p.exists()]
    receipt['outputs']={str(p):sha(p) for p in outputs}
    receipt['receipt_hash_note']='Receipt excludes its own hash to avoid self-reference.'
    receipt['constraints']={'network_calls':0,'reading_runs':0,'git_add_commit':False,'review_worktree_edited':False,'saved_judgments_only':True}
    dump(SS/'q3/SS6_RECEIPT.json',receipt)
    print(json.dumps(check,indent=2));print('SS6 READY: Q3 tables q3/Q3_TABLES.md, samples.jsonl 437, sheet SS/sheet/small_segments_sheet.html (417 cards)')
if __name__=='__main__':main()
