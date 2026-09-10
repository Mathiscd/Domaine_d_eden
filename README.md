# Domaine d'Éden — Château les Tourelles

Site de la maison d'hôtes et lieu événementiel du **Domaine d'Éden**, à Beaulieu
(Haute-Loire). Statique : HTML, CSS et JavaScript écrits à la main, **sans
framework et sans étape de build**. Le dossier `site/` *est* le site livré.

## Regarder le site

```
python -m http.server 8000 --directory site
```

puis <http://localhost:8000>. Les pages s'ouvrent aussi en `file://` — seul le
formulaire de réservation a besoin d'un vrai serveur.

## Ce qu'il y a dans le dépôt

| | |
|---|---|
| `site/` | le site publié : six pages, un CSS, deux JS, les polices et les images |
| `photos-sources/` | les photos d'origine et le logo du client — versionnés, jamais publiés |
| `tools/` | utilitaires de maintenance en Python, lancés à la main, jamais dans un build |
| `docs/` | charte graphique, architecture des pages, contrat du webhook, gabarits d'emails |

## Maintenance

Les scripts de `tools/` ne tournent que lorsqu'on touche aux images, au logo ou
au formulaire. Ils demandent `pillow`, `numpy`, `scikit-image` et `playwright`
selon le cas ; chacun explique son rôle en tête de fichier.

```
python tools/generer-images.py --ecrire   # variantes AVIF/WebP/JPEG des photos
python tools/verifier-srcset.py           # le balisage déclare-t-il tout ce qui existe
python tools/verifier-sizes.py            # les `sizes` collent-ils au rendu réel
python tools/verifier-mails.py            # le formulaire et les deux emails, de bout en bout
```

## Mise en ligne

Netlify publie `site/`. `netlify.toml` relaie en plus `/api/demande` vers le
webhook n8n qui traite les demandes de réservation, pour que le formulaire ne
sorte jamais du domaine du site.

---

Les règles du projet — design, contenus, pièges à ne pas « nettoyer » — sont
dans [CLAUDE.md](CLAUDE.md) et [docs/](docs/).
