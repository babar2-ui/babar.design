"""About page in the studio language (same as the homepage). Every section below the hero is
rebuilt from its own markup: same words, images, alts and links; only layout and classes change.
Sections alternate light / dark like the homepage; the CTA becomes a blue panel."""
import re


def _sec(h, label):
    a = h.index(f'data-screen-label="{label}"')
    a = h.rindex("<section", 0, a)
    b = h.index("</section>", a) + len("</section>")
    return a, b, re.sub(r' style="[^"]*"', "", h[a:b])


def _txt(s):
    return re.sub(r"\s+", " ", s).strip()


def _imgs(s):
    return re.findall(r"<img [^>]*>", s)


def _pill(s):
    return re.search(r'<div class="ds-pill">(.*?)</div>', s).group(1)


def _hd(tag, lead, dark=False, extra=""):
    return (f'<div class="axs-hd"><span class="pr-tag">{tag}</span>'
            f'<p class="axs-lead">{lead}</p>{extra}</div>')


def story(s):
    img = _imgs(s)[0]
    ps = re.findall(r"<p>(.*?)</p>", s, re.S)
    stats = re.findall(r"<div><div>([^<]*)</div><div>([^<]*)</div></div>", s)
    st = "".join(f'<div class="axs-stat"><dt>{b}</dt><dd>{a}</dd></div>' for a, b in stats)
    return (f'<section class="axs axs-light axs-story" data-screen-label="My story"><div class="axs-in">'
            f'<figure class="axs-photo">{img}</figure>'
            f'<div class="axs-body"><span class="pr-tag">{_pill(s)}</span><p class="axs-lead">{ps[0]}</p>'
            + "".join(f'<p class="axs-p">{p}</p>' for p in ps[1:])
            + f'<dl class="axs-stats">{st}</dl></div></div></section>')


def what(s):
    lead = re.search(r"<p>(.*?)</p>", s, re.S).group(1)
    img = _imgs(s)[0]
    items = re.findall(r"<div><div>([^<]*)</div><p>(.*?)</p></div>", s, re.S)
    cards = "".join(f'<article class="axs-card"><span class="axs-no" aria-hidden="true">/{i + 1:02d}</span>'
                    f'<h3 class="axs-ct">{t}</h3><p class="axs-cd">{d}</p></article>' for i, (t, d) in enumerate(items))
    return (f'<section class="axs axs-dark" data-screen-label="What I do"><div class="axs-in axs-stack">'
            + _hd(_pill(s), lead)
            + f'<figure class="axs-wide">{img}</figure><div class="axs-cards axs-c3">{cards}</div></div></section>')


def think(s):
    """Same pinned, scroll-driven card animation as the homepage Process section, light version."""
    import process2
    lead = re.search(r"<p>(.*?)</p>", s, re.S).group(1)
    rows = re.findall(r"<div><span>(.*?)</span><span>(.*?)</span></div>", s, re.S)
    cards = "".join(
        f'<li class="prx-card" style="--i:{i}"><span class="prx-no" aria-hidden="true">/{i + 1:02d}</span>'
        f'<span class="prx-big" aria-hidden="true" data-n="{i + 1:02d}"></span>'
        f'<div class="prx-b"><h3 class="prx-t">{t}</h3><p class="prx-p">{d}</p></div></li>'
        for i, (t, d) in enumerate(rows))
    return (f'<section class="prx prx-light" data-screen-label="How I think" style="--n:{len(rows)}"><div class="prx-pin">'
            f'<ol class="prx-stage">{cards}</ol>'
            f'<div class="prx-r"><p class="prx-h prx-lead">{lead}</p>'
            f'<div class="prx-foot"><span class="pr-tag">{_pill(s)}</span></div></div>'
            f'</div>{process2.SCRIPT}</section>')


def experience(s):
    ps = re.findall(r"<p>(.*?)</p>", s, re.S)
    stats = re.findall(r"<div><div>([^<]*)</div><div>([^<]*)</div></div>", s)
    img = _imgs(s)[0]
    st = "".join(f'<div class="axs-scard"><dt>{b}</dt><dd>{a}</dd></div>' for a, b in stats)
    return (f'<section class="axs axs-dark" data-screen-label="Experience and leadership"><div class="axs-in axs-stack">'
            + _hd(_pill(s), ps[0])
            + f'<dl class="axs-scards">{st}</dl>'
            f'<div class="axs-two"><div class="axs-copy">' + "".join(f'<p class="axs-p">{p}</p>' for p in ps[1:])
            + f'</div><figure class="axs-pic">{img}</figure></div></div></section>')


