# Charte graphique — Domaine d'Éden

> **v2 — « matière & mouvement »**. La v1 visait l'épure ; elle est arrivée trop blanche
> et trop immobile. La v2 garde l'ossature éditoriale et lui rend ce qui lui manquait :
> **de la couleur tirée du lieu, de la matière, du contraste et du mouvement.**

Direction : **éditorial château-nature**. Le site doit respirer comme un beau livre —
mais un livre imprimé sur papier chaud, avec des encres, du grain et des folios, pas une
page blanche. Ce que l'œil retient : la lumière des photos, la finesse de la serif, et
une terre cuite qui rappelle les tomettes du château.

## 1. Couleurs

### Fonds
| Rôle | Nom | Hex | Usage |
|---|---|---|---|
| Fond principal | Crème | `#F5F1E8` | fond de page, respiration |
| Fond alterné | Lin | `#EDE7DA` | sections alternées (+ voile terre cuite très léger) |
| Fond dense | Sable | `#E2D9C7` | réserves d'image, troisième niveau |
| Blanc | Ivoire | `#FBF8F1` | texte sur fond sombre, boutons clairs |

### Encres
| Rôle | Nom | Hex | Usage |
|---|---|---|---|
| Encre | Vert-noir | `#161B14` | textes, footer |
| Bande sombre | Forêt | `#1E2C1A` | sections `--dark`, encart table d'hôtes |
| Accent vert | Sapin | `#2F5130` | bouton primaire, liens |
| Vert clair | Sauge | `#5E6E51` | labels, mentions secondaires |

### Chauds — **c'est ce qui donne son caractère au site**
| Rôle | Nom | Hex | Usage |
|---|---|---|---|
| Accent principal | Terre cuite | `#9E4A2B` | mots en italique des titres, prix, lettrine, filets actifs, états au survol, folios |
| Terre profonde | Terre foncée | `#8A3F24` | bandeau défilant pleine largeur |
| Métal | Laiton | `#A87A3C` | filets, ornements, accents sur fond sombre |
| Laiton texte | Laiton foncé | `#8A6229` | eyebrows sur fond clair (contraste AA) |

Règles :
- La **terre cuite est l'accent narratif** : elle vient des tomettes, des chaises et de la
  pierre dorée des photos. Elle doit apparaître dans **chaque section** au moins une fois
  (un mot de titre, un prix, un filet, un survol).
- Le vert sapin reste le seul vert saturé en aplat. Le vert olive vif de l'ancien site
  (`#7CA544` env.) est toujours proscrit.
- Fonds sombres = `#1E2C1A` / `#161B14` (jamais de noir pur), texte dessus = ivoire à 82–96 %.
- **Contraste minimum AA (4.5:1) pour tout texte**, y compris eyebrows et légendes. C'est
  pour cela que le laiton se dédouble : `#A87A3C` pour les filets, `#8A6229` pour le texte.

## 2. Typographie

| Usage | Fonte | Style |
|---|---|---|
| Titres display (h1, h2) | **Cormorant Garamond** 300 | très grandes tailles, `letter-spacing: 0.005em`, jamais gras |
| Mot d'accent dans un titre | Cormorant Garamond **italique**, terre cuite | un fragment par titre, jamais plus |
| Eyebrows / labels / nav | **Jost** 500 | 11–12 px, uppercase, `letter-spacing: 0.22–0.26em` |
| Corps de texte | **Jost 400** | 17 px, `line-height: 1.7`, colonne max 60 ch |
| Chiffres remarquables, folios, prix | Cormorant Garamond italique | index « 01 », prix, distances |

> Le corps est passé de Jost 300 à **Jost 400** : en 300 sur crème, le texte disparaissait.

Échelle desktop : h1 hero `clamp(3.4rem, 9vw, 7.5rem)` · h2 `clamp(2.5rem, 5.4vw, 4.3rem)`
· h3 `clamp(1.5rem, 2.3vw, 1.9rem)` · corps `1.09rem`.

Hiérarchie type d'une section :
```
                                    01     ← folio géant, terre cuite 8 %, en filigrane
— EYEBROW LAITON ESPACÉ                    ← Jost 11px, uppercase
Grand titre serif                          ← Cormorant, encre
en italique terre cuite                    ← le fragment qui porte l'émotion
Paragraphe posé, colonne étroite            ← Jost 400, max 60ch
```

**Lettrine** : le premier paragraphe éditorial porte une capitale Cormorant terre cuite
(`.dropcap`, 3.6em, flottante). Une seule par page.

## 3. Espacements & grille

