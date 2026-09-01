#!/usr/bin/env python3
"""Banc d'essai responsive du Domaine d'Éden.

Sert `site/`, ouvre chaque page dans une matrice de vraies tailles d'écran
(du iPhone SE au 2560 px), capture la page entière et relève automatiquement
ce qui casse : débordement horizontal, cibles tactiles trop petites, texte
sous le seuil de lisibilité, lignes trop longues, images sous-résolues.

    python tools/audit-responsive.py                    # tout
    python tools/audit-responsive.py --pages index      # une page
    python tools/audit-responsive.py --vp mobile        # une classe d'écran
    python tools/audit-responsive.py --rapide           # 4 tailles clés

Sorties dans .audit/ : shots/<page>__<ecran>.png, rapport.json, RAPPORT.md
"""

import argparse
import functools
import http.server
import json
import shutil
import socketserver
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

RACINE = Path(__file__).resolve().parent.parent
SITE = RACINE / "site"
SORTIE = RACINE / ".audit"

PAGES = ["index", "chambres", "evenements", "reservation"]

# Largeur, hauteur, DPR, classe. Les tailles sont celles d'appareils réels :
# c'est là que le site sera vraiment vu, pas à des paliers ronds.
ECRANS = [
    ("se-320",         320,  568, 2, "mobile"),    # le pire cas encore en service
    ("android-360",    360,  740, 3, "mobile"),
    ("iphone-390",     390,  844, 3, "mobile"),
    ("iphone-max-430", 430,  932, 3, "mobile"),
    ("pliant-540",     540,  720, 2, "mobile"),    # Surface Duo, pliants dépliés
    ("tab-600",        600,  960, 2, "tablette"),
    ("ipad-768",       768, 1024, 2, "tablette"),
    ("ipad-air-820",   820, 1180, 2, "tablette"),
    ("surface-912",    912, 1368, 2, "tablette"),
    ("ipad-pay-1024", 1024,  768, 2, "tablette"),
    ("ipad-pay-1180", 1180,  820, 2, "tablette"),
    ("laptop-1280",   1280,  800, 1, "desktop"),
    ("laptop-1440",   1440,  900, 2, "desktop"),
    ("desktop-1920",  1920, 1080, 1, "desktop"),
    ("large-2560",    2560, 1440, 1, "desktop"),
]

RAPIDE = {"se-320", "iphone-390", "ipad-768", "laptop-1440"}

# Les blocs qu'on regarde un par un : une capture pleine page fait 12 000 px de
# haut, on n'y juge rien. --composants cadre chaque bloc, c'est là qu'on voit
# si une grille de 4 cartes tient encore à 768 px.
COMPOSANTS = {
    "index": [
        ("entete", "header"),
        ("hero", ".hero"),
        ("editorial", ".editorial"),
        ("chambres", "#chambres .rooms-grid"),
        ("evenements", ".events-wrap"),
        ("alentours", ".around-grid"),
        ("galerie", ".gallery"),
        ("contact", ".contact-grid"),
        ("pied", "footer"),
    ],
    "chambres": [
        ("entete", "header"),
        ("chambre-1", "#suite-roi-reine"),
        ("chambre-2", "#antichambre-nuit"),
        ("equipements", ".room-amenities-groups"),
    ],
    "evenements": [
        ("formats", ".formats-grid"),
        ("carte-format", ".format-card"),
        ("faits", ".facts-grid"),
        ("deroule", ".steps-flow"),
    ],
    "reservation": [
        ("formulaire", "form"),
        ("choix-chambres", ".room-choice-grid"),
        ("champs", ".field-row"),
    ],
}

