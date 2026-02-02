import json
import requests
import os
from dotenv import load_dotenv

# --- 1. Configuration ---
load_dotenv()
API_KEY = os.getenv("API_KEY")

# The specific JSON file you want to process
JSON_FILE_PATH = "location_json/prasertmanukitch(lad pla kao-liap duan) (fixed).json"

# Base folder for all downloads
BASE_OUTPUT_FOLDER = "streetview_images"

# Image size (width x height)
IMAGE_SIZE = "640x640"
# --------------------------

def download_streetview_images():
    # --- 2. Dynamic Folder Setup ---
    # Extract the filename without extension (e.g., "phahon yothin rd (ratchayothin-kaset)")
    json_filename = os.path.splitext(os.path.basename(JSON_FILE_PATH))[0]
    
    # Create the specific subfolder: streetview_images/phahon yothin rd.../
    output_dir = os.path.join(BASE_OUTPUT_FOLDER, json_filename)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    else:
        print(f"Directory already exists: {output_dir}")

    # Load the JSON data
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR: Could not read '{JSON_FILE_PATH}'. Reason: {e}")
        return

    coordinates = data.get('customCoordinates', [])
    if not coordinates:
        print("ERROR: No 'customCoordinates' found in the JSON file.")
        return

    print(f"Found {len(coordinates)} coordinates. Starting download to: {output_dir}")

    # --- 3. Loop and Download ---
    for i, item in enumerate(coordinates):
        
        # Limit for testing (remove this if block when ready for full download)
        # if i >= 5: 
        #     print("Stopping after 5 images (Test Mode). Remove limit to download all.")
        #     break

        # -- A. Extract Data --
        # 1. Heading (Adjusted for side view)
        # Note: We round it to 0 decimals for a cleaner filename
        heading_raw = (item.get('heading', 0) - 90) % 360
        heading = int(round(heading_raw))
        
        # 2. Pitch & FOV
        pitch = item.get('pitch', 0) - 15
        fov = 100
        
        # 3. Location
        lat = item.get('lat', 0)
        lng = item.get('lng', 0)
        
        # 4. Pano ID (Check both locations)
        pano_id = item.get('panoId')
        if not pano_id:
            pano_id = item.get('extra', {}).get('panoId')
            
        # 5. Date (Check both locations) - Default to 'NoDate' if missing
        pano_date = item.get('panoDate')
        if not pano_date:
            pano_date = item.get('extra', {}).get('panoDate', 'NoDate')

        # -- B. Build URL --
        if not pano_id:
            # Fallback to lat/lng if Pano ID is missing (less accurate)
            url = f"https://maps.googleapis.com/maps/api/streetview?size={IMAGE_SIZE}&location={lat},{lng}&heading={heading}&fov={fov}&pitch={pitch}&key={API_KEY}"
            id_for_name = "NoPanoID"
        else:
            # Preferred method: Use Pano ID
            url = f"https://maps.googleapis.com/maps/api/streetview?size={IMAGE_SIZE}&pano={pano_id}&heading={heading}&fov={fov}&pitch={pitch}&key={API_KEY}"
            id_for_name = pano_id

        # -- C. Name the File --
        # Format: Lat_Lng_PanoID_Heading_Date.jpg
        # We format Lat/Lng to 6 decimal places to ensure consistent length for sorting
        filename = f"{lat:.6f}_{lng:.6f}_{id_for_name}_{heading}_{pano_date}.jpg"
        filepath = os.path.join(output_dir, filename)

        # -- D. Download --
        # Skip if already exists (saves money/time if you re-run)
        if os.path.exists(filepath):
            print(f"Skipping {i}: File already exists ({filename})")
            continue

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(filepath, 'wb') as img_file:
                    img_file.write(response.content)
                print(f"[{i}] Downloaded: {filename}")
            else:
                print(f"[{i}] Failed (Status {response.status_code}): {url}")

        except requests.RequestException as e:
            print(f"[{i}] Network Error: {e}")

    print("--- Download complete! ---")

if __name__ == "__main__":
    download_streetview_images()