# UrgenceGabon.com - Notes techniques et contexte

Une plateforme web moderne pour trouver des pharmacies au Gabon. Interface mobile-first avec recherche, filtrage par ville, carte interactive, et système complet d'administration pour gérer les données.

## État actuel du projet

**Base de données** : PostgreSQL sur Replit
**Frontend** : Templates Jinja2 + Tailwind CSS + JavaScript vanilla
**Backend** : Flask (Python) avec SQLAlchemy ORM
**Déploiement** : Gunicorn sur port 5000

**Données actuelles** :
- 89 pharmacies dans 9 villes (Libreville, Port-Gentil, Franceville, etc.)
- Contacts d'urgence (police, pompiers, hôpitaux, SAMU)
- Popups personnalisées
- Système de publicités configurable

## Architecture technique

**Couche présentation** :
- `templates/index.html` : Page publique unique (SPA)
- `templates/admin/` : Pages administration
- `static/js/` : 7 modules JavaScript (app, map, pharmacy, forms, popups, ads, config)
- `static/css/style.css` : Styles personnalisés + Tailwind CDN

**Couche application** :
- `app.py` : Configuration Flask, security headers, rate limiting
- `routes/public.py` : 25+ endpoints publics (pharmacies, popups, publicités, soumissions)
- `routes/admin/` : 8 modules (auth, dashboard, pharmacy, submissions, emergency, settings, ads, logs)
- `extensions.py` : Extensions Flask (SQLAlchemy, Login, CSRF)

**Couche métier** :
- `services/pharmacy_service.py` : Opérations pharmacies (recherche, création, mise à jour, suppression, statistiques)
- `security/auth.py` : Configuration Flask-Login, création admin par défaut

**Couche données** :
- `models/` : 8 fichiers définissant 13 tables
  - Pharmacies + Contacts d'urgence + Soumissions + Publicités + Logs
- `init_db.py` : Initialisation intelligente avec vérification d'intégrité et préservation des données

## Modèles de données (13 tables)

| Modèle | Colonnes clés | Usage |
|--------|---------------|-------|
| Admin | id, username, password_hash | Authentification administration |
| Pharmacy | id, code, nom, ville, quartier, telephone, coordinates, is_garde | Annuaire principal |
| EmergencyContact | ville, service_type, label, phone_numbers | Numéros d'urgence |
| LocationSubmission | pharmacy_id, latitude, longitude, status | Soumissions GPS |
| InfoSubmission | pharmacy_id, field_name, current_value, proposed_value, status | Corrections d'infos |
| PharmacyProposal | tous les champs pharmacy + status | Propositions de nouvelles pharmas |
| Suggestion | category, subject, message, status, admin_response | Commentaires/idées |
| PharmacyView | pharmacy_id, viewed_at | Comptage des vues |
| Advertisement | title, description, media_type, priority, view_count, click_count | Publicités |
| AdSettings | configuration globale des pubs | Paramètres système |
| PopupMessage | title, description, image, is_active, show_once | Messages popup |
| SiteSettings | clé-valeur (meta, SEO, logo, structure) | Configuration site |
| ActivityLog | ip_address, method, path, status_code, response_time_ms, log_level | Audit/debug |

## Routes principales

