#!/bin/bash

BASE=~/osm/scripts/python
OUTDIR=~/osm/html/osm
SHAPESDIR=~/osm/data/Shapes/Schongebiete
DATE=$(date +%F)
LOG=${BASE}/update.log.$$
FLOG=${BASE}/update.log

echo "$(date) starting update..." > ${LOG}

function error {
    cat ${LOG} |sed 's/\r//g' | mailx -r info@xctrails.org -s "Schongebiete Update Error" info@xctrails.org
    cat ${LOG} >> ${FLOG}
    rm ${LOG}
    exit
}

cd $BASE
source .venv/bin/activate

OVP_SLEEP=120

rm html-out/*
python ./OSMSchutzgebiete.py silent >> $LOG 2>&1 
[ ! -f html-out/Schongebiete-Alpenrand-BY-Wege.html ] && error
cp html-out/Schongebiete-Alpenrand-BY-Wege.html $OUTDIR >> $LOG 2>&1 

sleep $OVP_SLEEP
python ./OSMSchutzgebiete.py skipways silent >> $LOG 2>&1 
cp html-out/Schongebiete-Alpenrand-BY.html $OUTDIR >> $LOG 2>&1 
[ ! -f html-out/Schongebiete-Alpenrand-BY.html ] && error

rm -rf data/*

sleep $OVP_SLEEP
python ./OSMSchutzgebieteCheck.py silent >> $LOG 2>&1 
[ ! -f data/SchongebieteTagFehler.geojson ] && error
cp data/SchongebieteTagFehler.geojson $OUTDIR >> $LOG 2>&1 

sleep $OVP_SLEEP
python ./OSMSchutzgebiete2GeoJSON.py silent >> $LOG 2>&1 
[ ! -f data/Schongebiete.geojson -o ! -r data/SchongebieteWays.geojson ] && error
cp data/Schongebiete.geojson $OUTDIR >> $LOG 2>&1 
cp data/Schongebiete-ColorStyles.geojson $OUTDIR >> $LOG 2>&1 
cp data/SchongebieteWays.geojson $OUTDIR >> $LOG 2>&1 
cp data/statistics.json $OUTDIR/../schongebiete/data >> $LOG 2>&1 
cp data/statistics.json statistics/statistics.${DATE}.json

# the following needs to correspond to the respective names/settings for the layer names (-nln) and dataseource in geoserver
ogr2ogr -f "PostgreSQL" PG:"dbname=schongebiete user=postgres" data/Schongebiete.geojson -nln geojson -overwrite >> $LOG 2>&1 
[ $? -ne 0 ] && error
ogr2ogr -f "PostgreSQL" PG:"dbname=schongebiete user=postgres" data/SchongebieteWays.geojson -nln geojsonWays -overwrite >> $LOG 2>&1 
[ $? -ne 0 ] && error

if [ ! -d data/Shapes ]; then
    mkdir data/Shapes
fi
cd data/Shapes
ogr2ogr -f "ESRI Shapefile" Schongebiete.shp ../Schongebiete.geojson >> $LOG 2>&1 
cp -f * $SHAPESDIR

cd $OUTDIR
ogr2ogr -f "KML" -a_srs "EPSG:4326" Schongebiete.kml Schongebiete.geojson > /dev/null 2>&1 
geojsontoosm Schongebiete.geojson > Schongebiete.osm

date=$(date +'%d.%m.%Y %H:%M'|sed 's/\s/%20/g')
wget -q -O ~/osm/html/schongebiete/data/status.svg "https://img.shields.io/static/v1?label=updated&message=${date}&color=green"

if [ -f ${LOG} ]; then
    echo "$(date) finshed" >> ${LOG}
    cat ${LOG} >> ${FLOG}
    rm ${LOG}
fi

