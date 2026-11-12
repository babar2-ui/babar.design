"""Client strip before Pricing: the companies named in the testimonials, shown as plain grey
wordmarks in a slow auto-scrolling row with faded edges (no one else's logo artwork is
recreated). Swap the names for real logo files once the owner provides them."""

CLIENTS = ["dot.it", "Insyteful", "Mentoris.AI", "Hanna Health", "WEMASY"]


def section():
    one = "".join(f'<li class="lgx-i">{c}</li>' for c in CLIENTS)
    return ('<section class="lgx" aria-label="Clients"><div class="lgx-mask">'
            f'<ul class="lgx-track">{one}</ul>'
            f'<ul class="lgx-track" aria-hidden="true">{one}</ul>'
            f'<ul class="lgx-track" aria-hidden="true">{one}</ul>'
            '</div></section>')


def place(h, p):
    a = h.index('<section id="pricing" data-screen-label="Pricing"')
    return h[:a] + section() + "\n  " + h[a:]
