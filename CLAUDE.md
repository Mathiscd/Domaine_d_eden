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
  favicon.ico          la marque, rendue pour 16/32/48 px   ⎫
  favicon.svg          la marque, réglée pour l'onglet       ⎬ générés — voir « Le logo »
  apple-touch-icon.png 180 px                                ⎭
  site.webmanifest     nom, couleurs, icônes 192/512/maskable
  assets/
    css/styles.css     styles globaux (variables CSS en tête de fichier)
    js/main.js         animations scroll, header, navigation, diaporama du hero
    js/reservation.js  logique du formulaire multi-étapes
    img/               variantes responsives `<nom>-<largeur>.{avif,webp,jpg}`,
                       plus `logo-eden.svg` et les icônes du manifeste
photos-sources/        photos sources 1500px (Gîtes de France) et le logo fourni
                       par le client — hors `site/`, donc versionnés mais jamais publiés
tools/
  generer-images.py    régénère les variantes depuis photos-sources/ (voir « Images »)
  generer-logo.py      redessine la marque et toutes ses déclinaisons (voir « Le logo »)
  extrait-logo.html    bloc <symbol> produit par le script, à recopier dans les pages
docs/
  CHARTE-GRAPHIQUE.md  couleurs, marque, typos, espacements, composants, ton
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

**Les sources font 2000px, pas 1500.** Les URLs de la fiche Gîtes de France
(`photos-sources/urls.txt`) portent un preset Drupal `styles/scale_w1500_h1500/` ;
retirer ce segment du chemin rend l'original en 2000×1500. C'est ce qui est
versionné, à la racine de `photos-sources/` — là où `generer-images.py` les lit.
Repartir des 1500px re-crée le flou sur les écrans à haute densité.

**Les largeurs vont jusqu'à 2000 parce que les écrans sont en DPR 2.** Une carte
chambre de 360px CSS demande 720px réels, un bandeau pleine largeur près de 3000.
Tant que le srcset s'arrêtait à 1500, tout le site était sous-résolu d'un facteur
2 sur un Retina — net en DPR 1, mou partout ailleurs. Les écrans DPR 1 ne
téléchargent pas ces variantes : le poids initial y est inchangé.

**Une réduction est un passe-bas : `reechantillonner()` ré-accentue.** Un unsharp
mask discret (rayon 0,6, 55 %, seuil 3) rend le micro-contraste que le LANCZOS
étale, sans halo. Il s'applique avant la mesure SSIM, donc la bissection continue
de ne mesurer que le coût de la compression. Monter `percent` produirait des
liserés sur les arêtes contrastées — les encadrements de fenêtre sur le ciel.

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
les remesurer : sous-estimer rend flou, sur-estimer gaspille. C'est ce que
contrôle `tools/verifier-sizes.py`, à relancer après toute retouche de mise
en page (servir `site/`, puis `python tools/verifier-sizes.py`).

## Le logo

Le client a fourni son château au trait en PNG (`photos-sources/logo-domaine-eden.png`,
619 px, blanc sur aplat vert texturé). Ce fichier ne sert plus qu'à la vérification :
sa géométrie a été **relevée au pixel** — axe de symétrie, pentes, arcs de couronne,
entraxes des créneaux — puis redessinée en vectoriel dans `tools/generer-logo.py`.
Symétrie parfaite, trait d'épaisseur constante, créneaux réguliers ; l'écart au dessin
d'origine reste sous 2 px sur une marque large de 359.

```
python tools/generer-logo.py              # écrit la marque, le favicon et les icônes
python tools/generer-logo.py --comparer   # + superpose le rendu au PNG du client
```

