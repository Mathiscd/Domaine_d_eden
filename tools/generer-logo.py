# -*- coding: utf-8 -*-
"""Vectorise le logo du Domaine d'Éden et produit toutes ses déclinaisons.

Le fichier fourni par le client (``photos-sources/logo-domaine-eden.png``) est un
PNG de 638 px composé de trois blocs : le lettrage « CHÂTEAU LES TOURELLES » en
haut, le dessin — château, tourelles, arbre — au centre, et « DOMAINE D'EDEN » en
bas. **Seul le dessin est repris ici** : le lettrage du PNG est bitmap et illisible
sous 200 px, alors que les pages composent déjà ces deux lignes en Cormorant et en
Jost, à la bonne graisse et à n'importe quelle taille. Le script isole donc la
bande centrale (voir ``bandes()``) et la vectorise.

Le dessin est bichrome et le reste :

    l'encre    #404041   le trait du château, les volets, les épis de faîtage
    le vert    #75983D   l'arbre, les toits des tourelles et le toit central

Chaque pixel est décomposé en ``blanc + a_vert·(vert−blanc) + a_encre·(encre−blanc)``
(moindres carrés, ``couvertures()``), ce qui sépare proprement les deux encres
jusque dans les pixels d'anti-crénelage. Les deux masques obtenus sont agrandis,
lissés, puis suivis par potrace. Le trait du client est volontairement irrégulier
— c'est un dessin à la main — et ce grain est conservé : c'est ce qui distingue
cette marque d'un pictogramme géométrique.

Le trait fait 2 px de large là où il est le plus fin, soit un demi-pixel une fois
la marque ramenée à 26 px de haut dans l'en-tête : le château y virerait au gris.
``--eden-trait`` le compense en cernant les aplats d'un liseré de la même couleur
— ``vector-effect="non-scaling-stroke"`` fait que sa valeur s'exprime en pixels
d'écran, indépendamment de la taille de rendu. Un moteur qui ignorerait cet
attribut interpréterait 0,9 comme 0,9 unité sur 1024 : invisible, jamais un pâté.

Sorties (toutes régénérables, aucune n'est à retoucher à la main) :

    site/assets/img/logo-eden.svg   la marque autonome, bichrome, à livrer au client
    tools/extrait-logo.html         le bloc <symbol> à recopier en tête des pages
    site/favicon.svg                tuile claire + marque, réglée pour l'onglet
    site/favicon.ico                la même, rendue pour 16, 32 et 48 px
    site/apple-touch-icon.png       180 px
    site/assets/img/icon-192.png    manifeste web
    site/assets/img/icon-512.png    manifeste web
    site/assets/img/icon-maskable-512.png   idem, marge élargie (zone sûre Android)

Usage :

    python tools/generer-logo.py              # écrit les fichiers
    python tools/generer-logo.py --comparer   # + superpose au PNG source (contrôle)
    python tools/generer-logo.py --planche    # + planche d'essai multi-tailles

Dépendances : Pillow, numpy, OpenCV, pypotrace, playwright (Chromium rastérise).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
import potrace
from PIL import Image

RACINE = Path(__file__).resolve().parent.parent
SITE = RACINE / "site"
IMG = SITE / "assets" / "img"
SOURCE = RACINE / "photos-sources" / "logo-domaine-eden.png"

# — Les trois encres du fichier client, relevées au recensement des couleurs —
BLANC = np.array([255.0, 255.0, 255.0])
VERT = np.array([117.0, 152.0, 61.0])
ENCRE = np.array([64.0, 64.0, 65.0])

# — Réglages du suivi de contour —
ECH = 3          # agrandissement avant seuillage : lisse l'escalier des pixels
MARGE = 8        # bordure vide ajoutée avant l'agrandissement (les morphologies
                 # de cv2 remplissent le bord si la forme le touche)
LARGEUR = 1024   # largeur du viewBox produit. Assez grande pour que les
                 # coordonnées entières gardent le trait le plus fin (2 px source,
                 # soit 5 unités) ; assez petite pour que le `d` reste court.

# Lissage propre à chaque encre. Le vert est un aplat : on peut le lisser fort.
# L'encre est un trait de 2 px par endroits : le flou seul l'amincirait jusqu'à
# le rompre, d'où un seuil abaissé à 0,37 qui lui rend ce que la gaussienne lui
# prend. Le couple (flou fort, seuil bas) est ce qui allège le tracé sans user le
# grain du trait : à flou 2,2 / seuil 0,42, le même dessin pèse 1,3 ko de plus
# pour des dentelures que plus personne ne voit passé 300 px.
ENCRE_FLOU, ENCRE_SEUIL, ENCRE_OUVRE = 3.0, 0.37, 3
VERT_FLOU, VERT_SEUIL, VERT_OUVRE = 3.5, 0.50, 7
# alphamax au maximum : potrace convertit alors le plus de coins possible en
# courbes, ce qui divise le nombre de segments d'un contour aussi irrégulier.
TURDSIZE, ALPHAMAX, OPTTOLERANCE = 40, 1.33, 2.5

# — Couleurs de rendu —
IVOIRE = "#FAFAF8"
ENCRE_HEX = "#2C3226"   # l'encre du dessin, ramenée dans la charte du site
VERT_HEX = "#74963D"    # le vert de marque de la charte


# ---------------------------------------------------------------------------
# 1. Lecture du PNG client : séparer les deux encres, écarter le lettrage
# ---------------------------------------------------------------------------

def couvertures(rgb: np.ndarray):
    """Décompose l'image en deux cartes de couverture, une par encre.

    Chaque pixel est supposé être un mélange sur blanc d'au plus deux teintes :
    ``p = blanc + a_v·(vert − blanc) + a_e·(encre − blanc)``. Le système est
    surdéterminé (trois canaux, deux inconnues) donc résolu aux moindres carrés :
    un pixel d'anti-crénelage à mi-chemin du vert rend a_v ≈ 0,5 et a_e ≈ 0, et
    le seuillage qui suit tombe exactement sur le bord optique de la forme.
    """
    base = np.stack([VERT - BLANC, ENCRE - BLANC], axis=1)
    a = (np.linalg.pinv(base) @ (rgb.reshape(-1, 3) - BLANC).T).T
    a = a.reshape(rgb.shape[0], rgb.shape[1], 2)
    return np.clip(a[..., 0], 0, 1), np.clip(a[..., 1], 0, 1)


def bandes(masque: np.ndarray, creux: int = 12):
    """Bandes horizontales d'encre, séparées par au moins ``creux`` lignes vides."""
    lignes = masque.sum(axis=1) > 2
    out, debut = [], None
    for y, plein in enumerate(lignes):
        if plein and debut is None:
            debut = y
        elif not plein and debut is not None:
            out.append((debut, y - 1))
            debut = None
    if debut is not None:
        out.append((debut, len(lignes) - 1))
    fusion = []
    for b in out:
        if fusion and b[0] - fusion[-1][1] < creux:
            fusion[-1] = (fusion[-1][0], b[1])
        else:
            fusion.append(b)
    return fusion


