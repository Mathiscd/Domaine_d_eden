# -*- coding: utf-8 -*-
"""Redessine le logo du Domaine d'Éden en vectoriel et produit ses déclinaisons.

Le fichier fourni par le client (``photos-sources/logo-domaine-eden.png``) est un
PNG de 619 px : un château au trait blanc sur un aplat vert texturé. Le trait y
fait 6,3 px de large, ce qui donne des jonctions empâtées, des créneaux d'épaisseur
inégale et des bords rongés par le JPEG d'origine — inutilisable en favicon, et
flou dès qu'on l'agrandit.

Plutôt que de vectoriser automatiquement ces bavures, la géométrie a été **relevée
au pixel** sur le masque du PNG (axe de symétrie, pentes, rayons, entraxes des
créneaux) puis reconstruite ici : symétrie parfaite autour de x = 179, graisse de
trait constante, créneaux régulièrement espacés. L'écart au dessin d'origine reste
sous 2 px sur une marque large de 359 — invisible, mais tout est net à n'importe
quelle taille.

Sorties (toutes régénérables, aucune n'est à retoucher à la main) :

    site/assets/img/logo-eden.svg   la marque complète et autonome, en ``currentColor``
    tools/extrait-logo.html         le bloc <symbol> à recopier en tête des pages
    site/favicon.svg                tuile claire + marque au trait, réglée pour l'onglet
    site/favicon.ico                la même, rendue pour 16, 32 et 48 px
    site/apple-touch-icon.png       180 px
    site/assets/img/icon-192.png    manifeste web
    site/assets/img/icon-512.png    manifeste web
    site/assets/img/icon-maskable-512.png   idem, marge élargie (zone sûre Android)

Toutes les icônes portent le même dessin au trait, vert sur tuile claire. Sous 48 px
le trait passe sous le demi-pixel et le château s'adoucit : la compensation optique
figée taille par taille limite la casse, mais l'onglet reste doux — c'est un arbitrage
en faveur de la cohérence de marque, arrêté avec le client.

Usage :

    python tools/generer-logo.py              # écrit les fichiers
    python tools/generer-logo.py --comparer   # + superpose au PNG source (contrôle)

Dépendances : Pillow, playwright (Chromium sert de rasteriseur SVG).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SITE = RACINE / "site"
IMG = SITE / "assets" / "img"
SOURCE = RACINE / "photos-sources" / "logo-domaine-eden.png"

# ---------------------------------------------------------------------------
# Repères relevés sur le PNG source (coordonnées en pixels de ce PNG, marque
# recadrée sur son encre : x 0→358, y 0→290).
# ---------------------------------------------------------------------------

AX = 179.0   # axe de symétrie de la marque
TX = 54.4    # axe de la tour gauche
SW = 6.3     # graisse du trait, mesurée à la transformée de distance

VERT = "#74963D"      # le vert de marque du client (charte)
VERT_TXT = "#4F6B26"  # le vert assombri, encre sur fond clair (AA 5,8:1)
IVOIRE = "#FDFDFB"


# ---------------------------------------------------------------------------
# Mini-constructeur de chemins : les commandes restent des tuples tant qu'on n'a
# pas fini, pour que le miroir soit un simple calcul sur les x.
# ---------------------------------------------------------------------------

def M(x, y): return ("M", x, y)
def L(x, y): return ("L", x, y)
def C(x1, y1, x2, y2, x, y): return ("C", x1, y1, x2, y2, x, y)
def Q(x1, y1, x, y): return ("Q", x1, y1, x, y)
def A(rx, ry, rot, laf, sf, x, y): return ("A", rx, ry, rot, laf, sf, x, y)
def Z(): return ("Z",)


def _n(v: float) -> str:
    """Nombre compact : pas de zéro final ni de « .0 » inutile."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def to_d(cmds) -> str:
    bouts = []
    for c in cmds:
        op, args = c[0], c[1:]
        if op == "A":
            rx, ry, rot, laf, sf, x, y = args
            bouts.append(f"A{_n(rx)} {_n(ry)} {_n(rot)} {int(laf)} {int(sf)} {_n(x)} {_n(y)}")
        elif op == "Z":
            bouts.append("Z")
        else:
            bouts.append(op + " ".join(_n(a) for a in args))
    return "".join(bouts)


