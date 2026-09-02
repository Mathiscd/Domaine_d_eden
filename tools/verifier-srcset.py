# -*- coding: utf-8 -*-
"""Contrôle que le balisage <picture> et le dossier d'images restent d'accord.

À relancer après tout passage de `generer-images.py` : c'est le décalage que ce
script attrape qui avait fait servir un 2000 px à un mobile en DPR 3, faute d'un
palier 1250 pourtant présent sur le disque.

    python tools/verifier-srcset.py

Trois vérifications, dans cet ordre :

1. **Fichier manquant** — un srcset qui pointe sur une variante absente. Erreur.
2. **Variante oubliée** — une variante existe sur le disque, pourrait entrer dans
   le srcset sans casser la monotonie, mais n'y est pas déclarée. Erreur : c'est
   un trou de résolution, le navigateur devra prendre la largeur au-dessus.
3. **Monotonie** — dans un srcset, le poids doit croître avec la largeur. Sinon
   le navigateur télécharge plus d'octets pour moins de pixels. Erreur.

Une variante plus lourde que la largeur au-dessus est légitimement absente du
balisage (`generer-images.py` l'élague) : le point 2 ne la réclame donc pas.
"""
import os, re, sys, glob
from collections import defaultdict

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(RACINE, 'site', '*.html')
IMAGES = os.path.join(RACINE, 'site', 'assets', 'img')

MOTIF_SRCSET = re.compile(r'((?:data-|image)?srcset)="([^"]+)"')
MOTIF_ENTREE = re.compile(r'assets/img/([^\s/]+)-(\d+)\.(avif|webp|jpg)\s+(\d+)w')
MOTIF_FICHIER = re.compile(r'(.+)-(\d+)\.(avif|webp|jpg)$')


def poids_disponibles():
    """{(nom, format): {largeur: poids}} pour tout ce qui est sur le disque."""
    d = defaultdict(dict)
    for chemin in glob.glob(os.path.join(IMAGES, '*')):
        m = MOTIF_FICHIER.match(os.path.basename(chemin))
        if m:
            d[(m.group(1), m.group(3))][int(m.group(2))] = os.path.getsize(chemin)
    return d


def croissant(largeurs, poids):
    """Le poids croît-il strictement avec la largeur ?"""
    connues = [w for w in largeurs if w in poids]
    return all(poids[a] < poids[b] for a, b in zip(connues, connues[1:]))


def main():
    dispo = poids_disponibles()
    erreurs = []
    nb = 0

    for page in sorted(glob.glob(PAGES)):
        html = open(page, encoding='utf-8').read()
        nom_page = os.path.basename(page)

        for attr, valeur in MOTIF_SRCSET.findall(html):
            entrees = MOTIF_ENTREE.findall(valeur)
            if not entrees:
                continue
            nb += 1
            nom, fmt = entrees[0][0], entrees[0][2]
            declarees = sorted({int(e[1]) for e in entrees})
            poids = dispo.get((nom, fmt), {})

            # 1. le descripteur doit correspondre à la largeur du nom de fichier
            for base, larg, ext, desc in entrees:
                if larg != desc:
                    erreurs.append(f'{nom_page}: {base}-{larg}.{ext} déclaré {desc}w')
                if not os.path.exists(os.path.join(IMAGES, f'{base}-{larg}.{ext}')):
                    erreurs.append(f'{nom_page}: {base}-{larg}.{ext} absent du disque')

            # 2. une variante ajoutable sans casser la monotonie doit être déclarée
            for w in sorted(set(poids) - set(declarees)):
                if croissant(sorted(declarees + [w]), poids):
                    erreurs.append(
                        f'{nom_page}: {nom}-{w}.{fmt} existe et tiendrait dans le '
                        f'srcset (déclaré : {declarees})')

            # 3. monotonie de ce qui est déclaré
            if not croissant(declarees, poids):
                erreurs.append(f'{nom_page}: {nom} [{fmt}] srcset non monotone {declarees}')

    print(f'{nb} srcset contrôlés dans {len(glob.glob(PAGES))} pages.')
    if erreurs:
        print(f'\n{len(erreurs)} problème(s) :')
        for e in erreurs:
            print(f'  - {e}')
        return 1
    print('Tout est cohérent : aucun trou de résolution, aucune variante fantôme.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
