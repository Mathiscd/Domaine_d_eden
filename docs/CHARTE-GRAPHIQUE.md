# Charte graphique — Domaine d'Éden

> **v4 — « rond, vert, familial »**. La v3 était éditoriale et anguleuse, calée sur
> grandlauron.com : angles vifs, filets d'un pixel, beaucoup de blanc, le vert en
> ponctuation. **Le client a demandé l'inverse**, et sa demande fait autorité : il veut
> retrouver l'esprit de sa maquette — tout arrondi, et de grands disques verts en fond.
> La v4 garde la typographie, les photos et la couleur de la v3 ; elle change les
> **formes** et la **quantité** de vert.

Direction : **maison d'hôtes chaleureuse**. Le site doit donner envie de pousser la porte,
pas d'admirer une façade. Ce que l'œil retient : des formes pleines et généreuses, de
grands cercles verts qui débordent du cadre, et des photos posées dans des cadres ronds.
Moins « palace », plus « on vous attend » — c'est une maison tenue par deux hôtes.

Trois gestes portent toute la direction :

1. **Rien n'a de coin droit.** Cartes, photos, boutons, champs, badges, vignettes,
   encadrés, bandes de section : tout passe par l'échelle de rayons (§ 4). Les rayons
   sont généreux et assumés — jamais un 4 px timide.
2. **Les disques.** De larges cercles du vert de marque et d'un vert plus clair, qui
   sortent par les bords, se chevauchent (deux disques qui se recouvrent dessinent une
   silhouette en pétale) et rythment le parcours. Ils sont **décoratifs** : le texte ne
   se pose jamais dessus sans passer par un fond porteur (§ 1).
3. **Le médaillon.** Là où c'est possible, un rond parfait : la seconde photo de
   l'éditorial, les vignettes du formulaire, les numéros d'étape, les pastilles, les
   boutons d'action.

**Ce qui ne change pas** : la couleur reste celle du client (`#74963D`, relevée sur son
identité), la typographie reste Cormorant Garamond + Jost, les photos restent celles du
lieu, et le ton éditorial reste le sien (§ 8). L'ancien site du client reste la **source
de contenu** — textes, informations, photos —, jamais une source de mise en page.

## 1. Couleurs

Une seule famille chromatique. Tout ce qui n'est pas photo est blanc, encre ou vert.

### Fonds
| Rôle | Nom | Hex | Usage |
|---|---|---|---|
| Fond principal | Blanc | `#FAFAF8` | fond de page, respiration |
| Fond alterné | Blanc verdi | `#F2F5EC` | sections alternées, encarts |
| Fond dense | Gris-vert | `#E4E9DA` | réserves d'image, troisième niveau |
| Blanc pur | Ivoire | `#FDFDFB` | texte sur fond sombre, boutons clairs |

### Encres
| Rôle | Nom | Hex | Usage |
|---|---|---|---|
| Encre | Vert-noir | `#161B14` | textes |
| Bande sombre | Forêt | `#22301A` | sections `--dark` (bandes photographiques) |

> Le pied de page et la carte « table d'hôtes » ne sont plus en encre ni en forêt :
> ils sont passés au **vert profond** `#40571E` (§ « les verts »). Le site se termine
> désormais sur du vert, pas sur du noir.

### Les verts — **c'est la couleur du client, pas une interprétation**

Huit nuances, et **c'est une échelle de contraste, pas une palette décorative** : chaque
teinte est définie par ce qu'elle sait porter. Les ratios sont mesurés sur l'ivoire
`#FDFDFB`, sauf mention contraire.

