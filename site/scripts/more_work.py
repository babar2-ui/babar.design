"""The end of every case study: "More case studies" with three other projects (image + title + tags),
taken in Work-page order after the current one (wrapping round). Replaces the single "Next case study"
on admin case studies and is added before the end of the original stand-alone case studies.
The block carries its own scoped styles (.mwx), so it looks the same on both kinds of page.

usage (from build.py, after the admin steps): more_work.place(stage)"""
import html, re

import industries as ind

CSS = ("<style>"
       ".mwx{background:#f2f1ee;color:#121212;padding:96px 0 104px;font-family:Archivo,system-ui,sans-serif}"
       ".mwx-in{max-width:1340px;margin:0 auto;padding:0 48px;box-sizing:border-box}"
       ".mwx-hd{display:flex;justify-content:space-between;align-items:center;gap:16px;padding-top:24px;border-top:1px solid #121212;margin-bottom:36px}"
       ".mwx-tag{font-family:'Plex Mono',ui-monospace,monospace;font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:#5d5d57}"
       ".mwx-all{font-family:'Plex Mono',ui-monospace,monospace;font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:#121212;text-decoration:none;padding:10px 16px;border:1px solid #dad9d4;border-radius:100px;transition:border-color .2s,color .2s}"
       ".mwx-all:hover{border-color:#2340ff;color:#2340ff}"
       ".mwx-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}"
       ".mwx-card{display:flex;flex-direction:column;gap:16px;color:#121212;text-decoration:none}"
       ".mwx-img{margin:0;aspect-ratio:4/3;border-radius:12px;overflow:hidden;background:#e6e5e1}"
       ".mwx-img img{display:block;width:100%;height:100%;object-fit:cover;transition:transform 1s cubic-bezier(.2,.7,.2,1)}"
       ".mwx-card:hover .mwx-img img{transform:scale(1.04)}"
       ".mwx-meta{font-family:'Plex Mono',ui-monospace,monospace;font-size:11px;letter-spacing:.05em;text-transform:uppercase;color:#5d5d57}"
       ".mwx-t{font-size:22px;line-height:1.2;letter-spacing:-.025em;font-weight:500;transition:color .2s}"
       ".mwx-card:hover .mwx-t{color:#2340ff}"
       "@media (max-width:1099px){.mwx-in{padding:0 24px}.mwx-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.mwx-card:nth-child(3){display:none}}"
       "@media (max-width:640px){.mwx{padding:64px 0 72px}.mwx-in{padding:0 16px}.mwx-grid{grid-template-columns:1fr;gap:28px}.mwx-card:nth-child(3){display:flex}.mwx-t{font-size:20px}}"
       "@media (prefers-reduced-motion:reduce){.mwx-img img{transition:none}}"
       "</style>")


def block(cards, me, slug):
    pool = [c for c in cards if c["href"]]
    idx = next((i for i, c in enumerate(pool) if c["href"].split("/")[0] == me), -1)
    picks = [pool[(idx + k) % len(pool)] for k in range(1, len(pool))] if idx >= 0 else pool
    picks = [c for c in picks if c["href"].split("/")[0] != me][:3]
    if len(picks) < 3:
        return ""
    out = ""
    for c in picks:
        img = ind.rebase(c["img"], "work", f"work/{slug}")
        img = re.sub(r" (?:sizes|srcset)=\"[^\"]*\"", "", img)
        img = img.replace("<img ", '<img loading="lazy" decoding="async" ', 1)
        href = ind.rebase(f'href="{c["href"]}"', "work", f"work/{slug}")
        meta = " · ".join(t.strip() for t in html.unescape(c["cat"]).split("·")[:2])
        out += (f'<a {href} class="mwx-card"><figure class="mwx-img">{img}</figure>'
                f'<span class="mwx-meta">{html.escape(meta)}</span><span class="mwx-t">{c["title"]}</span></a>')
    return (f'<section class="mwx" data-screen-label="More case studies">{CSS}<div class="mwx-in">'
            f'<div class="mwx-hd"><span class="mwx-tag">/ More case studies</span><a class="mwx-all" href="../index.html">All work</a></div>'
            f'<div class="mwx-grid">{out}</div></div></section>')


def place(stage):
    cards = ind.work_cards(stage)
    done = []
    for d in sorted((stage / "work").iterdir()):
        f = d / "index.html"
        if not d.is_dir() or not f.exists():
            continue
        h = f.read_text(encoding="utf-8")
        b = block(cards, d.name, d.name)
        if not b:
            continue
        m = re.search(r'<section class="axs axs-light csx-next".*?</section>', h, re.S)
        if m:  # admin case study: replaces "Next case study"
            h = h[:m.start()] + b + h[m.end():]
        elif "</main>" in h:  # original stand-alone case study: before the end of the page content
            i = h.rindex("</main>")
            h = h[:i] + b + h[i:]
        else:
            continue
        f.write_text(h, encoding="utf-8")
        done.append(d.name)
    return done
