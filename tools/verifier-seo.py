#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contrôle les invariants SEO / GEO du site. Aucune écriture.

Il y a trois façons de casser le référencement de ce site sans que rien ne se
voie à l'écran : déplacer une page sans toucher au sitemap, retoucher une
réponse de la FAQ sans son JSON-LD, ou renommer une image que l'`og:image`
désigne encore. Les trois sont silencieuses. C'est ce que ce script attrape.

Il complète les deux autres vérificateurs du dépôt — `verifier-srcset.py`
(le balisage déclare-t-il toutes les variantes présentes) et `verifier-sizes.py`
(les `sizes` correspondent-ils aux largeurs rendues). Ceux-là veillent sur les
images, celui-ci sur l'indexation.

    python tools/verifier-seo.py          # rapport complet
    python tools/verifier-seo.py --bref   # seulement les anomalies

Code de sortie 1 s'il reste une anomalie : utilisable tel quel dans un hook.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RACINE = Path(__file__).resolve().parent.parent
SITE = RACINE / "site"
DOMAINE = "https://domainededen.fr"

# Bornes usuelles d'affichage dans les SERP. Ce sont des repères, pas des règles
# absolues — Google mesure des pixels, pas des caractères — mais au-delà, la fin
# est coupée à coup sûr, et Google réécrit alors l'extrait lui-même.
TITRE_MAX = 60
META_MIN, META_MAX = 110, 165

OG_ATTENDUS = ["og:type", "og:site_name", "og:locale", "og:title",
               "og:description", "og:url", "og:image", "og:image:width",
               "og:image:height", "og:image:alt"]

anomalies: list[str] = []
notes: list[str] = []


def ko(page: str, message: str) -> None:
    anomalies.append(f"  ✗ {page} — {message}")


def ok(message: str) -> None:
    notes.append(f"  · {message}")


def texte_meta(html: str, cle: str, attribut: str = "property") -> str | None:
    m = re.search(rf'<meta {attribut}="{re.escape(cle)}" content="(.*?)">', html, re.S)
    return m.group(1) if m else None


def url_attendue(nom: str) -> str:
    """Les URLs gardent leur `.html` (cf. netlify.toml, pretty_urls = false)."""
    return f"{DOMAINE}/" if nom == "index.html" else f"{DOMAINE}/{nom}"


def sans_balises(fragment: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", fragment)).strip()


# ---------------------------------------------------------------------------
def controler_page(chemin: Path) -> dict:
    nom = chemin.name
    html = chemin.read_text(encoding="utf-8")
    noindex = bool(re.search(r'<meta name="robots"[^>]*content="[^"]*noindex', html, re.I))

    # -- canonical ----------------------------------------------------------
    m = re.search(r'<link rel="canonical" href="(.*?)">', html)
    if not m:
        ko(nom, "pas de <link rel=\"canonical\">")
    elif m.group(1) != url_attendue(nom):
        ko(nom, f'canonical = {m.group(1)}, attendu {url_attendue(nom)}')

    # -- titre et description ----------------------------------------------
    t = re.search(r"<title>(.*?)</title>", html, re.S)
    if not t:
        ko(nom, "pas de <title>")
    elif len(t.group(1)) > TITRE_MAX:
        ko(nom, f"<title> de {len(t.group(1))} caractères (max {TITRE_MAX}) — "
                "Google le tronquera")

    d = texte_meta(html, "description", "name")
    if not d:
        ko(nom, "pas de meta description")
    elif not (META_MIN <= len(d) <= META_MAX):
        ko(nom, f"meta description de {len(d)} caractères "
                f"(attendu {META_MIN}–{META_MAX})")

    # -- lang ---------------------------------------------------------------
    if '<html lang="fr">' not in html:
        ko(nom, 'l\'attribut lang="fr" manque sur <html>')

    if noindex:
        # Une page en noindex n'a besoin ni d'Open Graph ni de JSON-LD ; en
        # revanche elle ne doit surtout pas se retrouver dans le sitemap.
        return {"nom": nom, "noindex": True, "html": html}

    # -- Open Graph ---------------------------------------------------------
    for cle in OG_ATTENDUS:
        if texte_meta(html, cle) is None:
            ko(nom, f"balise {cle} manquante")
    if texte_meta(html, "twitter:card", "name") != "summary_large_image":
        ko(nom, 'twitter:card absent ou différent de "summary_large_image"')

    og_url = texte_meta(html, "og:url")
    if og_url and og_url != url_attendue(nom):
        ko(nom, f"og:url = {og_url}, attendu {url_attendue(nom)}")

    og_img = texte_meta(html, "og:image")
    if og_img:
        if not og_img.startswith("http"):
            ko(nom, "og:image doit être une URL absolue")
        else:
            fichier = SITE / og_img[len(DOMAINE) + 1:]
            if not fichier.exists():
                ko(nom, f"og:image introuvable sur le disque : {fichier.name}")
            else:
                try:
                    from PIL import Image
                    with Image.open(fichier) as im:
                        if im.size != (1200, 630):
                            ko(nom, f"og:image en {im.size[0]}×{im.size[1]}, "
                                    "attendu 1200×630")
                except ImportError:
                    pass

    # -- JSON-LD ------------------------------------------------------------
    blocs = re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                       html, re.S)
    if not blocs:
        ko(nom, "aucun JSON-LD")
        return {"nom": nom, "noindex": False, "html": html}

    for i, brut in enumerate(blocs):
        try:
            data = json.loads(brut)
        except json.JSONDecodeError as e:
            ko(nom, f"JSON-LD n°{i + 1} illisible : {e}")
            continue

        graphe = data.get("@graph", [data])
        ids = {n["@id"] for n in graphe if isinstance(n, dict) and "@id" in n}

        # Une référence {"@id": …} qui ne désigne aucun nœud de la MÊME page ne
        # se résout pas : le graphe est reconstruit page par page.
        def references(n, chemin_desc="") -> list[str]:
            trouve = []
            if isinstance(n, dict):
                if set(n.keys()) == {"@id"}:
                    trouve.append(n["@id"])
                for v in n.values():
                    trouve += references(v)
            elif isinstance(n, list):
                for v in n:
                    trouve += references(v)
            return trouve

        for ref in set(references(graphe)):
            if ref not in ids:
                ko(nom, f"JSON-LD : la référence @id « {ref} » ne désigne aucun "
                        "nœud de cette page")

        types = {t for n in graphe if isinstance(n, dict)
                 for t in ([n["@type"]] if isinstance(n.get("@type"), str)
                           else n.get("@type", []))}
        if "BedAndBreakfast" not in types:
            ko(nom, "JSON-LD : le nœud BedAndBreakfast manque")

    return {"nom": nom, "noindex": False, "html": html, "blocs": blocs}


