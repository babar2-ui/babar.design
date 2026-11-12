"""The 13 individual service pages, one shared template in the studio language. Every section is
rebuilt from that page's own markup: same words, links, images and alts; only layout changes.
Sections alternate light / dark like the homepage and About. A section that only had a "/ LABEL"
pill gets that label as its H2 (same as Services "/ HOW I WORK"); sections with a lead sentence keep
the pill + lead pattern used on About."""
import re


def _norm(s):
    s = re.sub(r' style="[^"]*"', "", s)
    s = re.sub(r'<span class="sc-interp">(.*?)</span>', r"\1", s, flags=re.S)
    s = re.sub(r">\s+<", "><", s)
    return s


def _sec(h, label):
    m = re.search(r'<section[^>]*data-screen-label="' + re.escape(label) + '"', h)
    assert m, label
    a = m.start()
    b = h.index("</section>", a) + len("</section>")
    return a, b, _norm(h[a:b])


def _pill(s):
    return re.search(r'<div class="ds-pill">(.*?)</div>', s).group(1).strip()


def _h2(s, cls=""):
    t = _pill(s)
    return f'<h2 class="svd-h{(" " + cls) if cls else ""}"><span aria-hidden="true">/ </span>{t.lstrip("/ ").strip()}</h2>'


def _img(s):
    m = re.search(r"<img [^>]*>", s)
    return m.group(0) if m else ""


def _hd(s, lead):
    return (f'<div class="axs-hd"><span class="pr-tag">{_pill(s)}</span>'
            f'<p class="axs-lead">{lead}</p></div>')


def overview(s):
    ps = re.findall(r"<p>(.*?)</p>", s, re.S)
    img = _img(s)
    body = "".join(f'<p class="axs-p">{p}</p>' for p in ps[1:])
    right = f'<figure class="axs-pic svd-pic">{img}</figure>' if img else ""
    return (f'<section class="axs axs-light svd-ov" data-screen-label="Overview"><div class="axs-in axs-stack">'
            + _hd(s, ps[0])
            + f'<div class="svd-two{"" if img else " is-solo"}"><div class="svd-copy">{body}</div>{right}</div></div></section>')


def challenge(s):
    lead = re.search(r"<p>(.*?)</p>", s, re.S).group(1)
    items = re.findall(r"<div><div>([^<]*)</div><p>(.*?)</p></div>", s, re.S)
    cards = "".join(f'<article class="axs-card"><span class="axs-no" aria-hidden="true">/{i + 1:02d}</span>'
                    f'<h3 class="axs-ct">{t}</h3><p class="axs-cd">{d}</p></article>' for i, (t, d) in enumerate(items))
    return (f'<section class="axs axs-dark" data-screen-label="The challenge"><div class="axs-in axs-stack">'
            + _hd(s, lead) + f'<div class="axs-cards axs-c{min(len(items), 4)} svd-cards">{cards}</div></div></section>')


def what_i_do(s):
    """Homepage Capabilities panels: one open at a time, opening in turn on scroll."""
    import capabilities2
    items = re.findall(r'<div class="scp6"><div>([^<]*)</div><p>(.*?)</p></div>', s, re.S)
    panels = "".join(
        f'<li class="cpx-p{" is-on" if i == 0 else ""}" style="--i:{i}">'
        f'<div class="cpx-strip"><h3 class="cpx-t"><button type="button" class="cpx-btn" aria-expanded="{"true" if i == 0 else "false"}">{t}</button></h3>'
        f'<span class="cpx-no" aria-hidden="true">/{i + 1:02d}</span></div>'
        f'<div class="cpx-body"><span class="cpx-num" aria-hidden="true" data-n="{i + 1:02d}"></span><p class="cpx-d">{d}</p></div></li>'
        for i, (t, d) in enumerate(items))
    return (f'<section data-screen-label="What I do" class="cpx cpx-about svd-cpx" style="--n:{len(items)}"><div class="cpx-pin">'
            f'<div class="cpx-hd">{_h2(s)}</div>'
            f'<ul class="cpx-row">{panels}</ul></div>{capabilities2.SCRIPT}</section>')


