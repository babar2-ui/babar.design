"""Industries: /industries/ (all industries) and /industries/<slug>/ (one page per industry).

Entries live in content/industries/<slug>.json (editable in the admin). They start from the
"Industries I serve" list used on every service page (same names, focus areas, sentences, images);
optional fields (overview, challenges, FAQs) add more to a page. A page with no overview text yet
is marked noindex and left out of the sitemap, so short pages never count against the site in search.

Pages are made from the About page's shell (head, sidebar, footer) with every link rebased, then
rx.py restyles them like the rest of the site. Also writes the list used by the sidebar menu
(site/scripts/navsub.py) to the file named by RX_INDUSTRIES.

usage (from build.py): industries.place(stage, content, nav_json)"""
import html, json, os, pathlib, posixpath, re

import cms

SITE = cms.SITE
esc = cms.esc
SKIP = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//|/|#|\{)", re.I)


# ---------------------------------------------------------------- links
def rebase(h, from_dir, to_dir):
    """Relative links written for a page in from_dir, rewritten for a page in to_dir (both relative
    to the site root, "" for the root), in the site's usual form: "../" * depth + path."""
    p = "../" * (len(to_dir.split("/")) if to_dir else 0)

    def fix(u):
        if not u or SKIP.match(u):
            return u
        path, sep, rest = re.match(r"([^?#]*)([?#]?)(.*)", u).groups()
        if not path:
            return u
        full = posixpath.normpath(posixpath.join(from_dir, path)) if from_dir else posixpath.normpath(path)
        return p + full + sep + rest

    h = re.sub(r'\b(href|src|action|poster)="([^"]*)"', lambda m: f'{m.group(1)}="{fix(m.group(2))}"', h)
    h = re.sub(r'\bsrcset="([^"]*)"', lambda m: 'srcset="' + ", ".join(
        " ".join([fix(b[0])] + b[1:]) for b in (i.strip().split() for i in m.group(1).split(",")) if b) + '"', h)
    return re.sub(r"url\((['\"]?)([^)'\"]+)\1\)", lambda m: f"url({m.group(1)}{fix(m.group(2))}{m.group(1)})", h)


def shell(stage, to_dir):
    """About page with its links rebased; returns (head+nav, footer) around the page content."""
    h = (stage / "about" / "index.html").read_text(encoding="utf-8")
    h = rebase(h, "about", to_dir)
    a = h.index("</header></div>") + len("</header></div>")
    b = h.index('<div class="sc-host" data-sc-name="Footer">')
    b = h.rindex("</section>", 0, b) + len("</section>")
    return h[:a], h[b:]


def head(h, title, desc, url, crumbs, image, image_alt, noindex):
    h = re.sub(r"<title>.*?</title>", f"<title>{esc(title)}</title>", h, count=1, flags=re.S)
    a = h.index('<meta name="description"')
    b = h.index("<style", a)
    meta = [f'<meta name="description" content="{esc(desc)}">',
            f'<link rel="canonical" href="{url}">',
            f'<link rel="alternate" hreflang="en" href="{url}">',
            f'<link rel="alternate" hreflang="x-default" href="{url}">',
            '<meta property="og:type" content="website">',
            '<meta property="og:site_name" content="Muhammad Babar">',
            f'<meta property="og:title" content="{esc(title)}">',
            f'<meta property="og:description" content="{esc(desc)}">',
            f'<meta property="og:url" content="{url}">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{esc(title)}">',
            f'<meta name="twitter:description" content="{esc(desc)}">']
    if image:
        img = SITE + image if image.startswith("/") else image
        meta += [f'<meta property="og:image" content="{esc(img)}">', f'<meta property="og:image:alt" content="{esc(image_alt)}">',
                 f'<meta name="twitter:image" content="{esc(img)}">']
    if noindex:
        meta.insert(0, '<meta name="robots" content="noindex, follow">')
    h = h[:a] + "\n".join(meta) + h[b:]
    items = [{"@type": "ListItem", "position": i + 1, "name": n, **({"item": u} if u else {})} for i, (n, u) in enumerate(crumbs)]
    graph = {"@context": "https://schema.org", "@graph": [
        {"@type": "Person", "@id": f"{SITE}/#person", "name": "Muhammad Babar", "url": f"{SITE}/about/"},
        {"@type": "BreadcrumbList", "itemListElement": items},
        {"@type": "WebPage", "name": title, "description": desc, "url": url, "inLanguage": "en",
         "about": {"@id": f"{SITE}/#person"}}]}
    ld = json.dumps(graph, ensure_ascii=False).replace("</", "<\\/")
    return re.sub(r'<script type="application/ld\+json">.*?</script>',
                  lambda m: f'<script type="application/ld+json">\n{ld}\n</script>', h, count=1, flags=re.S)


