# -*- coding: utf-8 -*-
"""Confronte les attributs `sizes` du balisage aux largeurs réellement rendues.

Ce n'est PAS une étape de build : c'est un contrôle de maintenance, à relancer
après toute retouche de la mise en page — ce sont les breakpoints du CSS qui
déterminent la largeur à laquelle chaque image est affichée, donc la valeur que
`sizes` doit annoncer.

    python -m http.server 8899 --directory site &
    python tools/verifier-sizes.py

L'enjeu : `sizes` dit au navigateur quelle largeur l'image occupera, et c'est sur
cette annonce qu'il choisit la variante du srcset — avant tout calcul de mise en
page. Sous-estimer sert une image trop petite, étirée donc floue (le double sur
un écran DPR 2) ; sur-estimer fait télécharger des pixels jamais affichés. Aucune
des deux erreurs n'est visible dans le HTML : il faut mesurer le rendu.

La largeur est relevée à chaque breakpoint du CSS (1024 / 940 / 900 / 640, plus
390 et 1440 comme bornes), après défilement complet pour que les images en
`loading="lazy"` soient posées. On signale un écart au-delà de 8 % : en deçà,
changer de variante ne changerait de toute façon pas le fichier retenu.

Dépendance (outil local uniquement, rien n'est livré au site) :
    pip install playwright && playwright install chromium
"""
import argparse, collections, re, sys

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit('Il manque Playwright : pip install playwright && playwright install chromium')

PAGES = ['index.html', 'chambres.html', 'evenements.html', 'reservation.html']

# Les breakpoints du CSS, plus les deux bornes de la fourchette d'usage. Une
# largeur juste au-dessus et au-dessous de chaque bascule révèle les erreurs de
# borne (`min-width: 901px` qui aurait dû être 900, typiquement).
LARGEURS = [390, 639, 641, 899, 901, 939, 941, 1023, 1025, 1440]

ECART_TOLERE = 0.08   # 8 % : en deçà, le srcset retiendrait la même variante


def decouper(sizes):
    """Découpe la liste `sizes` sur les virgules de premier niveau.

    Un simple split(',') couperait `min(78vw, 320px)` en deux moitiés
    inexploitables : on ne coupe qu'en dehors des parenthèses.
    """
    clauses, profondeur, courant = [], 0, ''
    for c in sizes:
        if c == '(':
            profondeur += 1
        elif c == ')':
            profondeur -= 1
        if c == ',' and profondeur == 0:
            clauses.append(courant.strip())
            courant = ''
        else:
            courant += c
    if courant.strip():
        clauses.append(courant.strip())
    return clauses


def sizes_annonce(sizes, viewport):
    """Ce que le navigateur retient de l'attribut `sizes` à ce viewport.

    Première clause dont la media query est vraie, comme le fait le navigateur ;
    la dernière valeur, sans condition, sert de repli.
    """
    for clause in decouper(sizes):
        mq = re.match(r'\((?:min-width):\s*(\d+)px\)\s+(.+)', clause)
        if mq:
            if viewport >= int(mq.group(1)):
                return valeur_px(mq.group(2), viewport)
        elif clause:
            return valeur_px(clause, viewport)
    return None


def valeur_px(v, viewport):
    """Résout une longueur CSS en pixels, y compris `min()` / `max()`.

    Le balisage s'en sert pour brider une largeur relative (`min(78vw, 320px)` :
    78 % du viewport, mais jamais plus de 320 px).
    """
    v = v.strip()
    fn = re.match(r'(min|max)\(\s*(.+?)\s*\)$', v)
    if fn:
        membres = [valeur_px(m, viewport) for m in fn.group(2).split(',')]
        membres = [m for m in membres if m is not None]
        if not membres:
            return None
        return min(membres) if fn.group(1) == 'min' else max(membres)
    if v.endswith('vw'):
        return viewport * float(v[:-2]) / 100
    if v.endswith('px'):
        return float(v[:-2])
    return None


def releve(page, url, viewport):
    page.set_viewport_size({'width': viewport, 'height': 900})
    page.goto(url, wait_until='load')
    # les images en lazy ne sont posées qu'une fois traversées
    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    page.wait_for_timeout(700)
    page.evaluate('window.scrollTo(0, 0)')
    page.wait_for_timeout(200)
    return page.evaluate("""() => [...document.images].map(i => ({
        src: i.getAttribute('src') || '',
        sizes: i.getAttribute('sizes') || '',
        rendu: Math.round(i.getBoundingClientRect().width),
    })).filter(x => x.rendu > 0 && x.sizes)""")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', default='http://localhost:8899',
                    help='racine du serveur de test (défaut : %(default)s)')
    args = ap.parse_args()

    ecarts = collections.defaultdict(list)

    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        ctx = nav.new_context(viewport={'width': 1440, 'height': 900})
        page = ctx.new_page()
        for nom in PAGES:
            for vp in LARGEURS:
                try:
                    images = releve(page, '%s/%s' % (args.base, nom), vp)
                except Exception as e:
                    sys.exit('Impossible de charger %s (serveur lancé ?) : %s' % (nom, e))
                for img in images:
                    annonce = sizes_annonce(img['sizes'], vp)
                    if not annonce:
                        continue
                    rendu = img['rendu']
                    if rendu and abs(annonce - rendu) / rendu > ECART_TOLERE:
                        base = re.sub(r'-\d+\.\w+$', '', img['src'].split('/')[-1])
                        ecarts[(nom, base)].append((vp, rendu, annonce, img['sizes']))
        nav.close()

    if not ecarts:
        print('Aucun écart : tous les `sizes` correspondent au rendu.')
        return 0

    print('Écarts au-delà de %d %% entre `sizes` et largeur rendue :\n' % (ECART_TOLERE * 100))
    for (nom, base), lignes in sorted(ecarts.items()):
        print('%s — %s' % (nom, base))
        for vp, rendu, annonce, _ in lignes:
            sens = 'sous-estime' if annonce < rendu else 'sur-estime'
            print('   viewport %4d : rendu %4d px, annoncé %4.0f px  (%s de %+.0f %%)'
                  % (vp, rendu, annonce, sens, 100 * (annonce - rendu) / rendu))
        print('   sizes actuel : %s\n' % lignes[0][3])
    return 1


if __name__ == '__main__':
    sys.exit(main())
