"""Homepage Services, studio layout: heading column on the left, a list of the three service
areas on the right. One row at a time is open (thumbnail | title + description | sub-services),
the others show only their dimmed title. Rebuilt from the existing section's markup, so every
word, link and image alt is carried over unchanged; nothing new is written."""
import re

CTA_ARROW = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>'
CHECK_SVG = re.compile(r'<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="m8\.5 12\.2 2\.4 2\.4 4\.6-4\.8"/></svg>')


def section(old):
    """old = the original <section id="services" ... class="sv">...</section> markup."""
    tag = re.search(r'<span class="pr-tag">(.*?)</span>', old).group(1)
    h2 = re.search(r'<h2 class="sv-h">(.*?)</h2>', old).group(1)
    intro = re.search(r'<div class="sv-intro"><p>(.*?)</p>', old, re.S).group(1)
    cta = re.search(r'<a class="pr-cta" href="([^"]*)">(.*?) <i', old, re.S)
    cards = re.findall(r'<article class="sv-card">(.*?)</article>', old, re.S)
    assert len(cards) == 3, len(cards)
    words = h2.split(" ")
    head = " ".join(words[:-1]) + f' <span class="svx-dim">{words[-1]}</span>' if len(words) > 1 else h2
    rows = []
    for i, c in enumerate(cards):
        title = re.search(r"<h3>(.*?)</h3>", c).group(1)
        desc = re.search(r'<p class="sv-d">(.*?)</p>', c, re.S).group(1)
        items = CHECK_SVG.sub("", re.search(r'<ul class="sv-list">(.*?)</ul>', c, re.S).group(1))
        img = re.search(r"<img [^>]*>", c).group(0)
        img = re.sub(r'\ssizes="[^"]*"', ' sizes="(max-width: 900px) 92vw, 220px"', img)
        on = " is-on" if i == 0 else ""
        rows.append(
            f'<article class="svx-row{on}" data-i="{i}">'
            f'<div class="svx-thumb">{img}</div>'
            f'<div class="svx-mid"><h3 class="svx-t"><button type="button" class="svx-btn" aria-expanded="{"true" if on else "false"}">{title}</button></h3>'
            f'<p class="svx-d">{desc}</p></div>'
            f'<ul class="svx-list">{items}</ul>'
            f'</article>')
    return f'''<section id="services" data-screen-label="Services" class="svx">
    <div class="svx-in">
      <div class="svx-hd">
        <span class="pr-tag">{tag}</span>
        <h2 class="svx-h">{head}</h2>
        <p class="svx-intro">{intro}</p>
      </div>
      <div class="svx-rows">{"".join(rows)}</div>
      <div class="svx-foot"><a class="svx-cta" href="{cta.group(1)}">{cta.group(2)} {CTA_ARROW}</a></div>
    </div>
    <script>(function(){{var s=document.currentScript.parentNode,r=[].slice.call(s.querySelectorAll('.svx-row'));
s.classList.add('is-js');function on(k){{r.forEach(function(x,i){{var a=i===k;x.classList.toggle('is-on',a);x.querySelector('.svx-btn').setAttribute('aria-expanded',a)}})}}
r.forEach(function(x,i){{x.addEventListener('mouseenter',function(){{if(matchMedia('(hover:hover) and (min-width:900px)').matches)on(i)}});x.querySelector('.svx-btn').addEventListener('click',function(){{on(i)}})}})}})();</script>
  </section>'''


def place(h, p):
    """Rebuild the services section and move it straight after About."""
    a = h.index('<section id="services" data-screen-label="Services" class="sv">')
    b = h.index("</section>", a) + len("</section>")
    new = section(h[a:b])
    h = h[:a] + h[b:]
    ab = h.index('<section id="about" data-screen-label="About"')
    ab_end = h.index("</section>", ab) + len("</section>")
    return h[:ab_end] + "\n  " + new + h[ab_end:]
