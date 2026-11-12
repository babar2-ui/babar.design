"""Prove the restyle changed no copy: for every page compare visible text, title, meta tags,
JSON-LD, canonical/hreflang links and image alt text between two builds. Blocks the studio
layer adds (.rx-card, .rx-foot, .rx-big) are ignored on the new side.
usage: textdiff.py <old build> <new build>"""
import pathlib, sys
from html.parser import HTMLParser

SKIP_CLASSES = {"rx-card", "rx-foot", "rx-big", "rx-strip", "rx-hbar", "rx-reel"}
VOID = {"area","base","br","col","embed","hr","img","input","link","meta","source","track","wbr"}

class X(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True)
        s.stack = []; s.skip = 0; s.text = []; s.meta = []; s.alts = []; s.ld = []; s.in_ld = False; s.in_title = False; s.title = ""
    def handle_starttag(s, t, a):
        a = dict(a)
        cls = set((a.get("class") or "").split())
        hide = bool(cls & SKIP_CLASSES) or t in ("script", "style", "template")
        if t == "script" and a.get("type") == "application/ld+json": s.in_ld = True
        if t == "title": s.in_title = True
        if t == "meta": s.meta.append(tuple(sorted((k, v) for k, v in a.items())))
        if t == "link" and a.get("rel") in ("canonical", "alternate"): s.meta.append(("link", a.get("rel"), a.get("hreflang"), a.get("href")))
        if t == "img" and not s.skip: s.alts.append(a.get("alt"))
        if t in VOID: return
        s.stack.append(hide); s.skip += hide
    def handle_endtag(s, t):
        if t in VOID: return
        if t == "script": s.in_ld = False
        if t == "title": s.in_title = False
        if s.stack: s.skip -= s.stack.pop()
    def handle_data(s, d):
        if s.in_ld: s.ld.append(d.strip()); return
        if s.in_title: s.title += d; return
        if s.skip: return
        d = " ".join(d.replace("\u2733", " ").replace("\u2726", " ").split())
        if d: s.text.append(d)

def read(p):
    x = X(); x.feed(p.read_text(encoding="utf-8")); return x

old, new = map(pathlib.Path, sys.argv[1:3])
bad = 0; n = 0
for f in sorted(old.rglob("*.html")):
    g = new / f.relative_to(old)
    a, b = read(f), read(g); n += 1
    probs = []
    if a.title != b.title: probs.append("title")
    if sorted(map(repr, a.meta)) != sorted(map(repr, b.meta)): probs.append("meta/links")
    if a.ld != b.ld: probs.append("json-ld")
    if a.alts != b.alts:
        from collections import Counter
        ca, cb = Counter(a.alts), Counter(b.alts)
        probs.append("alt text same set, reordered" if ca == cb else f"alt removed: {list((ca-cb).elements())}; alt added: {list((cb-ca).elements())}")
    if a.text != b.text:
        from collections import Counter
        wa, wb = Counter(" ".join(a.text).split()), Counter(" ".join(b.text).split())
        if wa == wb:
            probs.append("same words, reordered")
        else:
            probs.append(f"words removed: {dict(wa - wb)}; words added: {dict(wb - wa)}")
    if probs:
        bad += 1; print("DIFF", f.relative_to(old), "->", "; ".join(probs))
print(f"{n} pages compared, {bad} with differences")