| Rôle | Nom | Hex | Usage | Contraste |
|---|---|---|---|---|
| Vert de marque | Vert | `#74963D` | **disques**, filets, folios, bordures, survols, pictogrammes | 3,34:1 → grands titres et aplats seulement |
| Vert clair du client | Vert doux | `#8FB25C` | **disques** clairs, second disque du pétale | 2,37:1 → **décoratif**, ou porteur d'encre (7,2:1) |
| Vert d'aplat | Vert foncé | `#5C7A2E` | boutons, bandeau défilant, badges, pastilles, médaillons | 4,82:1 ✔ |
| Vert des blocs | Vert profond | `#40571E` | **tout aplat vert qui porte du texte courant blanc** : citation, carte table d'hôtes, encart illustré, pied de page, rideau | 7,93:1 ✔ (5,97:1 sur ivoire à 82 %) |
| Vert de texte | Vert texte | `#4F6B26` | italiques display, prix, eyebrows, liens accentués | 5,95:1 ✔ |
| Vert clair | Vert clair | `#9DBA6A` | accents **sur la forêt `#22301A`** | 6,42:1 sur forêt ✔ (3,72:1 sur vert profond) |
| Vert tendre | Vert tendre | `#C6D9A2` | petits accents **sur vert profond** : eyebrows, intertitres du pied, prix | 5,33:1 sur vert profond ✔ |
| Vert éteint | Sauge | `#5E7048` | labels secondaires, légendes, spécifications | 5,2:1 ✔ |

Règles :

- **Le vert de marque `#74963D` ne porte jamais de texte courant.** Il vaut 3,34:1 : de
  quoi tenir un grand titre (≥ 24 px, ou ≥ 18,66 px gras), rien d'autre. Le vert doux
  `#8FB25C`, à 2,37:1, ne porte **aucun** texte blanc, pas même un titre.
- **Un aplat vert qui porte un paragraphe est en `--vert-profond`, jamais ailleurs.**
  C'est la seule teinte de la famille qui laisse de la marge à l'ivoire à 82 %.
- **Un aplat qui porte du texte reste proche de son fond porteur.** Mesuré : au-delà de
  0,16 d'alpha de `--vert` (ou 0,12 de `--vert-doux`) posé sur `--vert-profond`, les
  petits accents en vert tendre passent sous 4,5:1. Le vert franc va dans les **disques**,
  pas sous les mots.
- **L'italique du titre est en `--vert-txt`, pas en `--vert`.** Sur un blanc nu, le vert de
  marque tenait tout juste ses 3:1 ; sous un disque, même très pâle, il tombait à 2,67:1.
- Sur les fonds sombres photographiques, les disques sont plafonnés à 0,2 d'alpha :
  au-delà, ils éclaircissent assez la forêt pour faire passer un eyebrow en vert clair
  sous AA (4,17:1 mesuré à 0,3).
- Aucune autre teinte n'est autorisée : ni brun, ni laiton, ni terre cuite. Seule
  exception fonctionnelle : `--erreur` `#9E3B2B`, réservé aux messages d'erreur de
  formulaire — jamais décoratif.
- Fonds sombres = `#40571E` (vert profond) pour les blocs, `#22301A` / `#161B14` pour les
  bandes photographiques. Jamais de noir pur.
- **Contraste minimum AA (4,5:1) pour tout texte**, 3:1 pour les grands textes, y compris
  eyebrows et légendes. Cela se **mesure sur la page rendue**, pas sur le CSS : un disque
  ou un dégradé passé sous un mot ne se voit dans aucune feuille de style.

### Les disques

Le motif du site, et sa seule ornementation. Un disque est un `<span>` vide, `aria-hidden`,
en `border-radius: 50%` — jamais une image, jamais un SVG répété.

- **Ils débordent.** Un disque touche toujours au moins un bord de sa section et sort du
  cadre. Le débord se règle en `translate` (pourcentage de la boîte du disque), pas en
  `top`/`left` négatif : un pourcentage de position se mesure sur le conteneur, et le même
  réglage sortirait un disque de 30 px d'une section courte et de 300 px d'une longue.
- **Ils se chevauchent par deux.** Un grand disque plein et un plus petit décalé d'un
  tiers : leur recouvrement dessine la silhouette en pétale de la maquette du client.
