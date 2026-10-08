"""Receipt-bound Chromium page images and DOM/PDF labels, without OCR."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from typing import Iterable, Mapping, Sequence
import time
import unicodedata
from urllib.parse import unquote, urlsplit

from PIL import Image

from greekocr.types import PathLike, Record
from .web_sources import _PoliteHTTP

__all__ = ['PageRecord', 'render_pages', 'records_from_dom', 'records_from_pdf',
           'degrade_twins', 'page_records']

_A4 = (210 / 25.4 * 96, 297 / 25.4 * 96)
_FREEZE = '''*,*::before,*::after {animation:none!important;transition:none!important;
 caret-color:transparent!important;scroll-behavior:auto!important}
 html {scroll-behavior:auto!important}'''
_DOM = r'''(scale) => {
 const lines=[], nodes=[], warnings=[];
 const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
 const segmenter=new Intl.Segmenter(document.documentElement.lang||'el',{granularity:'grapheme'});
 let node, id=0;
 const box=r=>[r.left+scrollX,r.top+scrollY,r.right+scrollX,r.bottom+scrollY];
 while(node=walker.nextNode()) {
  const parent=node.parentElement, raw=node.data, nodeId=id++;
  const info={node_id:nodeId,text_raw:raw,line_ids:[]}; nodes.push(info);
  if(!raw || parent.closest('script,style,template,svg,canvas')) {info.excluded='non-content';continue;}
  let invisible=false;
  for(let p=parent;p;p=p.parentElement) {
   const s=getComputedStyle(p);
   if(s.display==='none'||Number(s.opacity)===0) invisible=true;
  }
  const style=getComputedStyle(parent), range=document.createRange();range.selectNodeContents(node);
  if(style.visibility!=='visible')invisible=true;
  const rects=Array.from(range.getClientRects()).filter(r=>r.width>0&&r.height>0);
  info.rects_css=rects.map(box);info.rects_pixel=info.rects_css.map(r=>r.map(v=>v*scale));
  if(invisible||!rects.length) {info.excluded=raw.trim()?'not-visible':'collapsed-whitespace';continue;}
  if(style.textTransform!=='none') {info.excluded='text-transform';warnings.push('text-transform');continue;}
  if(style.writingMode!=='horizontal-tb'||style.direction!=='ltr') {
   info.excluded='unsupported-writing-direction';warnings.push('unsupported-writing-direction');continue;
  }
  const fragments=rects.map(r=>({rect:r,parts:[],start:null,end:null}));
  for(const s of segmenter.segment(raw)) {
   range.setStart(node,s.index);range.setEnd(node,s.index+s.segment.length);
   const glyphs=Array.from(range.getClientRects()).filter(r=>r.width>0&&r.height>0);
   if(!glyphs.length)continue;
   const g=glyphs[0], cx=(g.left+g.right)/2, cy=(g.top+g.bottom)/2;
   let best=0, distance=Infinity;
   fragments.forEach((f,i)=>{
    const r=f.rect, d=Math.abs(cy-(r.top+r.bottom)/2)*1000+
     Math.max(0,r.left-cx,cx-r.right);
    if(d<distance){best=i;distance=d;}
   });
   const f=fragments[best];f.parts.push(s.segment);
   f.start=f.start===null?s.index:Math.min(f.start,s.index);f.end=s.index+s.segment.length;
  }
  for(const f of fragments) {
   if(!f.parts.length)continue;
   let text=f.parts.join('');
   if(!['pre','pre-wrap','break-spaces'].includes(style.whiteSpace))text=text.replace(/[\t\r\n ]+/g,' ');
   const css=box(f.rect), lineId=lines.length;
   lines.push({line_id:lineId,node_id:nodeId,text:text.normalize('NFC'),text_raw:raw.slice(f.start,f.end),
    start_utf16:f.start,end_utf16:f.end,bbox_css:css,bbox_pixel:css.map(v=>v*scale),
    font_family:style.fontFamily,font_size:style.fontSize,white_space:style.whiteSpace,
    geometry_basis:'DOM Range.getClientRects',coordinate_system:'top-origin page pixels'});
   info.line_ids.push(lineId);
  }
  if(!info.line_ids.length)info.excluded='collapsed-whitespace';
 }
 const fonts=Array.from(document.fonts).map(f=>({family:f.family,style:f.style,
   weight:f.weight,status:f.status,stretch:f.stretch}));
 return {schema:'web-render-dom-v1',scale,lines,nodes,fonts,
  computed_font_families:Array.from(new Set(lines.map(l=>l.font_family))).sort(),
  width:Math.max(document.documentElement.scrollWidth,innerWidth),
  height:Math.max(document.documentElement.scrollHeight,innerHeight),
  warnings:Array.from(new Set(warnings))};
}'''


@dataclass(frozen=True)
class PageRecord:
    """Capture receipt and absolute artifact paths (None for failed captures)."""
    page_id: str
    html_path: str | None
    pdf_path: str | None
    png_path: str | None
    dom_path: str | None
    print_dom_path: str | None
    receipt_path: str
    receipt: Record


def _write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _metadata(path: Path, receipt: Mapping[str, object] | None) -> Record:
    if receipt is not None:
        return dict(receipt)
    candidate = path.parent / 'receipt.json'
    return json.loads(candidate.read_text()) if candidate.exists() else {}


async def _prepare_navigation(client: _PoliteHTTP, context, url: str, timeout: float) -> None:
    """Use the shared policy state before goto; never block Playwright's event loop."""
    origin = client._origin(url)

    async def pace(delay: float) -> None:
        wait = client._last.get(origin, -float('inf')) + delay - time.monotonic()
        if wait > 0:
            await asyncio.sleep(wait)
        client._last[origin] = time.monotonic()

    if origin not in client._robots:
        await pace(client.interval)
        # Fetch only robots here. Chromium owns the document and its subresources.
        response = await context.request.get(origin + '/robots.txt', timeout=timeout * 1000,
                                             max_redirects=0)
        try:
            body = await response.body()
            if len(body) > client.limit:
                raise ValueError('web response exceeds byte limit: ' + origin + '/robots.txt')
            client._cache_robots(origin, dict(status=response.status, body=body))
        finally:
            await response.dispose()
    await pace(client._navigation_interval(url))


