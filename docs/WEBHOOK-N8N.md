# Le formulaire de réservation → n8n → deux emails

Toutes les demandes du site — séjours **et** événements — partent du même
formulaire ([site/reservation.html](../site/reservation.html)) vers **un seul
webhook n8n**, qui déclenche deux envois SMTP :

| Nœud n8n | Destinataire | Rôle |
|---|---|---|
| « Send email MarketFrame » | `chateaulestourelles43@gmail.com` | la fiche complète pour Grégory et Thomas |
| « Send email client » | le visiteur | l'accusé de réception |

Les deux gabarits sont dans [docs/emails/](emails/) et se collent tels quels
dans le champ **HTML** de chaque nœud.

---

## 1. Les adresses

Elles sont posées en tête de [site/assets/js/reservation.js](../site/assets/js/reservation.js) :

```
production : https://n8n.srv1107413.hstgr.cloud/webhook/771531e2-ed8a-4f64-b110-beedd81cd96d
essai      : https://n8n.srv1107413.hstgr.cloud/webhook-test/771531e2-ed8a-4f64-b110-beedd81cd96d
```

Le script choisit **sur le nom d'hôte** : `localhost` et `127.0.0.1` tapent
l'adresse d'essai, tout le reste la production. L'aiguillage vaut mieux qu'une
ligne à commenter, qui finit toujours par partir en ligne un jour. L'adresse
d'essai n'écoute que le temps d'un clic sur « Listen for test event » ; en
dehors elle répond 404 et le formulaire affiche son message d'échec.

Reste **`SITE_URL`** : le domaine public du site. C'est lui que les emails
utilisent pour le logo et les liens, via `public_url` dans le payload.

**Le logo des emails a besoin d'une adresse publique, et c'est la seule chose
du montage qui l'exige.** Un client mail ne va pas chercher l'image lui-même :
ce sont les serveurs de Gmail, d'Outlook ou d'Apple qui la téléchargent. Une
adresse en `localhost` — ou un domaine qui ne résout pas — leur est inaccessible,
et le logo reste cassé même si le mail arrive parfaitement. C'est pourquoi le
payload porte **deux** adresses :

| champ | ce qu'il vaut | à quoi il sert |
|---|---|---|
| `site_url` | l'origine réelle, `http://localhost:8000` en essai | tracer d'où vient la demande |
| `public_url` | `SITE_URL` en local, `location.origin` en ligne | le logo et les liens des emails |

Les gabarits n'utilisent que `public_url` : un essai local produit donc
exactement le mail que recevra le visiteur, logo compris — à condition que
`SITE_URL` pointe sur un site réellement en ligne.

## 2. Réglages du nœud Webhook

**Les deux réglages ci-dessous manquent encore.** Mesuré sur l'URL de production
le 10 septembre 2026, par un `OPTIONS` — qui interroge la configuration sans
déclencher le workflow :

```
Access-Control-Allow-Methods: OPTIONS, GET
(aucun en-tête Access-Control-Allow-Origin)
```

- **HTTP Method : `POST`.** Le nœud est encore en `GET`. En GET les champs
  arriveraient tronqués dans l'URL, et les gabarits, qui lisent `$json.body`,
  ne trouveraient rien.
- **Options → Allowed Origins (CORS)** : le domaine du site (ou `*`). Depuis la
  mise en place du proxy (§2 bis) ce réglage ne sert plus qu'au **repli** direct
  — le garder, ne pas s'y fier. Il reste indispensable si le site est un jour
  hébergé ailleurs que sur Netlify.
- **Respond : Immediately.** Le site n'attend pas les mails ; il n'a besoin que
  d'un `200` pour afficher l'écran de confirmation.

Pour revérifier après correction :

```
curl -s -i -X OPTIONS "<url de production>" -H "Origin: https://<domaine du site>" -H "Access-Control-Request-Method: POST"
```

`Access-Control-Allow-Methods` doit alors mentionner `POST`, et
`Access-Control-Allow-Origin` renvoyer le domaine.

## 2 bis. Le proxy : le formulaire poste sur le domaine du site

Le navigateur du visiteur ne parle **qu'au domaine du site**. Une redirection de
`netlify.toml` relaie `POST /api/demande` vers le webhook n8n :

