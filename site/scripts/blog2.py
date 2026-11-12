"""Homepage Insights in the studio language: header row (label | two-tone heading | intro +
link), then three article cards: rounded image, a grey category pill + mono date and reading
time, and the title. Same words, links, images and alts as before."""
import re

ARROW = '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>'


def section(old):
    tag = re.search(r'<span class="pr-tag">(.*?)</span>', old).group(1)
    h2 = re.search(r'<h2 class="bl-h">(.*?)</h2>', old).group(1)
    intro = re.search(r'<div class="bl-intro"><p>(.*?)</p>', old, re.S).group(1)
    allx = re.search(r'<a class="pr-cta" href="([^"]*)">(.*?) <i', old, re.S)
    w = h2.split(" ")
    head = " ".join(w[:-1]) + f' <span class="blx-dim">{w[-1]}</span>' if len(w) > 1 else h2
    cards = []
    for href, body in re.findall(r'<a class="bl-card" href="([^"]*)">(.*?)</a>', old, re.S):
        img = re.search(r"<img [^>]*>", body).group(0)
        cat = re.search(r'<span class="bl-cat">(.*?)</span>', body).group(1)
        date = re.search(r'(<time class="bl-date"[^>]*>.*?</time>)', body).group(1).replace('class="bl-date"', 'class="blx-date"')
        title = re.search(r'<h3 class="bl-t">(.*?)</h3>', body, re.S).group(1)
        topic, _, read = cat.partition(", ")
        cards.append(f'<a class="blx-card" href="{href}"><div class="blx-media">{img}<span class="rdx-ov"><span class="rdx-btn">Read article {ARROW}</span></span></div>'
                     f'<div class="blx-meta"><span class="blx-cat">{topic}</span>{date}'
                     + (f'<span class="blx-read">{read}</span>' if read else "")
                     + f'</div><h3 class="blx-t">{title}</h3></a>')
    assert len(cards) == 3
    return f'''<section data-screen-label="Insights" class="blx">
    <div class="blx-in">
      <div class="blx-hd"><span class="pr-tag">{tag}</span><h2 class="blx-h">{head}</h2>
        <div class="blx-intro"><p>{intro}</p><a class="blx-all" href="{allx.group(1)}">{allx.group(2)} {ARROW}</a></div></div>
      <div class="blx-grid">{"".join(cards)}</div>
    </div>
  </section>'''


def place(h, p):
    a = h.index('<section data-screen-label="Insights" class="bl">')
    b = h.index("</section>", a) + len("</section>")
    return h[:a] + section(h[a:b]) + h[b:]
