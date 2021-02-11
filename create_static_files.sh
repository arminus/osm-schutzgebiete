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

rm html-out/*
python ./OSMSchutzgebiete.py silent >> $LOG 2>&1 
[ ! -f html-out/Schongebiete-Alpenrand-BY-Wege.html ] && error
cp html-out/Schongebiete-Alpenrand-BY-Wege.html $OUTDIR >> $LOG 2>&1 
sleep 5

python ./OSMSchutzgebiete.py skipways silent >> $LOG 2>&1 
cp html-out/Schongebiete-Alpenrand-BY.html $OUTDIR >> $LOG 2>&1 
[ ! -f html-out/Schongebiete-Alpenrand-BY.html ] && error
sleep 5

rm -rf data/*
python ./OSMSchutzgebiete2GeoJSON.py silent >> $LOG 2>&1 
[ ! -f data/Schongebiete.geojson -o ! -r data/SchongebieteWays.geojson ] && error
cp data/Schongebiete.geojson $OUTDIR >> $LOG 2>&1 
cp data/Schongebiete-ColorStyles.geojson $OUTDIR >> $LOG 2>&1 
cp data/SchongebieteWays.geojson $OUTDIR >> $LOG 2>&1 
cp data/statistics.json $OUTDIR/../schongebiete/data >> $LOG 2>&1 
cp data/statistics.json statistics/statistics.${DATE}.json
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

if [ -f ${LOG} ]; then
    echo "$(date) finshed" >> ${LOG}
    cat ${LOG} >> ${FLOG}
    rm ${LOG}
fi