- **Ils ne saturent pas.** Un ou deux par section, aux charnières du parcours — hero,
  citation, chambres, événementiel, CTA final, pied de page. Une section sur deux peut
  s'en passer.
- **Ils sont dimensionnés en `clamp(px, vw, px)`** : un disque de 620 px sur un 1440
  écraserait un écran de 390.
- **Ils ne créent jamais de défilement horizontal** : le conteneur `.disques` est en
  `overflow: hidden`, et les sections qui l'accueillent le sont déjà. C'est ce qui permet
  de ne pas poser d'`overflow-x` global, qui casserait le repère de calcul de l'en-tête.
- **Le texte ne se pose pas dessus.** Là où un disque franc croise une zone de lecture —
  le panneau de citation —, un voile de `--vert-profond` passe **au-dessus des disques et
  sous le texte** : les coins gardent le vert vif, la colonne de lecture retrouve son fond
  porteur.

## 2. La marque

Le château dessiné à la main que le client a fourni : façade au trait, volets sombres,
toits de tourelles et grand arbre en aplat vert. Le PNG d'origine
(`photos-sources/logo-domaine-eden.png`) reste la référence, mais il n'est jamais publié
tel quel : il est **vectorisé** par `tools/generer-logo.py`, qui sépare les deux encres,
suit leurs contours et **écarte le lettrage**. Tout ce qui affiche la marque descend de
ce script.

- **Le dessin seul, jamais le lettrage du fichier.** « Château les Tourelles » et
  « Domaine d'Éden » sont composés par les pages en Jost et en Cormorant, à la bonne
  graisse et à toutes les tailles. Les reprendre en bitmap depuis le PNG les rendrait
  flous et désaccordés du reste.
- **Deux teintes, deux rôles.** Le trait du château suit `currentColor` ; l'arbre et les
  toits suivent `--eden-feuille`. Les couples admis : ivoire + `--vert-clair` sur une
  photo sombre (hero), ivoire + `--vert-tendre` sur un aplat de **vert profond** (pied de
  page, rideau — le vert clair y descendrait à 3,7:1), `--foret` + `--vert` sur fond clair
  (en-tête au scroll, pages sans hero, menu mobile ouvert). Sans `--eden-feuille`, la
  marque redevient monochrome — c'est le repli, pas une variante à choisir.
- **Graisse optique.** Le trait du dessin descend à 2 px sur une source large de 404 :
  ramené à 26 px de haut, il tombe sous le demi-pixel et le château vire au gris.
  `--eden-trait` cerne alors chaque aplat d'un liseré de sa propre couleur, en pixels
  d'écran : 0,9 en en-tête à 26 px, 0,85 en pied de page à 30 px, 0 au-delà de 90 px —
  plus haut, le liseré bouche les fenêtres.
- **Elle reste discrète.** Emblème au-dessus du nom, jamais à côté ni à la place :
  c'est la signature typographique qui porte, la marque ponctue. En en-tête elle plafonne
  à 26 px et ne touche jamais le filet du rang de service.
- **Zone de respect** : au minimum la hauteur d'une tourelle autour du dessin. La marque
  ne se pose jamais sur une photo chargée — en-tête, elle bénéficie du voile du hero.
- **Icônes : le dessin bichrome sur tuile ivoire** — de l'onglet 16 px à l'icône d'écran
  d'accueil. À 16 px le château s'empâte : c'est assumé, la cohérence de la marque prime
  sur la netteté de l'onglet. La compensation optique y est figée taille par taille dans
  `generer-logo.py`, un PNG ne connaissant qu'une dimension.
- **Ne pas** : la recolorer hors des deux couples ci-dessus, l'incliner, l'étirer, lui
  rendre le lettrage du PNG, ou la reproduire depuis une capture. On la régénère.

## 3. Typographie

