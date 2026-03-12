# main.py corrigé
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import geopandas as gpd
import json
import os
import pandas as pd
import traceback

app = FastAPI(title="API Parcelles", description="API pour les données cadastrales")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SHAPEFILE_PATH = os.path.join(os.path.dirname(__file__), "DATA", "parcelles.shp")

# Variables globales avec valeurs par défaut
parcelles = gpd.GeoDataFrame()
parcelles_geojson = {"type": "FeatureCollection", "features": []}

# Chargement des données
try:
    print("=" * 50)
    print("🚀 DÉMARRAGE DE L'API")
    print("=" * 50)
    
    if not os.path.exists(SHAPEFILE_PATH):
        print(f"❌ ERREUR: Fichier non trouvé: {SHAPEFILE_PATH}")
    else:
        print(f"📁 Fichier trouvé: {SHAPEFILE_PATH}")
        print("Chargement du shapefile...")
        
        # 1. Charger le shapefile
        parcelles = gpd.read_file(SHAPEFILE_PATH)
        print(f"✅ Shapefile chargé: {len(parcelles)} entités")
        
        # 2. Vérifier et gérer le CRS
        if parcelles.crs is None:
            print("⚠️ CRS non défini - tentative de détection...")
            # Essayer CRS français communs
            try:
                # Souvent les données cadastrales sont en Lambert 93
                parcelles = parcelles.set_crs(epsg=2154)
                print("✅ CRS défini sur EPSG:2154 (Lambert 93)")
            except:
                parcelles = parcelles.set_crs(epsg=4326)
                print("✅ CRS défini sur EPSG:4326 (WGS84)")
        
        # 3. Convertir en WGS84 pour Leaflet
        try:
            if parcelles.crs.to_epsg() != 4326:
                parcelles = parcelles.to_crs(epsg=4326)
                print("✅ Conversion en EPSG:4326 réussie")
        except Exception as e:
            print(f"⚠️ Impossible de convertir le CRS: {e}")
        
        # 4. Limiter pour la performance
        parcelles = parcelles.head(50)
        print(f"📊 Limité à {len(parcelles)} parcelles")
        
        # 5. Gestion intelligente des colonnes
        cols_to_keep = ["geometry"]
        
        # Chercher l'identifiant de parcelle (différents noms possibles)
        id_variations = ['numero_parcelle', 'id_parcelle', 'parcelle', 'id', 
                        'NUMERO', 'ID_PARC', 'CODE_PAR', 'identifiant', 'section']
        
        id_found = False
        for id_col in id_variations:
            if id_col in parcelles.columns:
                cols_to_keep.insert(0, id_col)
                print(f"✅ Colonne identifiant trouvée: {id_col}")
                id_found = True
                break
        
        # Si aucun identifiant trouvé, en créer un
        if not id_found:
            parcelles['numero_parcelle'] = [f"PARC-{i:04d}" for i in range(1, len(parcelles) + 1)]
            cols_to_keep.insert(0, "numero_parcelle")
            print("⚠️ Aucun identifiant trouvé - création d'identifiants artificiels")
        
        # Garder seulement les colonnes nécessaires
        existing_cols = [col for col in cols_to_keep if col in parcelles.columns]
        parcelles = parcelles[existing_cols]
        print(f"📋 Colonnes conservées: {existing_cols}")
        
        # 6. Nettoyage des types de données
        for col in parcelles.columns:
            if col != "geometry":
                try:
                    if pd.api.types.is_datetime64_any_dtype(parcelles[col]):
                        parcelles[col] = parcelles[col].astype(str)
                        print(f"🕐 Conversion date: {col}")
                    elif pd.api.types.is_numeric_dtype(parcelles[col]):
                        parcelles[col] = parcelles[col].astype(float)
                        print(f"🔢 Conversion numérique: {col}")
                    else:
                        parcelles[col] = parcelles[col].astype(str)
                        print(f"📝 Conversion texte: {col}")
                except Exception as e:
                    print(f"⚠️ Erreur conversion {col}: {e}")
        
        # 7. Conversion en GeoJSON
        parcelles_geojson = json.loads(parcelles.to_json())
        print(f"✅ Conversion GeoJSON réussie")
        print(f"🎉 {len(parcelles)} parcelles chargées avec succès")
        
        # 8. Afficher un aperçu
        print("\n📊 APERÇU DES DONNÉES:")
        print(f"   - CRS: {parcelles.crs}")
        print(f"   - Colonnes: {list(parcelles.columns)}")
        print(f"   - Première parcelle: {parcelles.iloc[0].to_dict() if len(parcelles) > 0 else 'Aucune'}")