def approach(s):
    """Homepage Process: pinned, cards come in one by one on scroll."""
    import process2
    steps = re.findall(r'<span class="svc-step-t">(.*?)</span><span class="svc-step-d">(.*?)</span>', s, re.S)
    img = _img(s)
    cards = "".join(
        f'<li class="prx-card" style="--i:{i}"><span class="prx-no" aria-hidden="true">/{i + 1:02d}</span>'
        f'<span class="prx-big" aria-hidden="true" data-n="{i + 1:02d}"></span>'
        f'<div class="prx-b"><h3 class="prx-t">{t}</h3><p class="prx-p">{d}</p></div></li>'
        for i, (t, d) in enumerate(steps))
    fig = f'<figure class="svd-apimg">{img}</figure>' if img else '<div class="prx-foot prx-foot-line"></div>'
    return (f'<section class="prx svd-prx" data-screen-label="My approach" style="--n:{len(steps)}"><div class="prx-pin">'
            f'<ol class="prx-stage">{cards}</ol>'
            f'<div class="prx-r">{_h2(s, "prx-h")}{fig}</div>'
            f'</div>{process2.SCRIPT}</section>')


def what_you_get(s):
    items = re.findall(r"<div><div>([^<]*)</div><div>(.*?)</div></div>", s, re.S)
    rows = "".join(f'<li class="axs-row"><span class="axs-no" aria-hidden="true">/{i + 1:02d}</span>'
                   f'<h3 class="axs-rt">{t}</h3><p class="axs-rd">{d}</p></li>' for i, (t, d) in enumerate(items))
    return (f'<section class="axs axs-light" data-screen-label="What you get"><div class="axs-in axs-split">'
            f'<div class="axs-hd">{_h2(s)}</div><ol class="axs-rows">{rows}</ol></div></section>')


def benefits(s):
    items = re.findall(r"<div><div>([^<]*)</div><div>(.*?)</div></div>", s, re.S)
    st = "".join(f'<div class="axs-scard"><dt>{d}</dt><dd>{v}</dd></div>' for v, d in items)
    return (f'<section class="axs axs-dark" data-screen-label="Benefits"><div class="axs-in axs-stack">'
            f'{_h2(s)}<dl class="axs-scards svd-ben">{st}</dl></div></section>')


def who(s):
    items = re.findall(r"<div><div>([^<]*)</div><p>(.*?)</p></div>", s, re.S)
    cards = "".join(f'<article class="axs-card"><span class="axs-no" aria-hidden="true">/{i + 1:02d}</span>'
                    f'<h3 class="axs-ct">{t}</h3><p class="axs-cd">{d}</p></article>' for i, (t, d) in enumerate(items))
    return (f'<section class="axs axs-light axs-hoverblue" data-screen-label="Who it\'s for"><div class="axs-in axs-stack">'
            f'{_h2(s)}<div class="axs-cards axs-c{min(len(items), 4)} svd-cards">{cards}</div></div></section>')


def why(s):
    lead = re.search(r"<p>(.*?)</p>", s, re.S).group(1)
    items = re.findall(r"<div><span>(.*?)</span><span>(.*?)</span></div>", s, re.S)
    img = _img(s)
    rows = "".join(f'<li class="svd-why"><span class="axs-no" aria-hidden="true">/{i + 1:02d}</span>'
                   f'<h3 class="svd-wt">{t}</h3><p class="svd-wd">{d}</p></li>' for i, (t, d) in enumerate(items))
    right = f'<figure class="axs-pic svd-pic">{img}</figure>' if img else ""
    return (f'<section class="axs axs-dark" data-screen-label="Why work with me"><div class="axs-in axs-stack">'
            + _hd(s, lead)
            + f'<div class="svd-two{"" if img else " is-solo"}"><ol class="svd-whys">{rows}</ol>{right}</div></div></section>')