def miroir(cmds, axe=AX):
    """Symétrique d'un chemin. Sur un arc, le sens de balayage s'inverse."""
    out = []
    for c in cmds:
        op, args = c[0], list(c[1:])
        if op == "A":
            args[4] = 1 - args[4]          # sweep-flag
            args[5] = 2 * axe - args[5]    # x d'arrivée
        elif op != "Z":
            for i in range(0, len(args), 2):
                args[i] = 2 * axe - args[i]
        out.append((op, *args))
    return out


def rect(x, y, w, h):
    return [M(x, y), L(x + w, y), L(x + w, y + h), L(x, y + h), Z()]


def fente(cx, largeur, y_haut_arc, y_bas):
    """Meurtrière : rectangle blanc à sommet en plein cintre."""
    r = largeur / 2
    return [M(cx - r, y_bas), L(cx - r, y_haut_arc + r),
            A(r, r, 0, 0, 1, cx + r, y_haut_arc + r),
            L(cx + r, y_bas), Z()]


# ---------------------------------------------------------------------------
# La tour gauche
# ---------------------------------------------------------------------------

# Couronne : les deux arcs bombent vers le haut (la tour est vue en contre-plongée).
CR_HAUT_G, CR_HAUT_D = 6.2, 102.6      # angles supérieurs de la couronne
CR_BAS_Y = 154.0                        # naissance des épaules
ARC_HAUT_CTRL = 109.1                   # contrôle de l'arc supérieur (sommet à 114,8)
ARC_BAS_CTRL = 142.4                    # contrôle de l'arc inférieur (sommet à 148,2)


def _y_arc(x, y_bord, y_ctrl):
    """Ordonnée d'un des deux arcs de couronne à l'abscisse x."""
    t = (x - CR_HAUT_G) / (CR_HAUT_D - CR_HAUT_G)
    return y_bord - 2 * (y_bord - y_ctrl) * t * (1 - t)


TOUR_CONTOUR = [
    M(CR_HAUT_G, 120.5),
    L(CR_HAUT_G, CR_BAS_Y),
    L(16.4, 170),                          # épaule : la couronne déborde du fût
    C(15.2, 205, 12.6, 245, 9, 273),       # fût légèrement fuyant
    L(23, 284.5),                          # socle qui se resserre
    Q(TX, 290, 85.8, 284.5),
    L(99.8, 273),
    C(96.2, 245, 93.6, 205, 92.4, 170),
    L(CR_HAUT_D, CR_BAS_Y),
    L(CR_HAUT_D, 120.5),
    Q(TX, ARC_HAUT_CTRL, CR_HAUT_G, 120.5),
    Z(),
]

TOUR_ARC_BAS = [M(CR_HAUT_G, CR_BAS_Y), Q(TX, ARC_BAS_CTRL, CR_HAUT_D, CR_BAS_Y)]
TOUR_ARC_SOCLE = [M(11.1, 255), Q(TX, 264, 97.7, 255)]

TOUR_TOIT = [
    M(CR_HAUT_G, 120.5),
    C(7.5, 117, 18, 105, 20.6, 98.2),
    L(TX, 7.9),                            # pointe : jonction en onglet
    L(88.2, 98.2),
    C(90.8, 105, 101.3, 117, CR_HAUT_D, 120.5),
]

# Merlons : trois dents sous l'arc supérieur, à entraxe constant.
MERLONS = [[M(x, _y_arc(x, 120.5, ARC_HAUT_CTRL)), L(x, 130)]
           for x in (TX - 32.9, TX, TX + 32.9)]

# Corbeaux : cinq consoles sous l'arc inférieur, même longueur pour toutes.
CORBEAUX = [[M(x, _y_arc(x, CR_BAS_Y, ARC_BAS_CTRL)), L(x, _y_arc(x, CR_BAS_Y, ARC_BAS_CTRL) + 12)]
            for x in (TX - 28.4, TX - 14.2, TX, TX + 14.2, TX + 28.4)]

TOUR_FENTE = fente(TX, 14, 194.4, 224.5)


# ---------------------------------------------------------------------------
# Le corps central
# ---------------------------------------------------------------------------

FAITAGE = [M(130, 55.2), L(130, 63.5), L(228, 63.5), L(228, 55.2)]   # + ses deux épis
RAMPANT = [M(130, 63.5), L(95.9, 116.5)]                              # disparaît derrière la tour
CORNICHE = [M(93.5, 167), L(148.5, 167)]
SOL = [M(100, 272), L(258, 272)]