- Rythme vertical : sections `clamp(5.5rem, 11vw, 9.5rem)`. Ne jamais tasser.
- Conteneur : `max-width: 1240px`, gouttières `clamp(1.25rem, 4vw, 3.25rem)`.
- Le blanc reste un matériau — mais il doit être **rythmé** : crème → lin → forêt →
  bandeau terre cuite → crème. Jamais trois sections claires consécutives sans respiration.
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
  C'est ce qui empêche les aplats crème de paraître morts. Ne pas le retirer.
- **Folios** : le numéro de section en Cormorant italique, 12rem, terre cuite 8 %, calé
  au-dessus du contenu (`top: -0.75em`) pour ne jamais mordre un titre.

## 5. Composants

**Boutons** — rectangles fins, jamais de coins ronds. Au survol, un **voile plein monte
depuis le bas** (`::before` en `translateY(101% → 0)`, 550 ms) :
- Primaire : sapin → terre cuite au survol, texte ivoire.
- Clair : ivoire → terre cuite au survol.
- Ghost : bordure 1px, se remplit d'encre (ou d'ivoire sur fond sombre).
- Lien fléché : label espacé + trait terre cuite qui s'allonge de 2,4 à 4 rem.

**Header** — transparent sur le hero, crème translucide + flou au scroll, hauteur 86 px.
**S'escamote à la descente, revient à la remontée.** Jauge de lecture 2 px (laiton →
terre cuite) collée en bas du header. La nav souligne la section courante (scroll-spy).

**Cartes chambres** — photo 3/4 ; au survol : zoom 1.07 (900 ms), voile sombre en bas,
mention « Réserver » qui monte avec un filet laiton, titre qui passe en terre cuite.
Prix en italique serif terre cuite.

**Bandeau défilant** — pleine largeur, terre cuite foncée, Cormorant italique, séparateurs
✦ laiton, 42 s en boucle, **pause au survol**. Un seul par page, entre deux sections claires.

**Formulaire** — champs sans fond, bordure basse 1px qui passe en terre cuite au focus.
Étapes en pastilles numérotées Cormorant italique reliées par un filet (faite → sapin,
en cours → terre cuite). Cartes de choix : élévation 3 px + bordure laiton au survol,
terre cuite + fond teinté à la sélection.

**Galerie** — visionneuse plein écran maison (clic, `Entrée`, flèches ←/→, `Échap`),
légende reprise de l'`alt`. Au survol : voile vert + réticule ⤢.

## 6. Mouvement

Le site doit **vivre au scroll**. Rien de gadget, tout en `cubic-bezier(.16,1,.3,1)`.

- **Rideau d'ouverture** : voile encre plein écran avec la signature en Cormorant italique,
  qui se lève vers le haut (1,1 s). Filet de sécurité : 2,2 s maximum.
- **Cascade du hero** : eyebrow → titre → filet laiton qui s'ouvre → tagline → CTA →
  indice de scroll, décalés de 120 à 1100 ms.
- **Titres à masque** (`.ln`) : chaque ligne monte depuis son propre cadre en overflow
  caché, 1,05 s, décalage 110 ms par ligne.
- **Volet photo** (`data-reveal="mask"`) : `clip-path: inset(0 0 100% 0)` qui s'ouvre en
  1,25 s pendant que l'image passe de `scale(1.18)` à `1` en 1,6 s.
- **Révélations** (`data-reveal="up"`) : translateY 30px + fade, 950 ms, cascade 110 ms.
  Une seule fois. Un élément déjà dépassé (arrivée sur une ancre) s'affiche sans animer.
- **Hero** : ken-burns d'entrée (1.14 → 1.02, 2,4 s) puis dérive lente infinie (26 s).
- **Parallaxe** : réservée aux fonds photo (`data-parallax`, coefficient ≤ 0.2),
  désactivée sous 900 px.
- Hover photo : `scale(1.07)`, 900 ms.
- **Interdits** : parallax agressif, compteurs animés, carrousels automatiques, confettis,
  curseur personnalisé.
- `prefers-reduced-motion: reduce` → rideau supprimé, transitions à 0,01 ms, tout visible.

## 7. Ton éditorial

Poétique et sobre, jamais commercial. On écrit « Un château pour rêver, un domaine pour
se ressourcer » (leur signature — à conserver), pas « Réservez vite ! ». Vouvoiement,
phrases courtes, vocabulaire sensoriel (lumière, pierre, brume, silence). Les CTA sont
des invitations : « Demander une disponibilité », « Composer votre séjour », « Écrivez-nous ».

Le bandeau défilant puise dans ce même vocabulaire — **des sensations, pas des arguments** :
« Pierre & lumière · Feux de bois · Silence du parc · Via Fluvia · Table d'hôtes ·
Nuits sous les tourelles ».
