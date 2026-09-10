/* Domaine d'Éden — formulaire de demande multi-étapes */
(function () {
  'use strict';

  /* =====================================================================
     RÉGLAGES DE PRODUCTION
     ---------------------------------------------------------------------
     WEBHOOK : l'URL de production du nœud Webhook n8n. Le nœud doit être
     réglé sur **POST** (les données arrivent alors dans `$json.body`) et
     son option « Allowed Origins (CORS) » doit contenir le domaine du site
     — sans quoi le navigateur bloque la requête et rien ne part.

     WEBHOOK_TEST : la même adresse en `/webhook-test/`. Elle n'écoute que le
     temps d'un clic sur « Listen for test event » dans n8n ; en dehors, elle
     répond 404 et le formulaire affiche son message d'échec. C'est voulu :
     on essaie depuis un serveur local sans jamais écrire dans la vraie boîte
     des hôtes, et l'aiguillage se fait sur le nom d'hôte plutôt qu'en
     commentant une ligne — une ligne commentée finit toujours par partir en
     production.

     SITE_URL : le domaine public. En ligne il ne sert jamais — le script prend
     `location.origin` — mais c'est lui que reprennent les essais locaux et
     l'ouverture en `file://` (où `location.origin` vaut la chaîne "null"). Le
     logo d'un mail d'essai pointe ainsi sur une adresse réellement joignable :
     un client mail ne charge pas l'image lui-même, ce sont les serveurs de
     Gmail ou d'Outlook qui vont la chercher, et `localhost` leur est fermé.
     ===================================================================== */
  var WEBHOOK = 'https://n8n.srv1107413.hstgr.cloud/webhook/771531e2-ed8a-4f64-b110-beedd81cd96d';
  var WEBHOOK_TEST = 'https://n8n.srv1107413.hstgr.cloud/webhook-test/771531e2-ed8a-4f64-b110-beedd81cd96d';
  var PROXY = '/api/demande';
  var LOCAL = /^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname);
  var SITE_URL = 'https://domainededen.fr';

  /* La table d'hôtes est annoncée à 25 € par personne dans le formulaire
     (étape 1). Le chiffre ne sert qu'à l'estimation portée par le mail
     interne ; s'il change dans le balisage, il change ici. */
  var PRIX_TABLE = 25;

  var form = document.getElementById('resa-form');
  var panels = form.querySelectorAll('.step-panel');
  var dots = document.querySelectorAll('[data-step-dot]');
  var current = 1;
  var ouverture = Date.now();

  /* ---------- Bascule séjour / événement ---------- */
  var blocSejour = form.querySelector('[data-bloc="sejour"]');
  var blocEvent = form.querySelector('[data-bloc="evenement"]');

  function estEvenement() {
    return form.querySelector('input[name="motif"]:checked').value === 'evenement';
  }

  function syncMotif() {
    var isEvent = estEvenement();
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
      if (!estEvenement()) {
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

  /* ---------- Mise en forme ---------- */
  function fmtDate(v) {
    if (!v) return '—';
    return new Date(v + 'T12:00:00').toLocaleDateString('fr-FR', {
      weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
    });
  }

  function esc(s) {
    var d = document.createElement('div');
    d.textContent = s == null ? '' : s;
    return d.innerHTML;
  }

  function val(id) {
    var el = document.getElementById(id);
    return el ? el.value.trim() : '';
  }

  function coche(nom) {
    var el = form.querySelector('input[name="' + nom + '"]:checked');
    return el ? el.value : '';
  }

  /* Le téléphone en E.164 : le mail interne s'en sert pour un lien `tel:`
     cliquable depuis un mobile, quel que soit le formatage saisi. */
  function e164(tel) {
    var n = tel.replace(/[^\d+]/g, '');
    if (/^0\d{9}$/.test(n)) return '+33' + n.slice(1);
    if (/^\+\d{8,15}$/.test(n)) return n;
    return '';
  }

  function nuitsEntre(a, b) {
    if (!a || !b) return 0;
    var ms = new Date(b + 'T12:00:00') - new Date(a + 'T12:00:00');
    return Math.max(0, Math.round(ms / 86400000));
  }

  /* Référence lisible, partagée par les deux mails : EDN-AAMMJJ-XXXX. */
  function reference(date) {
    var p2 = function (n) { return String(n).padStart(2, '0'); };
    var jour = String(date.getFullYear()).slice(2) + p2(date.getMonth() + 1) + p2(date.getDate());
    var buf = new Uint8Array(2);
    if (window.crypto && crypto.getRandomValues) crypto.getRandomValues(buf);
    else { buf[0] = Math.random() * 256; buf[1] = Math.random() * 256; }
    var alea = '';
    for (var i = 0; i < buf.length; i++) alea += p2(buf[i].toString(16));
    return 'EDN-' + jour + '-' + alea.toUpperCase();
  }

  /* ---------- Collecte ----------
     Seule source de vérité : le récapitulatif affiché à l'étape 3 et le
     payload envoyé au webhook sont rendus depuis le MÊME objet. Les deux ne
     peuvent donc pas diverger — ce qui part est ce que le visiteur a validé. */
  function collecte() {
    var isEvent = estEvenement();
    var maintenant = new Date();
    var recap = [];
    var d = {
      source: 'site-domaine-eden',
      formulaire: 'reservation',
      type: isEvent ? 'evenement' : 'sejour',
      reference: reference(maintenant),
      envoye_le: maintenant.toISOString(),
      envoye_le_fr: maintenant.toLocaleString('fr-FR', {
        day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit'
      }),
      /* Deux adresses, deux usages — et il ne faut pas les confondre :

         `site_url` dit D'OÙ vient la demande. En essai local elle vaut
         `http://localhost:8000` : c'est une information de traçabilité.

         `public_url` est celle que les MAILS utilisent pour le logo et les
         liens. Un client mail ne rend pas l'image lui-même, il la fait
         chercher par ses serveurs — une adresse en localhost n'est joignable
         par aucun d'eux, et le logo reste cassé. En local on retombe donc sur
         le domaine de production, pour que le mail d'essai soit exactement
         celui que recevra le visiteur. */
      site_url: (location.origin && location.origin !== 'null') ? location.origin : SITE_URL,
      public_url: LOCAL ? SITE_URL : ((location.origin && location.origin !== 'null') ? location.origin : SITE_URL),
      page: location.href,
      sejour: null,
      evenement: null,
      recap: recap
    };

    /* `bloc` distingue les lignes de la DEMANDE de celles du CONTACT. Le mail
       du visiteur les affiche toutes ; le mail interne ne garde que la demande,
       parce qu'il porte déjà le contact et le message dans leurs propres
       encadrés — sans ce tri, il les imprimerait deux fois. */
    function ligne(label, valeur, bloc) {
      recap.push({ label: label, valeur: valeur, bloc: bloc || 'demande' });
    }

    if (isEvent) {
      var selEvt = document.getElementById('type-evenement');
      var optEvt = selEvt.options[selEvt.selectedIndex];
      var nb = val('nb-personnes');
      var dateEvt = val('date-evenement');
      d.evenement = {
        type: selEvt.value,
        type_slug: optEvt ? optEvt.dataset.slug : '',
        date: dateEvt,
        date_fr: fmtDate(dateEvt),
        nb_personnes: nb ? Number(nb) : null,
        hebergement: coche('hebergement_evt') === 'oui'
      };
      ligne('Demande', 'Événement ou groupe');
      ligne('Type', d.evenement.type);
      ligne('Date envisagée', d.evenement.date_fr);
      ligne('Personnes', nb || '—');
      ligne('Hébergement', d.evenement.hebergement ? 'Souhaité' : 'Sans hébergement');
    } else {
      var radio = form.querySelector('input[name="chambre"]:checked');
      var prix = radio.dataset.prix ? Number(radio.dataset.prix) : null;
      var adultes = Number(val('adultes')) || 0;
      var enfants = Number(val('enfants')) || 0;
      var voyageurs = adultes + enfants;
      var nuits = nuitsEntre(arrivee.value, depart.value);
      var table = coche('table') === 'oui';
      /* Estimation indicative, portée par le SEUL mail interne : le site ne
         chiffre rien au visiteur, la réservation reste arbitrée par les hôtes. */
      var eHeb = prix ? prix * nuits : null;
      var eTable = table ? PRIX_TABLE * voyageurs * nuits : 0;
      d.sejour = {
        chambre: radio.value,
        chambre_slug: radio.dataset.slug,
        prix_nuit: prix,
        arrivee: arrivee.value,
        arrivee_fr: fmtDate(arrivee.value),
        depart: depart.value,
        depart_fr: fmtDate(depart.value),
        nuits: nuits,
        adultes: adultes,
        enfants: enfants,
        voyageurs: voyageurs,
        table_hotes: table,
        estimation: {
          devise: 'EUR',
          hebergement: eHeb,
          table: eTable,
          total: eHeb === null ? null : eHeb + eTable,
          detail: eHeb === null
            ? 'Chambre laissée au choix des hôtes — aucune estimation possible.'
            : prix + ' € × ' + nuits + ' nuit(s)'
              + (table ? ' + ' + PRIX_TABLE + ' € × ' + voyageurs + ' pers. × ' + nuits + ' soir(s)' : '')
        }
      };
      ligne('Demande', 'Séjour en chambre d’hôtes');
      ligne('Chambre', d.sejour.chambre);
      ligne('Arrivée', d.sejour.arrivee_fr);
      ligne('Départ', d.sejour.depart_fr);
      ligne('Nuits', String(nuits));
      ligne('Voyageurs', adultes + ' adulte(s) · ' + enfants + ' enfant(s)');
      ligne('Table d’hôtes', table ? 'Avec plaisir' : 'Non merci');
    }

    var tel = val('telephone');
    var message = val('message');
    d.client = {
      prenom: val('prenom'),
      nom: val('nom'),
      nom_complet: (val('prenom') + ' ' + val('nom')).trim(),
      email: val('email'),
      telephone: tel,
      telephone_e164: e164(tel),
      message: message
    };

    ligne('Contact', d.client.nom_complet, 'contact');
    ligne('Email', d.client.email, 'contact');
    if (tel) ligne('Téléphone', tel, 'contact');
    if (message) ligne('Message', message, 'contact');

    d.rgpd = {
      consenti: document.getElementById('rgpd').checked,
      horodatage: d.envoye_le,
      texte: 'Informations utilisées uniquement pour répondre à la demande, non transmises à des tiers.'
    };

    /* Objets des deux mails : composés ici pour que n8n n'ait qu'à les recopier. */
    var qui = d.client.nom_complet || d.client.email;
    d.objet_client = 'Votre demande au Domaine d’Éden — ' + d.reference;
    d.objet_interne = isEvent
      ? 'Nouvelle demande · ' + d.evenement.type + ' · ' + (d.evenement.nb_personnes || '?')
        + ' pers. · ' + qui
      : 'Nouvelle demande · Séjour ' + d.sejour.nuits + ' nuit(s) dès le '
        + (d.sejour.arrivee || '?') + ' · ' + qui;

    d.technique = {
      referrer: document.referrer || '',
      utm: {
        source: params.get('utm_source') || '',
        medium: params.get('utm_medium') || '',
        campaign: params.get('utm_campaign') || ''
      },
      chambre_url: params.get('chambre') || '',
      format_url: format || '',
      langue: navigator.language || '',
      ecran: window.innerWidth + '×' + window.innerHeight,
      user_agent: navigator.userAgent,
      duree_saisie_s: Math.round((Date.now() - ouverture) / 1000)
    };

    return d;
  }

  /* ---------- Récapitulatif ---------- */
  function buildRecap() {
    document.getElementById('recap').innerHTML = collecte().recap.map(function (r) {
      return '<li><span class="label">' + esc(r.label) + '</span>'
           + '<span class="value">' + esc(r.valeur) + '</span></li>';
    }).join('');
  }

  /* ---------- Envoi ----------
     Point d'entrée unique. POST JSON vers le webhook n8n, qui déclenche les
     deux mails : accusé de réception au visiteur, fiche complète aux hôtes.
     `keepalive` couvre le cas où l'onglet est fermé dans la foulée. */
  function poste(url, corps) {
    return fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: corps,
      keepalive: true      /* la demande part même si l'onglet se ferme dans la foulée */
    }).then(function (r) {
      if (!r.ok) {
        var e = new Error('HTTP ' + r.status);
        e.statut = r.status;
        throw e;
      }
      return r;
    });
  }

  function submitRequest(data) {
    var corps = JSON.stringify(data);

    /* En local il n'y a pas de proxy : on tape l'adresse d'essai en direct. */
    if (LOCAL) return poste(WEBHOOK_TEST, corps);

    /* En ligne, le proxy d'abord (cf. netlify.toml) : la requête reste sur le
       domaine du site, donc ni pré-vol CORS ni domaine tiers à faire autoriser
       par un filtrage d'entreprise.

       Le repli direct couvre le seul cas où le proxy n'existe pas : un
       hébergeur sans les redirections de Netlify. On ne se rabat que sur un
       404 — une adresse qui n'est pas là. Un 500 vient de n8n lui-même et
       reviendrait à l'identique par l'autre chemin ; le renvoyer doublerait
       les demandes en cas de succès partiel. */
    return poste(PROXY, corps).catch(function (err) {
      if (err.statut !== 404) throw err;
      return poste(WEBHOOK, corps);
    });
  }

  var boutonEnvoi = form.querySelector('button[type="submit"]');
  var envoiError = document.getElementById('envoi-error');
  var envoiEnCours = false;

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (envoiEnCours) return;

    var rgpd = document.getElementById('rgpd');
    var rgpdError = document.getElementById('rgpd-error');
    if (!rgpd.checked) {
      rgpdError.style.display = 'block';
      return;
    }
    rgpdError.style.display = 'none';
    envoiError.style.display = 'none';

    /* Leurre anti-robot : le champ est hors écran et hors tabulation, un
       humain ne peut pas le remplir. On feint l'envoi plutôt que d'annoncer
       l'échec — un robot qui se sait repéré ajuste son tir suivant. */
    if (val('societe')) { show(4); return; }

    var data = collecte();
    envoiEnCours = true;
    var libelle = boutonEnvoi.textContent;
    boutonEnvoi.disabled = true;
    boutonEnvoi.textContent = 'Envoi en cours…';

    submitRequest(data).then(function () {
      show(4);
    }).catch(function (err) {
      console.error('Envoi de la demande :', err);
      envoiError.style.display = 'block';
      envoiError.scrollIntoView({ block: 'center', behavior: 'smooth' });
    }).then(function () {
      envoiEnCours = false;
      boutonEnvoi.disabled = false;
      boutonEnvoi.textContent = libelle;
    });
  });
})();
