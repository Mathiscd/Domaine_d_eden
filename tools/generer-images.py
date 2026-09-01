# -*- coding: utf-8 -*-
"""Génère le jeu d'images responsives du site à partir des photos sources.

Ce n'est PAS une étape de build : le site reste statique et ouvrable en file://.
C'est un utilitaire de maintenance, à relancer à la main le jour où le client
fournit de nouvelles photos.

    python tools/generer-images.py            # simulation, n'écrit rien
    python tools/generer-images.py --ecrire   # produit les fichiers

Pour chaque photo il produit, à plusieurs largeurs, un AVIF, un WebP et un JPEG
nommés `<nom>-<largeur>.<ext>` dans site/assets/img/. Le balisage <picture> des
pages pointe sur ces noms : voir la section « Images » du CLAUDE.md.

Principe : la qualité n'est pas choisie à la main mais **cherchée par bissection**,
séparément pour chaque image, chaque largeur et chaque format — la plus basse qui
tienne encore le plancher de fidélité. Une photo de ciel uni et un intérieur sombre
n'ont pas besoin du même réglage, et une valeur fixe gaspille sur l'une ou abîme
l'autre. La fidélité se mesure en SSIM contre le rééchantillonnage LANCZOS de la
source, jamais contre un JPEG déjà compressé (sinon on dépense des bits à
reproduire les artefacts du fichier intermédiaire).

Dépendances (outil local uniquement, rien n'est livré au site) :
    pip install pillow numpy scikit-image
"""
import argparse, io, json, os, sys

try:
    import numpy as np
    from PIL import Image, ImageFilter
    from skimage.metrics import structural_similarity
except ImportError:
    sys.exit('Il manque des dépendances : pip install pillow numpy scikit-image')

SOURCES = 'photos-sources'
SORTIE = 'site/assets/img'

# Quelle source alimente quel nom d'image du site. Deux noms peuvent pointer sur
# la même photo : une seule chambre a été photographiée pour l'instant.
#
# Les chambres sont illustrées par les captures Booking (plus bas), seules à
# montrer les cinq pièces distinctes. Les vues Gîtes de France ne servent donc
# que le château, les salons et le jardin — plus `chambre-brumes` et
# `chambre-suite`, gardées pour les bandeaux de chambres.html.
CORRESPONDANCE = {
    'chambre-brumes':  'gdf-0.jpg',   'chambre-suite':  'gdf-0.jpg',
    'chateau-angle':   'gdf-12.jpg',  'chateau-tour':   'gdf-10.jpg',
    'cour-roues':      'gdf-13.jpg',  'hero-chateau':   'gdf-11.jpg',
    'jardin':          'gdf-14.jpg',  'salle-a-manger': 'gdf-8.jpg',
    'salon':           'gdf-5.jpg',   'salon-piano':    'gdf-6.jpg',
    'table-hotes':     'gdf-9.jpg',

    # Deuxième vue (chambre) + salle de bains, une paire par chambre — issues des
    # captures Booking fournies par le client (photos-sources/Chambres/), bien plus
    # petites que les gdf-*.jpg : leur srcset s'arrête donc plus tôt.
    'chambre-suite-alt':   'chambre-suite-alt.jpg',
    'chambre-suite-sdb':   'chambre-suite-sdb.jpg',
    'chambre-nuit-alt':    'chambre-nuit-alt.jpg',
    'chambre-nuit-sdb':    'chambre-nuit-sdb.jpg',
    'chambre-boudoir-alt': 'chambre-boudoir-alt.jpg',
    'chambre-boudoir-sdb': 'chambre-boudoir-sdb.jpg',
    'chambre-brumes-alt':  'chambre-brumes-alt.jpg',
    'chambre-brumes-sdb':  'chambre-brumes-sdb.jpg',
    'chambre-songes-alt':  'chambre-songes-alt.jpg',
    'chambre-songes-sdb':  'chambre-songes-sdb.jpg',
}

# 1500 et 2000 servent les écrans à haute densité (DPR 2), où une carte de
# 360 px CSS réclame 720 px réels et le bandeau pleine largeur bien davantage.
LARGEURS = [240, 480, 768, 1100, 1500, 2000]

# 0,97 partout, sauf en 240 px : cette largeur ne sert qu'aux vignettes affichées
# en 78 px, où l'écart avec la source est invisible.
PLANCHER = 0.97
PLANCHER_VIGNETTE = 0.95
LARGEUR_VIGNETTE = 240

PLAGES = {'avif': (30, 95), 'webp': (40, 98), 'jpeg': (40, 98)}
EXT = {'avif': 'avif', 'webp': 'webp', 'jpeg': 'jpg'}


def reechantillonner(im, w, h):
    """Réduit en LANCZOS puis rend le micro-contraste perdu par la réduction.

    Toute réduction agit comme un passe-bas : les arêtes qui tenaient sur un
    pixel dans la source s'étalent, et l'image paraît molle même quand aucune
    information n'a été « perdue » au sens strict. Un unsharp mask de rayon
    inférieur au pixel rétablit ce micro-contraste sans halo visible.

    Volontairement discret (seuil 3 : le bruit et les aplats de ciel ne sont pas
    touchés). Monter `percent` produirait des liserés sur les arêtes contrastées
    — les encadrements de fenêtre sur le ciel, typiquement.

    L'accentuation est appliquée AVANT la mesure SSIM, donc la référence de
    fidélité est bien l'image accentuée : la bissection de qualité continue de
    mesurer le seul coût de la compression, pas celui de l'accentuation.
    """
    reduit = im.resize((w, h), Image.LANCZOS)
    return reduit.filter(ImageFilter.UnsharpMask(radius=0.6, percent=55, threshold=3))


