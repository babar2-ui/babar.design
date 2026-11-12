"""Blog article pages (insights/<slug>/) in the studio language. Same words, links and images.

  hero      no colour panel: breadcrumb, category / read time / date chips, headline, byline
  cover     wide rounded image
  body      "On this page" list from the section headings (sticky on wide screens) + the article;
            the article keeps its own markup, rx.css restyles it
  bio       author card
  related   "Keep reading" cards
  CTA       the article's closing line + "Let’s talk" become the blue panel used on every page
Works for the original articles and for the ones added in the admin (same markup, site/scripts/cms.py)."""
import re

TOC_JS = ("<script>(function(){var L=[].slice.call(document.querySelectorAll('.atx-toc a'));if(!L.length||!('IntersectionObserver' in window))return;"
          "var M={};L.forEach(function(a){M[a.getAttribute('href').slice(1)]=a});"
          "var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){L.forEach(function(a){a.classList.remove('is-on')});"
          "var a=M[e.target.id];if(a)a.classList.add('is-on')}})},{rootMargin:'0px 0px -70% 0px'});"
          "Object.keys(M).forEach(function(id){var t=document.getElementById(id);if(t)io.observe(t)})})();</script>")


def _sec(h, label):
    a = h.index(f'data-screen-label="{label}"')
    a = h.rindex("<section", 0, a)
    b = h.index("</section>", a) + len("</section>")
    return a, b


def _nostyle(s):
    return re.sub(r' style="[^"]*"', "", s)


def hero(s):
    crumb = _nostyle(re.search(r'<nav aria-label="Breadcrumb".*?</nav>', s, re.S).group(0))
    pill = re.search(r'<div class="ds-pill"[^>]*>(.*?)</div>', s, re.S).group(1).strip()
    parts = [x.strip() for x in re.sub(r"^/\s*", "", pill).split("·") if x.strip()]
    chips = f'<span class="atx-cat">{parts[0]}</span>' + "".join(f"<span>{x}</span>" for x in parts[1:])
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S).group(1)
    by = _nostyle(re.search(r'<div class="byline".*?</div>', s, re.S).group(0)).replace('class="byline"', 'class="byline atx-by"', 1)
    return (f'<section class="dsi atx-hero" data-screen-label="Article hero"><div class="atx-in">{crumb}'
            f'<div class="ds-pill atx-meta">{chips}</div><h1 class="atx-h1">{h1}</h1>{by}</div></section>')


def cover(s):
    img = re.search(r"<img [^>]*>", s).group(0)
    img = re.sub(r' style="[^"]*"', "", img)
    img = re.sub(r'sizes="[^"]*"', 'sizes="(max-width: 1099px) 92vw, 1100px"', img)
    return f'<section class="dsi atx-cover" data-screen-label="Article cover"><div class="atx-in"><figure class="atx-fig">{img}</figure></div></section>'


CTA_DIV = re.compile(r'<div style="margin-top: 60px; border-top: 1px solid rgb\(34, 34, 32\);[^"]*"><span[^>]*>(.*?)</span>'
                     r'<a href="([^"]*)" class="scp0"[^>]*>(.*?)</a></div>', re.S)


def body(s):
    inner = s[s.index(">") + 1:s.rindex("</section>")]
    m = CTA_DIV.search(inner)
    cta = None
    if m:
        cta = m.groups()
        inner = inner[:m.start()] + inner[m.end():]
    heads = re.findall(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', inner, re.S)
    toc = ""
    if len(heads) >= 2:
        items = "".join(f'<li><a href="#{i}">{re.sub(r"<[^>]+>", "", t).strip()}</a></li>' for i, t in heads)
        toc = f'<aside class="atx-toc" aria-label="On this page"><span class="pr-tag">/ On this page</span><ol>{items}</ol></aside>'
    sec = (f'<section class="dsi atx-main{"" if toc else " no-toc"}" data-screen-label="Article body"><div class="atx-in atx-grid">{toc}'
           f'<div class="atx-body">{inner}</div></div>{TOC_JS if toc else ""}</section>')
    return sec, cta


def bio(s):
    img = re.search(r"<img [^>]*>", s).group(0)
    img = re.sub(r' style="[^"]*"', "", img)
    name = re.search(r'<a href="[^"]*" rel="author">.*?</a>', s, re.S).group(0)
    p = _nostyle(re.search(r"<p[^>]*>.*?</p>", s, re.S).group(0)).replace("<p>", '<p class="atx-bp">', 1)
    return (f'<section class="dsi atx-bio" data-screen-label="Author bio"><div class="atx-in"><div class="atx-card">'
            f'<figure class="atx-ava">{img}</figure><div class="atx-bt"><span class="pr-tag">/ Written by</span>'
            f'<div class="atx-bn">{name}</div>{p}</div></div></div></section>')


NOARROW = re.compile(r"\s*→\s*$")


def related(s):
    tag = re.search(r'<div class="ds-pill"[^>]*>(.*?)</div>', s).group(1).strip()
    cards = re.findall(r'<a href="([^"]*)"[^>]*>\s*<div[^>]*>(.*?)</div>\s*<div[^>]*>(.*?)</div>\s*<span[^>]*>(.*?)</span>\s*</a>', s, re.S)
    out = "".join(
        f'<a class="atx-rc" href="{u}"><span class="atx-rm">{meta}</span><span class="atx-rt">{t.strip()}</span>'
        f'<span class="atx-rl">{NOARROW.sub("", r).strip()}</span></a>' for u, meta, t, r in cards)
    return (f'<section class="dsi atx-rel" data-screen-label="Related articles"><div class="atx-in">'
            f'<div class="atx-rh"><span class="pr-tag">{tag}</span></div><div class="atx-rg">{out}</div></div></section>')


def cta_panel(c):
    line, url, label = c
    w = line.strip().split(" ")
    head = " ".join(w[:-1]) + f' <span class="axs-dim">{w[-1]}</span>'
    return (f'<section class="axs axs-cta" data-screen-label="CTA"><div class="axs-in"><h2 class="axs-ch">{head}</h2>'
            f'<div class="axs-btns"><a href="{url}" class="axs-btn is-solid">{label}</a></div></div></section>')


def place(h):
    a, b = _sec(h, "Article hero")
    h = h[:a] + hero(h[a:b]) + h[b:]
    a, b = _sec(h, "Article cover")
    h = h[:a] + cover(h[a:b]) + h[b:]
    a, b = _sec(h, "Article body")
    new, cta = body(h[a:b])
    h = h[:a] + new + h[b:]
    a, b = _sec(h, "Author bio")
    h = h[:a] + bio(h[a:b]) + h[b:]
    a, b = _sec(h, "Related articles")
    h = h[:a] + related(h[a:b]) + (cta_panel(cta) if cta else "") + h[b:]
    return h.replace('<body class="ds rx">', '<body class="ds rx rx-art">', 1)