def recadrer(av: np.ndarray, ae: np.ndarray, marge: int = 2):
    """Retient la seule bande qui porte du vert : le dessin, sans le lettrage.

    Les deux lignes de texte du PNG sont en encre pure et séparées du dessin par
    une trentaine de lignes blanches ; l'arbre et les toits, eux, sont les seuls
    éléments verts de l'image. Chercher la bande verte plutôt que coder des
    coordonnées en dur permet de refaire tourner le script si le client renvoie
    son logo recadré ou à une autre échelle.
    """
    plein = (av > 0.5) | (ae > 0.5)
    verte = av > 0.5
    ys, _ = np.nonzero(verte)
    for haut, bas in bandes(plein, creux=12):
        if haut <= ys.min() and ys.max() <= bas:
            break
    else:                                     # pragma: no cover — filet de sécurité
        raise SystemExit("Le dessin et le lettrage ne se séparent pas : source inattendue.")
    xs = np.nonzero(plein[haut:bas + 1].any(axis=0))[0]
    y0, y1 = max(0, haut - marge), min(plein.shape[0], bas + 1 + marge)
    x0, x1 = max(0, xs.min() - marge), min(plein.shape[1], xs.max() + 1 + marge)
    return av[y0:y1, x0:x1], ae[y0:y1, x0:x1]