LUCARNE_FLECHE = [M(152.5, 146), L(AX, 94.5), L(205.5, 146)]
LUCARNE_EPI = [M(AX, 90.5), L(AX, 99)]
LUCARNE_FLANC = [M(152.5, 146), L(144.5, 146), L(144.5, 152), L(148.5, 164), L(148.5, 272)]

PORTE = [
    M(162.5, 272), L(162.5, 244),
    C(162.5, 236, 168, 226.5, AX, 226.5),
    C(190, 226.5, 195.5, 236, 195.5, 244),
    L(195.5, 272),
]

LUCARNE_FENTE_HAUTE = fente(AX, 9, 134, 155.5)
LUCARNE_FENTE_BASSE = fente(AX, 13, 179, 207.5)

# Croisée à quatre carreaux : la rangée basse est plus haute que la rangée haute,
# comme sur le dessin du client.
CROISEE = [r for x in (110.25, 124.75)
           for r in (rect(x, 189.5, 9.5, 11), rect(x, 204.5, 9.5, 17))]


def marque():
    """Chemins de la marque au trait : (tracés, aplats)."""
    traits = []
    for p in [TOUR_CONTOUR, TOUR_ARC_BAS, TOUR_ARC_SOCLE, TOUR_TOIT] + MERLONS + CORBEAUX:
        traits += [p, miroir(p)]
    traits += [FAITAGE, RAMPANT, miroir(RAMPANT), CORNICHE, miroir(CORNICHE), SOL,
               LUCARNE_FLECHE, LUCARNE_EPI, LUCARNE_FLANC, miroir(LUCARNE_FLANC), PORTE]

    aplats = [TOUR_FENTE, miroir(TOUR_FENTE), LUCARNE_FENTE_HAUTE, LUCARNE_FENTE_BASSE]
    aplats += CROISEE + [miroir(r) for r in CROISEE]
    return traits, aplats


# ---------------------------------------------------------------------------
# Écriture du SVG
# ---------------------------------------------------------------------------

def corps_svg(couleur="currentColor", graisse=SW, indent="  ", longueur=False):
    """``longueur`` ajoute pathLength=\"1\" : toutes les lignes se tracent alors à
    la même vitesse, quelle que soit leur longueur (animation du rideau)."""
    pl = ' pathLength="1"' if longueur else ""
    traits, aplats = marque()
    gr = graisse if isinstance(graisse, str) else _n(graisse)
    lignes = [f'{indent}<g fill="none" stroke="{couleur}" stroke-width="{gr}"'
              f' stroke-linecap="round" stroke-linejoin="miter" stroke-miterlimit="8">']
    lignes += [f'{indent}  <path{pl} d="{to_d(p)}"/>' for p in traits]
    lignes.append(f"{indent}</g>")
    lignes.append(f'{indent}<g fill="{couleur}" stroke="none">')
    lignes += [f'{indent}  <path d="{to_d(p)}"/>' for p in aplats]
    lignes.append(f"{indent}</g>")
    return "\n".join(lignes)


def svg_marque(view_box):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s" role="img"\n'
        '     aria-label="Domaine d’Éden — Château les Tourelles">\n'
        "%s\n</svg>\n" % (view_box, corps_svg())
    )


def extrait_symbole(view_box):
    """Bloc à recopier tel quel en tête de <body> des pages.

    Les pages n'ont pas de build : elles portent donc la marque une fois chacune,
    en <symbol>, et l'appellent ensuite par <use> — en-tête, pied de page et
    rideau d'ouverture partagent ainsi la même définition. Un <use> externe
    (href vers un fichier .svg) n'est pas implémenté par les navigateurs, d'où
    la recopie. La graisse passe par une variable CSS : réduite à 38 px de haut
    dans l'en-tête, la marque a besoin d'un trait plus épais pour ne pas virer au
    gris — c'est la feuille de style qui règle ``--eden-trait`` cas par cas."""
    return (
        "<!-- Marque du domaine — généré par tools/generer-logo.py, ne pas retoucher à la main.\n"
        "     Appelée par <use href=\"#eden-marque\"> dans l'en-tête, le pied de page et le rideau. -->\n"
        f'<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" aria-hidden="true" focusable="false" style="position:absolute">\n'
        f'  <symbol id="eden-marque" viewBox="{view_box}">\n'
        f"{corps_svg(indent='    ', graisse='var(--eden-trait, ' + _n(SW) + ')', longueur=True)}\n"
        "  </symbol>\n</svg>\n"
    )


