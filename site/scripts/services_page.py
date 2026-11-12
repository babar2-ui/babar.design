"""Services page in the studio language. Same words and links; the three service areas get the
matching images used on the homepage Services section (same files and alt text)."""
import re

IMGS = [  # (file id, has responsive variants, width, height, alt) — as on the homepage
    ("4ca7943d61980f", True, 1448, 1086, "Parking management mobile app UI design shown on a phone"),
    ("f05a898d950046", False, 1050, 385, "Specialty coffee website design shown on a laptop"),
    ("b32900cc821448", False, 1447, 603, "AI marketing image generator SaaS workflow UI design"),
]


def _sec(h, label):
    a = re.search(r'<section[^>]*data-screen-label="' + re.escape(label) + '"', h).start()
    b = h.index("</section>", a) + len("</section>")
    return a, b, re.sub(r' style="[^"]*"', "", h[a:b])


def _img(i):
    fid, resp, w, hh, alt = IMGS[i]
    ss = (f' srcset="../uploads/{fid}-w480.webp 480w, ../uploads/{fid}-w800.webp 800w, ../uploads/{fid}-w1200.webp 1200w, '
          f'../uploads/{fid}.webp {w}w" sizes="(max-width: 900px) 92vw, 560px"') if resp else ""
    return f'<img{ss} src="../uploads/{fid}.webp" alt="{alt}" width="{w}" height="{hh}" loading="lazy" decoding="async">'


def service_list(s):
    blocks = re.findall(r"<div>\s*<span>(\d+)</span>\s*<div>(.*?)</div>\s*<div>(.*?)</div>\s*</div>", s, re.S)
    assert len(blocks) == 3, len(blocks)
    rows = []
    for i, (num, main, links) in enumerate(blocks):
        h2 = re.search(r"<h2>(.*?)</h2>", main).group(1)
        p = re.search(r"<p>(.*?)</p>", main, re.S).group(1)
        btn = re.search(r'<a href="([^"]*)" class="scp1">(.*?)</a>', main)
        subs = re.findall(r'<a href="([^"]*)" class="scp5"><span>(.*?)</span><span>→</span></a>', links)
        li = "".join(f'<li><a href="{u}">{t}</a></li>' for u, t in subs)
        rows.append(
            f'<article class="svl-row"><div class="svl-main"><span class="svl-no">{num}</span><h2 class="svl-h"><span class="svl-mask"><span>{h2}</span></span></h2>'
            f'<p class="svl-p">{p}</p><a class="svl-btn" href="{btn.group(1)}">{btn.group(2)}</a></div>'
            f'<div class="svl-side"><figure class="svl-img">{_img(i)}</figure><ul class="svl-links">{li}</ul></div></article>')
    js = ("<script>(function(){var s=document.currentScript.closest('section');"
          "if(matchMedia('(prefers-reduced-motion: reduce)').matches||!('IntersectionObserver' in window))return;"
          "s.classList.add('is-js');var R=[].slice.call(s.querySelectorAll('.svl-row'));"
          "R.forEach(function(r){[].forEach.call(r.querySelectorAll('.svl-links li'),function(l,i){l.style.setProperty('--d',(0.35+i*0.07)+'s')})});"
          "var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('is-in');io.unobserve(e.target)}})},{threshold:0.18});"
          "R.forEach(function(r){io.observe(r)});"
          "var I=[].slice.call(s.querySelectorAll('.svl-img img')),t=false;"
          "function px(){t=false;var h=innerHeight;I.forEach(function(i){var b=i.parentNode.getBoundingClientRect();if(b.bottom<0||b.top>h)return;"
          "var k=((b.top+b.height/2)-h/2)/h;i.style.setProperty('--py',(k*-36).toFixed(1)+'px')})}"
          "addEventListener('scroll',function(){if(!t){t=true;requestAnimationFrame(px)}},{passive:true});px()})();</script>")
    return f'<section class="svl" data-screen-label="Service list"><div class="svl-in">{"".join(rows)}</div>{js}</section>'


def how(s):
    """Homepage Process animation, light version (same as About "How I think")."""
    import process2
    tag = re.search(r'<div class="ds-pill">(.*?)</div>', s).group(1)
    items = re.findall(r"<div><div>([^<]*)</div><p>(.*?)</p></div>", s, re.S)
    cards = "".join(
        f'<li class="prx-card" style="--i:{i}"><span class="prx-no" aria-hidden="true">/{i + 1:02d}</span>'
        f'<span class="prx-big" aria-hidden="true" data-n="{i + 1:02d}"></span>'
        f'<div class="prx-b"><h3 class="prx-t">{t}</h3><p class="prx-p">{d}</p></div></li>'
        for i, (t, d) in enumerate(items))
    head = tag.lstrip("/ ").strip()
    return (f'<section class="prx prx-light prx-svc" data-screen-label="How I work" style="--n:{len(items)}"><div class="prx-pin">'
            f'<ol class="prx-stage">{cards}</ol>'
            f'<div class="prx-r"><h2 class="prx-h prx-lead"><span aria-hidden="true">/ </span>{head}</h2>'
            f'<div class="prx-foot prx-foot-line"></div></div>'
            f'</div>{process2.SCRIPT}</section>')


def cta(s):
    h2 = re.search(r"<h2>(.*?)</h2>", s).group(1)
    p = re.search(r"<p>(.*?)</p>", s, re.S).group(1)
    u, t = re.search(r'<a href="([^"]*)" class="scp0">(.*?)</a>', s).groups()
    w = h2.split(" ")
    head = " ".join(w[:-1]) + f' <span class="axs-dim">{w[-1]}</span>'
    return (f'<section class="axs axs-cta" data-screen-label="CTA"><div class="axs-in">'
            f'<h2 class="axs-ch">{head}</h2><p class="axs-cp">{p}</p>'
            f'<div class="axs-btns"><a href="{u}" class="axs-btn is-solid">{t}</a></div></div></section>')


def place(h):
    for label, fn in (("Service list", service_list), ("How I work", how), ("CTA", cta)):
        a, b, clean = _sec(h, label)
        h = h[:a] + fn(clean) + h[b:]
    return h