# Relevé exécuté dans la page. Renvoie des faits, pas des jugements :
# c'est la lecture des captures qui tranche l'esthétique.
SONDE = r"""
() => {
  const vw = window.innerWidth, dpr = window.devicePixelRatio;
  const nom = (el) => {
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    if (el.classList.length) s += '.' + [...el.classList].slice(0, 3).join('.');
    return s;
  };
  const visible = (el) => {
    const st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden' || +st.opacity === 0) return false;
    if (st.clipPath === 'inset(50%)' || el.classList.contains('sr-only')) return false;  // texte pour lecteur d'écran
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  // Un débordement n'en est un que s'il atteint la fenêtre : un marquee ou un
  // visuel pleine largeur enfermé dans un parent qui coupe est intentionnel.
  const clippe = (el) => {
    for (let p = el.parentElement; p && p !== document.documentElement; p = p.parentElement) {
      const s = getComputedStyle(p);
      if (s.overflowX !== 'visible' || s.overflow !== 'visible') return true;
    }
    return false;
  };
  const tous = [...document.body.querySelectorAll('*')];

  // 1. Débordement horizontal : la page doit tenir dans sa largeur.
  const de = document.documentElement;
  const debordePage = de.scrollWidth - de.clientWidth;
  const coupables = [];
  for (const el of tous) {
    if (!visible(el)) continue;
    const st = getComputedStyle(el);
    // un conteneur qui défile horizontalement de son plein gré n'est pas un défaut
    if (st.overflowX === 'auto' || st.overflowX === 'scroll' || st.overflowX === 'hidden') continue;
    if (clippe(el)) continue;
    const r = el.getBoundingClientRect();
    const trop = Math.max(r.right - vw, -r.left);
    if (trop > 1.5) coupables.push({ el: nom(el), trop: Math.round(trop), largeur: Math.round(r.width) });
  }
  coupables.sort((a, b) => b.trop - a.trop);

  // 2. Cibles tactiles : 44x44 CSS px, la règle Apple / WCAG 2.5.5.
  // La mesure porte sur la zone qui répond au doigt, pas sur la boîte du
  // texte : une carte rendue cliquable par un `::after` étendu offre une
  // cible bien plus large que son <a>, et la compter comme trop petite
  // enverrait corriger ce qui va déjà bien. On part donc du centre et on
  // s'écarte tant que le point d'impact retombe sur le même lien.
  const sien = (n, el) => n && (n === el || el.contains(n) ||
                                (n.closest && n.closest('a[href],button,summary,[role="button"]') === el));
  const portee = (el, dx, dy) => {
    const r = el.getBoundingClientRect();
    const x = r.left + r.width / 2, y = r.top + r.height / 2;
    let d = 0;
    for (let pas = 4; pas <= 26; pas += 4) {
      if (!sien(document.elementFromPoint(x + dx * pas, y + dy * pas), el)) break;
      d = pas;
    }
    return d;
  };

  const petites = [];
  const candidats = [...document.querySelectorAll('a[href], button, input, select, textarea, summary, [role="button"], [tabindex]:not([tabindex="-1"])')];
  // Amener une cible au centre fait defiler tous ses ancetres, rails compris.
  // On note ou en etait chaque conteneur pour lui rendre sa place ensuite :
  // une sonde qui laisse la page ailleurs qu'elle ne l'a trouvee fausse la
  // capture suivante.
  const retour = window.scrollY;
  const places = tous.filter(el => el.scrollWidth > el.clientWidth || el.scrollHeight > el.clientHeight)
                     .map(el => [el, el.scrollLeft, el.scrollTop]);
  for (const el of candidats) {
    if (!visible(el)) continue;
    let r = el.getBoundingClientRect();
    if (r.width >= 44 && r.height >= 44) continue;
    // elementFromPoint travaille en coordonnées de fenêtre : hors écran il
    // renvoie null. On amène donc la cible au milieu, loin de l'en-tête fixe.
    el.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'instant' });
    r = el.getBoundingClientRect();
    const large = Math.max(r.width, portee(el, -1, 0) + portee(el, 1, 0));
    const haut = Math.max(r.height, portee(el, 0, -1) + portee(el, 0, 1));
    if (large < 44 || haut < 44) {
      petites.push({ el: nom(el), t: Math.round(large) + 'x' + Math.round(haut),
                     boite: Math.round(r.width) + 'x' + Math.round(r.height),
                     txt: (el.textContent || '').trim().slice(0, 34) });
    }
  }
  places.forEach(([el, x, y]) => { el.scrollLeft = x; el.scrollTop = y; });
  window.scrollTo(0, retour);

  // 3. Texte trop petit (< 13px).
  const menu = [];
  for (const el of tous) {
    if (!visible(el) || !el.childNodes.length) continue;
    const propre = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 3);
    if (!propre) continue;
    const px = parseFloat(getComputedStyle(el).fontSize);
    if (px < 13) menu.push({ el: nom(el), px: +px.toFixed(1), txt: el.textContent.trim().slice(0, 34) });
  }

  // 4. Longueur de ligne : au-delà de ~92 caractères l'oeil décroche.
  const longues = [];
  for (const el of document.querySelectorAll('p, li, blockquote')) {
    if (!visible(el)) continue;
    const st = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    if (r.height > parseFloat(st.lineHeight) * 1.6) {          // au moins 2 lignes : c'est un paragraphe
      const ch = r.width / (parseFloat(st.fontSize) * 0.5);    // ~0,5 em par caractère
      if (ch > 92) longues.push({ el: nom(el), ch: Math.round(ch), px: Math.round(r.width) });
    }
  }

  // 5. Images sous-résolues pour cet écran (flou sur Retina).
  const floues = [];
  for (const img of document.images) {
    if (!visible(img) || !img.naturalWidth) continue;
    const r = img.getBoundingClientRect();
    const ratio = img.naturalWidth / (r.width * dpr);
    if (ratio < 0.75) floues.push({ src: (img.currentSrc || '').split('/').pop(), ratio: +ratio.toFixed(2),
                                    rendu: Math.round(r.width) + 'px@' + dpr });
  }

  // 6. Défilements horizontaux volontaires : les carrousels qu'on veut voir apparaître.
  const rails = [];
  for (const el of tous) {
    const st = getComputedStyle(el);
    if (st.overflowX !== 'auto' && st.overflowX !== 'scroll') continue;
    if (el.scrollWidth <= el.clientWidth + 4) continue;
    rails.push({ el: nom(el), snap: st.scrollSnapType,
                 pages: +(el.scrollWidth / Math.max(el.clientWidth, 1)).toFixed(2) });
  }

  // Le même sélecteur revient à chaque section : on compte les cas, on ne les répète pas.
  const grouper = (liste, cle) => {
    const m = new Map();
    for (const x of liste) {
      const k = cle(x);
      if (m.has(k)) m.get(k).n++;
      else m.set(k, Object.assign({ n: 1 }, x));
    }
    return [...m.values()].sort((a, b) => b.n - a.n);
  };
  const menuG = grouper(menu, x => x.el + '|' + x.px);
  const ciblesG = grouper(petites, x => x.el + '|' + x.t);

  return {
    hauteur: Math.round(de.scrollHeight),
    debordePage: Math.round(debordePage),
    coupables: coupables.slice(0, 12),
    cibles: ciblesG.slice(0, 15), nbCibles: petites.length,
    menu: menuG.slice(0, 10), nbMenu: menu.length,
    longues: longues.slice(0, 8), nbLongues: longues.length,
    floues: floues.slice(0, 8), nbFloues: floues.length,
    rails: rails,
  };
}
"""


