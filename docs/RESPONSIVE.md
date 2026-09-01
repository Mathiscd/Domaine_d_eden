# Responsive — charte de mission

Objectif : que le site soit **juste** sur n'importe quel écran, pas seulement
« pas cassé ». Le point de départ (1er septembre) est un site qui ne déborde
nulle part mais qui se contente d'empiler : sur un iPhone, les cinq chambres
de l'accueil forment un ruban de 11 000 px qu'il faut traverser au pouce.

Le relevé se fait avec `python tools/audit-responsive.py` (voir en bas).

## Ce qu'on vise

### 1. Le tableau de bord — mesurable, vérifié à chaque passe

| # | Cible | Départ |
|---|---|---|
| M1 | 0 débordement horizontal, 15 écrans × 4 pages | **atteint**, à ne pas perdre |
| M2 | 0 cible tactile < 44×44 px sur mobile et tablette (hors liens en ligne dans un paragraphe) | 15 à 27 par page |
| M3 | 0 texte < 12 px sur mobile | 22 à 69 par page |
| M4 | 0 paragraphe au-delà de 92 caractères par ligne | 1 sur tablette |
| M5 | Aucune page de plus de ~8 écrans de haut sur mobile (390×844) | accueil **18,5** · chambres 12,7 · événements 9,8 · réservation 4,6 |

**Sur M5, une réserve honnête.** Les rails ont fait tomber l'accueil de 18,5 à
14,8 écrans et les événements de 9,8 à 8,5. La page chambres, elle, ne bougera
presque pas : cinq fiches complètes à la suite, c'est du contenu, pas de la
mise en page. La descendre à 8 écrans demanderait de couper du texte — une
décision éditoriale qui appartient au client, pas à cette refonte. On note
l'écart plutôt que de le maquiller.

### 2. Les composants à rendre adaptatifs

Ordre de priorité. Un composant est « fait » quand il est vu et jugé bon en
capture sur mobile (390), petite tablette (768), tablette paysage (1024) et
desktop (1440) — et que le tableau de bord n'a pas régressé.

| # | Composant | Aujourd'hui | Attendu |
|---|---|---|---|
| C1 | `#chambres .rooms-grid` (accueil) | ~~3 col. → 2 → 1 empilée~~ | **fait** — rail à puces sous 900 px |
| C2 | `.formats-grid` (événements) | ~~2×2 dès 940 px, empilé à 640~~ | **fait** — rail à puces sous 900 px, vues de 380 px |
| C3 | `.room-detail` × 5 (chambres) | ~~5 fiches empilées, une photo + `details`~~ | **fait** — les 2 photos en rail, puces sur l'image, commandes à 44 px |
| C4 | `.gallery` | ~~4 col. → 2 → 1~~ | **fait** — mosaïque jusqu'à 640 px, puis rail à **deux rangs** (5 arrêts, 5 puces) |
| C5 | `.facts-grid`, `.steps-flow` (événements) | 1fr 1fr à 940, 1 col. à 640 | lisibles à 600–900 px, pas de colonne orpheline |
| C6 | `.around-grid`, `.contact-grid`, `.editorial` | 1 col. sous 900 | palier tablette intermédiaire |
| C7 | En-tête, nav burger **et pied de page** | burger sous 900 px | zone tactile ≥ 44 px, panneau confortable en paysage. C'est là que se concentre tout ce qui reste de M2 : `a.icon-btn` 34×34, `button.nav-toggle` 42×45, les liens de nav et de pied à 18–22 px de haut |
| C8 | `reservation.html` | champs 1 col. sous 640 | pas de zoom iOS (≥ 16 px), progression lisible, vignettes tapables |

### 3. Les règles de construction

