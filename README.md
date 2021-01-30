## Some Jupyter notebooks for extractioin and analysis of OSM [Schongebiete](https://wiki.openstreetmap.org/wiki/DE:Betretungsverbote_für_Gebiete_im_Winter)
## General Links

https://github.com/njanakiev/osm-data-science/blob/master/docs/osm-data-science.ipynb
https://towardsdatascience.com/loading-data-from-openstreetmap-with-python-and-the-overpass-api-513882a27fd0

## Geopandas install on Windows:

python -m venv .env
.env\Scripts\activate

pip install wheel
pip install pipwin

pipwin install numpy
pipwin install pandas
pipwin install shapely
pipwin install gdal
pipwin install fiona
pipwin install pyproj
pipwin install six
pipwin install rtree
pipwin install geopandas

(-> https://stackoverflow.com/questions/54734667/error-installing-geopandas-a-gdal-api-version-must-be-specified-in-anaconda)

pip install ipykernel
ipython kernel install --user --name=projectname

(-> https://anbasile.github.io/posts/2017-06-25-jupyter-venv/)

## Folium

https://python-visualization.github.io/folium/quickstart.html#Getting-Started