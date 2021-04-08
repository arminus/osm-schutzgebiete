import geojson
from geojson import FeatureCollection
from shapely.geometry import LineString, Polygon

# http://norbertrenner.de/osm/bbox.html
extent = Polygon([(9.65,47.23),(13.13,47.23),(13.13,47.79),(9.65,47.79),(9.65,47.23)])

with open("C:/Data/Development/JavaScript/DigitizeThePlanet/data/SchongebieteWays.geojson", "r") as gFile:
    sg = geojson.load(gFile)

count = 0
features = []
for feature in sg['features']:
    p = LineString(feature.geometry.coordinates)
    if p.intersects(extent):
        features.append(feature)
        count += 1 
feature_collection = FeatureCollection(features)

with open("C:/Data/Development/JavaScript/DigitizeThePlanet/data/SchongebieteWays-BY.geojson", "w") as gFile:
    geojson.dump(feature_collection, gFile)

print(f"Exported {count} ways")