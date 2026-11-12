"""Studio layer (v3): restyle every design-system page without touching its copy.

  * inlines rx.css after all other style blocks (as <style id="rx-css">),
  * turns the fixed top bar into a left sidebar on wide screens (adds a small
    profile card and the existing contact details; on phones the burger menu stays),
  * marks the current section in the nav,
  * adds a large "Let's Work Together" link at the top of the footer.

Every word added already appears on the site (name, role line, email, phone,
availability line, the hero button label). Verified afterwards by textdiff.py.

usage: rx.py <src build> <out build> <rx.css>      (src is never modified)
"""
import hashlib, os, pathlib, re, shutil, sys

SRC, OUT, CSS = map(pathlib.Path, sys.argv[1:4])
if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(SRC, OUT)
# phone menu now also serves 901-1099px (the hover mega-menu is replaced by the sidebar list)
_sj = OUT / "assets" / "site.js"
_t = _sj.read_text(encoding="utf-8")
assert _t.count("if (window.innerWidth > 900) setOpen(false);") == 1
_t = _t.replace("if (window.innerWidth > 900) setOpen(false);", "if (window.innerWidth > 1099) setOpen(false);")
# the form posts to its own action when it has one (/api/contact on Vercel), else to Netlify Forms ("/")
assert _t.count("fetch('/', {") == 1
_t = _t.replace("fetch('/', {", "fetch(form.getAttribute('action') || '/', {")
_sj.write_text(_t, encoding="utf-8")
css = CSS.read_bytes()
ver = hashlib.sha256(css).hexdigest()[:8]

SECTIONS = ["about", "services", "industries", "work", "insights", "faq"]

def card(p):
    return (f'<div class="rx-card"><a class="rx-card-img" href="{p}about/index.html" tabindex="-1" aria-hidden="true">'
            f'<img src="{p}uploads/muhammad-babar-author.webp" alt="Muhammad Babar" width="160" height="160" decoding="async"></a>'
            f'<div class="rx-card-t"><span class="rx-card-r">UI UX &amp; AI product designer</span>'
            f'<a class="rx-card-n" href="{p}about/index.html">Muhammad Babar</a>'
            f'<a class="rx-card-cta" href="{p}contact/index.html"><i aria-hidden="true">+</i>Contact me</a></div></div>')

def reel(p):
    return (f'<a class="rx-reel" href="{p}work/index.html"><img src="{p}uploads/work-zippy-cover-w480.webp" '
            f'alt="Zippy fintech wallet app UI design" width="480" height="300" loading="lazy" decoding="async"></a>')

HERO_LABELS = ("Hero", "Services hero", "Industries hero", "Work hero", "Insights hero", "Article hero", "FAQ hero")
STRIP = ('<dl class="rx-strip"><div><dt>Years designing</dt><dd>8+</dd></div><div><dt>Projects delivered</dt><dd>300+</dd></div>'
         '<div><dt>Industries &amp; domains</dt><dd>20+</dd></div><div><dt>On-time delivery</dt><dd>100%</dd></div></dl>')

FOOT = ('<div class="rx-foot">'
        '<a class="rx-mono" href="mailto:babar.13@outlook.com">babar.13@outlook.com</a>'
        '<a class="rx-mono" href="tel:+923070460959">+92 307 0460959</a>'
        '<span class="rx-avail"><i aria-hidden="true"></i>Available for new projects.</span>')  # closed after the reel card

def no_stars(h):
    """Drop the decorative star glyphs (eight-spoked asterisk, four-pointed star) outside JSON-LD."""
    parts = re.split(r'(<script type="application/ld\+json".*?</script>)', h, flags=re.S)
    for i in range(0, len(parts), 2):
        s = parts[i]
        s = re.sub(r'<span style="[^"]*">\u2733</span>', "", s)                 # FAQ row icon
        s = s.replace("<span>\u2726</span>", '<span class="rx-dot" aria-hidden="true"></span>')  # marquee separators
        s = re.sub(r'[\u2733\u2726](?:&nbsp;|\u00a0|\s)*', "", s)
        parts[i] = s
    return "".join(parts)

# owner-supplied images that replace old ones (rb/src/uploads), plus their new alt text
for img in (CSS.parent / "uploads").glob("*.webp"):
    shutil.copy2(img, OUT / "uploads" / img.name)