async def _await_fonts(page, timeout: float) -> None:
    # evaluate itself has no timeout: the enclosing wall-clock watchdog covers it.
    await page.evaluate("""() => {
        window.__webRenderFontsReady = false;
        document.fonts.ready.then(() => { window.__webRenderFontsReady = true; });
    }""")
    handle = await page.wait_for_function('window.__webRenderFontsReady === true', timeout=timeout * 1000)
    await handle.dispose()


def render_pages(urls: Iterable[PathLike | Mapping[str, object]], out_dir: PathLike, *,
                 viewport: tuple[int, int] | Mapping[str, int] = (794, 1123), scale: float = 2.0,
                 print_to_pdf: bool = True, screenshot: bool = True,
                 block_media: bool = True, licences: Mapping[str, str] | None = None,
                 offline: bool = False, interval: float = 1.0,
                 timeout: float = 30.0, client: _PoliteHTTP | None = None) -> list[PageRecord]:
    """Render pages with polite top-level navigation and a 2*timeout page watchdog."""
    if isinstance(viewport, Mapping):
        viewport = (viewport['width'], viewport['height'])
    if (len(viewport) != 2 or any(not isinstance(v, int) or v <= 0 for v in viewport)
            or not math.isfinite(scale) or scale <= 0 or not math.isfinite(timeout) or timeout <= 0):
        raise ValueError('viewport, scale and timeout must be positive')
    client = client or _PoliteHTTP(interval=interval, timeout=timeout)
    try:
        from playwright.async_api import async_playwright, Error, TimeoutError as PlaywrightTimeout
    except ImportError as error:
        raise ImportError('install greek-ocr-toolkit[web] and playwright install chromium') from error
    # Resolve discovery generators before starting the browser's event loop.
    sources = list(urls)
    destination = Path(out_dir).resolve()
    destination.mkdir(parents=True, exist_ok=True)

    async def render() -> list[PageRecord]:
        records: list[PageRecord] = []
        failed = 0
        async with async_playwright() as playwright:
            try:
                browser = await playwright.chromium.launch(headless=True, timeout=10000)
            except Error as error:
                raise RuntimeError('Chromium unavailable or cannot start: ' + str(error).splitlines()[0]) from error
            try:
                for index, source in enumerate(sources):
                    spec = dict(source) if isinstance(source, Mapping) else {'url': str(source)}
                    original = str(spec.get('url') or spec.get('path') or '')
                    if not original and 'html' not in spec:
                        raise ValueError('render input needs url/path or html')
                    remote = urlsplit(original).scheme in ('http', 'https')
                    if remote and offline and 'html' not in spec:
                        raise ValueError('offline render refuses remote source: ' + original)
                    parts = urlsplit(original)
                    if parts.scheme == 'file' and parts.netloc not in ('', 'localhost'):
                        raise ValueError('remote file URLs are not supported')
                    local = Path(unquote(parts.path) if parts.scheme == 'file' else original).resolve() if not remote and 'html' not in spec else None
                    url = original if remote else local.as_uri() if local else original
                    licence = str(spec.get('licence') or (licences or {}).get(original) or 'unspecified; rights review required')
                    page_id = f'{index:05d}-' + hashlib.sha256(url.encode()).hexdigest()[:12]
                    work = destination / page_id
                    work.mkdir(exist_ok=False)
                    fetched_at = datetime.now(timezone.utc).isoformat()
                    started = time.monotonic()
                    context = None
                    blocked: list[Record] = []
                    responses = []
                    network = dict(responses=0, subresources=0, response_bytes=0,
                                   subresource_bytes=0, unmeasured_responses=0, resources=[],
                                   byte_basis='Chromium request.sizes responseBodySize (encoded body bytes)')
                    state = dict(final_url=url, http_status=None, bytes=0)

                    async def capture() -> PageRecord:
                        nonlocal context
                        context = await browser.new_context(viewport={'width': viewport[0], 'height': viewport[1]},
                                                            device_scale_factor=scale, locale='el-GR', timezone_id='UTC',
                                                            color_scheme='light', reduced_motion='reduce',
                                                            java_script_enabled=False, service_workers='block',
                                                            user_agent=client.user_agent)
                        page = await context.new_page()
                        page.set_default_timeout(timeout * 1000)

                        async def route_request(route):
                            request = route.request
                            target = request.url
                            if block_media and request.resource_type in ('image', 'media'):
                                blocked.append(dict(url=target, reason='block_media'))
                                await route.abort()
                            elif target.startswith(('http://', 'https://')) and (offline or not remote or 'html' in spec):
                                blocked.append(dict(url=target, reason='offline'))
                                await route.abort()
                            else:
                                await route.continue_()

                        def response_event(response):
                            # No body reads, HTTP, pacing or waits inside event callbacks.
                            request = response.request
                            subresource = not (request.is_navigation_request() and request.frame == page.main_frame)
                            network['responses'] += 1
                            network['subresources'] += int(subresource)
                            responses.append((response, subresource))

                        await context.route('**/*', route_request)
                        page.on('response', response_event)
                        if 'html' in spec:
                            await page.set_content(str(spec['html']), wait_until='load', timeout=timeout * 1000)
                            status, final_url = spec.get('api_status'), url
                            raw_html = str(spec['html']).encode('utf-8')
                        else:
                            if remote:
                                await _prepare_navigation(client, context, url, timeout)
                            response = await page.goto(url, wait_until='load', timeout=timeout * 1000)
                            status, final_url = response.status if response else None, page.url
                            state.update(final_url=final_url, http_status=status)
                            if remote:
                                if status is None or not 200 <= status < 300:
                                    raise ValueError('capture HTTP status ' + str(status))
                                raw_html = await response.body()
                                if len(raw_html) > client.limit:
                                    raise ValueError('web response exceeds byte limit: ' + final_url)
                            else:
                                raw_html = local.read_bytes()
                        state.update(final_url=final_url, http_status=status, bytes=len(raw_html))
                        await page.add_style_tag(content=_FREEZE)
                        await page.evaluate("""(blocked) => {
                            document.querySelectorAll('video,audio').forEach(e=>e.pause());
                            window.__webRenderImagesReady = blocked;
                            if(!blocked) {
                                document.querySelectorAll('img').forEach(e=>e.loading='eager');
                                Promise.all(Array.from(document.images).map(i=>i.decode().catch(()=>{})))
                                    .then(()=>{window.__webRenderImagesReady=true;});
                            }
                            window.scrollTo(0,0);
                        }""", block_media)
                        await _await_fonts(page, timeout)
                        if not block_media:
                            handle = await page.wait_for_function('window.__webRenderImagesReady === true', timeout=timeout * 1000)
                            await handle.dispose()
                        title = await page.title()
                        lang = await page.evaluate('document.documentElement.lang')
                        dom = await page.evaluate(_DOM, scale)
                        dom.update(source_url=final_url, licence=licence)
                        html_path = work / 'source.html'
                        html_path.write_bytes(raw_html)
                        (work / 'rendered.html').write_text(await page.content(), encoding='utf-8')
                        if 'source_json' in spec:
                            _write(work / 'source.json', spec['source_json'])
                        png_path = work / 'page.png' if screenshot else None
                        if png_path:
                            await page.screenshot(path=str(png_path), full_page=True, animations='disabled',
                                                  scale='device', timeout=timeout * 1000)
                        pdf_path = work / 'page.pdf' if print_to_pdf else None
                        print_dom_path = work / 'print_dom.json' if print_to_pdf else None
                        if pdf_path:
                            await page.emulate_media(media='print')
                            await page.set_viewport_size({'width': math.ceil(_A4[0]), 'height': math.ceil(_A4[1])})
                            # Match the continuous print layout's fractional A4 width. Fragmentation is audited separately.
                            await page.add_style_tag(content=f'html {{width:{_A4[0]}px!important}}')
                            await _await_fonts(page, timeout)
                            print_dom = await page.evaluate(_DOM, 1.0)
                            print_dom.update(source_url=final_url, licence=licence,
                                             layout='continuous print DOM; pagination may differ', a4_css=list(_A4))
                            _write(print_dom_path, print_dom)
                            await page.pdf(path=str(pdf_path), format='A4', print_background=True,
                                           margin=dict(top='0', right='0', bottom='0', left='0'),
                                           prefer_css_page_size=False, display_header_footer=False)
                        dom_path = work / 'dom.json'
                        _write(dom_path, dom)
                        for response, subresource in responses:
                            resource = dict(url=response.url, status=response.status,
                                            resource_type=response.request.resource_type, subresource=subresource, bytes=None)
                            try:
                                await response.finished()
                                resource['bytes'] = (await response.request.sizes())['responseBodySize']
                            except Error:
                                network['unmeasured_responses'] += 1
                            else:
                                network['response_bytes'] += resource['bytes']
                                if subresource:
                                    network['subresource_bytes'] += resource['bytes']
                            network['resources'].append(resource)
                        state['bytes'] += network['subresource_bytes']
                        receipt = dict(schema='web-render-v1', page_id=page_id, url=url, fetched_at=fetched_at,
                                       final_url=final_url, status=status, capture_status='rendered', title=title, lang=lang,
                                       licence=licence, source=spec.get('source'), api_url=spec.get('api_url'),
                                       viewport=list(viewport), scale=scale, user_agent=await page.evaluate('navigator.userAgent'),
                                       render_url=page.url, timeout=timeout, watchdog_seconds=2 * timeout,
                                       elapsed_seconds=time.monotonic() - started, bytes=state['bytes'], network=network,
                                       chromium_version=browser.version, fonts=dom['fonts'],
                                       computed_font_families=dom['computed_font_families'],
                                       sha256=dict(html=_sha(html_path), pdf=_sha(pdf_path) if pdf_path else None,
                                                   png=_sha(png_path) if png_path else None,
                                                   dom=_sha(dom_path), print_dom=_sha(print_dom_path) if print_dom_path else None,
                                                   rendered_html=_sha(work / 'rendered.html')),
                                       files=dict(html='source.html', pdf='page.pdf' if pdf_path else None,
                                                  png='page.png' if png_path else None, dom='dom.json',
                                                  print_dom='print_dom.json' if print_dom_path else None,
                                                  rendered_html='rendered.html'),
                                       determinism=dict(animations=False, javascript=False, service_workers=False,
                                                        fonts_awaited=True, block_media=block_media,
                                                        lazy_images='blocked' if block_media else 'eager', locale='el-GR', timezone='UTC'),
                                       blocked_requests=blocked, dom_warnings=dom['warnings'],
                                       api_final_url=spec.get('api_final_url'),
                                       label_limits='DOM fragments exclude generated content, hidden nodes, text-transform and non-LTR text')
                        receipt_path = work / 'receipt.json'
                        if 'source_json' in spec:
                            receipt['sha256']['source_json'] = _sha(work / 'source.json')
                            receipt['files']['source_json'] = 'source.json'
                        _write(receipt_path, receipt)
                        return PageRecord(page_id, str(html_path), str(pdf_path) if pdf_path else None,
                                          str(png_path) if png_path else None, str(dom_path),
                                          str(print_dom_path) if print_dom_path else None, str(receipt_path), receipt)

                    try:
                        record = await asyncio.wait_for(capture(), timeout=2 * timeout)
                        if time.monotonic() - started > 2 * timeout:
                            raise asyncio.TimeoutError('per-page watchdog exceeded')
                        progress_status = 'ok'
                    except (asyncio.TimeoutError, Error, OSError, ValueError) as error:
                        progress_status = 'timeout' if isinstance(error, (asyncio.TimeoutError, PlaywrightTimeout)) else 'error'
                        failed += 1
                        receipt = dict(schema='web-render-v1', page_id=page_id, url=url, fetched_at=fetched_at,
                                       final_url=state['final_url'], status=progress_status, capture_status=progress_status,
                                       http_status=state['http_status'], licence=licence, source=spec.get('source'),
                                       timeout=timeout, watchdog_seconds=2 * timeout,
                                       elapsed_seconds=time.monotonic() - started, bytes=state['bytes'], network=network,
                                       blocked_requests=blocked,
                                       error=str(error).splitlines()[0] if str(error) else 'per-page watchdog exceeded',
                                       files=dict(html=None, pdf=None, png=None, dom=None, print_dom=None, rendered_html=None),
                                       sha256={})
                        receipt_path = work / 'receipt.json'
                        _write(receipt_path, receipt)
                        record = PageRecord(page_id, None, None, None, None, None, str(receipt_path), receipt)
                    finally:
                        if context is not None:
                            # A stuck close must not keep an abandoned page holding up the wave.
                            try:
                                await asyncio.wait_for(context.close(), timeout=min(timeout, 1.0))
                            except (asyncio.TimeoutError, Error):
                                pass
                    records.append(record)
                    print(f"WEB_PAGE {index + 1}/{len(sources)} {progress_status} {url} {record.receipt['bytes']}", flush=True)
            finally:
                try:
                    await asyncio.wait_for(browser.close(), timeout=10)
                except (asyncio.TimeoutError, Error):
                    pass
        print(f'WEB_WAVE_DONE pages={len(records)} failed={failed}', flush=True)
        return records

    return asyncio.run(render())


