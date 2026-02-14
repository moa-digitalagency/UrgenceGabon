# UrgenceGabon - Référence API

Documentation des points de terminaison (endpoints) de l'API publique. L'API est RESTful et retourne des réponses JSON.

## Base URL
`/` (Les endpoints sont préfixés par `/api`)

## 1. Pharmacies

### `GET /api/pharmacies`
Récupère la liste des pharmacies filtrée.

**Paramètres (Query String) :**
*   `search` (string, optionnel) : Recherche textuelle dans le nom.
*   `ville` (string, optionnel) : Filtrer par ville exacte.
*   `garde` (boolean, optionnel) : `true` pour afficher uniquement les pharmacies de garde actives.
*   `gare` (boolean, optionnel) : `true` pour afficher uniquement celles proches d'une gare.

**Réponse (200 OK) :**
```json
[
  {
    "id": 1,
    "nom": "Pharmacie des Cocotiers",
    "ville": "Libreville",
    "quartier": "Centre-ville",
    "telephone": "011740000",
    "horaires": "8h-20h",
    "is_garde": true,
    "lat": 0.3924,
    "lng": 9.4536,
    "location_validated": true,
    "is_verified": true
  },
  ...
]
```

### `POST /api/pharmacy/:id/view`
Enregistre une vue sur une fiche pharmacie.

**Réponse :** `{"success": true}`

## 2. Contributions (Crowdsourcing)

**Note :** Ces endpoints sont limités en fréquence (Rate Limited).

### `POST /api/pharmacy/:id/submit-location`
Propose de nouvelles coordonnées GPS pour une pharmacie.

**Corps de la requête (JSON) :**
```json
{
  "latitude": 0.4123,
  "longitude": 9.4321,
  "name": "Jean Dupont",       // Optionnel
  "phone": "077000000"         // Optionnel
}
```

### `POST /api/pharmacy/:id/submit-info`
Signale une erreur sur une information.

**Corps de la requête (JSON) :**
```json
{
  "field_name": "telephone",   // Champ à corriger
  "proposed_value": "066123456",
  "comment": "Le numéro a changé"
}
```

## 3. Publicité & Marketing

### `GET /api/popups`
Récupère la liste des messages d'information actifs (Maintenance, Alertes).

**Réponse :**
```json
[
  {
    "id": 5,
    "title": "Maintenance",
    "description": "Le site sera en maintenance ce soir.",
    "show_once": true
  }
]
```

### `GET /api/ads/random`
Récupère une publicité aléatoire pondérée par priorité.

**Réponse :**
```json
{
  "id": 12,
  "title": "Promotion Santé",
  "media_type": "image",
  "image_url": "/static/uploads/ads/promo.jpg",
  "cta_url": "https://example.com",
  "skip_delay": 5
}
```

### `POST /api/ads/:id/view`
Compte une impression publicitaire.

### `POST /api/ads/:id/click`
Compte un clic sur une publicité.

## 4. Codes d'Erreur

*   **400 Bad Request :** Paramètres manquants ou invalides (JSON malformé).
*   **404 Not Found :** Ressource (Pharmacie, Pub) introuvable.
*   **429 Too Many Requests :** Limite de débit atteinte (Rate Limit).
*   **500 Internal Server Error :** Erreur serveur non gérée.
