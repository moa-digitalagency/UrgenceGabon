# UrgenceGabon - Guide Administrateur

Ce document est destiné aux administrateurs de la plateforme UrgenceGabon.com. Il décrit les procédures pour gérer les données, valider les contributions et configurer le site.

## 1. Accès & Tableau de Bord

### Connexion
Accédez à l'URL `/admin` (ou cliquez sur le bouclier 🛡️ en haut à droite).
Entrez vos identifiants administrateur.

### Tableau de Bord (Dashboard)
Le tableau de bord centralise toutes les informations clés :
*   **KPIs :** Nombre total de pharmacies, pharmacies de garde actives.
*   **Alertes :** Soumissions en attente de validation (Rouge = Urgence).
*   **Statistiques :** Vues totales, graphiques de fréquentation par ville.
*   **Logs :** Dernières actions effectuées sur le site.

## 2. Gestion des Pharmacies

### Ajouter une Pharmacie
1.  Dans le menu latéral, cliquez sur **"Ajouter Pharmacie"**.
2.  Remplissez le formulaire (Nom, Ville obligatoires).
3.  **Astuce :** Pour les coordonnées GPS, vous pouvez cliquer sur la carte pour placer le marqueur.
4.  Cochez **"Vérifié"** si vous êtes sûr des informations.

### Modifier / Supprimer
1.  Depuis la liste des pharmacies, cliquez sur **"Modifier"** (crayon) ou **"Supprimer"** (corbeille).
2.  **Attention :** La suppression est définitive.

### Gérer les Gardes (Important)
Pour activer le statut "De garde" d'une pharmacie :
1.  Cliquez sur l'icône **"Garde"** (croix verte) dans la liste.
2.  Définissez la **Date de début** (aujourd'hui par défaut).
3.  La **Date de fin** est calculée automatiquement (+7 jours), mais vous pouvez la modifier.
4.  Validez. La pharmacie apparaîtra immédiatement avec le badge rouge sur le site public.

## 3. Validation des Contributions

Le cœur du système participatif. Vous devez valider les données envoyées par les utilisateurs pour garantir la qualité.

### Localisations GPS
*   **Interface :** Compare la position actuelle (ou vide) avec la position proposée sur une carte.
*   **Action :**
    *   **Valider :** Met à jour la latitude/longitude de la pharmacie.
    *   **Rejeter :** Supprime la demande.

### Corrections d'Informations
*   **Interface :** Affiche "Valeur Actuelle" vs "Valeur Proposée" (ex: Ancien numéro vs Nouveau numéro).
*   **Action :**
    *   **Approuver :** Remplace instantanément la donnée en base.
    *   **Rejeter :** Ignore la modification.

### Nouvelles Pharmacies
*   Lorsqu'un utilisateur propose une nouvelle pharmacie, vérifiez qu'elle n'existe pas déjà (doublon).
*   Si validée, elle est créée avec un code unique (ex: `NEW8X2A`).

## 4. Configuration du Site

### SEO & Métadonnées
Dans l'onglet **"Paramètres"** :
*   **Titre du site :** Modifie la balise `<title>`.
*   **Description :** Modifie la balise meta description (Google).
*   **Images :** Upload du Logo et du Favicon.

### Contacts d'Urgence
Dans l'onglet **"Urgences"** :
*   Ajoutez ou modifiez les numéros (Police, SAMU, etc.).
*   Cochez **"National"** pour les numéros valables partout (ex: 177).
*   Sinon, spécifiez la **Ville** concernée.

## 5. Marketing & Publicités

UrgenceGabon dispose d'un moteur publicitaire intégré.

### Créer une Publicité
1.  Allez dans **"Publicités"** > **"Nouvelle Pub"**.
2.  **Média :** Upload d'une image ou lien vidéo (Youtube).
3.  **Priorité :** Plus le chiffre est élevé, plus la pub s'affichera souvent.
4.  **Dates :** Programmez le début et la fin de la campagne.

### Statistiques
Suivez les performances de chaque publicité :
*   **Vues :** Nombre d'affichages (Impressions).
*   **Clics :** Nombre de clics sur le bouton d'action (CTR).
