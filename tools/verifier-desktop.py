#!/usr/bin/env python3
"""Le desktop ne doit pas bouger.

Règle de la refonte responsive : toute la transformation vit dans des
`@media (max-width: …)`. Ce script le prouve au lieu de l'affirmer — il rend
les pages au-dessus du seuil des rails, à six largeurs de 901 à 1920 px, et
compare au rendu de référence.

Deux modes de référence :

    python tools/verifier-desktop.py --figer     # fige l'état actuel comme référence
    python tools/verifier-desktop.py             # compare à la référence figée

et, à défaut de référence figée, la comparaison se fait contre un point git :

    python tools/verifier-desktop.py --ref HEAD

**Préférer `--figer` avant de commencer une passe.** Le dossier de travail peut
contenir le travail de quelqu'un d'autre ; comparer à `HEAD` mélangerait alors
ses changements aux siens et signalerait des écarts qui n'ont rien à voir avec
la passe en cours. Une référence figée juste avant d'éditer isole exactement
l'effet de la passe.

En cas d'écart, le script décrit les zones qui diffèrent (position, taille,
nombre de pixels) et écrit les deux rendus dans `.audit/`, pour qu'on puisse
juger si l'écart est celui qu'on attendait.
"""

import argparse
import functools
import http.server
import io
import json
import shutil
import socketserver
import subprocess
import sys
import threading
from pathlib import Path

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

RACINE = Path(__file__).resolve().parent.parent
SITE = RACINE / "site"
SORTIE = RACINE / ".audit"
REFERENCE = SORTIE / "desktop-ref"
PAGES = ["index", "chambres", "evenements", "reservation"]
LARGEURS = [901, 940, 1024, 1280, 1440, 1920]


def servir(dossier, port):
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(dossier))
    h.log_message = lambda *a, **k: None
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", port), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def rendre(nav, port, nom, largeur):
    ctx = nav.new_context(viewport={"width": largeur, "height": 900},
                          device_scale_factor=1, reduced_motion="reduce")
    pg = ctx.new_page()
    pg.goto("http://127.0.0.1:%d/%s.html" % (port, nom), wait_until="load")
    try:
        pg.evaluate("() => document.fonts.ready")
    except Exception:
        pass
    # Les visuels sont en `loading="lazy"`. Sauter d'un coup en bas de page ne
    # les declenche pas tous — le navigateur ne charge que ce qui approche de
    # la fenetre — et la capture attrapait alors le fond gris de quelques
    # `figure`. Deux rendus differaient sur des bandes de la taille d'une
    # photo, et on lisait une regression la ou il n'y avait qu'une course.
    # On descend donc par paliers, puis on attend le decodage.
    pg.evaluate("""async () => {
      const pas = window.innerHeight * 0.8;
      for (let y = 0; y < document.body.scrollHeight; y += pas) {
        window.scrollTo(0, y);
        await new Promise(r => setTimeout(r, 60));
      }
      window.scrollTo(0, 0);
    }""")
    try:
        pg.wait_for_function(
            "() => [...document.images].every(i => i.complete || !i.getBoundingClientRect().width)",
            timeout=8000)
    except Exception:
        pass
    try:
        pg.evaluate("() => Promise.all([...document.images].map(i => i.decode().catch(() => {})))")
    except Exception:
        pass
    pg.wait_for_timeout(400)
    png = pg.screenshot(full_page=True)
    ctx.close()
    return png


def zones(avant, apres):
    """Décrit ce qui diffère : une liste de bandes, avec leur poids en pixels.

    Un écart attendu (un pied de page qui a gagné des liens) forme une bande
    étroite et bien située ; une vraie régression de mise en page en forme
    plusieurs, hautes, un peu partout. La forme du diff dit laquelle des deux
    on a sous les yeux.
    """
    a = Image.open(io.BytesIO(avant)).convert("RGB")
    b = Image.open(io.BytesIO(apres)).convert("RGB")
    if a.size != b.size:
        return [{"tout": "hauteur de page differente : %s vs %s" % (a.size, b.size)}]
    # Tolerance : un ecart de luminance <= 8/255 est invisible, et le rendu de
    # texte en produit toujours quelques-uns. On seuille l'image de difference
    # avant de chercher les zones, sinon on signale du bruit.
    d = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v > 8 else 0)
    boite = d.getbbox()
    if boite is None:
        return []
    # Regroupe les lignes qui diffèrent en bandes contiguës : plus lisible
    # qu'un rectangle unique qui engloberait tout de haut en bas.
    lignes = [y for y in range(boite[1], boite[3])
              if d.crop((0, y, a.size[0], y + 1)).getbbox() is not None]
    bandes, debut, prec = [], None, None
    for y in lignes:
        if debut is None:
            debut = y
        elif y - prec > 6:
            bandes.append((debut, prec))
            debut = y
        prec = y
    if debut is not None:
        bandes.append((debut, prec))
    out = []
    for y0, y1 in bandes:
        bb = d.crop((0, y0, a.size[0], y1 + 1)).getbbox()
        bande = d.crop((bb[0], y0 + bb[1], bb[2], y0 + bb[3]))
        out.append({"y": [y0 + bb[1], y0 + bb[3]], "x": [bb[0], bb[2]],
                    "px": sum(bande.histogram()[1:])})
    return out


