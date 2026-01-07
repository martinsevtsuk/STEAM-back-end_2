# Walkthrough: ML Service Separation & Frame Processing

I have successfully implemented the requested changes to offload people detection from the Raspberry Pi to a dedicated ML service.

## Changes Overview

### 1. New Python ML Service (`ml-service/`)

- Created a Flask-based microservice that uses YOLO11 for people detection.
- **Endpoint:** `POST /detect` accepts base64-encoded images and returns the people count.
- **Benefits:** Offloads heavy processing from the IoT device, allowing for faster capture on the Pi and better scalability.

### 2. Spring Boot Backend Updates

- **`CameraFrameDTO`**: New data transfer object for receiving frame data.
- **`MLServiceClient`**: New service that forwards frames to the ML service and retrieves the count.
- **`CameraPeopleManager`**: Added a new endpoint `POST /api/camera/frames/process` which orchestrates the flow:
  1. Receives frame from Pi.
  2. Forwards to ML service.
  3. Saves the resulting count to the database.

### 3. Raspberry Pi Client Updates (`STEAM/`)

- **`camera.py`**: Removed local YOLO logic. Now captures frames, encodes them as JPEG (base64), and puts them into a queue.
- **`main.py`**: Updated to send frames to the new backend endpoint instead of calculating the count locally.
- **`requirements.txt`**: Removed heavy ML dependencies (`ultralytics`, `torch`) to reduce memory footprint from ~500MB to ~50MB.

### 4. Docker Orchestration

- Updated `services.yaml` to include the `ml-service` and a pre-configured `backend` service.
- Configured network dependencies so the backend can reach the ML service via `http://ml-service:5000`.

### Verification Results

#### 1. Build & Startup

- **Spring Boot Backend:** Successfully built and running in Docker.
- **ML Service:** Successfully loading YOLO11 and running on port 5005 (host) / 5000 (container).
- **Database:** PostgreSQL 14 running and healthy.

#### 2. End-to-End Simulation

I ran a simulation script (`simulate_camera.py`) which performed the following:

1. Sent a base64-encoded frame to the backend.
2. Backend forwarded the frame to the ML service.
3. ML service performed inference and returned 0 (correct for a black pixel).
4. Data was successfully stored in the database and verified via GET request.

**Logs from ML Service:**

```
2026-01-07 08:33:18,878 - __main__ - INFO - Running people detection...
2026-01-07 08:33:19,078 - __main__ - INFO - Detected 0 people
2026-01-07 08:33:19,079 - werkzeug - INFO - 172.19.0.4 - - POST /detect HTTP/1.1 200 -
```

## How to Run

1. **Start the Infrastructure:**

   ```bash
   docker-compose -f services.yaml up --build -d
   ```

   _Note: Using port 5005 for the ML service on the host to avoid macOS Control Center conflicts._

2. **Run Simulation (Optional):**

   ```bash
   python3 simulate_camera.py
   ```

3. **Deploy to Pi:**
   Update the `STEAM` folder on your Raspberry Pi and install the lighter requirements:
   ```bash
   pip install -r requirements.txt
   ```
