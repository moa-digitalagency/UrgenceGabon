# Guide de Débogage VPS - UrgenceGabon.com

## Vue d'ensemble
Ce guide vous aide à diagnostiquer et résoudre les erreurs 500 sur votre VPS de production.

---

## 🔍 Étape 1: Exécuter le diagnostic complet

```bash
python diagnose_app.py
```

### Ce que ce script vérifie:
- ✅ Tous les modules Python requis
- ✅ Variables d'environnement (DATABASE_URL, SESSION_SECRET, etc.)
- ✅ Connexion à PostgreSQL
- ✅ Existence de toutes les tables de base de données
- ✅ Données dans les tables principales
- ✅ Compte administrateur
- ✅ Permissions des fichiers
- ✅ Routes de l'application
- ✅ Importation des modèles

### Interprétation des résultats:

**Si tous les tests passent ✅:**
```
🎉 Application diagnostiquée avec succès!
   L'application devrait fonctionner correctement.
```
→ Le problème vient de votre configuration serveur web (nginx/Apache)

**Si un test échoue ❌:**
→ Consultez la section "Problèmes courants" ci-dessous

---

## 📋 Erreurs courantes et solutions

### 1. **Erreur: DATABASE_URL non défini**
```bash
❌ DATABASE_URL: MANQUANT
```

**Solution:**
```bash
# Sur votre VPS, définissez la variable
export DATABASE_URL="postgresql://user:password@localhost:5432/dbname"

# Ou dans votre fichier .env
echo "DATABASE_URL=postgresql://user:password@localhost:5432/dbname" >> .env

# Puis redémarrez l'application
systemctl restart urgencegabon
```

### 2. **Erreur: Impossibilité de se connecter à PostgreSQL**
```bash
❌ Connexion à la base de données: Erreur
   FATAL: Aucune connexion à PostgreSQL
```

**Vérifications:**
```bash
# 1. PostgreSQL est-il en cours d'exécution?
sudo systemctl status postgresql

# 2. Démarrer PostgreSQL si nécessaire
sudo systemctl start postgresql

# 3. Tester la connexion directement
psql postgresql://user:password@localhost:5432/dbname -c "SELECT 1;"

# 4. Vérifier le firewall
sudo ufw allow 5432/tcp

# 5. Vérifier postgresql.conf listen_addresses
sudo nano /etc/postgresql/16/main/postgresql.conf
# Cherchez: listen_addresses = '*'
```

### 3. **Erreur: Tables manquantes**
```bash
❌ pharmacy: MANQUANTE
❌ admin: MANQUANTE
```

**Solution:**
```bash
# Réinitialiser la base de données
python init_db.py

# Charger les données de pharmacies
python load_pharmacies.py
```

### 4. **Erreur: Pas d'administrateur trouvé**
```bash
❌ Aucun administrateur trouvé
```

**Solution:**
```bash
# Définir les variables d'environnement
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="YourSecurePassword123!"

# Puis exécuter l'initialisation
python init_db.py

# Ou réinitialiser la base de données:
# 1. Supprimer la base
sudo -u postgres dropdb urgencegabon

# 2. Recréer la base
sudo -u postgres createdb urgencegabon

# 3. Réinitialiser
python init_db.py
```

### 5. **Erreur: Permissions des fichiers**
```bash
❌ Dossier des uploads: Non inscriptible
```

**Solution:**
```bash
# Corriger les permissions
sudo chown -R www-data:www-data /path/to/app
sudo chmod -R 755 /path/to/app
sudo chmod -R 775 /path/to/app/static/uploads
sudo chmod -R 775 /path/to/app/templates
```

---

## 🌐 Page d'erreur améliorée

Quand une erreur 500 se produit, vous verrez maintenant:

### En mode développement (FLASK_ENV=development):
✅ Message d'erreur détaillé  
✅ Informations sur la requête (URL, méthode, IP)  
✅ Pile d'exécution complète (traceback)  
✅ Suggestions de résolution  

### En production (FLASK_ENV=production):
✅ Message d'erreur sécurisé  
✅ Informations de débogage masquées  
⚠️ Les erreurs sont loggées dans les fichiers journaux  

---