# ---------------------------------------------------------------------------
# 2. Suivi de contour
# ---------------------------------------------------------------------------

def masque(couv: np.ndarray, flou: float, seuil: float, ouvre: int) -> np.ndarray:
    """Carte de couverture → bitmap binaire, agrandi et débarrassé de sa poussière.

    L'agrandissement précède le seuillage : interpoler la couverture puis couper
    à mi-hauteur place le contour au sous-pixel, là où seuiller d'abord figerait
    l'escalier de la grille source. L'ouverture-fermeture qui suit retire les
    grains isolés du fichier client sans entamer le grain du trait lui-même.
    """
    h, w = couv.shape
    g = cv2.copyMakeBorder(couv.astype(np.float32), MARGE, MARGE, MARGE, MARGE,
                           cv2.BORDER_CONSTANT, value=0)
    g = cv2.resize(g, ((w + 2 * MARGE) * ECH, (h + 2 * MARGE) * ECH),
                   interpolation=cv2.INTER_CUBIC)
    if flou:
        g = cv2.GaussianBlur(g, (0, 0), flou)
    m = (g > seuil).astype(np.uint8)
    if ouvre:
        noyau = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ouvre, ouvre))
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, noyau)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, noyau)
    return m


def _nombre(v: float) -> str:
    return str(int(round(v)))


def _commande(lettre: str, valeurs) -> str:
    """Sérialise une commande en économisant les séparateurs : « -3 » se colle."""
    s = lettre
    for i, v in enumerate(valeurs):
        t = _nombre(v)
        if i and not t.startswith("-"):
            s += " "
        s += t
    return s


def to_d(courbes, k: float, dec: float) -> str:
    """Courbes potrace → attribut ``d`` en commandes relatives et coordonnées entières.

    Le curseur suivi ici est la position **réellement écrite**, arrondis compris :
    sans cela, chaque arrondi se reporterait sur le segment suivant et le tracé
    dériverait de plusieurs unités d'un bout à l'autre du contour.
    """
    d, cx, cy = [], 0.0, 0.0
    for courbe in courbes:
        px, py = courbe.start_point.x * k - dec, courbe.start_point.y * k - dec
        d.append(_commande("m", (px - cx, py - cy)))
        cx, cy = cx + round(px - cx), cy + round(py - cy)
        for seg in courbe:
            if seg.is_corner:
                for p in (seg.c, seg.end_point):
                    px, py = p.x * k - dec, p.y * k - dec
                    if abs(px - cx) < 0.5 and abs(py - cy) < 0.5:
                        continue
                    d.append(_commande("l", (px - cx, py - cy)))
                    cx, cy = cx + round(px - cx), cy + round(py - cy)
            else:
                v = []
                for p in (seg.c1, seg.c2, seg.end_point):
                    v += [p.x * k - dec - cx, p.y * k - dec - cy]
                d.append(_commande("c", v))
                cx, cy = cx + round(v[4]), cy + round(v[5])
        d.append("z")
    return "".join(d)


def suivre(bitmap: np.ndarray, k: float, dec: float) -> str:
    """potrace attend le fond à 1 : d'où l'inversion. Tous les contours d'une même
    encre partent dans un seul ``d`` — potrace oriente les trous en sens inverse,
    la règle de remplissage ``nonzero`` les creuse donc toute seule."""
    courbes = potrace.Bitmap(~bitmap.astype(bool)).trace(
        turdsize=TURDSIZE, turnpolicy=potrace.POTRACE_TURNPOLICY_MAJORITY,
        alphamax=ALPHAMAX, opticurve=True, opttolerance=OPTTOLERANCE)
    return to_d(courbes, k, dec)