except Exception as e:
    print(f"❌ ERREUR CRITIQUE: {e}")
    traceback.print_exc()
    print("🔄 Utilisation des données par défaut (vides)")
    parcelles = gpd.GeoDataFrame()
    parcelles_geojson = {"type": "FeatureCollection", "features": []}

print("=" * 50)

@app.get("/")
def root():
    """Route racine avec informations de l'API"""
    return {
        "message": "API Parcelles - Aisne (02)",
        "status": "online" if len(parcelles) > 0 else "degraded",
        "parcelles_count": len(parcelles),
        "crs": str(parcelles.crs) if hasattr(parcelles, 'crs') else None,
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Cette page"},
            {"path": "/parcelles", "method": "GET", "description": "Toutes les parcelles (GeoJSON)"},
            {"path": "/parcelles/{index}", "method": "GET", "description": "Une parcelle spécifique"},
            {"path": "/parcelles/count", "method": "GET", "description": "Nombre de parcelles"},
            {"path": "/parcelles/columns", "method": "GET", "description": "Colonnes disponibles"},
            {"path": "/health", "method": "GET", "description": "Santé de l'API"},
            {"path": "/map", "method": "GET", "description": "Interface cartographique"}
        ]
    }

@app.get("/parcelles")
def get_parcelles():
    """Retourne toutes les parcelles en GeoJSON"""
    return JSONResponse(content=parcelles_geojson)

@app.get("/parcelles/count")
def get_parcelles_count():
    """Retourne le nombre de parcelles"""
    return {"count": len(parcelles)}

@app.get("/parcelles/columns")
def get_parcelles_columns():
    """Retourne les colonnes disponibles"""
    if len(parcelles) > 0:
        return {
            "columns": [col for col in parcelles.columns if col != "geometry"],
            "total": len([col for col in parcelles.columns if col != "geometry"]),
            "crs": str(parcelles.crs) if hasattr(parcelles, 'crs') else None
        }
    return {"columns": [], "total": 0, "crs": None}

@app.get("/parcelles/{index}")
def get_parcelle(index: int):
    """Retourne une parcelle spécifique par son index"""
    if len(parcelles) == 0:
        raise HTTPException(status_code=503, detail="Données non disponibles")
    
    if index < 0 or index >= len(parcelles):
        raise HTTPException(status_code=404, detail=f"Parcelle index {index} non trouvée (max: {len(parcelles)-1})")
    
    parcelle = parcelles.iloc[[index]]
    return json.loads(parcelle.to_json())

@app.get("/health")
def health_check():
    """Vérification de la santé de l'API"""
    return {
        "status": "healthy" if len(parcelles) > 0 else "unhealthy",
        "parcelles_loaded": len(parcelles) > 0,
        "parcelles_count": len(parcelles),
        "crs": str(parcelles.crs) if hasattr(parcelles, 'crs') else None,
        "columns": [col for col in parcelles.columns if col != "geometry"] if len(parcelles) > 0 else []
    }

@app.get("/map")
def map_page():
    """Page de la carte interactive"""
    return FileResponse("static/index.html")

# À la fin de votre main.py, ajoutez ceci :
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)