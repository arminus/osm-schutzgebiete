# In[1]:

import overpy
import utils.ovp2geojson as o2p

api = overpy.Overpass()

# # http://norbertrenner.de/osm/bbox.html
# bbox = "47.378,11.078,47.768,13.111" # OBB Süd, ways only
bbox = "48.8696,13.3218,48.9878,13.6033" # Bayerwald - Multipolygons
# bbox = "51.2,12.3095,51.2843,12.5241" # Leipzig - Relation
query = f"""
[bbox:{bbox}];
(
way["boundary"="protected_area"]["protect_class"="14"];
relation["boundary"="protected_area"]["protect_class"="14"];
);
(._;>;);
out body;
"""

result = api.query(query)

allResults = []         # this will be a list of relations and ways which are not part of a relation - i.e. the list we want to check
allRelationWayIds = []  # list of wayIds which are part of a relation (which can be skipped form result.ways here)

for rel in result.relations:
    allResults.append(rel)
    for member in rel.members:
        if (type(member) == overpy.RelationWay):
            way = result.get_way(member.ref, resolve_missing=True)
            allRelationWayIds.append(way.id)

for way in result.ways:
    if not way.id in allRelationWayIds:
        allResults.append(way)

print (f"retrieved {len(allResults)} ways and relations")

# In[2]:
o2p.create(result, allResults, f"test/test.geojson")
# %%
