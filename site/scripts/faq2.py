"""Homepage FAQ + Contact in the studio language.
FAQ: light ground; a sticky heading column on the left (label, "Answers before you ask." from
the FAQ page, Book a call) and numbered question rows on the right (native <details>, first open).
Contact: dark ground with column lines; heading, intro, email/phone and socials on the left,
the unchanged Netlify form in a square-cornered panel on the right."""
import re

ARROW = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>'


def faq(old, p):
    rows = re.findall(r'<details( open="")?[^>]*>\s*<summary[^>]*><span[^>]*>(.*?)</span>.*?</summary>\s*<p[^>]*>(.*?)</p>\s*</details>', old, re.S)
    assert len(rows) == 8, len(rows)
    items = "".join(
        f'<details class="fqx-row"{" open" if i == 0 else ""}><summary class="fqx-q"><span class="fqx-no" aria-hidden="true">/{i + 1:02d}</span>'
        f'<span class="fqx-qt">{q}</span><span class="fqx-pm" aria-hidden="true"></span></summary><p class="fqx-a">{a}</p></details>'
        for i, (_, q, a) in enumerate(rows))
    return (f'<section class="fqx" id="faq" data-screen-label="FAQ"><div class="fqx-in">'
            f'<div class="fqx-hd"><span class="pr-tag">/ {len(rows):02d} QUESTIONS / FAQ</span><h2 class="fqx-h">Answers before <span class="fqx-dim">you ask.</span></h2>'
            f'<a class="fqx-cta" href="{p}contact/index.html">Book a call {ARROW}</a></div>'
            f'<div class="fqx-list">{items}</div></div></section>')


def contact(old):
    h2 = re.search(r"<h2[^>]*>(.*?)</h2>", old).group(1)
    intro = re.search(r"</h2>\s*<p[^>]*>(.*?)</p>", old, re.S).group(1)
    mail = re.search(r'<a href="(mailto:[^"]*)"[^>]*><span class="sc-interp">(.*?)</span></a>', old)
    tel = re.search(r'<a href="(tel:[^"]*)"[^>]*><span class="sc-interp">(.*?)</span></a>', old)
    socials = re.findall(r'(<a href="https://[^"]*" target="_blank" aria-label="[^"]+") class="scp1" style="[^"]*">(<svg.*?</svg>)</a>', old, re.S)
    form = re.search(r'<form class="om-form".*?</form>', old, re.S).group(0)
    w = h2.split(" ")
    head = " ".join(w[:-2]) + f' <span class="ctx-dim">{" ".join(w[-2:])}</span>'
    soc = "".join(f'{a} class="ctx-soc">{svg}</a>' for a, svg in socials)
    return (f'<section class="ctx" id="contact" data-screen-label="Contact"><div class="ctx-in">'
            f'<div class="ctx-l"><h2 class="ctx-h">{head}</h2><p class="ctx-intro">{intro}</p>'
            f'<a class="ctx-big" href="{mail.group(1)}">{mail.group(2)} {ARROW}</a>'
            f'<a class="ctx-big" href="{tel.group(1)}">{tel.group(2)} {ARROW}</a>'
            f'<div class="ctx-socs">{soc}</div></div>'
            f'<div class="ctx-r">{form}</div></div></section>')


def place(h, p):
    a = h.index('<section class="dsi" id="faq" data-screen-label="FAQ"')
    b = h.index("</section>", a) + len("</section>")
    h = h[:a] + faq(h[a:b], p) + h[b:]
    a = h.index('<section class="dsc" id="contact" data-screen-label="Contact"')
    b = h.index("</section>", a) + len("</section>")
    return h[:a] + contact(h[a:b]) + h[b:]