| Usage | Fonte | Style |
|---|---|---|
| Titres display (h1, h2) | **Cormorant Garamond** 300 | très grandes tailles, `letter-spacing: 0.005em`, jamais gras |
| Mot d'accent dans un titre | Cormorant Garamond **italique**, vert de marque | un fragment par titre, jamais plus |
| Eyebrows / labels / nav | **Jost** 500 | 11–12 px, uppercase, `letter-spacing: 0.22–0.26em`, vert texte |
| Corps de texte | **Jost 400** | 17 px, `line-height: 1.7`, colonne max 60 ch |
| Chiffres remarquables, folios, prix | Cormorant Garamond italique | index « 01 », prix, distances |

> Le corps est passé de Jost 300 à **Jost 400** : en 300 sur fond clair, le texte disparaissait.

Échelle desktop : h1 hero `clamp(3.4rem, 9vw, 7.5rem)` · h2 `clamp(2.5rem, 5.4vw, 4.3rem)`
· h3 `clamp(1.5rem, 2.3vw, 1.9rem)` · corps `1.09rem`.

Hiérarchie type d'une section :
```
                                    01     ← folio géant, vert 8,5 %, en filigrane
— EYEBROW VERT ESPACÉ                      ← Jost 11px, uppercase
Grand titre serif                          ← Cormorant, encre
en italique verte                          ← le fragment qui porte l'émotion
Paragraphe posé, colonne étroite            ← Jost 400, max 60ch
```

**Lettrine** : le premier paragraphe éditorial porte une capitale Cormorant verte
(`.dropcap`, 3.6em, flottante). Une seule par page.

## 4. Rayons, espacements & grille

### L'échelle de rayons

Elle est déclarée une seule fois, en tête de `styles.css`. **Un composant choisit un
barreau de l'échelle, jamais une valeur en dur** — et aucun ne reste à zéro.

| Variable | Valeur | Pour |
|---|---|---|
| `--r-xs` | `0.55rem` | coches, filets, micro-éléments |
| `--r-sm` | `0.95rem` | petites tuiles — barreau libre aujourd'hui, gardé pour que l'échelle reste continue |
| `--r-md` | `clamp(1rem, 2.2vw, 1.5rem)` | lignes de coordonnées, récapitulatif |
| `--r-lg` | `clamp(1.4rem, 3.4vw, 2.2rem)` | cartes, photos de carte, encadrés, cartes de choix |
| `--r-xl` | `clamp(1.8rem, 5vw, 3.2rem)` | encarts pleine largeur, coins bas de l'en-tête |
| `--r-2xl` | `clamp(2.2rem, 7vw, 4.5rem)` | bandes de section, grands médias, hero, pied de page |
| `--r-pilule` | `999px` | boutons, badges, champs d'une ligne, puces, jauges, tuiles de liste |
| `--r-cercle` | `50%` | médaillons, pastilles, icônes, vignettes, numéros |

Les grands barreaux sont en `clamp` : un rayon fixe de 48 px avale une carte de 300 px sur
un téléphone. Et un rayon a besoin d'épaisseur pour se voir — les filets d'un pixel de la
v3 sont passés à 2 ou 3 px avant d'être arrondis.

**Cas particulier des photos** : le rayon se pose sur le **conteneur** (`figure`, `div`)
avec `overflow: hidden`, ou directement sur l'`<img>`. Jamais sur le `<picture>`, qui est
en `display: contents` et n'a pas de boîte à découper.

**Deux bandes de même teinte qui se suivent** (le cadre puis le déroulé, sur
`evenements.html`) soudent leur couture : sans cela, le fond de page apparaît en accolade
entre les deux.

### Espacements & grille

- Rythme vertical : sections `clamp(5.5rem, 11vw, 9.5rem)`. Ne jamais tasser.
- Conteneur : `max-width: 1240px`, gouttières `clamp(1.25rem, 4vw, 3.25rem)`.
- Le blanc reste un matériau — mais il doit être **rythmé** : blanc → blanc verdi →
  bloc vert → bandeau pilule → blanc. Jamais trois sections claires consécutives sans
  respiration ; c'est désormais un disque ou un bloc vert qui la donne.
