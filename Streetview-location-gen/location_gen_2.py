import osmnx as ox
import pandas as pd
import math
import json

# --- CONFIGURATION ---
# 1. Center Point (Chatuchak / Lat Phrao area)
center_point = (13.778884, 100.544333) 
dist = 2000  # 2km radius

# 2. Target Name
TARGET_ROAD_NAME = "Phahon"
TARGET_ROAD_NAME_TH = "พหลโยธิน"

# 3. SETTINGS
INTERVAL_METERS = 10  # Changed to 10m as requested

# 4. BROAD FILTER (Capture Everything)
# Previous script only took 'trunk/primary'.
# This one takes 'tertiary', 'service', 'residential' too, 
# so it catches the "middle road" or frontage roads inside the park area.
road_types = '["highway"~"trunk|primary|secondary|tertiary|service|residential"]'

print(f"Searching for ALL roads named '{TARGET_ROAD_NAME}'...")

# --- STEP 1: DOWNLOAD ---
G = ox.graph_from_point(center_point, dist=dist, custom_filter=road_types)
G_proj = ox.project_graph(G)
edges = ox.graph_to_gdfs(G_proj, nodes=False, edges=True)

# Filter by Name
mask = (
    edges['name'].astype(str).str.contains(TARGET_ROAD_NAME, case=False, na=False) | 
    edges['name'].astype(str).str.contains(TARGET_ROAD_NAME_TH, case=False, na=False)
)
specific_road = edges[mask]

print(f"Found {len(specific_road)} segments matching the name.")

# --- STEP 2: HELPER FUNCTIONS ---
def get_heading(lat1, lon1, lat2, lon2):
    # Convert to radians for math
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dLon_r = math.radians(lon2 - lon1)
    
    y = math.sin(dLon_r) * math.cos(lat2_r)
    x = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(lat2_r) * math.cos(dLon_r)
    
    brng = math.degrees(math.atan2(y, x))
    return (brng + 360) % 360

# --- STEP 3: GENERATE POINTS ---
custom_coordinates = []

for index, row in specific_road.iterrows():
    line = row['geometry']
    length = line.length
    
    # Skip if segment is too short
    if length < INTERVAL_METERS:
        continue

    # Check if One-Way
    is_oneway = row.get('oneway', True)
    
    current_dist = 0
    while current_dist < length:
        # Interpolate
        point_geom = line.interpolate(current_dist)
        # Look ahead 5m for heading
        next_point_geom = line.interpolate(min(current_dist + 5, length)) 
        
        # Project to Lat/Lon
        p1 = ox.projection.project_geometry(point_geom, crs=G_proj.graph['crs'], to_latlong=True)[0]
        p2 = ox.projection.project_geometry(next_point_geom, crs=G_proj.graph['crs'], to_latlong=True)[0]
        
        # Calculate Forward Heading
        heading = get_heading(p1.y, p1.x, p2.y, p2.x)
        
        # Function to create the object structure
        def create_obj(h):
            return {
                "lat": round(p1.y, 7),
                "lng": round(p1.x, 7),
                "heading": round(h, 2),
                "pitch": 0, "zoom": 0, "panoId": None,
                "countryCode": None, "stateCode": None,
                "extra": {"panoId": None, "panoDate": None}
            }

        # 1. Forward View
        custom_coordinates.append(create_obj(heading))
        
        # 2. Backward View (Only if NOT one-way)
        # Most main Phahonyothin roads are One-Way lines in OSM, 
        # so this usually won't trigger unless it's a small service road.
        # But if it does, you get the reverse view.
        if not is_oneway:
            custom_coordinates.append(create_obj((heading + 180) % 360))
            
        current_dist += INTERVAL_METERS

# --- STEP 4: SAVE ---
filename = f"{TARGET_ROAD_NAME}_All_Roads.json"

with open(filename, "w", encoding="utf-8") as f:
    f.write('{\n')
    f.write(f'  "name": "{TARGET_ROAD_NAME} Full Capture",\n')
    f.write('  "customCoordinates": [\n')
    
    for i, coord in enumerate(custom_coordinates):
        json_str = json.dumps(coord, ensure_ascii=False)
        comma = "," if i < len(custom_coordinates) - 1 else ""
        f.write(f'    {json_str}{comma}\n')
        
    f.write('  ]\n')
    f.write('}')

print(f"Saved {len(custom_coordinates)} points to {filename}")