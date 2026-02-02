import os
import json
import csv

# --- CONFIGURATION ---
INPUT_ROOT = "annotated_streetview_images"  # Where your subfolders with JSONs are
OUTPUT_REPORT = "final_safety_report.csv"

# The "Strict Rule" Thresholds
THRESH_WARNING = 0.20  # 20%
THRESH_CRITICAL = 0.35 # 35%
THRESH_BOTH_TRIGGER = 20.0

# IDs from your dataset
ID_OBSTACLE = 1
ID_DAMAGE = 4
ID_SIDEWALK = 3

def analyze_folder(folder_path):
  json_path = os.path.join(folder_path, "_annotations.coco.json")
  if not os.path.exists(json_path):
    return []

  with open(json_path, 'r') as f:
    data = json.load(f)

  # 1. Map Annotations to Images
  # Structure: {image_id: [ann1, ann2, ...]}
  img_anns = {}
  for ann in data['annotations']:
    img_id = ann['image_id']
    if img_id not in img_anns:
      img_anns[img_id] = []
    img_anns[img_id].append(ann)

  results = []

  # 2. Analyze Each Image
  for img in data['images']:
    img_id = img['id']
    filename = img['file_name']
    
    # Initialize areas
    area_obs = 0.0
    area_dmg = 0.0
    area_sidewalk = 0.0
    
    if img_id in img_anns:
      for ann in img_anns[img_id]:
        cat_id = ann['category_id']
        area = ann['area']
          
        if cat_id == ID_OBSTACLE:
          area_obs += area
        elif cat_id == ID_DAMAGE:
          area_dmg += area
        elif cat_id == ID_SIDEWALK:
          area_sidewalk += area
    
    # CALCULATE PERCENTAGE
    pct_obs = 0.0
    pct_dmg = 0.0
    pct_total = 0.0
    
    if area_sidewalk > 0:
      pct_obs = (area_obs / area_sidewalk) * 100
      pct_dmg = (area_dmg / area_sidewalk) * 100
      pct_total = pct_obs + pct_dmg
    else:
      # Error case: no sidewalk found with impediments
      if (area_obs + area_dmg) > 0:
        pct_total = -1 
  
    # CLASSIFY Severity
    if pct_total == -1:
      status = "ERROR (No Sidewalk)"
    elif pct_total > (THRESH_CRITICAL * 100):
      status = "CRITICAL"
    elif pct_total > (THRESH_WARNING * 100):
      status = "WARNING"
    else:
      status = "SAFE"

    # CLASSIFY PROBLEM TYPE
    
    if status == "SAFE":
      problem_type = "None"
    elif pct_obs > THRESH_BOTH_TRIGGER and pct_dmg > THRESH_BOTH_TRIGGER:
      problem_type = "BOTH"
    elif pct_obs > pct_dmg:
      problem_type = "OBSTACLE"
    else:
      problem_type = "SURFACE DAMAGE"

    results.append({
      "folder": os.path.basename(folder_path),
      "file": filename,
      "status": status,
      "problem_type": problem_type,
      "total_blocked_pct": round(pct_total, 2),
      "obstacle_pct": round(pct_obs, 2),
      "damage_pct": round(pct_dmg, 2)
    })

  return results

def main():
  all_data = []
  print(f"Starting Detailed Analysis in '{INPUT_ROOT}'...\n")

  for root, dirs, files in os.walk(INPUT_ROOT):
    if "_annotations.coco.json" in files:
      print(f"   Analyzing: {os.path.basename(root)}")
      folder_stats = analyze_folder(root)
      all_data.extend(folder_stats)

  if all_data:
    print(f"\nSaving Detailed Report to {OUTPUT_REPORT}...")
    
    # Updated Columns
    keys = ["folder", "file", "status", "problem_type", "total_blocked_pct", "obstacle_pct", "damage_pct"]
    
    with open(OUTPUT_REPORT, 'w', newline='') as f:
      writer = csv.DictWriter(f, fieldnames=keys)
      writer.writeheader()
      writer.writerows(all_data)
        
    print("Done.")
    
    # --- QUICK STATS ---
    total = len(all_data)
    crit = sum(1 for x in all_data if x['status'] == "CRITICAL")
    warn = sum(1 for x in all_data if x['status'] == "WARNING")
    
    # Count Problem Types (Only for non-safe images)
    count_obs = sum(1 for x in all_data if x['problem_type'] == "OBSTACLE")
    count_dmg = sum(1 for x in all_data if x['problem_type'] == "SURFACE DAMAGE")
    count_both = sum(1 for x in all_data if "BOTH" in x['problem_type'])
    
    print("\n--- SUMMARY ---")
    print(f"Total Images:     {total}")
    print(f"WARNING Alerts:  {warn} ({(warn/total)*100:.1f}%)")
    print(f"CRITICAL Alerts:  {crit} ({(crit/total)*100:.1f}%)")
    print(f"Mainly Obstacles: {count_obs}")
    print(f"Mainly Damage:    {count_dmg}")
    print(f"Double Trouble:   {count_both}")
      
  else:
    print("No JSON files found.")

if __name__ == "__main__":
    main()