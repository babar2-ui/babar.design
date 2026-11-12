"""Build babar.info.

    python3 build.py            -> dist/          (what Netlify publishes)
                                   _build/local/  (same site with relative links: open index.html on a computer)

Steps
  1. copy site/source (the original export, never edited) to _build/stage
  2. add the admin entries (content/insights, work, industries, uploads)          site/scripts/cms.py, industries.py
  3. restyle every page in the studio design                                       site/scripts/rx.py
  4. root-absolute links, sitemap.xml, robots.txt                                  site/scripts/mkdist.py
  5. add the admin (admin/) and check that every link and image resolves           site/scripts/refcheck.py
A problem in an admin entry stops the build with a plain message, so Netlify keeps the live site as it was.
"""
import datetime, os, pathlib, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent
SCRIPTS = ROOT / "site" / "scripts"
BUILD = ROOT / "_build"
STAGE, LOCAL, DIST = BUILD / "stage", BUILD / "local", ROOT / "dist"
CONTENT = pathlib.Path(os.environ.get("CMS_CONTENT") or ROOT / "content")  # another folder only for testing


def run(*args):
    r = subprocess.run([sys.executable, *map(str, args)], cwd=ROOT)
    if r.returncode:
        sys.exit(r.returncode)


def vercel_forms(out):
    """On Vercel there is no Netlify Forms: the contact form posts to the api/contact.js function
    (emails through Resend) and the Netlify-only reCAPTCHA box is left out (the honeypot stays)."""
    n = 0
    for f in out.rglob("*.html"):
        h = f.read_text(encoding="utf-8")
        if 'data-netlify="true"' not in h:
            continue
        h = h.replace('method="POST" data-netlify="true" data-netlify-recaptcha="true"', 'method="POST" action="/api/contact" data-netlify="true"')
        h = h.replace('<div class="om-captcha" data-netlify-recaptcha="true"></div>', "")
        assert 'action="/api/contact"' in h and 'data-netlify-recaptcha="true"' not in h, f
        f.write_text(h, encoding="utf-8")
        n += 1
    print("vercel: contact form on", n, "pages posts to /api/contact")


def main():
    for d in (STAGE, LOCAL, DIST):
        if d.exists():
            shutil.rmtree(d)
    BUILD.mkdir(exist_ok=True)
    shutil.copytree(ROOT / "site" / "source", STAGE)

    sys.path.insert(0, str(SCRIPTS))
    import cms
    try:
        made = cms.place(STAGE, CONTENT)
    except cms.ContentError as e:
        sys.exit(f"\nADMIN ENTRY PROBLEM: {e}\nFix it in babar.info/admin and publish again. The live site was not changed.\n")
    import industries
    nav_json = BUILD / "industries-nav.json"
    try:
        made += industries.place(STAGE, CONTENT, nav_json)
    except cms.ContentError as e:
        sys.exit(f"\nADMIN ENTRY PROBLEM: {e}\nFix it in babar.info/admin and publish again. The live site was not changed.\n")
    os.environ["RX_INDUSTRIES"] = str(nav_json)  # the sidebar Industries menu (navsub.py)
    print("admin entries:", ", ".join(made) or "none")

    run(SCRIPTS / "rx.py", STAGE, LOCAL, ROOT / "site" / "studio" / "rx.css")
    shutil.copy2(ROOT / "site" / "studio" / "Start-Preview.bat", LOCAL / "Start-Preview.bat")
    run(SCRIPTS / "mkdist.py", LOCAL, DIST, datetime.date.today().isoformat())
    (DIST / "Start-Preview.bat").unlink(missing_ok=True)
    (DIST / "netlify.toml").unlink(missing_ok=True)  # the repository's own netlify.toml is the one Netlify reads
    robots = DIST / "robots.txt"
    robots.write_text(robots.read_text(encoding="utf-8").replace("Allow: /\n", "Allow: /\nDisallow: /admin/\n"), encoding="utf-8")
    shutil.copytree(ROOT / "admin", DIST / "admin")
    if os.environ.get("VERCEL") or os.environ.get("DEPLOY_TARGET") == "vercel":
        vercel_forms(DIST)
    run(SCRIPTS / "refcheck.py", DIST, "abs")
    run(SCRIPTS / "refcheck.py", LOCAL, "rel")
    shutil.rmtree(STAGE)
    print("done: dist/ and _build/local/")


if __name__ == "__main__":
    main()