```toml
[[redirects]]
  from = "/api/demande"
  to = "https://n8n.srv1107413.hstgr.cloud/webhook/771531e2-…"
  status = 200
  force = true
```

**Pourquoi.** Sans elle, le navigateur doit joindre `n8n.srv….hstgr.cloud`, un
tiers qu'un filtrage d'entreprise — FortiGate et consorts — bloque volontiers
parce qu'il est « non catégorisé ». Le formulaire échouerait alors sur un réseau
où le site s'affiche parfaitement. Avec le proxy, il n'y a qu'un domaine à
autoriser : celui du site. Effet de bord bienvenu, la requête devient de même
origine, donc **plus de pré-vol CORS du tout**.

**Mesuré**, sur un site Netlify jetable créé pour l'occasion puis supprimé : un
`POST` traverse le proxy avec son corps JSON intact et son `Content-Type`, et un
`fetch` depuis une page du site répond 200 sans qu'aucune requête `OPTIONS` ne
soit émise.

`reservation.js` tente le proxy d'abord, et **ne se rabat sur l'adresse n8n
directe que sur un 404** — c'est-à-dire quand la redirection n'existe pas, sur
un hébergeur qui n'est pas Netlify. Se rabattre sur un 500 ferait arriver la
demande deux fois chez les hôtes, puisque l'erreur viendrait de n8n lui-même.
`tools/verifier-mails.py` éprouve les deux chemins à chaque passage.

En local il n'y a pas de proxy : le script tape l'adresse d'essai en direct.

## 3. Réglages des deux nœuds SMTP

|  | Mail interne | Mail visiteur |
|---|---|---|
| **To** | `chateaulestourelles43@gmail.com` | `{{ $json.body.client.email }}` |
| **Subject** | `{{ $json.body.objet_interne }}` | `{{ $json.body.objet_client }}` |
| **Reply-To** | `{{ $json.body.client.email }}` | `chateaulestourelles43@gmail.com` |
| **Email Format** | HTML | HTML |
| **Gabarit** | [emails/mail-interne.html](emails/mail-interne.html) | [emails/mail-client.html](emails/mail-client.html) |

Le `Reply-To` du mail interne est ce qui compte le plus au quotidien :
« Répondre » depuis la boîte des hôtes écrit alors directement au visiteur,
sans copier-coller d'adresse.

## 4. Le payload

Un seul objet JSON, le même pour les deux motifs. `sejour` et `evenement`
s'excluent : celui qui ne s'applique pas vaut `null`.

```jsonc
{
  "source": "site-domaine-eden",
  "formulaire": "reservation",
  "type": "sejour",                   // "sejour" | "evenement"
  "reference": "EDN-260910-6144",     // EDN-AAMMJJ-XXXX, portée par les deux mails
  "envoye_le": "2026-09-10T10:36:02.451Z",
  "envoye_le_fr": "10 septembre 2026 à 12:36",
  "site_url": "http://localhost:8000", // d'OÙ vient la demande : traçabilité
  "public_url": "https://…",          // ce que les MAILS utilisent : logo et liens
  "page": "https://…/reservation.html?chambre=refuge-brumes",

  "client": {
    "prenom": "Camille", "nom": "Perrin", "nom_complet": "Camille Perrin",
    "email": "camille.perrin@example.org",
    "telephone": "06 12 34 56 78",
    "telephone_e164": "+33612345678", // pour le lien `tel:` du mail interne
    "message": "…"                    // peut être vide
  },

  "sejour": {
    "chambre": "Refuge des Brumes", "chambre_slug": "refuge-brumes",
    "prix_nuit": 90,                  // null si « Peu importe — conseillez-moi »
    "arrivee": "2026-10-02", "arrivee_fr": "vendredi 2 octobre 2026",
    "depart":  "2026-10-05", "depart_fr":  "lundi 5 octobre 2026",
    "nuits": 3, "adultes": 2, "enfants": 1, "voyageurs": 3,
    "table_hotes": true,
    "estimation": {                   // mail INTERNE seulement — cf. §5
      "devise": "EUR", "hebergement": 270, "table": 225, "total": 495,
      "detail": "90 € × 3 nuit(s) + 25 € × 3 pers. × 3 soir(s)"
    }
  },

  "evenement": {
    "type": "Mariage", "type_slug": "mariage",
    "date": "2027-06-12", "date_fr": "samedi 12 juin 2027",
    "nb_personnes": 24,               // null si non renseigné
    "hebergement": true
  },

  "rgpd": { "consenti": true, "horodatage": "…", "texte": "…" },

  "recap": [                          // ce que le visiteur a VU et validé
    { "label": "Chambre", "valeur": "Refuge des Brumes", "bloc": "demande" },
    { "label": "Email",   "valeur": "camille…",          "bloc": "contact" }
  ],

  "objet_client":  "Votre demande au Domaine d’Éden — EDN-260910-6144",
  "objet_interne": "Nouvelle demande · Séjour 3 nuit(s) dès le 2026-10-02 · Camille Perrin",

  "technique": {
    "referrer": "…", "utm": { "source": "…", "medium": "…", "campaign": "…" },
    "chambre_url": "…", "format_url": "…", "langue": "fr",
    "ecran": "1280×900", "user_agent": "…",
    "duree_saisie_s": 3               // un robot remplit en moins d'une seconde
  }
}
```

