/* Domaine d'Éden — interactions globales
   Aucune dépendance externe. Tout est désactivé si prefers-reduced-motion. */
(function () {
  'use strict';

  var root = document.documentElement;
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.main-nav');
  var progress = document.querySelector('.scroll-progress');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ------------------------------------------------------------------
     1. Rideau d'ouverture + cascade du hero
     ------------------------------------------------------------------ */
  function openCurtain() {
    root.classList.add('is-loaded');
  }

  if (reduce) {
    openCurtain();
  } else {
    var opened = false;
    var open = function () {
      if (opened) return;
      opened = true;
      openCurtain();
    };
    window.addEventListener('load', function () { setTimeout(open, 420); });
    // filet de sécurité : jamais plus de 2,2 s de rideau
    setTimeout(open, 2200);
  }

  /* ------------------------------------------------------------------
     2. Header : solide au scroll, escamotable, jauge de lecture
     ------------------------------------------------------------------ */
  var lastY = window.scrollY;
  var ticking = false;

  function onScroll() {
    var y = window.scrollY;

    if (header) {
      header.classList.toggle('is-solid', y > 60);
      // on masque le header quand on descend, on le rend quand on remonte
      if (!header.classList.contains('nav-open')) {
        header.classList.toggle('is-hidden', y > 420 && y > lastY + 4);
      }
    }

    if (progress) {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      progress.style.transform = 'scaleX(' + (max > 0 ? Math.min(y / max, 1) : 0) + ')';
    }

    lastY = y;
    ticking = false;
  }

  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; window.requestAnimationFrame(onScroll); }
  }, { passive: true });
  onScroll();

  /* ------------------------------------------------------------------
     3. Menu mobile
     ------------------------------------------------------------------ */
  if (toggle && nav) {
    Array.prototype.forEach.call(nav.querySelectorAll('a'), function (a, i) {
      a.style.setProperty('--i', i);
    });

    var closeNav = function () {
      header.classList.remove('nav-open');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    };

    toggle.addEventListener('click', function () {
      var open = header.classList.toggle('nav-open');
      header.classList.remove('is-hidden');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.style.overflow = open ? 'hidden' : '';
    });

    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') closeNav();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && header.classList.contains('nav-open')) closeNav();
    });
  }

  /* ------------------------------------------------------------------
     4. Révélations au scroll (up / mask / fade + titres à masque)
     ------------------------------------------------------------------ */
  var revealed = Array.prototype.slice.call(
    document.querySelectorAll('[data-reveal], .reveal, .around-item')
  );

  /* Un élément en « volet » a un clip-path replié : son aire d'intersection est nulle,
     l'observateur ne se déclencherait jamais. On observe donc son parent à sa place. */
  function watchTarget(el) {
    return el.getAttribute('data-reveal') === 'mask' && el.parentElement
      ? el.parentElement
      : el;
  }

  if ('IntersectionObserver' in window && !reduce) {
    var watched = [];

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        // déjà dépassé (arrivée directe sur une ancre) → on affiche sans animer
        var passed = !entry.isIntersecting && entry.boundingClientRect.top < 0;
        if (!entry.isIntersecting && !passed) return;
        io.unobserve(entry.target);
        watched.forEach(function (pair) {
          if (pair.watch === entry.target) pair.el.classList.add('is-visible');
        });
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });

    revealed.forEach(function (el) {
      var w = watchTarget(el);
      watched.push({ el: el, watch: w });
      io.observe(w);
    });
  } else {
    revealed.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* Les lignes de titre se décalent automatiquement */
  Array.prototype.forEach.call(document.querySelectorAll('.ln'), function (el, i) {
    var siblings = el.parentNode.querySelectorAll('.ln');
    var idx = Array.prototype.indexOf.call(siblings, el);
    el.style.setProperty('--ln-delay', (idx * 110) + 'ms');
  });

  /* ------------------------------------------------------------------
     5. Parallaxe douce sur les images marquées data-parallax
     ------------------------------------------------------------------ */
  var pxItems = Array.prototype.slice.call(document.querySelectorAll('[data-parallax]'));

  if (pxItems.length && !reduce && window.matchMedia('(min-width: 900px)').matches) {
    var pxTicking = false;

    var runParallax = function () {
      var vh = window.innerHeight;
      pxItems.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.bottom < -200 || r.top > vh + 200) return;
        var speed = parseFloat(el.getAttribute('data-parallax')) || 0.1;
        // -1 (au-dessus) → 1 (en dessous)
        var pos = (r.top + r.height / 2 - vh / 2) / (vh / 2 + r.height / 2);
        el.style.transform = 'translate3d(0,' + (pos * speed * 100).toFixed(2) + 'px,0)';
      });
      pxTicking = false;
    };

    window.addEventListener('scroll', function () {
      if (!pxTicking) { pxTicking = true; window.requestAnimationFrame(runParallax); }
    }, { passive: true });
    window.addEventListener('resize', runParallax, { passive: true });
    runParallax();
  }

  /* ------------------------------------------------------------------
     6. Scroll-spy : la nav souligne la section courante
     ------------------------------------------------------------------ */
  var navLinks = Array.prototype.slice.call(
    document.querySelectorAll('.main-nav a[href^="#"]')
  );

  if (navLinks.length && 'IntersectionObserver' in window) {
    var targets = navLinks
      .map(function (a) { return document.querySelector(a.getAttribute('href')); })
      .filter(Boolean);

    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        navLinks.forEach(function (a) {
          a.classList.toggle('is-current', a.getAttribute('href') === '#' + entry.target.id);
        });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });

    targets.forEach(function (t) { spy.observe(t); });
  }

  /* ------------------------------------------------------------------
     7. Bandeau défilant : on duplique le groupe pour une boucle continue
     ------------------------------------------------------------------ */
  Array.prototype.forEach.call(document.querySelectorAll('.marquee__track'), function (track) {
    var group = track.querySelector('.marquee__group');
    if (group) track.appendChild(group.cloneNode(true));
  });

  /* ------------------------------------------------------------------
     8. Galerie : visionneuse plein écran
     ------------------------------------------------------------------ */
  var figures = Array.prototype.slice.call(document.querySelectorAll('.gallery figure'));

  if (figures.length) {
    var lb = document.createElement('div');
    lb.className = 'lightbox';
    lb.setAttribute('role', 'dialog');
    lb.setAttribute('aria-modal', 'true');
    lb.setAttribute('aria-label', 'Galerie photo');
    lb.innerHTML =
      '<button class="lb-close" aria-label="Fermer">&times;</button>' +
      '<button class="lb-prev" aria-label="Photo précédente">&#8249;</button>' +
      '<button class="lb-next" aria-label="Photo suivante">&#8250;</button>' +
      '<img alt=""><p class="lightbox__cap"></p>';
    document.body.appendChild(lb);

    var lbImg = lb.querySelector('img');
    var lbCap = lb.querySelector('.lightbox__cap');
    var current = 0;
    var lastFocus = null;

    function show(i) {
      current = (i + figures.length) % figures.length;
      var src = figures[current].querySelector('img');
      lbImg.src = src.currentSrc || src.src;
      lbImg.alt = src.alt || '';
      lbCap.textContent = src.alt || '';
    }

    function openLb(i) {
      lastFocus = document.activeElement;
      show(i);
      lb.classList.add('is-open');
      document.body.style.overflow = 'hidden';
      lb.querySelector('.lb-close').focus();
    }

    function closeLb() {
      lb.classList.remove('is-open');
      document.body.style.overflow = '';
      if (lastFocus) lastFocus.focus();
    }

    figures.forEach(function (fig, i) {
      fig.setAttribute('tabindex', '0');
      fig.setAttribute('role', 'button');
      fig.setAttribute('aria-label', 'Agrandir : ' + (fig.querySelector('img').alt || 'photo'));
      fig.addEventListener('click', function () { openLb(i); });
      fig.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openLb(i); }
      });
    });

    lb.querySelector('.lb-close').addEventListener('click', closeLb);
    lb.querySelector('.lb-prev').addEventListener('click', function () { show(current - 1); });
    lb.querySelector('.lb-next').addEventListener('click', function () { show(current + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) closeLb(); });

    document.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('is-open')) return;
      if (e.key === 'Escape') closeLb();
      if (e.key === 'ArrowLeft') show(current - 1);
      if (e.key === 'ArrowRight') show(current + 1);
    });
  }
})();
