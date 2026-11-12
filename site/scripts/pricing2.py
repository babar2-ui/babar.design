"""Homepage Pricing in the studio language: dark ground with column lines, header row
(label | two-tone heading | intro), three square-cornered plan cards (number + icon on top,
name, who it is for, big price, mono terms line, diamond-bullet list, full-width button; the
recommended plan in blue), then the four guarantees as a mono strip. Same words as before."""
import re

ARROW = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>'
SVG = re.compile(r"<svg.*?</svg>", re.S)


def section(old):
    tag = re.search(r'<span class="pr-tag">(.*?)</span>', old).group(1)
    h2 = re.search(r'<h2 class="pc-h">(.*?)</h2>', old).group(1)
    intro = re.search(r'<p class="pc-intro">(.*?)</p>', old, re.S).group(1)
    w = h2.split(" ")
    head = " ".join(w[:-1]) + f' <span class="pcx-dim">{w[-1]}</span>' if len(w) > 1 else h2
    cards = []
    for i, c in enumerate(re.findall(r'<article class="pc-card[^"]*">.*?</article>', old, re.S)):
        rec = "is-dark" in c[:40]
        badge = re.search(r'<span class="pc-badge">(.*?)</span>', c)
        ic = re.search(r'<span class="pc-ic" aria-hidden="true">(<svg.*?</svg>)</span>', c, re.S).group(1)
        name = re.search(r'<h3 class="pc-name">(.*?)</h3>', c).group(1)
        who = re.search(r'<p class="pc-for">(.*?)</p>', c).group(1)
        price = re.search(r'<div class="pc-price">(.*?)</div>', c, re.S).group(1).replace('class="pc-', 'class="pcx-')
        note = re.findall(r'<span>(.*?)</span>', re.search(r'<div class="pc-note">(.*?)</div>', c, re.S).group(1))
        items = SVG.sub("", re.search(r'<ul class="pc-list">(.*?)</ul>', c, re.S).group(1))
        cta = re.search(r'<a class="pc-cta" href="([^"]*)">(.*?)</a>', c)
        cards.append(
            f'<article class="pcx-card{" is-rec" if rec else ""}">'
            f'<div class="pcx-top"><span class="pcx-no" aria-hidden="true">/0{i + 1}</span>'
            + (f'<span class="pcx-badge">{badge.group(1)}</span>' if badge else "")
            + f'<span class="pcx-ic" aria-hidden="true">{ic}</span></div>'
            f'<h3 class="pcx-name">{name}</h3><p class="pcx-for">{who}</p>'
            f'<div class="pcx-price">{price}</div>'
            f'<div class="pcx-note">{"<i></i>".join(f"<span>{n}</span>" for n in note)}</div>'
            f'<ul class="pcx-list">{items}</ul>'
            f'<a class="pcx-cta" href="{cta.group(1)}">{cta.group(2)} {ARROW}</a></article>')
    assert len(cards) == 3
    strip = SVG.sub("", re.search(r'<ul class="pc-strip">(.*?)</ul>', old, re.S).group(1))
    return f'''<section id="pricing" data-screen-label="Pricing" class="pcx">
    <div class="pcx-in">
      <div class="pcx-hd"><span class="pr-tag">{tag}</span><h2 class="pcx-h">{head}</h2><p class="pcx-intro">{intro}</p></div>
      <div class="pcx-grid">{"".join(cards)}</div>
      <ul class="pcx-strip">{strip}</ul>
    </div>
  </section>'''


def place(h, p):
    a = h.index('<section id="pricing" data-screen-label="Pricing" class="pc">')
    b = h.index("</section>", a) + len("</section>")
    return h[:a] + section(h[a:b]) + h[b:]