# ---------------------------------------------------------------------------
# Rastérisation : Chromium sert à la fois de rasteriseur et de règle (getBBox
# avec le trait, que seul un moteur SVG sait calculer honnêtement).
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

    def boite(self, svg: str, vue, echelle=4):
        """Boîte englobante réelle, onglets compris : on rastérise et on mesure
        l'encre. ``getBBox`` ignore le trait sur un groupe, et c'est justement le
        trait — et la pointe d'onglet des flèches — qui déborde ici."""
        import numpy as np
        from PIL import Image

        x0, y0, vw, vh = vue
        w, h = int(vw * echelle), int(vh * echelle)
        self.page.set_viewport_size({"width": w, "height": h})
        self.page.set_content(
            f"<body style='margin:0'><div style='width:{w}px;height:{h}px;color:#000'>"
            f"{svg}</div></body>"
        )
        tampon = RACINE / ".logo-boite.png"
        self.page.query_selector("div").screenshot(path=str(tampon), omit_background=True)
        a = np.asarray(Image.open(tampon).convert("RGBA"))[..., 3] > 8
        tampon.unlink(missing_ok=True)
        ys, xs = np.nonzero(a)
        return (x0 + xs.min() / echelle, y0 + ys.min() / echelle,
                (xs.max() - xs.min() + 1) / echelle, (ys.max() - ys.min() + 1) / echelle)

    def png(self, svg: str, chemin: Path, taille: int, muet=False):
        chemin.parent.mkdir(parents=True, exist_ok=True)
        self.page.set_viewport_size({"width": taille, "height": taille})
        self.page.set_content(
            f"<body style='margin:0'>"
            f"<div style='width:{taille}px;height:{taille}px'>{svg}</div></body>"
        )
        self.page.query_selector("div").screenshot(path=str(chemin))
        if not muet:
            print(f"  {chemin.relative_to(RACINE)}  {taille}×{taille}")


# ---------------------------------------------------------------------------

def _cadrer(cote, boite, marge):
    """Transform qui inscrit ``boite`` dans une tuile carrée, marge comprise."""
    bx, by, bw, bh = boite
    utile = cote * (1 - 2 * marge)
    k = min(utile / bw, utile / bh)
    return (f"translate({_n((cote - bw * k) / 2 - bx * k)} "
            f"{_n((cote - bh * k) / 2 - by * k)}) scale({_n(k)})")


def tuile(contenu, cote=64, fond=IVOIRE):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {cote} {cote}" role="img"\n'
        f'     aria-label="Domaine d’Éden">\n'
        f'  <rect width="{cote}" height="{cote}" fill="{fond}"/>\n'
        f"{contenu}\n</svg>\n"
    )


def svg_tuile(boite, cote=64, marge=0.09, fond=IVOIRE, encre=VERT_TXT, graisse=SW):
    """La marque au trait sur tuile claire — toutes les icônes du site.

    ``graisse`` monte à mesure que la tuile rétrécit : à 16 px le trait nominal ne
    pèse plus qu'un cinquième de pixel et le château s'efface. C'est la même
    compensation optique que ``--eden-trait`` dans la feuille de style, mais figée
    ici, un PNG ne connaissant qu'une taille."""
    return tuile(
        f'  <g transform="{_cadrer(cote, boite, marge)}">\n'
        f"{corps_svg(encre, graisse, indent='    ')}\n"
        f"  </g>", cote, fond)


