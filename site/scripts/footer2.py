"""Site-wide footer, clean and minimal in the studio language: dark ground; logo, the
"Let's Work Together" link and the availability line on the left; the four existing columns
(Sitemap, Services, Contact, Availability) on the right with mono labels; a thin rule, then the
social links (the same five as the homepage contact block) and the copyright line.
Every word and link of the old footer is kept."""
import re

ARROW = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>'
_SOCIALS = None


def socials(src_index):
    global _SOCIALS
    if _SOCIALS is None:
        h = src_index.read_text(encoding="utf-8")
        found = re.findall(r'<a (href="https://[^"]*" target="_blank" aria-label="[^"]+")[^>]*>(<svg.*?</svg>)</a>', h, re.S)
        seen, out = set(), []
        for a, svg in found:
            if a not in seen:
                seen.add(a); out.append(f'<a {a} rel="noopener" class="ftx-soc">{svg}</a>')
        _SOCIALS = "".join(out[:5])
    return _SOCIALS


def build(h, p, src_index):
    a = h.index("<footer")
    b = h.index("</footer>", a) + len("</footer>")
    old = h[a:b]
    label = ' data-screen-label="Footer"' if 'data-screen-label="Footer"' in old[:200] else ""
    big = re.search(r'<a class="rx-big" href="([^"]*)">(.*?)</a>', old)
    cols = re.findall(r'<div><div style="color: rgb\(138, 138, 132\); margin-bottom: 16px;">(.*?)</div>(.*?)</div>(?=\s*<div><div style="color|\s*</div>\s*<div style="display: flex; justify-content)', old, re.S)
    assert len(cols) == 4, (len(cols), old[:400])
    logo = re.search(r'<div style="font-size: 64px[^"]*">(<svg.*?</svg>)</div>', old, re.S).group(1)
    copy = re.search(r'<div style="font-size: 12px; color: rgb\(138, 138, 132\);">(.*?)</div>', old).group(1)
    colhtml = ""
    for lab, body in cols:
        links = re.findall(r'<a href="([^"]*)"[^>]*>(.*?)</a>', body, re.S)
        if links:
            inner = "".join(f'<li><a href="{u}">{t}</a></li>' for u, t in links)
            colhtml += f'<div class="ftx-col"><span class="ftx-k">{lab}</span><ul>{inner}</ul></div>'
        else:
            txt = re.sub(r"<[^>]+>", "", body).strip()
            colhtml += f'<div class="ftx-col"><span class="ftx-k">{lab}</span><p class="ftx-avail"><i aria-hidden="true"></i>{txt}</p></div>'
    new = (f'<footer class="ftx"{label}><div class="ftx-in">'
           f'<div class="ftx-top"><div class="ftx-brand"><a class="ftx-logo" href="{p}index.html" aria-label="Home">{logo}</a>'
           f'<a class="rx-big ftx-cta" href="{big.group(1)}">{big.group(2)} {ARROW}</a></div>'
           f'<nav class="ftx-cols" aria-label="Footer">{colhtml}</nav></div>'
           f'<div class="ftx-bot"><div class="ftx-socs">{socials(src_index)}</div><p class="ftx-copy">{copy}</p></div>'
           f'</div></footer>')
    return h[:a] + new + h[b:]
