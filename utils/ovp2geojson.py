from geojson.geometry import LineString
import overpy
import geojson
from geojson import FeatureCollection, Feature, Polygon

import shapely.geometry as geometry
from shapely.ops import linemerge, unary_union, polygonize

def resortWays(result, rel):
    """resort ways of a relation to form a consecutive -->-->--> line
    Parameters:
    - result: the entire overpass query result for way lookup
    - rel: ovperpy.Relation
    Returns:
    - the sorted lonLats as list of lon,lat tuples
    """
    lonLats = []
    relNumber = 0
    for member in rel.members:
        memberLonLats = []
        if (type(member) == overpy.RelationWay):
            way = result.get_way(member.ref, resolve_missing=True)
            # print(f"\nw{way.id}") # proper order in the test case is 59 81 86 85
            wayNodes = way.get_nodes(resolve_missing=True)
            for node in wayNodes:
                # we get these in the order/direction of the way, i.e. we have the usual s->ee<-s problem -> turn around the next
                # print(f"n{node.id} {float(node.lon)},{float(node.lat)}")
                memberLonLats.append((float(node.lon),float(node.lat)))
            if relNumber==0:
                # first member
                lonLats = memberLonLats
            elif relNumber==1:
                # check for e0<--s0==s1-->e1 and e0<--s0==e1<--s1 and turn into -->-->
                s0 = lonLats[0]
                e0 = lonLats[len(lonLats)-1]
                s1 = memberLonLats[0];
                e1 = memberLonLats[len(memberLonLats)-1];

                if s0==s1: # e0<--s0==s1-->e1
                    # print(f"reverting 0")
                    lonLats.reverse()
                if s0==e1: # e0<--s0==e1<--s1
                    # print("reverting 0 and 1")
                    lonLats.reverse()
                    memberLonLats.reverse()

                if (e0==e1): # s0-->e0==e1<--s1
                    # print("reverting 1")
                    memberLonLats.reverse()
                lonLats += memberLonLats
            else:
                # check for s0-->e0==e1<--s1
                e0 = lonLats[len(lonLats)-1]
                e1 = memberLonLats[len(memberLonLats)-1]
                if e0==e1:
                    # print(f"reverting {relNumber}")
                    memberLonLats.reverse()
                lonLats += memberLonLats

            relNumber += 1
        
        # else:
        #     rel = result.get_relation(member.ref, resolve_missing=True)
        #     for relMember in rel.members:
        #         if (type(relMember) == overpy.RelationWay):
        #             way = result.get_way(relMember.ref, resolve_missing=True)
        #             wayNodes = way.get_nodes(resolve_missing=True)
        #             for node in wayNodes:
        #                 lonLats.append((float(node.lon),float(node.lat)))
        #         else:
        #             print(f"Unsupported relation {wayRel.id} of relations of relations")
        else:
            print(f"Unsupported relation {rel.id} of relations")

    return lonLats

def createMultiPoly(result, rel):
    """split member ways of a multipolygon relation into distinct polygons
    from https://gis.stackexchange.com/questions/259422/how-to-get-a-multipolygon-object-from-overpass-ql
    Parameters:
    - result: the entire overpass query result for way lookup
    - rel: overpy.Relation
    Returns:
    - multiLonLats: a list of lists of lon,lat tuples
    """
    ways = []
    for member in rel.members:
        if (type(member) == overpy.RelationWay):
            ways.append(result.get_way(member.ref, resolve_missing=True))

    lss = []
    for ii_w,way in enumerate(ways):
        ls_coords = []
        for node in way.nodes:
            ls_coords.append((node.lon,node.lat)) # create a list of node coordinates
        lss.append(geometry.LineString(ls_coords)) # create a LineString from coords 

    merged = linemerge([*lss]) # merge LineStrings
    borders = unary_union(merged) # linestrings to a MultiLineString
    polygons = polygonize(borders)

    multiLonLats = []
    for polygon in polygons:
        lonLats = []
        for point in list(polygon.exterior.coords):
            lonLats.append((float(point[0]),float(point[1])))
        multiLonLats.append(lonLats)
    return multiLonLats


def create(result, allResults, withStyles, lType, outFile):
    """dump a geojson from 
    Parameters:
    - result:     this is the entire overpass query result - relations and *all* ways
    - allResults: this is the list of ways w/o parent relations and the relations w/o child ways for the main loop
    - withStyles: apply geojson.io styles
    - outFile:    out File name
    Returns:
    - writes outFile
    """
    features = []

    styles = [
        {"stroke": "#555555", "stroke-width": 2, "stroke-opacity": 1, "fill": "#FF0000", "fill-opacity": 0.4},
        {"stroke": "#555555", "stroke-width": 2, "stroke-opacity": 1, "fill": "#FF6A00", "fill-opacity": 0.4},
        {"stroke": "#555555", "stroke-width": 2, "stroke-opacity": 1, "fill": "#FFD800", "fill-opacity": 0.4},
        {"stroke": "#555555", "stroke-width": 2, "stroke-opacity": 1, "fill": "#4CFF00", "fill-opacity": 0.4},
        {"stroke": "#555555", "stroke-width": 2, "stroke-opacity": 1, "fill": "#00FFFF", "fill-opacity": 0.4},
        {"stroke": "#555555", "stroke-width": 2, "stroke-opacity": 1, "fill": "#0094FF", "fill-opacity": 0.4},
        {"stroke": "#555555", "stroke-width": 2, "stroke-opacity": 1, "fill": "#0026FF", "fill-opacity": 0.4},
        {"stroke": "#555555", "stroke-width": 2, "stroke-opacity": 1, "fill": "#B200FF", "fill-opacity": 0.4}
    ]
    unclassifiedStyle = {"stroke": "#555555", "stroke-width": 2, "stroke-opacity": 1, "fill": "#808080", "fill-opacity": 0.4}
    
    for wayRel in allResults:
        lonLats = []
        multiLonLats = []
        if (type(wayRel) == overpy.Way):
            for node in wayRel.nodes:
                lonLats.append((float(node.lon),float(node.lat)))
        else:
            if 'type' in wayRel.tags and wayRel.tags['type'] == "multipolygon":
                multiLonLats = createMultiPoly(result, wayRel)
            else:
                lonLats += resortWays(result, wayRel)
        if (len(lonLats)>0 or len(multiLonLats)>0):
            if withStyles:
                if 'classification' in wayRel.tags:
                    classification = wayRel.tags['classification'].replace("type","")
                    if len(classification) == 1:
                        wayRel.tags.update(styles[int(classification)-1])
                    else:
                        wayRel.tags.update(unclassifiedStyle)
                else:
                    wayRel.tags.update(unclassifiedStyle)
            if (len(multiLonLats)>0):
                for lonLats in multiLonLats:
                    # this must be a polygon
                    features.append(Feature(geometry=Polygon([lonLats]),properties=wayRel.tags))
            else:
                if lType == "LineString":
                    features.append(Feature(geometry=LineString(lonLats),properties=wayRel.tags))
                else:
                    features.append(Feature(geometry=Polygon([lonLats]),properties=wayRel.tags))

    feature_collection = FeatureCollection(features)

    with open(outFile, "w") as gFile:
        geojson.dump(feature_collection, gFile)
