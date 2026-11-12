"""Homepage Testimonials, studio layout: light ground split into three columns by dashed lines;
the heading, intro and button sit at the top of the first column and the review cards are
staggered down the columns. Each card: square portrait, topic label top right, name, role,
then the quote. Rebuilt from the existing cards (same quotes, names, roles, portraits and alts).
Dropped: the decorative pull-quote (an aria-hidden excerpt of the quote itself) and the big
quote-mark glyph."""
import re

COLS = [[2, 5], [0, 3, 6, 8], [1, 4, 7, 9]]  # first column also holds the heading


def section(old):
    tag = re.search(r'<span class="pr-tag">(.*?)</span>', old).group(1)
    h2 = re.search(r'<h2 class="tm-h">(.*?)</h2>', old).group(1)
    intro = re.search(r'<div class="tm-intro"><p>(.*?)</p>', old, re.S).group(1)
    cta = re.search(r'(<a class="pr-cta" href="[^"]*">.*?</a>)', old, re.S).group(1)
    figs = re.findall(r'<figure class="tm-card">(.*?)</figure>', old, re.S)
    assert len(figs) == 10, len(figs)
    cards = []
    for f in figs:
        topic = re.search(r'<span class="tm-tag">(.*?)</span>', f).group(1).strip()
        quote = re.search(r'<blockquote class="tm-q"[^>]*>(.*?)</blockquote>', f, re.S).group(1)
        av = re.search(r'<span class="tm-av">(.*?)</span>', f, re.S).group(1)
        name = re.search(r'<span class="tm-name"[^>]*>(.*?)</span>', f).group(1)
        role = re.search(r'<span class="tm-role"[^>]*>(.*?)</span>', f).group(1)
        cards.append(f'<figure class="tmx-card"><div class="tmx-top"><span class="tmx-av">{av}</span><span class="tmx-topic">{topic}</span></div>'
                     f'<figcaption class="tmx-who"><span class="tmx-name">{name}</span><span class="tmx-role">{role}</span></figcaption>'
                     f'<blockquote class="tmx-q">{quote}</blockquote></figure>')
    w = h2.split(" ")
    head = " ".join(w[:-1]) + f' <span class="tmx-dim">{w[-1]}</span>' if len(w) > 1 else h2
    hd = f'<div class="tmx-hd"><span class="pr-tag">{tag}</span><h2 class="tmx-h">{head}</h2><p class="tmx-intro">{intro}</p>{cta}</div>'
    cols = []
    for i, idx in enumerate(COLS):
        inner = (hd if i == 0 else "") + "".join(cards[k] for k in idx)
        cols.append(f'<div class="tmx-col tmx-c{i + 1}">{inner}</div>')
    return f'<section data-screen-label="Testimonials" class="tmx"><div class="tmx-in">{"".join(cols)}</div></section>'


def place(h, p):
    a = h.index('<section data-screen-label="Testimonials" class="tm">')
    b = h.index("</section>", a) + len("</section>")
    return h[:a] + section(h[a:b]) + h[b:]
