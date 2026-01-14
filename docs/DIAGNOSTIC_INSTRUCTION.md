# Guide de Correction des Pharmacies Corrompues

## Sur votre Serveur VPS

### Étape 1: Diagnostic
Copiez et exécutez ce script Python sur votre VPS:

```bash
python check_pharmacies.py
```

Ce script va:
- ✅ Identifier toutes les pharmacies corrompues de Libreville
- ✅ Lister les champs manquants ou invalides
- ✅ Générer le script SQL de correction

### Étape 2: Correction Automatique
Deux options:

**Option A: Correction Python (Recommandée)**
```bash
python fix_pharmacies.py
```
Cela va automatiquement:
- Supprimer les pharmacies avec données manquantes critiques
- Corriger les coordonnées GPS invalides
- Fixer les dates de garde invalides
- Rétablir les valeurs par défaut appropriées

**Option B: Correction Manuelle SQL**
Si vous préférez utiliser SQL directement:

```sql
-- 1. Identifier les pharmacies problématiques
SELECT id, code, nom, latitude, longitude FROM pharmacy WHERE ville = 'Libreville';

-- 2. Supprimer celles avec code ou nom manquants
DELETE FROM pharmacy WHERE (code IS NULL OR code = '') AND ville = 'Libreville';
DELETE FROM pharmacy WHERE (nom IS NULL OR nom = '') AND ville = 'Libreville';

-- 3. Corriger les coordonnées GPS invalides
UPDATE pharmacy SET latitude = 0.4162, longitude = 9.4673
WHERE ville = 'Libreville' AND (
  latitude IS NULL OR longitude IS NULL OR
  latitude < -90 OR latitude > 90 OR 
  longitude < -180 OR longitude > 180
);

-- 4. Vérifier le résultat
SELECT id, code, nom, latitude, longitude FROM pharmacy WHERE ville = 'Libreville';
```

### Étape 3: Vérification
Après correction, redémarrez votre application et vérifiez:
1. La page d'accueil charge sans erreur 500
2. Les pharmacies de Libreville s'affichent correctement
3. La carte fonctionne

### Problèmes Courants

**Erreur 500 lors de l'affichage des pharmacies:**
- Cause probable: Coordonnées GPS invalides (latitude/longitude hors limites)
- Solution: Exécuter `fix_pharmacies.py` ou le script SQL option 3

**Erreur lors de l'édition:**
- Cause probable: Données manquantes (code, nom)
- Solution: Exécuter `fix_pharmacies.py`

**Les pharmacies ne s'affichent pas:**
- Cause probable: Type établissement invalide
- Solution: Vérifier avec le script diagnostic

## Fichiers à Copier sur votre VPS

1. `check_pharmacies.py` - Script de diagnostic
2. `fix_pharmacies.py` - Script de correction automatique

Ces scripts utilisent votre application Flask existante et votre base de données.
