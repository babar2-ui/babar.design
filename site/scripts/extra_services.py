"""Service pages added after the original export (content/services/<slug>.json, editable in the admin),
e.g. AI-Assisted UI/UX Design. Same building blocks and animations as the 13 original service pages
(service_detail.py), made from the About page shell like the industry pages.

Each new service is also listed wherever "AI Product Design" (or another service named in the entry's
"after" field) is listed: the Services menu, the phone menu and the Services page.

usage (from build.py, before the other admin steps): extra_services.place(stage, content)"""
import html, json, re

import cms
import industries as ind

SITE = cms.SITE
esc = cms.esc


def load(folder):
    out = []
    for f in sorted(folder.glob("*.json")) if folder.exists() else []:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except ValueError as e:
            raise cms.ContentError(f"services/{f.name}: not valid JSON ({e})")
        if d.get("draft"):
            continue
        if not cms.SLUG.match(f.stem):
            raise cms.ContentError(f"services/{f.name}: the file name must be lowercase letters, numbers and dashes")
        for k in ("name", "headline", "summary"):
            if not str(d.get(k) or "").strip():
                raise cms.ContentError(f"services/{f.stem}: '{k}' is empty")
        d["slug"] = f.stem
        out.append(d)
    return out


def add_to_menus(stage, svcs):
    """List each new service right after the service named in its "after" field, on every page."""
    for f in stage.rglob("*.html"):
        h = f.read_text(encoding="utf-8")
        rel = f.parent.relative_to(stage)
        p = "../" * (0 if str(rel) == "." else len(rel.parts))
        new = h
        for d in svcs:
            after = re.escape(d.get("after") or "AI Product Design")
            url = f'{p}services/{d["slug"]}/index.html'
            name = esc(d.get("menu_name") or d["name"])
            if url in new:
                continue
            # Services menu and the Services page list: <a href class="scp5"><svg/>?<span>Name</span><span>→</span>?</a>,
            # checked one link at a time (links never nest), so a match can never run across several links
            def dup(m):
                a = m.group(0)
                if not re.fullmatch(r'<a href="[^"]*" class="scp5"[^>]*>(?:<svg.*?</svg>)?<span>' + after + r'</span>(?:<span[^>]*>→</span>)?</a>', a, re.S):
                    return a
                b = re.sub(r'^<a href="[^"]*"', f'<a href="{url}"', a)
                b = b.replace(f"<span>{html.unescape(after.replace(chr(92), ''))}</span>", f"<span>{name}</span>", 1)
                return a + "\n                  " + b
            new = re.sub(r"<a\b[^>]*>.*?</a>", dup, new, flags=re.S)
            # phone menu
            new = re.sub(r'<a class="nd-sub"(?: aria-current="page")? href="[^"]*">' + after + r"</a>",
                         lambda m: m.group(0) + f'\n      <a class="nd-sub" href="{url}">{name}</a>', new)
        if new != h:
            f.write_text(new, encoding="utf-8")


def crumb(p, name):
    return (f'    <nav aria-label="Breadcrumb" style="display: flex; gap: 8px; font-size: 13px; color: rgb(138, 138, 132);"><a href="{p}index.html" class="scp5">Home</a>'
            f'<span>/</span><a href="../index.html" class="scp5">Services</a><span>/</span><span style="color: rgb(201, 201, 196);">{esc(name)}</span></nav>\n')