def vectoriser():
    """→ (d de l'encre, d du vert, largeur, hauteur) du viewBox."""
    rgb = np.asarray(Image.open(SOURCE).convert("RGB")).astype(np.float32)
    av, ae = recadrer(*couvertures(rgb))
    h, w = av.shape
    k = LARGEUR / (w * ECH)
    dec = MARGE * ECH * k
    d_encre = suivre(masque(ae, ENCRE_FLOU, ENCRE_SEUIL, ENCRE_OUVRE), k, dec)
    d_vert = suivre(masque(av, VERT_FLOU, VERT_SEUIL, VERT_OUVRE), k, dec)
    return d_encre, d_vert, LARGEUR, int(round(h * ECH * k))


# ---------------------------------------------------------------------------
# 3. Assemblage SVG
# ---------------------------------------------------------------------------

def corps(d_encre, d_vert, encre, feuille, trait=None, indent="  "):
    """Les deux aplats, l'encre puis le vert — l'arbre passe devant le château.

    ``trait`` cerne chaque aplat d'un liseré de sa propre couleur : c'est la
    compensation optique des petites tailles, le trait du dessin tombant sous le
    pixel dès que la marque descend sous 40 px. Le liseré resserre du même geste
    les fenêtres, qui sinon se boucheraient à l'anti-crénelage."""
    if trait is None:
        gabarit = '{i}<path fill="{c}" d="{d}"/>'
    else:
        gabarit = ('{i}<path fill="{c}" stroke="{c}" stroke-width="' + trait + '"'
                   ' stroke-linejoin="round" vector-effect="non-scaling-stroke" d="{d}"/>')
    return "\n".join(gabarit.format(i=indent, c=c, d=d)
                     for c, d in ((encre, d_encre), (feuille, d_vert)))


def svg_marque(d_encre, d_vert, w, h):
    """La marque autonome, à livrer au client : couleurs réelles, aucun réglage."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img"\n'
        f'     aria-label="Domaine d’Éden — Château les Tourelles">\n'
        f"{corps(d_encre, d_vert, ENCRE_HEX, VERT_HEX)}\n</svg>\n"
    )


def extrait_symbole(d_encre, d_vert, w, h):
    """Bloc à recopier tel quel en tête de <body> des pages.

    Les pages n'ont pas de build : chacune porte donc la marque une seule fois,
    en <symbol>, et l'appelle ensuite par <use> — en-tête, pied de page et rideau
    partagent la même définition. Un <use> vers un .svg externe n'est pas
    implémenté par les navigateurs, d'où la recopie.

    Deux variables la règlent, toutes deux héritées jusque dans l'arbre du <use> :
    ``--eden-feuille`` donne sa couleur au feuillage (à défaut il suit le texte,
    et la marque est monochrome), ``--eden-trait`` l'épaissit aux petites tailles."""
    return (
        "<!-- Marque du domaine — généré par tools/generer-logo.py, ne pas retoucher à la main.\n"
        "     Appelée par <use href=\"#eden-marque\"> dans l'en-tête, le pied de page et le rideau.\n"
        "     Réglages hérités : --eden-feuille (couleur de l'arbre et des toits),\n"
        "     --eden-trait (épaississement optique, en pixels d'écran). -->\n"
        '<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" aria-hidden="true" focusable="false" style="position:absolute">\n'
        f'  <symbol id="eden-marque" viewBox="0 0 {w} {h}">\n'
        f"{corps(d_encre, d_vert, 'currentColor', 'var(--eden-feuille, currentColor)', trait='var(--eden-trait, 0)', indent='    ')}\n"
        "  </symbol>\n</svg>\n"
    )


