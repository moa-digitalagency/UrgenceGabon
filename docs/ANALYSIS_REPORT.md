# Rapport d'analyse du projet UrgenceGabon.com

Suite à l'analyse complète du projet, voici les erreurs potentielles et points d'attention détectés :

## 1. Sécurité : Vulnérabilité CSRF Critique
**Gravité : Haute**

Plusieurs routes d'administration utilisées via AJAX sont exemptées de la protection CSRF (`@csrf.exempt`) alors qu'elles effectuent des modifications d'état (validation, activation/désactivation, suppression). Un attaquant pourrait inciter un administrateur connecté à visiter une page malveillante pour effectuer ces actions à son insu.

**Routes concernées :**
- `/admin/pharmacy/<int:id>/toggle-garde`
- `/admin/pharmacy/<int:id>/validate-location`
- `/admin/pharmacy/<int:id>/invalidate-location`
- `/admin/pharmacy/<int:id>/toggle-verified`
- `/admin/pharmacy/<int:id>/update-coordinates`
- `/admin/pharmacy/<int:id>/set-garde`
- `/admin/location-submission/<int:id>/approve` (et reject)
- `/admin/info-submission/<int:id>/approve` (et reject)
- `/admin/suggestion/<int:id>/respond` (et archive)
- `/admin/pharmacy-proposal/<int:id>/approve` (et reject)
- `/admin/ad/<int:id>/toggle`

**Recommandation :**
1. Retirer le décorateur `@csrf.exempt` de ces routes.
2. Ajouter le jeton CSRF dans les en-têtes des appels `fetch` dans `templates/admin/dashboard.html` et autres fichiers JS.

Exemple de correction JS :
```javascript
fetch(endpoint, {
    method: 'POST',
    headers: {
        'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
    }
})
```

## 2. Intégrité des données : Validation trop permissive
**Gravité : Moyenne**

Le système de soumission de corrections (`InfoSubmission`) permet de proposer des modifications pour n'importe quel champ du modèle `Pharmacy`. Lors de l'approbation (`routes/admin/submissions.py`), le code utilise `setattr(pharmacy, submission.field_name, submission.proposed_value)` sans vérifier si le champ est sensible (ex: `id`, `validated_by_admin_id`, `created_at`).

**Recommandation :**
Définir une liste blanche (whitelist) des champs modifiables (ex: `nom`, `telephone`, `horaires`, `services`) et rejeter les autres.

## 3. Gestion des dates et fuseaux horaires
**Gravité : Faible/Moyenne**

L'application utilise `datetime.utcnow()` pour stocker et comparer les dates. Le Gabon est sur le fuseau UTC+1 (WAT).
- Les gardes sont définies sur 7 jours via `timedelta(days=7)`, débutant probablement à minuit UTC, ce qui correspond à 01:00 du matin au Gabon.
- L'affichage "Actuellement de garde" (`is_currently_garde`) se base sur UTC.
- Conséquence : Une pharmacie pourrait apparaître comme fermée entre 00h00 et 01h00 le jour du début de garde.

**Recommandation :**
Utiliser des dates "timezone-aware" ou stocker explicitement en UTC mais convertir en heure locale pour l'affichage et les calculs de début/fin de journée.

## 4. Politique de sécurité de contenu (CSP)
**Gravité : Faible**

L'en-tête `Content-Security-Policy` autorise `'unsafe-inline'` pour les scripts et les styles. Bien que souvent nécessaire pour les frameworks CSS utilitaires comme Tailwind (en mode CDN) ou pour des scripts inline simples, cela réduit la protection contre les attaques XSS.

**Recommandation :**
Si possible, déplacer les scripts inline dans des fichiers `.js` séparés ou utiliser des "nonces".

## 5. Analyse statique
Quelques faux positifs ont été relevés par l'analyseur statique concernant l'utilisation de `func.count` avec SQLAlchemy, mais le code est fonctionnel.
Aucune erreur de syntaxe ou d'importation manquante n'a été détectée dans les fichiers principaux.

## Conclusion
Le projet est globalement bien structuré et suit les bonnes pratiques Flask (Blueprints, Application Factory, Extensions). La correction des vulnérabilités CSRF est prioritaire avant toute mise en production.
