"""Homepage About, studio layout: heading + intro statement + chips on top, then a row of
portrait / stat rotator (5 slides) / team photo. Uses the existing About copy word for word;
the only new visible text is the button label "Work with me" (already used on the site)."""

CHECK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5 10 17.5 19 7"/></svg>'
ARROW = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
PREV = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M4 9h10a6 6 0 0 1 0 12h-2"/></svg>'
NEXT = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 14 5-5-5-5"/><path d="M20 9H10a6 6 0 0 0 0 12h2"/></svg>'
CHIPS = [("AI products", "services/ai-product-design/index.html"), ("SaaS", "services/saas-product-design/index.html"),
         ("Fintech apps", "services/fintech-app-design/index.html"), ("Mobile apps", "services/mobile-app-design/index.html"),
         ("Dashboards", "services/dashboard-design/index.html"), ("Design systems", "services/design-systems/index.html")]

def section(p):
    chips = "".join(f'<li><a href="{p}{u}">{t}</a></li>' for t, u in CHIPS)
    chips += f'<li><a href="{p}services/index.html" aria-label="See all 13 services">+7</a></li>'
    slides = [
        '<div class="abx-n">8+</div><p class="abx-c">Years designing</p>',
        '<div class="abx-n">300+</div><p class="abx-c">Projects delivered</p>',
        '<div class="abx-n">20+</div><p class="abx-c">Industries &amp; domains</p>',
        '<div class="abx-n">100% <span class="abx-pill">ON TIME</span></div><p class="abx-c">On-time delivery</p>'
        '<div class="abx-seg" aria-hidden="true">' + "<i></i>" * 8 + '</div>',
        '<div class="abx-n">48h <span class="abx-pill">PROPOSAL</span></div><p class="abx-c">From discovery call to a clear plan</p>'
        f'<ul class="abx-bars"><li>SCOPE {CHECK}</li><li>TIMELINE {CHECK}</li><li>COST {CHECK}</li><li>PROPOSAL IN 48H {CHECK}</li></ul>',
    ]
    n = len(slides)
    sl = "".join(f'<div class="abx-slide{" is-on" if i == 0 else ""}" role="group" aria-roledescription="slide" aria-label="{i + 1} of {n}">{s}</div>' for i, s in enumerate(slides))
    return f'''<section id="about" data-screen-label="About" class="abx">
    <div class="abx-top">
      <div class="abx-l"><h2 class="abx-h">About me</h2><p class="abx-sub">Muhammad Babar · UI UX &amp; AI product designer, 8+ years.</p></div>
      <div class="abx-r">
        <span class="abx-k">Who you’re working with:</span>
        <p class="abx-big">I'm Muhammad Babar, a UI UX and AI&nbsp;UX designer turning ambiguous problems into intelligent, intuitive products.</p>
        <p class="abx-p">Fluent across the modern product design stack and comfortable sitting between design, product, and engineering.</p>
        <a class="abx-cta" href="{p}contact/index.html">Work with me {ARROW}</a>
        <div class="abx-what"><span class="abx-k">What I design</span><ul class="abx-chips">{chips}</ul></div>
      </div>
    </div>
    <div class="abx-row">
      <figure class="abx-photo"><img src="{p}uploads/muhammad-babar-portrait.webp" alt="Muhammad Babar, UI UX and AI product designer, portrait" width="760" height="960" loading="lazy" decoding="async">
        <figcaption>From research and flows<br>to shipped product UI.<br><span>Designed end to end.</span></figcaption></figure>
      <div class="abx-stat" data-abx>
        <div class="abx-slides" aria-live="polite">{sl}</div>
        <div class="abx-ctl"><button type="button" class="abx-prev" aria-label="Previous">{PREV}</button><span class="abx-count" aria-hidden="true"><b>01</b>/{n:02d}</span><button type="button" class="abx-next" aria-label="Next">{NEXT}</button></div>
      </div>
      <figure class="abx-team"><img src="{p}uploads/muhammad-babar-design-review.webp" alt="Muhammad Babar reviewing a product design on a tablet with a teammate" width="960" height="900" loading="lazy" decoding="async"></figure>
    </div>
    <script>(function(){{var r=document.querySelector('[data-abx]');if(!r)return;var s=[].slice.call(r.querySelectorAll('.abx-slide')),c=r.querySelector('.abx-count b'),i=0,t;
function go(k){{i=(k+s.length)%s.length;s.forEach(function(e,j){{e.classList.toggle('is-on',j===i)}});c.textContent=(i<9?'0':'')+(i+1)}}
function auto(){{clearInterval(t);if(!matchMedia('(prefers-reduced-motion: reduce)').matches)t=setInterval(function(){{go(i+1)}},4200)}}
r.querySelector('.abx-prev').addEventListener('click',function(){{go(i-1);auto()}});r.querySelector('.abx-next').addEventListener('click',function(){{go(i+1);auto()}});
r.addEventListener('mouseenter',function(){{clearInterval(t)}});r.addEventListener('mouseleave',auto);r.classList.add('is-js');auto()}})();</script>
  </section>'''
