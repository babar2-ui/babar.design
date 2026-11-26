"""Homepage "Statement": the short line under About becomes a minimal blue call-to-action band.
Same words; the two buttons are the hero's own ("Let's Work Together", "View My Work").
Set into the blue: a faint grid and the BABAR wordmark as a large outline, drifting slowly."""
import re


def place(h, p, src_index):
    m = re.search(r'<section class="dsi" data-screen-label="Statement"[^>]*>\s*<p[^>]*>(.*?)</p>\s*</section>', h, re.S)
    assert m, "Statement section not found"
    text = m.group(1).strip()
    src = src_index.read_text(encoding="utf-8")
    logo = re.search(r'<div style="font-size: 64px[^"]*">(<svg.*?</svg>)</div>', src, re.S).group(1)
    logo = re.sub(r' (?:style|role|aria-label|class)="[^"]*"', "", logo).replace("<svg ", '<svg aria-hidden="true" focusable="false" ', 1)
    new = (f'<section class="stx" data-screen-label="Statement"><div class="stx-bg" aria-hidden="true"><div class="stx-grid"></div>'
           f'<div class="stx-mark">{logo}</div></div><div class="stx-in">'
           f'<p class="stx-p">{text}</p><div class="stx-btns">'
           f'<a href="{p}contact/index.html" class="stx-btn is-solid">Let\'s Work Together</a>'
           f'<a href="{p}work/index.html" class="stx-btn">View My Work</a></div></div></section>')
    return h[:m.start()] + new + h[m.end():]
