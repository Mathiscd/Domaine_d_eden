/* Domaine d'Éden — formulaire de demande multi-étapes */
(function () {
  'use strict';

  var form = document.getElementById('resa-form');
  var panels = form.querySelectorAll('.step-panel');
  var dots = document.querySelectorAll('[data-step-dot]');
  var current = 1;

  /* ---------- Bascule séjour / événement ---------- */
  var blocSejour = form.querySelector('[data-bloc="sejour"]');
  var blocEvent = form.querySelector('[data-bloc="evenement"]');

  function syncMotif() {
    var isEvent = form.querySelector('input[name="motif"]:checked').value === 'evenement';
    blocSejour.hidden = isEvent;
    blocEvent.hidden = !isEvent;
  }
  form.querySelectorAll('input[name="motif"]').forEach(function (r) {
    r.addEventListener('change', syncMotif);
  });

  /* ---------- Pré-remplissage via URL (?chambre=…, ?motif=evenement, ?format=…) ----------
     `?format=` vient des cartes de la page Événements. Il implique le motif
     « événement », même si `motif` est absent de l'URL : on coche le bouton
     radio puis on laisse syncMotif() révéler le bloc — pas de second chemin
     qui manipulerait `hidden` à la main. */
  var params = new URLSearchParams(window.location.search);
  var format = params.get('format');

  if (params.get('motif') === 'evenement' || format) {
    var evt = form.querySelector('input[name="motif"][value="evenement"]');
    if (evt) { evt.checked = true; }
  }
  if (format) {
    /* On sélectionne par `data-slug`, jamais par libellé : ceux-ci portent des
       apostrophes typographiques et des barres obliques. */
    var typeEvt = document.getElementById('type-evenement');
    var opt = typeEvt && typeEvt.querySelector('option[data-slug="' + format + '"]');
    if (opt) { typeEvt.value = opt.value; }
  }
  if (params.get('chambre')) {
    var room = form.querySelector('input[name="chambre"][data-slug="' + params.get('chambre') + '"]');
    if (room) { room.checked = true; }
  }

  syncMotif();

  /* ---------- Dates minimales ---------- */
  var today = new Date().toISOString().split('T')[0];
  ['arrivee', 'depart', 'date-evenement'].forEach(function (id) {
    var el = document.getElementById(id);
    if (el) el.min = today;
  });
  var arrivee = document.getElementById('arrivee');
  var depart = document.getElementById('depart');
  arrivee.addEventListener('change', function () {
    if (arrivee.value) depart.min = arrivee.value;
  });

  /* ---------- Navigation entre étapes ---------- */
  function show(step) {
    current = step;
    panels.forEach(function (p) {
      p.classList.toggle('is-active', Number(p.dataset.step) === step);
    });
    dots.forEach(function (d) {
      var n = Number(d.dataset.stepDot);
      d.classList.toggle('is-active', n === step);
      d.classList.toggle('is-done', n < step);
    });
    var bar = document.querySelector('.steps-bar');
    if (bar) bar.style.display = step === 4 ? 'none' : '';
    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (step === 3) buildRecap();
  }

  function setError(field, on) {
    field.closest('.field').classList.toggle('has-error', on);
  }

  function validateStep(step) {
    var ok = true;
    if (step === 1) {
      var isEvent = form.querySelector('input[name="motif"]:checked').value === 'evenement';
      if (!isEvent) {
        if (!arrivee.value || arrivee.value < today) { setError(arrivee, true); ok = false; }
        else setError(arrivee, false);
        if (!depart.value || (arrivee.value && depart.value <= arrivee.value)) { setError(depart, true); ok = false; }
        else setError(depart, false);
      }
    }
    if (step === 2) {
      var prenom = document.getElementById('prenom');
      var nom = document.getElementById('nom');
      var email = document.getElementById('email');
      [prenom, nom].forEach(function (f) {
        var bad = !f.value.trim();
        setError(f, bad);
        if (bad) ok = false;
      });
      var badMail = !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim());
      setError(email, badMail);
      if (badMail) ok = false;
    }
    return ok;
  }

  form.addEventListener('click', function (e) {
    if (e.target.closest('[data-next]')) {
      if (validateStep(current)) show(current + 1);
    }
    if (e.target.closest('[data-prev]')) show(current - 1);
  });

  /* ---------- Récapitulatif ---------- */
  function fmtDate(v) {
    if (!v) return '—';
    return new Date(v + 'T12:00:00').toLocaleDateString('fr-FR', {
      weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
    });
  }

  function row(label, value) {
    return '<li><span class="label">' + label + '</span><span class="value">' + value + '</span></li>';
  }

  function esc(s) {
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function buildRecap() {
    var isEvent = form.querySelector('input[name="motif"]:checked').value === 'evenement';
    var html = '';
    if (isEvent) {
      html += row('Demande', 'Événement ou groupe');
      html += row('Type', esc(document.getElementById('type-evenement').value));
      html += row('Date envisagée', fmtDate(document.getElementById('date-evenement').value));
      var nb = document.getElementById('nb-personnes').value;
      html += row('Personnes', nb ? esc(nb) : '—');
      html += row('Hébergement', form.querySelector('input[name="hebergement_evt"]:checked').value === 'oui' ? 'Souhaité' : 'Sans hébergement');
    } else {
      html += row('Demande', 'Séjour en chambre d’hôtes');
      html += row('Chambre', esc(form.querySelector('input[name="chambre"]:checked').value));
      html += row('Arrivée', fmtDate(arrivee.value));
      html += row('Départ', fmtDate(depart.value));
      html += row('Voyageurs', document.getElementById('adultes').value + ' adulte(s) · ' + document.getElementById('enfants').value + ' enfant(s)');
      html += row('Table d’hôtes', form.querySelector('input[name="table"]:checked').value === 'oui' ? 'Avec plaisir' : 'Non merci');
    }
    html += row('Contact', esc(document.getElementById('prenom').value + ' ' + document.getElementById('nom').value));
    html += row('Email', esc(document.getElementById('email').value));
    var tel = document.getElementById('telephone').value.trim();
    if (tel) html += row('Téléphone', esc(tel));
    var msg = document.getElementById('message').value.trim();
    if (msg) html += row('Message', esc(msg));
    document.getElementById('recap').innerHTML = html;
  }

  /* ---------- Envoi ----------
     Point d'entrée unique pour brancher l'envoi réel (Formspree / Brevo) :
     la demande doit arriver dans la boîte mail du client, avec auto-réponse
     au visiteur (cf. proposition commerciale). */
  function submitRequest(data) {
    // TODO déploiement : POST vers le service d'envoi.
    console.log('Demande à envoyer :', data);
    return Promise.resolve();
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var rgpd = document.getElementById('rgpd');
    var rgpdError = document.getElementById('rgpd-error');
    if (!rgpd.checked) {
      rgpdError.style.display = 'block';
      return;
    }
    rgpdError.style.display = 'none';
    var data = {};
    new FormData(form).forEach(function (v, k) { data[k] = v; });
    submitRequest(data).then(function () { show(4); });
  });
})();
