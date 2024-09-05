# Cahier des Charges

## Adhésion (priorité)

- Créer automatiquement un contact lorsqu'une personne adhère et paie en ligne.
- Envoyer automatiquement notre mail de bienvenue ainsi que la facture acquittée par paiement lors de l'adhésion en ligne :
  - Ne pas envoyer de bon de commande ou autre, uniquement la facture acquittée.
  - S'assurer que la facture soit également enregistrée comme facture acquittée dans notre partie comptabilité.
- Pour les anciens adhérents qui vont ré-adhérer cette année, est-il possible d'avoir une alerte ou autre ? (ce n'est pas prioritaire)
- Note : Les mails sont déjà prêts et les adhésions sont également prêtes.

## Partie facture (priorité : avoir rapidement)

- Nous avons importé toutes nos factures depuis 2017 dans le logiciel. Est-il possible de les relier et de les marquer comme payées ?
- Pouvoir calculer ce qu'un événement nous a coûté, en incluant pour chaque événement les recettes et les dépenses.
- Pouvoir scanner nos tickets de caisse pour la partie comptabilité.
- Nous former, si possible, sur la partie comptabilité pour :
  - Savoir comment gérer les factures et les attribuer à des projets.
  - Exemple : Lorsque nous organisons des réunions et que nous facturons les repas aux participants, nous souhaiterions pouvoir répertorier les factures par commission.

## Partie évènement (non prioritaire, mais un plus)

- Nous avons déjà programmé des mails pour :
  - Confirmer l'inscription
  - Envoyer un rappel 2 jours avant l'événement
  - Remercier avec un sondage intégré
- Vérifier que tout est correctement configuré.
- IMPORTANT : Après l'événement, trouver une solution pour :
  - Cocher uniquement les personnes présentes
  - Faire en sorte que le mail automatique soit envoyé uniquement à celles-ci
- Imprimer automatiquement les étiquettes (pas urgent)

## Partie statistique

- Pouvoir suivre la participation individuelle de nos adhérents.
- Pouvoir savoir combien de personnes sont venues à quels événements.
- En fin d'année, faire un bilan des événements qui ont le mieux fonctionné.
- Pouvoir voir quand un non-adhérent est devenu adhérent.

# Plan de projet Odoo

## 1. Adhésion (Priorité Haute)

- [ ] Configurer la création automatique de contacts lors de l'adhésion en ligne
- [ ] Mettre en place l'envoi automatique du mail de bienvenue et de la facture acquittée
- [ ] Configurer l'enregistrement automatique de la facture acquittée dans la comptabilité
- [ ] (Optionnel) Implémenter une alerte pour les ré-adhésions

## 2. Gestion des factures (Priorité Haute)

- [ ] Importer et relier les factures existantes depuis 2017
- [ ] Marquer les factures importées comme payées
- [ ] Configurer le calcul des coûts et recettes par événement
- [ ] Mettre en place un système de scan des tickets de caisse
- [ ] Organiser une formation sur la gestion des factures et l'attribution aux projets

## 3. Gestion des événements (Priorité Moyenne)

- [ ] Vérifier la configuration des mails automatiques existants
- [ ] Implémenter un système pour marquer les présences après l'événement
- [ ] Configurer l'envoi du mail de remerciement uniquement aux présents
- [ ] (Optionnel) Mettre en place l'impression automatique des étiquettes

## 4. Statistiques (Priorité Basse)

- [ ] Développer un module de suivi de la participation individuelle
- [ ] Créer des rapports sur la fréquentation des événements
- [ ] Mettre en place un système de bilan annuel des événements
- [ ] Implémenter un suivi de conversion des non-adhérents en adhérents

## Points d'attention

- Tester chaque fonctionnalité avec le client avant de passer à la suivante
- Prévoir des points réguliers avec le client pour valider l'avancement
- Documenter les processus mis en place pour faciliter la formation du client

# Plan d'action développeur Odoo

## 1. Configuration initiale

- [ ] Créer un projet Odoo.sh pour le développement et les tests
- [ ] Configurer l'environnement de développement local
- [ ] Créer un module personnalisé pour les fonctionnalités spécifiques

## 2. Adhésion (Priorité Haute)

- [ ] Développer un hook pour créer automatiquement un contact lors de l'adhésion en ligne
- [ ] Configurer le workflow d'envoi automatique du mail de bienvenue
- [ ] Personnaliser le modèle de facture acquittée
- [ ] Implémenter la logique pour enregistrer la facture acquittée dans la comptabilité
- [ ] (Optionnel) Créer une alerte pour les ré-adhésions avec `@api.constrains`

## 3. Gestion des factures (Priorité Haute)

- [ ] Écrire un script d'importation pour les factures existantes depuis 2017
- [ ] Développer une fonction pour marquer les factures importées comme payées
- [ ] Créer un modèle de calcul pour les coûts et recettes par événement
- [ ] Intégrer un module OCR pour le scan des tickets de caisse (ex: OCA/edi)
- [ ] Préparer un guide de formation pour la gestion des factures et l'attribution aux projets

## 4. Gestion des événements (Priorité Moyenne)

- [ ] Auditer et optimiser la configuration des mails automatiques existants
- [ ] Développer une interface pour marquer les présences après l'événement
- [ ] Modifier le workflow d'envoi du mail de remerciement pour cibler uniquement les présents
- [ ] (Optionnel) Intégrer un système d'impression automatique d'étiquettes

## 5. Statistiques (Priorité Basse)

- [ ] Créer un modèle pour le suivi de la participation individuelle
- [ ] Développer des rapports Qweb pour la fréquentation des événements
- [ ] Implémenter un dashboard pour le bilan annuel des événements
- [ ] Créer un champ calculé pour suivre la conversion des non-adhérents en adhérents

## 6. Tests et déploiement

- [ ] Écrire des tests unitaires pour chaque nouvelle fonctionnalité
- [ ] Effectuer des tests d'intégration sur l'environnement de staging
- [ ] Préparer la documentation technique et utilisateur
- [ ] Planifier le déploiement en production avec le client

## 7. Formation et support

- [ ] Préparer le matériel de formation pour le client
- [ ] Organiser une session de formation sur la gestion des factures et des événements
- [ ] Mettre en place un système de support pour répondre aux questions post-déploiement

## Ressources Odoo à utiliser

- Utiliser `ir.actions.server` pour les actions automatisées
- Exploiter `mail.template` pour la gestion des emails automatiques
- Utiliser `@api.depends` pour les champs calculés dans les statistiques
- Exploiter le système de rapports Qweb pour les bilans et statistiques
- Utiliser les hooks `post_init_hook` pour l'importation initiale des données