"""Sidebar Services list: the hover mega-menu (hidden in the sidebar layout) becomes an open/close
list under "Services". Same links and words; the per-link icons are dropped (owner's rule: no stars
or decorative icons in the menu). Starts open on the Services pages."""
import re

MEGA = re.compile(r'<div class="nav-mega" hidden="">.*?</div></div>(?=\s*</div>\s*<a href=)', re.S)
GROUP = re.compile(r'<a href="([^"]*)" class="scp5" style="display: block;[^"]*">([^<]*)</a>\s*<div[^>]*>(.*?)</div>', re.S)
LINK = re.compile(r'<a href="([^"]*)" class="scp5"[^>]*>(?:<svg.*?</svg>)?<span>(.*?)</span></a>', re.S)
FOOT = re.compile(r'<span[^>]*>([^<]*)</span>\s*<a href="([^"]*)" class="scp5"[^>]*>([^<]*?)\s*→</a>')


def place(h, rel_parts):
    m = MEGA.search(h)
    assert m, "mega menu not found"
    mega = m.group(0)
    here = len(rel_parts) == 2 and rel_parts[0] == "services"
    on = len(rel_parts) >= 1 and rel_parts[0] == "services"
    groups = []
    for gu, gt, body in GROUP.findall(mega):
        li = ""
        for u, t in LINK.findall(body):
            cur = ' aria-current="page"' if here and u == "index.html" else ""
            li += f'<li><a href="{u}"{cur}>{t}</a></li>'
        groups.append(f'<div class="rx-sg"><a class="rx-sh" href="{gu}">{gt}</a><ul>{li}</ul></div>')
    assert len(groups) == 3, groups
    note, au, at = FOOT.search(mega).groups()
    new = (f'<div class="rx-sub" id="rx-sub"><div class="rx-sub-in">{"".join(groups)}'
           f'<p class="rx-snote">{note} <a href="{au}">{at}</a></p></div></div>')
    h = h[:m.start()] + new + h[m.end():]
    # +/- marker inside the Services link, so the whole row is one link to the Services page;
    # hovering (or keyboard focus) shows the service pages tooltip
    i = h.index('<div class="nav-has-menu"')
    j = h.index("</a>", i)
    h = h[:j] + '<span class="rx-st" aria-hidden="true"></span>' + h[j:]
    h = h.replace('<div class="nav-has-menu"', f'<div class="nav-has-menu rx-svc{" is-sec" if on else ""}"', 1)
    if here:  # phone menu: mark this page too
        d = h.find('id="nav-drawer"')
        if d != -1:
            k2 = h.find('<a class="nd-sub" href="index.html"', d)
            if k2 != -1:
                h = h[:k2] + '<a class="nd-sub" aria-current="page" href="index.html"' + h[k2 + len('<a class="nd-sub" href="index.html"'):]
    js = ("<script>(function(){var w=document.querySelector('.rx-svc'),b=w&&w.querySelector('.rx-st'),p=w&&w.querySelector('.rx-sub'),tm;if(!b||!p)return;"
          "var mq=matchMedia('(min-width:1100px)');"
          "function place(){var r=b.getBoundingClientRect(),h=p.offsetHeight,t=Math.max(12,Math.min(r.top-22,innerHeight-h-12));"
          "p.style.setProperty('--tt-top',t+'px');p.style.setProperty('--tt-arrow',Math.max(14,Math.min(h-26,r.top+r.height/2-t-6))+'px')}"
          "function set(o){clearTimeout(tm);if(o&&!mq.matches)return;w.classList.toggle('is-open',o);if(o)place()}"
          "w.addEventListener('mouseenter',function(){set(true)});"
          "w.addEventListener('mouseleave',function(){clearTimeout(tm);tm=setTimeout(function(){set(false)},220)});"
          "w.addEventListener('focusin',function(){set(true)});"
          "w.addEventListener('focusout',function(e){if(!w.contains(e.relatedTarget))set(false)});"
          "document.addEventListener('keydown',function(e){if(e.key==='Escape')set(false)});"
          "addEventListener('resize',function(){if(w.classList.contains('is-open'))place()});"
          "var n=document.querySelector('.rx-nav');n&&n.addEventListener('scroll',function(){if(w.classList.contains('is-open'))place()},{passive:true})})();</script>")
    k = h.index("</nav>", i)
    return h[:k] + js + h[k:]
