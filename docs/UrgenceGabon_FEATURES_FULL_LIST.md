# UrgenceGabon - Bible des Fonctionnalités

Liste exhaustive de toutes les fonctionnalités de la plateforme, incluant les règles de validation, les comportements métier et les processus en arrière-plan.

## 1. Interface Publique (Visiteurs)

### A. Recherche et Navigation
*   **Barre de recherche globale :** Recherche instantanée par nom de pharmacie. Insensible à la casse.
*   **Filtres par ville :** 9 villes supportées (Libreville, Port-Gentil, Franceville, Oyem, Mouila, Makokou, Koulamoutou, Moanda, Ntom).
*   **Filtres spéciaux :**
    *   **Pharmacies de garde :** Affiche uniquement les établissements avec `is_garde=True` et dont la date de fin de garde est postérieure à l'heure actuelle (UTC+1).
    *   **Proche gare :** Filtre sur `categorie_emplacement='gare'`.
*   **Onglets de navigation (SPA) :** Navigation sans rechargement de page (Toutes, Garde, Carte, Urgences, Suggestions).
*   **Deep Linking :** Les URLs supportent les ancres (ex: `/#pharmacy-123`) pour partager une pharmacie spécifique.

### B. Carte Interactive (Leaflet)
*   **Affichage :** Carte OpenStreetMap centrée sur le Gabon.
*   **Marqueurs :**
    *   **Vert :** Pharmacie standard.
    *   **Rouge/Clignotant :** Pharmacie de garde.
    *   **Bleu :** Position utilisateur (si géolocalisation acceptée).
*   **Popups :** Au clic sur un marqueur, affiche nom, téléphone (cliquable) et lien vers l'itinéraire Google Maps.
*   **Clustering :** Regroupement automatique des marqueurs proches pour éviter l'encombrement.

### C. Fiche Détaillée Pharmacie
*   **Informations affichées :** Nom, Ville, Quartier, Téléphone, Horaires, Services, Type d'établissement.
*   **Badges :**
    *   **"DE GARDE" :** Si active.
    *   **"VÉRIFIÉ" :** Si `is_verified=True` (validé par admin).
*   **Actions :**
    *   **Appeler :** Lien `tel:` direct.
    *   **Itinéraire :** Ouvre Google Maps avec les coordonnées.
    *   **Signaler une erreur :** Ouvre le formulaire de correction.
    *   **Proposer GPS :** Ouvre le formulaire de localisation si non validée.

### D. Système de Contributions (Crowdsourcing)
*   **Proposer une localisation :** Formulaire pour envoyer Latitude/Longitude.
    *   *Validation :* Coordonnées doivent être des float valides.
    *   *Anti-spam :* Limité à 20 soumissions/heure par IP.
*   **Signaler une erreur :** Correction de champ spécifique (Nom, Tel, Horaires, etc.).
    *   *Logique :* Crée une `InfoSubmission` avec valeur actuelle vs proposée.
    *   *Anti-spam :* Limité à 20 soumissions/heure par IP.
*   **Proposer une pharmacie :** Formulaire complet pour ajouter un établissement manquant.
    *   *Champs requis :* Nom, Ville.
    *   *Anti-spam :* Limité à 10 soumissions/heure par IP.
*   **Boîte à suggestions :** Envoi de feedback général (Amélioration, Bug, Autre).
    *   *Anti-spam :* Limité à 100 soumissions/heure par IP.

### E. Numéros d'Urgence
*   **Organisation :**
    1.  **National :** Police, Pompiers, SAMU (affichés en premier).
    2.  **Local :** Filtrés par ville sélectionnée.
*   **Tri :** Basé sur le champ `ordering` en base de données.

### F. Système Publicitaire (Frontend)
*   **Popups Publicitaires :**
    *   **Déclencheurs :** Temps (après X sec), Pages vues (toutes les X pages), ou Rechargement.
    *   **Contenu :** Image ou Vidéo (Youtube/MP4).
    *   **Timer "Passer" :** Bouton de fermeture bloqué pendant X secondes (configurable, défaut 5s).
    *   **Priorité :** Sélection aléatoire pondérée par le champ `priority`.
    *   **Tracking :** Compte les vues (`view_count`) et les clics (`click_count`).
*   **Popups d'Information :** Messages administratifs (ex: Maintenance) affichés une seule fois par session (`show_once=True`).

## 2. Interface Administration (/admin)

