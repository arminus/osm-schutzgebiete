#!/bin/bash

BASE=~/osm/scripts/python
OUTDIR=~/osm/html/osm
SHAPESDIR=~/osm/data/Shapes/Schongebiete

LOG=${BASE}/update.log

cd $BASE
source .venv/bin/activate

python ./OSMSchutzgebiete.py silent 2>&1 >> $LOG
sleep 5
python ./OSMSchutzgebiete.py skipways silent 2>&1 >> $LOG
sleep 5
python ./OSMSchutzgebiete2GeoJSON.py silent 2>&1 >> $LOG

cp data/Schongebiete.geojson $OUTDIR 2>&1 >> $LOG
cp data/Schongebiete-ColorStyles.geojson $OUTDIR 2>&1 >> $LOG
cp html-out/Schongebiete-Alpenrand-BY.html $OUTDIR 2>&1 >> $LOG
cp html-out/Schongebiete-Alpenrand-BY-Wege.html $OUTDIR 2>&1 >> $LOG

if [ ! -d data/Shapes ]; then
    mkdir data/Shapes
fi
cd data/Shapes
ogr2ogr -f "ESRI Shapefile" Schongebiete.shp ../Schongebiete.geojson 2>&1 >> $LOG
cp -f * $SHAPESDIR

cd $OUTDIR
ogr2ogr -f "KML" -a_srs "EPSG:4326" Schongebiete.kml Schongebiete.geojson 2>&1 >> $LOG
geojsontoosm Schongebiete.geojson > Schongebiete.osm

