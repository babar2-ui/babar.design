# babar.design

This is my new website and final website: **babar.info**.

## Adding a case study or a blog article

1. Go to **https://babar.info/admin** and sign in.
2. Choose **Blog articles** or **Case studies**, then **New**.
3. Fill in the form, upload images (they are converted to WebP), and click **Save**.
4. Netlify rebuilds the site; the new page is live in about 1–2 minutes.

- Blog articles appear at the top of babar.info/insights, with the same layout as the existing articles.
- Case studies appear at the top of babar.info/work, with their own page in the site's design.
- Turn on **Draft** to keep an entry saved but off the website.
- If an entry has a problem (for example a missing image), the build stops with a plain message in
  Netlify's deploy log and the live site stays as it was.

## How the site is built

```
site/source/    the original export of every page (never edited by hand)
site/studio/    rx.css (the studio design) and replacement images
site/scripts/   the scripts that restyle the pages (rx.py) and build the admin entries (cms.py)
content/        what the admin saves: insights/*.json, work/*.json, uploads/
admin/          the admin (Sveltia CMS) and its settings, config.yml
build.py        runs everything: python3 build.py
netlify.toml    build command, headers and redirects for Netlify
vercel.json     the same for Vercel
api/contact.js  Vercel only: emails each contact form message through Resend
```

`python3 build.py` (Python 3.9+, nothing to install: Markdown is bundled in `site/scripts/_vendor`) writes:

- `dist/`: what Netlify publishes
- `_build/local/`: the same site with relative links, to open on a computer (`Start-Preview.bat`)

## One-time setup

1. **Netlify**: open the babar-info project → Project configuration → Build & deploy → Link repository →
   GitHub → `babar2-ui/babar.design`, branch `main`. The build settings come from `netlify.toml`.
2. **Admin sign-in**, pick one:
   - **Access token** (quickest): on GitHub, Settings → Developer settings → Fine-grained tokens → Generate.
     Repository access: only `babar2-ui/babar.design`; permission **Contents: Read and write**.
     At babar.info/admin choose *Sign In Using Access Token* and paste it (it stays in that browser only).
   - **Sign in with GitHub**: on GitHub, Settings → Developer settings → OAuth Apps → New:
     homepage `https://babar.info`, callback `https://api.netlify.com/auth/done`. Then in Netlify,
     Project configuration → Access & security → OAuth → Install provider → GitHub, with the app's
     client ID and secret.

## Hosting on Vercel

1. vercel.com → Add New → Project → import `babar2-ui/babar.design`. Leave the settings as they are;
   they come from `vercel.json` (build `python3 build.py`, output `dist`).
2. Contact form: create a free account at resend.com **with babar.13@outlook.com** (until a domain is
   verified, Resend only delivers to the account's own address), then API Keys → Create. In Vercel,
   Project → Settings → Environment Variables, add `RESEND_API_KEY` (Production and Preview) and redeploy.
   Optional: verify babar.info in Resend (Domains) and set `CONTACT_FROM` to e.g. `babar.info <hello@babar.info>`.
3. Domain: Project → Settings → Domains → add `babar.info` and `www.babar.info`, then add the DNS records
   Vercel shows at your DNS provider. When babar.info opens the Vercel site, remove the domain from Netlify.

On Vercel the form posts to `/api/contact`; on Netlify it still uses Netlify Forms. The admin works the same on both.