**Routes publiques** (pas d'authentification) :
- GET `/` - Page d'accueil
- GET `/sitemap.xml` - Sitemap dynamique
- GET `/robots.txt` - Robots.txt dynamique
- GET `/api/pharmacies` - Liste pharmacies (filtres: search, ville, garde)
- GET `/api/emergency-contacts` - Contacts d'urgence
- GET `/api/popups` - Messages popup actifs
- GET `/api/ads/settings` - Configuration publicités
- GET `/api/ads/random` - Publicité aléatoire
- POST `/api/pharmacy/<id>/view` - Enregistrer une vue
- POST `/api/pharmacy/<id>/submit-location` - Soumettre GPS
- POST `/api/pharmacy/<id>/submit-info` - Soumettre correction
- POST `/api/suggestions` - Envoyer suggestion
- POST `/api/pharmacy-proposal` - Proposer pharmacie
- POST `/api/ads/<id>/view` - Enregistrer vue pub
- POST `/api/ads/<id>/click` - Enregistrer clic pub

**Routes administration** (authentification requise) :
- `/admin/login` - Connexion
- `/admin/logout` - Déconnexion
- `/admin/` - Tableau de bord (stats + soumissions en attente)
- `/admin/pharmacy/*` - CRUD pharmacies
- `/admin/submissions/*` - Validation des soumissions
- `/admin/emergency-contacts/*` - CRUD contacts d'urgence
- `/admin/settings` - Configuration du site
- `/admin/popups/*` - Gestion popups
- `/admin/ads/*` - Gestion publicités + configuration
- `/admin/logs` - Journal d'activité

## Système de gestion des données

**init_db.py** (source unique de vérité) :
1. Crée toutes les tables manquantes
2. Vérifie l'intégrité des données existantes
3. Ajoute les colonnes manquantes sans perte
4. Initialise l'admin par défaut
5. Configure les paramètres SEO par défaut

Aucun script de migration destructive. Les données existantes sont toujours préservées.

## Sécurité

**Headers** : X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, CSP
**Authentification** : Sessions Flask-Login, cookies HttpOnly + SameSite
**Protection CSRF** : Flask-WTF sur tous les formulaires admin
**Rate limiting** : 200 requêtes/jour, 50/heure (Flask-Limiter)
**Validation** : SQLAlchemy (injections SQL impossibles)
**XSS** : Jinja2 échappe l'HTML, escapeHtml() en JavaScript
**Uploads** : Extensions limitées (image/svg/ico), noms sécurisés avec UUID

## Développement et préférences

**Communication** : Français, langage simple
**Code** : Commenté quand nécessaire
**Tests** : Validation manuelle avant commit
**Workflow** : npm non utilisé - vanilla JS modulaire

## Flux de données clés

### Recherche de pharmacies
Utilisateur tape → JS appelle GET /api/pharmacies → PharmacyService filtre → JSON retourné → UI mise à jour

### Soumission d'information
Utilisateur soumet → JS appelle POST /api/pharmacy/{id}/submit-info → Entry créée (pending) → Admin voit dans dashboard → Approbation met à jour la pharmacie

### Affichage publicités
JS charge /api/ads/settings → Timer/compteur déclenché → GET /api/ads/random (pondéré) → Popup s'affiche → Vue comptabilisée

### Indexation SEO
Moteur de recherche → /robots.txt (bloque /admin) → /sitemap.xml (liste pages publiques) → Crawle pages publiques

## Variables d'environnement requises

```
DATABASE_URL=postgres://...              # PostgreSQL
SESSION_SECRET=...                       # Clé secrète Flask (min 32 char)
ADMIN_USERNAME=admin                     # Par défaut
ADMIN_PASSWORD=...                       # Défini au démarrage
```

Optionnelles :
```
FLASK_ENV=production                     # Par défaut
USE_HTTPS=true                           # Par défaut
```

## Démarrage

```bash
# Développement avec rechargement automatique
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app

# Production (pas de rechargement)
gunicorn --bind 0.0.0.0:5000 main:app
```

## Dépendances externes

**Python** :
- Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Limiter
- psycopg2-binary (PostgreSQL)
- Werkzeug (hashing)
- python-dotenv (env vars)

**CDN** :
- Tailwind CSS
- Leaflet.js 1.9.4 (cartes)
- Chart.js (graphiques)
- Google Fonts (Inter)

## Historique des modifications

**Décembre 2025 (Session 3 - Consolidation)**
- Fusion check_tables.py + migrate_db.py → init_db.py
- Stats repositionnées en admin uniquement
- Documentation complète de l'application

**Décembre 2025 (Session 2 - Audit complet)**
- Audit sécurité : 6 headers + rate limiting
- Vérification 25+ endpoints
- Migration sécurisée sans perte données
- Documentation exhaustive (9 fichiers)

**Décembre 2025 (Session 1)**
- Système de logs d'activité complet
- Refactoring JavaScript (7 modules)
- Routes admin modulaires (8 fichiers)
- Endpoints SEO (/sitemap.xml, /robots.txt)

**Sessions précédentes**
- Système publicitaire configurable
- Statistiques avec graphiques
- Upload fichiers sécurisé
- Catégorisation pharmacies
- Vérification GPS
- Design mobile-first
