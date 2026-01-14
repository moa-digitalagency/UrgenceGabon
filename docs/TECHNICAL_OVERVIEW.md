# Vue technique complète - UrgenceGabon.com

Vue d'ensemble complète de l'architecture, des fonctionnalités et des décisions techniques.

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Fonctionnalités actuelles](#fonctionnalités-actuelles)
4. [Flux de données](#flux-de-données)
5. [Base de données](#base-de-données)
6. [Sécurité](#sécurité)
7. [Performance](#performance)
8. [Maintenabilité](#maintenabilité)

## Vue d'ensemble

**UrgenceGabon.com** est une plateforme web servant de répertoire centralisé pour les pharmacies et services d'urgence au Gabon. Elle combine un interface publique simple pour les visiteurs avec un panneau d'administration robuste pour la gestion des données.

**Stack technique** :
- Backend : Flask (Python)
- Frontend : Jinja2 + Tailwind CSS + JavaScript vanilla
- Base de données : PostgreSQL
- Serveur : Gunicorn
- Hébergement : Replit

**Caractéristiques** :
- 89 pharmacies indexées
- 9 villes couvertes
- Interface responsive mobile-first
- Système complet d'administration
- SEO optimisé avec sitemap et robots.txt dynamiques
- Système de publicités configurable
- Audit trail complet des activités

## Architecture

### Pile technologique

```
┌─────────────────────────────────────┐
│     Navigateur (HTML/CSS/JS)        │
├─────────────────────────────────────┤
│   Tailwind CSS | JavaScript Vanilla │
│   Leaflet.js   | Chart.js           │
├─────────────────────────────────────┤
│     Flask (Application Backend)      │
│   Templates Jinja2 | Blueprints     │
├─────────────────────────────────────┤
│  SQLAlchemy ORM | Flask-Login       │
│  Flask-WTF      | Flask-Limiter     │
├─────────────────────────────────────┤
│     PostgreSQL (Base de données)    │
│   13 tables | Migrations sûres      │
└─────────────────────────────────────┘
```

### Répartition des fichiers

**Frontend** (170 lignes HTML + 600+ lignes JS + 400+ lignes CSS) :
- `templates/index.html` : Page unique publique
- `templates/admin/` : 9 pages administration
- `static/js/` : 7 modules JavaScript modulaires
- `static/css/style.css` : Styles personnalisés

**Backend** (2 100+ lignes Python) :
- `app.py` : Factory Flask, middleware, error handlers
- `routes/` : 11 fichiers de routes (1 public + 8 admin modules)
- `models/` : 8 fichiers de modèles (13 tables)
- `services/` : 1 fichier de logique métier
- `security/` : Authentification
- `utils/` : Utilitaires (helpers GPS)
- `extensions.py` : Configuration des extensions
- `init_db.py` : Initialisation/migration intelligente

### Organisation des blueprints

**public_bp** (`routes/public.py`) :
- Routes pour le public
- 25+ endpoints API
- Gestion SEO (sitemap, robots)
- 522 lignes

**admin_bp** (`routes/admin/__init__.py`) :
- Factory blueprint admin
- Décorateurs de protection
- 8 sous-modules :
  - `auth.py` (authentification)
  - `dashboard.py` (tableau de bord)
  - `pharmacy.py` (CRUD pharmacies)
  - `submissions.py` (validation soumissions)
  - `emergency.py` (contacts urgence)
  - `settings.py` (config site)
  - `ads.py` (gestion pubs)
  - `logs.py` (journal d'activité)

## Fonctionnalités actuelles

### Interface publique

**Onglets de navigation** :
1. **Toutes les pharmacies** : Affichage liste avec recherche et filtrage par ville
2. **Pharmacies de garde** : 24h/24 avec horaires
3. **Carte** : Visualisation Leaflet avec marqueurs
4. **Numéros d'urgence** : Police, pompiers, ambulance, hôpitaux
5. **Boîte à suggestions** : Feedback utilisateurs

**Fonctionnalités utilisateur** :
- Recherche libre (nom, quartier, services)
- Filtrage par ville
- Filtrage par type (garde, gare, etc.)
- Vue détaillée de chaque pharmacie
- Soumission de coordonnées GPS
- Correction d'informations (téléphone, horaires, etc.)
- Suggestion de nouvelles pharmacies
- Affichage de popups personnalisés
- Affichage de publicités (images ou vidéos)

### Interface administrateur

**Tableau de bord** :
- 20+ statistiques clés
- Graphiques (Chart.js)
- Vues par city et type
- Interaction utilisateurs (recherches, filtres)
- Soumissions en attente

**Gestion des pharmacies** :
- Ajout/édition/suppression
- Activation/désactivation service de garde
- Définition des dates de garde
- Validation des coordonnées GPS
- Vérification des informations

**Validation des soumissions** :
- Soumissions de localisation GPS
- Corrections d'informations
- Propositions de nouvelles pharmacies
- Suggestions et commentaires

**Configuration du site** :
- Métadonnées SEO
- Logo et favicon
- Paramètres OpenGraph et Twitter
- Code structuré JSON-LD
- Codes d'en-tête/pied de page

**Gestion des popups** :
- Affichage/masquage
- Images uploadées ou URLs
- Contrôle de la fréquence

**Gestion des publicités** :
- CRUD des publicités
- Configuration globale
- Plusieurs déclencheurs (temps, page, rechargement)
- Statistiques de vue et clic
- Différenciation mobile/desktop

**Journal d'activité** :
- Toutes les requêtes HTTP
- IP address et user agent
- Temps de réponse
- Filtres par type, niveau, chemin

## Flux de données

### 1. Recherche de pharmacies

```
Utilisateur → JS appelle GET /api/pharmacies
   ↓
PharmacyService.get_all_pharmacies(search, ville, garde_only)
   ↓
Requête SQL filtrée
   ↓
Pharmacy.to_dict() JSON
   ↓
JS met à jour liste + carte
```

### 2. Soumission de localisation GPS

```
Utilisateur soumet GPS → POST /api/pharmacy/<id>/submit-location
   ↓
Validation coordonnées (float)
   ↓
LocationSubmission créée avec status=pending
   ↓
Admin voit dans tableau de bord
   ↓
Admin approuve → Pharmacy.latitude/longitude mises à jour
   ↓
Status → approved
```

### 3. Validation d'une correction d'information

```
Utilisateur soumet info → POST /api/pharmacy/<id>/submit-info
   ↓
Validation champ modifiable (telephone, horaires, services, etc.)
   ↓
InfoSubmission créée avec current_value + proposed_value
   ↓
Admin voit dans tableau de bord
   ↓
Admin approuve → Pharmacy.<field> mis à jour
   ↓
Status → approved
```

### 4. Affichage de publicités

```
JS initialise (ChargeLes paramètres globaux)
   ↓
GET /api/ads/settings → AdSettings
   ↓
Selon trigger_type :
   - "time" : Timer initial puis répétition
   - "page" : Compteur de pages/clics
   - "refresh" : À chaque rechargement
   ↓
Quand condition remplie → GET /api/ads/random
   ↓
Advertisement sélectionnée (pondérée par priorité)
   ↓
Popup affichée avec délai skip_delay
   ↓
POST /api/ads/<id>/view → view_count++
   ↓
Si clic → POST /api/ads/<id>/click → click_count++
```

### 5. Indexation SEO

```
Moteur de recherche → GET /robots.txt
   ↓
Découvre /sitemap.xml
   ↓
GET /sitemap.xml
   ↓
XML généré dynamiquement :
   - /
   - /#pharmacy-1, /#pharmacy-2, etc.
   - Dates de modification (updated_at)
   ↓
Moteur de recherche crawle pages indexées
   ↓
Pages /admin/* explicitement bloquées
```

### 6. Authentification administrateur

```
Utilisateur → GET /admin (non connecté)
   ↓
Redirection vers /admin/login
   ↓
POST /admin/login (username + password)
   ↓
Validation avec Admin.check_password()
   ↓
Flask-Login enregistre la session
   ↓
Cookie sécurisé créé (HttpOnly, SameSite, Secure)
   ↓
Redirection vers /admin/ (tableau de bord)
```

## Base de données

### 13 tables (modèles)

#### Authentification
- **Admin** : Comptes administrateur (username, password_hash)

#### Données principales
- **Pharmacy** : Annuaire pharmacies (code, nom, ville, coordinates, garde, vérification)
- **EmergencyContact** : Contacts urgence (type, label, téléphones, par ville)

#### Soumissions utilisateurs
- **LocationSubmission** : GPS proposé (status: pending/approved/rejected)
- **InfoSubmission** : Correction d'info (field, current, proposed, status)
- **PharmacyProposal** : Nouvelle pharmacie (tous les champs + status)
- **Suggestion** : Commentaires/idées (category, message, admin_response, status)
- **PharmacyView** : Comptage des vues (timestamps)
- **PageInteraction** : Interactions utilisateur (search, filter, tab_switch, page_load)
- **UserAction** : Actions détaillées

#### Configuration
- **Advertisement** : Publicités (title, description, image/video, cta, priority, view_count, click_count)
- **AdSettings** : Config globale pubs (trigger, delays, limits, mobile/desktop)
- **PopupMessage** : Messages popup (title, description, image, show_once)
- **SiteSettings** : Clé-valeur (meta, SEO, logo, structured data)

#### Audit
- **ActivityLog** : Journal requêtes (IP, method, path, status, response_time, log_level)

### Migrations sûres

**init_db.py** gère :
1. Création des tables manquantes
2. Vérification des données existantes
3. Ajout des colonnes manquantes (avec valeurs par défaut)
4. Initialisation de l'admin
5. Configuration SEO par défaut

**Zéro perte de données** : Toutes les opérations sont additive (CREATE TABLE IF NOT EXISTS, ALTER TABLE ADD COLUMN)

## Sécurité

### Authentification
- Sessions Flask-Login
- Mots de passe hashés Werkzeug (algorithme par défaut + salage)
- Admin créé automatiquement au démarrage
- Décorateur @login_required sur toutes les routes sensibles

### Protection des communications
- Cookies sécurisés : HttpOnly=true, SameSite=Lax, Secure=true (production)
- CSRF : Tokens Flask-WTF avec expiration 1h
- Headers sécurité : X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, CSP

### Injection SQL
- SQLAlchemy avec requêtes préparées
- Aucune construction de SQL en strings
- Impossible par conception

### Cross-Site Scripting (XSS)
- Jinja2 échappe HTML par défaut
- Fonction escapeHtml() en JavaScript pour contenus dynamiques
- Aucun HTML innerHTML direct

### Upload de fichiers
- Extensions whitelist (png, jpg, jpeg, gif, webp, svg, ico)
- Noms sécurisés avec UUID
- Stockage en /static/uploads/<type>/

### Rate limiting
- 200 requêtes par jour
- 50 requêtes par heure
- Basé sur IP cliente

### Audit trail
- Logging de toutes les requêtes HTTP
- Enregistrement IP + User-Agent
- Erreurs 400+ loggées
- Actions admin détaillées

## Performance

### Frontend
- Pas de framework lourd (vanilla JS)
- Modules JavaScript (séparation concerns)
- CSS Tailwind (CDN - cache navigateur)
- Leaflet.js pour carte interactive légère
- Chart.js pour graphiques

### Backend
- Connection pooling PostgreSQL (pool_recycle=300, pool_pre_ping=true)
- Gunicorn avec reuse-port (scaling)
- Queries optimisées SQLAlchemy
- Pas de N+1 queries visibles

### Caching
- Headers Cache-Control pour assets statiques
- Sitemap généré à la demande (pas de cache)
- Robots.txt généré à la demande

## Maintenabilité

### Structure
- Séparation concerns (routes, modèles, services)
- Blueprints modulaires
- JavaScript modulaire (7 fichiers)
- Code commenté aux points clés

### Documentation
- README.md : Vue d'ensemble
- ARCHITECTURE.md : Architecture détaillée
- API.md : Endpoints documentés
- ADMIN_GUIDE.md : Guide d'utilisation admin
- USER_COMMERCIAL.md : Fonctionnalités pour utilisateurs
- COMMERCIAL.md : Présentation commerciale
- TECHNICAL_OVERVIEW.md : Cette vue technique
- CURRENT_FEATURES.md : Liste complète des fonctionnalités

### Code quality
- Pas de dépendances externes (sauf framework standard)
- Commentaires explicatifs (français)
- Noms variables explicites
- Gestion d'erreurs cohérente

### Database
- Script init_db.py unique pour initialisation
- Migrations sûres (préservation données)
- Audit des activités
- Backup implicite via Replit

### Déploiement
- Configuration simple (variables d'env)
- Pas de build step (sauf pour prod sans --reload)
- Gunicorn production-ready
- WSGI compatible

## Points d'amélioration possibles

1. **Pagination** : Endpoints API sans pagination (OK pour volume actuel)
2. **Caching** : Cache Redis pour stats fréquent
3. **Full-text search** : PostgreSQL FTS pour recherche avancée
4. **API REST** : Plus cohérente (actuellement REST-ish)
5. **Tests** : Suite de tests automatisés
6. **CI/CD** : Pipeline de déploiement automatisé
7. **Monitoring** : Intégration service monitoring
8. **Analytics** : Plus de tracking détaillé
