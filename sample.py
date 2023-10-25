
# laneletの読み込み
import numpy as np
import lanelet2
from lanelet2_extension.projection import MGRSProjector
import lanelet2.geometry as lg2
import lanelet2_extension.geometry as lg2_extension

def print_layer(layer, layerName):
    print("IDs in " + layerName)
    print(sorted([elem.id for elem in layer]))

proj = MGRSProjector(lanelet2.io.Origin(0.0, 0.0))
ll2_map = lanelet2.io.load("/home/keisuke-ota/autoware_map/followtrajectoryaction_scenario/lanelet2_map.osm", proj)

layers = {
#        "Points": ll2_map.pointLayer,
#        "Line Strings": ll2_map.lineStringLayer,
        "Polygons": ll2_map.polygonLayer,
        "Lanelets": ll2_map.laneletLayer,
        "Areas": ll2_map.areaLayer,
#        "Regulatory Elements": ll2_map.regulatoryElementLayer,
    }

for layer_name, layer in layers.items():
    print_layer(layer, layer_name)


lanelet56 = ll2_map.laneletLayer.get(1119)

# geometry
## length, area
print(
f"""The length of left bound, right bound and centerline of lanelet56 is \
{lg2.length(lanelet56.leftBound)}, \
{lg2.length(lanelet56.rightBound)}, \
{lg2.length(lanelet56.centerline)}. \
The area of lanelet56 is {lg2_extension.area(lanelet56.polygon2d())}
"""
)

# regulatory element
## get associated traffic lights
lights = lanelet56.trafficLights()
for light in lights:
    print(light.stopLine)
## get turn_direction
if "turn_direction" in lanelet56.attributes:
    turn_direction = lanelet56.attributes["turn_direction"]
    print(f"lanelet56 has {turn_direction} turn_direction value")

# routing
traffic_rules = lanelet2.traffic_rules.create(lanelet2.traffic_rules.Locations.Germany, \
                                              lanelet2.traffic_rules.Participants.Vehicle)
graph = lanelet2.routing.RoutingGraph(ll2_map, traffic_rules)
## get conflicting lanelets
conflictings = graph.conflicting(lanelet56)
print(f"lanelet56 is conflicting with {[conflicting.id for conflicting in conflictings]}")
## get following lanelets
followings = graph.following(lanelet56)
print(f"lanelet56 is connected to {[following.id for following in followings]}")
previouses = graph.previous(lanelet56)
print(f"lanelet56 is followed by {[previous.id for previous in previouses]}")

centerline = lanelet56.centerline
print(
f"The centerline of lanelet56 is of id {centerline.id} and \
contains {len(centerline)} points."
)
## access to points
pts = []
for p in centerline:
    pts.append(p)
## length, area
print(f"The length centerline is {lg2.length(centerline)}.")


basic_pts = [p.basicPoint() for p in pts]
center = np.sum(basic_pts) * (1.0 / len(basic_pts))
print(basic_pts,center)

center_sd_frame = lg2.toArcCoordinates(lg2.to2D(centerline), lg2.to2D(center))
print(f"""The center of centerline56 is \
({center_sd_frame.distance}, {center_sd_frame.length}) \
in arc coordinates
""")