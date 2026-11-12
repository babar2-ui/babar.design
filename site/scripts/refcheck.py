"""Every local href/src/srcset/url() in a build must point at a file that exists.
usage: refcheck.py <build> <abs|rel>"""
import pathlib, posixpath, re, sys
R, mode = pathlib.Path(sys.argv[1]), sys.argv[2]
SKIP = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//|#|\{)", re.I)
n = bad = 0; seen = set()
for f in R.rglob("*.html"):
    h = f.read_text(encoding="utf-8")
    h = re.sub(r'<script type="application/ld\+json".*?</script>', "", h, flags=re.S)
    urls = re.findall(r'\b(?:href|src|action|poster)="([^"]*)"', h)
    for s in re.findall(r'\bsrcset="([^"]*)"', h): urls += [i.strip().split()[0] for i in s.split(",") if i.strip()]
    urls += [u for q, u in re.findall(r"url\((['\"]?)([^)'\"]+)\1\)", h)]
    for u in urls:
        if not u or SKIP.match(u): continue
        path = re.split(r"[?#]", u)[0]
        if not path or path.startswith("/api/"): continue  # serverless functions (Vercel)
        if path.startswith("/"): t = R / path.lstrip("/")
        else: t = f.parent / path
        if t.is_dir() or path.endswith("/"): t = t / "index.html"
        n += 1
        if not t.exists():
            bad += 1
            if (f.name, u) not in seen and len(seen) < 15: seen.add((f.name, u)); print("MISSING", f.relative_to(R), u)
print(f"{n} references, {bad} missing")
sys.exit(1 if bad else 0)
