# Architecture & contenus — Domaine d'Éden

**Quatre pages.** Le site n'est plus un one-page : l'accueil garde le déroulé complet,
et deux pages dédiées approfondissent l'hébergement et l'événementiel.

| Page | Fichier | Rôle |
|---|---|---|
| Accueil | `index.html` | le déroulé complet, inchangé dans son ordre — c'est la page qui raconte |
| Les chambres | `chambres.html` | les 5 chambres en pleine largeur, ce qui est compris, la table d'hôtes, les salons |
| Événements | `evenements.html` | les 4 formats, le cadre, le déroulé en 4 temps, la formule traiteur |
| Réservation | `reservation.html` | formulaire multi-étapes, cible de tous les CTA |

Navigation commune (deux rangs, cf. charte §5) : Accueil · Le domaine · Les chambres ·
Événements · Galerie · Contact + bouton « Réserver ». Depuis les pages intérieures,
« Le domaine », « Galerie » et « Contact » pointent vers les ancres de `index.html`.

Tous les CTA convergent vers `reservation.html` — avec paramètre d'URL quand le contexte
le permet : `?chambre=boudoir-reves` depuis une chambre, `?motif=evenement` depuis
l'événementiel.

## index.html — le déroulé (ordre validé par la proposition)

1. **Hero** — plein écran, **diaporama de 5 vues du domaine** en fondu enchaîné
   (façade, allée, cour-jardin, salon de musique, tour), voile sombre dégradé,
   repères cliquables en bas à droite.
   Eyebrow : « Beaulieu · Haute-Loire · Auvergne ». H1 : « Domaine d'Éden ».
   Sous-titre serif italique : « Un château pour rêver, un domaine pour se ressourcer. »
   CTA primaire → réservation ; CTA ghost tel : 06 65 32 92 61. Flèche scroll discrète.
2. **L'esprit des lieux** (`#domaine`) — éditorial asymétrique : collage 2 photos
   (jardin + cour) / texte : le domaine, l'arrivée par l'allée, la reconnexion à
   l'essentiel. Mention Via Fluvia (accueil cyclistes). Signature « Grégory & Thomas ».
3. **Les hôtes** — bande courte : leur histoire (Parisiens installés en Auvergne),
   les deux cockers et les chats, note Booking « Personnel 9,8/10 » en preuve discrète.
4. **Bandeau défilant** — bande pleine largeur vert foncé, vocabulaire sensoriel en
   Cormorant italique (« Pierre & lumière · Feux de bois · Silence du parc… »).
   Décoratif (`aria-hidden`), il sert de respiration colorée entre les hôtes et les chambres.
5. **Les chambres** (`#chambres`) — intro + 5 cartes + la carte « salons ».
   Chaque carte **renvoie vers son ancre dans `chambres.html`** (`#boudoir-reves`…).
   Sous la grille : deux CTA — « Visiter les cinq chambres » (page dédiée) et
   « Composer votre séjour » (réservation) — puis l'encart **table d'hôtes**
   (25 €/pers, sur réservation 24–48 h) + **gîte 2–4 personnes à venir en 2027**.
6. **L'événementiel** (`#evenements`) — bande sombre : mariages intimistes, cousinades,
   séminaires, privatisation jusqu'à 30 personnes, formule traiteur.
   CTA « Découvrir l'événementiel » (page dédiée) + « Demander un devis ».
7. **Les alentours** (`#alentours`) — Le Puy-en-Velay (17 km), la Via Fluvia à vélo,
   gorges de la Loire / villages, tables locales (La Galoche…).
8. **Galerie** (`#galerie`) — mosaïque 7 photos à placement explicite (4×3, remplissage exact),
   visionneuse plein écran maison (clavier + flèches + Échap).
9. **Espace Soreï** — encart vert : centre de médiation équine et d'accompagnement au
   sein du domaine ; **bouton sortant vers <https://thomasploton.fr/>** (`target="_blank"`).
   Rien de plus : le contenu du site Soreï ne se réintègre pas ici.
