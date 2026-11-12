"""Pages from the admin (babar.info/admin, Sveltia CMS) entries in content/.

  content/insights/<slug>.json -> insights/<slug>/index.html   same markup as the five existing articles
  content/work/<slug>.json     -> work/<slug>/index.html       case-study template in the studio style
  content/uploads/*            -> uploads/cms/*

Their cards are added to the top of the Insights and Work list pages (newest first, in the same
markup as the existing cards, so the list pages' own restyling and the industry filter apply).
Runs on the staged copy of site/source, before rx.py, so every new page gets the same sidebar,
footer and stylesheet as the rest of the site.

usage (from build.py): cms.place(stage_dir, content_dir)"""
import datetime, html, json, pathlib, re, shutil, struct

import markdown

SITE = "https://babar.info"
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


class ContentError(Exception):
    pass


def esc(s):
    return html.escape(str(s or ""), quote=True)


# ---------------------------------------------------------------- images
def imgsize(path):
    """(width, height) for webp / png / jpeg / gif, or None."""
    try:
        b = path.read_bytes()[:65536]
    except OSError:
        return None
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        kind = b[12:16]
        if kind == b"VP8X":
            return 1 + int.from_bytes(b[24:27], "little"), 1 + int.from_bytes(b[27:30], "little")
        if kind == b"VP8 ":
            w, h = struct.unpack("<HH", b[26:30])
            return w & 0x3FFF, h & 0x3FFF
        if kind == b"VP8L":
            v = int.from_bytes(b[21:25], "little")
            return (v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", b[16:24])
    if b[:6] in (b"GIF87a", b"GIF89a"):
        return struct.unpack("<HH", b[6:10])
    if b[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(b):
            if b[i] != 0xFF:
                i += 1
                continue
            m = b[i + 1]
            if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack(">HH", b[i + 5:i + 9])
                return w, h
            i += 2 + struct.unpack(">H", b[i + 2:i + 4])[0]
    return None


class Ctx:
    def __init__(self, stage, content):
        self.stage, self.content = stage, content

    def local(self, url):
        """/uploads/cms/x.webp -> the staged file (so sizes can be read and missing files caught)."""
        if url.startswith("/") and not url.startswith("//"):
            return self.stage / url.lstrip("/").split("?")[0]
        return None

    def rel(self, url, p):
        """Root-absolute site URL -> relative to a page at depth p ("../../"), so the open-locally build works too."""
        if not url or not url.startswith("/") or url.startswith("//"):
            return url
        path, _, frag = url.partition("#")
        path = path.lstrip("/")
        if path == "" or path.endswith("/"):
            path += "index.html"
        return p + path + ("#" + frag if frag else "")

    def img(self, url, alt, p, extra="", style="", sizes=None):
        if not url:
            raise ContentError("an image is missing")
        f = self.local(url)
        if f is not None and not f.exists():
            raise ContentError(f"image not found: {url}")
        wh = imgsize(f) if f is not None else None
        dims = f' width="{wh[0]}" height="{wh[1]}"' if wh else ""
        st = f' style="{style}"' if style else ""
        return f'<img{extra}{dims} src="{esc(self.rel(url, p))}" alt="{esc(alt)}"{st}>'


# ---------------------------------------------------------------- entries
def load(folder):
    out = []
    if not folder.exists():
        return out
    for f in sorted(folder.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except ValueError as e:
            raise ContentError(f"{f.name}: not valid JSON ({e})")
        if d.get("draft"):
            continue
        slug = f.stem
        if not SLUG.match(slug):
            raise ContentError(f"{f.name}: the file name must be lowercase letters, numbers and dashes")
        for k in ("title", "description"):
            if not str(d.get(k) or "").strip():
                raise ContentError(f"{f.name}: '{k}' is empty")
        d["slug"] = slug
        d["date"] = str(d.get("date") or datetime.date.today().isoformat())[:10]
        d["updated"] = str(d.get("updated") or "")[:10]
        out.append(d)
    out.sort(key=lambda d: d["date"], reverse=True)
    return out


def day(iso):
    y, m, d = iso.split("-")
    return f"{int(d)} {MONTHS[int(m) - 1]} {y}"


def words(md):
    return len(re.findall(r"[A-Za-z0-9’']+", re.sub(r"!\[[^\]]*\]\([^)]*\)|<[^>]+>|\([^)]*\)", " ", md or "")))


def md_html(src, ctx, p):
    out = markdown.markdown(src or "", extensions=["extra", "toc", "sane_lists"],
                            extension_configs={"toc": {"permalink": False}}, output_format="html")
    # internal links and images: root-absolute -> relative
    out = re.sub(r'(href|src)="(/[^/"][^"]*|/)"', lambda m: f'{m.group(1)}="{ctx.rel(m.group(2), p)}"', out)
    return out


# ---------------------------------------------------------------- head
def head(h, d, url, kind, p, ctx):
    title = d.get("seo_title") or d["title"]
    desc = d["description"]
    og = d.get("og_image") or d.get("cover")
    og_alt = d.get("og_image_alt") or d.get("cover_alt") or d["title"]
    og_abs = SITE + og if og and og.startswith("/") else og
    h = re.sub(r"<title>.*?</title>", f"<title>{esc(title)}</title>", h, count=1, flags=re.S)
    a = h.index('<meta name="description"')
    b = h.index("<style", a)
    meta = [f'<meta name="description" content="{esc(desc)}">',
            f'<link rel="canonical" href="{url}">',
            f'<link rel="alternate" hreflang="en" href="{url}">',
            f'<link rel="alternate" hreflang="x-default" href="{url}">',
            '<meta property="og:type" content="article">',
            '<meta property="og:site_name" content="Muhammad Babar">',
            f'<meta property="og:title" content="{esc(title)}">',
            f'<meta property="og:description" content="{esc(desc)}">',
            f'<meta property="og:url" content="{url}">']
    if og_abs:
        meta += [f'<meta property="og:image" content="{esc(og_abs)}">', f'<meta property="og:image:alt" content="{esc(og_alt)}">']
    meta += ['<meta name="twitter:card" content="summary_large_image">',
             f'<meta name="twitter:title" content="{esc(title)}">',
             f'<meta name="twitter:description" content="{esc(desc)}">']
    if og_abs:
        meta += [f'<meta name="twitter:image" content="{esc(og_abs)}">', f'<meta name="twitter:image:alt" content="{esc(og_alt)}">']
    meta += [f'<meta property="article:published_time" content="{d["date"]}">']
    if d["updated"]:
        meta += [f'<meta property="article:modified_time" content="{d["updated"]}">']
    meta += [f'<meta property="article:author" content="{SITE}/about/">']
    h = h[:a] + "\n".join(meta) + h[b:]
    section, sec_url = ("Insights", f"{SITE}/insights/") if kind == "insights" else ("Work", f"{SITE}/work/")
    item = {"@type": "Article" if kind == "insights" else "CreativeWork",
            "headline": d["title"], "description": desc,
            "author": {"@type": "Person", "@id": f"{SITE}/#person", "name": "Muhammad Babar",
                       "jobTitle": "Senior UI UX Designer", "url": f"{SITE}/about/"},
            "datePublished": d["date"], "url": url, "mainEntityOfPage": url, "inLanguage": "en",
            "publisher": {"@id": f"{SITE}/#person"}}
    if d["updated"]:
        item["dateModified"] = d["updated"]
    if og_abs:
        item["image"] = og_abs
    if d.get("keywords"):
        item["keywords"] = d["keywords"]
    graph = {"@context": "https://schema.org", "@graph": [
        {"@type": "Person", "@id": f"{SITE}/#person", "name": "Muhammad Babar", "url": f"{SITE}/about/"},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": section, "item": sec_url},
            {"@type": "ListItem", "position": 3, "name": d["title"]}]}, item]}
    ld = json.dumps(graph, ensure_ascii=False).replace("</", "<\\/")
    h = re.sub(r'<script type="application/ld\+json">.*?</script>',
               lambda m: f'<script type="application/ld+json">\n{ld}\n</script>', h, count=1, flags=re.S)
    return h


# ---------------------------------------------------------------- articles (same markup as the existing ones)
S_P = "margin: 0px 0px 24px;"
S_H2 = "margin: 48px 0px 16px; font-size: 26px; font-weight: 500; letter-spacing: -0.01em; color: rgb(242, 242, 239);"
S_H3 = "margin: 36px 0px 12px; font-size: 20px; font-weight: 500; letter-spacing: -0.01em; color: rgb(242, 242, 239);"
S_A = "color: rgb(242, 242, 239); border-bottom: 1px solid rgb(58, 58, 54);"
S_CODE = "font-family: ui-monospace, monospace; font-size: 14px; background: rgb(22, 22, 20); border: 1px solid rgb(34, 34, 32); border-radius: 4px; padding: 1px 6px;"
S_PILL = "border: 1px solid rgb(42, 42, 38); border-radius: 100px; padding: 8px 16px; font-size: 12px; color: rgb(201, 201, 196);"
S_GREY = "color: rgb(138, 138, 132);"
LAZY = ' loading="lazy" decoding="async"'


def style_article(body, ctx, p):
    body = re.sub(r"<p>\s*(<img [^>]*>)\s*</p>", lambda m: figure(m.group(1), ctx), body)
    body = re.sub(r"<blockquote>\s*(.*?)\s*</blockquote>", lambda m: (
        '<div style="margin: 48px 0px; border-left: 2px solid rgb(242, 242, 239); padding-left: 28px;">'
        + re.sub(r"<p>", '<p style="margin: 0px; font-size: 24px; line-height: 1.5; letter-spacing: -0.01em; color: rgb(242, 242, 239); text-wrap: pretty;">', m.group(1))
        + "</div>"), body, flags=re.S)
    body = body.replace("<p>", f'<p style="{S_P}">')
    body = re.sub(r"<h[12]( id=\"[^\"]*\")?>", lambda m: f'<h2{m.group(1) or ""} style="{S_H2}">', body).replace("</h1>", "</h2>")
    body = re.sub(r"<h([3-6])( id=\"[^\"]*\")?>", lambda m: f'<h3{m.group(2) or ""} style="{S_H3}">', body)
    body = re.sub(r"</h[4-6]>", "</h3>", body)
    body = re.sub(r"<(ul|ol)>", r'<\1 style="margin: 0px 0px 24px; padding-left: 22px;">', body)
    body = body.replace("<li>", '<li style="margin: 0px 0px 8px;">')
    body = re.sub(r'<a href="', f'<a style="{S_A}" href="', body)
    body = body.replace("<code>", f'<code style="{S_CODE}">')
    body = re.sub(r"<pre><code[^>]*>", '<pre style="margin: 0px 0px 24px; background: rgb(17, 17, 16); border: 1px solid rgb(34, 34, 32); border-radius: 8px; padding: 18px 20px; overflow-x: auto; font-size: 13px; line-height: 1.6;"><code style="font-family: ui-monospace, monospace;">', body)
    body = re.sub(r"<hr\s*/?>", '<hr style="border: 0px; border-top: 1px solid rgb(34, 34, 32); margin: 48px 0px;">', body)
    body = body.replace("<table>", '<div style="overflow-x: auto; margin: 0px 0px 24px;"><table style="width: 100%; border-collapse: collapse; font-size: 14px; line-height: 1.6;">').replace("</table>", "</table></div>")
    body = re.sub(r"<(th|td)( style=\"[^\"]*\")?>", lambda m: f'<{m.group(1)} style="text-align: left; padding: 12px 14px 12px 0px; border-top: 1px solid rgb(34, 34, 32); vertical-align: top;">', body)
    return body


def figure(img, ctx, cls=None):
    src = re.search(r'src="([^"]*)"', img).group(1)
    alt = html.unescape(re.search(r'alt="([^"]*)"', img).group(1)) if 'alt="' in img else ""
    cap = re.search(r'title="([^"]*)"', img)
    # src is already relative here: find the staged file to read its size
    f = (ctx.stage / re.sub(r"^(\.\./)+", "", src)) if not re.match(r"^[a-z]+:|//", src) else None
    if f is not None and not f.exists():
        raise ContentError(f"image not found: {src}")
    wh = imgsize(f) if f is not None else None
    dims = f' width="{wh[0]}" height="{wh[1]}"' if wh else ""
    if cls:
        tag = f'<img{dims} src="{src}" alt="{esc(alt)}" loading="lazy" decoding="async">'
        return f'<figure class="{cls}">{tag}' + (f"<figcaption>{cap.group(1)}</figcaption>" if cap else "") + "</figure>"
    tag = f'<img{dims} src="{src}" alt="{esc(alt)}" loading="lazy" decoding="async" style="width:100%;height:auto;display:block;border-radius:8px">'
    return ('<figure style="margin: 40px 0px;">' + tag
            + (f'<figcaption style="margin-top: 12px; font-size: 13px; color: rgb(138, 138, 132);">{cap.group(1)}</figcaption>' if cap else "")
            + "</figure>")


def meta_line(d):
    cat = str(d.get("category") or "Insights").strip().upper()
    mins = int(d.get("read_time") or 0) or max(1, round(words(d.get("body")) / 220))
    return cat, f"{mins} MIN READ"


def article(tpl, d, others, ctx):
    p = "../../"
    url = f"{SITE}/insights/{d['slug']}/"
    h = head(tpl, d, url, "insights", p, ctx)
    cat, read = meta_line(d)
    y, m, _ = d["date"].split("-")
    dates = f'<span style="{S_GREY}">· Published <time datetime="{d["date"]}">{day(d["date"])}</time></span>'
    if d["updated"]:
        dates += f'<span style="{S_GREY}">· Updated <time datetime="{d["updated"]}">{day(d["updated"])}</time></span>'
    crumb = esc(d.get("short_title") or d["title"])
    hero = (f'<section class="dsi" data-screen-label="Article hero" style="padding: 120px 40px 60px; max-width: 820px; margin: 0px auto;">\n'
            f'      <nav aria-label="Breadcrumb" style="display: flex; gap: 8px; font-size: 13px; color: rgb(138, 138, 132);"><a href="{p}index.html" class="scp5">Home</a><span>/</span><a href="../index.html" class="scp5">Insights</a><span>/</span><span style="color: rgb(201, 201, 196);">{crumb}</span></nav>\n'
            f'      <div class="ds-pill" style="font-size: 12px; letter-spacing: 0.12em; color: rgb(138, 138, 132); margin: 32px 0px 24px;">/ {esc(cat)} · {read} · {MONTHS[int(m) - 1].upper()} {y}</div>\n'
            f'      <h1 style="margin: 0px 0px 24px; font-size: 52px; line-height: 1.1; letter-spacing: -0.02em; font-weight: 500; text-wrap: pretty;">{esc(d["title"])}</h1>\n'
            f'      <div class="byline" style="display: flex; align-items: center; flex-wrap: wrap; gap: 8px 12px; font-size: 13px;">\n'
            f'        <img width="160" height="160" src="{p}uploads/muhammad-babar-author.webp" alt="Muhammad Babar, senior UI UX designer and article author" style="width: 36px; height: 36px; border-radius: 50%; object-fit: cover;">\n'
            f'        <a href="{p}about/index.html" rel="author">Muhammad Babar</a><span style="{S_GREY}">· Senior UI UX Designer</span>{dates}\n'
            f'      </div>\n    </section>\n\n')
    cover = (f'    <section class="dsi" data-screen-label="Article cover" style="padding: 0px 40px 60px; max-width: 1000px; margin: 0px auto;">\n'
             f'      <div class="rs-media" style="height: 420px; border-radius: 8px; overflow: hidden; position: relative; aspect-ratio: 1000 / 420;"><div style="position: absolute; inset: 0px;">'
             + ctx.img(d.get("cover"), d.get("cover_alt") or "", p, extra=' fetchpriority="high"', style="width:100%;height:100%;object-fit:cover;display:block")
             + "</div></div>\n    </section>\n\n")
    take = ""
    tk = [t for t in (d.get("takeaways") or []) if str(t).strip()]
    if tk:
        rows = "".join(f'<div style="display: flex; gap: 12px;"><span style="color: rgb(138, 138, 132); flex-shrink: 0;">{i + 1:02d}</span><span>{esc(t)}</span></div>' for i, t in enumerate(tk))
        take = ('<div style="background: rgb(17, 17, 16); border: 1px solid rgb(34, 34, 32); border-radius: 8px; padding: 28px; margin: 0px 0px 40px;">'
                '<div style="font-size: 12px; letter-spacing: 0.12em; color: rgb(138, 138, 132); margin-bottom: 16px;">KEY TAKEAWAYS</div>'
                f'<div style="display: flex; flex-direction: column; gap: 12px; font-size: 14px; line-height: 1.6;">{rows}</div></div>')
    body = style_article(md_html(d.get("body"), ctx, p), ctx, p)
    # takeaways go after the opening paragraphs (before the first heading), as in the existing articles
    k = body.find("<h2")
    body = (body[:k] + take + body[k:]) if (take and k > 0) else (take + body)
    tags = [t for t in (d.get("tags") or []) if str(t).strip()]
    tags_html = (f'<div style="display: flex; gap: 8px; flex-wrap: wrap; margin: 40px 0px 0px;">'
                 + "".join(f'<span style="{S_PILL}">{esc(t)}</span>' for t in tags) + "</div>") if tags else ""
    cta_t = d.get("cta_text") or "Planning a redesign or a new product launch?"
    cta = (f'<div style="margin-top: 60px; border-top: 1px solid rgb(34, 34, 32); padding-top: 32px; display: flex; justify-content: space-between; align-items: center; gap: 24px;">'
           f'<span style="font-size: 14px; color: rgb(138, 138, 132);">{esc(cta_t)}</span><a href="{p}contact/index.html" class="scp0" style="background: rgb(242, 242, 239); color: rgb(10, 10, 10); padding: 12px 20px; border-radius: 4px; font-size: 13px; font-weight: 500; flex-shrink: 0; white-space: nowrap;">Let’s talk</a></div>')
    body_sec = (f'    <section class="dsi" data-screen-label="Article body" style="padding: 0px 40px 100px; max-width: 680px; margin: 0px auto; font-size: 16px; line-height: 1.8; color: rgb(201, 201, 196);">\n'
                f"      {body}\n      {tags_html}\n      {cta}\n    </section>\n")
    a = h.index('<section class="dsi" data-screen-label="Article hero"')
    b = h.index('<section class="dsi" data-screen-label="Author bio"')
    h = h[:a] + hero + cover + body_sec + "    " + h[b:]
    # keep reading: the newest three other articles
    a = h.index('<section class="dsi" data-screen-label="Related articles"')
    grid = h.index('<div style="display: grid;', a)
    b = h.index("</section>", a)
    cards = "".join(
        f'\n      <a href="../{o["slug"]}/index.html" style="display: flex; flex-direction: column; gap: 12px; border-top: 1px solid rgb(34, 34, 32); padding-top: 20px;">\n'
        f'        <div style="font-size: 12px; color: rgb(138, 138, 132);">{esc(o["meta"])}</div>\n'
        f'        <div style="font-size: 18px; font-weight: 500; line-height: 1.4; letter-spacing: -0.01em;">{o["title"]}</div>\n'
        f'        <span style="font-size: 13px; color: rgb(138, 138, 132);">Read article →</span>\n      </a>'
        for o in [o for o in others if o["slug"] != d["slug"]][:3])
    h = h[:grid] + f'<div style="display: grid; grid-template-columns: repeat(3, minmax(0px, 1fr)); gap: 32px;">{cards}\n    </div>\n  ' + h[b:]
    return h


def insight_card(d, ctx):
    p = "../"
    cat, read = meta_line(d)
    img = ctx.img(d.get("cover"), d.get("cover_alt") or "", p, extra=' decoding="async" loading="lazy"', style="width:100%;height:100%;object-fit:cover;display:block")
    return (f'\n    <a href="{d["slug"]}/index.html" style="display: flex; flex-direction: column; gap: 16px;">\n'
            f'      <div class="rs-media" style="height: 240px; border-radius: 8px; overflow: hidden; position: relative; aspect-ratio: 379 / 240;"><div style="position: absolute; inset: 0px;">{img}</div></div>\n'
            f'      <div style="font-size: 12px; color: rgb(138, 138, 132);">{esc(cat)} · {read}</div>\n'
            f'      <div style="font-size: 20px; font-weight: 500; line-height: 1.35; letter-spacing: -0.01em;">{esc(d["title"])}</div>\n'
            f'      <span style="font-size: 13px; color: rgb(138, 138, 132);">Read article →</span>\n    </a>')


def existing_articles(listing):
    """Title / meta / slug of the articles already on the Insights page (for "Keep reading")."""
    out = []
    for m in re.finditer(r'<a href="(?:\.\./insights/)?([a-z0-9-]+)/index\.html" style="display: flex; flex-direction: column; gap: 16px;">(.*?)</a>', listing, re.S):
        meta = re.search(r'<div style="font-size: 12px; color: rgb\(138, 138, 132\);">(.*?)</div>', m.group(2))
        title = re.search(r'<div style="font-size: 20px;[^"]*">(.*?)</div>', m.group(2), re.S)
        if meta and title:
            out.append({"slug": m.group(1), "meta": meta.group(1), "title": title.group(1).strip()})
    return out


# ---------------------------------------------------------------- case studies (studio template)
def case_category(d):
    parts = [str(d.get(k) or "").strip().upper() for k in ("industry", "platform")]
    if d.get("year"):
        parts.append(str(d["year"]).strip())
    return " · ".join(x for x in parts if x) or "CASE STUDY"


def case(tpl, d, cases, old_cases, ctx):
    p = "../../"
    url = f"{SITE}/work/{d['slug']}/"
    h = head(tpl, d, url, "work", p, ctx)
    cat = case_category(d)
    details = [x for x in (d.get("details") or []) if str(x.get("label") or "").strip() and str(x.get("value") or "").strip()]
    det = "".join(f'<div class="csx-d"><dt>{esc(x["label"])}</dt><dd>{esc(x["value"])}</dd></div>' for x in details)
    live = (f'<a class="scp0 csx-live" href="{esc(d["live_url"])}" target="_blank" rel="noopener">View live site</a>' if d.get("live_url") else "")
    hero = (f'<section class="dsi" data-screen-label="Article hero" style="padding: 120px 40px 60px; max-width: 1200px; margin: 0px auto;">\n'
            f'      <nav aria-label="Breadcrumb" style="display: flex; gap: 8px; font-size: 13px; color: rgb(138, 138, 132);"><a href="{p}index.html" class="scp5">Home</a><span>/</span><a href="../index.html" class="scp5">Work</a><span>/</span><span style="color: rgb(201, 201, 196);">{esc(d.get("short_title") or d["title"])}</span></nav>\n'
            f'      <div class="ds-pill" style="font-size: 12px; letter-spacing: 0.12em; color: rgb(138, 138, 132); margin: 32px 0px 24px;">/ {esc(cat)}</div>\n'
            f'      <h1 style="margin: 0px 0px 24px; font-size: 52px; line-height: 1.1; letter-spacing: -0.02em; font-weight: 500; text-wrap: pretty;">{esc(d["title"])}</h1>\n'
            + (f'      <p style="margin: 0px; font-size: 15px; line-height: 1.7; color: rgb(154, 154, 148); max-width: 520px;">{esc(d.get("summary"))}</p>\n' if d.get("summary") else "")
            + (f'      <dl class="csx-dl">{det}</dl>\n' if det else "") + (f"      {live}\n" if live else "")
            + "    </section>\n")
    cover = ('<section class="axs axs-light csx-cover" data-screen-label="Case cover"><div class="axs-in"><figure class="csx-wide">'
             + ctx.img(d.get("cover"), d.get("cover_alt") or "", p, extra=' fetchpriority="high"') + "</figure></div></section>")
    out = [hero, cover]
    stats = [s for s in (d.get("stats") or []) if str(s.get("value") or "").strip()][:4]
    if stats:
        st = "".join(f'<div class="axs-scard"><dt>{esc(s.get("label"))}</dt><dd>{esc(s["value"])}</dd></div>' for s in stats)
        lead = f'<p class="axs-lead">{esc(d["results_intro"])}</p>' if d.get("results_intro") else ""
        out.append(f'<section class="axs axs-dark csx-res" data-screen-label="Results"><div class="axs-in axs-stack">'
                   f'<div class="axs-hd"><span class="pr-tag">/ Results</span>{lead}</div><dl class="axs-scards csx-n{len(stats)}">{st}</dl></div></section>')
    dark = bool(stats)
    for i, s in enumerate(d.get("sections") or []):
        heading, txt = str(s.get("heading") or "").strip(), str(s.get("body") or "").strip()
        imgs = [x for x in (s.get("images") or []) if x.get("image")]
        if not (heading or txt or imgs):
            continue
        dark = not dark
        label = str(s.get("label") or "").strip() or f"{i + 1:02d}"
        prose = md_html(txt, ctx, p)
        prose = re.sub(r"<p>\s*(<img [^>]*>)\s*</p>", lambda m: figure(m.group(1), ctx, "csx-fig"), prose)
        gal = ""
        if imgs:
            figs = "".join(f'<figure class="csx-fig">{ctx.img(x["image"], x.get("alt") or "", p, extra=LAZY)}'
                           + (f'<figcaption>{esc(x["caption"])}</figcaption>' if x.get("caption") else "") + "</figure>" for x in imgs)
            gal = f'<div class="csx-gal csx-g{min(len(imgs), 3)}">{figs}</div>'
        top = ""
        if heading or txt:
            top = (f'<div class="csx-row"><span class="pr-tag">/ {esc(label)}</span><div class="csx-main">'
                   + (f'<h2 class="csx-h">{esc(heading)}</h2>' if heading else "")
                   + (f'<div class="csx-prose">{prose}</div>' if txt else "") + "</div></div>")
        out.append(f'<section class="axs {"axs-dark" if dark else "axs-light"} csx-sec" data-screen-label="{esc(label)}"><div class="axs-in axs-stack">{top}{gal}</div></section>')
    # next case study: the next one added in the admin, then the existing case studies
    pool = cases + [c for c in old_cases if c["slug"] != d["slug"]]
    if len(pool) > 1:
        n = pool[(pool.index(d) + 1) % len(pool)]
        nimg = n["img"] if "img" in n else ctx.img(n["cover"], n.get("cover_alt") or "", p, extra=' loading="lazy" decoding="async"')
        out.append(f'<section class="axs axs-light csx-next" data-screen-label="Next case study"><div class="axs-in">'
                   f'<a class="csx-nx" href="../{n["slug"]}/index.html"><span class="pr-tag">/ Next case study</span>'
                   f'<span class="csx-nt">{esc(n["title"])}</span><figure class="csx-nimg">{nimg}</figure></a></div></section>')
    out.append(f'<section class="axs axs-cta" data-screen-label="CTA"><div class="axs-in"><h2 class="axs-ch">Want results like <span class="axs-dim">these?</span></h2>'
               f'<div class="axs-btns"><a href="{p}contact/index.html" class="axs-btn is-solid">Start a project</a></div></div></section>')
    a = h.index("<article>")
    b = h.index("</section>", h.index('data-screen-label="Related articles"')) + len("</section>")
    return h[:a] + '<article class="csx">\n    ' + "\n".join(out) + "\n  </article>" + h[b:]


def existing_cases(listing):
    """Slug / title / image of the case studies already on the Work page (for "Next case study")."""
    out = []
    for m in re.finditer(r'<a href="([a-z0-9-]+)/index\.html" style="display: grid;(.*?)</a>', listing, re.S):
        img = re.search(r"<img [^>]*>", m.group(2))
        title = re.search(r"<h3[^>]*><span class=\"sc-interp\">(.*?)</span></h3>", m.group(2))
        if img and title:
            tag = re.sub(r'(?<=["\s,])\.\./uploads/', "../../uploads/", img.group(0))
            tag = re.sub(r' (?:fetchpriority|loading|decoding|style|sizes)="[^"]*"', "", tag)
            tag = tag.replace("<img ", '<img loading="lazy" decoding="async" sizes="(max-width: 900px) 92vw, 700px" ', 1)
            out.append({"slug": m.group(1), "title": html.unescape(title.group(1)), "img": tag})
    return out


def work_card(d, ctx):
    p = "../"
    img = ctx.img(d.get("cover"), d.get("cover_alt") or "", p, extra=' decoding="async" loading="lazy"', style="width:100%;height:100%;object-fit:cover;display:block")
    stats = [s for s in (d.get("stats") or []) if str(s.get("value") or "").strip()][:2]
    st = "".join(f'<div><div style="font-size: 36px; font-weight: 500;"><span class="sc-interp">{esc(s["value"])}</span></div>'
                 f'<div style="font-size: 12px; color: rgb(138, 138, 132); margin-top: 4px;"><span class="sc-interp">{esc(s.get("label"))}</span></div></div>' for s in stats)
    return (f'\n      <a href="{d["slug"]}/index.html" style="display: grid; grid-template-columns: minmax(0px, 1fr) minmax(0px, 1fr); gap: 40px; align-items: stretch;">\n'
            f'        <div class="rs-case" style="border-radius: 8px; overflow: hidden; position: relative; min-height: 360px;">\n'
            f'          <div style="position: absolute; inset: 0px;">{img}</div>\n        </div>\n'
            f'        <div class="scp6" style="background: rgb(17, 17, 16); border: 1px solid rgb(34, 34, 32); border-radius: 8px; padding: 36px; display: flex; flex-direction: column; justify-content: space-between; gap: 32px;">\n'
            f'          <div>\n            <div style="font-size: 12px; color: rgb(138, 138, 132); margin-bottom: 14px;"><span class="sc-interp">{esc(case_category(d))}</span></div>\n'
            f'            <h3 style="margin: 0px 0px 12px; font-size: 26px; font-weight: 500; letter-spacing: -0.01em;"><span class="sc-interp">{esc(d["title"])}</span></h3>\n'
            f'            <p style="margin: 0px; font-size: 14px; line-height: 1.6; color: rgb(154, 154, 148);"><span class="sc-interp">{esc(d.get("summary") or d["description"])}</span></p>\n          </div>\n'
            f'          <div style="display: flex; justify-content: space-between; align-items: end; border-top: 1px solid rgb(34, 34, 32); padding-top: 24px;">\n'
            f'            <div style="display: flex; gap: 40px;">{st}</div>\n            <span style="font-size: 20px;">→</span>\n          </div>\n        </div>\n      </a>')


# ---------------------------------------------------------------- entry point
def place(stage, content):
    stage, content = pathlib.Path(stage), pathlib.Path(content)
    up = content / "uploads"
    if up.exists():
        dst = stage / "uploads" / "cms"
        dst.mkdir(parents=True, exist_ok=True)
        for f in up.iterdir():
            if f.is_file() and not f.name.startswith("."):
                shutil.copy2(f, dst / f.name)
    ctx = Ctx(stage, content)
    tpl = (stage / "insights" / "ui-ux-design-trends-2026" / "index.html").read_text(encoding="utf-8")
    made = []

    posts = load(content / "insights")
    lst_f = stage / "insights" / "index.html"
    lst = lst_f.read_text(encoding="utf-8")
    old = existing_articles(lst)
    taken = {o["slug"] for o in old}
    others = [{"slug": d["slug"], "meta": " · ".join(meta_line(d)), "title": esc(d["title"])} for d in posts] + old
    for d in posts:
        if d["slug"] in taken:
            raise ContentError(f"insights/{d['slug']}: an article with this address already exists")
        out = stage / "insights" / d["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            out.write_text(article(tpl, d, others, ctx), encoding="utf-8")
        except ContentError as e:
            raise ContentError(f"insights/{d['slug']}: {e}")
        made.append(f"insights/{d['slug']}")
    if posts:
        a = lst.index('data-screen-label="Articles"')
        a = lst.index(">", a) + 1
        lst = lst[:a] + "".join(insight_card(d, ctx) for d in posts) + lst[a:]
        lst_f.write_text(lst, encoding="utf-8")

    cases = load(content / "work")
    wl_f = stage / "work" / "index.html"
    wl = wl_f.read_text(encoding="utf-8")
    old_cases = existing_cases(wl)
    for d in cases:
        if (stage / "work" / d["slug"]).exists():
            raise ContentError(f"work/{d['slug']}: a case study with this address already exists")
        if not d.get("cover"):
            raise ContentError(f"work/{d['slug']}: the cover image is missing")
    for d in cases:
        out = stage / "work" / d["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            import industries  # the article shell's own links point from insights/; rebase them for work/<slug>/
            out.write_text(case(industries.rebase(tpl, "insights/ui-ux-design-trends-2026", f"work/{d['slug']}"), d, cases, old_cases, ctx), encoding="utf-8")
        except ContentError as e:
            raise ContentError(f"work/{d['slug']}: {e}")
        made.append(f"work/{d['slug']}")
    if cases:
        k = '<h2 class="ds-sr">Case studies</h2>'
        a = wl.index(k) + len(k)
        wl = wl[:a] + "".join(work_card(d, ctx) for d in cases) + wl[a:]
        wl_f.write_text(wl, encoding="utf-8")
    return made
