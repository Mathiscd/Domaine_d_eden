"""Contrôle de bout en bout du formulaire de réservation et des deux emails.

Le script rejoue un séjour et un événement dans un vrai navigateur, capte le
POST réellement émis vers le webhook, puis évalue les expressions ``{{ … }}``
des gabarits de ``docs/emails/`` **dans un moteur JavaScript** — comme le fait
n8n — avant de photographier les quatre combinaisons (deux mails × deux motifs).

Trois choses sont vérifiées d'un coup, et ce sont les trois qui cassent en
silence :

  — les **chemins d'envoi**. En ligne, la demande passe par ``/api/demande``,
    que Netlify relaie vers n8n ; le repli direct ne joue que sur un 404. Un
    repli trop large ferait arriver la demande **deux fois** chez les hôtes ;
  — le **payload**. Une clé renommée dans ``reservation.js`` ne se voit nulle
    part tant qu'un mail ne part pas avec un trou dedans ;
  — les **expressions n8n**. Elles ne sont pas relues par l'éditeur : une
    parenthèse manquante ne se découvre qu'au premier envoi en production.
    Ici, une expression fautive s'imprime en clair dans la sortie.

Les deux adresses de webhook sont détournées vers une URL interceptée : rien ne
sort de la machine, aucun email n'est envoyé, et le vrai workflow n'est jamais
déclenché.

    python tools/verifier-mails.py
    python tools/verifier-mails.py --sortie build/mails
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

RACINE = Path(__file__).resolve().parent.parent
SITE = RACINE / "site"
GABARITS = RACINE / "docs" / "emails"
PORT = 8811
HOOK = "https://webhook.verification.local/eden"
# Faux nom d'hôte résolu vers le serveur local : il met `LOCAL` à false dans
# reservation.js, ce qui est le seul moyen d'éprouver les chemins de production.
FAUX_HOTE = "eden.test"

# Non gourmand : aucune expression des gabarits ne contient « }} ».
EXPR = re.compile(r"\{\{(.+?)\}\}", re.S)

# Les deux constantes d'adresse de reservation.js, détournées le temps du contrôle.
ADRESSE = re.compile(r"\b(var (?:WEBHOOK|WEBHOOK_TEST)) = '[^']*';")

# Les quatre rendus : chaque gabarit avec chacun des deux motifs, pour que les
# branches conditionnelles (estimation, message, téléphone absent) soient toutes
# empruntées au moins une fois.
CAS = (
    ("mail-client.html", "sejour", "client-sejour"),
    ("mail-client.html", "evenement", "client-evenement"),
    ("mail-interne.html", "sejour", "interne-sejour"),
    ("mail-interne.html", "evenement", "interne-evenement"),
)


def cocher(page, selecteur: str):
    """Coche un bouton radio ou une case.

    Les entrées du formulaire sont visuellement masquées derrière leur étiquette :
    un vrai clic atterrit sur la carte, pas sur l'input. On force l'état et on
    émet l'événement, qui est ce que le script du formulaire écoute."""
    page.eval_on_selector(
        selecteur,
        "el => { el.checked = true;"
        " el.dispatchEvent(new Event('change', {bubbles:true})); }")


def rendre(moteur, gabarit: str, payload: dict) -> tuple[str, list[str]]:
    """Remplace chaque ``{{ … }}`` par sa valeur, ``$json`` lié comme dans n8n."""
    moteur.evaluate("d => { window.$json = d; }", {"body": payload})
    morceaux, fautes, pos = [], [], 0
    for m in EXPR.finditer(gabarit):
        morceaux.append(gabarit[pos:m.start()])
        source = m.group(1).strip()
        try:
            morceaux.append(moteur.evaluate(
                "src => { const $json = window.$json;"
                " return String(eval('(' + src + ')')); }", source))
        except Exception as err:  # noqa: BLE001 — on veut TOUTES les fautes, pas la première
            faute = f"{source[:90]} … → {err}"
            fautes.append(faute)
            morceaux.append(f"[[EXPRESSION FAUTIVE : {faute}]]")
        pos = m.end()
    morceaux.append(gabarit[pos:])
    return "".join(morceaux), fautes