def expertise(s):
    """Same one-open-at-a-time panels as the homepage Capabilities section (pinned, opens on scroll)."""
    import capabilities2
    lead = re.search(r"<p>(.*?)</p>", s, re.S).group(1)
    items = re.findall(r"<div><div>([^<]*)</div><p>(.*?)</p></div>", s, re.S)
    panels = "".join(
        f'<li class="cpx-p{" is-on" if i == 0 else ""}" style="--i:{i}">'
        f'<div class="cpx-strip"><h3 class="cpx-t"><button type="button" class="cpx-btn" aria-expanded="{"true" if i == 0 else "false"}">{t}</button></h3>'
        f'<span class="cpx-no" aria-hidden="true">/{i + 1:02d}</span></div>'
        f'<div class="cpx-body"><span class="cpx-num" aria-hidden="true" data-n="{i + 1:02d}"></span><p class="cpx-d">{d}</p></div></li>'
        for i, (t, d) in enumerate(items))
    return (f'<section data-screen-label="Areas of expertise" class="cpx cpx-about" style="--n:{len(items)}"><div class="cpx-pin">'
            f'<div class="cpx-hd"><span class="pr-tag">{_pill(s)}</span><p class="cpx-lead">{lead}</p></div>'
            f'<ul class="cpx-row">{panels}</ul></div>{capabilities2.SCRIPT}</section>')


def work(s):
    lead = re.search(r"<p>(.*?)</p>", s, re.S).group(1)
    eyebrow = re.search(r'<span class="om-eyebrow">(.*?)</span>', s).group(1)
    arc = re.search(r'<span class="om-arc">(.*?)</span>', s).group(1)
    steps = re.findall(r'<span class="om-step-t">(.*?)</span><span class="om-step-d">(.*?)</span>', s)
    img = _imgs(s)[0]
    st = "".join(f'<li class="axs-step"><span class="axs-no" aria-hidden="true">/{i + 1:02d}</span>'
                 f'<span class="axs-stt">{t}</span><span class="axs-std">{d}</span></li>' for i, (t, d) in enumerate(steps))
    return (f'<section class="axs axs-dark" data-screen-label="How I work"><div class="axs-in axs-stack">'
            + _hd(_pill(s), lead)
            + f'<div class="axs-two axs-work"><div class="axs-approach"><div class="axs-aph"><span>{eyebrow}</span><span>{arc}</span></div>'
            f'<ol class="axs-steps">{st}</ol></div><figure class="axs-pic">{img}</figure></div></div></section>')


def tools(s):
    lead = re.search(r"<p>(.*?)</p>", s, re.S).group(1)
    cols = re.findall(r"<div><div>([^<]*)</div><div>(.*?)</div></div>", s, re.S)
    cols = cols + [("Branding", "Adobe Illustrator · Photoshop<br>Logo design · Brand guidelines")]  # added at the owner's request
    c = "".join(f'<div class="axs-tool"><span class="axs-tk">{k}</span><p class="axs-tv">{v}</p></div>' for k, v in cols)
    return (f'<section class="axs axs-light" data-screen-label="Tools and skills"><div class="axs-in axs-stack">'
            + _hd(_pill(s), lead) + f'<div class="axs-tools">{c}</div></div></section>')


def beyond(s):
    ps = re.findall(r"<p>(.*?)</p>", s, re.S)
    img = _imgs(s)[0]
    return (f'<section class="axs axs-dark" data-screen-label="Beyond design"><div class="axs-in axs-two axs-beyond">'
            f'<div class="axs-copy"><span class="pr-tag">{_pill(s)}</span><p class="axs-lead">{ps[0]}</p>'
            + "".join(f'<p class="axs-p">{p}</p>' for p in ps[1:])
            + f'</div><figure class="axs-pic axs-tall">{img}</figure></div></section>')


def cta(s):
    h2 = re.search(r"<h2>(.*?)</h2>", s).group(1)
    p = re.search(r"<p>(.*?)</p>", s, re.S).group(1)
    links = re.findall(r'<a href="([^"]*)" class="(scp\d)">(.*?)</a>', s)
    w = h2.split(" ")
    head = " ".join(w[:-1]) + f' <span class="axs-dim">{w[-1]}</span>'
    btn = "".join(f'<a href="{u}" class="axs-btn{" is-solid" if c == "scp0" else ""}">{t}</a>' for u, c, t in links)
    return (f'<section class="axs axs-cta" data-screen-label="CTA"><div class="axs-in">'
            f'<h2 class="axs-ch">{head}</h2><p class="axs-cp">{p}</p><div class="axs-btns">{btn}</div></div></section>')


BUILD = [("My story", story), ("What I do", what), ("How I think", think), ("Experience and leadership", experience),
         ("Areas of expertise", expertise), ("How I work", work), ("Tools and skills", tools),
         ("Beyond design", beyond), ("CTA", cta)]


def place(h):
    for label, fn in BUILD:
        a, b, clean = _sec(h, label)
        h = h[:a] + fn(clean) + h[b:]
    return h.replace('<body class="ds rx">', '<body class="ds rx rx-about">', 1)
