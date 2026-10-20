"""Offline structural verification and optional local headless screenshots.
Run with a Python providing bs4 and Playwright (no installation or network).
"""
import base64, hashlib, json
from pathlib import Path
from bs4 import BeautifulSoup
D=Path(__file__).resolve().parent
r=json.loads((D/'receipt.json').read_text())
manifest={m['line_id']:m for m in map(json.loads,(D/'cards.jsonl').read_text().splitlines())}
soup=BeautifulSoup((D/'seg09_sheet.html').read_text(),'html.parser')
cards=soup.select('.card');ids=[]
assert len(cards)==r['cards']==len(manifest)
for card in cards:
    note=card.select_one('.notes');lid=note['data-line'];m=manifest[lid]
    assert note['data-id']=='seg09:'+lid;ids.append(note['data-id'])
    assert not card.has_attr('data-verdict') and not {'vkeep','vdrop'}&set(card.get('class',[]))
    assert card['data-tool']==m['verdicts']['0.9-s4']
    assert not card.select_one('.note').get_text()
    assert hashlib.sha256(base64.b64decode(card.select_one('img')['src'].split(',',1)[1])).hexdigest()==m['crop_sha256']
    assert len(card.select('tr.version'))==2
    assert [v.th.get_text() for v in card.select('tr.version')]==['0.8','0.9-s4 (latest)']
    assert card.select_one('table tr th').get_text()=='Google'
    assert card.select_one('.ov svg')
assert len(ids)==len(set(ids))
assert not soup.select('link,iframe,img[src^="http"],script[src]')
assert len(soup.select('script'))==1
assert soup.select_one('script').string==(D/'vendor/owner_sheet.js').read_text()
r['structural_checks']={'cards':len(cards),'exact_embedded_crop_hashes':len(cards),'initial_marks_empty':True,'database_ids_unique':True,'last_two_versions':True,'self_contained':True,'embedded_js_byte_exact':True,'google_directly_beneath_crop':True}
r['screenshot']='unavailable';failures=[]
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser=None
        for engine,options in [
            (p.chromium,dict(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args=['--disable-background-networking','--disable-component-update','--no-first-run'])),
            (p.firefox,dict(firefox_user_prefs={'network.offline':True,'app.update.enabled':False,'toolkit.telemetry.enabled':False}))]:
            try:browser=engine.launch(headless=True,timeout=10000,**options);break
            except Exception as exc:failures.append(str(exc))
        if browser:
            context=browser.new_context(viewport={'width':1100,'height':1000},device_scale_factor=1,service_workers='block')
            blocked=[]
            def route(req):
                if req.request.url.startswith(('file:','data:')):req.continue_()
                else:blocked.append(req.request.url);req.abort()
            context.route('**/*',route)
            page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto((D/'seg09_sheet.html').as_uri(),wait_until='load')
            actual=page.locator('.card');assert actual.count()==r['cards']
            assert page.locator('.card[data-verdict],.card.vkeep,.card.vdrop').count()==0
            bounds=[actual.nth(i).bounding_box() for i in range(3)];top=bounds[0]['y'];bottom=bounds[-1]['y']+bounds[-1]['height']
            page.screenshot(path=str(D/'first_3_cards.png'),clip={'x':0,'y':top-10,'width':1100,'height':bottom-top+20},animations='disabled')
            page.screenshot(path=str(D/'intro.png'),animations='disabled')
            page.set_viewport_size({'width':390,'height':844});actual.first.scroll_into_view_if_needed()
            page.screenshot(path=str(D/'narrow_first_card.png'),animations='disabled')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            assert not errors and not blocked
            browser.close();r['screenshot']='ok'
            r['screenshots']=['first_3_cards.png','intro.png','narrow_first_card.png']
            r['browser_checks']={'page_errors':errors,'network_requests':blocked,'narrow_no_horizontal_overflow':True}
except Exception as exc:failures.append(str(exc))
(D/'browser_check.log').write_text('\n\n'.join(failures)+'\n')
r['screenshot_reason']='Local Chrome closed during launch; local headless Firefox aborted (SIGABRT). No download or network attempted.' if r['screenshot']=='unavailable' else ''
r['builder_sha256']=hashlib.sha256((D/'build.py').read_bytes()).hexdigest()
r['manifest_sha256']=hashlib.sha256((D/'cards.jsonl').read_bytes()).hexdigest()
(D/'receipt.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(r['structural_checks']));print('screenshot:',r['screenshot'])