IND = re.compile(r'<div class="scp7"><div><span>(\d+)</span><span>(.*?)</span><span>(.*?)</span></div>'
                 r'<div><div><div><p>(.*?)</p><div>(.*?)</div></div>(?:<div><div>(<img [^>]*>)</div></div>)?</div></div></div>', re.S)


def industries(s):
    """Rows like the homepage Services list: one open at a time (hover on desktop, tap anywhere)."""
    items = IND.findall(s)
    assert len(items) == len(re.findall('class="scp7"', s)), (len(items), s[:300])
    rows = []
    for i, (no, name, tags, p, chips, img) in enumerate(items):
        ch = "".join(f'<li>{c}</li>' for c in re.findall(r"<span>(.*?)</span>", chips))
        on = i == 0
        rows.append(
            f'<li class="ind-row{" is-on" if on else ""}"><h3 class="ind-t"><button type="button" class="ind-btn" aria-expanded="{"true" if on else "false"}">'
            f'<span class="ind-no">{no}</span><span class="ind-n">{name}</span><span class="ind-k">{tags}</span></button></h3>'
            f'<div class="ind-body"><div class="ind-bin"><div class="ind-copy"><p class="ind-p">{p}</p><ul class="ind-chips">{ch}</ul></div>'
            + (f'<figure class="ind-img">{img}</figure>' if img else "")
            + "</div></div></li>")
    js = ("<script>(function(){var s=document.currentScript.closest('section'),r=[].slice.call(s.querySelectorAll('.ind-row'));"
          "s.classList.add('is-js');function on(k){r.forEach(function(x,i){var a=i===k;x.classList.toggle('is-on',a);x.querySelector('.ind-btn').setAttribute('aria-expanded',a)})}"
          "r.forEach(function(x,i){x.addEventListener('mouseenter',function(){if(matchMedia('(hover:hover) and (min-width:1100px)').matches)on(i)});"
          "x.querySelector('.ind-btn').addEventListener('click',function(){on(i)})})})();</script>")
    return (f'<section class="axs axs-light svd-ind" data-screen-label="Industries"><div class="axs-in axs-stack">'
            f'{_h2(s)}<ul class="ind-list">{"".join(rows)}</ul></div>{js}</section>')


def tools(s):
    lead = re.search(r"<p>(.*?)</p>", s, re.S).group(1)
    items = re.findall(r'<div class="scp6"><div><div>(<img [^>]*>)</div></div><span>(.*?)</span></div>', s, re.S)
    tiles = "".join(f'<li class="svd-tool"><span class="svd-logo">{im}</span><span class="svd-tn">{t}</span></li>' for im, t in items)
    return (f'<section class="axs axs-dark" data-screen-label="Tools and expertise"><div class="axs-in axs-stack">'
            + _hd(s, lead) + f'<ul class="svd-tools">{tiles}</ul></div></section>')


CASE = re.compile(r'<(?:a href="([^"]*)"|div) class="svc-case"><div class="rs-case"><div>(<img [^>]*>)</div></div>'
                  r'<div><div><div>(.*?)</div><h3>(.*?)</h3><p>(.*?)</p></div><div>((?:<div><div>[^<]*</div><div>[^<]*</div></div>)*)</div></div></(?:a|div)>', re.S)