- **Une seule primitive de carrousel**, réutilisée par C1, C2, C3, C4. Elle
  compte ses puces par **arrêt** (position de défilement distincte), pas par
  enfant : un rail à deux rangs comme la galerie a deux fois moins de puces
  que de vues. Seuil commun à 900 px, sauf `data-rail="etroit"` qui ne prend
  qu'à 640. Pas
  cinq implémentations. Un rail `scroll-snap-type: x mandatory` en CSS + un
  petit module dans `main.js` (§11) qui fabrique les puces, suit la position
  au défilement et pose les attributs ARIA. Le seuil de bascule n'est écrit
  qu'une fois, en CSS : le JS lit l'`overflow-x` calculé pour savoir si le
  rail est actif. Le rail doit rester utilisable **sans JavaScript** — c'est
  du défilement natif, les puces sont un ajout.
- **Le desktop ne bouge pas.** Toute la transformation vit dans des
  `@media (max-width: …)`. Une passe qui change le rendu à 1440 px est ratée.
- **Pas de librairie.** Contrainte du projet, elle tient ici aussi.
- **`prefers-reduced-motion`** : le défilement des carrousels passe en
  `scroll-behavior: auto`, pas d'animation de puce.
- **Accessibilité** : le rail est `role="group"` + `aria-roledescription="carrousel"`,
  chaque vue `aria-label="n sur N"`, les puces sont de vrais `<button>` de
  44 px de zone tactile. La navigation au clavier suit le focus.
- Ne pas toucher aux images, au logo, ni aux polices : leurs réglages sont
  mesurés et documentés dans `CLAUDE.md`.

## Le banc d'essai

```
python tools/audit-responsive.py                     # 15 écrans × 4 pages, captures pleine page
python tools/audit-responsive.py --rapide            # 4 tailles clés
python tools/audit-responsive.py --vp mobile         # une classe d'écran
python tools/audit-responsive.py --composants        # une capture par bloc
python tools/audit-responsive.py --cadres            # la fenêtre cadrée sur chaque bloc
```

`--cadres` est le cadrage qui compte pour juger un carrousel : on y voit
l'amorce de la vue suivante, les puces, et ce que l'en-tête recouvre.
`--composants` sort le bloc seul, utile pour lire un détail.

**Et surtout, à chaque passe :**

```
python tools/verifier-desktop.py
```

Il rend les quatre pages à six largeurs de 901 à 1920 px et compare au rendu
de référence. C'est la preuve que la règle « le desktop ne bouge pas » tient.

**Figer la référence avant d'éditer**, pas comparer à `HEAD` :

```
python tools/verifier-desktop.py --figer   # au début de la passe
… on édite …
python tools/verifier-desktop.py           # à la fin
```

Le dossier de travail peut contenir le travail de quelqu'un d'autre — c'est
arrivé pendant la passe 2, où les pieds de page ont gagné des liens légaux
d'une autre session. Comparer à `HEAD` mélange alors les deux ; une référence
figée juste avant d'éditer isole exactement l'effet de la passe.

En cas d'écart le script décrit les **bandes** qui diffèrent (position, taille,
poids en pixels) et écrit `.audit/ecart-<page>-<largeur>-{avant,apres}.png`.
La forme du diff se lit : une bande étroite et bien située est un changement
attendu, plusieurs bandes hautes sont une régression de mise en page.

Sorties dans `.audit/` (non versionné) : `RAPPORT.md`, `rapport.json`,
`shots/`. La sonde relève le débordement horizontal, les cibles tactiles, le
texte trop petit, les lignes trop longues, les images sous-résolues et les
carrousels détectés.

Trois mesures à ne pas mal lire :

- **`cibles`** mesure la zone qui répond au doigt, pas la boîte du texte : la
  sonde part du centre et s'écarte tant que le point d'impact retombe sur le
  même lien. Une carte rendue cliquable par un `::after` étendu compte donc
  pour sa vraie taille. Le champ `boite` donne la boîte brute à côté.

