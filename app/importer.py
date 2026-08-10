import json
import sqlite3
import os

DB_PATH = "/code/data/pois.db"
JSON_PATH = "/code/data/filtered.json"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table for POIs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pois (
            id INTEGER PRIMARY KEY,
            lat REAL,
            lon REAL,
            type TEXT,
            name TEXT,
            tags TEXT
        )
    ''')
    
    # Create spatial indices
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_lat ON pois(lat)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_lon ON pois(lon)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON pois(type)')
    
    conn.commit()
    return conn

def import_data(conn):
    print("Starting data import into SQLite...")
    if not os.path.exists(JSON_PATH):
        print(f"Error: {JSON_PATH} not found.")
        return

    cursor = conn.cursor()
    
    # Clear existing data just in case
    cursor.execute('DELETE FROM pois')
    
    count = 0
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        features = data.get("features", [])
        for feature in features:
            props = feature.get("properties", {})
            geom = feature.get("geometry", {})
            
            if geom.get("type") == "Point":
                lon, lat = geom.get("coordinates", [0, 0])
                osm_id = feature.get("id", "").replace("node/", "")
                
                try:
                    osm_id = int(osm_id)
                except ValueError:
                    continue
                    
                poi_type = (
                    props.get("amenity") or 
                    props.get("shop") or 
                    props.get("tourism") or 
                    props.get("historic") or 
                    props.get("leisure") or 
                    props.get("sport") or 
                    props.get("public_transport") or 
                    props.get("highway") or 
                    "unknown"
                )
                name = props.get("name", "Unnamed")
                tags = json.dumps(props)
                
                cursor.execute(
                    'INSERT INTO pois (id, lat, lon, type, name, tags) VALUES (?, ?, ?, ?, ?, ?)',
                    (osm_id, lat, lon, poi_type, name, tags)
                )
                count += 1
                
    conn.commit()
    print(f"Import complete! {count} POIs inserted.")

if __name__ == "__main__":
    conn = init_db()
    import_data(conn)
    conn.close()
