"""Homepage Work: move the case-study grid straight after Services and give it a heading row
("Featured work" with a project count, a "( Case Studies )" label and an "All work" link).
The phrases already exist on the site; the cards themselves are untouched."""
import re

ARROW = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>'


CAT = re.compile(r'<div style="font-size: 12px; color: rgb\(138, 138, 132\); margin-bottom: 14px;">\s*<span class="sc-interp">(.*?)</span></div>\s*')
VIEW = '<span class="wkx-view">View case study <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg></span>'


def cardify(m):
    """Card = image + title. The category line becomes tag pills on the image (shown on hover
    with a blur); description and stats stay in the page for search engines and screen readers
    but are visually hidden."""
    c = m.group(0)
    cat = CAT.search(c)
    assert cat, c[:200]
    c = c[:cat.start()] + c[cat.end():]
    tags = "".join(f'<span class="wkx-tag">{t.strip()}</span>' for t in cat.group(1).split("\u00b7"))
    linked = c.startswith("<a ")
    ov = f'<div class="wkx-ov"><div class="wkx-tags">{tags}</div>{VIEW if linked else ""}</div>'
    r = c.index('class="rs-case"')
    img_end = c.index("</div>", c.index("<img", r)) + len("</div>")
    c = c[:img_end] + ov + c[img_end:]
    return c.replace('class="om-case"', 'class="om-case wkx-card"', 1)


def place(h, p):
    a = h.index('<section class="dsi" id="work" data-screen-label="Case studies"')
    b = h.index("</section>", a) + len("</section>")
    sec = h[a:b]
    # homepage shows the first 6 projects; the rest stay on /work/
    starts = [m.start() for m in re.finditer(r'<(?:a href="[^"]*"|div) class="om-case"', sec)]
    if len(starts) > 6:
        sec = sec[:starts[6]] + sec[sec.rindex("</section>"):]
    n = len(re.findall(r'class="om-case"', sec))
    head = (f'<div class="wkx-hd"><h2 class="wkx-h">Featured work<sup class="wkx-n" aria-label="{n} projects">{n}</sup></h2>'
            f'<span class="wkx-k">( Case Studies )</span>'
            f'<a class="wkx-all" href="{p}work/index.html">All work {ARROW}</a></div>')
    sec = re.sub(r'<(a href="[^"]*"|div) class="om-case".*?(?=<(?:a href="[^"]*"|div) class="om-case"|\s*</section>)', cardify, sec, flags=re.S)
    open_end = sec.index(">") + 1
    sec = sec[:open_end].replace('class="dsi"', 'class="dsi wkx"', 1) + head + sec[open_end:]
    h = h[:a] + h[b:]
    s = h.index('<section id="services" data-screen-label="Services"')
    s_end = h.index("</section>", s) + len("</section>")
    return h[:s_end] + "\n  " + sec + h[s_end:]
