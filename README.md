# API Parcelles Cadastrales - Aisne (02)

Application web permettant de visualiser les parcelles cadastrales du département de l'Aisne (02) sur une carte interactive, avec une API FastAPI en backend et Leaflet en frontend.


## Technologies utilisées

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, JavaScript, Leaflet
- **Données géospatiales**: GeoPandas, Shapefile
- **Carte**: OpenStreetMap

## Structure du projet

```
projet_parcelles/
│
├── main.py                 # Application FastAPI principale
├── README.md               # Documentation du projet
├── requirements.txt        # Dépendances Python
│
├── DATA/                   # Dossier des données
│   └── parcelles.shp       # Shapefile des parcelles (Aisne)
│
└── static/                 # Fichiers statiques
    └── index.html          # Interface utilisateur
    │
└── screenshots/            # Captures d'écran de l'application
    ├── 1.png
    ├── 2.png
    └── 3.png
```

## Installation

### Étapes d'installation

1. **Installer les dépendances**
```bash
pip install -r requirements.txt
```


## Lancement de l'application

1. **Démarrer le serveur**
```bash
python -m uvicorn main:app --reload
```

2. **Accéder à l'application**
   - Interface web: http://127.0.0.1:8000/map
   - API Parcelles: http://127.0.0.1:8000/parcelles

## Points d'API disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Informations sur l'API |
| `/parcelles` | GET | Récupère toutes les parcelles (GeoJSON) |
| `/map` | GET | Affiche l'interface cartographique |


## Utilisation

### Interface cartographique

1. Ouvrez votre navigateur à l'adresse `http://127.0.0.1:8000/map`
2. La carte affiche automatiquement toutes les parcelles du shapefile
3. Cliquez sur une parcelle pour voir son numéro
4. Utilisez les contrôles de zoom pour naviguer

### API

```python
# Exemple d'appel API avec Python
import requests

response = requests.get("http://127.0.0.1:8000/parcelles")
parcelles = response.json()
print(f"Nombre de parcelles: {len(parcelles['features'])}")
```

## Configuration

### Limitation des données
Par défaut, l'API charge les 500 premières parcelles pour des raisons de performance. Pour modifier ce comportement :

```python
# Dans main.py
parcelles = parcelles.head(1000)  # Charge 1000 parcelles
```

### Format des données
- Projection: EPSG:4326 (WGS84)
- Format de sortie: GeoJSON
- Colonnes conservées: geometry, numero_parcelle

Interface principale
![Capture 1](screenshots/1.png)
*Vue d'ensemble de la carte avec les parcelles*

### Détail d'une parcelle
![Capture 2](screenshots/2.png)
*Affichage du popup avec le numéro de parcelle*

### Vue rapprochée
![Capture 3](screenshots/3.png)
*Zoom sur un groupe de parcelles*

## Auteur

Hamza Nasr

## Licence

Ce projet est réalisé dans le cadre d'un exercice technique.

---

**Note**: Projet développé dans le cadre d'un exercice interne - Données cadastrales de l'Aisne (02)