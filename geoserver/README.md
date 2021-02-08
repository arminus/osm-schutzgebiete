## Styles for GeoServer:
All styles based on https://wiki.openstreetmap.org/wiki/DE:Betretungsverbote_f%C3%BCr_Gebiete_im_Winter

SLD conditions are using the type1-type8 classification tag/property
(Note: property gets shortened to "classifica" when this is imported via Shape Files into geoserver)

* https://docs.geoserver.org/stable/en/user/styling/sld/index.html
* https://docs.geoserver.org/stable/en/user/styling/sld/cookbook/polygons.html
* https://docs.geoserver.org/latest/en/user/styling/sld/extensions/pointsymbols.html

* content.ftl -> this goes into webapps/geoserver/data/templates for the GetFeatureInfo HTML return

### Adding the layers with Leaflet
(presently not enabled for CORS, URL is subject to change)

```
var wmsLayer = L.tileLayer.wms("https://www.xctrails.org/geoserver/schongebiete/wms", {
    layers: 'schongebiete:geojson',
    format: 'image/png',
    styles: 'schongebiete-full-pgis',
    transparent: true
});

var wmsLayerWays = L.tileLayer.wms("https://www.xctrails.org/geoserver/schongebiete/wms", {
    layers: 'schongebiete:geojsonways',
    format: 'image/png',
    styles: 'schongebiete-ways-pgis',
    transparent: true,
    legend: legend,
    openLegendOnLoad: true
});
```