def svg_tuile(d_encre, d_vert, w, h, cote=64, marge=0.09, epaisseur=0.0, fond=IVOIRE):
    """La marque sur tuile claire — toutes les icônes du site.

    ``epaisseur`` s'exprime directement en pixels de la tuile finale : le liseré
    porte ``non-scaling-stroke``, sa graisse échappe donc à la mise à l'échelle du
    groupe. Elle monte à mesure que la tuile rétrécit — à 16 px, le trait nominal
    du dessin ne pèse plus qu'un vingtième de pixel."""
    utile = cote * (1 - 2 * marge)
    k = min(utile / w, utile / h)
    tx, ty = (cote - w * k) / 2, (cote - h * k) / 2
    trait = f"{epaisseur:.2f}" if epaisseur else None
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {cote} {cote}" role="img"\n'
        f'     aria-label="Domaine d’Éden">\n'
        f'  <rect width="{cote}" height="{cote}" fill="{fond}"/>\n'
        f'  <g transform="translate({tx:.2f} {ty:.2f}) scale({k:.4f})">\n'
        f"{corps(d_encre, d_vert, ENCRE_HEX, VERT_HEX, trait=trait, indent='    ')}\n"
        f"  </g>\n</svg>\n"
    )


# ---------------------------------------------------------------------------
# 4. Rastérisation (Chromium)
# ---------------------------------------------------------------------------

class Rendu:
    def __init__(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self.nav = self._pw.chromium.launch()
        self.page = self.nav.new_page()

    def fermer(self):
        self.nav.close()
        self._pw.stop()

    def png(self, svg: str, chemin: Path, taille: int, muet=False):
        chemin.parent.mkdir(parents=True, exist_ok=True)
        self.page.set_viewport_size({"width": taille, "height": taille})
        self.page.set_content(
            f"<body style='margin:0'>"
            f"<div style='width:{taille}px;height:{taille}px'>{svg}</div></body>")
        self.page.query_selector("div").screenshot(path=str(chemin))
        if not muet:
            print(f"  {chemin.relative_to(RACINE)}  {taille}×{taille}")


def ecrire(chemin: Path, contenu: str):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(contenu, encoding="utf-8")
    print(f"  {chemin.relative_to(RACINE)}  {len(contenu.encode()) / 1024:.1f} ko")


# ---------------------------------------------------------------------------

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--comparer", action="store_true",
                    help="superpose le rendu au dessin du client et chiffre l'écart")
    ap.add_argument("--planche", action="store_true",
                    help="publie une planche d'essai de la marque à toutes ses tailles")
    args = ap.parse_args()

    de, dv, w, h = vectoriser()
    print(f"Marque vectorisée : viewBox 0 0 {w} {h}"
          f"  (encre {len(de) / 1024:.1f} ko, vert {len(dv) / 1024:.1f} ko)")

    print("SVG :")
    ecrire(IMG / "logo-eden.svg", svg_marque(de, dv, w, h))
    ecrire(RACINE / "tools" / "extrait-logo.html", extrait_symbole(de, dv, w, h))

    # L'onglet. Le SVG sert les navigateurs modernes, l'ICO tout le reste ; chaque
    # taille est rendue pour elle-même, jamais réduite depuis une plus grande —
    # un trait fin rééchantillonné vire au gris.
    ecrire(SITE / "favicon.svg", svg_tuile(de, dv, w, h, marge=0.04, epaisseur=0.5))

    r = Rendu()
    try:
        print("PNG :")
        tampon = RACINE / ".logo-tmp.png"
        vues = []
        for taille, marge, ep in ((16, 0.02, 0.45), (32, 0.03, 0.45), (48, 0.04, 0.5)):
            r.png(svg_tuile(de, dv, w, h, marge=marge, epaisseur=ep), tampon, taille, muet=True)
            vues.append(Image.open(tampon).convert("RGBA").copy())
        vues[-1].save(SITE / "favicon.ico", format="ICO",
                      sizes=[(16, 16), (32, 32), (48, 48)], append_images=vues[:2])
        tampon.unlink(missing_ok=True)
        print(f"  {(SITE / 'favicon.ico').relative_to(RACINE)}  16 + 32 + 48")

        # Les grandes icônes : le trait a la place de s'exprimer, compensation
        # réduite. Le gabarit « maskable » recule la marge pour survivre au
        # rognage circulaire d'Android.
        for chemin, taille, marge, ep in ((SITE / "apple-touch-icon.png", 180, 0.09, 0.6),
                                          (IMG / "icon-192.png", 192, 0.09, 0.6),
                                          (IMG / "icon-512.png", 512, 0.09, 0.3),
                                          (IMG / "icon-maskable-512.png", 512, 0.235, 0.4)):
            r.png(svg_tuile(de, dv, w, h, marge=marge, epaisseur=ep), chemin, taille)

        if args.planche:
            planche(r, de, dv, w, h)
        if args.comparer:
            comparer(r, de, dv, w, h)
    finally:
        r.fermer()


