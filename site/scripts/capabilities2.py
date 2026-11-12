"""Homepage Capabilities, studio layout: header row (label | heading | intro), then a row of six
panels. One panel is open at a time (wide, blue, big icon, number, title, text); the others
show a white title strip over a grey body. The first is open to begin with; on wide screens
the section pins and scrolling opens the panels one after another (click also opens one).
On phones the panels stack and each opens as it scrolls into view. Same words and icons."""
import re

SCRIPT = "<script>(function(){var s=document.currentScript.closest('section'),P=[].slice.call(s.querySelectorAll('.cpx-p')),n=P.length,cur=0,tick=false;\nvar wide=matchMedia('(min-width:900px) and (prefers-reduced-motion:no-preference)');\nfunction set(k){cur=k;P.forEach(function(p,i){var a=i===k;p.classList.toggle('is-on',a);p.querySelector('.cpx-btn').setAttribute('aria-expanded',a)})}\nfunction run(){return s.offsetHeight-innerHeight}\nfunction draw(){tick=false;if(!wide.matches)return;var r=s.getBoundingClientRect(),R=run(),p=R>0?Math.max(0,Math.min(1,-r.top/R)):0,k=Math.min(n-1,Math.floor(p*n*.9999));if(k!==cur)set(k)}\nfunction q(){if(!tick){tick=true;requestAnimationFrame(draw)}}\nfunction mode(){s.classList.toggle('is-pin',wide.matches);if(wide.matches){draw()}else{P.forEach(function(p,i){if(i>0&&!p.dataset.seen)p.classList.remove('is-on')})}}\nP.forEach(function(p,i){p.querySelector('.cpx-btn').addEventListener('click',function(){if(wide.matches){var R=run(),top=s.getBoundingClientRect().top+scrollY;scrollTo({top:top+R*(i+.5)/n,behavior:'smooth'})}else{p.classList.toggle('is-on')}})});\nif('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting&&!wide.matches){e.target.dataset.seen=1;e.target.classList.add('is-on');e.target.querySelector('.cpx-btn').setAttribute('aria-expanded',true);io.unobserve(e.target)}})},{rootMargin:'0px 0px -35% 0px'});P.slice(1).forEach(function(p){io.observe(p)})}\naddEventListener('scroll',q,{passive:true});addEventListener('resize',function(){mode();q()});(wide.addEventListener?wide.addEventListener('change',mode):wide.addListener(mode));s.classList.add('is-js');mode()})();</script>"


def section(old):
    tag = re.search(r'<span class="pr-tag">(.*?)</span>', old).group(1)
    h2 = re.search(r'<h2 class="cp-h">(.*?)</h2>', old).group(1)
    intro = re.search(r'<p class="cp-intro">(.*?)</p>', old, re.S).group(1)
    items = re.findall(r'<span>(/\d+)</span>.*?<span class="cp-ic" aria-hidden="true">(<svg.*?</svg>)</span><div><h3>(.*?)</h3><p>(.*?)</p>', old, re.S)
    assert len(items) == 6, len(items)
    # "Accessible by Default" removed from the homepage at the owner's request; renumber the rest
    items = [it for it in items if it[2] != "Accessible by Default"]
    assert len(items) == 5
    items = [(f"/{k + 1:02d}", svg, t, d) for k, (_, svg, t, d) in enumerate(items)]
    tag = re.sub(r"/ 06 ", f"/ {len(items):02d} ", tag)
    BOLT = '<svg viewBox="0 0 24 24"><path d="M12 3.5 18.5 10 15 18.5H9L5.5 10Z"/><circle cx="12" cy="11.5" r="1.6"/><path d="M12 3.5v6.4M9 21h6"/></svg>'  # pen nib, as in Process "Design"
    items = [(no, BOLT if "Claude" in t else svg, t, d) for no, svg, t, d in items]  # no sparkle/star icons
    panels = "".join(
        f'<li class="cpx-p{" is-on" if i == 0 else ""}" style="--i:{i}">'
        f'<div class="cpx-strip"><h3 class="cpx-t"><button type="button" class="cpx-btn" aria-expanded="{"true" if i == 0 else "false"}">{t}</button></h3><span class="cpx-no" aria-hidden="true">{no}</span></div>'
        f'<div class="cpx-body"><span class="cpx-ic" aria-hidden="true">{svg}</span><p class="cpx-d">{d}</p></div></li>'
        for i, (no, svg, t, d) in enumerate(items))
    return f'''<section data-screen-label="Capabilities" class="cpx" style="--n:{len(items)}">
    <div class="cpx-pin">
      <div class="cpx-hd"><span class="pr-tag">{tag}</span><h2 class="cpx-h">{h2}</h2><p class="cpx-intro">{intro}</p></div>
      <ul class="cpx-row">{panels}</ul>
    </div>
    {SCRIPT}
  </section>'''


def place(h, p):
    a = h.index('<section data-screen-label="Capabilities" class="cp">')
    b = h.index("</section>", a) + len("</section>")
    return h[:a] + section(h[a:b]) + h[b:]