def featured(s):
    """Homepage Work cards: image + title; hover blurs the image and shows the tags + View case study.
    Description and stats stay in the page as screen-reader text, as on the homepage."""
    tag = _pill(s)
    h2 = re.search(r"<h2>(.*?)</h2>", s).group(1)
    sub = re.search(r'<p class="feat-sub">(.*?)</p>', s, re.S)
    cases = CASE.findall(s)
    assert len(cases) == s.count('class="svc-case"'), len(cases)
    import work2
    cards = ""
    for u, img, cat, title, p, stats in cases:
        cat = re.sub(r"^\s*✳(?:&nbsp;| |\s)*", "", cat)  # no star icons (owner's rule)
        tg = "".join(f'<span class="wkx-tag">{t.strip()}</span>' for t in cat.split("·"))
        st = " ".join(f"<span>{v}</span> <span>{k}</span>" for v, k in re.findall(r"<div><div>(.*?)</div><div>(.*?)</div></div>", stats))
        open_, close = (f'<a href="{u}" class="svd-case wkx-card">', "</a>") if u else ('<div class="svd-case wkx-card">', "</div>")
        cards += (f'{open_}<figure class="svd-cimg">{img}'
                  f'<div class="wkx-ov" aria-hidden="true"><div class="wkx-tags">{tg}</div>{work2.VIEW if u else ""}</div></figure>'
                  f'<span class="ds-sr">{cat}</span><h3 class="svd-ct">{title}</h3>'
                  f'<span class="ds-sr">{p} {st}</span>{close}')
    head = (f'<div class="svd-fhd"><span class="pr-tag">{tag}</span><h2 class="svd-fh">{h2}</h2>'
            + (f'<p class="axs-p svd-fsub">{sub.group(1)}</p>' if sub else "") + "</div>")
    return (f'<section class="axs axs-light svd-feat" data-screen-label="Featured work"><div class="axs-in axs-stack">'
            f'{head}<div class="svd-cases svd-n{len(cases)}">{cards}</div></div></section>')


def faqs(s):
    items = re.findall(r"<div><div>([^<]*)</div><p>(.*?)</p></div>", s, re.S)
    rows = "".join(
        f'<details class="fqx-row"{" open" if k == 0 else ""}><summary class="fqx-q">'
        f'<span class="fqx-no" aria-hidden="true">/{k + 1:02d}</span><span class="fqx-qt">{q}</span>'
        f'<span class="fqx-pm" aria-hidden="true"></span></summary><div class="fqx-a">{a}</div></details>'
        for k, (q, a) in enumerate(items))
    return (f'<section class="fqx svd-faq" data-screen-label="FAQs"><div class="fqx-in">'
            f'<div class="fqx-hd">{_h2(s, "fqx-h")}</div><div class="fqx-list">{rows}</div></div></section>')


def cta(s):
    h2 = re.search(r"<h2>(.*?)</h2>", s).group(1)
    p = re.search(r"<p>(.*?)</p>", s, re.S).group(1)
    links = re.findall(r'<a href="([^"]*)" class="(scp\d)">(.*?)</a>', s)
    w = h2.split(" ")
    head = " ".join(w[:-1]) + f' <span class="axs-dim">{w[-1]}</span>'
    btn = "".join(f'<a href="{u}" class="axs-btn{" is-solid" if c == "scp0" else ""}">{t}</a>' for u, c, t in links)
    return (f'<section class="axs axs-cta" data-screen-label="CTA"><div class="axs-in">'
            f'<h2 class="axs-ch">{head}</h2><p class="axs-cp">{p}</p><div class="axs-btns">{btn}</div></div></section>')


BUILD = [("Overview", overview), ("The challenge", challenge), ("What I do", what_i_do), ("My approach", approach),
         ("What you get", what_you_get), ("Benefits", benefits), ("Who it's for", who), ("Why work with me", why),
         ("Industries", industries), ("Tools and expertise", tools), ("Featured work", featured), ("FAQs", faqs),
         ("CTA", cta)]


def place(h):
    # the cover image under the hero is removed at the owner's request (all service pages)
    a, b, _ = _sec(h, "Cover")
    h = h[:a] + h[b:]
    for label, fn in BUILD:
        a, b, clean = _sec(h, label)
        h = h[:a] + fn(clean) + h[b:]
    return h.replace('<body class="ds rx">', '<body class="ds rx rx-svd">', 1)
