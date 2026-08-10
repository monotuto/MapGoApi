from fastapi import FastAPI, HTTPException, Query
import sqlite3
import json
from typing import List, Optional
import os

app = FastAPI(title="POI API (Offline)", description="API to fetch Points of Interest using a local SQLite database.")

DB_PATH = "/code/data/pois.db"

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=503, detail="Database is not ready yet. Please wait for the initial import to finish.")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/pois")
def get_pois(
    min_lat: float = Query(..., description="Minimum Latitude (e.g., 48.85)"),
    min_lon: float = Query(..., description="Minimum Longitude (e.g., 2.34)"),
    max_lat: float = Query(..., description="Maximum Latitude (e.g., 48.86)"),
    max_lon: float = Query(..., description="Maximum Longitude (e.g., 2.35)"),
    poi_types: Optional[List[str]] = Query(
        ["bench", "waste_basket", "shop", "restaurant", "cafe", "museum", "park", "bus_stop", "pharmacy", "hospital", "supermarket", "bakery", "atm"], 
        description="List of POI types to fetch. Default includes many common types."
    )
):
    """
    Fetch points of interest within a bounding box from the local database.
    """
    if min_lat >= max_lat or min_lon >= max_lon:
        raise HTTPException(status_code=400, detail="Invalid bounding box coordinates.")

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Prepare the query
    placeholders = ','.join('?' for _ in poi_types)
    query = f"""
        SELECT id, lat, lon, type, name, tags 
        FROM pois 
        WHERE lat BETWEEN ? AND ? 
          AND lon BETWEEN ? AND ? 
          AND type IN ({placeholders})
        LIMIT 1000
    """
    
    # Parameters for the query
    params = [min_lat, max_lat, min_lon, max_lon] + poi_types
    
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "id": row["id"],
                "lat": row["lat"],
                "lon": row["lon"],
                "type": row["type"],
                "name": row["name"],
                "tags": json.loads(row["tags"]) if row["tags"] else {}
            })
            
        return {"count": len(results), "pois": results}
    
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.get("/health")
def health_check():
    return {"status": "ok"}
