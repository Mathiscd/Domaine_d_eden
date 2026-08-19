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
    img/               variantes responsives `<nom>-<largeur>.{avif,webp,jpg}`
photos-sources/        photos sources 1500px (Gîtes de France) — hors `site/`,
                       donc versionnées mais jamais publiées
tools/
  generer-images.py    régénère les variantes depuis photos-sources/ (voir « Images »)
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
- **Performance** : pas de librairie JS externe. Voir « Images » et « Pièges » ci-dessous.

## Images

Chaque photo est livrée en AVIF, WebP et JPEG, à plusieurs largeurs, via un
`<picture>` : `<source type="image/avif">`, puis WebP, puis l'`<img>` JPEG en
dernier recours. Nommage `assets/img/<nom>-<largeur>.<ext>`.

**Régénérer** (le jour où le client fournit ses vraies photos) :

```
python tools/generer-images.py            # simulation
python tools/generer-images.py --ecrire   # produit les fichiers
```

Le script cherche la qualité par bissection, image par image et format par format
— la plus basse qui tienne le plancher SSIM (0,97 ; 0,95 en 240px, largeur qui ne
sert qu'aux vignettes 78px de la réservation). Ne pas remplacer ça par une qualité
fixe : un ciel uni et un intérieur sombre n'ont pas les mêmes besoins.

Trois règles à ne pas casser :

- **Encoder depuis `photos-sources/`, jamais depuis un JPEG déjà compressé** —
  sinon les bits partent à reproduire les artefacts du fichier intermédiaire.
- **`speed=4` pour l'AVIF** (le défaut de Pillow est 6) : ~3 % de moins à qualité
  égale. Changer ce réglage oblige à régénérer tout le jeu.
- **Un srcset doit rester monotone** : une variante plus lourde qu'une plus grande
  ferait télécharger plus d'octets pour moins de pixels. Le script élague ces
  cas format par format ; c'est pourquoi certaines images n'ont pas toutes les largeurs.

Les `sizes` sont calés sur les largeurs **réellement rendues**, mesurées aux
breakpoints du CSS (1024 / 940 / 900 / 640). Si la mise en page change, il faut
les remesurer : sous-estimer rend flou, sur-estimer gaspille.

## Pièges — ne pas « nettoyer » sans comprendre

- **`picture { display: contents }`** : sans ça le `<picture>` s'interpose entre
  l'image et son conteneur, et tous les `height:100%` + `object-fit:cover`, plus
  les `.photo-inset` en absolu, perdent leur référence de calcul.
- **Les doublures de police** (`Cormorant secours`, `Jost secours`, avec
  `size-adjust` / `ascent-override`) : Cormorant fait 87 % de la largeur de
  Georgia, son italique 77 %. Sans ces doublures, tout le texte se remet en page
  à l'arrivée des webfonts — c'était l'essentiel du CLS. Les valeurs sont mesurées,
  pas devinées ; les modifier au jugé casse la compensation.
- **Le diaporama du hero charge ses vues à la main** (`data-src` / `data-srcset`,
  promus par `main.js`). Elles sont empilées en absolu, donc « dans le viewport » :
  `loading="lazy"` ne les différerait pas et les cinq partiraient d'un coup.
- **Le rideau d'ouverture ne joue qu'à l'arrivée sur le site**, pas à chaque page.
  Un script de garde dans le `<head>` tranche avant le premier paint (sessionStorage,
  repli sur le référent) et pose `no-curtain` + `is-loaded` sur `<html>`. Il doit
  rester inline et en `<head>` : ailleurs, le rideau apparaîtrait puis disparaîtrait.
- **La parallaxe mesure un parent, pas l'image** : le rect de l'image inclut la
  translation qu'on vient de lui appliquer, donc le décalage se cumulerait.

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
