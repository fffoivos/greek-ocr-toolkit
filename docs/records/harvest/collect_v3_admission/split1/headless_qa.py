"""Offline browser QA for the lead; use an installed Playwright-compatible browser.
No downloads, network requests, live database, or publication.
"""
import base64,json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent
MOCK="""window.__writes=[];window.__reads=[];window.claude={use:async()=>({doc:(path)=>({get:async()=>{window.__reads.push(path);return {exists:false,data:()=>({})}},set:async(doc)=>{window.__writes.push({path,doc})}})})};"""

def main():
 result={'network':'OFF','screenshots':[],'status':'started'}
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch(executable_path=os.environ.get('SPLIT1_BROWSER','/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'),headless=True)
   context=browser.new_context(offline=True);context.route('http://**',lambda r:r.abort());context.route('https://**',lambda r:r.abort());context.add_init_script(MOCK)
   page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto((HERE/'OWNER_REVIEW.html').as_uri());page.wait_for_timeout(1400)
   assert page.evaluate('window.__writes.length')==0
   assert page.evaluate('window.__reads.length')==1359
   for name,size in [('desktop',{'width':1440,'height':1100}),('narrow',{'width':390,'height':844})]:
    page.set_viewport_size(size);page.evaluate('window.scrollTo(0,0)');page.screenshot(path=str(HERE/f'qa_{name}_intro.png'))
    first=page.locator('.card').first;first.scroll_into_view_if_needed();first.screenshot(path=str(HERE/f'qa_{name}_card.png'))
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),name
    result['screenshots'] += [f'qa_{name}_intro.png',f'qa_{name}_card.png']
   assert not errors,errors
   page.locator('.card .verdict').first.click();page.wait_for_timeout(500);assert page.evaluate('window.__writes.length')==1
   result.update(status='passed',errors=errors);browser.close()
 except Exception as e:
  result.update(status='blocked_or_failed',error=str(e));raise
 finally:(HERE/'headless_qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
