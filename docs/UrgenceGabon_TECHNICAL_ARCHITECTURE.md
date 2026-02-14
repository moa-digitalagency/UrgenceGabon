# UrgenceGabon - Architecture Technique

Ce document détaille l'architecture logicielle, la structure de la base de données et les choix technologiques du projet UrgenceGabon.com.

## 1. Vue d'ensemble

L'application est construite sur une architecture **monolithique modulaire** utilisant le micro-framework Flask. Elle est conçue pour être légère, rapide et facile à déployer.

*   **Langage :** Python 3.11+
*   **Framework Web :** Flask 3.1.2
*   **Base de données :** PostgreSQL (Production) / SQLite (Dev)
*   **ORM :** SQLAlchemy 2.0
*   **Frontend :** Jinja2 (Templating) + Tailwind CSS (Styling) + Vanilla JS (Interactivité)
*   **Serveur WSGI :** Gunicorn

## 2. Structure du Projet

```
urgence-gabon/
├── app.py                 # Factory de l'application, configuration globale
├── main.py                # Point d'entrée WSGI
├── extensions.py          # Initialisation des extensions Flask (DB, Login, CSRF...)
├── init_db.py             # Script idempotent de migration/initialisation DB
├── models/                # Définitions des modèles SQLAlchemy (1 fichier/domaine)
│   ├── pharmacy.py        # Modèle principal
│   ├── admin.py           # Authentification
│   └── ...
├── routes/                # Blueprints Flask
│   ├── public.py          # Routes frontend public (API + HTML)
│   └── admin/             # Blueprint Admin modulaire
│       ├── __init__.py    # Setup blueprint
│       ├── pharmacy.py    # CRUD Pharmacies
│       └── ...
├── services/              # Logique métier (Business Logic Layer)
├── static/                # Assets publics
│   ├── js/                # Modules JavaScript (ES6 style)
│   ├── css/               # Tailwind CSS compilé/custom
│   └── uploads/           # Stockage médias (Images pubs, logos)
├── templates/             # Templates HTML Jinja2
│   ├── base.html          # Layout principal
│   ├── index.html         # SPA Publique
│   └── admin/             # Vues Administration
└── docs/                  # Documentation projet
```

## 3. Base de Données

### Schéma Relationnel
La base de données est normalisée et comprend 15 tables principales :

1.  **Core Data :**
    *   `pharmacy` : Entité centrale. Contient infos, coordonnées GPS, statut garde.
    *   `emergency_contact` : Numéros d'urgence (Police, SAMU...).
    *   `admin` : Comptes administrateurs (Username + Hash password).

2.  **User Contributions (Crowdsourcing) :**
    *   `location_submission` : Propositions de coordonnées GPS.
    *   `info_submission` : Corrections de données (différentiel).
    *   `pharmacy_proposal` : Propositions de nouveaux établissements.
    *   `suggestion` : Messages libres.

3.  **Marketing & Analytics :**
    *   `advertisement` : Publicités (contenu média).
    *   `ad_settings` : Configuration globale du moteur de pub.
    *   `pharmacy_view` : Log des vues par pharmacie.
    *   `page_interaction` : Log des recherches et filtres.
    *   `user_action` : Log des clics (CTA pub, appels).

4.  **Configuration :**
    *   `site_settings` : Clé-valeur pour config dynamique (SEO, Logos).
    *   `popup_message` : Messages d'information temporaires.

### Stratégie de Migration (`init_db.py`)
Le projet n'utilise pas Alembic mais un script de migration personnalisé **idempotent** :
*   **Principe :** Le script peut être lancé à chaque déploiement sans risque.
*   **Tables :** Crée les tables si elles n'existent pas (`CREATE TABLE IF NOT EXISTS`).
*   **Colonnes :** Inspecte le schéma existant et ajoute les colonnes manquantes (`ALTER TABLE ... ADD COLUMN`) avec des valeurs par défaut sûres.
*   **Données :** Préserve strictement toutes les données existantes.

## 4. Backend (Flask)

### Blueprints
L'application est divisée en deux blueprints principaux :
1.  **`public_bp`** (`routes/public.py`) : Gère l'affichage de la SPA (Single Page Application) et l'API JSON consommée par le frontend.
2.  **`admin_bp`** (`routes/admin/`) : Interface d'administration sécurisée, découpée en sous-modules (`pharmacy`, `ads`, `settings`...) pour la maintenabilité.

### Extensions Clés
*   **Flask-SQLAlchemy :** Gestion de la base de données.
*   **Flask-Login :** Gestion des sessions utilisateurs (Admin).
*   **Flask-WTF :** Protection CSRF.
*   **Flask-Limiter :** Protection contre le brute-force et le spam sur les formulaires publics.
*   **Werkzeug :** Hachage des mots de passe et sécurisation des noms de fichiers uploadés.

## 5. Frontend

### Approche "Hybride"
Le frontend n'utilise pas de framework JS lourd (React/Vue) pour maximiser la performance et le SEO, mais se comporte comme une SPA :
*   **HTML :** Rendu initial côté serveur (SSR) via Jinja2 pour un SEO optimal et un First Paint rapide.
*   **CSS :** Tailwind CSS via CDN pour le prototypage rapide et la légèreté.
*   **JS :** JavaScript Vanilla modulaire (`static/js/`) pour l'interactivité (Carte, Filtres, Modales).
    *   `map.js` : Gestion Leaflet (Carte).
    *   `pharmacy.js` : Gestion de la liste et des détails.
    *   `ads.js` : Gestion du moteur de publicité frontend.

## 6. Sécurité

*   **CSRF :** Tous les formulaires POST (Admin et Public) incluent un token CSRF validé par Flask-WTF.
*   **Rate Limiting :**
    *   Soumission GPS/Info : 20 requêtes/heure par IP.
    *   Suggestions : 100 requêtes/heure par IP.
*   **Injections SQL :** Impossible grâce à l'utilisation stricte de l'ORM SQLAlchemy.
*   **XSS :** Échappement automatique par Jinja2 + Fonctions `escapeHtml()` côté client.
*   **Uploads :**
    *   Vérification des extensions (`allowed_file`).
    *   Renommage complet (UUID) pour éviter les collisions et les noms de fichiers malveillants.
    *   Chemins absolus sécurisés.

## 7. Déploiement

### Variables d'Environnement
La configuration passe exclusivement par les variables d'environnement (12-factor app) :
*   `DATABASE_URL` : Chaîne de connexion PostgreSQL.
*   `SECRET_KEY` : Clé de signature des sessions.
*   `ADMIN_USERNAME` / `ADMIN_PASSWORD` : Credentials initiaux.

### Serveur
*   **Gunicorn :** Serveur d'application WSGI de production.
*   **Commande :** `gunicorn --bind 0.0.0.0:5000 main:app`
*   **WhiteNoise (Optionnel) :** Pour servir les fichiers statiques efficacement si pas de Nginx en frontal.
