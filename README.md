## Jupyter notebooks for extraction and analysis of OSM [Schongebiete](https://wiki.openstreetmap.org/wiki/DE:Betretungsverbote_für_Gebiete_im_Winter)

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/arminus/osm-schutzgebiete/HEAD)
### OSMSchutzgebiete.ipynb
* used to track mapping progress, in particular of to be taged ways
* extracts all protect_class=14 ways and relations and contained ways
* output goes into a folium map which can be statically deployed somewhere

### OSMSchutzgebiete2GeoJSON.ipynb
* "direct" translation of the Queries in the [Wiki](https://wiki.openstreetmap.org/wiki/DE:Betretungsverbote_für_Gebiete_im_Winter)
* extracts all data live from overpass and uses the queries to classify from type1 to type8 according to the definition
* produces a geojson with respective properties, e.g.

```
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    ...
                ]
            },
            "properties": {
                "access": "no",
                "boundary": "protected_area",
                "protect_class": "14",
                "protection_title": "Gebietsverbot",
                "classification": "type1",
                "stroke": "#555555",
                "stroke-width": 2,
                "stroke-opacity": 1,
                "fill": "#ffff80",
                "fill-opacity": 0.4
            }
        },
        ....
    ]
}
            
```
* classification: the type (1-8) as determined by the queries
* stroke*/fill*: styles for https://geojson.io
  * geojson.io has limited styling support, so this visualization uses the following fill color scheme:
  * ![](images/legend.png)
* nevertheless, the explit classification tag can be used to simplify downstream processing
* further limitations and ToDos in the notebook

---

## General Links

* https://github.com/njanakiev/osm-data-science/blob/master/docs/osm-data-science.ipynb
* https://towardsdatascience.com/loading-data-from-openstreetmap-with-python-and-the-overpass-api-513882a27fd0

## Geopandas install on Windows:
(currently not used)

```
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
```

(-> https://stackoverflow.com/questions/54734667/error-installing-geopandas-a-gdal-api-version-must-be-specified-in-anaconda)

pip install ipykernel
ipython kernel install --user --name=projectname

(-> https://anbasile.github.io/posts/2017-06-25-jupyter-venv/)

## Folium

https://python-visualization.github.io/folium/quickstart.html#Getting-Started