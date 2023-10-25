# laneletの読み込み
import lanelet2
from lanelet2_extension.projection import MGRSProjector
import lanelet2.geometry as lg2
import numpy as np

def setNextTrajectoryPoint(start_lane, start_offset, start_s, target_length, target_lane, lane_resolution, tolerance):
    arc_coords = lg2.ArcCoordinates() 
    arc_coords.distance = start_offset #offset, t
    arc_coords.length = start_s  #s

    start_position = lg2.fromArcCoordinates(lg2.to2D(start_lane.centerline), arc_coords) #(x,y) of start

    for l in np.arange(start_s if start_lane == target_lane else 0, lg2.length(target_lane.centerline), lane_resolution): #(start, stop, step)
        arc_coords = lg2.ArcCoordinates() 
        arc_coords.distance = 0.0 #offset, t
        arc_coords.length = l  #s

        target_position = lg2.fromArcCoordinates(lg2.to2D(target_lane.centerline), arc_coords) #(x,y) of target
        
        if abs(lg2.distance(target_position, start_position) - target_length) < tolerance: #tolerance[m]
            return lg2.toArcCoordinates(lg2.to2D(target_lane.centerline), target_position) #return (offset, s)
            
    else:
        return None


def calcAllTrajectoryPoints(laneID_list, start_offset, start_s, target_length, lane_resolution, tolerance):
    lane_list = list()
    for lID in laneID_list:
        lane_list.append(ll2_map.laneletLayer.get(lID)) # need to check if laneID is valid and exists in the map
    
    current_point = lg2.ArcCoordinates()
    current_point.distance = start_offset
    current_point.length = start_s
    print("{}\t{}\t{}".format(laneID_list[0], current_point.distance, current_point.length))

    result_trajectory = list()
    
    i = 1
    while i < len(lane_list):
        goal_point = setNextTrajectoryPoint(start_lane=lane_list[i-1],\
                                            start_offset=current_point.distance,start_s=current_point.length,\
                                            target_length=target_length,\
                                            target_lane=lane_list[i],\
                                            lane_resolution=lane_resolution,\
                                            tolerance=tolerance)
        if goal_point is None:
            goal_point = setNextTrajectoryPoint(start_lane=lane_list[i-1],\
                                            start_offset=current_point.distance,start_s=current_point.length,\
                                            target_length=target_length,\
                                            target_lane=lane_list[i-1],\
                                            lane_resolution=lane_resolution,\
                                            tolerance=tolerance)
            if goal_point is None:
                print("no point on the target lane:{} from lane:{} at a distance:{}m".format(laneID_list[i], laneID_list[i-1], target_length))
                return None
            else:
                i = i-1        
        current_point = goal_point
        
        print("{}\t{}\t{}".format(laneID_list[i],goal_point.distance, goal_point.length))
        result_trajectory.append([laneID_list[i], goal_point])
        i=i+1
    return result_trajectory
    
    
if __name__ == "__main__":
    proj = MGRSProjector(lanelet2.io.Origin(0.0, 0.0))
    ll2_map = lanelet2.io.load("/home/keisuke-ota/autoware_map/followtrajectoryaction_scenario/lanelet2_map.osm", proj)

    calcAllTrajectoryPoints(laneID_list=[1119,41,48],\
                            start_offset=0,\
                            start_s=0,\
                            target_length=16.0,\
                            lane_resolution=0.1,
                            tolerance=0.1)