def ssim(a, b):
    """SSIM canonique (fenêtre gaussienne 11x11, sigma 1,5), sur les trois canaux."""
    return structural_similarity(a, b, channel_axis=2, data_range=255.0,
                                 gaussian_weights=True, sigma=1.5,
                                 use_sample_covariance=False)


def enregistrer(img, fmt, q, chemin):
    opts = {'quality': q}
    if fmt == 'jpeg':
        opts.update(optimize=True, progressive=True)
    elif fmt == 'webp':
        opts.update(method=6)          # effort maximal
    elif fmt == 'avif':
        # speed=4 et non le défaut 6 de Pillow : ~3 % de moins à qualité égale
        # pour 0,5 s de plus par image. speed=0 ne gagne que 2 % de plus mais
        # coûte sept fois le temps. Ne pas changer sans régénérer tout le jeu :
        # les fichiers livrés ont été produits avec cette valeur.
        opts.update(speed=4)
    img.save(chemin, 'JPEG' if fmt == 'jpeg' else EXT[fmt].upper(), **opts)


def meilleure_qualite(ref, ref_arr, fmt, plancher, essai):
    """Plus basse qualité qui atteigne encore le plancher, par bissection."""
    lo, hi = PLAGES[fmt]
    trouve = None
    while lo <= hi:
        mid = (lo + hi) // 2
        enregistrer(ref, fmt, mid, essai)
        with Image.open(essai) as im:
            arr = np.asarray(im.convert('RGB'), dtype=np.float64)
        if ssim(ref_arr, arr) >= plancher:
            trouve, hi = mid, mid - 1
        else:
            lo = mid + 1
    return trouve


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ecrire', action='store_true', help='écrit vraiment les fichiers')
    ap.add_argument('--manifeste', default='', help='chemin où déposer un manifeste JSON')
    args = ap.parse_args()

    if not os.path.isdir(SOURCES):
        sys.exit('Dossier introuvable : %s (lancer depuis la racine du dépôt)' % SOURCES)

    manifeste, total = {}, 0
    for nom in sorted(CORRESPONDANCE):
        src = os.path.join(SOURCES, CORRESPONDANCE[nom])
        if not os.path.exists(src):
            print('  ABSENTE  %-16s -> %s' % (nom, src))
            continue
        with Image.open(src) as im:
            im = im.convert('RGB')
            larg_src, haut_src = im.size
            sortie = []
            # jamais d'agrandissement : on s'arrête à la définition de la source
            largeurs = [w for w in LARGEURS if w < larg_src] + [larg_src]
            for w in largeurs:
                h = max(1, int(round(w * haut_src / float(larg_src))))
                ref = reechantillonner(im, w, h) if w < larg_src else im
                ref_arr = np.asarray(ref, dtype=np.float64)
                plancher = PLANCHER_VIGNETTE if w == LARGEUR_VIGNETTE else PLANCHER
                for fmt in ('avif', 'webp', 'jpeg'):
                    final = os.path.join(SORTIE, '%s-%d.%s' % (nom, w, EXT[fmt]))
                    essai = final + '.essai'
                    q = meilleure_qualite(ref, ref_arr, fmt, plancher, essai)
                    if q is None:
                        print('  !! %s %dpx %s : plancher %.3f hors d\'atteinte' % (nom, w, fmt, plancher))
                        os.path.exists(essai) and os.remove(essai)
                        continue
                    enregistrer(ref, fmt, q, essai)
                    taille = os.path.getsize(essai)
                    if args.ecrire:
                        os.replace(essai, final)
                    else:
                        os.remove(essai)
                    sortie.append({'format': fmt, 'width': w, 'height': h,
                                   'bytes': taille, 'quality': q,
                                   'path': 'assets/img/%s-%d.%s' % (nom, w, EXT[fmt])})
                    total += taille

        # Une variante plus lourde qu'une plus grande n'a rien à faire dans un
        # srcset : le navigateur téléchargerait plus d'octets pour moins de pixels.
        # On élague format par format, chacun ayant son propre <source>.
        for fmt in ('avif', 'webp', 'jpeg'):
            lst = sorted([v for v in sortie if v['format'] == fmt], key=lambda v: v['width'])
            for i, v in enumerate(lst[:-1]):
                if any(p['bytes'] <= v['bytes'] for p in lst[i + 1:]):
                    sortie.remove(v)
                    print('  élaguée  %s-%d.%s (plus lourde qu\'une plus grande)'
                          % (nom, v['width'], EXT[fmt]))
        manifeste[nom] = {'source': src, 'width': larg_src, 'height': haut_src,
                          'variants': sortie}
        print('  %-16s %d largeurs, %4.0f Ko' %
              (nom, len(largeurs), sum(v['bytes'] for v in sortie) / 1024.0))

    print('\ntotal : %.1f Mo%s' % (total / 1048576.0, '' if args.ecrire else '  (simulation)'))
    if args.manifeste:
        io.open(args.manifeste, 'w', encoding='utf-8').write(
            json.dumps(manifeste, indent=1, ensure_ascii=False))
        print('manifeste : ' + args.manifeste)
    if not args.ecrire:
        print('Relancer avec --ecrire pour produire les fichiers.')
    print('\nPenser ensuite à mettre à jour les srcset/sizes des <picture> si les '
          'largeurs ont changé, puis à vérifier sous Playwright.')


if __name__ == '__main__':
    main()
