import osmnx as ox
import pandas as pd
import math
import json

# --- 1. CONFIGURATION: MASTER SEGMENT LIST ---
# Format: ("File_Label", (Start_Lat, Start_Lng), (End_Lat, End_Lng), "Road_Name_EN", "Road_Name_TH")
SEGMENTS = [
    # --- PHAHON YOTHIN ---
    ("Phahon_SaphanKhwai_to_Chatuchak", (13.7936, 100.5498), (13.8030, 100.5540), "Phahon", "พหลโยธิน"),
    ("Phahon_Chatuchak_to_Ratchayothin", (13.8135, 100.5605), (13.8267, 100.5732), "Phahon", "พหลโยธิน"),
    ("Phahon_Ratchayothin_to_Kaset", (13.8267, 100.5732), (13.8398, 100.5760), "Phahon", "พหลโยธิน"),
    ("Phahon_Kaset_to_BangBua", (13.8410, 100.5765), (13.8560, 100.5840), "Phahon", "พหลโยธิน"),

    # --- LAT PHRAO ---
    # ("LatPhrao_HaYaek_to_Ratchada", (13.8140, 100.5600), (13.8060, 100.5735), "Lat Phrao", "ลาดพร้าว"),
    # ("LatPhrao_Ratchada_to_ChokChai4", (13.8060, 100.5735), (13.7960, 100.5950), "Lat Phrao", "ลาดพร้าว"),
    # ("LatPhrao_ChokChai4_to_LiapDuan", (13.7960, 100.5950), (13.7885, 100.6100), "Lat Phrao", "ลาดพร้าว"),

    # # --- RATCHADAPHISEK ---
    # ("Ratchada_Sutthisan_to_LatPhrao", (13.7895, 100.5735), (13.8060, 100.5735), "Ratchadaphisek", "รัชดาภิเษก"),
    # ("Ratchada_LatPhrao_to_Ratchayothin", (13.8060, 100.5735), (13.8267, 100.5732), "Ratchadaphisek", "รัชดาภิเษก"),

    # # --- VIBHAVADI ---
    # ("Vibhavadi_Sutthisan_to_HaYaek", (13.7850, 100.5580), (13.8120, 100.5590), "Vibhavadi", "วิภาวดี"),
    # ("Vibhavadi_HaYaek_to_Kaset", (13.8150, 100.5595), (13.8420, 100.5650), "Vibhavadi", "วิภาวดี"),
]

INTERVAL_METERS = 10 
road_types = '["highway"~"trunk|primary|secondary|tertiary|trunk_link|primary_link|secondary_link"]'

# --- 2. HELPER FUNCTIONS ---
def get_heading(lat1, lon1, lat2, lon2):
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dLon_r = math.radians(lon2 - lon1)
    y = math.sin(dLon_r) * math.cos(lat2_r)
    x = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(lat2_r) * math.cos(dLon_r)
    return (math.degrees(math.atan2(y, x)) + 360) % 360

# --- 3. MAIN LOOP ---
print(f"Starting Batch Processing for {len(SEGMENTS)} segments...")

for label, start_coord, end_coord, name_en, name_th in SEGMENTS:
    
    # Calculate Center Point & Radius
    mid_lat = (start_coord[0] + end_coord[0]) / 2
    mid_lon = (start_coord[1] + end_coord[1]) / 2
    center_point = (mid_lat, mid_lon)
    
    dist_deg = math.sqrt((start_coord[0]-end_coord[0])**2 + (start_coord[1]-end_coord[1])**2)
    dist = (dist_deg * 111000) / 2 + 500
    
    print(f"\n>>> Processing: {label}")
    print(f"    Center: {center_point}, Radius: {int(dist)}m, Searching: {name_en}")

    # --- STEP 1: DOWNLOAD ---
    try:
        G = ox.graph_from_point(center_point, dist=dist, custom_filter=road_types)
        G_proj = ox.project_graph(G)
        edges = ox.graph_to_gdfs(G_proj, nodes=False, edges=True)
    except Exception as e:
        print(f"    ! Error downloading map: {e}")
        continue

    # --- STEP 2: FIX NAME FILTERING ---
    cols_to_check = ['name', 'name:en', 'name:th', 'official_name']
    existing_cols = [c for c in cols_to_check if c in edges.columns]
    
    # FIX: Handle lists correctly
    def combine_names(row):
        combined = []
        for col in existing_cols:
            val = row[col]
            # Case 1: Value is a List (e.g., ['Phahon', 'OtherName'])
            if isinstance(val, list):
                 combined.extend([str(v) for v in val])
            # Case 2: Value is a single string/number and NOT Nan
            elif pd.notna(val):
                combined.append(str(val))
        return " ".join(combined)

    if not edges.empty:
        edges['searchable_name'] = edges.apply(combine_names, axis=1)
        mask = (
            edges['searchable_name'].str.contains(name_en, case=False) | 
            edges['searchable_name'].str.contains(name_th, case=False)
        )
        specific_road = edges[mask]
    else:
        specific_road = pd.DataFrame()

    print(f"    Found {len(specific_road)} road segments.")
    
    if len(specific_road) == 0:
        continue

    # --- STEP 3: GENERATE POINTS ---
    custom_coordinates = []

    for index, row in specific_road.iterrows():
        line = row['geometry']
        length = line.length
        
        if length < INTERVAL_METERS:
            continue

        is_oneway = row.get('oneway', True)
        
        current_dist = 0
        while current_dist < length:
            point_geom = line.interpolate(current_dist)
            next_point_geom = line.interpolate(min(current_dist + 5, length)) 
            
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
            if not is_oneway:
                custom_coordinates.append(create_obj((heading + 180) % 360))
                
            current_dist += INTERVAL_METERS

    # --- STEP 4: SAVE FILE ---
    if custom_coordinates:
        filename = f"{label}.json"
        with open(filename, "w", encoding="utf-8") as f:
            f.write('{\n')
            f.write(f'  "name": "{label}",\n')
            f.write('  "customCoordinates": [\n')
            for i, coord in enumerate(custom_coordinates):
                json_str = json.dumps(coord, ensure_ascii=False)
                comma = "," if i < len(custom_coordinates) - 1 else ""
                f.write(f'    {json_str}{comma}\n')
            f.write('  ]\n')
            f.write('}')
        print(f"    -> Saved {len(custom_coordinates)} points to {filename}")

print("\nAll done!")