- Grilles éditoriales asymétriques (5/7, 6/5) plutôt que 50/50.
- Galerie : mosaïque à **placement explicite** (4 colonnes × 3 rangées, remplissage exact).
  Les spans automatiques laissent des trous — ne pas y revenir.

## 5. Imagerie & matière

- Photos du lieu uniquement — jamais de banque d'images.
- Ratios maîtrisés : hero plein écran, portraits 3/4 pour les chambres, 4/5 éditorial.
- Traitement : aucun filtre de couleur ; voile vert profond en dégradé
  (`rgba(20,30,10,0.4→0.9)`) sur les photos support de texte. **Le texte prime toujours
  sur la photo** : si le titre se bat avec l'image, on assombrit le voile, on ne déplace
  pas le titre. Les densités actuelles ont été relevées jusqu'à ce que la mesure au pixel
  passe — la façade du château est claire, et un voile « qui a l'air suffisant » ne l'est
  pas toujours.
- **Coins ronds partout** (§ 4). Les photos de cartes prennent `--r-lg`, les grands médias
  et les bandeaux `--r-2xl`.
- **Médaillons** : là où la photo est un portrait du lieu plutôt qu'un plan large, elle
  devient un cercle parfait — la seconde vue du collage éditorial, les vignettes de
  chambre du formulaire, les vignettes de la visionneuse. Un médaillon garde la **largeur**
  rendue de la photo qu'il remplace : les `sizes` du balisage restent justes.
- **Grain papier** : un bruit SVG fixe (`--grain`) en `multiply` à 5,5 % sur toute la page.
  C'est ce qui empêche les aplats blancs de paraître morts. Ne pas le retirer.
- **Folios** : le numéro de section en Cormorant italique, 12rem, vert 8,5 %, calé
  au-dessus du contenu (`top: -0.75em`) pour ne jamais mordre un titre.

## 6. Composants

**Boutons** — des **pilules** (`--r-pilule`), jamais un rectangle. Au survol, un **voile
circulaire s'épanouit depuis le centre** (`::before` en `scale(0 → 1)` sur un cercle de
250 % du bouton, 550 ms) et le bouton se soulève de 2 px. Le voile qui montait par le bas
appartenait au vocabulaire anguleux : un front droit sous un bord rond se voit.
- Primaire : vert foncé → vert profond au survol, texte ivoire.
- Clair : ivoire (texte vert profond) → vert foncé au survol.
- Ghost : bordure verte 1,5 px et texte vert texte, se remplit de vert foncé.
- Ghost clair : bordure ivoire sur fond sombre, se remplit d'ivoire.
- Lien sortant (`.btn--out`) : flèche ↗ accolée au label, `target="_blank" rel="noopener"`.
- Lien fléché : label espacé + trait vert arrondi qui s'allonge de 2,4 à 4 rem.

**Header — deux rangs**, calé sur la référence Grand Lauron :
1. *Barre de service*, 62 px : **réseaux sociaux à gauche** (pictogrammes SVG dans des
   boutons ronds de 34 px, bordure 1px, qui se remplissent de vert au survol), **signature
   centrée**, **numéro de téléphone à droite** (Cormorant 1,18 rem + petit combiné).
2. *Navigation*, 54 px, centrée : Accueil · Le domaine · Les chambres · Événements ·
   Galerie · Contact + bouton « Réserver ».

Transparent sur le hero ; au scroll il devient une **tuile** blanche translucide et floutée,
aux **deux coins bas arrondis** (`--r-xl`), posée sur la page avec une ombre douce — le filet
d'un pixel qui la soulignait de bord à bord ne tient pas sous un coin rond. **S'escamote à la
descente, revient à la remontée.** Jauge de lecture : une pilule de 3 px (vert clair → vert),
**rentrée du rayon des coins**, sans quoi elle dépasserait de l'arrondi par les deux bouts.