- **`flou`** compte les images servies sous la densité de l'écran. C'est un
  plafond des sources (930 px pour les chambres, 2000 px pour les bandeaux),
  documenté dans `CLAUDE.md` — **rien à corriger ici**, on le regarde
  seulement pour vérifier qu'un changement de mise en page n'a pas aggravé
  les `sizes`.
- **`coupables`** ignore ce qui est clippé par un parent : un marquee ou un
  visuel pleine largeur enfermé dans un `overflow: hidden` est intentionnel.

## Journal des passes

<!-- Une ligne par passe : date, objectif visé, ce qui a changé, état du tableau de bord. -->

| # | Objectif | Changement | M1 | M2 | M3 | M4 | M5 |
|---|---|---|---|---|---|---|---|
| 0 | relevé initial | banc d'essai `tools/audit-responsive.py` | ok | 15–24 | 22–69 | 1 | 18,5 / 12,7 / 9,8 / 4,6 |
| 1 | **C1** — les chambres de l'accueil en carrousel | Primitive de rail créée : CSS `[data-rail]` sous 900 px (flex + `scroll-snap` + sortie de gouttière), puces posées par `main.js` §11. Le seuil n'existe qu'en CSS, le JS lit `overflow-x` calculé — pas de valeur recopiée. `sizes` des cartes recalé de `93vw` à `min(78vw, 320px)`. Ajout de `tools/verifier-desktop.py` : 24/24 rendus desktop identiques. | ok | 15–24 | 22–69 | 0–1 | accueil **18,5 → 14,8** |
| 2 | **C2** — les cartes formats en carrousel | `data-rail` sur `.formats-grid`, vues de `min(86%, 380px)` — du texte demande plus de largeur qu'une photo. **Sonde M2 corrigée** : elle mesurait la boîte du `<a>` et signalait les cartes entièrement cliquables par `::after` étendu ; elle mesure désormais la zone qui répond au doigt. **Sonde réordonnée** : elle passe après les captures et restaure les positions de défilement, son `scrollIntoView` laissait les rails déplacés. `verifier-desktop.py` : mode `--figer` + description des bandes en écart. | ok | 15–27 | 25–72 | 0–1 | événements 9,8 → **8,5** |
| 3 | **C3** — les deux photos de chaque chambre en rail | La photo de salle de bains, jusqu'ici accessible seulement en visionneuse, entre dans la page : un vrai `<picture>` avec ses srcsets avif/webp/jpg (généré depuis `data-room-photos` et les fichiers sur disque), **pas une injection JS** qui aurait perdu les variantes. Au-dessus de 901 px la 2ᵉ vue est `display:none` et `loading="lazy"` — **mesuré : 0 photo de sdb téléchargée en desktop**, 2 en mobile. Puces posées sur l'image (en flux, elles poussaient le bouton hors du cadre). La visionneuse s'ouvre sur la photo touchée, plus sur la première. `room-media-btn` et `summary` portés à 44 px. `verifier-desktop.py` : seuil de perception appliqué aussi à la détection. | ok | chambres **27 → 17** | 72 | 0–1 | chambres 12,7 → 12,6 |
| 4 | **C4** — la galerie en rail à deux rangs | La mosaïque tient jusqu'à 640 px (sur une tablette, une galerie doit rester une grille) ; en dessous, `grid-auto-flow: column` sur deux rangs. Neuf photos en file auraient demandé neuf puces, soit 396 px de cibles sur un écran de 390 — sur deux rangs elles font **cinq colonnes, donc cinq puces**, et on voit deux photos à la fois. La primitive compte désormais ses puces par arrêt, pas par enfant. `sizes` de la galerie recalé (27 attributs). **Les deux outils attendaient mal les images `lazy`** : ils capturaient le fond gris d'un `figure` et signalaient des régressions fantômes de la taille d'une photo — corrigé par un défilement par paliers puis attente du décodage. | ok | 15–24 | 25–72 | 0–1 | **accueil 14,8 → 12,7** |
