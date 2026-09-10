# Domaine d'Éden — Refonte du site

## Le projet

Refonte complète du site du **Domaine d'Éden – Château les Tourelles**, maison d'hôtes
et lieu événementiel à Beaulieu (Haute-Loire, Auvergne), tenue par Grégory et Thomas.
Prestation cadrée par la proposition commerciale MarketFrame
([proposition-domaine-eden-onepage.pdf](proposition-domaine-eden-onepage.pdf)) validée par le client.

**Livrable** : un site éditorial de **quatre pages** — accueil (le déroulé complet),
chambres, événements — plus une page de réservation dédiée avec formulaire multi-étapes.
Statique (HTML/CSS/JS vanilla), sans framework, sans build.

## Règle d'or du design — **elle a changé, à la demande du client**

Le site a d'abord été construit contre son ancien site : éditorial, anguleux, épuré,
sur le modèle de [grandlauron.com](https://www.grandlauron.com/). **Le client a demandé
l'inverse**, et sa demande fait autorité — elle remplace la règle précédente, pas
l'inverse. Il veut retrouver l'esprit de sa propre maquette :

- **Un site rond.** Tout arrondi, et généreusement : cartes, photos, boutons, champs,
  badges, vignettes, encadrés, bandes de section, coins du hero. Jusqu'aux **pilules** et
  aux **médaillons parfaitement circulaires** (portraits, vignettes, pastilles, icônes,
  boutons d'action). Pas de rayon timide de 4 px.
- **De grands disques verts en fond** : de larges cercles de `#74963D` et d'un vert plus
  clair `#8FB25C`, qui débordent du cadre, se chevauchent (deux disques qui se recouvrent
  dessinent une silhouette en pétale) et sortent par les bords.
- **Moins premium, plus familial** : chaleureux, accueillant, doux. C'est une maison
  d'hôtes tenue par deux hôtes, pas un palace. Le rond, la générosité des formes et la
  présence franche du vert servent ça.

Ce qui **n'a pas** changé : l'ancien site du client (captures `Capture*.PNG` à la racine)
reste **uniquement une source de contenu** — textes, informations, photos. On lui reprend
son langage de formes et sa couleur, jamais sa mise en page (composition chargée, texte
sur photo non voilée). La structure de l'en-tête reste celle de Grand Lauron (réseaux à
gauche, signature centrée, téléphone à droite, nav en second rang) : elle a été validée et
ne fait pas partie du virage.

**La couleur reste la sienne** : le vert `#74963D` relevé sur ses captures. C'est toujours
la seule teinte du site — aucun brun, laiton ni vert olive vif en aplat. Elle est
simplement beaucoup plus présente qu'avant, et la famille s'est étoffée d'un vert plus
clair pour les disques (`#8FB25C`) et d'un vert profond (`#40571E`) pour les aplats qui
portent du texte blanc. **Le vert de marque ne porte pas de texte courant** : 3,34:1.

Toute décision visuelle se prend contre [docs/CHARTE-GRAPHIQUE.md](docs/CHARTE-GRAPHIQUE.md)
(**v4 — « rond, vert, familial »**).
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
    js/reservation.js  logique du formulaire multi-étapes et envoi au webhook
    img/               variantes responsives `<nom>-<largeur>.{avif,webp,jpg}`,
                       plus `logo-eden.svg`, `logo-email.png` (la marque servie
                       aux clients mail) et les icônes du manifeste
photos-sources/        photos sources 1500px (Gîtes de France), le logo fourni par le
                       client (`logo-domaine-eden.png`) et le logo qu'il remplace
                       (`…-ancien.png`) — hors `site/` : versionnés, jamais publiés
tools/
  generer-images.py    régénère les variantes depuis photos-sources/ (voir « Images »)
  verifier-srcset.py   contrôle que le balisage déclare bien toutes les variantes
  generer-logo.py      vectorise la marque et produit ses déclinaisons (voir « Le logo »)
  extrait-logo.html    bloc <symbol> produit par le script, à recopier dans les pages
  verifier-mails.py    rejoue le formulaire, évalue les expressions n8n, rend les mails
docs/
  CHARTE-GRAPHIQUE.md  couleurs, marque, typos, espacements, composants, ton
  ARCHITECTURE.md      plan des pages, sections, contenus validés
  WEBHOOK-N8N.md       contrat du webhook, réglages des nœuds, forme du payload
  emails/
    mail-client.html   accusé de réception du visiteur   ⎫ à coller dans le champ
    mail-interne.html  fiche complète pour les hôtes     ⎭ HTML des nœuds SMTP
```

## Contraintes techniques

- **Statique pur** : ouvrable en `file://`, hébergeable n'importe où. Pas de npm, pas de build.
- **Fonts** : Cormorant Garamond + Jost, **auto-hébergées** dans `site/assets/fonts/`
  (sous-ensembles latin et latin-ext seulement), avec stack de secours système.
- **Formulaire** : toutes les demandes — séjours **et** événements — partent en
  POST JSON vers un **webhook n8n**, qui envoie les deux mails de la proposition
  (fiche complète aux hôtes, accusé de réception au visiteur). Point d'entrée
  unique dans `reservation.js` (`submitRequest()`) ; contrat du payload, réglages
  des nœuds et gabarits : [docs/WEBHOOK-N8N.md](docs/WEBHOOK-N8N.md). En ligne, la
  demande ne sort pas du domaine du site : elle passe par `/api/demande`, que
  `netlify.toml` relaie vers n8n. En local, le script tape l'adresse d'essai en
  direct. `tools/verifier-mails.py` éprouve les deux chemins, le payload et les
  expressions n8n à chaque passage.
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
python tools/generer-images.py --seulement chevaux-aube --ecrire   # une seule photo
```

`--seulement` sert à ajouter une image sans rebissecter les vingt autres : à réglages
inchangés le script les réécrirait à l'identique, pour une heure de calcul. Sans
l'option, tout le jeu est traité, comme avant.

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

`tools/verifier-srcset.py` contrôle l'autre moitié : que le balisage déclare
bien **toutes** les variantes présentes sur le disque. Un palier généré mais
non branché est invisible à l'œil et coûte cher — c'est ce qui faisait servir
un 2000 px à un mobile en DPR 3. À lancer après chaque `generer-images.py`.

## Le logo

Le client a fourni son logo en PNG (`photos-sources/logo-domaine-eden.png`, 638 px) :
un château dessiné à la main — façade au trait `#404041`, volets sombres, toits de
tourelles et grand arbre en aplat vert `#75983D` — encadré de deux lignes de lettrage,
« CHÂTEAU LES TOURELLES » au-dessus, « DOMAINE D'EDEN » en dessous.

`tools/generer-logo.py` le **vectorise**, et n'en garde que le dessin :

- **Le lettrage est écarté.** Il est bitmap, donc flou dès 200 px, et les pages
  composent déjà ces deux lignes en Jost et en Cormorant. Le script repère la seule
  bande horizontale qui porte du vert — le dessin, l'arbre étant le seul élément vert
  de l'image — plutôt que des coordonnées en dur : le logo peut être renvoyé recadré
  ou à une autre échelle sans rien retoucher.
- **Les deux encres sont séparées avant le seuillage.** Chaque pixel est décomposé en
  `blanc + a_vert·(vert−blanc) + a_encre·(encre−blanc)` aux moindres carrés, ce qui
  donne la bonne couverture jusque dans l'anti-crénelage — un simple seuil sur la
  luminance rangerait les pixels de bord du vert avec l'encre.
- **Le grain du trait est conservé.** Le dessin est irrégulier parce qu'il est fait à
  la main ; c'est ce qui le distingue d'un pictogramme géométrique. On lisse assez pour
  que le `d` reste court, pas assez pour redresser le trait.

```
python tools/generer-logo.py              # écrit la marque, le favicon et les icônes
python tools/generer-logo.py --comparer   # + superpose le rendu au PNG du client
python tools/generer-logo.py --planche    # + planche d'essai de 20 à 220 px
```

`--comparer` sort un IoU par encre (≈ 0,99 sur le vert, ≈ 0,85 sur l'encre — un trait
large de 2 px perd la moitié de son recouvrement pour un décalage d'un pixel) et
`.logo-diff.png`, où le rouge marque ce qui manque et le bleu ce qui a été ajouté.
`--planche` est le seul juge des réglages de `--eden-trait` : la marque y est rendue
à toutes ses tailles, sur fond sombre et sur fond clair.

**Dans les pages** : pas de build, donc chaque page porte la marque **une seule fois**,
en `<symbol id="eden-marque">` juste après `<body>`, et l'appelle ensuite par
`<use href="#eden-marque">` — en-tête, pied de page, rideau d'ouverture. Ce bloc est
généré (`tools/extrait-logo.html`) : on le recopie, on ne le retouche pas à la main.
Un `<use>` vers un fichier `.svg` externe n'est pas implémenté par les navigateurs,
d'où la recopie ; `site/assets/img/logo-eden.svg` reste le fichier autonome à livrer
au client. Deux variables règlent le rendu, toutes deux héritées jusque dans l'arbre du
`<use>` : `--eden-feuille` (couleur de l'arbre et des toits) et `--eden-trait`
(épaississement optique). Le viewBox est `0 0 1024 917` et il est répété sur chaque
`<svg class="eden-marque">` : le régénérer oblige à le propager dans les six pages.

## Pièges — ne pas « nettoyer » sans comprendre

- **`picture { display: contents }`** : sans ça le `<picture>` s'interpose entre
  l'image et son conteneur, et tous les `height:100%` + `object-fit:cover`, plus
  les `.photo-inset` en absolu, perdent leur référence de calcul.
- **Les doublures de police** (`Cormorant secours`, `Jost secours`, avec
  `size-adjust` / `ascent-override`) : Cormorant fait 87 % de la largeur de
  Georgia, son italique 77 %. Sans ces doublures, tout le texte se remet en page
  à l'arrivée des webfonts — c'était l'essentiel du CLS. Les valeurs sont mesurées,
  pas devinées ; les modifier au jugé casse la compensation.
- **Le preload de l'image de tête passe avant la feuille de style**, et c'est
  volontaire. Le mettre après accélère le premier paint — le CSS bloque le rendu,
  l'image non — mais retarde d'autant l'arrivée du LCP : mesuré en 3G bridée
  (300 ms, 700 kbps) sur mobile, FCP 1888 → 1420 ms mais LCP 3904 → 4768 ms.
  Le LCP pèse plus lourd que le FCP dans les Core Web Vitals : l'ordre actuel est
  le bon compromis. Essai déjà fait, ne pas le refaire.
- **Le diaporama du hero charge ses vues à la main** (`data-src` / `data-srcset`,
  promus par `main.js`). Elles sont empilées en absolu, donc « dans le viewport » :
  `loading="lazy"` ne les différerait pas et les cinq partiraient d'un coup.
- **Et il se tait sur lien étroit, ou dès qu'on l'a dépassé.** Ses vues pèsent 0,4 à
  0,6 Mo pièce en DPR 2, et deux d'entre elles — `chateau-angle`, `jardin` — sont
  **les mêmes photos que le collage de la section 01**, servies là en 1100 et 768 px.
  Mesuré en 3G bridée : la vue 2 (`chateau-angle-1962`, 449 ko) tenait le tuyau de
  8,9 s à 20,2 s, et le collage — `lazy`, priorité basse — attendait derrière
  **7,4 s et 9,5 s après qu'on l'ait atteint**. D'où deux garde-fous dans `main.js` :
  un appel *spéculatif* (`charge(n, true)`) ne part que si le hero est encore à
  l'écran, et `play()` s'abstient si `navigator.connection` annonce `saveData` ou
  2g/3g — première vue seule, les puces chargeant à la demande. Résultat : collage à
  5,6 s / 6,6 s, LCP inchangé (6,85 s contre 6,80 s).
  **Ne pas « corriger ça » en rendant le collage `eager`** : essai fait, les deux
  photos arrivent alors avant le scroll, mais elles se disputent la bande passante
  avec l'image de tête et le LCP passe de 6,8 à 11,5 s.
- **Le rideau d'ouverture ne joue qu'à l'arrivée sur le site**, pas à chaque page.
  Un script de garde dans le `<head>` tranche avant le premier paint (sessionStorage,
  repli sur le référent) et pose `no-curtain` + `is-loaded` sur `<html>`. Il doit
  rester inline et en `<head>` : ailleurs, le rideau apparaîtrait puis disparaîtrait.
- **`--eden-trait` n'est pas la graisse du dessin, c'est un liseré.** Le dessin est fait
  d'aplats ; son trait le plus fin mesure 2 px sur une source large de 404, soit un
  demi-pixel à 26 px de haut — le château virerait au gris. La variable cerne alors
  chaque aplat d'un contour de sa propre couleur, ce qui l'épaissit **et** resserre les
  fenêtres, qui sinon se boucheraient à l'anti-crénelage. Elle s'exprime en pixels
  d'écran (`vector-effect="non-scaling-stroke"` sur les tracés) : 0,9 en en-tête, 0 dans
  le rideau. Un moteur qui ignorerait `non-scaling-stroke` lirait 0,9 unité sur 1024 —
  invisible, jamais un pâté. La variable traverse l'arbre du `<use>` (les propriétés
  personnalisées s'y héritent), d'où une seule définition pour trois tailles ; côté
  icônes la même compensation est figée taille par taille, un PNG ne connaissant qu'une
  dimension.
- **`--eden-feuille` bascule sans transition.** Le trait de la marque suit `color` et
  fond en 0,5 s au passage du header en `.is-solid` ; le feuillage passe par une
  propriété personnalisée, qui ne sait pas s'interpoler sans `@property`. À 26 px, les
  deux teintes changeant dans le même sens, la bascule ne se voit pas — ne pas ajouter
  d'`@property` pour ça.
- **Les icônes sont le dessin bichrome sur tuile ivoire** — onglet compris. À 16 px le
  château s'empâte : c'est un arbitrage assumé en faveur de la cohérence de marque. Une
  silhouette simplifiée tiendrait mieux à cette taille ; ne pas y revenir sans le
  demander au client.
- **Le rideau ne « dessine » plus le château, il le lève.** La version au trait
  déroulait `stroke-dashoffset` sur des tracés `pathLength="1"` ; le nouveau dessin est
  fait d'aplats, il n'y a plus de longueur à dérouler. L'animation porte sur le
  `clip-path` du `<svg>` hôte — un front horizontal qui remonte — ce qui laisse la
  marque partagée avec l'en-tête intacte : rien à dupliquer, rien à animer dans l'arbre
  du `<use>`.
- **Les polices sont auto-hébergées, et sans `preload`.** Le passage par Google
  Fonts coûtait deux allers-retours en cascade (googleapis pour la feuille, puis
  gstatic pour les woff2) que les `preconnect` ne masquaient qu'à moitié : les
  polices n'arrivaient qu'à 5,2 s en 3G bridée, contre 3,0 s servies depuis le
  domaine. Leurs `@font-face` sont **dans `styles.css`**, pas dans une feuille à
  part : styles.css bloque déjà le rendu, une seconde requête n'ajouterait qu'un
  aller-retour. Et **ne pas les précharger** : mesuré, `<link rel=preload as=font>`
  vole la bande passante au CSS et à l'image de tête, qui pèsent plus lourd — le
  LCP de chambres.html passait de 3,0 à 5,1 s. Les doublures métriques suffisent
  à rendre le texte lisible tout de suite. Seuls latin et latin-ext sont livrés :
  le site est francophone.

- **Un srcset doit déclarer toutes les variantes présentes sur le disque.** Le
  palier 1250 avait été généré sans être branché dans le balisage : un mobile en
  DPR 3 (390 × 3 = 1170 px demandés) ne trouvait rien entre 1100 et 2000 et
  prenait le 2000. LCP de chambres.html : 6,0 s → 3,3 s une fois le 1250 déclaré.
  Après tout passage de `generer-images.py`, vérifier que le HTML suit — en
  gardant la monotonie du srcset, qui est ce qui justifie l'absence *volontaire*
  du 1500 sur `chambre-suite`, `chambre-brumes` et `salle-a-manger` (il y pèse
  plus lourd que le 2000, le script l'élague).

- **La parallaxe mesure un parent, pas l'image** : le rect de l'image inclut la
  translation qu'on vient de lui appliquer, donc le décalage se cumulerait.

- **Les disques débordent par `translate`, pas par un `top`/`left` négatif.** Un
  pourcentage de position se mesure sur le conteneur, un pourcentage de `translate` sur la
  boîte du disque : le même réglage sortirait un disque de 30 px d'une section courte et de
  300 px d'une section longue. `translate` est utilisé comme **propriété autonome**, pour
  laisser `transform` à la dérive (`.disque--flotte`) sans qu'elles s'écrasent.

- **Aucun `overflow-x: hidden` global n'a été ajouté, et il ne faut pas en ajouter.**
  Les disques sortent du cadre mais sont clippés deux fois : par `.disques`
  (`overflow: hidden`) et par la section qui l'accueille, qui l'était déjà. Vérifié à
  390 px sur les six pages : `scrollWidth == clientWidth`.

- **Le vert franc va dans les disques, jamais sous les mots.** Mesuré : au-delà de 0,16
  d'alpha de `--vert` (ou 0,12 de `--vert-doux`) posé sur `--vert-profond`, les petits
  accents en vert tendre passent sous 4,5:1 ; au-delà de 0,2 sur la forêt, c'est l'eyebrow
  en vert clair qui tombe (4,17:1 à 0,3). Là où un disque franc croise une zone de lecture
  — le panneau de citation —, un **voile de `--vert-profond` passe au-dessus des disques et
  sous le texte** : les coins gardent le vert vif, la colonne de lecture son fond porteur.

- **Le contraste se mesure sur la page rendue, pas sur le CSS.** Un disque, un dégradé ou
  une photo passés sous un mot ne se voient dans aucune feuille de style. La méthode
  employée : on emballe chaque nœud de texte dans un `<span>`, on relève ses rectangles de
  ligne, puis on rephotographie la page **avec l'encre rendue transparente** et on
  échantillonne le fond réel sous chaque mot (Playwright + Pillow). Trois précautions sans
  lesquelles le relevé ment : figer les animations, désactiver `scroll-behavior: smooth`,
  et photographier écran par écran — jamais en `fullPage`, où Chromium redimensionne le
  viewport à la hauteur du document et recalcule tous les `svh`/`dvh`.

- **`radial-gradient(circle 46% at …)` est invalide** : le rayon d'un cercle doit être une
  longueur ou un mot-clé (`closest-side`…), jamais un pourcentage — seule une ellipse en
  accepte. Toute la déclaration `background` est alors jetée **sans erreur visible**, et
  c'est ainsi que le voile sombre du CTA final avait disparu. Écrire `ellipse X% Y%`.

- **Le formulaire poste sur `/api/demande`, pas sur l'adresse n8n.** Le proxy de
  `netlify.toml` n'est pas une coquetterie : il évite au navigateur du visiteur
  d'avoir à joindre `n8n.srv….hstgr.cloud`, un tiers qu'un filtrage d'entreprise
  (FortiGate) bloque volontiers comme « non catégorisé » — le formulaire
  échouerait alors sur un réseau où le site s'affiche parfaitement. Il supprime
  aussi tout pré-vol CORS, la requête devenant de même origine. Le repli vers
  l'adresse directe **ne joue que sur un 404** (proxy absent) : se rabattre sur
  un 500, qui vient de n8n lui-même, ferait arriver la demande deux fois chez les
  hôtes.

- **Le mail du visiteur ne porte aucun montant, et ce n'est pas un oubli.** Le
  payload transporte bien une `estimation` (tarif de la chambre × nuits, plus la
  table d'hôtes), mais seul le gabarit interne l'affiche : le site ne chiffre rien
  au visiteur, il n'y a ni paiement en ligne ni devis automatique, et la
  réservation reste arbitrée par les hôtes. L'ajouter côté visiteur en ferait un
  devis ferme. Même raison pour le récapitulatif : `recap` est construit par la
  fonction qui remplit l'étape 3 du formulaire, si bien que ce qui part est
  exactement ce que le visiteur a relu — ne pas recomposer ces lignes dans n8n.

- **Le rayon d'une photo se pose sur son conteneur ou sur l'`<img>`, jamais sur le
  `<picture>`** : celui-ci est en `display: contents` et n'a pas de boîte à découper
  (même raison que le piège ci-dessus).

- **Le médaillon rond garde la largeur de la photo qu'il remplace.** La vue en médaillon
  du collage éditorial est passée de `aspect-ratio: 4/3` à `1`, mais sa largeur est
  toujours 54 % de la colonne : les `sizes` du balisage restent justes. Changer la largeur
  d'un média oblige à repasser `tools/verifier-sizes.py`.

- **`.aside-band` reste sur une colonne.** Ses `sizes` déclarent 1 140 px au desktop,
  c'est-à-dire toute la largeur du conteneur. La passer en deux colonnes ferait rendre la
  photo à ~520 px : le navigateur téléchargerait deux fois trop d'octets sans qu'on ait
  touché au HTML.

- **Pas d'`overflow: hidden` sur l'en-tête**, malgré ses coins bas arrondis : son
  `backdrop-filter` en fait déjà le bloc conteneur de ses descendants fixes, et le menu
  plein écran en dépend. La jauge de lecture est rentrée du rayon des coins plutôt que
  clippée.

## Vérification visuelle

Tester avec Playwright (installé globalement) : servir `site/` via
`python -m http.server`, capturer desktop 1440×900 et mobile 390×844, pleine page.
Comparer l'intention à la charte avant toute itération de design.

## Contenus — points de vigilance

- 5 chambres : Suite du Roi et de la Reine, Antichambre de la Nuit, Boudoir des Rêves,
  Refuge des Brumes, Repaire des Songes. Tarifs 90 — 104 € petit-déjeuner compris
  (104 € la Suite du Roi et de la Reine ; 97 € l'Antichambre de la Nuit et le Repaire
  des Songes ; 90 € le Boudoir des Rêves et le Refuge des Brumes).
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
- **Thomas Ploton** (équicoaching à pied, à l'Espace Soreï, au sein du domaine) : son
  site est séparé (<https://thomasploton.fr/>), uniquement un lien sortant. L'encart
  porte **son nom**, pas celui du lieu — « Espace Soreï » ne dit rien à qui arrive
  sur la page, le client l'a fait remarquer. Il reste court : deux phrases, un lien.
  Ne pas réintégrer ses formules ni ses tarifs. La photo de fond de l'encart
  (`chevaux-aube`) vient de son site — seule source disponible, et elle plafonne à
  **1600 px**, là où les vues du château montent à 2000. Elle est voilée de vert profond
  et cadrée à 42 % de sa hauteur : le défaut de `cover` ne montrait que de l'herbe.
  Et elle est le fond de la SECTION, pas une vignette dans une tuile — essayé, la tuile
  faisait trois fois sa hauteur en largeur et n'en laissait voir qu'une lanière.
- Un seul geste attendu du visiteur : **envoyer une demande** (pas de paiement en ligne,
  pas de calendrier de disponibilités). La réservation reste gérée par les hôtes.
- Coordonnées : 2562 Avenue de Bazac, 43800 Beaulieu · 06 65 32 92 61 ·
  chateaulestourelles43@gmail.com · Arrivée 16 h–20 h, départ 9 h–10 h.
