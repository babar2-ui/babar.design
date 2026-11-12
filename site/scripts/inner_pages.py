"""Work, Insights and FAQ pages in the studio language. Same words, links, images and alts.

Work: light filter pills, the homepage case-card treatment (image + title; hover blurs the image
and shows tags + "View case study"), blue CTA panel. The category line stays in the card as
screen-reader text so the industry filter (assets/site.js, which reads "INDUSTRY ·") keeps working.
Insights: category pill + read time, homepage-style titles.
FAQ: one block per topic (sticky topic heading on the left, numbered rows on the right)."""
import re
import work2

CARD = re.compile(r'<(a href="[^"]*"|div) style="display: grid; grid-template-columns: minmax\(0px, 1fr\) minmax\(0px, 1fr\); gap: 40px; align-items: stretch;">')
ARROW_SPAN = re.compile(r'\s*<span[^>]*>→</span>')


def _sec(h, label):
    m = re.search(r'<section[^>]*data-screen-label="' + re.escape(label) + '"', h)
    return m.start(), h.index("</section>", m.start()) + len("</section>")


def _cta(h):
    a, b = _sec(h, "CTA")
    s = h[a:b]
    h2 = re.search(r"<h2[^>]*>(.*?)</h2>", s).group(1)
    p = re.search(r"<p[^>]*>(.*?)</p>", s, re.S)
    u, t = re.search(r'<a href="([^"]*)" class="scp0"[^>]*>(.*?)</a>', s).groups()
    w = h2.split(" ")
    head = " ".join(w[:-1]) + f' <span class="axs-dim">{w[-1]}</span>'
    new = (f'<section class="axs axs-cta" data-screen-label="CTA"><div class="axs-in"><h2 class="axs-ch">{head}</h2>'
           + (f'<p class="axs-cp">{p.group(1)}</p>' if p else "")
           + f'<div class="axs-btns"><a href="{u}" class="axs-btn is-solid">{t}</a></div></div></section>')
    return h[:a] + new + h[b:]


def work(h):
    a, b = _sec(h, "Case list")
    sec = h[a:b]
    starts = [m.start() for m in CARD.finditer(sec)] + [sec.rindex("</section>")]
    out = sec[:starts[0]]
    for i in range(len(starts) - 1):
        c = sec[starts[i]:starts[i + 1]]
        cat = work2.CAT.search(c)
        assert cat, c[:200]
        catxt = cat.group(1)
        c = c[:cat.start()] + c[cat.end():]
        tags = "".join(f'<span class="wkx-tag">{t.strip()}</span>' for t in catxt.split("·"))
        linked = c.startswith("<a ")
        ov = f'<div class="wkx-ov" aria-hidden="true"><div class="wkx-tags">{tags}</div>{work2.VIEW if linked else ""}</div>'
        r = c.index('class="rs-case"')
        img_end = c.index("</div>", c.index("<img", r)) + len("</div>")
        c = c[:img_end] + ov + c[img_end:]
        c = ARROW_SPAN.sub("", c)
        open_end = c.index(">") + 1
        c = c[:open_end - 1] + ' class="wkx-card wpx-card">' + f'<span class="ds-sr wpx-cat">{catxt}</span>' + c[open_end:]
        out += c
    out += sec[starts[-1]:]
    out = out.replace('<section class="dsi"', '<section class="dsi wkx wpx"', 1)
    h = h[:a] + out + h[b:]
    return _cta(h)


META = re.compile(r'<div style="font-size: 12px; color: rgb\(138, 138, 132\);">([^<·]+?) · ([^<]+)</div>')


def insights(h):
    a, b = _sec(h, "Articles")
    s = h[a:b]
    s = META.sub(lambda m: f'<div class="rdx-meta"><span class="blx-cat">{m.group(1)}</span><span class="blx-read">{m.group(2)}</span></div>', s)
    s = s.replace('<div style="font-size: 20px;', '<div class="rdx-t" style="font-size: 20px;')
    s = s.replace('<section class="dsi"', '<section class="dsi inx"', 1)
    return h[:a] + s + h[b:]


def faq(h):
    a, b = _sec(h, "FAQ list")
    s = re.sub(r' style="[^"]*"', "", h[a:b])
    parts = re.split(r"<h2>(.*?)</h2>", s)
    groups = []
    for gi in range(1, len(parts), 2):
        title, body = parts[gi], parts[gi + 1]
        rows = re.findall(r"<details( open=\"\")?>\s*<summary>(?:\s*<span>\s*</span>)?\s*<span>(.*?)</span>\s*<span class=\"om-plus\">\+</span></summary>(.*?)</details>", body, re.S)
        assert rows, title
        items = "".join(
            f'<details class="fqx-row"{" open" if (gi == 1 and k == 0) else ""}><summary class="fqx-q">'
            f'<span class="fqx-no" aria-hidden="true">/{k + 1:02d}</span><span class="fqx-qt">{q}</span>'
            f'<span class="fqx-pm" aria-hidden="true"></span></summary><div class="fqx-a fqp-a">{ans.strip()}</div></details>'
            for k, (_, q, ans) in enumerate(rows))
        groups.append(f'<div class="fqp-group"><div class="fqp-hd"><span class="pr-tag">/ {gi // 2 + 1:02d}</span>'
                      f'<h2 class="fqp-h">{title}</h2></div><div class="fqx-list">{items}</div></div>')
    new = f'<section class="fqx fqp" data-screen-label="FAQ list"><div class="fqp-in">{"".join(groups)}</div></section>'
    return h[:a] + new + h[b:]


def place(h, rel):
    return {"work": work, "insights": insights, "faq": faq}[rel](h)