def records_from_dom(png: PathLike, dom_lines: PathLike | Mapping[str, object] | Sequence[Record], *,
                     receipt: Mapping[str, object] | None = None) -> list[Record]:
    """Return per-text-node fragments in screenshot pixels, preserving raw text."""
    path = Path(png).resolve()
    metadata = _metadata(path, receipt)
    dom = json.loads(Path(dom_lines).read_text()) if isinstance(dom_lines, (str, Path)) else dom_lines
    lines = dom['lines'] if isinstance(dom, Mapping) else dom
    result = []
    with Image.open(path) as image:
        width, height = image.size
    for index, line in enumerate(lines):
        box = list(map(float, line['bbox_pixel']))
        if len(box) != 4 or not all(math.isfinite(v) for v in box) or box[2] <= box[0] or box[3] <= box[1]:
            raise ValueError('invalid DOM line box')
        result.append(dict(line, line_id=f"{metadata.get('page_id', path.stem)}-dom-{index:05d}",
                           text=unicodedata.normalize('NFC', line['text']), bbox_pixel=box,
                           page_path=str(path), tier='exact-rendered', label_tier='exact-rendered',
                           provenance='web_render', source_url=metadata.get('final_url') or line.get('source_url') or (dom.get('source_url') if isinstance(dom, Mapping) else None) or path.as_uri(),
                           licence=metadata.get('licence') or line.get('licence') or (dom.get('licence') if isinstance(dom, Mapping) else None) or 'unspecified; rights review required',
                           clipped=box[0] < 0 or box[1] < 0 or box[2] > width or box[3] > height))
    return result