# ---------------------------------------------------------------- data
def load(folder):
    out = []
    for f in sorted(folder.glob("*.json")) if folder.exists() else []:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except ValueError as e:
            raise cms.ContentError(f"industries/{f.name}: not valid JSON ({e})")
        if d.get("draft"):
            continue
        if not cms.SLUG.match(f.stem):
            raise cms.ContentError(f"industries/{f.name}: the file name must be lowercase letters, numbers and dashes")
        for k in ("name", "summary"):
            if not str(d.get(k) or "").strip():
                raise cms.ContentError(f"industries/{f.stem}: '{k}' is empty")
        d["slug"] = f.stem
        out.append(d)
    out.sort(key=lambda d: (int(d.get("order") or 99), d["name"]))
    return out


CARD_START = re.compile(r'<(?:a href="([^"]*)"|div) style="display: grid; grid-template-columns: minmax\(0px, 1fr\) minmax\(0px, 1fr\); gap: 40px; align-items: stretch;">')


def work_cards(stage):
    """Case cards on the Work page (the original ones and the admin's): link, image, category, title, summary, stats."""
    h = (stage / "work" / "index.html").read_text(encoding="utf-8")
    a = h.index('data-screen-label="Case list"')
    s = h[a:h.index("</section>", a)]
    starts = [m for m in CARD_START.finditer(s)]
    out = []
    for i, m in enumerate(starts):
        c = s[m.start():starts[i + 1].start() if i + 1 < len(starts) else len(s)]
        img = re.search(r"<img [^>]*>", c).group(0)
        img = re.sub(r' (?:fetchpriority|loading|decoding|style)="[^"]*"', "", img)
        cat = re.search(r'margin-bottom: 14px;">.*?<span class="sc-interp">(.*?)</span>', c, re.S).group(1)
        title = re.search(r'<h3[^>]*><span class="sc-interp">(.*?)</span></h3>', c, re.S).group(1)
        summ = re.search(r'<p[^>]*><span class="sc-interp">(.*?)</span></p>', c, re.S).group(1)
        stats = re.findall(r'font-size: 36px;[^>]*><span class="sc-interp">(.*?)</span></div><div[^>]*><span class="sc-interp">(.*?)</span>', c)
        out.append({"href": m.group(1), "img": img, "cat": cat, "title": title, "summary": summ, "stats": stats})
    return out


# ---------------------------------------------------------------- pages
HERO = ('<section class="dsi" data-screen-label="Industries hero" style="padding: 120px 40px 60px; max-width: 1200px; margin: 0px auto;">\n'
        '{crumb}    <div class="ds-pill" style="font-size: 12px; letter-spacing: 0.12em; color: rgb(138, 138, 132); margin-bottom: 24px;">{pill}</div>\n'
        '    <h1 style="margin: 0px 0px 24px; font-size: 72px; line-height: 1.05; letter-spacing: -0.03em; font-weight: 500; max-width: 900px; text-wrap: pretty;">{h1}</h1>\n'
        '{p}  </section>\n')