## 📊 Fichiers journaux à vérifier

```bash
# 1. Journaux de l'application Flask
tail -f /var/log/urgencegabon/app.log

# 2. Journaux de Gunicorn
tail -f /var/log/urgencegabon/gunicorn.log

# 3. Journaux d'erreurs (stderr)
tail -f /var/log/urgencegabon/error.log

# 4. Journaux PostgreSQL
tail -f /var/log/postgresql/postgresql.log

# 5. Journaux Nginx (si utilisé)
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## 🛠️ Configuration recommandée pour la production

### 1. **Variables d'environnement (.env)**
```bash
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@localhost/urgencegabon
SESSION_SECRET=your-very-long-random-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=YourSecurePassword123!
USE_HTTPS=true
SECRET_KEY=another-long-random-secret-here
```

### 2. **Configuration Gunicorn**
```bash
gunicorn --bind 0.0.0.0:5000 \
         --workers 4 \
         --worker-class sync \
         --timeout 30 \
         --access-logfile /var/log/urgencegabon/access.log \
         --error-logfile /var/log/urgencegabon/error.log \
         --log-level info \
         main:app
```

### 3. **Service systemd** (/etc/systemd/system/urgencegabon.service)
```ini
[Unit]
Description=UrgenceGabon Application
After=network.target postgresql.service

[Service]
User=www-data
WorkingDirectory=/path/to/app
EnvironmentFile=/path/to/app/.env
ExecStart=/usr/bin/gunicorn --bind 0.0.0.0:5000 main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4. **Configuration Nginx**
```nginx
server {
    listen 80;
    server_name urgencegabon.com www.urgencegabon.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /path/to/app/static/;
    }
}
```

---

## 🔧 Processus de débogage complet

### Quand vous voyez l'erreur 500 sur l'admin:

```bash
# Étape 1: Vérifier l'application
python diagnose_app.py

# Étape 2: Vérifier les logs
tail -50 /var/log/urgencegabon/app.log
tail -50 /var/log/urgencegabon/error.log

# Étape 3: Vérifier PostgreSQL
psql $DATABASE_URL -c "SELECT 1;"

# Étape 4: Tester localement
python -c "from app import app; from routes.admin.dashboard import admin_dashboard; print('Admin route OK')"

# Étape 5: Redémarrer les services
sudo systemctl restart urgencegabon
sudo systemctl restart postgresql

# Étape 6: Vérifier à nouveau
python diagnose_app.py
```

---

## 💡 Conseils de débogage

### Activer le mode debug temporairement:
```bash
# ATTENTION: Ne PAS utiliser en production!
export FLASK_ENV=development
python app.py
```

### Vérifier la connectivité réseau:
```bash
# Vérifier si le port 5000 est ouvert
sudo netstat -tlnp | grep 5000
# ou
sudo ss -tlnp | grep 5000

# Vérifier depuis une autre machine
nc -zv urgencegabon.com 5000
```

### Tester la route directement:
```bash
# En SSH sur le serveur
curl http://localhost:5000/admin/
curl -H "Authorization: Basic admin:password" http://localhost:5000/admin/

# Ou avec une requête JSON
curl -X GET http://localhost:5000/api/stats
```

---

## 📞 Support et ressources

Quand vous rencontrez une erreur:

1. **Exécutez** `python diagnose_app.py`
2. **Vérifiez** les logs (voir section "Fichiers journaux")
3. **Consultez** ce guide pour la solution
4. **Redémarrez** les services
5. **Testez** à nouveau

Si le problème persiste, partagez:
- Sortie de `diagnose_app.py`
- Dernières lignes des fichiers journaux
- Configuration (variables d'environnement masquées)

---

## 🚀 Mise à jour de l'application

Après chaque mise à jour:

```bash
# 1. Arrêter l'application
sudo systemctl stop urgencegabon

# 2. Mettre à jour les dépendances
pip install -r requirements.txt

# 3. Exécuter les migrations
python init_db.py

# 4. Redémarrer
sudo systemctl start urgencegabon

# 5. Vérifier
python diagnose_app.py
```

---

**Dernière mise à jour:** 2025-12-29  
**Version:** 1.0