def demandes(page) -> dict[str, dict]:
    """Remplit le formulaire deux fois et renvoie les deux payloads captés."""
    recu: dict[str, str] = {}

    def servir_js(route):
        """Détourne les deux constantes vers une URL interceptée.

        On réécrit la déclaration entière plutôt qu'une adresse littérale : le
        contrôle continue de fonctionner le jour où l'instance n8n change de
        nom, et il ne peut pas frapper le vrai webhook par accident."""
        r = route.fetch()
        corps, n = ADRESSE.subn(lambda m: f"{m.group(1)} = '{HOOK}';", r.text())
        if n != 2:
            raise SystemExit(f"reservation.js : {n} constante(s) de webhook trouvée(s), 2 attendues.")
        route.fulfill(response=r, body=corps)

    def capter(route):
        recu["corps"] = route.request.post_data
        route.fulfill(status=200, body='{"ok":true}',
                      headers={"Access-Control-Allow-Origin": "*"})

    page.route("**/reservation.js", servir_js)
    page.route(HOOK.rsplit("/", 1)[0] + "/**", capter)
    base = f"http://localhost:{PORT}/reservation.html"

    # — Un séjour complet : chambre imposée par l'URL, table d'hôtes, enfant,
    #   téléphone, et un message qui porte les caractères qui cassent le HTML.
    page.goto(base + "?chambre=refuge-brumes&utm_source=instagram&utm_medium=bio")
    page.wait_for_timeout(400)
    page.fill("#arrivee", "2026-10-02")
    page.fill("#depart", "2026-10-05")
    page.select_option("#enfants", "1")
    cocher(page, 'input[name="table"][value="oui"]')
    page.click("[data-step='1'] [data-next]")
    page.fill("#prenom", "Camille")
    page.fill("#nom", "Perrin")
    page.fill("#email", "camille.perrin@example.org")
    page.fill("#telephone", "06 12 34 56 78")
    page.fill("#message", "Nous arriverons vers 19 h.\n"
                          "Anniversaire de mariage <10 ans> & une surprise ?")
    page.click("[data-step='2'] [data-next]")
    page.wait_for_timeout(300)
    cocher(page, "#rgpd")
    page.click("button[type=submit]")
    page.wait_for_timeout(900)
    if not page.is_visible("[data-step='4'].is-active"):
        raise SystemExit("Le formulaire n'a pas affiché l'écran de confirmation.")
    sejour = json.loads(recu["corps"])

    # — Un événement dépouillé : ni téléphone, ni message. C'est le cas qui
    #   éprouve les replis des gabarits.
    recu.clear()
    page.goto(base + "?format=mariage")
    page.wait_for_timeout(400)
    page.fill("#date-evenement", "2027-06-12")
    page.fill("#nb-personnes", "24")
    page.click("[data-step='1'] [data-next]")
    page.fill("#prenom", "Léa")
    page.fill("#nom", "Nguyen")
    page.fill("#email", "lea.nguyen@example.org")
    page.click("[data-step='2'] [data-next]")
    page.wait_for_timeout(300)
    cocher(page, "#rgpd")
    page.click("button[type=submit]")
    page.wait_for_timeout(900)
    evenement = json.loads(recu["corps"])

    return {"sejour": sejour, "evenement": evenement}