Pas d'`overflow: hidden` sur l'en-tête : son `backdrop-filter` en fait déjà le bloc conteneur
de ses descendants fixes, et le menu plein écran en dépend.
La nav souligne la page courante (`aria-current`) ou, sur l'accueil, la section lue
(scroll-spy — l'attribut `data-spy` neutralise alors le marqueur « Accueil »).
Sous 940 px : le second rang s'efface, un burger ouvre un menu plein écran qui reprend
**en pied de menu le téléphone et les deux pictogrammes**.

**Cartes chambres** — photo 3/4 en `--r-lg` ; au survol : zoom 1.07 (900 ms), voile sombre
en bas, mention « Découvrir » qui monte avec un filet vert clair arrondi, titre qui passe en
vert texte. Prix en italique serif vert texte.

**Carte de service** (`.room-card--service`, la table d'hôtes) — sixième case de la grille
des chambres, en **vert profond** : c'est un service, pas une chambre, et elle porte du texte
courant blanc. Accents en vert tendre.

**Chambre en pleine largeur** (`.room-detail`, page Chambres) — grille 6/5 alternée un rang
sur deux, photo 4/3 en `--r-2xl`, **folio romain dans une pastille verte** posée sur la photo
(nu, il se perdait dans les zones claires), spécifications à puces rondes, pied de bloc en
**tuile verte pâle** : prix à gauche, bouton « Demander cette chambre » à droite.

**Encart illustré** (`.aside-band` — table d'hôtes, formule traiteur) — une grande tuile
`--r-2xl` : photo pleine largeur en tête, panneau vert profond dessous. Elle reste sur **une
colonne** : les `sizes` du balisage déclarent toute la largeur du conteneur, et la passer en
deux colonnes ferait télécharger deux fois trop d'octets.

**Cartes formats** (`.format-card`, page Événements) — fond blanc verdi, `--r-lg`, **chiffre
en médaillon vert** en tête (il remplace le filet de 2 px), élévation de 4 px au survol.

**Tuiles de fait** (`.fact`) — carte ronde, le chiffre dans une **pilule verte** en tête.

**Bandeau défilant** — une **grande pilule verte** rentrée des gouttières, vert foncé,
Cormorant italique, séparateurs en **points ronds** vert tendre, 42 s en boucle, **pause au
survol**. Son fond n'accepte que des accents *sombres* : le vert foncé donne tout juste ses
4,82:1 à l'ivoire, et le texte descend à 18 px sur téléphone. Un seul par page.

**Formulaire** — champs **en pilule pleine** (ivoire, bordure verte 1,5 px), qui prennent un
halo vert de 4 px au focus ; le message libre passe en `--r-lg`, une pilule de 140 px de haut
ferait un stade. Étapes en pastilles rondes de 2,4 rem reliées par une barre arrondie.
Cartes de choix et cartes chambres en `--r-lg` / pilule, **vignette ronde de 78 px**.
Récapitulatif et consentement en tuiles vert pâle. Erreurs en `--erreur`, seule teinte non verte.

**Galerie** — mosaïque de photos en `--r-lg`, visionneuse plein écran maison (clic, `Entrée`,
flèches ←/→, `Échap`), légende reprise de l'`alt`. Au survol : voile vert + **réticule dans
une pastille ronde**. Les commandes de la visionneuse sont trois pastilles de 46 px ; ses
vignettes, des médaillons ronds.

**Pied de page** — **vert profond**, deux grands coins hauts arrondis, un pétale de disques
qui remonte du coin bas gauche. C'est la dernière image qu'on emporte du site.

## 7. Mouvement

Le site doit **vivre au scroll**. Rien de gadget, tout en `cubic-bezier(.16,1,.3,1)`.

- **Rideau d'ouverture** : deux volets **verts** (vert profond, deux disques plus clairs en
  fond) qui s'écartent, chacun avec son **bord intérieur arrondi** — ce n'est plus une
  déchirure droite mais deux formes pleines qui glissent hors de l'écran. Un **médaillon
  circulaire** s'ouvre derrière la marque avant elle ; le château se lève ensuite par
  `clip-path`. Il ne joue **qu'à l'arrivée sur le site** : le script de garde inline dans le
  `<head>` tranche avant le premier paint (sessionStorage, repli sur le référent) et pose
  `no-curtain` + `is-loaded` sur `<html>`. Filet de sécurité : 3 s maximum.
- **Diaporama du hero** (accueil) : 5 vues du domaine en **fondu enchaîné de 1,7 s**, une
  vue toutes les 6,8 s, la vue affichée dérivant lentement de `scale(1.03)` à `scale(1.085)`.
  Repères cliquables en bas à droite : des **pastilles rondes de 9 px** qui s'étirent en
  pilule sur la vue courante (cible tactile de 44 px). Le défilement
  se met en pause quand l'onglet passe en arrière-plan. C'est la seule rotation automatique
  du site : ailleurs, les carrousels restent proscrits.
- **Cascade du hero** : eyebrow → titre → filet vert qui s'ouvre → tagline → CTA →
  indice de scroll → repères du diaporama, décalés de 120 à 1250 ms.
- **Titres à masque** (`.ln`) : chaque ligne monte depuis son propre cadre en overflow
  caché, 1,05 s, décalage 110 ms par ligne. Sur les bandeaux de titre des pages intérieures,
  la révélation est portée par `.is-loaded` (pas d'observateur : le titre est déjà à l'écran).
- **Volet photo** (`data-reveal="mask"`) : `clip-path: inset(0 0 100% 0)` qui s'ouvre en
  1,25 s pendant que l'image passe de `scale(1.18)` à `1` en 1,6 s.
- **Révélations** (`data-reveal="up"`) : translateY 30px + fade, 950 ms, cascade 110 ms.
  Une seule fois. Un élément déjà dépassé (arrivée sur une ancre) s'affiche sans animer.
- **Bandeau de titre** des pages intérieures : entrée seule (`scale(1.1 → 1)`, 2,8 s),
  sans dérive — la page n'y séjourne pas.
- **Parallaxe** : réservée aux fonds photo (`data-parallax`, coefficient ≤ 0.2),
  désactivée sous 900 px.
- **Dérive des disques** (`.disque--flotte`) : 22 à 31 s, `translate` + `scale(1,045)` en
  alternance. Le fond respire, rien ne bouge assez pour attirer l'œil. Elle porte sur
  `transform` seul — jamais sur une propriété qui déclencherait une remise en page — et la
  position du disque passe par la propriété autonome `translate`, pour ne pas se marcher
  dessus.
- Hover photo : `scale(1.07)`, 900 ms.
- **Interdits** : parallax agressif, compteurs animés, carrousels de contenu (le diaporama
  du hero est décoratif, pas un contenu à parcourir), confettis, curseur personnalisé.
- `prefers-reduced-motion: reduce` → rideau supprimé, diaporama figé sur la première vue,
  **dérive des disques arrêtée** (les disques restent, ils ne bougent plus), transitions à
  0,01 ms, tout visible.

## 8. Ton éditorial

Poétique et sobre, jamais commercial. On écrit « Un château pour rêver, un domaine pour
se ressourcer » (leur signature — à conserver), pas « Réservez vite ! ». Vouvoiement,
phrases courtes, vocabulaire sensoriel (lumière, pierre, brume, silence). Les CTA sont
des invitations : « Demander une disponibilité », « Composer votre séjour », « Écrivez-nous ».

Le bandeau défilant puise dans ce même vocabulaire — **des sensations, pas des arguments** :
« Pierre & lumière · Feux de bois · Silence du parc · Via Fluvia · Table d'hôtes ·
Nuits sous les tourelles ».
