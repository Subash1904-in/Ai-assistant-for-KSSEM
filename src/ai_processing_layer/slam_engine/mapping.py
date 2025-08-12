"""
SLAM Mapping Engine for KSSEM Virtual AI Assistant
Implements ORB-SLAM3 based mapping and localization for campus navigation
"""

import json
import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional
import math
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Point3D:
    x: float
    y: float
    z: float
    
    def distance_to(self, other: 'Point3D') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)

@dataclass
class NavigationRoute:
    start: Point3D
    end: Point3D
    waypoints: List[Point3D]
    distance: float
    estimated_time: float
    instructions: List[str]

class KSSEMSLAMEngine:
    """
    SLAM Engine specifically designed for KSSEM campus navigation
    Provides mapping, localization, and route planning capabilities
    """
    
    def __init__(self, landmarks_file: str = "/workspace/data/kssem_campus_map/landmarks.json"):
        """Initialize SLAM engine with KSSEM campus map data"""
        self.landmarks_file = landmarks_file
        self.campus_map = None
        self.current_location = None
        self.confidence_threshold = 0.85
        self.load_campus_map()
        
    def load_campus_map(self) -> None:
        """Load KSSEM campus landmarks and building data"""
        try:
            with open(self.landmarks_file, 'r') as f:
                self.campus_map = json.load(f)
            print(f"✓ Loaded KSSEM campus map with {len(self.campus_map['buildings'])} buildings")
        except FileNotFoundError:
            print(f"⚠ Warning: Campus map file not found at {self.landmarks_file}")
            self.campus_map = self._create_default_map()
    
    def _create_default_map(self) -> Dict:
        """Create a basic default map if file is not available"""
        return {
            "campus_info": {"name": "KSSEM Campus", "coordinate_system": "local_grid"},
            "buildings": [],
            "pathways": [],
            "navigation_points": []
        }
    
    def localize_position(self, sensor_data: Dict) -> Tuple[Point3D, float]:
        """
        Localize current position using sensor data (camera, GPS, etc.)
        Returns position and confidence score
        """
        # Simulate localization using visual landmarks and GPS
        # In real implementation, this would use ORB-SLAM3 algorithm
        
        if "gps" in sensor_data:
            gps_coords = sensor_data["gps"]
            # Convert GPS to local coordinates (simplified)
            local_x = (gps_coords["longitude"] - 77.5946) * 111000  # Rough conversion
            local_y = (gps_coords["latitude"] - 12.9716) * 111000
            confidence = 0.8
        else:
            # Fallback to visual localization
            local_x, local_y = self._visual_localization(sensor_data.get("camera_frame"))
            confidence = 0.7
        
        position = Point3D(local_x, local_y, 0)
        self.current_location = position
        
        return position, confidence
    
    def _visual_localization(self, camera_frame: Optional[np.ndarray]) -> Tuple[float, float]:
        """Perform visual localization using camera frame"""
        if camera_frame is None:
            return 200.0, 150.0  # Default to central junction
        
        # Simplified visual localization
        # In real implementation, this would use ORB features and map matching
        height, width = camera_frame.shape[:2]
        center_x, center_y = width // 2, height // 2
        
        # Mock calculation based on visual features
        return float(center_x * 0.5), float(center_y * 0.5)
    
    def find_building(self, building_name: str) -> Optional[Dict]:
        """Find building information by name or ID"""
        if not self.campus_map:
            return None
        
        building_name = building_name.lower()
        
        for building in self.campus_map["buildings"]:
            if (building_name in building["name"].lower() or 
                building_name in building["id"].lower() or
                any(dept.lower() in building_name for dept in building.get("departments", []))):
                return building
        
        return None
    
    def find_facility(self, facility_name: str) -> Optional[Dict]:
        """Find facility by name (library, cafeteria, etc.)"""
        if not self.campus_map:
            return None
        
        facility_name = facility_name.lower()
        
        # Check buildings for facilities
        for building in self.campus_map["buildings"]:
            if facility_name in building["name"].lower():
                return building
            
            # Check facilities within buildings
            for facility in building.get("facilities", []):
                if facility_name in facility.lower():
                    return building
        
        return None
    
    def calculate_route(self, destination: str, start_location: Optional[Point3D] = None) -> Optional[NavigationRoute]:
        """
        Calculate optimal route from current/start location to destination
        """
        if start_location is None:
            start_location = self.current_location or Point3D(200, 150, 0)  # Default to central junction
        
        # Find destination building/facility
        destination_building = self.find_building(destination) or self.find_facility(destination)
        
        if not destination_building:
            print(f"⚠ Destination '{destination}' not found on campus")
            return None
        
        # Get destination coordinates
        dest_coords = destination_building["coordinates"]["center"]
        dest_point = Point3D(dest_coords[0], dest_coords[1], dest_coords[2])
        
        # Calculate route using A* pathfinding algorithm
        waypoints = self._calculate_waypoints(start_location, dest_point)
        
        # Calculate total distance and estimated time
        total_distance = self._calculate_total_distance(waypoints)
        estimated_time = total_distance / 1.5  # Assuming walking speed of 1.5 m/s
        
        # Generate turn-by-turn instructions
        instructions = self._generate_instructions(waypoints, destination_building)
        
        return NavigationRoute(
            start=start_location,
            end=dest_point,
            waypoints=waypoints,
            distance=total_distance,
            estimated_time=estimated_time,
            instructions=instructions
        )
    
    def _calculate_waypoints(self, start: Point3D, end: Point3D) -> List[Point3D]:
        """Calculate waypoints using simplified A* pathfinding"""
        # Simplified pathfinding - in real implementation, use A* with obstacles
        waypoints = [start]
        
        # Add intermediate waypoints based on campus layout
        if abs(start.x - end.x) > 50 or abs(start.y - end.y) > 50:
            # Add waypoint at central junction if needed
            central_junction = Point3D(200, 150, 0)
            if start.distance_to(central_junction) > 20 and end.distance_to(central_junction) > 20:
                waypoints.append(central_junction)
        
        # Add pathway intersections as waypoints
        waypoints.extend(self._get_pathway_intersections(start, end))
        
        waypoints.append(end)
        return waypoints
    
    def _get_pathway_intersections(self, start: Point3D, end: Point3D) -> List[Point3D]:
        """Get relevant pathway intersections between start and end points"""
        intersections = []
        
        # Major intersections on campus
        major_intersections = [
            Point3D(150, 150, 0),  # Library intersection
            Point3D(250, 150, 0),  # Cafeteria intersection
            Point3D(200, 100, 0),  # Admin intersection
            Point3D(200, 250, 0),  # Department intersection
        ]
        
        for intersection in major_intersections:
            # Add intersection if it's roughly on the path
            if self._is_point_on_path(start, end, intersection, threshold=30):
                intersections.append(intersection)
        
        return intersections
    
    def _is_point_on_path(self, start: Point3D, end: Point3D, point: Point3D, threshold: float) -> bool:
        """Check if a point is roughly on the path between start and end"""
        # Calculate distance from point to line segment
        line_length = start.distance_to(end)
        if line_length == 0:
            return start.distance_to(point) <= threshold
        
        t = max(0, min(1, ((point.x - start.x) * (end.x - start.x) + 
                          (point.y - start.y) * (end.y - start.y)) / (line_length ** 2)))
        
        projection = Point3D(
            start.x + t * (end.x - start.x),
            start.y + t * (end.y - start.y),
            start.z + t * (end.z - start.z)
        )
        
        return point.distance_to(projection) <= threshold
    
    def _calculate_total_distance(self, waypoints: List[Point3D]) -> float:
        """Calculate total distance of the route"""
        total_distance = 0.0
        for i in range(len(waypoints) - 1):
            total_distance += waypoints[i].distance_to(waypoints[i + 1])
        return total_distance
    
    def _generate_instructions(self, waypoints: List[Point3D], destination: Dict) -> List[str]:
        """Generate turn-by-turn navigation instructions"""
        instructions = []
        
        if len(waypoints) < 2:
            return ["You are already at your destination."]
        
        instructions.append(f"Starting navigation to {destination['name']}")
        
        for i in range(len(waypoints) - 1):
            current = waypoints[i]
            next_point = waypoints[i + 1]
            
            # Calculate direction
            dx = next_point.x - current.x
            dy = next_point.y - current.y
            distance = current.distance_to(next_point)
            
            # Determine direction
            if abs(dx) > abs(dy):
                direction = "east" if dx > 0 else "west"
            else:
                direction = "north" if dy > 0 else "south"
            
            # Generate instruction
            if i == 0:
                instructions.append(f"Head {direction} for {distance:.0f} meters")
            else:
                instructions.append(f"Continue {direction} for {distance:.0f} meters")
        
        # Add final instruction
        entrance = destination.get("entrance_points", [{}])[0]
        if entrance:
            instructions.append(f"Arrive at {destination['name']} - look for the main entrance")
        else:
            instructions.append(f"You have arrived at {destination['name']}")
        
        return instructions
    
    def get_nearby_landmarks(self, location: Optional[Point3D] = None, radius: float = 100) -> List[Dict]:
        """Get landmarks within specified radius of location"""
        if location is None:
            location = self.current_location or Point3D(200, 150, 0)
        
        nearby = []
        
        if not self.campus_map:
            return nearby
        
        # Check buildings
        for building in self.campus_map["buildings"]:
            building_center = building["coordinates"]["center"]
            building_point = Point3D(building_center[0], building_center[1], building_center[2])
            
            if location.distance_to(building_point) <= radius:
                nearby.append({
                    "type": "building",
                    "name": building["name"],
                    "distance": location.distance_to(building_point),
                    "coordinates": building_center
                })
        
        # Check navigation points
        for nav_point in self.campus_map.get("navigation_points", []):
            nav_coords = nav_point["coordinates"]
            nav_point_3d = Point3D(nav_coords[0], nav_coords[1], nav_coords[2])
            
            if location.distance_to(nav_point_3d) <= radius:
                nearby.append({
                    "type": "landmark",
                    "name": nav_point["name"],
                    "distance": location.distance_to(nav_point_3d),
                    "coordinates": nav_coords
                })
        
        # Sort by distance
        nearby.sort(key=lambda x: x["distance"])
        return nearby
    
    def update_map(self, new_landmarks: List[Dict]) -> None:
        """Update campus map with new landmark data"""
        if not self.campus_map:
            return
        
        for landmark in new_landmarks:
            # Add new landmarks to navigation points
            self.campus_map["navigation_points"].append(landmark)
        
        # Save updated map
        self._save_map()
    
    def _save_map(self) -> None:
        """Save updated campus map to file"""
        try:
            with open(self.landmarks_file, 'w') as f:
                json.dump(self.campus_map, f, indent=2)
            print("✓ Campus map updated successfully")
        except Exception as e:
            print(f"⚠ Error saving map: {e}")
    
    def get_campus_statistics(self) -> Dict:
        """Get comprehensive campus mapping statistics"""
        if not self.campus_map:
            return {}
        
        return {
            "total_buildings": len(self.campus_map.get("buildings", [])),
            "total_pathways": len(self.campus_map.get("pathways", [])),
            "navigation_points": len(self.campus_map.get("navigation_points", [])),
            "kiosk_locations": len(self.campus_map.get("kiosk_locations", [])),
            "campus_area": self.campus_map.get("campus_info", {}).get("total_area", "Unknown"),
            "last_updated": self.campus_map.get("campus_info", {}).get("last_updated", "Unknown")
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize SLAM engine
    slam_engine = KSSEMSLAMEngine()
    
    # Test localization
    test_sensor_data = {
        "gps": {"latitude": 12.9716, "longitude": 77.5946},
        "camera_frame": np.zeros((480, 640, 3), dtype=np.uint8)
    }
    
    position, confidence = slam_engine.localize_position(test_sensor_data)
    print(f"Current position: ({position.x:.1f}, {position.y:.1f}) with confidence {confidence:.2f}")
    
    # Test route calculation
    route = slam_engine.calculate_route("Computer Science")
    if route:
        print(f"\nRoute to Computer Science Department:")
        print(f"Distance: {route.distance:.1f} meters")
        print(f"Estimated time: {route.estimated_time:.1f} seconds")
        print("Instructions:")
        for i, instruction in enumerate(route.instructions):
            print(f"{i+1}. {instruction}")
    
    # Test nearby landmarks
    nearby = slam_engine.get_nearby_landmarks()
    print(f"\nNearby landmarks:")
    for landmark in nearby[:5]:
        print(f"- {landmark['name']} ({landmark['distance']:.1f}m away)")
    
    # Get campus statistics
    stats = slam_engine.get_campus_statistics()
    print(f"\nCampus Statistics: {stats}")