`--comparer` sort un taux de recouvrement (IoU ≈ 0,82, la limite d'un trait de 6 px)
et `.logo-diff.png`, où le rouge marque ce qui manque et le bleu ce qui a été ajouté.
C'est le contrôle à refaire si on touche à la géométrie.

**Dans les pages** : pas de build, donc chaque page porte la marque **une seule fois**,
en `<symbol id="eden-marque">` juste après `<body>`, et l'appelle ensuite par
`<use href="#eden-marque">` — en-tête, pied de page, rideau d'ouverture. Ce bloc est
généré (`tools/extrait-logo.html`) : on le recopie, on ne le retouche pas à la main.
Un `<use>` vers un fichier `.svg` externe n'est pas implémenté par les navigateurs,
d'où la recopie ; `site/assets/img/logo-eden.svg` reste le fichier autonome à livrer
au client.

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
- **`--eden-trait`** : la marque est dessinée avec un trait de 6,3 unités pour 291 de
  haut. À 26 px dans l'en-tête, cela ne fait plus qu'un demi-pixel et le château vire au
  gris — la variable l'épaissit à mesure qu'on rapetisse. Elle traverse l'arbre du
  `<use>` (les propriétés personnalisées s'y héritent), c'est ce qui permet une seule
  définition pour trois tailles. Même compensation côté icônes, mais figée taille par
  taille dans le script : un PNG ne connaît qu'une dimension.
- **Les icônes sont toutes le dessin au trait, vert sur tuile claire** — onglet compris.
  Sous 48 px il s'adoucit franchement : c'est un arbitrage assumé en faveur de la
  cohérence de marque. Une silhouette pleine tiendrait mieux à 16 px ; ne pas y revenir
  sans le demander au client, c'est lui qui a tranché.
- **Le rideau anime la marque partagée par héritage** : `stroke-dashoffset` et
  `fill-opacity` font partie des propriétés qui descendent dans l'arbre du `<use>`.
  C'est ce qui permet de faire tracer le château sans dupliquer ses chemins — et
  `fill-opacity` ne touche que les ouvertures, les tracés étant en `fill: none`.
- **La parallaxe mesure un parent, pas l'image** : le rect de l'image inclut la
  translation qu'on vient de lui appliquer, donc le décalage se cumulerait.

## Vérification visuelle

Tester avec Playwright (installé globalement) : servir `site/` via
`python -m http.server`, capturer desktop 1440×900 et mobile 390×844, pleine page.
Comparer l'intention à la charte avant toute itération de design.

## Contenus — points de vigilance

- 5 chambres : Suite du Roi et de la Reine, Antichambre de la Nuit, Boudoir des Rêves,
  Refuge des Brumes, Repaire des Songes. Tarifs indicatifs 90–99 € petit-déjeuner compris.
- Les photos actuelles proviennent de deux sources : la fiche Gîtes de France
  (2000px, une seule chambre photographiée — les vues du château, salons, jardin)
  et des captures Booking (`photos-sources/Chambres/`, ~930px) qui, elles, montrent
  les cinq chambres distinctes. **Ces captures plafonnent à 930px** : c'est la
  limite de netteté restante du site, et aucun réencodage ne la lèvera. Sur mobile
  DPR 3 elles servent 86–89 % des pixels demandés (écart peu visible) ; sur desktop
  elles suffisent. À remplacer dès que le client fournit ses photos définitives —
  c'est le seul vrai correctif. Booking bloque la récupération automatique.
- Les trois bandeaux pleine largeur (hero, `chateau-angle`) restent à ~65 % des
  pixels d'un Retina : la source 2000px est le plafond. Sans photos plus grandes,
  il n'y a rien à corriger là.
- Espace Soreï : site séparé (<https://thomasploton.fr/>), uniquement un lien sortant.
  Ne pas réintégrer son contenu.
- Un seul geste attendu du visiteur : **envoyer une demande** (pas de paiement en ligne,
  pas de calendrier de disponibilités). La réservation reste gérée par les hôtes.
- Coordonnées : 2562 Avenue de Bazac, 43800 Beaulieu · 06 65 32 92 61 ·
  chateaulestourelles43@gmail.com · Arrivée 16 h–20 h, départ 9 h–10 h.
