# Architecture & contenus — Domaine d'Éden

Deux pages. Tous les CTA de `index.html` pointent vers `reservation.html`
(sauf « Événementiel » et « Écrivez-nous » qui pré-sélectionnent le motif dans le formulaire
via paramètre d'URL `?motif=evenement`).

## index.html — le déroulé (ordre validé par la proposition)

1. **Hero** — plein écran, photo façade du château (tourelle), voile sombre dégradé.
   Eyebrow : « Beaulieu · Haute-Loire · Auvergne ». H1 : « Domaine d'Éden ».
   Sous-titre serif italique : « Un château pour rêver, un domaine pour se ressourcer. »
   CTA primaire → réservation ; CTA ghost tel : 06 65 32 92 61. Flèche scroll discrète.
2. **L'esprit des lieux** (`#domaine`) — éditorial asymétrique : collage 2 photos
   (jardin + cour) / texte : le domaine, l'arrivée par l'allée, la reconnexion à
   l'essentiel. Mention Via Fluvia (accueil cyclistes). Signature « Grégory & Thomas ».
3. **Les hôtes** — bande courte : leur histoire (Parisiens installés en Auvergne),
   les deux cockers et les chats, note Booking « Personnel 9,8/10 » en preuve discrète.
4. **Bandeau défilant** — bande pleine largeur terre cuite, vocabulaire sensoriel en
   Cormorant italique (« Pierre & lumière · Feux de bois · Silence du parc… »).
   Décoratif (`aria-hidden`), il sert de respiration colorée entre les hôtes et les chambres.
5. **Les chambres** (`#chambres`) — intro + 5 cartes :
   - Suite du Roi et de la Reine — la majestueuse
   - Antichambre de la Nuit — l'énigmatique
   - Boudoir des Rêves — le délicat
   - Refuge des Brumes — l'apaisant
   - Repaire des Songes — le mystérieux
   Détails communs : 2 pers · sdb privative · petit-déjeuner inclus. Prix « à partir de 90 € ».
   ⚠️ Photos : une seule chambre dispose de photos HD (fiche Gîtes de France). Les cartes
   réutilisent provisoirement ses angles + pièces du château. À remplacer par les photos
   définitives du client, chambre par chambre.
   Encart sous la grille : **table d'hôtes** (25 €/pers, sur réservation 24–48 h,
   produits locaux) + **gîte 2–4 personnes à venir en 2027**.
6. **L'événementiel** (`#evenements`) — bande sombre (vert-noir) : mariages intimistes,
   cousinades, séminaires, privatisation jusqu'à 30 personnes, formule traiteur planches
   apéritives. CTA « Télécharger la plaquette » (PDF placeholder) + CTA demande.
7. **Les alentours** (`#alentours`) — 3–4 items : Le Puy-en-Velay (17 km), la Via Fluvia
   à vélo, gorges de la Loire / villages (Lavoûte-sur-Loire), tables locales (La Galoche…).
8. **Galerie** (`#galerie`) — mosaïque 7 photos à placement explicite (4×3, remplissage exact),
   visionneuse plein écran maison (clavier + flèches + Échap).
9. **Espace Soreï** — court bandeau : centre de médiation équine et d'accompagnement au
   sein du domaine ; **lien sortant** vers son site. Rien de plus.
10. **Contact & accès** (`#contact`) — adresse, tel, mail, horaires arrivée/départ,
   carte (lien Google Maps, pas d'iframe lourde), CTA final pleine largeur
   « Composer votre séjour ».
11. **Footer** — encre : logo, nav, coordonnées, réseaux (FB/IG), mentions légales,
    crédit MarketFrame.

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
- Espace Soreï : espacesorei43@gmail.com — site propre (URL à confirmer par le client).

## Mapping photos (assets/img)

| Fichier | Contenu | Usage |
|---|---|---|
| hero-chateau.jpg | façade + tourelle, ciel bleu (gdf-11) | hero |
| chateau-angle.jpg | château angle allée (gdf-12) | esprit des lieux / événementiel |
| chateau-tour.jpg | tour côté jardin (gdf-10) | galerie / alentours |
| cour-roues.jpg | mur de la cour, roues de charrette (gdf-13) | collage esprit des lieux |
| jardin.jpg | cour jardin arbustes (gdf-14) | collage esprit des lieux |
| chambre-*.jpg | chambre bleue toile de Jouy, 4 angles (gdf-0/1/2/3) | cartes chambres (provisoire) |
| salon.jpg / salon-piano.jpg | salons moulures & poutres (gdf-5/6) | chambres/galerie |
| salle-a-manger.jpg / table-hotes.jpg | salle à manger (gdf-8/9) | table d'hôtes |
| cuisine.jpg (gdf-7), salle-bain.jpg (gdf-4) | annexes | galerie si besoin |
