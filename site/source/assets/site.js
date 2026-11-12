/* Behaviour for the prerendered site.
 *
 * The pages are static HTML, so the interactions the design's runtime used to
 * provide are reimplemented here: the services mega-menu, the phone menu,
 * the work page's industry filter, and contact form submission.
 */
(function () {
  'use strict';

  var EMAIL = 'babar.13@outlook.com';

  /* ---- Marquees -----------------------------------------------------------
   * Each looping band ships one copy of its content, so crawlers and screen
   * readers read it once; the seamless loop needs a second copy, added here
   * hidden from assistive tech and not focusable.
   */
  [].slice.call(document.querySelectorAll('[data-marquee]')).forEach(function (track) {
    var copy = track.firstElementChild && track.firstElementChild.cloneNode(true);
    if (!copy) return;
    copy.setAttribute('aria-hidden', 'true');
    copy.inert = true;
    [].slice.call(copy.querySelectorAll('[id]')).forEach(function (el) { el.removeAttribute('id'); });
    track.appendChild(copy);
    track.setAttribute('data-marquee', 'ready');
  });

  /* ---- Services mega-menu ------------------------------------------------ */
  var host = document.querySelector('.nav-has-menu');
  var mega = host && host.querySelector('.nav-mega');
  if (host && mega) {
    var closeTimer;
    var open = function (yes) {
      clearTimeout(closeTimer);
      if (yes) mega.hidden = false;
      else closeTimer = setTimeout(function () { mega.hidden = true; }, 120);
    };
    host.addEventListener('mouseenter', function () { open(true); });
    host.addEventListener('mouseleave', function () { open(false); });
    host.addEventListener('focusin', function () { open(true); });
    host.addEventListener('focusout', function (e) {
      if (!host.contains(e.relatedTarget)) open(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') mega.hidden = true;
    });
  }

  /* ---- Phone / tablet menu ----------------------------------------------- */
  var burger = document.querySelector('.nav-burger');
  var drawer = document.getElementById('nav-drawer');
  if (burger && drawer) {
    var setOpen = function (yes) {
      drawer.hidden = !yes;
      burger.setAttribute('aria-expanded', yes ? 'true' : 'false');
      document.documentElement.style.overflow = yes ? 'hidden' : '';
    };
    burger.addEventListener('click', function () { setOpen(drawer.hidden); });
    drawer.addEventListener('click', function (e) { if (e.target.closest('a')) setOpen(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setOpen(false); });
    window.addEventListener('resize', function () { if (window.innerWidth > 900) setOpen(false); });
  }

  /* ---- Work page industry filter ----------------------------------------- */
  var filter = document.querySelector('[data-screen-label="Industry filter"]');
  var list = document.querySelector('[data-screen-label="Case list"]');
  if (filter && list) {
    var buttons = [].slice.call(filter.querySelectorAll('button'));
    var cards = [].slice.call(list.children).filter(function (el) {
      return el.textContent.indexOf('·') !== -1;
    });
    var industryOf = function (el) {
      var m = el.textContent.replace(/\s+/g, ' ').match(/([A-Z][A-Z0-9 &+/-]*?)\s*·/);
      return m ? m[1].trim().toUpperCase() : '';
    };
    var label = function (b) { return b.textContent.trim().toUpperCase(); };
    var apply = function (active) {
      cards.forEach(function (c) {
        var ind = industryOf(c);
        // card tags can be shorter than button labels: HEALTH -> Healthcare, SAAS -> SaaS & B2B
        c.hidden = !(active === 'ALL' || (ind && (ind === active || active.indexOf(ind) === 0)));
      });
      buttons.forEach(function (b) {
        var on = label(b) === active;
        b.style.background = on ? '#f2f2ef' : 'transparent';
        b.style.color = on ? '#0a0a0a' : '#c9c9c4';
        b.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
    };
    var navH = function () { return window.innerWidth > 900 ? 75 : 81; };
    buttons.forEach(function (b) {
      b.setAttribute('type', 'button');
      b.addEventListener('click', function () {
        apply(label(b));
        // if the bar is stuck, bring the start of the filtered list back under it
        if (filter.classList.contains('is-stuck')) {
          var y = list.getBoundingClientRect().top + window.scrollY - navH() - filter.offsetHeight - 16;
          window.scrollTo({ top: y, behavior: 'smooth' });
        }
      });
    });
    apply('ALL');

    // hairline under the bar only while it is stuck
    var stuck = function () { filter.classList.toggle('is-stuck', filter.getBoundingClientRect().top <= navH() + 1 && list.getBoundingClientRect().bottom > navH() + filter.offsetHeight); };
    window.addEventListener('scroll', stuck, { passive: true });
    window.addEventListener('resize', stuck);
    stuck();
  }

  /* ---- Homepage process ---------------------------------------------------
   * The step nearest the middle of the screen is the one being read: it turns
   * dark. Without script the first step stays highlighted.
   */
  var steps = [].slice.call(document.querySelectorAll('[data-process] > li'));
  if (steps.length) {
    var stepTick = false;
    var markStep = function () {
      stepTick = false;
      var mid = window.innerHeight / 2, best = steps[0], gap = Infinity;
      steps.forEach(function (s) {
        var r = s.getBoundingClientRect(), d = Math.abs((r.top + r.bottom) / 2 - mid);
        if (d < gap) { gap = d; best = s; }
      });
      steps.forEach(function (s) { s.classList.toggle('is-on', s === best); });
    };
    window.addEventListener('scroll', function () { if (!stepTick) { stepTick = true; requestAnimationFrame(markStep); } }, { passive: true });
    window.addEventListener('resize', markStep);
    markStep();
  }

  /* ---- Homepage services ---------------------------------------------------
   * The first card starts open; each of the others opens as it scrolls into
   * view and stays open. Without script, or with reduced motion, all are open.
   */
  var svCards = [].slice.call(document.querySelectorAll('.sv-card'));
  if (svCards.length && 'IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.documentElement.classList.add('sv-js');
    svCards[0].classList.add('is-open');
      // strictly in order: a card opens only once the one before it has finished
    // opening, and only while it is still in view (opening pushes it down)
    var svSeen = svCards.map(function () { return false; }), svBusy = false;
    var svNext = function () {
      if (svBusy) return;
      for (var i = 1; i < svCards.length; i++) if (!svCards[i].classList.contains('is-open')) break;
      if (i === svCards.length || !svSeen[i]) return;
      svCards[i].classList.add('is-open'); svBusy = true;
      setTimeout(function () { svBusy = false; svNext(); }, 750);
    };
    var svIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { svSeen[svCards.indexOf(en.target)] = en.isIntersecting; });
      svNext();
    }, { rootMargin: '0px 0px -65% 0px' });
    svCards.forEach(function (c) { svIO.observe(c); });
  }

  /* ---- Contact forms ------------------------------------------------------
   * Submissions go to Netlify Forms on this site's own host (same-origin POST);
   * Netlify emails each one on to the address set in Forms -> Notifications.
   * Without JavaScript the form still submits natively.
   */
  [].slice.call(document.querySelectorAll('form[data-netlify]')).forEach(function (form) {
    var submit = form.querySelector('[type="submit"]');
    if (!submit) return;
    var idle = submit.textContent;
    var status = document.createElement('p');
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');
    status.style.cssText = 'margin:4px 0 0;font-size:13px;line-height:1.5;color:#9a9a94';
    form.appendChild(status);
    var say = function (text, ok) {
      status.textContent = text;
      status.style.color = ok ? '#9a9a94' : '#e0a58a';
    };
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var email = form.querySelector('[name="email"]');
      if (email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email.value.trim())) {
        say('That email address looks incomplete — please check it.', false);
        email.focus();
        return;
      }
      // Netlify adds the reCAPTCHA widget at deploy; its answer travels in the
      // form data as g-recaptcha-response
      var captcha = form.querySelector('[data-netlify-recaptcha]') && window.grecaptcha;
      if (captcha && !grecaptcha.getResponse()) {
        say('Please tick “I’m not a robot” before sending.', false);
        return;
      }
      var data = new URLSearchParams();
      new FormData(form).forEach(function (v, k) { data.append(k, v); });
      submit.disabled = true;
      submit.textContent = 'Sending…';
      say('', true);
      fetch('/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: data.toString(),
      })
        .then(function (r) {
          if (!r.ok) throw new Error(r.status);
          say("Thanks — your message is on its way. I'll reply within a day.", true);
          form.reset();
        })
        .catch(function () {
          say("Couldn't send just now. Please email " + EMAIL + ' directly.', false);
        })
        .then(function () {
          submit.disabled = false;
          submit.textContent = idle;
          if (captcha) grecaptcha.reset(); // each answer is valid for one submission only
        });
    });
  });
})();
