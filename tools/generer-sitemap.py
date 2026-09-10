#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Produit `site/sitemap.xml` à partir des pages réellement présentes.

Le sitemap n'est pas écrit à la main parce qu'il ment vite : une page ajoutée,
une date de retouche, une photo remplacée, et il pointe à côté. Ici il se
régénère depuis le disque et depuis git.

Trois partis pris, tous délibérés :

* **Les URLs gardent leur `.html`**, exactement comme les liens internes du
  site — lesquels ne peuvent pas s'en passer, le site devant rester ouvrable
  en `file://`. Netlify sait servir `/chambres` sans extension, et le ferait
  même en redirigeant `/chambres.html` vers lui : `netlify.toml` désactive donc
  explicitement `pretty_urls`. Sans ça, chaque lien interne coûterait un 301,
  et le canonical déclaré ici ne serait pas l'URL réellement servie.

* **Les pages en `noindex` sont exclues.** Mentions légales et politique de
  confidentialité portent `<meta name="robots" content="noindex, follow">` :
  les déclarer ici enverrait à Google une consigne contradictoire — « indexe
  cette page » d'un côté, « ne l'indexe pas » de l'autre. Le script lit la
  balise, il ne tient pas une liste en dur.

* **`lastmod` vient de git, pas du système de fichiers.** La date de
  modification d'un fichier change à chaque `checkout` ; la date du dernier
  commit qui a touché la page est la seule qui corresponde à une vraie retouche
  de contenu.

Les photos sont déclarées en extension `image/` : pour une maison d'hôtes, la
recherche d'images est une porte d'entrée réelle. Le script retient la plus
grande variante JPEG de chaque photo citée par la page — le JPEG et non l'AVIF,
parce que c'est lui que porte l'`<img>`, donc l'URL que le crawler verra.

    python tools/generer-sitemap.py            # simulation
    python tools/generer-sitemap.py --ecrire   # écrit site/sitemap.xml
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

# La console Windows est en cp1252 : sans ça, la première flèche du journal
# fait tomber le script sur un UnicodeEncodeError.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RACINE = Path(__file__).resolve().parent.parent
SITE = RACINE / "site"
DOMAINE = "https://domainededen.fr"

# Priorité et fréquence par page. Ce sont des indications, que Google ignore
# largement depuis des années — on les garde parce que Bing et quelques
# agrégateurs les lisent encore, et parce qu'elles ne coûtent rien.
PAGES = {
    "index.html": ("1.0", "monthly"),
    "chambres.html": ("0.9", "monthly"),
    "evenements.html": ("0.9", "monthly"),
    "reservation.html": ("0.8", "yearly"),
}

NOINDEX = re.compile(r'<meta\s+name="robots"[^>]*content="[^"]*noindex', re.I)
IMG_SRC = re.compile(r'<img[^>]+src="(assets/img/[^"]+\.jpg)"', re.I)
IMG_ALT = re.compile(r'alt="([^"]*)"')


def url_page(fichier: str) -> str:
    """`index.html` → `/` (racine servie par Netlify), les autres → `/<nom>.html`."""
    if fichier == "index.html":
        return DOMAINE + "/"
    return DOMAINE + "/" + fichier


def derniere_retouche(fichier: str) -> str:
    """Date du dernier commit ayant touché la page, au format ISO."""
    try:
        sortie = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", f"site/{fichier}"],
            cwd=RACINE, capture_output=True, text=True, timeout=10,
        )
        jour = sortie.stdout.strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", jour):
            return jour
    except (OSError, subprocess.SubprocessError):
        pass
    return date.today().isoformat()


def plus_grande_variante(chemin: str) -> str | None:
    """`…/chambre-suite-480.jpg` → la variante la plus large réellement sur le disque."""
    m = re.fullmatch(r"assets/img/(.+)-(\d+)\.jpg", chemin)
    if not m:
        return None
    nom = m.group(1)
    largeurs = []
    for f in (SITE / "assets" / "img").glob(f"{nom}-*.jpg"):
        m2 = re.fullmatch(rf"{re.escape(nom)}-(\d+)\.jpg", f.name)
        if m2:
            largeurs.append(int(m2.group(1)))
    if not largeurs:
        return None
    return f"assets/img/{nom}-{max(largeurs)}.jpg"


def photos(html: str) -> list[tuple[str, str]]:
    """Les photos de la page, dédoublonnées, dans l'ordre d'apparition.

    Une même photo apparaît à plusieurs largeurs dans le balisage ; on ne
    déclare qu'une URL par photo, la plus grande, et on lui garde l'`alt` de
    l'`<img>` comme légende.
    """
    vues: dict[str, str] = {}
    for balise in re.finditer(r"<img\b[^>]*>", html, re.I):
        src = IMG_SRC.search(balise.group(0))
        if not src:
            continue
        grande = plus_grande_variante(src.group(1))
        if not grande or grande in vues:
            continue
        alt = IMG_ALT.search(balise.group(0))
        vues[grande] = (alt.group(1).strip() if alt else "")
    return list(vues.items())


def construire() -> tuple[str, list[str]]:
    lignes = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
    ]
    journal = []

    for fichier in sorted(SITE.glob("*.html"), key=lambda p: p.name):
        nom = fichier.name
        html = fichier.read_text(encoding="utf-8")

        if NOINDEX.search(html):
            journal.append(f"  ignorée (noindex) : {nom}")
            continue
        if nom not in PAGES:
            journal.append(f"  ignorée (hors liste) : {nom}")
            continue

        priorite, frequence = PAGES[nom]
        images = photos(html)
        journal.append(f"  {nom:<24} → {url_page(nom):<38} {len(images)} photo(s)")

        lignes.append("  <url>")
        lignes.append(f"    <loc>{escape(url_page(nom))}</loc>")
        lignes.append(f"    <lastmod>{derniere_retouche(nom)}</lastmod>")
        lignes.append(f"    <changefreq>{frequence}</changefreq>")
        lignes.append(f"    <priority>{priorite}</priority>")
        for src, legende in images:
            lignes.append("    <image:image>")
            lignes.append(f"      <image:loc>{escape(DOMAINE + '/' + src)}</image:loc>")
            if legende:
                lignes.append(f"      <image:title>{escape(legende)}</image:title>")
            lignes.append("    </image:image>")
        lignes.append("  </url>")

    lignes.append("</urlset>")
    return "\n".join(lignes) + "\n", journal


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ecrire", action="store_true",
                    help="écrit site/sitemap.xml (sans l'option : simulation)")
    args = ap.parse_args()

    xml, journal = construire()
    for ligne in journal:
        print(ligne)

    cible = SITE / "sitemap.xml"
    if args.ecrire:
        cible.write_text(xml, encoding="utf-8")
        print(f"\nÉcrit : {cible.relative_to(RACINE)} ({len(xml)} octets)")
    else:
        print(f"\nSimulation — {len(xml)} octets seraient écrits dans "
              f"{cible.relative_to(RACINE)}. Relancer avec --ecrire.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
