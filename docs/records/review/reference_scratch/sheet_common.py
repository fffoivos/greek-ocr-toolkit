
def toolpills(html):
    import re as _re
    def rep(m):
        tool=m.group(1); return m.group(0).replace('</div>', f'<span class="toolpill {tool}">tool: {tool}</span></div>',1)
    return _re.sub(r'<div class="card"[^>]*data-tool="(KEEP|DROP|UNCERTAIN)"[^>]*><div class="lid">[^<]*(?:<[^>]+>[^<]*)*?</div>', rep, html)