def copie_reference_git(ref, dest):
    """Le site tel qu'il est à `ref`, images comprises."""
    if dest.exists():
        shutil.rmtree(dest)
    # `generer-images.py` écrit ses essais de compression en `<final>.essai` et
    # les efface aussitôt : les copier, c'est courir après un fichier déjà parti.
    shutil.copytree(SITE, dest, ignore=shutil.ignore_patterns("*.essai"))
    suivis = subprocess.run(["git", "ls-tree", "-r", "--name-only", ref, "site/"],
                            cwd=RACINE, capture_output=True, text=True, check=True).stdout.split()
    for chemin in suivis:
        if not chemin.endswith((".html", ".css", ".js", ".webmanifest", ".svg")):
            continue
        blob = subprocess.run(["git", "show", "%s:%s" % (ref, chemin)],
                              cwd=RACINE, capture_output=True, check=True).stdout
        cible = dest / Path(chemin).relative_to("site")
        cible.parent.mkdir(parents=True, exist_ok=True)
        cible.write_bytes(blob)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--figer", action="store_true",
                    help="fige le rendu actuel comme reference (a faire avant d'editer)")
    ap.add_argument("--ref", default=None,
                    help="point git de comparaison, si aucune reference n'est figee")
    ap.add_argument("--pages", default=",".join(PAGES))
    ap.add_argument("--largeurs", default=",".join(str(x) for x in LARGEURS))
    args = ap.parse_args()

    pages = [p for p in args.pages.split(",") if p]
    largeurs = [int(x) for x in args.largeurs.split(",") if x]
    SORTIE.mkdir(exist_ok=True)

    if args.figer:
        if REFERENCE.exists():
            shutil.rmtree(REFERENCE)
        REFERENCE.mkdir(parents=True)
        srv = servir(SITE, 8802)
        with sync_playwright() as p:
            nav = p.chromium.launch()
            for w in largeurs:
                for nom in pages:
                    (REFERENCE / ("%s-%d.png" % (nom, w))).write_bytes(rendre(nav, 8802, nom, w))
                    print("  fige  %-12s %5dpx" % (nom, w))
            nav.close()
        srv.shutdown()
        (REFERENCE / "manifeste.json").write_text(
            json.dumps({"pages": pages, "largeurs": largeurs}, indent=1), encoding="utf-8")
        print("\nReference figee : %d rendus dans %s" % (len(pages) * len(largeurs), REFERENCE))
        return

    figee = (REFERENCE / "manifeste.json").exists() and args.ref is None
    srv_ref = None
    if not figee:
        ref = args.ref or "HEAD"
        print("Pas de reference figee : comparaison contre %s "
              "(le travail d'autrui present dans l'arbre y apparaitra comme un ecart).\n" % ref)
        dossier_ref = SORTIE / "ref-site"
        copie_reference_git(ref, dossier_ref)
        srv_ref = servir(dossier_ref, 8801)

    srv = servir(SITE, 8802)
    ecarts = []
    with sync_playwright() as p:
        nav = p.chromium.launch()
        for w in largeurs:
            for nom in pages:
                apres = rendre(nav, 8802, nom, w)
                if figee:
                    chemin = REFERENCE / ("%s-%d.png" % (nom, w))
                    if not chemin.exists():
                        print("  %-12s %5dpx  (pas dans la reference)" % (nom, w))
                        continue
                    avant = chemin.read_bytes()
                else:
                    avant = rendre(nav, 8801, nom, w)
                bandes = zones(avant, apres)
                if not bandes:
                    print("  %-12s %5dpx  identique" % (nom, w))
                    continue
                ecarts.append((nom, w))
                total = sum(b.get("px", 0) for b in bandes)
                print("  %-12s %5dpx  ECART : %d bande(s), %d px" % (nom, w, len(bandes), total))
                for b in bandes[:6]:
                    if "tout" in b:
                        print("        %s" % b["tout"])
                    else:
                        print("        y %d-%d, x %d-%d, %d px"
                              % (b["y"][0], b["y"][1], b["x"][0], b["x"][1], b["px"]))
                base = SORTIE / ("ecart-%s-%d" % (nom, w))
                base.with_name(base.name + "-avant.png").write_bytes(avant)
                base.with_name(base.name + "-apres.png").write_bytes(apres)
        nav.close()
    srv.shutdown()
    if srv_ref:
        srv_ref.shutdown()

    if ecarts:
        print("\n%d ecart(s). Captures avant/apres dans .audit/ecart-*.png" % len(ecarts))
        sys.exit(1)
    print("\nRendu desktop inchange sur %d page(s) x %d largeur(s)." % (len(pages), len(largeurs)))


if __name__ == "__main__":
    main()