def attendre_images(page, delai=2500):
    """N'immortalise pas une image encore en vol.

    Les visuels sont en `loading="lazy"` : les amener dans la fenetre lance
    leur chargement, mais la capture peut partir avant. On voyait alors le
    fond du `figure` a la place de la photo — et on croyait a un trou dans la
    grille.
    """
    try:
        page.wait_for_function(
            "() => [...document.images].every(i => i.complete || !i.getBoundingClientRect().width)",
            timeout=delai)
    except Exception:
        pass


def serveur(port_essai=8765):
    """Sert site/ en tâche de fond, renvoie (port, arret)."""
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SITE))
    handler.log_message = lambda *a, **k: None
    socketserver.TCPServer.allow_reuse_address = True
    srv = None
    for port in range(port_essai, port_essai + 40):
        try:
            srv = socketserver.ThreadingTCPServer(("127.0.0.1", port), handler)
            break
        except OSError:
            continue
    if srv is None:
        sys.exit("aucun port libre")
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return port, srv.shutdown


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", default=",".join(PAGES))
    ap.add_argument("--vp", default="", help="filtre : nom d'ecran, ou classe mobile/tablette/desktop")
    ap.add_argument("--rapide", action="store_true", help="4 tailles cles seulement")
    ap.add_argument("--sans-captures", action="store_true")
    ap.add_argument("--composants", action="store_true", help="une capture par bloc au lieu de la page entiere")
    ap.add_argument("--cadres", action="store_true", help="la fenetre cadree sur chaque bloc : ce que voit vraiment le visiteur")
    args = ap.parse_args()

    pages = [p for p in args.pages.split(",") if p]
    ecrans = ECRANS
    if args.rapide:
        ecrans = [e for e in ecrans if e[0] in RAPIDE]
    if args.vp:
        f = args.vp.split(",")
        ecrans = [e for e in ecrans if e[0] in f or e[4] in f]
    if not ecrans:
        sys.exit("aucun ecran ne correspond a --vp")

    shots = SORTIE / "shots"
    shots.mkdir(parents=True, exist_ok=True)

    port, arret = serveur()
    base = "http://127.0.0.1:%d" % port
    rapport = {"pages": pages, "ecrans": [e[0] for e in ecrans], "releves": []}

    with sync_playwright() as p:
        nav = p.chromium.launch()
        for nom, w, h, dpr, classe in ecrans:
            ctx = nav.new_context(
                viewport={"width": w, "height": h},
                device_scale_factor=dpr,
                is_mobile=(classe == "mobile"),
                has_touch=classe in ("mobile", "tablette"),
                reduced_motion="reduce",   # neutralise rideau + reveals : tout est visible
            )
            page = ctx.new_page()
            for nom_page in pages:
                page.goto("%s/%s.html" % (base, nom_page), wait_until="load")
                page.wait_for_timeout(350)
                try:
                    page.evaluate("() => document.fonts.ready")
                except Exception:
                    pass
                page.wait_for_timeout(150)
                if args.cadres:
                    # La fenetre, pas l'element : c'est le seul cadrage ou l'on
                    # juge un carrousel — on y voit l'amorce de la vue suivante,
                    # les puces, et ce que la barre d'en-tete recouvre.
                    for cnom, sel in COMPOSANTS.get(nom_page, []):
                        el = page.query_selector(sel)
                        if el is None:
                            continue
                        try:
                            el.scroll_into_view_if_needed()
                        except Exception:
                            continue
                        page.wait_for_timeout(160)
                        attendre_images(page)
                        page.screenshot(path=str(shots / ("%s__%s__%s__vue.png" % (nom_page, cnom, nom))),
                                        scale="css")
                elif args.composants:
                    # un fichier par bloc : c'est cadre par cadre qu'on juge une mise en page
                    for cnom, sel in COMPOSANTS.get(nom_page, []):
                        el = page.query_selector(sel)
                        if el is None:
                            continue
                        boite = el.bounding_box()
                        if not boite or boite["height"] < 4:
                            continue
                        chemin = shots / ("%s__%s__%s.png" % (nom_page, cnom, nom))
                        try:
                            el.scroll_into_view_if_needed()
                            page.wait_for_timeout(120)
                            attendre_images(page)
                            el.screenshot(path=str(chemin))
                        except Exception:
                            continue
                elif not args.sans_captures:
                    # capture a DPR 1 : lisible, et 15x4 fichiers restent legers
                    chemin = shots / ("%s__%s.png" % (nom_page, nom))
                    page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
                    attendre_images(page)
                    page.evaluate("() => window.scrollTo(0, 0)")
                    page.wait_for_timeout(120)
                    page.screenshot(path=str(chemin), full_page=True, scale="css")
                    shot = str(chemin.relative_to(RACINE)).replace("\\", "/")
                # La sonde passe apres les captures : elle deplace la page pour
                # mesurer les cibles tactiles, la capture doit la voir intacte.
                r = page.evaluate(SONDE)
                r.update(page=nom_page, ecran=nom, w=w, h=h, dpr=dpr, classe=classe)
                if not args.composants and not args.cadres and not args.sans_captures:
                    r["shot"] = shot
                rapport["releves"].append(r)
                cri = r["debordePage"] > 1 or r["coupables"]
                print("  %s %-12s %-14s deborde=%4d coupables=%2d cibles=%2d petit-texte=%2d lignes-longues=%2d rails=%d"
                      % ("!!" if cri else "  ", nom_page, nom, r["debordePage"], len(r["coupables"]),
                         r["nbCibles"], r["nbMenu"], r["nbLongues"], len(r["rails"])))
            ctx.close()
        nav.close()
    arret()

    SORTIE.mkdir(exist_ok=True)
    (SORTIE / "rapport.json").write_text(json.dumps(rapport, indent=1, ensure_ascii=False), encoding="utf-8")

    # Synthese lisible : d'abord ce qui casse, ecran par ecran.
    L = ["# Releve responsive", ""]
    durs = [r for r in rapport["releves"] if r["debordePage"] > 1 or r["coupables"]]
    L.append("**%d releves en debordement** sur %d." % (len(durs), len(rapport["releves"])))
    L.append("")
    L.append("| page | ecran | deborde | coupable principal | cibles<44 | txt<13 | lignes>92ch | flou | rails |")
    L.append("|---|---|--:|---|--:|--:|--:|--:|--:|")
    for r in rapport["releves"]:
        c = r["coupables"][0] if r["coupables"] else None
        L.append("| %s | %s | %d | %s | %d | %d | %d | %d | %d |"
                 % (r["page"], r["ecran"], r["debordePage"],
                    ("%s +%dpx" % (c["el"], c["trop"])) if c else "—",
                    r["nbCibles"], r["nbMenu"], r["nbLongues"], r["nbFloues"], len(r["rails"])))
    L.append("")
    for r in rapport["releves"]:
        det = []
        if r["coupables"]:
            det.append("  - debordent : " + "; ".join("%s (+%dpx)" % (c["el"], c["trop"]) for c in r["coupables"][:6]))
        if r["cibles"]:
            det.append("  - cibles tactiles : " + "; ".join("%s %s" % (c["el"], c["t"]) for c in r["cibles"][:6]))
        if r["menu"]:
            det.append("  - texte < 13px : " + "; ".join("%s %spx" % (m["el"], m["px"]) for m in r["menu"][:6]))
        if r["longues"]:
            det.append("  - lignes longues : " + "; ".join("%s ~%dch" % (x["el"], x["ch"]) for x in r["longues"][:5]))
        if r["floues"]:
            det.append("  - sous-resolu : " + "; ".join("%s x%s" % (f["src"], f["ratio"]) for f in r["floues"][:5]))
        if r["rails"]:
            det.append("  - carrousels : " + "; ".join("%s %secrans snap=%s" % (x["el"], x["pages"], x["snap"]) for x in r["rails"]))
        if det:
            L.append("### %s · %s (%dx%d @%d)" % (r["page"], r["ecran"], r["w"], r["h"], r["dpr"]))
            L += det
            L.append("")
    (SORTIE / "RAPPORT.md").write_text("\n".join(L), encoding="utf-8")
    print("\n-> .audit/RAPPORT.md  (%d releves en debordement / %d)" % (len(durs), len(rapport["releves"])))


if __name__ == "__main__":
    main()