P = '    <p style="margin: 0px; font-size: 15px; line-height: 1.7; color: rgb(154, 154, 148); max-width: 560px;">{}</p>\n'


def crumb(p, name):
    return (f'    <nav aria-label="Breadcrumb" style="display: flex; gap: 8px; font-size: 13px; color: rgb(138, 138, 132);"><a href="{p}index.html" class="scp5">Home</a>'
            f'<span>/</span><a href="../index.html" class="scp5">Industries</a><span>/</span><span style="color: rgb(201, 201, 196);">{esc(name)}</span></nav>\n')


def img_tag(ctx, d, p, extra=""):
    return ctx.img(d["image"], d.get("image_alt") or "", p, extra=extra or cms.LAZY)


def cta(p):
    return (f'<section class="axs axs-cta" data-screen-label="CTA"><div class="axs-in"><h2 class="axs-ch">Want results like <span class="axs-dim">these?</span></h2>'
            f'<div class="axs-btns"><a href="{p}contact/index.html" class="axs-btn is-solid">Start a project</a></div></div></section>')


IND_JS = ("<script>(function(){var s=document.currentScript.closest('section'),r=[].slice.call(s.querySelectorAll('.ind-row'));"
          "s.classList.add('is-js');function on(k){r.forEach(function(x,i){var a=i===k;x.classList.toggle('is-on',a);x.querySelector('.ind-btn').setAttribute('aria-expanded',a)})}"
          "r.forEach(function(x,i){x.addEventListener('mouseenter',function(){if(matchMedia('(hover:hover) and (min-width:1100px)').matches)on(i)});"
          "x.querySelector('.ind-btn').addEventListener('click',function(){on(i)})})})();</script>")


def index_page(stage, inds, ctx):
    top, foot = shell(stage, "industries")
    p = "../"
    url = f"{SITE}/industries/"
    names = [d["name"] for d in inds]
    intro = ", ".join(names[:-1]) + " and " + names[-1] + "." if len(names) > 1 else (names[0] + "." if names else "")
    rows = []
    for i, d in enumerate(inds):
        ch = "".join(f"<li>{esc(c)}</li>" for c in d.get("focus") or [])
        on = i == 0
        rows.append(
            f'<li class="ind-row{" is-on" if on else ""}"><h3 class="ind-t"><button type="button" class="ind-btn" aria-expanded="{"true" if on else "false"}">'
            f'<span class="ind-no">{i + 1:02d}</span><span class="ind-n">{esc(d["name"])}</span><span class="ind-k">{esc(d.get("tagline"))}</span></button></h3>'
            f'<div class="ind-body"><div class="ind-bin"><div class="ind-copy"><p class="ind-p">{esc(d["summary"])}</p><ul class="ind-chips">{ch}</ul>'
            f'<a class="ind-more" href="{d["slug"]}/index.html">Explore {esc(d["name"])}</a></div>'
            f'<figure class="ind-img">{img_tag(ctx, d, p)}</figure></div></div></li>')
    body = (HERO.format(crumb="", pill="/ INDUSTRIES I SERVE", h1="Industries I serve", p=P.format(esc(intro)))
            + f'<section class="axs axs-light svd-ind inx-list" data-screen-label="Industries"><div class="axs-in axs-stack">'
            f'<ul class="ind-list">{"".join(rows)}</ul></div>{IND_JS}</section>' + cta(p))
    title = "Industries I Serve | Muhammad Babar, UI UX Designer"
    desc = "UI UX design for " + intro[:-1] if intro else "Industries I serve"
    top = head(top, title, desc, url, [("Home", f"{SITE}/"), ("Industries", None)],
               inds[0]["image"] if inds else None, inds[0].get("image_alt") if inds else "", False)
    return top + "\n  " + body + foot


