import overpy
import geojson
from geojson import FeatureCollection, Feature, Polygon

# dump a geoson from 
# - result:     this is the entire overpass query result - relations and *all* ways
# - allResults: this is the list of ways w/o parent relations and the relations w/o child ways for the main loop
# -> outfile
# FIXME: multipolygons (Bayerische Wald) are rendered as one Polygon - somehow need to separate them into individual polygons/features
def create(result, allResults, outFile):
    features = []

    styles = [
        {"stroke": "#555555", "stroke-width": 2, "stroke-opacity": 1, "fill": "#FF0000", "fill-opacity": 0.4},
        {"stroke": "#555555", "stroke-width": 2, "stroke-opacity": 1, "fill": "#FF6A00", "fill-opacity": 0.4},
        {"stroke": "#555555", "stroke-width": 2, "stroke-opacity": 1, "fill": "#FFD800", "fill-opacity": 0.4},
        {"stroke": "#555555", "stroke-width": 2, "stroke-opacity": 1, "fill": "#4CFF00", "fill-opacity": 0.4},
        {"stroke": "#555555", "stroke-width": 2, "stroke-opacity": 1, "fill": "#00FFFF", "fill-opacity": 0.4},
        {"stroke": "#555555", "stroke-width": 2, "stroke-opacity": 1, "fill": "#0094FF", "fill-opacity": 0.4},
        {"stroke": "#555555", "stroke-width": 2, "stroke-opacity": 1, "fill": "#0094FF", "fill-opacity": 0.4},
        {"stroke": "#555555", "stroke-width": 2, "stroke-opacity": 1, "fill": "#B200FF", "fill-opacity": 0.4}
    ]
    unclassifiedStyle = {"stroke": "#555555", "stroke-width": 2, "stroke-opacity": 1, "fill": "#808080", "fill-opacity": 0.4}

    for wayRel in allResults:
        lonLats = []
        if (type(wayRel) == overpy.Way):
            for node in wayRel.nodes:
                lonLats.append((float(node.lon),float(node.lat)))
        else:
            relNumber = 0
            for member in wayRel.members:
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
                
                else:
                    print(f"Unsupported relation {wayRel.id} of relations")

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
        if (len(lonLats)>0):
            classification = wayRel.tags['classification'].replace("type","")
            if len(classification) == 1:
                wayRel.tags.update(styles[int(classification)-1])
            else:
                wayRel.tags.update(unclassifiedStyle)
            features.append(Feature(geometry=Polygon([lonLats]),properties=wayRel.tags))

    feature_collection = FeatureCollection(features)

    with open(outFile, "w") as gFile:
        geojson.dump(feature_collection, gFile)
