"""Homepage Process, studio layout: the section pins while you scroll; on the left one step card
at a time rises in (tilted, in perspective) and the previous card tilts up and away; on the right
the heading, label, intro and button stay put. Rebuilt from the existing markup: same words,
same icons. Without script, on phones, or with reduced motion the four cards simply stack."""
import re

SCRIPT = "<script>(function(){var s=document.currentScript.closest('section'),c=[].slice.call(s.querySelectorAll('.prx-card')),n=c.length;\nvar mq=matchMedia('(min-width:900px) and (prefers-reduced-motion:no-preference)'),tick=false;\nfunction cl(v,a,b){return Math.max(a,Math.min(b,v))}\nfunction draw(){tick=false;if(!mq.matches){s.classList.remove('is-js');c.forEach(function(x){x.style.transform='';x.style.opacity=''});return}\ns.classList.add('is-js');var r=s.getBoundingClientRect(),run=r.height-innerHeight,p=run>0?cl(-r.top/run,0,1):0,t=p*(n-1);\nc.forEach(function(x,i){var d=t-i,tr,o;\nif(d<=-1){tr='translate3d(0,95%,0) rotateX(-38deg)';o=0}\nelse if(d<0){var e=d+1,f=1-e;tr='translate3d(0,'+(f*95)+'%,0) rotateX('+(-38*f)+'deg)';o=cl(e*2,0,1)}\nelse if(i<n-1){var l=cl(d,0,1);tr='translate3d('+(-14*l)+'%,'+(-78*l)+'%,0) rotateX('+(34*l)+'deg) rotateZ('+(-9*l)+'deg) scale('+(1-.16*l)+')';o=1-cl((l-.55)*2.4,0,1)}\nelse{tr='none';o=1}\nx.style.transform=tr;x.style.opacity=o;x.style.zIndex=10+i;x.classList.toggle('is-on',Math.abs(d)<.5)})}\nfunction q(){if(!tick){tick=true;requestAnimationFrame(draw)}}\naddEventListener('scroll',q,{passive:true});addEventListener('resize',q);(mq.addEventListener?mq.addEventListener('change',q):mq.addListener(q));draw()})();</script>"


def section(old):
    tag = re.search(r'<span class="pr-tag">(.*?)</span>', old).group(1)
    h2 = re.search(r'<h2 class="pr-h">(.*?)</h2>', old).group(1)
    intro = re.search(r'<p class="pr-p">(.*?)</p>', old, re.S).group(1)
    cta = re.search(r'(<a class="pr-cta" href="[^"]*">.*?</a>)', old, re.S).group(1)
    steps = re.findall(r'<span>(/\d+)</span>.*?<span class="pr-ic" aria-hidden="true">(<svg.*?</svg>)</span><div><h3>(.*?)</h3><p>(.*?)</p>', old, re.S)
    assert len(steps) == 4, len(steps)
    cards = "".join(
        f'<li class="prx-card" style="--i:{i}"><span class="prx-no" aria-hidden="true">{no}</span>'
        f'<span class="prx-ic" aria-hidden="true">{svg}</span>'
        f'<div class="prx-b"><h3 class="prx-t">{t}</h3><p class="prx-p">{p}</p></div></li>'
        for i, (no, svg, t, p) in enumerate(steps))
    return f'''<section id="process" data-screen-label="Process" class="prx" style="--n:{len(steps)}">
    <div class="prx-pin">
      <ol class="prx-stage">{cards}</ol>
      <div class="prx-r">
        <h2 class="prx-h">{h2}</h2>
        <div class="prx-foot"><span class="pr-tag">{tag}</span><div class="prx-intro"><p>{intro}</p>{cta}</div></div>
      </div>
    </div>
    {SCRIPT}
  </section>'''


def place(h, p):
    a = h.index('<section id="process" data-screen-label="Process" class="pr">')
    b = h.index("</section>", a) + len("</section>")
    return h[:a] + section(h[a:b]) + h[b:]