def services_groups(top):
    """The service groups of the menu (titles and links), already rebased for this page."""
    mega = re.search(r'<div class="nav-mega" hidden="">.*?</div></div>(?=\s*</div>\s*<a href=)', top, re.S).group(0)
    out = []
    for gt, body in re.findall(r'<a href="[^"]*" class="scp5" style="display: block;[^"]*">([^<]*)</a>\s*<div[^>]*>(.*?)</div>', mega, re.S):
        links = re.findall(r'<a href="([^"]*)" class="scp5"[^>]*>(?:<svg.*?</svg>)?<span>(.*?)</span></a>', body, re.S)
        out.append((re.sub(r"^[✳\s]*(?:&nbsp;)?\s*", "", gt).strip(), links))
    return out


def detail_page(stage, d, inds, cards, ctx):
    slug = d["slug"]
    top, foot = shell(stage, f"industries/{slug}")
    p = "../../"
    url = f"{SITE}/industries/{slug}/"
    n = inds.index(d) + 1
    has_text = bool(str(d.get("overview") or "").strip())
    out = [HERO.format(crumb=crumb(p, d["name"]), pill=f"/ {n:02d} · {esc(str(d.get('tagline') or '').upper())}",
                       h1=esc(d.get("headline") or d["name"]), p=P.format(esc(d["summary"])))]
    # what I design: the focus areas, with the industry image
    focus = [f for f in d.get("focus") or [] if str(f).strip()]
    cards_html = "".join(f'<article class="axs-card"><span class="axs-no" aria-hidden="true">/{i + 1:02d}</span><h3 class="axs-ct">{esc(f)}</h3></article>'
                         for i, f in enumerate(focus))
    out.append(f'<section class="axs axs-light inx-focus" data-screen-label="Focus"><div class="axs-in inx-two">'
               f'<div class="inx-fl"><span class="pr-tag">/ What I design</span><div class="axs-cards inx-cards">{cards_html}</div></div>'
               f'<figure class="inx-pic">{img_tag(ctx, d, p)}</figure></div></section>')
    if has_text:
        out.append(f'<section class="axs axs-light csx-sec" data-screen-label="Overview"><div class="axs-in axs-stack"><div class="csx-row">'
                   f'<span class="pr-tag">/ Overview</span><div class="csx-main"><div class="csx-prose">{cms.md_html(d["overview"], ctx, p)}</div></div></div></div></section>')
    ch = [c for c in d.get("challenges") or [] if str(c.get("title") or "").strip()]
    if ch:
        items = "".join(f'<article class="axs-card"><span class="axs-no" aria-hidden="true">/{i + 1:02d}</span><h3 class="axs-ct">{esc(c["title"])}</h3>'
                        + (f'<p class="axs-cd">{esc(c.get("text"))}</p>' if c.get("text") else "") + "</article>" for i, c in enumerate(ch))
        out.append(f'<section class="axs axs-dark" data-screen-label="Challenges"><div class="axs-in axs-stack"><div class="axs-hd"><span class="pr-tag">/ Challenges</span></div>'
                   f'<div class="axs-cards axs-c{min(len(ch), 4)}">{items}</div></div></section>')
    # case studies in this industry
    m = str(d.get("work_match") or "").strip().upper()
    mine = [c for c in cards if m and html.unescape(c["cat"]).upper().startswith(m)]
    if mine:
        import work2
        cs = ""
        for c in mine:
            tags = "".join(f'<span class="wkx-tag">{t.strip()}</span>' for t in c["cat"].split("·"))
            img = rebase(c["img"], "work", f"industries/{slug}")
            href = rebase(f'href="{c["href"]}"', "work", f"industries/{slug}") if c["href"] else ""
            tag = "a" if href else "div"
            stats = " ".join(f"<span>{v}</span> <span>{k}</span>" for v, k in c["stats"])
            cs += (f'<{tag} {href + " " if href else ""}class="svd-case wkx-card"><figure class="svd-cimg">{img}'
                   f'<div class="wkx-ov" aria-hidden="true"><div class="wkx-tags">{tags}</div>{work2.VIEW if href else ""}</div></figure>'
                   f'<span class="ds-sr">{c["cat"]}</span><h3 class="svd-ct">{c["title"]}</h3><span class="ds-sr">{c["summary"]} {stats}</span></{tag}>')
        out.append(f'<section class="axs axs-light svd-feat" data-screen-label="Case studies"><div class="axs-in axs-stack">'
                   f'<div class="svd-fhd"><span class="pr-tag">/ Selected work</span></div>'
                   f'<div class="svd-cases svd-n{min(len(mine), 3)}">{cs}</div></div></section>')
    # services
    groups = services_groups(top)
    gs = "".join(f'<div class="inx-sg"><span class="inx-sh">{gt}</span><ul>' + "".join(f'<li><a href="{u}">{t}</a></li>' for u, t in links) + "</ul></div>"
                 for gt, links in groups)
    out.append(f'<section class="axs axs-dark inx-svc" data-screen-label="Services"><div class="axs-in axs-stack">'
               f'<div class="axs-hd"><span class="pr-tag">/ Services</span></div><div class="inx-sgs">{gs}</div></div></section>')
    faqs = [f for f in d.get("faqs") or [] if str(f.get("question") or "").strip() and str(f.get("answer") or "").strip()]
    if faqs:
        rows = "".join(f'<details class="fqx-row"{" open" if i == 0 else ""}><summary class="fqx-q"><span class="fqx-no" aria-hidden="true">/{i + 1:02d}</span>'
                       f'<span class="fqx-qt">{esc(f["question"])}</span><span class="fqx-pm" aria-hidden="true"></span></summary>'
                       f'<div class="fqx-a">{cms.md_html(f["answer"], ctx, p)}</div></details>' for i, f in enumerate(faqs))
        out.append(f'<section class="fqx svd-faq" data-screen-label="FAQs"><div class="fqx-in"><div class="fqx-hd"><span class="pr-tag">/ FAQs</span></div>'
                   f'<div class="fqx-list">{rows}</div></div></section>')
    # other industries
    others = "".join(f'<li><a href="../{o["slug"]}/index.html">{esc(o["name"])}</a></li>' for o in inds if o is not d)
    out.append(f'<section class="axs axs-light inx-more" data-screen-label="More industries"><div class="axs-in axs-stack">'
               f'<div class="axs-hd"><span class="pr-tag">/ More industries</span></div><ul class="inx-chips">{others}</ul></div></section>')
    out.append(cta(p))
    title = d.get("seo_title") or f"{d['name']} UI UX Design | Muhammad Babar"
    desc = d.get("description") or d["summary"]
    top = head(top, title, desc, url, [("Home", f"{SITE}/"), ("Industries", f"{SITE}/industries/"), (d["name"], None)],
               d.get("image"), d.get("image_alt") or "", not has_text)
    return top + "\n  " + "\n".join(out) + foot


def place(stage, content, nav_json):
    stage, content = pathlib.Path(stage), pathlib.Path(content)
    inds = load(content / "industries")
    nav = [{"slug": d["slug"], "name": d["name"]} for d in inds]
    pathlib.Path(nav_json).write_text(json.dumps(nav, ensure_ascii=False), encoding="utf-8")
    if not inds:
        return []
    ctx = cms.Ctx(stage, content)
    cards = work_cards(stage)
    (stage / "industries").mkdir(exist_ok=True)
    (stage / "industries" / "index.html").write_text(index_page(stage, inds, ctx), encoding="utf-8")
    made = ["industries"]
    for d in inds:
        out = stage / "industries" / d["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            out.write_text(detail_page(stage, d, inds, cards, ctx), encoding="utf-8")
        except cms.ContentError as e:
            raise cms.ContentError(f"industries/{d['slug']}: {e}")
        made.append(f"industries/{d['slug']}")
    return made
