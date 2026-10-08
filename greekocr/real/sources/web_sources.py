"""Greek web seeds and a bounded, robots-aware transport (no import-time I/O)."""
from __future__ import annotations

import html
import json
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from collections import deque
from html.parser import HTMLParser
from typing import Iterator, Sequence

from greekocr.types import Record

__all__ = ['source_catalog', 'source_pages', 'mastodon_post_html']

USER_AGENT = 'GreekOCRWebRender/0.1 (research page capture; robots respected)'
_CATALOG = {
    'wikipedia-random': dict(url='https://el.wikipedia.org/wiki/Ειδικό:Τυχαία', licence='CC-BY-SA-4.0', kind='random'),
    'wikipedia-featured': dict(url='https://el.wikipedia.org/wiki/Βικιπαίδεια:Προβεβλημένα_λήμματα', licence='CC-BY-SA-4.0', kind='wiki'),
    'wikisource': dict(url='https://el.wikisource.org/wiki/Κατηγορία:Πολυτονικά_κείμενα', licence='work-specific; transcription CC-BY-SA-4.0; underlying work review required', kind='wiki'),
    'gov': dict(url='https://www.gov.gr/', licence='unknown; government page rights review required', kind='links'),
    'eur-lex': dict(url='https://eur-lex.europa.eu/legal-content/EL/TXT/?uri=CELEX:32016R0679', licence='EU reuse policy; document-specific rights review required', kind='links'),
    'news-kathimerini': dict(url='https://www.kathimerini.gr/', licence='all-rights-reserved; permission required', kind='links'),
    'news-naftemporiki': dict(url='https://www.naftemporiki.gr/', licence='all-rights-reserved; permission required', kind='links'),
    'news-efsyn': dict(url='https://www.efsyn.gr/', licence='all-rights-reserved; permission required', kind='links'),
    'mastodon': dict(url='https://mastodon.social/api/v1/timelines/public?local=true&limit=20', licence='author-specific; public visibility is not a reuse licence', kind='mastodon'),
    'gutenberg': dict(url='https://www.gutenberg.org/browse/languages/el', licence='Project Gutenberg terms; underlying work jurisdiction review required', kind='gutenberg'),
}


def source_catalog() -> dict[str, Record]:
    """Return seed metadata with conservative licence tags and >=1 second rates."""
    return {name: dict(row, interval=1.0, robots=True) for name, row in _CATALOG.items()}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class _PoliteHTTP:
    """All requests, including redirects/assets, pass the same per-origin gate."""
    def __init__(self, interval: float = 1.0, timeout: float = 30.0,
                 user_agent: str = USER_AGENT, limit: int = 16_000_000) -> None:
        import math
        if not math.isfinite(interval) or interval < 1:
            raise ValueError('web rate interval must be >=1 second')
        if not math.isfinite(timeout) or timeout <= 0 or limit <= 0:
            raise ValueError('web timeout and byte limit must be positive')
        self.interval, self.timeout, self.user_agent, self.limit = interval, timeout, user_agent, limit
        self._robots: dict[str, urllib.robotparser.RobotFileParser] = {}
        self._last: dict[str, float] = {}
        self._opener = urllib.request.build_opener(_NoRedirect())

    def _pace(self, origin: str, interval: float | None = None) -> None:
        wait = self._last.get(origin, -float('inf')) + (interval or self.interval) - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self._last[origin] = time.monotonic()

    def _request(self, url: str) -> Record:
        request = urllib.request.Request(url, headers={'User-Agent': self.user_agent, 'Accept-Encoding': 'identity'})
        try:
            response = self._opener.open(request, timeout=self.timeout)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            body = response.read(self.limit + 1)
            if len(body) > self.limit:
                raise ValueError('web response exceeds byte limit: ' + url)
            return dict(url=url, status=response.code, headers=dict(response.headers), body=body)

    def get(self, url: str) -> Record:
        for _ in range(10):
            parsed = urllib.parse.urlsplit(url)
            if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.username:
                raise ValueError('only credential-free HTTP(S) source URLs are supported')
            origin = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, '', '', ''))
            if origin not in self._robots:
                self._pace(origin)
                robots = self._request(origin + '/robots.txt')
                parser = urllib.robotparser.RobotFileParser(origin + '/robots.txt')
                if robots['status'] in (404, 410):
                    parser.parse([])
                elif robots['status'] == 200:
                    parser.parse(robots['body'].decode('utf-8', errors='replace').splitlines())
                else:
                    raise ValueError('robots unavailable; refusing capture: ' + origin)
                self._robots[origin] = parser
            parser = self._robots[origin]
            if not parser.can_fetch(self.user_agent, url):
                raise ValueError('robots disallows capture: ' + url)
            delay = max(self.interval, parser.crawl_delay(self.user_agent) or 0)
            rate = parser.request_rate(self.user_agent)
            if rate:
                delay = max(delay, rate.seconds / rate.requests)
            self._pace(origin, delay)
            result = self._request(url)
            location = next((v for k, v in result['headers'].items() if k.lower() == 'location'), None)
            if result['status'] in (301, 302, 303, 307, 308) and location:
                url = urllib.parse.urljoin(url, location)
                continue
            return result
        raise ValueError('too many source redirects')