`recap` est la **seule source de vérité** des deux emails : il est construit par
la même fonction que le récapitulatif affiché à l'étape 3 du formulaire. Ce qui
part est donc exactement ce que le visiteur a relu avant d'envoyer — les deux ne
peuvent pas diverger. Chaque ligne porte un `bloc` : le mail du visiteur les
affiche toutes, le mail interne ne garde que `demande`, puisqu'il imprime déjà
le contact et le message dans leurs propres encadrés.

## 5. L'estimation ne part que dans le mail interne

Le site ne chiffre rien au visiteur : pas de paiement en ligne, pas de devis
automatique, la réservation reste arbitrée par les hôtes. `sejour.estimation`
est un calcul de commodité — tarif de la chambre × nuits, plus 25 € par personne
et par soir si la table d'hôtes est demandée — et le gabarit du mail visiteur ne
l'affiche nulle part. **Ne pas l'y ajouter** : ce serait lu comme un devis ferme.

Le tarif de chaque chambre est déclaré en `data-prix` sur son bouton radio, à
côté du prix affiché ; le prix de la table est la constante `PRIX_TABLE` de
`reservation.js`. Si les tarifs bougent, les deux endroits bougent ensemble.

## 6. Le leurre anti-robot

Le formulaire porte un champ `societe` hors écran et hors tabulation. Un humain
ne peut pas le remplir. S'il arrive rempli, `reservation.js` **feint l'envoi**
sans rien émettre — un robot qui se sait repéré ajuste son tir suivant. Rien ne
part alors vers n8n, et c'est pourquoi le champ n'est pas dans le payload.

Si du spam passait tout de même par un appel direct au webhook, `technique.duree_saisie_s`
donne le second filet : un nœud *IF* qui écarte les demandes remplies en moins
de trois secondes, avant les deux envois.

## 7. Rendu des emails

Tables imbriquées et styles en ligne : c'est la seule mise en page qu'Outlook,
Gmail et Apple Mail rendent tous les trois. Le rond du site — `border-radius`
sur les cartes, les lignes du récapitulatif et les boutons — est honoré partout
**sauf par Outlook pour Windows**, qui les rend carrés sans rien casser d'autre.
C'est un arbitrage assumé : la solution VML alourdirait les gabarits d'autant de
blocs conditionnels qu'il y a de coins.

Les webfonts du site ne sont pas chargées (aucun client mail ne les garantit) :
Georgia remplace Cormorant Garamond et Arial remplace Jost, deux substitutions
proches en dessin et en chasse.

Le logo est un **PNG** — `site/assets/img/logo-email.png`, rendu depuis
`logo-eden.svg`, 400 px pour un affichage à 112 px — parce que Gmail et Outlook
n'affichent pas de SVG. Il est servi depuis le site : régénérer la marque
(`tools/generer-logo.py`) demande de le régénérer aussi.

## 8. Vérifier avant de mettre en ligne

`tools/verifier-mails.py` rejoue un séjour et un événement dans un vrai
navigateur, capte le POST réellement émis, évalue les expressions `{{ … }}`
comme le ferait n8n et photographie les quatre combinaisons (deux mails × deux
motifs) :

```
python tools/verifier-mails.py            # écrit dans .verif-mails/
```

Une expression fautive y apparaît en clair dans la sortie plutôt que de casser
un envoi en production.
