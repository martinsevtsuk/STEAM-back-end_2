import base64
import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:13869/api/camera/frames/process"
TEST_IMAGE_PATH = "STEAM/yolo11n.pt" # Not an image, but I'll create a dummy pixel one

def create_test_image_base64():
    # A simple 1x1 black pixel PNG as base64
    # Real image would be better, but this tests the pipeline
    pixel_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    return pixel_b64

def simulate_camera_upload():
    print(f"Connecting to {BACKEND_URL}...")
    
    frame_data = create_test_image_base64()
    
    payload = {
        "frameData": frame_data,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            BACKEND_URL, 
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        duration = time.time() - start_time
        
        if response.status_code == 200:
            print("Successfully processed frame!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print(f"Time taken: {duration:.2f} seconds")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Failing to connect to backend: {e}")
        print("Make sure the backend is running and accessible at localhost:13869")

def check_db_results():
    GET_URL = "http://localhost:13869/api/camera/get?number_limit=5"
    try:
        response = requests.get(GET_URL)
        if response.status_code == 200:
            print("\nLatest records in database:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error fetching results: {response.status_code}")
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    print("--- STEAM Camera Simulation ---")
    simulate_camera_upload()
    time.sleep(1) # Give it a second
    check_db_results()