### A. Sécurité & Accès
*   **Authentification :** Login/Password.
    *   *Hachage :* Werkzeug (scrypt/pbkdf2 par défaut).
    *   *Session :* Cookie sécurisé (`HttpOnly`, `SameSite=Lax`).
    *   *Protection :* Décorateur `@login_required` sur toutes les routes `/admin`.
*   **Création compte :** Automatique au démarrage via variables d'env `ADMIN_USERNAME` / `ADMIN_PASSWORD`.

### B. Tableau de Bord (Dashboard)
*   **Statistiques Clés :**
    *   Total pharmacies / En garde / Vérifiées.
    *   Soumissions en attente (GPS, Infos, Suggestions).
    *   Vues totales et par ville (Graphique Chart.js).
    *   Interactions utilisateurs (Recherches, Filtres, Clics).
*   **Logs d'activité récents :** Dernières actions admin et erreurs système.

### C. Gestion des Pharmacies (CRUD)
*   **Ajout/Edition :** Formulaire complet.
    *   *Champs :* Nom, Ville, Quartier, Tel, BP, Horaires, Services, Propriétaire.
    *   *Types :* Pharmacie Générale, Dépôt, Hospitalière.
    *   *Vérification :* Checkbox "Vérifié" manuel.
*   **Gestion des Gardes :**
    *   **Activation :** Définition date début + date fin (automatiquement +7 jours par défaut).
    *   **Logique :** La pharmacie reste "En garde" tant que `NOW() < garde_end_date`.
*   **Validation GPS :**
    *   Vue carte comparative (Position actuelle vs Position proposée).
    *   Action : Valider (Met à jour la pharmacie) ou Rejeter.

### D. Validation des Contributions
*   **Flux de travail :**
    1.  Liste des soumissions "pending".
    2.  Comparaison Valeur Actuelle / Valeur Proposée.
    3.  Action : Approuver (Applique modification en base) ou Rejeter.
*   **Suggestions :** Possibilité de répondre (stocke la réponse en base) et d'archiver.
*   **Nouvelles Pharmacies :** Approuver crée une nouvelle entrée `Pharmacy` avec un code unique généré (`NEW` + 6 chars alpanumériques).

### E. Configuration & Marketing
*   **Gestion Publicités :**
    *   CRUD complet (Titre, Image/Vidéo, Dates, Priorité).
    *   Configuration globale : Délai avant affichage, Fréquence, Mobile vs Desktop.
    *   Stats : Vues et Clics par publicité.
*   **Paramètres du Site (SEO) :**
    *   Modification dynamique des Meta Tags (Title, Description, Keywords).
    *   Configuration OpenGraph et Twitter Cards.
    *   Upload Logo et Favicon.
    *   Injection de code (Header/Footer) pour Analytics.
*   **Contacts d'Urgence :** CRUD des numéros (National vs Local).

## 3. Fonctionnalités Techniques (Backend)

### A. Architecture de Données (PostgreSQL)
*   **Modèles (15 tables) :**
    *   `Pharmacy` : Cœur du système.
    *   `LocationSubmission`, `InfoSubmission`, `PharmacyProposal` : Données temporaires.
    *   `Advertisement`, `AdSettings` : Moteur de pub.
    *   `ActivityLog` : Audit trail.
*   **Migrations Sûres :** Script `init_db.py` idempotent.
    *   Utilise `CREATE TABLE IF NOT EXISTS`.
    *   Utilise `ALTER TABLE ADD COLUMN IF NOT EXISTS` (simulé pour SQLite) pour les mises à jour de schéma sans perte de données.

### B. Sécurité Avancée
*   **CSRF Protection :** Tokens `Flask-WTF` sur tous les formulaires POST.
*   **Rate Limiting :** `Flask-Limiter` appliqué sur les endpoints publics sensibles (Soumissions : 10-100/heure).
*   **Upload Sécurisé :**
    *   Validation extension (`png, jpg, gif...`).
    *   Renommage UUID pour éviter écrasement et exécution de code.
    *   Nettoyage automatique des fichiers orphelins (suppression ancienne image si remplacée).

### C. Performance & SEO
*   **Sitemap Dynamique (`/sitemap.xml`) :**
    *   Généré à la volée.
    *   Inclut toutes les URLs de pharmacies et villes.
    *   `Last-Modified` basé sur la date de mise à jour de la pharmacie.
*   **Robots.txt Dynamique :** Bloque `/admin`, autorise les bots légitimes (Google, GPTBot).
*   **Assets :** Fichiers statiques servis avec headers de cache.
*   **PWA :** Manifest JSON dynamique selon configuration admin.
