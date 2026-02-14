# 🏥 UrgenceGabon.com

![Status](https://img.shields.io/badge/status-production--ready-green)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-orange)

> **L'annuaire intelligent des pharmacies de garde au Gabon.**
> Trouvez instantanément une pharmacie ouverte, localisez-la sur la carte et accédez aux numéros d'urgence vitaux.

---

## 📑 Table des matières

1.  [À propos](#-à-propos)
2.  [Fonctionnalités Clés](#-fonctionnalités-clés)
3.  [Stack Technique](#-stack-technique)
4.  [Installation & Démarrage](#-installation--démarrage)
5.  [Architecture](#-architecture)
6.  [Documentation Complète](#-documentation-complète)

---

## 💡 À propos

**UrgenceGabon.com** répond à une problématique critique de santé publique : l'accès rapide et fiable à l'information pharmaceutique, en particulier la nuit et les week-ends.

La plateforme centralise les données de **9 villes** (Libreville, Port-Gentil, Franceville...) et offre une expérience utilisateur fluide, même avec une connexion internet limitée (PWA Ready).

---

## 🚀 Fonctionnalités Clés

*   🔍 **Recherche Instantanée :** Par nom, ville ou proximité.
*   🌙 **Pharmacies de Garde :** Mise à jour en temps réel des établissements ouverts 24h/24.
*   🗺️ **Carte Interactive :** Visualisation précise via Leaflet/OpenStreetMap.
*   🚑 **Numéros d'Urgence :** Accès direct aux services de police, pompiers et SAMU.
*   📱 **100% Mobile First :** Interface optimisée pour tous les écrans.
*   🤝 **Crowdsourcing :** Les utilisateurs peuvent signaler des erreurs et proposer des corrections.
*   🛡️ **Administration Robuste :** Gestion complète des données, validation des contributions et statistiques.

---

## 🛠 Stack Technique

**Backend**
*   🐍 **Python 3.11**
*   🌶️ **Flask 3.1** (Micro-framework)
*   🗄️ **PostgreSQL** + **SQLAlchemy** (ORM)
*   🔒 **Flask-Login** & **Werkzeug** (Sécurité)

**Frontend**
*   🎨 **Tailwind CSS** (Utility-first)
*   ⚡ **JavaScript Vanilla** (Pas de framework lourd)
*   🗺️ **Leaflet.js** (Cartographie)
*   📊 **Chart.js** (Tableaux de bord admin)

**DevOps**
*   🦄 **Gunicorn** (Serveur WSGI)
*   📦 **Replit** (Environnement de déploiement)

---

## ⚡ Installation & Démarrage

### Pré-requis
*   Python 3.11+
*   PostgreSQL (ou SQLite pour le dev local)

### 1. Cloner le projet
```bash
git clone https://github.com/votre-repo/urgence-gabon.git
cd urgence-gabon
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Configurer l'environnement
Créez un fichier `.env` ou exportez les variables :
```bash
export DATABASE_URL="postgresql://user:pass@localhost/urgence_gabon"
export SECRET_KEY="votre_cle_secrete_tres_longue"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="password_securise"
```

### 4. Initialiser la base de données
Le script est idempotent (ne supprime pas vos données existantes) :
```bash
python init_db.py
```

### 5. Lancer le serveur
```bash
# Mode développement
python main.py

# Mode production (Gunicorn)
gunicorn --bind 0.0.0.0:5000 main:app
```

Accédez à `http://localhost:5000`.

---

## 🏗 Architecture

Le projet suit une architecture MVC (Model-View-Controller) modulaire via les **Blueprints Flask** :

*   `models/` : Définitions de la base de données (15 tables).
*   `routes/` :
    *   `public.py` : API et vues pour les visiteurs.
    *   `admin/` : Module d'administration sécurisé.
*   `static/js/` : Logique frontend modulaire (`map.js`, `pharmacy.js`...).

La sécurité est au cœur du design avec **CSRF Protection**, **Rate Limiting** sur les formulaires publics et **Hachage Argon2** des mots de passe.

---

## 📚 Documentation Complète

Toute la documentation technique et fonctionnelle se trouve dans le dossier `docs/` :

*   📖 **[Bible des Fonctionnalités](docs/UrgenceGabon_FEATURES_FULL_LIST.md)** : Liste exhaustive de ce que fait l'application.
*   🏗️ **[Architecture Technique](docs/UrgenceGabon_TECHNICAL_ARCHITECTURE.md)** : Deep dive dans le code et la BDD.
*   👤 **[Guide Utilisateur](docs/UrgenceGabon_USER_GUIDE.md)** : Comment utiliser le site.
*   🛡️ **[Guide Administrateur](docs/UrgenceGabon_ADMIN_GUIDE.md)** : Gérer le site au quotidien.
*   🔌 **[Référence API](docs/UrgenceGabon_API_REFERENCE.md)** : Documentation des endpoints JSON.
*   💼 **[Présentation Commerciale](docs/UrgenceGabon_COMMERCIAL_PITCH.md)** : Vision et modèle économique.

---

<p align="center">
  Développé avec ❤️ pour le Gabon 🇬🇦
</p>
