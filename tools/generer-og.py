#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Produit les images de partage `og-<page>.jpg`, en 1200 × 630.

Pourquoi un fichier dédié plutôt que de réutiliser une variante existante :
aucune photo du site n'est en 1,91:1. Facebook, LinkedIn, WhatsApp, Slack,
Bluesky et les aperçus des assistants IA recadrent alors eux-mêmes, au centre,
sans savoir où est le sujet — le château y perd ses tourelles. 1200 × 630 est
le format que toutes ces plateformes attendent, et le plancher sous lequel
X/Twitter bascule de la grande carte à la vignette carrée.

Ces images ne passent PAS par la bissection SSIM de `generer-images.py`, et
c'est délibéré : elles ne sont jamais servies au visiteur, seulement aux robots
d'aperçu, qui les recompressent tous de leur côté. Chercher le dernier
pour-cent de poids ici n'aurait aucun effet sur les Core Web Vitals — la
qualité est fixée une fois pour toutes.

Le recadrage se fait au ratio, depuis `photos-sources/`, jamais depuis un JPEG
déjà compressé du site (même règle que `generer-images.py`). `ancrage` dit où
prendre la bande dans la hauteur de la source : 0 en haut, 1 en bas, 0,5 au
centre. Les vues du château sont ancrées un peu au-dessus du centre — sinon la
bande ne retient que la pelouse et coupe les toits.

    python tools/generer-og.py            # simulation
    python tools/generer-og.py --ecrire   # écrit les fichiers
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageFilter
except ImportError:
    sys.exit("Il manque Pillow : pip install pillow")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RACINE = Path(__file__).resolve().parent.parent
SOURCES = RACINE / "photos-sources"
SORTIE = RACINE / "site" / "assets" / "img"

LARGEUR, HAUTEUR = 1200, 630
QUALITE = 84

# page → (source, ancrage vertical). Les noms de source sont ceux de
# CORRESPONDANCE dans generer-images.py : on partage les mêmes originaux.
CARTES = {
    "og-accueil":     ("gdf-11.jpg", 0.06),  # la façade : la tourelle est tout en haut du cadre
    "og-chambres":    ("gdf-0.jpg",  0.50),  # la chambre : le lit est au centre
    "og-evenements":  ("gdf-8.jpg",  0.50),  # la salle à manger dressée
    "og-reservation": ("gdf-13.jpg", 0.45),  # la cour et ses roues de charrette
}


def recadrer(im: Image.Image, ancrage: float) -> Image.Image:
    """Découpe la plus grande bande en 1200:630 tenant DANS la source, puis la réduit.

    Le sens de la comparaison compte, et se trompe facilement : c'est la
    dimension la plus contraignante qui doit rester entière. Une source plus
    large que le ratio cible (paysage très allongé) garde toute sa hauteur et
    perd sur les côtés ; une source plus étroite — les 4:3 des Gîtes de France,
    c'est-à-dire toutes celles d'ici — garde toute sa largeur et perd en
    hauteur, ce que règle `ancrage`.

    Inverser ces deux cas fait demander à PIL une bande plus grande que
    l'image : `crop()` ne s'en plaint pas, il complète en noir. D'où des
    bandes noires sur les côtés plutôt qu'une erreur.
    """
    ratio = LARGEUR / HAUTEUR
    w, h = im.size

    if w / h >= ratio:          # source plus large que la cible : on rogne les côtés
        bande_h = h
        bande_w = round(h * ratio)
    else:                       # source plus étroite : on rogne en hauteur
        bande_w = w
        bande_h = round(w / ratio)

    gauche = round((w - bande_w) / 2)
    haut = round((h - bande_h) * ancrage)
    coupe = im.crop((gauche, haut, gauche + bande_w, haut + bande_h))
    assert coupe.size == (bande_w, bande_h) and bande_w <= w and bande_h <= h

    # Même accentuation que reechantillonner() dans generer-images.py : une
    # réduction est un passe-bas, l'unsharp discret rend le micro-contraste.
    reduit = coupe.resize((LARGEUR, HAUTEUR), Image.LANCZOS)
    return reduit.filter(ImageFilter.UnsharpMask(radius=0.6, percent=55, threshold=3))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ecrire", action="store_true",
                    help="écrit les fichiers (sans l'option : simulation)")
    args = ap.parse_args()

    for nom, (source, ancrage) in CARTES.items():
        chemin = SOURCES / source
        if not chemin.exists():
            print(f"  ABSENT : {chemin.relative_to(RACINE)}")
            continue

        with Image.open(chemin) as im:
            carte = recadrer(im.convert("RGB"), ancrage)

        cible = SORTIE / f"{nom}.jpg"
        if args.ecrire:
            carte.save(cible, "JPEG", quality=QUALITE, optimize=True,
                       progressive=True, subsampling=1)
            poids = cible.stat().st_size
            print(f"  {nom}.jpg  ← {source}  ancrage {ancrage}  {poids // 1024} Ko")
        else:
            print(f"  {nom}.jpg  ← {source}  ancrage {ancrage}  (simulation)")

    if not args.ecrire:
        print("\nSimulation. Relancer avec --ecrire.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
