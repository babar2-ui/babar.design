// Contact form on Vercel: each submission is emailed to you through Resend (https://resend.com).
// Vercel → Project → Settings → Environment Variables:
//   RESEND_API_KEY  required, from resend.com → API Keys
//   CONTACT_TO      optional, default babar.13@outlook.com
//   CONTACT_FROM    optional, default "babar.info <onboarding@resend.dev>"; once babar.info is verified
//                   in Resend, use e.g. "babar.info <hello@babar.info>"
// The form posts here from the homepage and the Contact page (build.py points it at /api/contact on Vercel).

const MAX = 5000;
const SKIP = new Set(['form-name', 'bot-field', 'g-recaptcha-response']);
const LABELS = { name: 'Name', email: 'Email', phone: 'Phone', country: 'Country', description: 'About the project', message: 'Message' };

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

module.exports = async function handler(req, res) {
  const wantsPage = /text\/html/.test(req.headers.accept || '');  // form sent without JavaScript
  const done = (status, ok) => (wantsPage
    ? res.redirect(303, ok ? '/contact/?sent=1' : '/contact/?error=1')
    : res.status(status).json({ ok }));

  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false });
  }
  let body = req.body || {};
  if (typeof body === 'string') body = Object.fromEntries(new URLSearchParams(body));
  if (body['bot-field']) return done(200, true);  // honeypot filled in: a bot, quietly ignore

  const fields = Object.entries(body)
    .filter(([k, v]) => !SKIP.has(k) && typeof v === 'string' && v.trim())
    .slice(0, 20)
    .map(([k, v]) => [k, v.trim().slice(0, MAX)]);
  const get = (k) => (fields.find(([key]) => key === k) || [])[1] || '';
  const email = get('email');
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) || fields.length < 2) return done(400, false);

  const key = process.env.RESEND_API_KEY;
  if (!key) {
    console.error('contact: RESEND_API_KEY is not set');
    return done(500, false);
  }
  const who = get('name') || email;
  const text = fields.map(([k, v]) => `${LABELS[k] || k}: ${v}`).join('\n\n');
  const html = '<table cellpadding="8" style="font-family:Arial,sans-serif;font-size:14px;border-collapse:collapse">'
    + fields.map(([k, v]) => `<tr><td style="color:#666;vertical-align:top;white-space:nowrap">${esc(LABELS[k] || k)}</td>`
      + `<td style="white-space:pre-wrap">${esc(v)}</td></tr>`).join('') + '</table>';

  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: process.env.CONTACT_FROM || 'babar.info <onboarding@resend.dev>',
        to: [process.env.CONTACT_TO || 'babar.13@outlook.com'],
        reply_to: email,
        subject: `New enquiry from ${who} (babar.info)`,
        text,
        html,
      }),
    });
    if (!r.ok) {
      console.error('contact: Resend replied', r.status, (await r.text()).slice(0, 500));
      return done(502, false);
    }
    return done(200, true);
  } catch (e) {
    console.error('contact: could not reach Resend', e && e.message);
    return done(502, false);
  }
};
