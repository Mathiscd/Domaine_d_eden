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
     1. Rideau d'ouverture
     Le script de garde en <head> en a la charge : lui seul sait, avant le
     premier paint, s'il s'agit de l'arrivée sur le site ou d'une simple
     navigation interne. Il n'attend plus le chargement des images. On ne
     garde ici qu'un filet de sécurité s'il n'a pas tourné.
     ------------------------------------------------------------------ */
  setTimeout(function () { root.classList.add('is-loaded'); }, 2400);

  /* ------------------------------------------------------------------
     1 bis. Arrivée sur une ancre (chambres.html#boudoir-reves…)
     Le navigateur saute à la cible avant l'arrivée des webfonts ; la mise
     en page au-dessus se resserre ensuite d'une cinquantaine de pixels et
     mange le `scroll-margin-top`, si bien que le titre de la chambre
     finissait sous l'en-tête fixe. On rejoue le saut une fois les polices
     posées — et seulement si le visiteur n'a pas déjà pris la main.
     ------------------------------------------------------------------ */
  if (location.hash.length > 1) {
    var ancre = null;
    try { ancre = document.querySelector(location.hash); } catch (e) { ancre = null; }
    if (ancre) {
      /* On ne peut pas comparer les positions pour deviner qui a scrollé :
         le saut du navigateur vers l'ancre a lieu après ce script. On écoute
         donc le geste lui-même. */
      var mainPrise = false;
      var prendLaMain = function () { mainPrise = true; };
      ['wheel', 'touchstart', 'keydown'].forEach(function (ev) {
        window.addEventListener(ev, prendLaMain, { passive: true, once: true });
      });

      /* getBoundingClientRect() intègre le translateY(30px) de l'animation
         d'apparition tant qu'elle n'est pas jouée — on viserait 30 px trop
         bas. On remonte donc la chaîne des offsetParent, qui ignore les
         transformations. */
      var hauteurDoc = function (el) {
        var y = 0;
        for (var n = el; n; n = n.offsetParent) y += n.offsetTop;
        return y;
      };

      var recaler = function () {
        if (mainPrise) return;
        var marge = parseFloat(getComputedStyle(ancre).scrollMarginTop) || 0;
        var vise = Math.max(0, Math.round(hauteurDoc(ancre) - marge));
        if (Math.abs(vise - window.scrollY) < 2) return;
        window.scrollTo({ top: vise, behavior: 'auto' });
      };

      /* La feuille Google Fonts est chargée en `media="print"` puis promue :
         `document.fonts.ready` résout donc une première fois avant même que
         les @font-face existent. On repasse après `load`, quand la feuille
         est appliquée, puis une dernière fois au repos. */
      window.addEventListener('load', function () {
        recaler();
        if (document.fonts && document.fonts.ready) document.fonts.ready.then(recaler);
        setTimeout(recaler, 400);
      });
    }
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
    Array.prototype.forEach.call(nav.children, function (a, i) {
      if (a.tagName === 'A') a.style.setProperty('--i', i);
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

    /* `closest` et non `e.target.tagName` : le téléphone et les pictogrammes
       du pied de menu enveloppent un <span> ou un <svg>, et le clic y atterrit.
       Les ancres de la page courante (index.html#galerie depuis l'accueil) ne
       rechargent rien : sans cette fermeture, le menu resterait par-dessus la
       section visée. */
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) closeNav();
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
    if (el.getAttribute('data-reveal') !== 'mask') return el;
    // <picture> est en display:contents : il n'a pas de boite, donc pas d'aire
    // d'intersection. On remonte jusqu'au premier parent qui en a une.
    var p = el.parentElement;
    while (p && p.tagName === 'PICTURE') p = p.parentElement;
    return p || el;
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

    /* Deux pièges à éviter ici.
       1. Mesurer l'image elle-même : son rect inclut la translation qu'on vient de
          lui appliquer, donc le décalage se cumule d'un cadre à l'autre. On mesure
          donc un parent, que la parallaxe ne bouge jamais (en sautant les <picture>,
          qui sont en display:contents et n'ont pas de boîte).
       2. Mémoriser les positions une fois pour toutes : les images en chargement
          différé déplacent la page après coup, et le repère devient faux. On relit
          donc à chaque cadre — mais toutes les lectures d'abord, toutes les
          écritures ensuite, pour n'imposer qu'un seul calcul de mise en page. */
    var mesures = pxItems.map(function (el) {
      var ref = el.parentElement;
      while (ref && ref.tagName === 'PICTURE') ref = ref.parentElement;
      return { el: el, ref: ref || el, vitesse: parseFloat(el.getAttribute('data-parallax')) || 0.1 };
    });

    var bouge = function () {
      var vh = window.innerHeight;
      var i, o;
      for (i = 0; i < mesures.length; i++) {          // lectures groupées
        o = mesures[i];
        var r = o.ref.getBoundingClientRect();
        o.haut = r.top;
        o.demi = r.height / 2;
      }
      for (i = 0; i < mesures.length; i++) {          // puis écritures groupées
        o = mesures[i];
        if (o.haut > vh + 200 || o.haut + o.demi * 2 < -200) continue;
        // -1 (au-dessus) → 1 (en dessous)
        var pos = (o.haut + o.demi - vh / 2) / (vh / 2 + o.demi);
        o.el.style.transform = 'translate3d(0,' + (pos * o.vitesse * 100).toFixed(2) + 'px,0)';
      }
      pxTicking = false;
    };

    var planifie = function () {
      if (!pxTicking) { pxTicking = true; window.requestAnimationFrame(bouge); }
    };

    window.addEventListener('scroll', planifie, { passive: true });
    window.addEventListener('resize', planifie, { passive: true });
    window.addEventListener('load', planifie);
    bouge();
  }

  /* ------------------------------------------------------------------
     6. Scroll-spy : la nav souligne la section courante
     ------------------------------------------------------------------ */
  /* Toutes les entrées de la nav portent la forme absolue-relative
     `index.html#domaine` — le même balisage sert sur les quatre pages, et
     « Les chambres » / « Événements » y mènent à la section de l'accueil, les
     pages de détail restant atteintes depuis cette section. On ne
     peut donc plus les reconnaître à `href^="#"` : on retient le fragment et
     on ne garde que les ancres dont la cible existe dans cette page. C'est ce
     qui cantonne le scroll-spy à l'accueil sans avoir à le tester nommément. */
  var navLinks = Array.prototype.slice.call(
    document.querySelectorAll('.main-nav a[href*="#"]')
  ).map(function (a) {
    var frag = a.getAttribute('href').split('#')[1];
    var cible = null;
    if (frag) { try { cible = document.getElementById(frag); } catch (e) { cible = null; } }
    return cible ? { a: a, frag: frag, cible: cible } : null;
  }).filter(Boolean);

  if (navLinks.length && 'IntersectionObserver' in window) {
    var marque = function (frag) {
      navLinks.forEach(function (l) {
        var actif = l.frag === frag;
        l.a.classList.toggle('is-current', actif);
        /* `aria-current="true"` (et non "page") : la section lue n'est pas une
           page, et cela laisse `aria-current="page"` au lien « Accueil ». */
        if (actif) l.a.setAttribute('aria-current', 'true');
        else if (l.a.getAttribute('aria-current') === 'true') l.a.removeAttribute('aria-current');
      });
    };

    /* La section retenue est celle qui coupe la bande centrale du viewport.
       On ne se fie pas au seul `isIntersecting` des entrées reçues : un saut
       programmatique (retour en haut, clic sur une ancre) coalesce les
       notifications, et la section quittée peut ne jamais être signalée comme
       sortie — son état restait alors collé à la nav. On relit donc la
       géométrie de toutes les cibles à chaque notification, ce qui redonne
       toujours la même réponse quel que soit le chemin parcouru. */
    var relire = function () {
      /* Même bande que le rootMargin de l'observateur : de 45 % à 50 % de la
         hauteur du viewport, mesurée depuis le haut. */
      var h = window.innerHeight;
      var haut = h * 0.45;
      var bas = h * 0.50;
      var retenue = null;
      navLinks.forEach(function (l) {
        if (retenue !== null) return;
        var r = l.cible.getBoundingClientRect();
        if (r.top < bas && r.bottom > haut) retenue = l.frag;
      });
      marque(retenue);
    };

    var spy = new IntersectionObserver(relire, { rootMargin: '-45% 0px -50% 0px' });

    navLinks.forEach(function (l) { spy.observe(l.cible); });

    /* Un saut instantané (retour en haut, ancre cliquée) peut ne franchir la
       bande d'aucune cible : l'observateur ne notifie alors rien du tout et
       l'état resterait figé. On relit donc aussi au scroll — la lecture est
       purement géométrique et déjà cadencée par le rAF du handler commun. */
    window.addEventListener('scroll', relire, { passive: true });
    window.addEventListener('resize', relire, { passive: true });
    relire();
    // la nav signale qu'un scroll-spy la pilote : le lien « page courante »
    // s'efface au profit de la section réellement lue
    var navEl = document.querySelector('.main-nav');
    if (navEl) navEl.setAttribute('data-spy', '');
  }

  /* ------------------------------------------------------------------
     7. Bandeau défilant : on duplique le groupe pour une boucle continue
     ------------------------------------------------------------------ */
  Array.prototype.forEach.call(document.querySelectorAll('.marquee__track'), function (track) {
    var group = track.querySelector('.marquee__group');
    if (group) track.appendChild(group.cloneNode(true));
  });

  /* ------------------------------------------------------------------
     8. Diaporama du hero : fondu enchaîné lent, dérive sur la vue active
     ------------------------------------------------------------------ */
  var show = document.querySelector('[data-slideshow]');

  if (show) {
    var slides = Array.prototype.slice.call(show.querySelectorAll('.hero-slide'));
    var dots = Array.prototype.slice.call(document.querySelectorAll('.hero-dots button'));
    var idx = 0;
    var timer = null;
    var demande = 0;
    var DUREE = 6800; // temps d'affichage d'une vue, fondu compris

    /* Les vues sont empilées en absolu : toutes sont « dans le viewport », si bien
       que loading="lazy" ne les différerait pas — les cinq images partaient d'un coup.
       On les appelle donc à la main, chacune juste avant son tour. */
    var charge = function (n) {
      var vue = slides[(n + slides.length) % slides.length];
      var img = vue.querySelector('img[data-src]');
      if (!img) return;
      // les <source> d'abord : c'est eux qui decident du format retenu
      Array.prototype.forEach.call(vue.querySelectorAll('[data-srcset]'), function (s) {
        s.setAttribute('srcset', s.getAttribute('data-srcset'));
        s.removeAttribute('data-srcset');
      });
      img.setAttribute('fetchpriority', 'low');
      img.src = img.getAttribute('data-src');
      img.removeAttribute('data-src');
    };

    var applique = function (n) {
      idx = n;
      slides.forEach(function (s, k) { s.classList.toggle('is-active', k === idx); });
      dots.forEach(function (d, k) { d.setAttribute('aria-current', k === idx ? 'true' : 'false'); });
      charge(idx + 1); // la suivante s'amorce pendant que celle-ci est à l'écran
    };

    var goTo = function (i) {
      var n = (i + slides.length) % slides.length;
      var jeton = ++demande;
      charge(n);
      var img = slides[n].querySelector('img');
      // saut direct sur une vue pas encore arrivée (clic sur une puce lointaine) :
      // on l'attend plutôt que de fondre vers du vide
      if (img && !img.complete) {
        var passe = function () { if (jeton === demande) applique(n); };
        img.addEventListener('load', passe, { once: true });
        img.addEventListener('error', passe, { once: true });
        return;
      }
      applique(n);
    };

    var play = function () {
      if (timer) clearInterval(timer);
      timer = setInterval(function () { goTo(idx + 1); }, DUREE);
    };

    dots.forEach(function (d, n) {
      d.addEventListener('click', function () { goTo(n); play(); });
    });

    if (slides.length > 1 && !reduce) {
      // on ne fait défiler que si l'onglet est visible : pas d'images qui sautent au retour
      document.addEventListener('visibilitychange', function () {
        if (document.hidden) { clearInterval(timer); timer = null; }
        else play();
      });
      /* La deuxième vue s'amorce après le chargement de la page, puis au premier
         temps mort : plus tôt, elle se disputerait la bande passante avec l'image
         de tete, qui est le LCP. La première bascule n'a lieu qu'à 6,8 s. */
      var amorce = function () { charge(1); };
      var auCalme = function () {
        if ('requestIdleCallback' in window) requestIdleCallback(amorce, { timeout: 2000 });
        else setTimeout(amorce, 600);
      };
      if (document.readyState === 'complete') auCalme();
      else window.addEventListener('load', auCalme);
      play();
    }
  }

  /* ------------------------------------------------------------------
     9. Galerie : visionneuse plein écran
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
      // plein ecran : on rejoue le srcset avec sizes=92vw pour obtenir une grande
      // variante, au lieu de reafficher la vignette deja en cache
      var ss = src.getAttribute('srcset');
      if (ss) { lbImg.setAttribute('sizes', '92vw'); lbImg.setAttribute('srcset', ss); }
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

  /* ------------------------------------------------------------------
     10. Chambres : mini-galerie par chambre (chambre + salle de bains)
     Une seule lightbox partagée, réalimentée avec la liste de vues de la
     chambre cliquée (data-room-photos, JSON dans l'attribut).
     ------------------------------------------------------------------ */
  var roomMedias = Array.prototype.slice.call(document.querySelectorAll('.room-detail-media[data-room-photos]'));

  if (roomMedias.length) {
    var rlb = document.createElement('div');
    rlb.className = 'room-lightbox';
    rlb.setAttribute('role', 'dialog');
    rlb.setAttribute('aria-modal', 'true');
    rlb.setAttribute('aria-label', 'Photos de la chambre');
    rlb.innerHTML =
      '<div class="room-lightbox__frame">' +
        '<button class="lb-close" aria-label="Fermer">&times;</button>' +
        '<div class="room-lightbox__stage">' +
          '<button class="lb-prev" aria-label="Photo précédente">&#8249;</button>' +
          '<img alt="">' +
          '<button class="lb-next" aria-label="Photo suivante">&#8250;</button>' +
        '</div>' +
        '<p class="room-lightbox__cap"></p>' +
        '<div class="room-lightbox__dots"></div>' +
        '<div class="room-lightbox__thumbs"></div>' +
      '</div>';
    document.body.appendChild(rlb);

    var rlbImg = rlb.querySelector('img');
    var rlbCap = rlb.querySelector('.room-lightbox__cap');
    var rlbDots = rlb.querySelector('.room-lightbox__dots');
    var rlbThumbs = rlb.querySelector('.room-lightbox__thumbs');
    var rPhotos = [];
    var rCurrent = 0;
    var rLastFocus = null;

    function rShow(i) {
      rCurrent = (i + rPhotos.length) % rPhotos.length;
      var p = rPhotos[rCurrent];
      rlbImg.src = p.src;
      rlbImg.alt = p.alt || '';
      rlbCap.textContent = p.alt || '';
      Array.prototype.forEach.call(rlbDots.children, function (d, di) {
        d.classList.toggle('is-active', di === rCurrent);
      });
      Array.prototype.forEach.call(rlbThumbs.children, function (t, ti) {
        t.classList.toggle('is-active', ti === rCurrent);
      });
    }

    function rBuild(photos) {
      rPhotos = photos;
      rlbDots.innerHTML = '';
      rlbThumbs.innerHTML = '';
      photos.forEach(function (p, i) {
        var dot = document.createElement('button');
        dot.setAttribute('aria-label', 'Photo ' + (i + 1));
        dot.addEventListener('click', function () { rShow(i); });
        rlbDots.appendChild(dot);

        var thumb = document.createElement('button');
        thumb.setAttribute('aria-label', 'Photo ' + (i + 1));
        var timg = document.createElement('img');
        timg.src = p.thumb || p.src;
        timg.alt = '';
        thumb.appendChild(timg);
        thumb.addEventListener('click', function () { rShow(i); });
        rlbThumbs.appendChild(thumb);
      });
    }

    function rOpen(photos, startAt) {
      rLastFocus = document.activeElement;
      rBuild(photos);
      rShow(startAt || 0);
      rlb.classList.add('is-open');
      document.body.style.overflow = 'hidden';
      rlb.querySelector('.lb-close').focus();
    }

    function rClose() {
      rlb.classList.remove('is-open');
      document.body.style.overflow = '';
      if (rLastFocus) rLastFocus.focus();
    }

    roomMedias.forEach(function (media) {
      var photos;
      try { photos = JSON.parse(media.getAttribute('data-room-photos')); }
      catch (e) { return; }
      if (!photos || !photos.length) return;

      var btn = media.querySelector('.room-media-btn');
      var open = function (i) { rOpen(photos, i); };

      /* La photo reste cliquable à la souris, mais sans role="button" ni
         tabindex : le vrai bouton « Voir les N photos » est déjà à
         l'intérieur — imbriquer deux commandes doublait l'arrêt de
         tabulation et produisait un bouton dans un bouton. */
      media.addEventListener('click', function () { open(0); });
      if (btn) {
        btn.addEventListener('click', function (e) { e.stopPropagation(); open(0); });
      }
    });

    rlb.querySelector('.lb-close').addEventListener('click', rClose);
    rlb.querySelector('.lb-prev').addEventListener('click', function () { rShow(rCurrent - 1); });
    rlb.querySelector('.lb-next').addEventListener('click', function () { rShow(rCurrent + 1); });
    rlb.addEventListener('click', function (e) { if (e.target === rlb) rClose(); });

    document.addEventListener('keydown', function (e) {
      if (!rlb.classList.contains('is-open')) return;
      if (e.key === 'Escape') rClose();
      if (e.key === 'ArrowLeft') rShow(rCurrent - 1);
      if (e.key === 'ArrowRight') rShow(rCurrent + 1);
    });
  }
})();
