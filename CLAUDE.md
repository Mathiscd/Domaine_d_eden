# Domaine d'Éden — Refonte du site

## Le projet

Refonte complète du site du **Domaine d'Éden – Château les Tourelles**, maison d'hôtes
et lieu événementiel à Beaulieu (Haute-Loire, Auvergne), tenue par Grégory et Thomas.
Prestation cadrée par la proposition commerciale MarketFrame
([proposition-domaine-eden-onepage.pdf](proposition-domaine-eden-onepage.pdf)) validée par le client.

**Livrable** : un site éditorial de **quatre pages** — accueil (le déroulé complet),
chambres, événements — plus une page de réservation dédiée avec formulaire multi-étapes.
Statique (HTML/CSS/JS vanilla), sans framework, sans build.

## Règle d'or du design

L'ancien site du client (captures `Capture*.PNG` à la racine) sert **uniquement de
source de contenu** (textes, infos, photos). Son design — cercles verts criards,
composition chargée — est le contre-exemple : le nouveau site doit être
**diamétralement opposé**. La référence esthétique est
[grandlauron.com](https://www.grandlauron.com/) : éditorial, épuré, photographique,
serif élégante, beaucoup de blanc — c'est aussi elle qui dicte la structure du header
(réseaux à gauche, signature centrée, téléphone à droite, nav en second rang).

**La couleur, en revanche, est celle du client** : le vert `#74963D` relevé sur ses
captures. C'est la seule teinte du site — aucun brun, laiton ni vert olive vif en aplat.

Toute décision visuelle se prend contre [docs/CHARTE-GRAPHIQUE.md](docs/CHARTE-GRAPHIQUE.md).
La structure et les contenus sont dans [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Arborescence

```
site/
  index.html           accueil : toutes les sections du déroulé
  chambres.html        les 5 chambres en détail (ancres #suite-roi-reine, #boudoir-reves…)
  evenements.html      les formats, le cadre, le déroulé, la table
  reservation.html     formulaire de demande multi-étapes (cible de tous les CTA)
  assets/
    css/styles.css     styles globaux (variables CSS en tête de fichier)
    js/main.js         animations scroll, header, navigation, diaporama du hero
    js/reservation.js  logique du formulaire multi-étapes
    img/               photos optimisées, noms sémantiques
    img/src/           photos sources 1500px (Gîtes de France) — ne pas livrer
docs/
  CHARTE-GRAPHIQUE.md  couleurs, typos, espacements, composants, ton
  ARCHITECTURE.md      plan des pages, sections, contenus validés
```

## Contraintes techniques

- **Statique pur** : ouvrable en `file://`, hébergeable n'importe où. Pas de npm, pas de build.
- **Fonts** : Google Fonts (Cormorant Garamond + Jost), avec stack de secours système.
- **Formulaire** : front seul pour l'instant. L'envoi réel (boîte mail du client +
  auto-réponse, cf. proposition) sera branché via Formspree/Brevo au déploiement —
  point d'entrée unique dans `reservation.js` (`submitRequest()`).
- **Responsive** : mobile d'abord vérifié à 390px, desktop à 1440px. Menu burger sous 900px.
- **Accessibilité** : contrastes AA sur le texte, focus visibles, `prefers-reduced-motion` respecté.
- **Performance** : images `loading="lazy"` hors hero, pas de librairie JS externe.

## Vérification visuelle

Tester avec Playwright (installé globalement) : servir `site/` via
`python -m http.server`, capturer desktop 1440×900 et mobile 390×844, pleine page.
Comparer l'intention à la charte avant toute itération de design.

## Contenus — points de vigilance

- 5 chambres : Suite du Roi et de la Reine, Antichambre de la Nuit, Boudoir des Rêves,
  Refuge des Brumes, Repaire des Songes. Tarifs indicatifs 90–99 € petit-déjeuner compris.
- Les photos actuelles proviennent de la fiche Gîtes de France du client (une seule
  chambre photographiée) : plusieurs cartes chambres réutilisent des angles de la même
  pièce **en attendant les photos définitives du client** — signalé dans ARCHITECTURE.md.
- Espace Soreï : site séparé (<https://thomasploton.fr/>), uniquement un lien sortant.
  Ne pas réintégrer son contenu.
- Un seul geste attendu du visiteur : **envoyer une demande** (pas de paiement en ligne,
  pas de calendrier de disponibilités). La réservation reste gérée par les hôtes.
- Coordonnées : 2562 Avenue de Bazac, 43800 Beaulieu · 06 65 32 92 61 ·
  chateaulestourelles43@gmail.com · Arrivée 16 h–20 h, départ 9 h–10 h.