10. **Contact & accès** (`#contact`) — adresse, tel, mail, horaires arrivée/départ,
   carte (lien Google Maps, pas d'iframe lourde), CTA final pleine largeur
   « Composer votre séjour ».
11. **Footer** — encre : logo, nav (4 pages), coordonnées, réseaux (pictogrammes FB/IG),
    mentions légales, crédit MarketFrame.

## chambres.html — l'hébergement en détail

1. **Bandeau de titre** — photo chambre, fil d'Ariane, « Cinq chambres, *cinq univers* ».
2. **Ce qui est compris** — 3 faits : 90–99 € la nuit petit-déjeuner compris ·
   arrivées 16 h–20 h / départs 9 h–10 h · parking, abri vélos, salons, animaux.
3. **Les cinq chambres** — un bloc pleine largeur par chambre, grille alternée,
   ancre par chambre (`#suite-roi-reine`, `#antichambre-nuit`, `#boudoir-reves`,
   `#refuge-brumes`, `#repaire-songes`), spécifications, prix, CTA
   « Demander cette chambre » → `reservation.html?chambre=<slug>`.
4. **Table d'hôtes** — encart repris de l'accueil (25 €/pers) + badge gîte 2027.
5. **Les espaces communs** — éditorial salons + piano, lien vers la galerie de l'accueil.
6. **CTA final** — « Demander une disponibilité ».

## evenements.html — l'événementiel en détail

1. **Bandeau de titre** — « Vos plus beaux jours, *entre parc et tourelles* ».
2. **Recevoir ici** — éditorial : un seul événement à la fois, le domaine entier.
3. **Les quatre formats** — mariages intimistes · cousinades & anniversaires ·
   séminaires & journées d'équipe · privatisation complète. Chaque carte porte
   3 repères concrets (capacité, durée, inclus).
4. **Le cadre** (bande sombre) — 30 personnes reçues · 5 chambres sur place ·
   1 événement à la fois.
5. **Comment ça se passe** — 4 temps : votre message → la visite → le devis → le jour J.
6. **À table** — formule traiteur simple (planches, produits locaux), traiteur extérieur
   possible ; badge table d'hôtes 25 €/pers.
7. **CTA final** — « Demander un devis » → `reservation.html?motif=evenement`.

## reservation.html — formulaire multi-étapes

Page calme : photo en bandeau étroit ou colonne, formulaire au centre, header réduit
avec retour au site. **3 étapes**, barre de progression fine :

1. **Votre séjour** — motif (Séjour chambre d'hôtes / Événement ou groupe), si chambre :
   choix de la chambre (cartes radio avec miniature, option « Peu importe / conseillez-moi »),
   dates arrivée/départ (natifs `type=date`), nb adultes/enfants, table d'hôtes (oui/non),
   si événement : type (mariage, séminaire, cousinade…), nb personnes (jusqu'à 30), date envisagée.
2. **Vos coordonnées** — prénom, nom, email, téléphone, message libre facultatif
   (« demandes particulières, heure d'arrivée… »).
3. **Récapitulatif** — relecture élégante (liste dotée façon menu), consentement RGPD,
   bouton « Envoyer la demande ».

Après envoi : écran de confirmation (« Votre demande est entre nos mains — réponse sous
24 h ») rappelant le téléphone. Envoi réel à brancher dans `submitRequest()`
(Formspree/Brevo → boîte mail du client + auto-réponse, cf. proposition).

Validation inline (dates cohérentes, email), navigation Précédent/Suivant, état conservé
si retour en arrière. Paramètres d'URL : `?chambre=boudoir-des-reves` et `?motif=evenement`
pré-remplissent l'étape 1.

## Données de référence

- Adresse : 2562 Avenue de Bazac, 43800 Beaulieu (lieu-dit Adiac) — Haute-Loire.
- Tél : 06 65 32 92 61 · Mail : chateaulestourelles43@gmail.com
- Arrivée 16 h–20 h · Départ 9 h–10 h · Animaux admis sur demande · Parking privé gratuit.
- Notes Booking (preuve sociale, usage discret) : 8,8/10 « Superbe », Personnel 9,8.
- Espace Soreï : espacesorei43@gmail.com — site propre : <https://thomasploton.fr/>.
- Réseaux sociaux : comptes Facebook et Instagram existants — **URL exactes à fournir par
  le client** ; en attendant, les pictogrammes du header et du footer pointent vers
  l'accueil des deux plateformes (`parts` du générateur → constantes `FB` / `IG`).

## Mapping photos (assets/img)

| Fichier | Contenu | Usage |
|---|---|---|
| hero-chateau.jpg | façade + tourelle, ciel bleu (gdf-11) | 1re vue du diaporama du hero |
| chateau-angle.jpg | château angle allée (gdf-12) | esprit des lieux / événementiel |
| chateau-tour.jpg | tour côté jardin (gdf-10) | galerie / alentours |
| cour-roues.jpg | mur de la cour, roues de charrette (gdf-13) | collage esprit des lieux |
| jardin.jpg | cour jardin arbustes (gdf-14) | collage esprit des lieux |
| chambre-*.jpg | chambre bleue toile de Jouy, 4 angles (gdf-0/1/2/3) | cartes chambres + blocs de chambres.html (provisoire) |
| salon.jpg / salon-piano.jpg | salons moulures & poutres (gdf-5/6) | chambres/galerie |
| salle-a-manger.jpg / table-hotes.jpg | salle à manger (gdf-8/9) | table d'hôtes |
| cuisine.jpg (gdf-7), salle-bain.jpg (gdf-4) | annexes | galerie si besoin |