SWAPS = [("d1f1a3d518c4c0", "why-ai-designed-products-look-the-same-cover",
          "Break the pattern: three identical grey SaaS landing pages beside a distinctive Make your mark design with a bold blue 3D arch",
          "Break the pattern: three identical grey website layouts beside a distinctive bold blue design held in a hand"),
         ("50771ac475eb55", "saturated-colours-hurting-your-icons-cover",
          "Saturated versus tinted app icon backgrounds compared", "Saturated versus tinted app icon backgrounds compared"),
         ("98b829e560ce0c", "claude-design-vs-figma-ai-cover",
          "Claude Design and Figma logos facing off: AI design tool comparison",
          "Claude Design and Figma logos on two pages with a drafting compass between them: AI design tool comparison"),
         ("f2bceb84c5f82e", "before-using-claude-design-cover",
          "Claude Design logo with a numbered checklist: 7 things to know before using Claude Design",
          "Claude Design logo with a numbered checklist: 7 things to know before using Claude Design"),
         ("3aa58b6ef24f4a", "ui-ux-design-trends-2026-cover",
          "Collage of profile card UI designs illustrating UI UX design trends for 2026",
          "Product designer thinking, surrounded by a bento grid layout, a voice AI prompt and accessibility controls, illustrating UI UX design trends for 2026")]
SIZES = {"ui-ux-design-trends-2026-cover": ("800", "600"), "before-using-claude-design-cover": ("1400", "788"), "saturated-colours-hurting-your-icons-cover": ("1400", "788"), "claude-design-vs-figma-ai-cover": ("1400", "788")}  # old full width/height -> new 1672x941

def swap_imgs(h):
    for old_id, new_id, old_alt, new_alt in SWAPS:
        if old_id not in h:
            continue
        def fix(m):
            t = m.group(0).replace(old_id, new_id).replace(f'alt="{old_alt}"', f'alt="{new_alt}"')
            if new_id in SIZES:
                w0, h0 = SIZES[new_id]
                t = t.replace(f'width="{w0}" height="{h0}"', 'width="1672" height="941"').replace(f" {w0}w", " 1672w")
            if "srcset=" not in t:  # old image had one size only: give the new one responsive sizes
                pre = re.search(r'src="([^"]*)' + new_id + r'\.webp"', t).group(1)
                ss = ", ".join(f"{pre}{new_id}-w{w}.webp {w}w" for w in (480, 800, 1200)) + f", {pre}{new_id}.webp 1672w"
                sz = "(max-width: 600px) 92vw, 1000px" if 'fetchpriority="high"' in t else "(max-width: 600px) 92vw, (max-width: 1100px) 46vw, 560px"
                t = t.replace("<img ", f'<img srcset="{ss}" sizes="{sz}" ', 1)
            return re.sub(r"object-position:[^;\"]*", "object-position:50% 50%", t)
        h = re.sub(r"<img[^>]*" + old_id + r"[^>]*>", fix, h)
    return h

for f in sorted(OUT.rglob("*.html")):
    f.write_text(swap_imgs(no_stars(f.read_text(encoding="utf-8"))), encoding="utf-8")

