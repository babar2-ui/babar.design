"""Homepage "Statement": the short line under About becomes a minimal blue call-to-action band.
Same words; the two buttons are the hero's own ("Let's Work Together", "View My Work").
Set into the blue: a faint grid that fades out towards the edges."""
import re


def place(h, p, src_index):
    m = re.search(r'<section class="dsi" data-screen-label="Statement"[^>]*>\s*<p[^>]*>(.*?)</p>\s*</section>', h, re.S)
    assert m, "Statement section not found"
    text = m.group(1).strip()
    new = (f'<section class="stx" data-screen-label="Statement"><div class="stx-bg" aria-hidden="true"><div class="stx-grid"></div></div><div class="stx-in">'
           f'<p class="stx-p">{text}</p><div class="stx-btns">'
           f'<a href="{p}contact/index.html" class="stx-btn is-solid">Let\'s Work Together</a>'
           f'<a href="{p}work/index.html" class="stx-btn">View My Work</a></div></div></section>')
    return h[:m.start()] + new + h[m.end():]