# ---------------------------------------------------------------------------
def controler_faq(pages: dict) -> None:
    """La FAQ visible et le FAQPage doivent dire exactement la même chose.

    C'est le seul endroit du site où un texte existe en double. S'ils divergent,
    Google considère le balisage comme non représentatif du contenu — et un
    assistant qui repère la contradiction cesse de faire confiance à la page.
    """
    html = pages["index.html"]["html"]

    visibles = [(sans_balises(q), sans_balises(r)) for q, r in re.findall(
        r'<summary><span>(.*?)</span></summary>\s*'
        r'<div class="faq-reponse"><p>(.*?)</p></div>', html, re.S)]

    balisees = []
    for brut in pages["index.html"].get("blocs", []):
        for n in json.loads(brut).get("@graph", []):
            if isinstance(n, dict) and n.get("@type") == "FAQPage":
                balisees = [(q["name"], q["acceptedAnswer"]["text"])
                            for q in n["mainEntity"]]

    if not visibles:
        ko("index.html", "aucune question visible dans la section FAQ")
        return
    if not balisees:
        ko("index.html", "la section FAQ existe mais le FAQPage JSON-LD manque")
        return
    if len(visibles) != len(balisees):
        ko("index.html", f"{len(visibles)} question(s) visible(s) contre "
                         f"{len(balisees)} balisée(s)")
        return

    import html as H
    for (qv, rv), (qb, rb) in zip(visibles, balisees):
        if H.unescape(qv) != qb:
            ko("index.html", f"FAQ : question divergente — « {qv[:55]}… »")
        if H.unescape(rv) != rb:
            ko("index.html", f"FAQ : réponse divergente sous « {qb[:45]}… »")
    ok(f"FAQ : {len(visibles)} questions, texte visible et FAQPage identiques")


# ---------------------------------------------------------------------------
def controler_sitemap(pages: dict) -> None:
    fichier = SITE / "sitemap.xml"
    if not fichier.exists():
        ko("sitemap.xml", "absent — le relancer avec tools/generer-sitemap.py")
        return

    try:
        racine = ElementTree.parse(fichier).getroot()
    except ElementTree.ParseError as e:
        ko("sitemap.xml", f"XML invalide : {e}")
        return

    NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    IMG = "{http://www.google.com/schemas/sitemap-image/1.1}"
    declarees = {u.find(NS + "loc").text for u in racine.findall(NS + "url")}
    attendues = {url_attendue(n) for n, p in pages.items() if not p["noindex"]}

    for manquante in sorted(attendues - declarees):
        ko("sitemap.xml", f"{manquante} est indexable mais absente du sitemap")
    for en_trop in sorted(declarees - attendues):
        ko("sitemap.xml", f"{en_trop} est déclarée mais n'est pas une page "
                          "indexable (page supprimée, renommée, ou en noindex)")

    manquantes = [i.text for i in racine.iter(IMG + "loc")
                  if not (SITE / i.text[len(DOMAINE) + 1:]).exists()]
    for m in manquantes[:5]:
        ko("sitemap.xml", f"photo déclarée mais absente du disque : {m}")
    if not manquantes:
        ok(f"sitemap : {len(declarees)} URL, "
           f"{len(list(racine.iter(IMG + 'loc')))} photos, toutes présentes")


