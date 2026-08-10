#!/bin/bash
set -e

DB_FILE="/code/data/pois.db"
REGION_URL=${OSM_REGION_URL:-"https://download.geofabrik.de/europe/france/ile-de-france-latest.osm.pbf"}
PBF_FILE="/code/data/region.osm.pbf"
FILTERED_PBF="/code/data/filtered.osm.pbf"
JSON_FILE="/code/data/filtered.json"

if [ ! -f "/code/data/.import_success" ]; then
    echo "Local database not found or incomplete. Starting download and import process..."
    
    # Clean up any broken db from previous failed runs
    rm -f "$DB_FILE"

    
    mkdir -p /code/data
    
    echo "1/4 Downloading OSM data from ${REGION_URL}..."
    wget -qO "$PBF_FILE" "$REGION_URL"
    
    echo "2/4 Filtering points of interest (amenity, shop, tourism, historic, leisure, sport, public_transport)..."
    # Using osmium to extract relevant nodes, ways (buildings), and relations (areas)
    osmium tags-filter "$PBF_FILE" nwr/amenity nwr/shop nwr/tourism nwr/historic nwr/leisure nwr/sport nwr/highway=bus_stop nwr/public_transport -o "$FILTERED_PBF" --overwrite
    
    echo "3/4 Converting to JSON format..."
    osmium export "$FILTERED_PBF" -f geojsonseq -o "$JSON_FILE" --overwrite
    
    echo "4/4 Importing into local SQLite database..."
    python /code/app/importer.py
    
    echo "Cleaning up temporary files..."
    rm -f "$PBF_FILE" "$FILTERED_PBF" "$JSON_FILE"
    
    # Mark as successfully imported
    touch /code/data/.import_success
    echo "Initialization complete!"
else
    echo "Local database found and import was successful previously. Skipping import."
fi

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