done = skipped = 0
for f in sorted(OUT.rglob("*.html")):
    h = f.read_text(encoding="utf-8")
    if '<body class="ds">' not in h:
        skipped += 1
        continue  # standalone case studies keep their own design for now
    rel = f.parent.relative_to(OUT)
    depth = 0 if str(rel) == "." else len(rel.parts)
    p = "../" * depth
    # stylesheet: after the last style block of the real head
    body_at = h.index('<body class="ds">')
    head_end = h.rindex("</head>", 0, body_at)
    inline = css.decode("utf-8").replace("url(fonts/", f"url({p}assets/fonts/")
    h = h[:head_end] + f'<style id="rx-css">{inline}</style>' + h[head_end:]
    h = h.replace('<body class="ds">', '<body class="ds rx">', 1)
    # header -> sidebar
    assert h.count('<header style="position: fixed;') == 1, f
    h = h.replace('<header style="position: fixed;', '<header class="rx-nav" style="position: fixed;', 1)
    hs = h.index('<header class="rx-nav"')
    logo_end = h.index("</svg></a>", hs) + len("</svg></a>")
    h = h[:logo_end] + card(p) + h[logo_end:]
    sys.path.insert(0, str(pathlib.Path(__file__).parent)); import navsub
    h = navsub.place(h, rel.parts if depth else ())
    nav_end = h.index("</nav>", hs) + len("</nav>")
    h = h[:nav_end] + FOOT + reel(p) + "</div>" + h[nav_end:]
    # heroes: full-bleed colour panel
    if depth == 0:
        sys.path.insert(0, str(pathlib.Path(__file__).parent)); import about2
        a = h.index('<section id="about" data-screen-label="About" class="ab">')
        b = h.index("</section>", a) + len("</section>")
        h = h[:a] + about2.section(p) + h[b:]
        import services2
        h = services2.place(h, p)
        import work2
        h = work2.place(h, p)
        import process2
        h = process2.place(h, p)
        import testimonials2
        h = testimonials2.place(h, p)
        import capabilities2
        h = capabilities2.place(h, p)
        # Trust section ("Built with the rigor, accessibility, and craft...") removed at the owner's request
        t = h.index('<section class="dsi" data-screen-label="Trust"')
        h = h[:t] + h[h.index("</section>", t) + len("</section>"):]
        # the "Case Studies" and "Testimonies" marquee bands are removed at the owner's request
        for first in ("Case Studies", "Testimonies", "FAQ", "Get in Touch"):
            m = re.search(r'<div class="ds[ik]" style="[^"]*overflow: hidden[^"]*">\s*<div data-marquee[^>]*>\s*<div[^>]*><span>' + first + '</span>', h)
            assert m, (f, first)
            i, depth = m.start(), 0
            for t in re.finditer(r'<div\b|</div>', h[m.start():]):
                depth += 1 if t.group(0) == "<div" else -1
                if depth == 0:
                    i = m.start() + t.end(); break
            h = h[:m.start()] + h[i:]
        import logos2
        h = logos2.place(h, p)
        import pricing2
        h = pricing2.place(h, p)
        import blog2
        h = blog2.place(h, p)
        import faq2
        h = faq2.place(h, p)
        hero = h.index('<section id="top" class="hero-fit"')
        hero_end = h.index("</section>", hero)
        socials = re.findall(r'<a href="https://(?:www\.)?(?:linkedin|dribbble|behance|instagram|upwork)[^"]*" target="_blank" aria-label="[^"]+"[^>]*>.*?</a>', h, flags=re.S)[:5]
        assert len(socials) == 5, f
        bar = '<div class="rx-hbar"><div class="rx-hsoc">' + "".join(re.sub(r' class="(?:scp1" style="[^"]*|ctx-soc)"', ' class="rx-soc"', s) for s in socials) + "</div></div>"
        # the portrait is not used in the hero any more (it stays in the sidebar card and About)
        im = re.search(r'<img srcset="[^"]*muhammad-babar-ui-ux-designer[^>]*>\s*', h[hero:hero_end])
        assert im, f
        h = h[:hero + im.start()] + h[hero + im.end():]
        hero_end = h.index("</section>", hero)
        body_open = h.index(">", hero) + 1
        h = h[:body_open] + bar + h[body_open:hero_end] + STRIP + h[hero_end:]
    else:
        for lab in HERO_LABELS:
            k = f'<section class="dsi" data-screen-label="{lab}"'
            if lab == "Article hero" and rel.parts[0] == "insights":
                continue  # blog articles: no colour panel, just the article (owner's request)
            if k in h:
                h = h.replace(k, f'<section class="dsi rx-hero" data-screen-label="{lab}"', 1)
                break
        if str(rel) == "about":
            sys.path.insert(0, str(pathlib.Path(__file__).parent)); import about_page
            h = about_page.place(h)
        if str(rel) in ("work", "insights", "faq"):
            sys.path.insert(0, str(pathlib.Path(__file__).parent)); import inner_pages
            h = inner_pages.place(h, str(rel))
        if str(rel) == "services":
            sys.path.insert(0, str(pathlib.Path(__file__).parent)); import services_page
            h = services_page.place(h)
        if rel.parts[0] == "industries":  # industry pages use the service-page building blocks
            h = h.replace('<body class="ds rx">', '<body class="ds rx rx-svd rx-inx">', 1)
        if len(rel.parts) == 2 and rel.parts[0] == "insights":
            sys.path.insert(0, str(pathlib.Path(__file__).parent)); import article_page
            h = article_page.place(h)
        if len(rel.parts) == 2 and rel.parts[0] == "services":
            sys.path.insert(0, str(pathlib.Path(__file__).parent)); import service_detail
            h = service_detail.place(h)
    # article cards: "Read article" moves onto the image as a button shown on hover (image blurs)
    RA = '<span style="font-size: 13px; color: rgb(138, 138, 132);">Read article →</span>'
    RBTN = ('<span class="rdx-ov"><span class="rdx-btn">Read article <svg viewBox="0 0 24 24" width="14" height="14" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg></span></span>')
    def rcard(m):
        a, body = m.group(1), m.group(2)
        if RA not in body or 'class="rs-media"' not in body:
            return m.group(0)
        body = re.sub(r'\s*' + re.escape(RA), "", body)
        i = body.index('class="rs-media"'); j = body.index("</div></div>", i) + len("</div>")
        body = body[:j] + RBTN + body[j:]
        return a.replace("<a ", '<a class="rdx-card" ', 1) + body + "</a>"
    h = re.sub(r'(<a href="[^"]*" style="display: flex; flex-direction: column; gap: 16px;">)(.*?)</a>', rcard, h, flags=re.S)
    # current section
    top = rel.parts[0] if depth else ""
    if top in SECTIONS:
        pat = f'<a href="{p}{top}/index.html" class="scp5"'
        nav_s, nav_e = h.index('<nav class="nav-links"', hs), h.index("</nav>", hs)
        seg = h[nav_s:nav_e]
        if pat in seg:
            seg = seg.replace(pat, pat + ' aria-current="page"', 1)
            h = h[:nav_s] + seg + h[nav_e:]
    # footer headline link
    m = re.search(r'<footer[^>]*>\s*<div[^>]*>', h)
    assert m, f
    h = h[:m.end()] + f'<a class="rx-big" href="{p}contact/index.html">Let\'s Work Together</a>' + h[m.end():]
    sys.path.insert(0, str(pathlib.Path(__file__).parent)); import footer2
    h = footer2.build(h, p, SRC / "index.html")
    # no icons inside buttons (owner's rule): strip the arrow svg / icon <i> from every CTA button
    BTN = r'(<(?:a|span)\b[^>]*class="(?:[^"]* )?(?:pcx-cta|pr-cta|abx-cta|svx-cta|wkx-all|blx-all|fqx-cta|rdx-btn|wkx-view|rx-big ftx-cta)(?: [^"]*)?"[^>]*>)(.*?)(</(?:a|span)>)'
    def noicon(m):
        inner = re.sub(r'\s*<i aria-hidden="true">\s*<svg.*?</svg>\s*</i>', "", m.group(2), flags=re.S)
        inner = re.sub(r'\s*<svg.*?</svg>', "", inner, flags=re.S)
        return m.group(1) + inner.rstrip() + m.group(3)
    h = re.sub(BTN, noicon, h, flags=re.S)
    # colourful brand icons (owner-supplied SVGs) in every social link
    import json
    ICONS = json.loads((pathlib.Path(__file__).parent / "social_icons.json").read_text())
    n_ig = [0]
    def swap(m):
        if 'class="rx-soc"' in m.group(1):
            return m.group(0)  # the hero top bar keeps the original outline icons
        svg = ICONS[m.group(2)]
        if "__ID__" in svg:
            n_ig[0] += 1; svg = svg.replace("__ID__", f"igrad{n_ig[0]}")
        return m.group(1) + svg
    h = re.sub(r'(<a href="https://[^"]*(?:linkedin|dribbble|behance|instagram|upwork)\.[^"]*"[^>]*aria-label="(LinkedIn|Dribbble|Behance|Instagram|Upwork)"[^>]*>)\s*<svg.*?</svg>', swap, h, flags=re.S)
    f.write_text(h, encoding="utf-8")
    done += 1
print("restyled", done, "pages; left as is", skipped, "; rx.css v", ver)