# ---------------------------------------------------------------------------
def controler_robots() -> None:
    fichier = SITE / "robots.txt"
    if not fichier.exists():
        ko("robots.txt", "absent")
        return
    t = fichier.read_text(encoding="utf-8")

    if f"Sitemap: {DOMAINE}/sitemap.xml" not in t:
        ko("robots.txt", "ne déclare pas le sitemap")

    # Un « Disallow: / » sous l'un de ces agents rendrait le site invisible là où
    # il veut précisément être vu. Le repérer vaut mieux que de le découvrir
    # trois mois plus tard dans la Search Console.
    groupes = re.findall(r"User-agent:\s*(\S+)\s*\n((?:(?!User-agent:).)*)", t, re.S)
    essentiels = {"googlebot", "bingbot", "oai-searchbot", "perplexitybot",
                  "claude-searchbot", "*"}
    for agent, corps in groupes:
        if agent.lower() in essentiels and re.search(r"^Disallow:\s*/\s*$", corps, re.M):
            ko("robots.txt", f"« {agent} » est bloqué par Disallow: / — "
                             "le site deviendrait invisible pour lui")
    ok(f"robots.txt : {len(groupes)} groupes d'agents, sitemap déclaré")


# ---------------------------------------------------------------------------
def controler_liens(pages: dict) -> None:
    """Liens internes morts, et ancres qui ne mènent nulle part."""
    ids = {n: set(re.findall(r'\sid="([^"]+)"', p["html"])) for n, p in pages.items()}
    morts = 0

    for nom, p in pages.items():
        for href in set(re.findall(r'href="([^"]+)"', p["html"])):
            if href.startswith(("http", "mailto:", "tel:", "#")) or not href:
                if href.startswith("#") and href[1:] not in ids[nom]:
                    ko(nom, f"ancre morte : {href}")
                    morts += 1
                continue
            cible, _, frag = href.partition("#")
            cible = cible.split("?")[0]
            if not cible.endswith(".html"):
                continue
            if cible not in pages:
                ko(nom, f"lien vers une page inexistante : {cible}")
                morts += 1
            elif frag and frag not in ids[cible]:
                ko(nom, f"ancre morte : {cible}#{frag}")
                morts += 1

    if not morts:
        ok("liens internes : aucune page ni ancre morte")


# ---------------------------------------------------------------------------
def controler_structure(pages: dict) -> None:
    depart = len(anomalies)
    for nom, p in pages.items():
        html = p["html"]

        h1 = re.findall(r"<h1[ >]", html)
        if len(h1) != 1:
            ko(nom, f"{len(h1)} <h1> (il en faut exactement un)")

        # Sauts de niveau : un h4 qui suit un h2 laisse un trou dans le plan.
        niveaux = [int(m) for m in re.findall(r"<h([1-6])[ >]", html)]
        for a, b in zip(niveaux, niveaux[1:]):
            if b > a + 1:
                ko(nom, f"saut de niveau h{a} → h{b} dans le plan de la page")
                break

        sans_alt = re.findall(r"<img(?![^>]*\salt=)[^>]*>", html)
        if sans_alt:
            ko(nom, f"{len(sans_alt)} <img> sans attribut alt")

        if 'class="skip-link"' not in html:
            ko(nom, "pas de lien d'évitement")
        elif 'id="contenu"' not in html:
            ko(nom, "le lien d'évitement n'a pas de cible id=\"contenu\"")

    if len(anomalies) == depart:
        ok("structure : un h1 par page, plan sans saut, tous les alt présents, "
           "lien d'évitement partout")


# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bref", action="store_true",
                    help="n'afficher que les anomalies")
    args = ap.parse_args()

    pages = {}
    for chemin in sorted(SITE.glob("*.html")):
        pages[chemin.name] = controler_page(chemin)

    indexables = [n for n, p in pages.items() if not p["noindex"]]
    controler_faq(pages)
    controler_sitemap(pages)
    controler_robots()
    controler_liens(pages)
    controler_structure(pages)

    print(f"\n{len(pages)} pages contrôlées — {len(indexables)} indexables, "
          f"{len(pages) - len(indexables)} en noindex.\n")

    if not args.bref:
        for n in notes:
            print(n)
        if notes:
            print()

    if anomalies:
        print(f"{len(anomalies)} anomalie(s) :\n")
        for a in anomalies:
            print(a)
        print()
        return 1

    print("  Aucune anomalie.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
