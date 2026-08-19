# Charte graphique — Domaine d'Éden

> **v3 — « le vert de la maison »**. La v2 tenait sur une terre cuite inventée pour le site.
> Le client a sa couleur : le **vert #74963D** de son identité (cf. `Capture 6.PNG`).
> La v3 remplace intégralement les bruns, les laitons et les verts sapin/olive par une
> famille de verts construite sur ce vert-là, posée sur des **blancs** plutôt que sur des crèmes.

Direction : **éditorial château-nature**. Le site doit respirer comme un beau livre — de
grands blancs, une serif fine, des photos qui portent. Ce que l'œil retient : la lumière
des photos, la finesse de la serif, et **un seul vert**, celui de la maison.

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
| Encre | Vert-noir | `#161B14` | textes, footer |
| Bande sombre | Forêt | `#22301A` | sections `--dark`, encart table d'hôtes |

### Les verts — **c'est la couleur du client, pas une interprétation**
| Rôle | Nom | Hex | Usage | Contraste |
|---|---|---|---|---|
| Vert de marque | Vert | `#74963D` | italiques display, filets, folios, voiles, bordures, survols, pictogrammes | 3,3:1 → **grands textes et aplats seulement** |
| Vert d'aplat | Vert foncé | `#5C7A2E` | boutons, bandeau défilant, badges, pastilles — tout ce qui porte de l'ivoire | 4,8:1 sur ivoire ✔ |
| Vert de texte | Vert texte | `#4F6B26` | prix, eyebrows, liens accentués, chiffres, survols de titre | 5,8:1 ✔ |
| Vert clair | Vert clair | `#9DBA6A` | accents **sur fond sombre** : eyebrows, filets, numéros, soulignements | 6,4:1 sur forêt ✔ |
| Vert éteint | Sauge | `#5E7048` | labels secondaires, légendes, spécifications | 5,2:1 ✔ |

Règles :
- **Le vert de marque `#74963D` ne porte jamais de petit texte.** Sous 24 px, on descend
  à `--vert-txt` ; sur un aplat qui porte de l'ivoire, on descend à `--vert-fonce`.
  Les quatre nuances existent uniquement pour cette raison — ce n'est pas une palette
  décorative, c'est une échelle de contraste.
- Le vert doit apparaître dans **chaque section** au moins une fois (un mot de titre en
  italique, un prix, un filet, un survol).
- Aucune autre teinte n'est autorisée : ni brun, ni laiton, ni terre cuite, ni vert olive
  vif en aplat. Seule exception fonctionnelle : `--erreur` `#9E3B2B`, réservé aux messages
  d'erreur de formulaire — jamais décoratif.
- Fonds sombres = `#22301A` / `#161B14` (jamais de noir pur), texte dessus = ivoire à 82–96 %.
- **Contraste minimum AA (4.5:1) pour tout texte**, y compris eyebrows et légendes.

## 2. Typographie

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

## 3. Espacements & grille

- Rythme vertical : sections `clamp(5.5rem, 11vw, 9.5rem)`. Ne jamais tasser.
- Conteneur : `max-width: 1240px`, gouttières `clamp(1.25rem, 4vw, 3.25rem)`.
- Le blanc reste un matériau — mais il doit être **rythmé** : blanc → blanc verdi → forêt →
  bandeau vert → blanc. Jamais trois sections claires consécutives sans respiration.
- Grilles éditoriales asymétriques (5/7, 6/5) plutôt que 50/50.
- Galerie : mosaïque à **placement explicite** (4 colonnes × 3 rangées, remplissage exact).
  Les spans automatiques laissent des trous — ne pas y revenir.

## 4. Imagerie & matière

- Photos du lieu uniquement — jamais de banque d'images.
- Ratios maîtrisés : hero plein écran, portraits 3/4 pour les chambres, 4/5 éditorial.
- Traitement : aucun filtre de couleur ; voile `rgba(12,18,10,0.26→0.86)` en dégradé
  sur les photos support de texte. **Le texte prime toujours sur la photo** : si le titre
  se bat avec l'image, on assombrit le voile, on ne déplace pas le titre.
- Coins droits partout.
- **Grain papier** : un bruit SVG fixe (`--grain`) en `multiply` à 5,5 % sur toute la page.
  C'est ce qui empêche les aplats blancs de paraître morts. Ne pas le retirer.
- **Folios** : le numéro de section en Cormorant italique, 12rem, vert 8,5 %, calé
  au-dessus du contenu (`top: -0.75em`) pour ne jamais mordre un titre.

## 5. Composants