def _visual_lines(dom: Record) -> list[Record]:
    """Join same-baseline inline fragments for comparison only, never relabel PDF."""
    groups: list[list[Record]] = []
    for line in sorted(dom['lines'], key=lambda r: (r['bbox_css'][1], r['bbox_css'][0])):
        b = line['bbox_css']
        group = next((g for g in groups if abs(g[0]['bbox_css'][3] - b[3]) <= 2
                      and b[0] - max(x['bbox_css'][2] for x in g) <= 32), None)
        if group is None:
            groups.append([line])
        else:
            group.append(line)
    result = []
    for group in groups:
        group.sort(key=lambda r: r['bbox_css'][0])
        text = ''.join(r['text'] for r in group).strip()
        if text:
            result.append(dict(text=unicodedata.normalize('NFC', text),
                               bbox_css=[min(r['bbox_css'][0] for r in group), min(r['bbox_css'][1] for r in group),
                                         max(r['bbox_css'][2] for r in group), max(r['bbox_css'][3] for r in group)]))
    return result


def _iou(a: Sequence[float], b: Sequence[float]) -> float:
    inter = max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def records_from_pdf(pdf_path: PathLike, *, dom_lines: PathLike | Mapping[str, object] | None = None,
                     receipt: Mapping[str, object] | None = None, out_dir: PathLike | None = None,
                     iou_threshold: float = 0.5) -> list[Record]:
    """Use the vendored PDFium extractor and write an independent DOM agreement report."""
    from greekocr._vendor.bench.o4b_textlayer_lines import pdf_pages
    from greekocr._vendor.bench.extract_lines import SCALE
    if not 0 <= iou_threshold <= 1:
        raise ValueError('IoU threshold must be in [0,1]')
    path = Path(pdf_path).resolve()
    metadata = _metadata(path, receipt)
    if dom_lines is None:
        candidate = path.parent / 'print_dom.json'
        dom_lines = candidate if candidate.exists() else None
    dom = json.loads(Path(dom_lines).read_text()) if isinstance(dom_lines, (str, Path)) else dom_lines
    visual = _visual_lines(dict(dom)) if dom is not None else []
    used: set[int] = set()
    output = Path(out_dir).resolve() if out_dir else path.parent / (path.stem + '_records')
    output.mkdir(parents=True, exist_ok=True)
    rows, failures = [], []
    for page_number, image, candidates, error in pdf_pages(path):
        if error:
            failures.append(dict(page=page_number, error=error))
            continue
        raster = output / f'p{page_number:04d}.png'
        image.save(raster)
        for index, candidate in enumerate(candidates):
            text = unicodedata.normalize('NFC', candidate['text']).strip()
            if not text:
                continue
            # PDFium tight boxes are at 200dpi. DOM Range boxes are CSS em boxes at 96dpi.
            css_box = [v / SCALE * 96 / 72 for v in candidate['char_bbox_pixel']]
            matches = [i for i, line in enumerate(visual) if i not in used and line['text'] == text]
            match = max(matches, key=lambda i: _iou(css_box, _page_box(visual[i]['bbox_css'], page_number)), default=None)
            agreement: Record = dict(text_match=match is not None, dom_line=match, iou=None)
            if match is not None:
                used.add(match)
                agreement['iou'] = _iou(css_box, _page_box(visual[match]['bbox_css'], page_number))
            line_id = f"{metadata.get('page_id', path.stem)}-pdf-p{page_number:04d}-{index:05d}"
            crop = output / (line_id + '.png')
            image.crop(candidate['bbox_pixel']).save(crop)
            rows.append(dict(candidate, text=text, line_id=line_id, page=page_number,
                             page_path=str(raster), crop_path=str(crop), tier='exact-rendered',
                             label_tier='exact-rendered', provenance='web_render',
                             source_url=metadata.get('final_url') or (dom.get('source_url') if dom else None) or path.as_uri(),
                             licence=metadata.get('licence') or (dom.get('licence') if dom else None) or 'unspecified; rights review required',
                             document_sha256=_sha(path), coordinate_system='top-origin 200dpi PDF raster pixels',
                             dom_agreement=agreement))
    values = [r['dom_agreement']['iou'] for r in rows if r['dom_agreement']['iou'] is not None]
    report = dict(schema='web-render-agreement-v1', pdf_sha256=_sha(path), pdf_lines=len(rows),
                  dom_visual_lines=len(visual), matched_lines=len(used),
                  pdf_text_agreement=len(used) / len(rows) if rows and dom is not None else None,
                  dom_text_coverage=len(used) / len(visual) if visual else None,
                  mean_iou=sum(values) / len(values) if values else None, iou_threshold=iou_threshold,
                  boxes_at_threshold=sum(v >= iou_threshold for v in values), failures=failures,
                  comparison='NFC text, strip outer whitespace; independent print DOM em boxes vs PDF glyph boxes',
                  geometry_limit='continuous DOM y modulo A4 is approximate under print fragmentation/CSS margins; low IoU is retained')
    _write(output / 'agreement.json', report)
    (output / 'records.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')
    return rows


