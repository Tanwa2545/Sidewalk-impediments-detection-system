import os
import cv2
import json
import numpy as np
import torch
import datetime
from PIL import Image
from rfdetr import RFDETRSegMedium

# --- CONFIGURATION ---
# 1. Path to your best model
CHECKPOINT_PATH = "output/checkpoint_best_ema.pth"

# 2. Where your raw folders are (The folder containing "Junction to Junction" folders)
INPUT_ROOT = "streetview_images" 

# 3. Where you want the results
OUTPUT_ROOT = "annotated_streetview_images"

CONFIDENCE_THRESHOLD = 0.30

# Define your standard Colors
CLASS_COLORS = {
  1: (0, 255, 255),    # Obstacle: Yellow
  2: (0, 165, 255),    # Road: Orange
  3: (255, 255, 0),    # Sidewalk Structure: Cyan
  4: (255, 0, 255),    # Surface Damage: Magenta
  5: (0, 0, 255),      # Vehicle: Red
  6: (255, 0, 128),    # Walkable Path: Purple
}

DRAW_ORDER = {
  2: 0,   # Road (Background)
  3: 1,   # Sidewalk Structure (Background)
  6: 2,   # Walkable Path (Midground)
  5: 3,   # Vehicle (Foreground)
  4: 4,   # Surface Damage (Critical Foreground)
  1: 5    # Obstacle (Critical Foreground)
}

# Define Category Names (Must match your training IDs)
CATEGORY_MAP = [
  {"id": 1, "name": "obstacle"},
  {"id": 2, "name": "road"},
  {"id": 3, "name": "sidewalk_structure"},
  {"id": 4, "name": "surface_damage"},
  {"id": 5, "name": "vehicle"},
  {"id": 6, "name": "walkable_path"}
]
CAT_ID_TO_NAME = {cat['id']: cat['name'] for cat in CATEGORY_MAP}

def main():
  # 1. Load Model
  print(f"Loading Model from {CHECKPOINT_PATH}...")
  model = RFDETRSegMedium(pretrain_weights=CHECKPOINT_PATH)
  model.optimize_for_inference()
  print("Model Ready.\n")

  # 2. Walk through every subfolder
  n=0
  for root, dirs, files in os.walk(INPUT_ROOT):
    # Filter for images only
    # if n>1:
    #   break
    # n+=1
    image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not image_files:
      continue

    # Create corresponding Output Folder
    relative_path = os.path.relpath(root, INPUT_ROOT)
    current_output_dir = os.path.join(OUTPUT_ROOT, relative_path)
    os.makedirs(current_output_dir, exist_ok=True)
    
    print(f"Processing Folder: {relative_path} ({len(image_files)} images)")

    # Initialize JSON for THIS subfolder
    folder_json = {
      "info": {
        "description": f"Predictions for {relative_path}",
        "date_created": datetime.datetime.now().isoformat()
      },
      "licenses": [],
      "categories": CATEGORY_MAP,
      "images": [],
      "annotations": []
    }

    ann_id_counter = 1

    for img_idx, filename in enumerate(image_files):
      input_path = os.path.join(root, filename)
      output_img_path = os.path.join(current_output_dir, filename)
      
      # A. Load Image
      try:
        image_pil = Image.open(input_path).convert("RGB")
        image_bgr = cv2.imread(input_path) # Reload for CV2 drawing
        w, h = image_pil.size
      except Exception as e:
        print(f"Error loading {filename}: {e}")
        continue

      # B. Add Image info to JSON
      # We use the enumerate index as ID to keep it simple per folder
      image_id = img_idx + 1 
      folder_json["images"].append({
        "id": image_id,
        "file_name": filename,
        "width": w,
        "height": h,
        "date_captured": datetime.datetime.now().isoformat()
      })

      # C. Predict
      detections = model.predict(image_pil, threshold=CONFIDENCE_THRESHOLD)

      # D. Draw & Record Data
      overlay = image_bgr.copy()
      
      if detections.mask is not None:
        det_list = []
        for i in range(len(detections)):
          class_id = int(detections.class_id[i])
          # Get priority (default to 10 if unknown)
          priority = DRAW_ORDER.get(class_id, 10) 
          det_list.append((priority, i))
        
        # Sort: Lowest priority first (Background), Highest last (Foreground)
        det_list.sort(key=lambda x: x[0])
        
        # Draw and Record
        overlay = image_bgr.copy()
        for _, i in det_list:
          class_id = int(detections.class_id[i])
          mask = detections.mask[i]
          score = float(detections.confidence[i])
          bbox = detections.xyxy[i]

          # Higher threshold for other class except obstacle and surface damage
          if class_id not in [1, 4] and score < 0.45:
            continue

          # 1. Visualization
          color = CLASS_COLORS.get(class_id, (255, 255, 255))
          mask_uint8 = (mask * 255).astype(np.uint8)
          contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
          
          for contour in contours:
            cv2.fillPoly(overlay, [contour], color)
            # Thin white outline
            cv2.polylines(image_bgr, [contour], True, (255, 255, 255), 1)

            # 2. JSON Annotation
            if len(contour) > 2:
              # Convert BBox to COCO [x,y,w,h]
              x1, y1, x2, y2 = bbox
              bbox_wh = [float(x1), float(y1), float(x2 - x1), float(y2 - y1)]
              
              folder_json["annotations"].append({
                "id": ann_id_counter,
                "image_id": image_id,
                "category_id": class_id,
                "bbox": bbox_wh,
                "area": float(np.sum(mask)),
                "segmentation": [contour.flatten().tolist()],
                "iscrowd": 0,
                "score": score
              })
              ann_id_counter += 1

      # E. Save Visual Image (Blend)
      alpha = 0.35
      cv2.addWeighted(overlay, alpha, image_bgr, 1 - alpha, 0, image_bgr)
      cv2.imwrite(output_img_path, image_bgr)
        
    # F. Save JSON for this folder
    json_output_path = os.path.join(current_output_dir, "_annotations.coco.json")
    with open(json_output_path, 'w') as f:
      json.dump(folder_json, f)
        
    print(f"Saved {len(image_files)} images & JSON to: {current_output_dir}")

  print("\nAll folders processed.")

if __name__ == "__main__":
    main()