class _Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href')
            if href:
                self.links.append(href)


def _links(body: bytes, url: str, kind: str) -> Iterator[str]:
    parser = _Links()
    parser.feed(body.decode('utf-8', errors='replace'))
    origin = urllib.parse.urlsplit(url)
    seen = {url}
    for link in parser.links:
        absolute = urllib.parse.urldefrag(urllib.parse.urljoin(url, link))[0]
        parts = urllib.parse.urlsplit(absolute)
        if parts.scheme not in ('http', 'https') or parts.netloc != origin.netloc or absolute in seen:
            continue
        path = urllib.parse.unquote(parts.path)
        if kind == 'wiki' and (not path.startswith('/wiki/') or ':' in path[6:]):
            continue
        if kind == 'gutenberg' and not path.startswith('/ebooks/'):
            continue
        if kind == 'links' and path in ('', '/'):
            continue
        seen.add(absolute)
        yield absolute


def mastodon_post_html(post: Record) -> str:
    """Render recorded public JSON as inert post HTML, with author and source link."""
    # Keep text only: remote markup must not introduce scripts, tracking or assets.
    parser = _PostText()
    parser.feed(str(post.get('content', '')))
    account = post.get('account') or {}
    author = html.escape(str(account.get('display_name') or account.get('acct') or ''))
    url = html.escape(str(post.get('url') or post.get('uri') or ''), quote=True)
    content = html.escape(''.join(parser.text))
    warning = html.escape(str(post.get('spoiler_text') or ''))
    return ('<!doctype html><html lang="el"><meta charset="utf-8"><title>Mastodon post</title>'
            '<style>body{font:20px/1.5 serif;margin:32px}p{white-space:pre-wrap}</style>'
            f'<body><h1>{author}</h1><p>{warning}</p><p>{content}</p><a href="{url}">Source</a></body></html>')


class _PostText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.text: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self._skip += 1
        if tag == 'br':
            self.text.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self._skip = max(0, self._skip - 1)
        if tag == 'p':
            self.text.append('\n')

    def handle_data(self, data):
        if not self._skip:
            self.text.append(data)


def source_pages(sources: Sequence[str], max_pages: int = 10, *,
                 category: str | None = None, mastodon_instance: str = 'https://mastodon.social',
                 client: _PoliteHTTP | None = None) -> Iterator[Record]:
    """Yield bounded seeds/articles; discovery fetches only when iteration needs it."""
    if max_pages < 1:
        raise ValueError('max_pages must be positive')
    client = client or _PoliteHTTP()
    names = [name for source in sources for name in
             (('news-kathimerini', 'news-naftemporiki', 'news-efsyn') if source == 'news' else (source,))]
    if not names or any(name not in _CATALOG for name in names):
        raise ValueError('unknown or empty web sources')
    # Round robin gives every selected source a seed before discovering article links.
    pending = deque(_source_pages([name], max_pages, category=category,
                                  mastodon_instance=mastodon_instance, client=client) for name in names)
    count = 0
    while pending and count < max_pages:
        iterator = pending.popleft()
        try:
            row = next(iterator)
        except StopIteration:
            continue
        yield row
        count += 1
        pending.append(iterator)


def _source_pages(sources: Sequence[str], max_pages: int, *, category: str | None,
                  mastodon_instance: str, client: _PoliteHTTP) -> Iterator[Record]:
    count = 0
    for name in sources:
        if name not in _CATALOG:
            raise ValueError('unknown web source: ' + name)
        spec = _CATALOG[name]
        url = spec['url']
        if name == 'wikisource' and category:
            url = 'https://el.wikisource.org/wiki/' + urllib.parse.quote('Κατηγορία:' + category)
        if name == 'mastodon':
            url = mastodon_instance.rstrip('/') + '/api/v1/timelines/public?local=true&limit=20'
            response = client.get(url)
            if response['status'] != 200:
                raise ValueError('Mastodon timeline HTTP ' + str(response['status']))
            for post in json.loads(response['body']):
                if post.get('visibility') != 'public':
                    continue
                yield dict(url=post.get('url') or post.get('uri'), html=mastodon_post_html(post),
                           licence=spec['licence'], source=name, api_url=url,
                           source_json=post, api_status=response['status'], api_final_url=response['url'])
                count += 1
                if count >= max_pages:
                    return
            continue
        yield dict(url=url, licence=spec['licence'], source=name)
        count += 1
        if count >= max_pages:
            return
        if spec['kind'] == 'random':
            while count < max_pages:
                yield dict(url=url, licence=spec['licence'], source=name)
                count += 1
            return
        response = client.get(url)
        if response['status'] != 200:
            raise ValueError('source discovery HTTP ' + str(response['status']))
        for link in _links(response['body'], response['url'], spec['kind']):
            yield dict(url=link, licence=spec['licence'], source=name)
            count += 1
            if count >= max_pages:
                return