def planche(r: Rendu, de, dv, w, h):
    """Planche de contrôle : la marque de 20 à 220 px, sur fond sombre et clair,
    avec plusieurs valeurs de ``--eden-trait``. C'est le seul juge du réglage."""
    def bloc(fond, encre, feuille):
        lignes = []
        for taille in (20, 26, 30, 44, 90, 220):
            cell = "".join(
                f"<figure style='margin:0;text-align:center'>"
                f"<figcaption style='font:9px sans-serif;color:{encre};opacity:.55'>{taille}px · {t}</figcaption>"
                f"<svg viewBox='0 0 {w} {h}' style='height:{taille}px;width:auto;overflow:visible;"
                f"color:{encre};--eden-feuille:{feuille};--eden-trait:{t}'>"
                f"{corps(de, dv, 'currentColor', 'var(--eden-feuille)', trait='var(--eden-trait)', indent='')}"
                f"</svg></figure>" for t in (0, 0.5, 0.9, 1.3))
            lignes.append(f"<div style='display:flex;gap:26px;align-items:flex-end;padding:9px 0'>{cell}</div>")
        return f"<div style='background:{fond};padding:14px'>" + "".join(lignes) + "</div>"

    html = ("<body style='margin:0'>"
            + bloc("#161B14", "#FDFDFB", "#9DBA6A")
            + bloc("#FAFAF8", ENCRE_HEX, VERT_HEX) + "</body>")
    r.page.set_viewport_size({"width": 900, "height": 900})
    r.page.set_content(html)
    r.page.screenshot(path=str(RACINE / ".logo-planche.png"), full_page=True)
    print(f"\nPlanche d'essai : .logo-planche.png")


def comparer(r: Rendu, de, dv, w, h):
    """Superpose le tracé au dessin du client et chiffre l'écart, encre par encre."""
    rgb = np.asarray(Image.open(SOURCE).convert("RGB")).astype(np.float32)
    av, ae = recadrer(*couvertures(rgb))
    sh, sw = av.shape

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
           f'style="width:{sw}px;height:{sh}px;display:block">'
           f'<path fill="#f00" d="{de}"/><path fill="#0f0" d="{dv}"/></svg>')
    r.page.set_viewport_size({"width": sw, "height": sh})
    r.page.set_content(f"<body style='margin:0;background:#000'>{svg}</body>")
    tampon = RACINE / ".logo-cmp.png"
    r.page.query_selector("svg").screenshot(path=str(tampon))
    rendu = np.asarray(Image.open(tampon).convert("RGB"))
    tampon.unlink(missing_ok=True)

    diff = np.zeros((sh, sw, 3), np.uint8)
    for nom, source, calque, canal in (("encre", ae > 0.5, rendu[..., 0] > 127, 0),
                                       ("vert ", av > 0.5, rendu[..., 1] > 127, 1)):
        inter, union = (source & calque).sum(), (source | calque).sum()
        print(f"  {nom} : IoU {inter / union:.3f}"
              f"  (source {source.sum()} px, rendu {calque.sum()} px)")
        diff[..., 0] |= np.where(source & ~calque, 255, 0).astype(np.uint8)
        diff[..., 2] |= np.where(calque & ~source, 255, 0).astype(np.uint8)
        diff[..., 1] |= np.where(source & calque, 150, 0).astype(np.uint8)
    print("\nSuperposition au dessin du client :" if False else "")
    Image.fromarray(diff).save(RACINE / ".logo-diff.png")
    print("  écarts : .logo-diff.png  (rouge = manquant, bleu = en trop, vert = commun)")


if __name__ == "__main__":
    sys.exit(main())
