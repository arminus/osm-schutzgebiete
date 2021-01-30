#!/bin/bash

BASE=~/osm/scripts/python
OUTDIR=~/osm/html/osm

cd $BASE
source .venv/bin/activate

python ./OSMSchutzgebiete.py silent
sleep 5
python ./OSMSchutzgebiete.py skipways silent
sleep 5
python ./OSMSchutzgebiete2GeoJSON.py silent

cp data/Schongebiete.geojson $OUTDIR
cp html-out/Schongebiete-Alpenrand-BY.html $OUTDIR
cp html-out/Schongebiete-Alpenrand-BY-Wege.html $OUTDIR