def chemins(nav) -> list[str]:
    """Éprouve les deux chemins d'envoi en ligne : proxy présent, puis absent.

    En production le formulaire poste sur ``/api/demande``, que Netlify relaie
    vers n8n (cf. ``netlify.toml``) : la requête reste sur le domaine du site,
    hors d'atteinte d'un filtrage d'entreprise qui bloquerait l'instance n8n.
    Le repli direct ne couvre que le 404 — un hébergeur sans redirections.

    Les deux fautes que ce contrôle attrape, et qu'aucune relecture ne voit :
    un repli qui part sur autre chose qu'un 404 (la demande arriverait **deux
    fois** chez les hôtes), et un `LOCAL` mal détecté (le site en ligne taperait
    l'adresse d'essai, qui n'écoute jamais).

    Le faux nom d'hôte est indispensable : sur `localhost`, le script prend
    volontairement l'adresse d'essai et aucun de ces deux chemins n'est
    emprunté."""
    soucis: list[str] = []
    for titre, proxy_repond in (("proxy présent", True), ("proxy absent", False)):
        vus: list[tuple[str, str]] = []
        pg = nav.new_page(viewport={"width": 1280, "height": 900})

        def sur_proxy(route):
            vus.append(("proxy", route.request.post_data_json.get("reference")))
            route.fulfill(status=200, body='{"ok":true}') if proxy_repond \
                else route.fulfill(status=404, body="Not Found")

        def sur_n8n(route):
            vus.append(("n8n-direct", route.request.post_data_json.get("reference")))
            route.fulfill(status=200, body='{"ok":true}',
                          headers={"Access-Control-Allow-Origin": "*"})

        pg.route("**/api/demande", sur_proxy)
        pg.route("https://n8n.srv1107413.hstgr.cloud/**", sur_n8n)
        pg.goto(f"http://{FAUX_HOTE}:{PORT}/reservation.html")
        pg.wait_for_timeout(500)
        pg.fill("#arrivee", "2026-10-02")
        pg.fill("#depart", "2026-10-04")
        pg.click("[data-step='1'] [data-next]")
        pg.fill("#prenom", "Camille")
        pg.fill("#nom", "Perrin")
        pg.fill("#email", "camille.perrin@example.org")
        pg.click("[data-step='2'] [data-next]")
        pg.wait_for_timeout(300)
        cocher(pg, "#rgpd")
        pg.click("button[type=submit]")
        pg.wait_for_timeout(1200)
        confirme = pg.is_visible("[data-step='4'].is-active")
        pg.close()

        empruntes = [v[0] for v in vus]
        attendu = ["proxy"] if proxy_repond else ["proxy", "n8n-direct"]
        if empruntes != attendu:
            soucis.append(f"{titre} : chemins {empruntes}, attendu {attendu}")
        if len({v[1] for v in vus}) != 1:
            soucis.append(f"{titre} : références différentes d'un envoi à l'autre "
                          f"— la demande arriverait en double")
        if not confirme:
            soucis.append(f"{titre} : pas d'écran de confirmation")
        print(f"  {titre:<16} {' → '.join(empruntes)}"
              f"{'' if confirme else '   (PAS DE CONFIRMATION)'}")
    return soucis


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sortie", default=".verif-mails",
                    help="dossier des rendus HTML et PNG (défaut : .verif-mails)")
    args = ap.parse_args()
    sortie = (RACINE / args.sortie).resolve()
    sortie.mkdir(parents=True, exist_ok=True)

    serveur = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT), "-d", "site"],
        cwd=str(RACINE), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    fautes_totales, soucis = 0, []
    try:
        with sync_playwright() as pw:
            nav = pw.chromium.launch(
                args=[f"--host-resolver-rules=MAP {FAUX_HOTE} 127.0.0.1"])
            print("Chemins d'envoi en production :")
            soucis = chemins(nav)
            for x in soucis:
                print(f"  !! {x}")
            page = nav.new_page(viewport={"width": 1280, "height": 900})
            payloads = demandes(page)
            print("Payloads captés :")
            for nom, d in payloads.items():
                print(f"  {nom:<10} {len(json.dumps(d))} octets  ·  {d['reference']}"
                      f"  ·  {len(d['recap'])} lignes de récapitulatif")

            # Le logo des emails est servi par le site local le temps du rendu.
            # En vrai, `public_url` porte le domaine de production : un client
            # mail ne saurait pas atteindre localhost. Ici, c'est justement ce
            # qu'on veut, puisque le rendu se fait dans ce navigateur-ci.
            for d in payloads.values():
                d["public_url"] = f"http://localhost:{PORT}"

            vue = nav.new_page(viewport={"width": 700, "height": 900})
            print("Rendus :")
            for fichier, motif, nom in CAS:
                html, fautes = rendre(page,
                                      (GABARITS / fichier).read_text(encoding="utf-8"),
                                      payloads[motif])
                fautes_totales += len(fautes)
                for f in fautes:
                    print(f"  !! {nom} : {f}")
                page_html = sortie / f"{nom}.html"
                page_html.write_text("<!doctype html><meta charset='utf-8'>" + html,
                                     encoding="utf-8")
                vue.goto(page_html.as_uri())
                vue.wait_for_timeout(500)
                vue.screenshot(path=str(sortie / f"{nom}.png"), full_page=True)
                hauteur = vue.evaluate("document.body.scrollHeight")
                print(f"  {nom:<20} {hauteur} px"
                      f"{'' if not fautes else f'  ({len(fautes)} expression(s) fautive(s))'}")
            nav.close()
    finally:
        serveur.terminate()

    print(f"\n{sortie.relative_to(RACINE) if sortie.is_relative_to(RACINE) else sortie}")
    if fautes_totales or soucis:
        if fautes_totales:
            print(f"ÉCHEC : {fautes_totales} expression(s) n8n fautive(s).")
        if soucis:
            print(f"ÉCHEC : {len(soucis)} anomalie(s) sur les chemins d'envoi.")
        return 1
    print("Chemins d'envoi corrects, et toutes les expressions n8n s'évaluent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
