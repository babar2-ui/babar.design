"""No long dashes anywhere on the site (owner's rule): every em dash (—) and spaced en dash (–) in page
text, alt text, labels and page titles is rewritten. Runs on the finished pages, so it also covers
admin entries.
  "SIPPO — a bubble tea brand"   -> "SIPPO: a bubble tea brand"   (a short name before the dash)
  "… for teams — fast and easy"  -> "… for teams, fast and easy"  (inside a sentence)
  "2–4 weeks"                    -> "2-4 weeks"                    (number ranges)
Stylesheets and scripts are left alone, except the JSON-LD data, which repeats page titles.

usage: nodash.py <build dir>"""
import pathlib, re, sys

NAME = re.compile(r"\s*[A-Z0-9][\w.&'’]*(?: [A-Z0-9][\w.&'’]*)?\s*")
DASH = re.compile(r"\s+[—–]\s+|\s*—\s*")


def fix_text(t):
    if "—" not in t and "–" not in t:
        return t
    t = re.sub(r"(\d)\s*–\s*(\d)", r"\1-\2", t)
    out, last = [], 0
    for m in DASH.finditer(t):
        left = t[last:m.start()]
        seg_start = max(left.rfind(". "), left.rfind("| "), left.rfind("\n"))
        tail = left[seg_start + 2:] if seg_start >= 0 else left
        sep = ": " if NAME.fullmatch(tail) else ", "
        if m.end() == len(t) or not t[m.end():].strip():
            sep = ""
        out.append(left.rstrip(" ,") + sep)
        last = m.end()
    out.append(t[last:])
    return "".join(out).replace("–", "-")


ATTR = re.compile(r'\b(alt|title|aria-label|content|placeholder)="([^"]*)"')


def fix_html(h):
    parts = re.split(r"(<script\b.*?</script>|<style\b.*?</style>)", h, flags=re.S)
    for i, p in enumerate(parts):
        if i % 2:
            if p.startswith('<script type="application/ld+json"'):
                parts[i] = fix_text(p)
            continue
        bits = re.split(r"(<[^>]+>)", p)
        for j, b in enumerate(bits):
            if j % 2:
                bits[j] = ATTR.sub(lambda m: f'{m.group(1)}="{fix_text(m.group(2))}"', b)
            else:
                bits[j] = fix_text(b)
        parts[i] = "".join(bits)
    return "".join(parts)


if __name__ == "__main__":
    root = pathlib.Path(sys.argv[1])
    n = 0
    for f in root.rglob("*.html"):
        h = f.read_text(encoding="utf-8")
        h2 = fix_html(h)
        if h2 != h:
            f.write_text(h2, encoding="utf-8")
            n += 1
    print("no long dashes:", n, "pages updated")
