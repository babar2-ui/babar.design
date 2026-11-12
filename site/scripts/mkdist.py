"""Make the Netlify build from the open-locally build: every relative link becomes
root-absolute ("../../about/index.html" -> "/about/", "uploads/x.webp" -> "/uploads/x.webp"),
then add netlify.toml, robots.txt and sitemap.xml.
usage: mkdist.py <preview build> <dist out> <lastmod YYYY-MM-DD>"""
import pathlib, posixpath, re, shutil, sys

SRC, OUT, LASTMOD = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
SITE = "https://babar.info"
if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(SRC, OUT)

SKIP = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//|/|#|\{)", re.I)

def absolute(base_dir, url):
    if not url or SKIP.match(url):
        return url
    path, sep, rest = re.match(r"([^?#]*)([?#]?)(.*)", url).groups()
    if not path:
        return url
    full = posixpath.normpath(posixpath.join(base_dir, path)) if base_dir else posixpath.normpath(path)
    if full == "index.html":
        full = ""
    elif full.endswith("/index.html"):
        full = full[: -len("index.html")]
    return "/" + full + sep + rest

def convert(h, base_dir):
    h = re.sub(r'\b(href|src|action|poster)="([^"]*)"', lambda m: f'{m.group(1)}="{absolute(base_dir, m.group(2))}"', h)
    def srcset(m):
        parts = []
        for item in m.group(2).split(","):
            bits = item.strip().split(None, 1)
            if bits:
                bits[0] = absolute(base_dir, bits[0])
                parts.append(" ".join(bits))
        return f'{m.group(1)}="{", ".join(parts)}"'
    h = re.sub(r'\b(srcset)="([^"]*)"', srcset, h)
    h = re.sub(r"url\((['\"]?)([^)'\"]+)\1\)", lambda m: f"url({m.group(1)}{absolute(base_dir, m.group(2))}{m.group(1)})", h)
    return h

pages = []
for f in sorted(OUT.rglob("*.html")):
    rel = f.parent.relative_to(OUT).as_posix()
    base = "" if rel == "." else rel
    t = convert(f.read_text(encoding="utf-8"), base)
    f.write_text(t, encoding="utf-8")
    if '<meta name="robots" content="noindex' not in t:  # noindex pages (e.g. a short industry page) stay out of the sitemap
        pages.append("/" if not base else f"/{base}/")

(OUT / "netlify.toml").write_text('''[build]
  publish = "."

[[headers]]
  for = "/*"
  [headers.values]
    Strict-Transport-Security = "max-age=31536000; includeSubDomains"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    X-Frame-Options = "SAMEORIGIN"

[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/uploads/*"
  [headers.values]
    Cache-Control = "public, max-age=2592000"

[[headers]]
  for = "/*.html"
  [headers.values]
    Cache-Control = "public, max-age=0, must-revalidate"

[[redirects]]
  from = "/work/finpay"
  to = "/work/"
  status = 301

[[redirects]]
  from = "/work/finpay/*"
  to = "/work/"
  status = 301
''', encoding="utf-8")
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
def prio(u):
    return "1.0" if u == "/" else "0.8" if u.count("/") == 2 else "0.6"
urls = "\n".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{LASTMOD}</lastmod><priority>{prio(u)}</priority></url>" for u in pages)
(OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n', encoding="utf-8")
print(len(pages), "pages; sitemap, robots.txt, netlify.toml written")