def page(stage, d, ctx):
    import capabilities2, process2
    slug = d["slug"]
    top, foot = ind.shell(stage, f"services/{slug}")
    p = "../../"
    url = f"{SITE}/services/{slug}/"
    name = d["name"]
    hero = ind.HERO.format(crumb=crumb(p, name), pill=esc(d.get("pill") or f"/ {name.upper()}"),
                           h1=esc(d["headline"]), p=ind.P.format(esc(d.get("hero_lead") or d["summary"])))
    hero = hero.replace('data-screen-label="Industries hero"', 'data-screen-label="Services hero"', 1)
    out = [hero.replace("  </section>", ind.HERO_BTNS.format(p=p) + "  </section>", 1)]
    body = cms.md_html(d.get("overview") or "", ctx, p).replace("<p>", '<p class="axs-p">')
    pic = f'<figure class="axs-pic svd-pic">{ctx.img(d["image"], d.get("image_alt") or "", p, extra=cms.LAZY)}</figure>' if d.get("image") else ""
    out.append(f'<section class="axs axs-light svd-ov" data-screen-label="Overview"><div class="axs-in axs-stack">'
               f'<div class="axs-hd"><span class="pr-tag">/ Overview</span><p class="axs-lead">{esc(d["summary"])}</p></div>'
               f'<div class="svd-two{"" if pic else " is-solo"}"><div class="svd-copy">{body}</div>{pic}</div></div></section>')
    ch = ind._items(d, "challenges")
    if ch:
        cards = "".join(f'<article class="axs-card"><span class="axs-no" aria-hidden="true">/{i + 1:02d}</span>'
                        f'<h3 class="axs-ct">{esc(c["title"])}</h3><p class="axs-cd">{esc(c.get("text"))}</p></article>' for i, c in enumerate(ch))
        out.append(f'<section class="axs axs-dark" data-screen-label="The challenge"><div class="axs-in axs-stack">'
                   f'{ind._h2("THE CHALLENGE")}<div class="axs-cards axs-c{min(len(ch), 4)} svd-cards">{cards}</div></div></section>')
    wd = ind._items(d, "what_i_do")
    if wd:
        panels = "".join(
            f'<li class="cpx-p{" is-on" if i == 0 else ""}" style="--i:{i}">'
            f'<div class="cpx-strip"><h3 class="cpx-t"><button type="button" class="cpx-btn" aria-expanded="{"true" if i == 0 else "false"}">{esc(x["title"])}</button></h3>'
            f'<span class="cpx-no" aria-hidden="true">/{i + 1:02d}</span></div>'
            f'<div class="cpx-body"><span class="cpx-num" aria-hidden="true" data-n="{i + 1:02d}"></span><p class="cpx-d">{esc(x.get("text"))}</p></div></li>'
            for i, x in enumerate(wd))
        out.append(f'<section data-screen-label="What I do" class="cpx cpx-about svd-cpx" style="--n:{len(wd)}"><div class="cpx-pin">'
                   f'<div class="cpx-hd">{ind._h2("WHAT I DO")}</div><ul class="cpx-row">{panels}</ul></div>{capabilities2.SCRIPT}</section>')
    ap = ind._items(d, "approach")
    if ap:
        steps = "".join(
            f'<li class="prx-card" style="--i:{i}"><span class="prx-no" aria-hidden="true">/{i + 1:02d}</span>'
            f'<span class="prx-big" aria-hidden="true" data-n="{i + 1:02d}"></span>'
            f'<div class="prx-b"><h3 class="prx-t">{esc(x["title"])}</h3><p class="prx-p">{esc(x.get("text"))}</p></div></li>' for i, x in enumerate(ap))
        out.append(f'<section class="prx svd-prx" data-screen-label="My approach" style="--n:{len(ap)}"><div class="prx-pin">'
                   f'<ol class="prx-stage">{steps}</ol><div class="prx-r">{ind._h2("MY APPROACH", "prx-h")}<div class="prx-foot prx-foot-line"></div></div>'
                   f'</div>{process2.SCRIPT}</section>')
    wg = ind._items(d, "deliverables")
    if wg:
        rows = "".join(f'<li class="axs-row"><span class="axs-no" aria-hidden="true">/{i + 1:02d}</span>'
                       f'<h3 class="axs-rt">{esc(x["title"])}</h3><p class="axs-rd">{esc(x.get("text"))}</p></li>' for i, x in enumerate(wg))
        out.append(f'<section class="axs axs-light" data-screen-label="What you get"><div class="axs-in axs-split">'
                   f'<div class="axs-hd">{ind._h2("WHAT YOU GET")}</div><ol class="axs-rows">{rows}</ol></div></section>')
    wy = ind._items(d, "why")
    if wy:
        rows = "".join(f'<li class="svd-why"><span class="axs-no" aria-hidden="true">/{i + 1:02d}</span>'
                       f'<h3 class="svd-wt">{esc(x["title"])}</h3><p class="svd-wd">{esc(x.get("text"))}</p></li>' for i, x in enumerate(wy))
        out.append(f'<section class="axs axs-dark" data-screen-label="Why work with me"><div class="axs-in axs-stack">'
                   f'{ind._h2("WHY WORK WITH ME")}<div class="svd-two is-solo"><ol class="svd-whys">{rows}</ol></div></div></section>')
    # related reading and services, as chips
    rel = [r for r in d.get("related") or [] if str(r.get("label") or "").strip() and str(r.get("link") or "").startswith("/")]
    if rel:
        chips = "".join(f'<li><a href="{ctx.rel(r["link"], p)}">{esc(r["label"])}</a></li>' for r in rel)
        out.append(f'<section class="axs axs-light inx-more" data-screen-label="Related"><div class="axs-in axs-stack">'
                   f'<div class="axs-hd"><span class="pr-tag">/ Related</span></div><ul class="inx-chips">{chips}</ul></div></section>')
    out.append(ind.tools_section(stage, slug))
    faqs = [f for f in d.get("faqs") or [] if str(f.get("question") or "").strip() and str(f.get("answer") or "").strip()]
    if faqs:
        rows = "".join(f'<details class="fqx-row"{" open" if i == 0 else ""}><summary class="fqx-q"><span class="fqx-no" aria-hidden="true">/{i + 1:02d}</span>'
                       f'<span class="fqx-qt">{esc(f["question"])}</span><span class="fqx-pm" aria-hidden="true"></span></summary>'
                       f'<div class="fqx-a">{cms.md_html(f["answer"], ctx, p)}</div></details>' for i, f in enumerate(faqs))
        out.append(f'<section class="fqx svd-faq" data-screen-label="FAQs"><div class="fqx-in"><div class="fqx-hd">{ind._h2("FAQS", "fqx-h")}</div>'
                   f'<div class="fqx-list">{rows}</div></div></section>')
    out.append(ind.cta(p))
    title = d.get("seo_title") or f"{name} | Muhammad Babar"
    desc = d.get("description") or d["summary"]
    top = ind.head(top, title, desc, url, [("Home", f"{SITE}/"), ("Services", f"{SITE}/services/"), (name, None)],
                   d.get("image"), d.get("image_alt") or "", False)
    return top + "\n  " + "\n".join(out) + foot


def place(stage, content):
    svcs = load(content / "services")
    if not svcs:
        return []
    for d in svcs:
        if (stage / "services" / d["slug"]).exists():
            raise cms.ContentError(f"services/{d['slug']}: a service page with this address already exists")
    add_to_menus(stage, svcs)
    ctx = cms.Ctx(stage, content)
    made = []
    for d in svcs:
        out = stage / "services" / d["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            out.write_text(page(stage, d, ctx), encoding="utf-8")
        except cms.ContentError as e:
            raise cms.ContentError(f"services/{d['slug']}: {e}")
        made.append(f"services/{d['slug']}")
    return made