def _page_box(box: Sequence[float], page: int) -> list[float]:
    return [box[0], box[1] - (page - 1) * _A4[1], box[2], box[3] - (page - 1) * _A4[1]]


def degrade_twins(page_png: PathLike, labels: Sequence[Record], *,
                  out_dir: PathLike | None = None, seed: int = 0) -> Record:
    """Call a vendored degradation adapter if present, else report unavailable (no fake twin)."""
    vendor = Path(__file__).resolve().parents[2] / '_vendor'
    modules = list(vendor.rglob('page_degrade.py'))
    if not modules:
        return dict(status='unavailable', reason='pipeline/page_degrade.py is not vendored',
                    page_png=str(Path(page_png).resolve()), labels=[dict(r) for r in labels], seed=seed)
    spec = importlib.util.spec_from_file_location('_greekocr_page_degrade', modules[0])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    adapter = getattr(module, 'degrade_twins', None)
    if not callable(adapter):
        return dict(status='unavailable', reason='vendored module has no label-preserving degrade_twins adapter',
                    vendor_path=str(modules[0]), labels=[dict(r) for r in labels], seed=seed)
    return adapter(page_png, labels, out_dir=out_dir, seed=seed)


def page_records(directory: PathLike) -> Record:
    """Verify capture hashes and extract all available screenshot/PDF records offline."""
    root = Path(directory).resolve()
    receipts = sorted(root.glob('*/receipt.json'))
    if (root / 'receipt.json').exists():
        receipts = [root / 'receipt.json']
    if not receipts:
        raise ValueError('no web render receipts found')
    summary = []
    for receipt_path in receipts:
        receipt = json.loads(receipt_path.read_text())
        work = receipt_path.parent
        if receipt.get('capture_status') in ('timeout', 'error'):
            summary.append(dict(page_id=receipt['page_id'], status=receipt['status'],
                                error=receipt['error'], dom_records=0, pdf_records=0, agreement=None))
            continue
        for kind, name in receipt['files'].items():
            if name:
                target = (work / name).resolve()
                if target.parent != work or _sha(target) != receipt['sha256'][kind]:
                    raise ValueError('capture checksum mismatch: ' + kind)
        dom_rows = records_from_dom(work / receipt['files']['png'], work / receipt['files']['dom'], receipt=receipt) if receipt['files']['png'] else []
        (work / 'dom_records.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in dom_rows), encoding='utf-8')
        pdf_rows = records_from_pdf(work / receipt['files']['pdf'], receipt=receipt) if receipt['files']['pdf'] else []
        summary.append(dict(page_id=receipt['page_id'], dom_records=len(dom_rows), pdf_records=len(pdf_rows),
                            agreement=str(work / 'page_records' / 'agreement.json') if pdf_rows else None))
    return dict(schema='web-render-records-v1', pages=summary)