**Boutons** — rectangles fins, jamais de coins ronds. Au survol, un **voile plein monte
depuis le bas** (`::before` en `translateY(101% → 0)`, 550 ms) :
- Primaire : vert foncé → encre au survol, texte ivoire.
- Clair : ivoire → vert foncé au survol.
- Ghost : bordure 1px, se remplit d'encre (ou d'ivoire sur fond sombre).
- Lien sortant (`.btn--out`) : flèche ↗ accolée au label, `target="_blank" rel="noopener"`.
- Lien fléché : label espacé + trait vert qui s'allonge de 2,4 à 4 rem.

**Header — deux rangs**, calé sur la référence Grand Lauron :
1. *Barre de service*, 62 px : **réseaux sociaux à gauche** (pictogrammes SVG dans des
   boutons ronds de 34 px, bordure 1px, qui se remplissent de vert au survol), **signature
   centrée**, **numéro de téléphone à droite** (Cormorant 1,18 rem + petit combiné).
2. *Navigation*, 54 px, centrée : Accueil · Le domaine · Les chambres · Événements ·
   Galerie · Contact + bouton « Réserver ».

Transparent sur le hero, blanc translucide + flou au scroll. **S'escamote à la descente,
revient à la remontée.** Jauge de lecture 2 px (vert clair → vert) collée en bas du header.
La nav souligne la page courante (`aria-current`) ou, sur l'accueil, la section lue
(scroll-spy — l'attribut `data-spy` neutralise alors le marqueur « Accueil »).
Sous 940 px : le second rang s'efface, un burger ouvre un menu plein écran qui reprend
**en pied de menu le téléphone et les deux pictogrammes**.

**Cartes chambres** — photo 3/4 ; au survol : zoom 1.07 (900 ms), voile sombre en bas,
mention « Découvrir » qui monte avec un filet vert clair, titre qui passe en vert texte.
Prix en italique serif vert texte.

**Chambre en pleine largeur** (`.room-detail`, page Chambres) — grille 6/5 alternée un rang
sur deux, photo 4/3 avec son folio romain en ivoire, spécifications en `✦` espacés,
pied de bloc : prix à gauche, bouton « Demander cette chambre » à droite.

**Cartes formats** (`.format-card`, page Événements) — fond blanc verdi, filet vert 2 px
en tête, élévation de 4 px au survol.

**Bandeau défilant** — pleine largeur, vert foncé, Cormorant italique, séparateurs
✦ vert clair, 42 s en boucle, **pause au survol**. Un seul par page, entre deux sections claires.

**Formulaire** — champs sans fond, bordure basse 1px qui passe en vert au focus.
Étapes en pastilles numérotées Cormorant italique reliées par un filet (faite → vert foncé,
en cours → vert foncé + label vert texte). Cartes de choix : élévation 3 px + bordure verte
au survol, vert + fond teinté à la sélection. Erreurs en `--erreur`, seule teinte non verte.

**Galerie** — visionneuse plein écran maison (clic, `Entrée`, flèches ←/→, `Échap`),
légende reprise de l'`alt`. Au survol : voile vert + réticule ⤢.

## 6. Mouvement

Le site doit **vivre au scroll**. Rien de gadget, tout en `cubic-bezier(.16,1,.3,1)`.

- **Rideau d'ouverture** : voile encre plein écran avec la signature en Cormorant italique,
  qui se lève vers le haut (1,1 s). Filet de sécurité : 2,2 s maximum.
- **Diaporama du hero** (accueil) : 5 vues du domaine en **fondu enchaîné de 1,7 s**, une
  vue toutes les 6,8 s, la vue affichée dérivant lentement de `scale(1.03)` à `scale(1.085)`.
  Repères cliquables en bas à droite (traits de 2 rem, actif en vert clair). Le défilement
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
- Hover photo : `scale(1.07)`, 900 ms.
- **Interdits** : parallax agressif, compteurs animés, carrousels de contenu (le diaporama
  du hero est décoratif, pas un contenu à parcourir), confettis, curseur personnalisé.
- `prefers-reduced-motion: reduce` → rideau supprimé, diaporama figé sur la première vue,
  transitions à 0,01 ms, tout visible.

## 7. Ton éditorial

Poétique et sobre, jamais commercial. On écrit « Un château pour rêver, un domaine pour
se ressourcer » (leur signature — à conserver), pas « Réservez vite ! ». Vouvoiement,
phrases courtes, vocabulaire sensoriel (lumière, pierre, brume, silence). Les CTA sont
des invitations : « Demander une disponibilité », « Composer votre séjour », « Écrivez-nous ».

Le bandeau défilant puise dans ce même vocabulaire — **des sensations, pas des arguments** :
« Pierre & lumière · Feux de bois · Silence du parc · Via Fluvia · Table d'hôtes ·
Nuits sous les tourelles ».
