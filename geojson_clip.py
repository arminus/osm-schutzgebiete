from fastkml import kml, styles

import geojson
from geojson import FeatureCollection
from shapely.geometry import Polygon

# extent = Polygon([(11.56,47.55),(11.56,47.83),(12.22,47.83),(12.22,47,55)])

with open("data/MangfallgebirgeShape.kml", 'rt', encoding="utf-8") as myfile:
    doc=myfile.read()
k = kml.KML()
k.from_string(doc)
kFeatures = list(k.features())
f2 = list(kFeatures[0].features())
extent = Polygon(f2[0].geometry)

with open("data/Schongebiete.geojson", "r") as gFile:
    sg = geojson.load(gFile)

k = kml.KML()
ns = '{http://www.opengis.net/kml/2.2}'
d = kml.Document(ns, '20210204', 'SG-Mangfallgebirge', 'OSM Schutzgebiete')
k.append(d)
# f = kml.Folder(ns, 'fid', 'f name', 'f description')
# d.append(f)

count = 0
features = []
for feature in sg['features']:
    geoms = feature.geometry.coordinates
    for geom in geoms:
        p = Polygon(geom)
        if p.intersects(extent):
            features.append(feature)
            count += 1 

            name = feature['properties']['name'] if 'name' in feature['properties'] else ""
            desc = feature['properties']['description'] if 'description' in feature['properties'] else ""
            ed = []
            for prop in feature['properties']:
                if prop != 'name' and prop != 'description':
                    ed.append(kml.Data(name=prop,value=str(feature['properties'][prop])))
            ed = kml.ExtendedData(elements=ed)

            # https://stackoverflow.com/questions/13034702/google-maps-kml-8-digit-hex-code/13036015
            if feature['properties']['classification'] == "type1":
                lcolor = "ff0000ff"
                pcolor = "440000ff"
            elif feature['properties']['classification'] == "type2":
                lcolor = "ffFF6A00"
                pcolor = "440FF6A00"
            else:
                lcolor = "ffFFD800"
                pcolor = "44FFD800"
            ls = styles.LineStyle(ns, color=lcolor, width=3)
            ps = styles.PolyStyle(ns, color=pcolor)
            s1 = styles.Style(styles = [ls,ps])

            pMark = kml.Placemark(ns, feature.properties['@id'], name, desc, extended_data=ed, styles=[s1])
            pMark.geometry = p

            d.append(pMark)

feature_collection = FeatureCollection(features)

# or directly write a KML with props and styles - https://github.com/cleder/fastkml/issues/65

with open("data/Mangfallgebirge.geojson", "w") as gFile:
    geojson.dump(feature_collection, gFile)

with open("data/Mangfallgebirge.kml", "w") as kFile:
    kFile.write(k.to_string(prettyprint=True))


print(f"Exported {count} polygons")