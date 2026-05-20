# Return Tracker

Return Tracker est une petite application Flask permettant de suivre les retours produits d'une boutique en ligne.

L'objectif du projet est de centraliser les produits, d'enregistrer les retours clients et de garder une trace des informations liées à chaque retour.  
L'application utilise des fichiers CSV afin de rester simple à lancer et à modifier.

## Version 2 - Suivi et analyse des retours

Cette deuxième version reprend les fonctionnalités de la V1 et ajoute plusieurs améliorations autour de l'ergonomie, de la gestion des retours, et l'ajout d'une nouvelle page pour l'analyse des données.

## Fonctionnalités principales

### Produits

- import de produits depuis un fichier CSV Shopify ;
- ajout manuel d'un produit ;
- modification d'un produit ;
- suppression d'un produit ;
- affichage des produits regroupés par nom, couleur et taille.

### Ajout d'un retour

La page d'ajout de retour a été améliorée avec un sélecteur de produit plus lisible.

Cette amélioration rend le formulaire plus simple à utiliser, surtout lorsque la liste de produits commence à devenir longue.

### Liste des retours

La page des retours permet maintenant de consulter les retours enregistrés avec plus de confort.

Nouveautés ajoutées :

- affichage raccourci des noms de produits trop longs ;
- possibilité de déplier un nom de produit pour le voir en entier ;
- affichage des commentaires sous forme de Oui / Non ;
- possibilité de déplier un commentaire lorsqu'il existe ;
- modification d'un retour déjà enregistré ;
- suppression d'un retour enregistré.

Ces ajouts permettent de corriger plus facilement une erreur de saisie ou de supprimer un retour de test.

### Statistiques

Une nouvelle page de statistiques a été ajoutée afin d'exploiter les retours enregistrés.

Elle affiche pour chaque produit retourné :

- le nombre de retours ;
- la raison principale de retour ;
- le pourcentage de chaque raison ;
- l'action principale effectuée ;
- le détail des actions en pourcentage.

Les produits sont classés selon le nombre de retours et le pourcentage de la raison principale, afin d’afficher en premier ceux qui semblent avoir un problème clairement identifiable.

L'idée n'est pas seulement de voir les produits les plus retournés, mais aussi de repérer ceux pour lesquels une raison revient clairement plus souvent que les autres.

## Utilité de la V2

La V1 permettait surtout d'enregistrer les retours.  
Cette V2 ajoute une première couche d'analyse et rend l'application plus pratique à utiliser.

Elle permet notamment de mieux comprendre :

- quels produits reviennent le plus souvent ;
- quelles raisons de retour sont les plus fréquentes ;
- si un produit semble avoir un problème précis ;
- quelles actions sont généralement prises après un retour.

Cette version transforme donc l'application en un petit outil de suivi interne, plutôt qu'une simple liste de retours.

## Technologies utilisées

- Python
- Flask
- HTML
- CSS
- CSV
- JavaScript léger pour le sélecteur de produit

## Lancer le projet

Depuis le dossier du projet :

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py


http://127.0.0.1:5050