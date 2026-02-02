import osmnx as ox
import pandas as pd
import math
import json

# --- CONFIGURATION ---
center_point = (13.833340, 100.610172)  # Chatuchak / Lat Phrao
dist = 2000
TARGET_ROAD_NAME = "Prasert Manukitch" 
TARGET_ROAD_NAME_TH = "ประเสริฐมนูกิจ"
INTERVAL_METERS = 10 

# --- THE FIX IS HERE ---
# We allow "Tertiary" (often frontage roads) and "Links" (ramps/connectors)
# We EXPLICITLY exclude 'residential' and 'service' to kill the Sois.
road_types = '["highway"~"trunk|primary|secondary|tertiary|trunk_link|primary_link|secondary_link"]'

print(f"Searching for MAIN roads and FRONTAGE roads named '{TARGET_ROAD_NAME}'...")

# 1. DOWNLOAD
G = ox.graph_from_point(center_point, dist=dist, custom_filter=road_types)
G_proj = ox.project_graph(G)
edges = ox.graph_to_gdfs(G_proj, nodes=False, edges=True)

# 2. FILTER BY NAME
mask = (
    edges['name'].astype(str).str.contains(TARGET_ROAD_NAME, case=False, na=False) | 
    edges['name'].astype(str).str.contains(TARGET_ROAD_NAME_TH, case=False, na=False)
)
specific_road = edges[mask]

print(f"Found {len(specific_road)} segments (Main Roads + Frontage only).")

# 3. HELPER (Heading)
def get_heading(lat1, lon1, lat2, lon2):
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dLon_r = math.radians(lon2 - lon1)
    y = math.sin(dLon_r) * math.cos(lat2_r)
    x = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(lat2_r) * math.cos(dLon_r)
    return (math.degrees(math.atan2(y, x)) + 360) % 360

# 4. GENERATE POINTS
custom_coordinates = []

for index, row in specific_road.iterrows():
    line = row['geometry']
    length = line.length
    
    if length < INTERVAL_METERS:
        continue

    is_oneway = row.get('oneway', True)
    
    current_dist = 0
    while current_dist < length:
        # Interpolate
        point_geom = line.interpolate(current_dist)
        next_point_geom = line.interpolate(min(current_dist + 5, length)) 
        
        # Project
        p1 = ox.projection.project_geometry(point_geom, crs=G_proj.graph['crs'], to_latlong=True)[0]
        p2 = ox.projection.project_geometry(next_point_geom, crs=G_proj.graph['crs'], to_latlong=True)[0]
        
        heading = get_heading(p1.y, p1.x, p2.y, p2.x)
        
        def create_obj(h):
            return {
                "lat": round(p1.y, 7), "lng": round(p1.x, 7),
                "heading": round(h, 2), "pitch": 0, "zoom": 0, "panoId": None,
                "countryCode": None, "stateCode": None,
                "extra": {"panoId": None, "panoDate": None}
            }

        custom_coordinates.append(create_obj(heading))
        
        # If it's a two-way road (rare for main Phahon, but possible for frontage), get reverse view
        if not is_oneway:
            custom_coordinates.append(create_obj((heading + 180) % 360))
            
        current_dist += INTERVAL_METERS

# 5. SAVE
filename = f"{TARGET_ROAD_NAME}_Main_Only.json"

with open(filename, "w", encoding="utf-8") as f:
    f.write('{\n')
    f.write(f'  "name": "{TARGET_ROAD_NAME} Main Roads Only",\n')
    f.write('  "customCoordinates": [\n')
    for i, coord in enumerate(custom_coordinates):
        json_str = json.dumps(coord, ensure_ascii=False)
        comma = "," if i < len(custom_coordinates) - 1 else ""
        f.write(f'    {json_str}{comma}\n')
    f.write('  ]\n')
    f.write('}')

print(f"Saved {len(custom_coordinates)} points. Check {filename}")