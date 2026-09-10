# Architecture & contenus — Domaine d'Éden

**Quatre pages.** Le site n'est plus un one-page : l'accueil garde le déroulé complet,
et deux pages dédiées approfondissent l'hébergement et l'événementiel.

| Page | Fichier | Rôle |
|---|---|---|
| Accueil | `index.html` | le déroulé complet, inchangé dans son ordre — c'est la page qui raconte |
| Les chambres | `chambres.html` | les 5 chambres en pleine largeur, ce qui est compris, la table d'hôtes, les salons |
| Événements | `evenements.html` | les 4 formats, le cadre, le déroulé en 4 temps, la formule traiteur |
| Réservation | `reservation.html` | formulaire multi-étapes, cible de tous les CTA |

Navigation commune (deux rangs, cf. charte §6) : Accueil · Le domaine · Les chambres ·
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
6. **L'événementiel** (`#evenements`) — bande sombre : les trois formats de privatisation
   (week-end, midi ou soirée, entreprise) jusqu'à 30 personnes, formule traiteur.
   CTA « Découvrir l'événementiel » (page dédiée) + « Demander un devis ».
7. **Les alentours** (`#alentours`) — Le Puy-en-Velay (17 km), la Via Fluvia à vélo,
   gorges de la Loire / villages, tables locales (La Galoche…).
8. **Galerie** (`#galerie`) — mosaïque 7 photos à placement explicite (4×3, remplissage exact),
   visionneuse plein écran maison (clavier + flèches + Échap).
9. **Thomas Ploton** — bande pleine largeur dont la PHOTO est le fond (les chevaux
   à l'aube, voilée de vert profond), sur le patron de `.final-cta` :
   l'équicoaching à pied, à l'Espace Soreï, au sein du domaine ; **bouton sortant vers
   <https://thomasploton.fr/>** (`target="_blank"`). L'encart porte le nom de la personne
   et non celui du lieu — « Espace Soreï » ne dit rien à qui arrive ici. Rien de plus :
   le contenu de son site ne se réintègre pas ici.
10. **Contact & accès** (`#contact`) — adresse, tel, mail, horaires arrivée/départ,
   carte (lien Google Maps, pas d'iframe lourde), CTA final pleine largeur
   « Composer votre séjour ».
11. **Footer** — encre : logo, nav (4 pages), coordonnées, réseaux (pictogrammes FB/IG),
    mentions légales, crédit MarketFrame.

## chambres.html — l'hébergement en détail

1. **Bandeau de titre** — photo chambre, fil d'Ariane, « Cinq chambres, *cinq univers* ».
2. **Ce qui est compris** — 3 faits : 90 — 104 € la nuit petit-déjeuner compris ·
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
2. **Un décor d'exception** — éditorial, texte du client : le charme du château, chaque
   moment son ambiance, et les proches qui dorment sur place.
3. **Les trois formats** — découpés **par durée de privatisation**, à la demande du
   client, et non plus par type d'événement : *un week-end entier* (mariages & grandes
   réceptions) · *un midi ou une soirée* (anniversaires, cousinades, baptêmes) ·
   *le format entreprise* (soirée en semaine, journée de formation, séminaire
   résidentiel). Les trois sont des privatisations : le domaine entier, un seul
   événement à la fois. Chaque carte porte 3 repères concrets et mène à
   `reservation.html?motif=evenement&format=<mariage|cousinade|seminaire>` — les
   `data-slug` du select n'ont pas changé.
   Après la grille, **bande de partenariat Thomas Ploton** (prolongement de la carte
   entreprise) : l'équicoaching en équipe, lien sortant vers <https://thomasploton.fr/>.
   Elle est hors de la section des formats — le lien de titre des cartes s'étend en
   `::after` sur toute leur surface, un lien imbriqué y serait mort.
4. **La promesse** (`quote-band`) — « vous ne venez pas simplement louer un espace ».
5. **Le cadre** (bande sombre) — 30 personnes reçues · 5 chambres sur place ·
   1 événement à la fois.
6. **Comment ça se passe** — 4 temps : votre message → la visite → le devis → le jour J.
7. **À table** — formule traiteur simple (planches, produits locaux), traiteur extérieur
   possible. La table d'hôtes à 25 €/pers. reste l'affaire des chambres : en
   réception, on parle de service traiteur.
8. **CTA final** — « Imaginez votre événement *au château* », « Demander un devis »
   → `reservation.html?motif=evenement`.

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
- Thomas Ploton (Espace Soreï, au sein du domaine) : ploton.thomas@gmail.com,
  06 65 32 92 61 — site propre : <https://thomasploton.fr/>. Équicoaching à pied :
  séances individuelles (Équi Émotion, 90 €), constellations familiales avec les chevaux
  (Équanima, soirées), parcours Renaissance, soins énergétiques, et formats en équipe.
  Aucun prérequis équestre. La photo de fond de l'encart (`chevaux-aube`) vient de son
  site — c'est la seule source disponible, 1600 px.
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
| chambre-chateau.jpg | la chambre bleue toile de Jouy (gdf-0), seule photographiée par les Gîtes de France | décor : fond du hero de chambres.html, tuile de la galerie de l'accueil |
| chambre-`<nom>`-alt / -sdb.jpg | les cinq chambres réelles + leur salle de bains, captures Booking (~930px, sources PNG) | blocs de chambres.html et cartes de la réservation |
| salon.jpg / salon-piano.jpg | salons moulures & poutres (gdf-5/6) | chambres/galerie |
| salle-a-manger.jpg / table-hotes.jpg | salle à manger (gdf-8/9) | table d'hôtes |
| cuisine.jpg (gdf-7), salle-bain.jpg (gdf-4) | annexes | galerie si besoin |