def ecrire(chemin: Path, contenu: str):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(contenu, encoding="utf-8")
    print(f"  {chemin.relative_to(RACINE)}  {len(contenu.encode()) / 1024:.1f} ko")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--comparer", action="store_true",
                    help="superpose le rendu au PNG source et publie les écarts")
    args = ap.parse_args()

    r = Rendu()
    try:
        # 1. La marque, dans une boîte qui épouse exactement son encre.
        VUE = (-20, -20, 400, 330)
        provisoire = svg_marque("%s %s %s %s" % VUE)
        bx, by, bw, bh = r.boite(provisoire, VUE)
        vb = "%s %s %s %s" % (_n(math.floor(bx * 10) / 10), _n(math.floor(by * 10) / 10),
                              _n(math.ceil(bw * 10) / 10), _n(math.ceil(bh * 10) / 10))
        print("Boîte de la marque :", vb)
        print("SVG :")
        ecrire(IMG / "logo-eden.svg", svg_marque(vb))
        ecrire(RACINE / "tools" / "extrait-logo.html", extrait_symbole(vb))

        # 2. L'onglet. Le SVG sert les navigateurs modernes, l'ICO tout le reste ;
        #    chaque taille est rendue pour elle-même, jamais réduite depuis une
        #    plus grande — un trait fin rééchantillonné vire au gris.
        boite = (bx, by, bw, bh)
        ecrire(SITE / "favicon.svg", svg_tuile(boite, marge=0.05, graisse=SW * 2))

        print("PNG :")
        from PIL import Image
        tampon = RACINE / ".logo-tmp.png"
        frames = []
        for taille, marge, graisse in ((16, 0.04, SW * 2.5), (32, 0.05, SW * 1.9),
                                       (48, 0.06, SW * 1.5)):
            r.png(svg_tuile(boite, marge=marge, graisse=graisse), tampon, taille, muet=True)
            frames.append(Image.open(tampon).convert("RGBA").copy())
        frames[-1].save(SITE / "favicon.ico", format="ICO",
                        sizes=[(16, 16), (32, 32), (48, 48)], append_images=frames[:2])
        tampon.unlink(missing_ok=True)
        print(f"  {(SITE / 'favicon.ico').relative_to(RACINE)}  16 + 32 + 48")

        # 3. Les grandes icônes : le trait a la place de s'exprimer, graisse
        #    nominale. Le gabarit « maskable » recule la marge pour survivre au
        #    rognage circulaire d'Android.
        r.png(svg_tuile(boite), SITE / "apple-touch-icon.png", 180)
        r.png(svg_tuile(boite), IMG / "icon-192.png", 192)
        r.png(svg_tuile(boite), IMG / "icon-512.png", 512)
        r.png(svg_tuile(boite, marge=0.235), IMG / "icon-maskable-512.png", 512)

        if args.comparer:
            comparer(r, svg_marque(vb), vb)
    finally:
        r.fermer()


def comparer(r: Rendu, svg: str, vb: str):
    """Superpose le rendu au masque du PNG source et chiffre l'écart."""
    import numpy as np
    from PIL import Image

    if not SOURCE.exists():
        print(f"\n(pas de source à comparer : {SOURCE})")
        return

    src = np.asarray(Image.open(SOURCE).convert("RGB")).astype(np.float32)[:-1, :-1]
    mn = src.min(axis=2)
    fond = float(np.median(np.concatenate([mn[:20].ravel(), mn[-20:].ravel()])))
    masque = np.clip((mn - fond - 6) / (250 - fond - 6), 0, 1) > 0.5
    ys, xs = np.nonzero(masque)
    masque = masque[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

    h, w = masque.shape
    x0, y0, vw, vh = (float(v) for v in vb.split())
    # on rend la marque exactement au gabarit du relevé (0→358 × 0→290)
    page = (f"<body style='margin:0;background:#000'>"
            f"<div style='width:{w}px;height:{h}px;overflow:hidden;position:relative'>"
            f"<div style='position:absolute;left:{x0}px;top:{y0}px;"
            f"width:{vw}px;height:{vh}px;color:#fff'>{svg}</div></div></body>")
    r.page.set_viewport_size({"width": w, "height": h})
    r.page.set_content(page)
    tampon = RACINE / ".logo-cmp.png"
    r.page.query_selector("div").screenshot(path=str(tampon))
    rendu = np.asarray(Image.open(tampon).convert("L")).astype(np.float32) / 255 > 0.5

    inter = (masque & rendu).sum()
    union = (masque | rendu).sum()
    print(f"\nSuperposition au dessin du client : IoU {inter / union:.3f}"
          f"  (encre source {masque.sum()}, encre rendue {rendu.sum()})")

    diff = np.zeros((h, w, 3), np.uint8)
    diff[..., 0] = np.where(masque & ~rendu, 255, 0)     # rouge : perdu
    diff[..., 1] = np.where(masque & rendu, 190, 0)      # vert : commun
    diff[..., 2] = np.where(rendu & ~masque, 255, 0)     # bleu : ajouté
    Image.fromarray(diff).save(RACINE / ".logo-diff.png")
    print(f"  écarts : {(RACINE / '.logo-diff.png').name}"
          f"  (rouge = manquant, bleu = en trop)")
    tampon.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
