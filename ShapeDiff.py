# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# Read existing OSM Schutzgebiete from geojson export
# Read (updated) DAV Shapefile
# 
# compare to find new or changed polygons and create an epsg:4326 shape file only with changed/new polygons for import in JOSM
# 
# Note: due to some epsg:4326 <-> epsg:31468 reprojection issue the geojson slightly (~ 2 meters) deviates from the DAV shapes
# -> fuzzy matching with intersection over union approach is taken
# 
# Deleted polygons are not yet detected

# %%
import fiona
import pyproj
from shapely.geometry import shape, mapping
from shapely.ops import transform
from shapely.geometry import Polygon
from rdp import rdp

import copy

def dpr(poly,epsilon=0.000005):
    coords = []
    for x,y in poly.exterior.coords:
        coords.append([x,y])
    coords = rdp(coords, epsilon=epsilon)
    return Polygon(coords)

# for tests
# origShapeFile = 'E:/OSM/Schutzgebiete/Rauhkopf.geojson' # epsg:4326
# newShapeFile = 'E:/OSM/Schutzgebiete/Rauhkopf/Rauhkopf.shp' # epsg:31468

# real files
origShapeFile = 'E:/OSM/Schutzgebiete/Schongebiete.geojson' # epsg:4326
newShapeFile = 'E:/OSM/Schutzgebiete/200126_Schutzgebiete_By-Karten/Schutzgebiete_BY-Karten.shp' # epsg:31468
# newShapeFile = 'E:/OSM/Schutzgebiete/Schongebiete-Alt/Schongebiete.shp' # epsg:31468

origShapeFile = 'E:/OSM/Schutzgebiete/Test/Bruennstein.geojson' # epsg:4326
newShapeFile = 'E:/OSM/Schutzgebiete/Test/Bruennstein-DAV.shp' # epsg:31468

shapesUpdateFile = 'E:/OSM/Schutzgebiete/New/new-shapes.shp'

oldFeatures = []
with fiona.open(origShapeFile) as input:
    oldCrs = input.crs
    for feat in input:
        if feat['geometry'] != None and len(feat['geometry']['coordinates'][0]) > 2:
            poly = shape(feat['geometry'])
            poly = dpr(poly)
            feat['geometry'] = mapping(poly)
            oldFeatures.append(feat)
size = len(oldFeatures);          
print(f"OSM-Gebiete in {origShapeFile}: {size} / {oldCrs['init']}")


# %%
# import matplotlib.pyplot as plt
# poly = shape(oldFeatures[300]['geometry'])
# x,y = poly.exterior.xy
# plt.plot(x,y)


# %%
# read and 3D to 2D convert abnd reproject DAV shapefile

project = pyproj.Transformer.from_proj(
    pyproj.Proj(init='epsg:31468'), # source coordinate system
    pyproj.Proj(init='epsg:4326')) # destination coordinate system

newFeatures = []
with fiona.open(newShapeFile) as input:
    schema = input.schema
    crs = input.crs
    if crs['init'] != "epsg:31468":
        print(f"Bad CRS {crs['init']} in {newShapeFile}")
        exit

    driver = input.driver
    for feat in input:
        if feat['geometry'] != None:
            if len(feat['geometry']['coordinates']) > 1:
                # multipolygons - code to be improved...
                for pfeat in feat['geometry']['coordinates']:
                    try: # some are len(1) lists, some aren't ?!
                        poly = Polygon(pfeat[0])
                    except:
                        poly = Polygon(pfeat)
                    poly = transform(lambda x, y, z=None: (x, y), poly)
                    poly = transform(project.transform, poly)
                    feat2 = copy.deepcopy(feat)
                    feat2['geometry'] = mapping(dpr(poly))
                    newFeatures.append(feat2)
                continue
            if len(feat['geometry']['coordinates'][0]) < 3:
                print("Skipping 2-point line")
                continue
            # transform 3D to 2D
            poly = shape(feat['geometry'])
            poly = transform(lambda x, y, z=None: (x, y), poly)
            poly = transform(project.transform, poly)
            feat['geometry'] = mapping(dpr(poly))
            newFeatures.append(feat)

size = len(newFeatures);          
print(f"Gebiete in {newShapeFile}: {size}")


# %%
geod = pyproj.Geod(ellps='WGS84')
import statistics

# both polygons need to be in epsg:4326
def is_shifted(poly1, poly2):
    # poly1 = normalize(poly1)
    # poly2 = normalize(poly2)
    p1c = []
    p2c = []
    for x,y in poly1.exterior.coords:
        p1c.append([x,y])
    for x,y in poly2.exterior.coords:
        p2c.append([x,y])

    dists = []
    maxDist = 0
    for i in range(0,len(p2c)):
        azimuth1, azimuth2, distance = geod.inv(p1c[i][0], p1c[i][1], p2c[i][0], p2c[i][1])
        print(i, p1c[i][0], p1c[i][1], p2c[i][0], p2c[i][1], distance)
        if distance > maxDist:
            maxDist = distance;
        dists.append(distance)

    print(maxDist)
    print(statistics.stdev(dists))
    print(statistics.pvariance(dists))

    if maxDist < 3.5 and statistics.stdev(dists) < 0.1 and statistics.pvariance(dists) < 0.001:
        return True
    else:
        return False


# %%
# https://www.reddit.com/r/gis/comments/mcw0y0/comparing_two_linestrings_with_shapely/

# from collections import OrderedDict
# dummyProps = OrderedDict([('Id', None),('Name', ''),('Regelung', '')])

newCount = 0 
foundCount = 0
shiftCount = 0
with fiona.open(shapesUpdateFile, 'w', crs={'init':'epsg:4326'}, driver='ESRI Shapefile', schema=schema) as out:
    for newFeature in newFeatures:
        # apply a buffer to avoid TopologyException: Input geom 1 is invalid: Self-intersection at or near point
        # https://www.programmersought.com/article/69515213493/
        newGeom = Polygon(shape(newFeature['geometry']).exterior).buffer(0.0001)
        found = False
        shifted = False
        for oldFeature in oldFeatures:
            try:
                oldGeom = Polygon(shape(oldFeature['geometry'])).buffer(0.0001)
                shifted = is_shifted(newGeom, oldGeom)
                if shifted:
                    shiftCount += 1
            except Exception as ex:
                # FIXME: 'MultiPolygon' object has no attribute 'exterior' - why ?!?! - MultiPolygons get removed above?!
                # print(ex)
                # print(oldFeature['geometry'])
                continue
            if not shifted:
                try:
                    # https://www.pyimagesearch.com/2016/11/07/intersection-over-union-iou-for-object-detection/
                    iou = newGeom.intersection(oldGeom).area / newGeom.union(oldGeom).area
                except Exception as ex:
                    print(ex)
                    print(newGeom)
                    print(oldGeom)
            if iou > 0.985 or shifted:
                found = True
                foundCount +=1
        if not found and not shifted:
            newCount += 1
            out.write(newFeature)
print(f"Gefundene Gebiete = {foundCount}")
print(f"Shifted Gebiete = {shiftCount}")
print(f"Neue/Geänderte Gebiete = {newCount} -> in {shapesUpdateFile}")
# takes ~ 185secs


