/* Motion layer for the prerendered site.
 *
 * The page markup has no animation hooks, so this script finds them itself:
 * the blocks of each section reveal as they scroll in, the page headline rises
 * word by word, stat numbers count up, the closing statement lights up as you
 * read it, clickable cards lift, dark cards catch a light that follows the
 * pointer, buttons drift toward the pointer, and arrows nudge on hover.
 * Nothing runs for people who prefer reduced motion.
 */
(function () {
  'use strict';

  if (!('IntersectionObserver' in window)) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var doc = document.documentElement;
  var lite = document.body.hasAttribute('data-fx-lite'); // standalone case studies: reveals only
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var each = function (list, fn) { Array.prototype.forEach.call(list, fn); };
  var chrome = 'header, nav, site-nav, .nav-drawer, #nav-drawer, .nav-mega';
  doc.classList.add('fx-on');

  /* ---- Scroll reveal ----------------------------------------------------- */
  var settle = function (el) {
    el.addEventListener('animationend', function done(e) {
      if (e.target !== el) return;
      el.removeEventListener('animationend', done);
      el.classList.remove('fx-reveal', 'fx-img', 'fx-in', 'fx-seq');
      el.style.removeProperty('--fx-d');
    });
  };
  var io = new IntersectionObserver(function (entries) {
    var t = 0;
    entries.forEach(function (e) {
      var el = e.target;
      if (!e.isIntersecting) {
        // already scrolled past (a jump link, a restored scroll position): just show it
        if (e.boundingClientRect.bottom < 0) {
          io.unobserve(el);
          el.classList.remove('fx-reveal', 'fx-img', 'fx-title');
        }
        return;
      }
      io.unobserve(el);
      // things that arrive together come in one after another
      el.style.setProperty('--fx-d', Math.min(t, 0.8) + 's');
      t += el.classList.contains('fx-seq') ? 0.16 : 0.08; // cards in a row clearly take turns
      if (!el.classList.contains('fx-title')) settle(el);
      el.classList.add('fx-in');
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });

  var movable = function (el) {
    if (!el || el.nodeType !== 1 || el.closest(chrome) || el.closest('.reveal')) return false;
    var cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.position === 'absolute' || cs.position === 'fixed' || cs.position === 'sticky') return false;
    if (cs.animationName !== 'none' || cs.transform !== 'none') return false;
    if (el.querySelector('[style*="animation"]')) return false; // marquees and rotators keep their own motion
    if (/auto|scroll/.test(getComputedStyle(el.parentElement).overflowX)) return false; // off-screen in a swipe row
    var r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  // what is already on screen when the page opens stays put, so the first paint is never held back
  var onFirstScreen = function (el) { var r = el.getBoundingClientRect(); return r.top < window.innerHeight && r.bottom > 0; };
  var reveal = function (el) { if (onFirstScreen(el)) return; el.classList.add('fx-reveal'); io.observe(el); };

  // the page headline: wrap each word so it can rise out of a mask
  var title = [].filter.call(document.querySelectorAll('h1'), function (h) { return !h.closest(chrome); })[0];
  if (title && !lite) {
    title.setAttribute('aria-label', title.textContent.replace(/\s+/g, ' ').trim());
    var i = 0, walker = document.createTreeWalker(title, NodeFilter.SHOW_TEXT), texts = [];
    while (walker.nextNode()) texts.push(walker.currentNode);
    texts.forEach(function (t) {
      var frag = document.createDocumentFragment();
      t.textContent.split(/(\s+)/).forEach(function (part) {
        if (!part) return;
        if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
        var w = document.createElement('span'), inner = document.createElement('span');
        w.className = 'fx-w'; w.setAttribute('aria-hidden', 'true');
        inner.textContent = part; inner.style.setProperty('--fx-i', i++);
        w.appendChild(inner); frag.appendChild(w);
      });
      t.parentNode.replaceChild(frag, t);
    });
    title.classList.add('fx-title');
    io.observe(title);
  }

  // a card in a row: its top edge draws across, then its parts rise in turn,
  // and line icons draw their strokes
  var sequence = function (card) {
    card.classList.add('fx-seq');
    each(card.children, function (c, j) { c.style.setProperty('--fx-c', Math.min(j, 4)); });
    each(card.querySelectorAll('svg circle, svg rect, svg path, svg line, svg polyline, svg ellipse'), function (s) {
      var cs = getComputedStyle(s);
      if (cs.stroke !== 'none' && (cs.fill === 'none' || cs.fillOpacity === '0')) s.setAttribute('pathLength', '1');
    });
  };

  // blocks of a section: step through single-child wrappers, then take the
  // children; a grid or row of cards reveals card by card
  var itemsOf = function (root) {
    var el = root, out = [], depth = 0;
    while (el.children.length === 1 && depth++ < 5) el = el.children[0];
    var take = function (k) {
      if (k === title) return;
      if (title && k.contains(title)) { each(k.children, take); return; }
      if (!movable(k)) return;
      var cs = getComputedStyle(k), n = k.children.length;
      if ((/grid|flex/.test(cs.display)) && n >= 3 && n <= 12 && !k.matches('a, form, button, nav, ul, ol')) {
        var row = n <= 6;
        each(k.children, function (c) {
          if (!movable(c)) return;
          out.push(c);
          if (row && c.getBoundingClientRect().height < 520 && c.children.length <= 6) sequence(c);
        });
      } else out.push(k);
    };
    each(el.children, take);
    return out;
  };
  var roots = [].filter.call(document.querySelectorAll('section, [data-screen-label], [data-fx-items]'), function (s) {
    return !s.parentElement.closest('section, [data-screen-label], [data-fx-items]') && !s.closest(chrome);
  });
  roots.forEach(function (s) {
    var items = s.hasAttribute('data-fx-items') ? [].filter.call(s.children, movable) : itemsOf(s);
    items.forEach(reveal);
    if (lite) return;
    // large images settle from a slight zoom as their block arrives
    each(s.querySelectorAll('img'), function (img) {
      if (img.classList.contains('fx-reveal') || img.closest('[style*="animation"]')) return;
      var box = img.parentElement, r = img.getBoundingClientRect();
      if (r.width < 240 || getComputedStyle(box).overflow !== 'hidden' || getComputedStyle(img).transform !== 'none') return;
      if (onFirstScreen(img)) return;
      img.classList.add('fx-img'); io.observe(img);
    });
  });

  window.addEventListener('beforeprint', function () {
    each(document.querySelectorAll('.fx-reveal, .fx-img'), function (el) { el.classList.remove('fx-reveal', 'fx-img'); });
  });

  /* ---- Reading progress ------------------------------------------------- */
  if (!document.querySelector('.progress')) {
    var bar = document.createElement('div');
    bar.className = 'fx-progress'; bar.setAttribute('aria-hidden', 'true');
    document.body.appendChild(bar);
    var ticking = false;
    var paint = function () {
      ticking = false;
      var max = doc.scrollHeight - window.innerHeight;
      bar.style.transform = 'scaleX(' + (max > 0 ? Math.min(window.scrollY / max, 1) : 0) + ')';
    };
    window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(paint); } }, { passive: true });
    paint();
  }

  if (lite) return;

  /* ---- Counting numbers ------------------------------------------------- */
  each(document.querySelectorAll('body *'), function (el) {
    if (el.children.length || el.closest(chrome) || el.closest('h1, h2, h3')) return;
    var text = el.textContent.trim();
    var m = text.match(/^(\D{0,2}?)(\d[\d,]*(?:\.\d+)?)(\s?[%+×xkKmM]*\+?)$/);
    if (!m || parseFloat(getComputedStyle(el).fontSize) < 30) return;
    var target = parseFloat(m[2].replace(/,/g, '')), decimals = (m[2].split('.')[1] || '').length;
    var commas = m[2].indexOf(',') !== -1;
    var fmt = function (v) {
      var s = v.toFixed(decimals);
      return commas ? s.replace(/\B(?=(\d{3})+(?!\d))/g, ',') : s;
    };
    var run = function () {
      run = function () {};
      var t0 = performance.now(), dur = 1400 + Math.min(target, 2000) * 0.2;
      (function step(now) {
        var p = Math.min((now - t0) / dur, 1), eased = 1 - Math.pow(1 - p, 4);
        el.textContent = p < 1 ? m[1] + fmt(target * eased) + m[3] : text;
        if (p < 1) requestAnimationFrame(step);
      })(t0);
    };
    var cio = new IntersectionObserver(function (es) {
      if (es[0].isIntersecting) { cio.disconnect(); run(); }
    }, { threshold: 0.6 });
    cio.observe(el);
  });

  /* ---- Statement words light up as they are read ------------------------ */
  var glows = [];
  each(document.querySelectorAll('[data-screen-label="Statement"] p'), function (p) {
    if (p.children.length) return;
    var words = p.textContent.split(/(\s+)/);
    p.textContent = '';
    var spans = [];
    words.forEach(function (w) {
      if (/^\s*$/.test(w)) { p.appendChild(document.createTextNode(w)); return; }
      var s = document.createElement('span'); s.className = 'fx-glow-word'; s.textContent = w;
      p.appendChild(s); spans.push(s);
    });
    glows.push({ el: p, spans: spans });
  });
  if (glows.length) {
    var glowTick = false;
    var light = function () {
      glowTick = false;
      var vh = window.innerHeight;
      glows.forEach(function (g) {
        var r = g.el.getBoundingClientRect();
        var p = Math.max(0, Math.min(1, (vh * 0.85 - r.top) / (r.height + vh * 0.3)));
        var lit = Math.round(p * g.spans.length);
        g.spans.forEach(function (s, k) { s.classList.toggle('fx-lit', k < lit); });
      });
    };
    window.addEventListener('scroll', function () { if (!glowTick) { glowTick = true; requestAnimationFrame(light); } }, { passive: true });
    light();
  }

  /* ---- Arrows nudge toward where they point ----------------------------- */
  var arrowKind = { '→': '', '↗': 'fx-ne', '↓': 'fx-s', '←': 'fx-w2' };
  each(document.querySelectorAll('a, button'), function (a) {
    var walker = document.createTreeWalker(a, NodeFilter.SHOW_TEXT), nodes = [];
    while (walker.nextNode()) if (/[→↗↓←]/.test(walker.currentNode.textContent)) nodes.push(walker.currentNode);
    nodes.forEach(function (t) {
      var parent = t.parentNode;
      if (parent.classList && parent.classList.contains('fx-arrow')) return;
      var trimmed = t.textContent.trim();
      if (trimmed.length === 1 && parent !== a && parent.childNodes.length === 1) {
        parent.classList.add('fx-arrow');
        if (arrowKind[trimmed]) parent.classList.add(arrowKind[trimmed]);
        return;
      }
      var frag = document.createDocumentFragment();
      t.textContent.split(/([→↗↓←])/).forEach(function (part) {
        if (!part) return;
        if (part in arrowKind) {
          var s = document.createElement('span');
          s.className = 'fx-arrow' + (arrowKind[part] ? ' ' + arrowKind[part] : '');
          s.textContent = part; frag.appendChild(s);
        } else frag.appendChild(document.createTextNode(part));
      });
      parent.replaceChild(frag, t);
    });
  });

  /* ---- Work filter: results settle in ------------------------------------ */
  var filterBar = document.querySelector('[data-screen-label="Industry filter"]');
  var caseList = document.querySelector('[data-screen-label="Case list"]');
  if (filterBar && caseList) {
    filterBar.addEventListener('click', function (e) {
      if (!e.target.closest('button')) return;
      setTimeout(function () {
        var k = 0;
        each(caseList.children, function (c) {
          if (c.hidden) return;
          io.unobserve(c);
          c.classList.remove('fx-reveal', 'fx-in', 'fx-pop');
          void c.offsetWidth; // restart the animation
          c.style.setProperty('--fx-d', Math.min(k++ * 0.07, 0.35) + 's');
          c.classList.add('fx-pop');
        });
      }, 0);
    });
  }

  /* ---- Services rows open one by one as the list scrolls up --------------- */
  var svc = document.querySelector('[data-screen-label="Services"]');
  var panels = svc ? [].slice.call(svc.querySelectorAll('details')) : [];
  if (panels.length > 1) {
    var auto = true, current = -1;
    var fold = function (d, open) {
      if (d.open === open && !d._fx) return;
      if (d._fx) d._fx.cancel();
      var start = d.getBoundingClientRect().height;
      d.open = open;
      var end = d.getBoundingClientRect().height;
      d.open = true; // keep the text visible while it folds away
      d.style.overflow = 'hidden'; d.style.boxSizing = 'border-box';
      var anim = d._fx = d.animate({ height: [start + 'px', end + 'px'] }, { duration: 520, easing: 'cubic-bezier(.2,.7,.2,1)' });
      var finish = function () {
        if (d._fx !== anim) return;
        d._fx = null; d.open = open;
        d.style.overflow = ''; d.style.boxSizing = '';
      };
      anim.onfinish = finish; anim.oncancel = finish;
    };
    var pick = function () {
      if (!auto) return;
      var step = Math.max(140, window.innerHeight * 0.2);
      var top = panels[0].getBoundingClientRect().top;
      var k = Math.max(0, Math.min(panels.length - 1, Math.floor((window.innerHeight * 0.65 - top) / step)));
      if (k === current) return;
      current = k;
      panels.forEach(function (d, j) { fold(d, j === k); });
    };
    var svcTick = false;
    window.addEventListener('scroll', function () { if (!svcTick) { svcTick = true; requestAnimationFrame(function () { svcTick = false; pick(); }); } }, { passive: true });
    pick();
    // once someone opens or closes a row themselves, leave the rows to them
    panels.forEach(function (d) {
      d.querySelector('summary').addEventListener('click', function () {
        auto = false;
        panels.forEach(function (p) { if (p._fx) p._fx.finish(); });
      });
    });
  }

  if (!finePointer) return;

  /* ---- Cards: lift, and a light that follows the pointer ----------------- */
  each(document.querySelectorAll('a'), function (a) {
    if (a.closest(chrome)) return;
    var cs = getComputedStyle(a), r = a.getBoundingClientRect();
    if (!/block|grid|flex/.test(cs.display) || r.height < 100 || r.width < 200) return;
    if (cs.position === 'sticky' || cs.transform !== 'none') return;
    a.classList.add('fx-lift');
  });

  var darkCard = function (el) {
    var cs = getComputedStyle(el);
    if (parseFloat(cs.borderTopLeftRadius) < 6) return false;
    var r = el.getBoundingClientRect();
    if (r.width < 180 || r.height < 110 || r.width > window.innerWidth * 0.9) return false;
    var bg = cs.backgroundColor.match(/\d+(\.\d+)?/g) || [];
    var filled = bg.length >= 3 && (bg[3] === undefined || parseFloat(bg[3]) > 0.5);
    var dark = filled && (+bg[0] + +bg[1] + +bg[2]) / 3 < 40 && cs.backgroundColor !== getComputedStyle(document.body).backgroundColor;
    var outlined = !filled && parseFloat(cs.borderTopWidth) >= 1 && cs.borderTopStyle !== 'none';
    return (dark || outlined) && getComputedStyle(el, '::after').content === 'none';
  };
  var spots = [].filter.call(document.querySelectorAll('section *, [data-screen-label] *'), function (el) {
    return !el.closest(chrome) && !el.matches('img, input, textarea, select, button') && darkCard(el);
  });
  spots.forEach(function (el) {
    if (spots.some(function (o) { return o !== el && el.contains(o); })) return; // light the innermost card
    var cs = getComputedStyle(el);
    if (cs.position === 'static') el.style.position = 'relative';
    el.classList.add('fx-spot');
    el.addEventListener('pointermove', function (e) {
      var r = el.getBoundingClientRect();
      el.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      el.style.setProperty('--my', (e.clientY - r.top) + 'px');
    });
  });

  /* ---- Buttons drift toward the pointer ---------------------------------- */
  each(document.querySelectorAll('a, button'), function (b) {
    if (b.closest('nav, .nav-mega, #nav-drawer, [data-screen-label="Industry filter"]') || b.classList.contains('fx-lift')) return;
    var cs = getComputedStyle(b), r = b.getBoundingClientRect();
    var filled = cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== 'transparent';
    var outlined = parseFloat(cs.borderTopWidth) >= 1 && cs.borderTopStyle !== 'none';
    if (!(filled || outlined) || r.height < 32 || r.height > 64 || r.width < 70 || r.width > 340) return;
    if (cs.transform !== 'none' || b.textContent.trim().length > 32) return;
    b.classList.add('fx-magnet');
    b.addEventListener('pointermove', function (e) {
      var rr = b.getBoundingClientRect();
      var dx = (e.clientX - rr.left) / rr.width - 0.5, dy = (e.clientY - rr.top) / rr.height - 0.5;
      b.style.transform = 'translate(' + (dx * 10).toFixed(1) + 'px,' + (dy * 8).toFixed(1) + 'px)';
    });
    b.addEventListener('pointerleave', function () { b.style.transform = ''; });
  });
})();
