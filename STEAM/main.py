from camera import camera_main
from async_ultra import AsyncUltraSensor
import asyncio
import httpx
import time
import json
from datetime import datetime

SERVER_IP = "194.5.157.250"
SERVER_PORT = "13869"
BASE_URL = f"http://{SERVER_IP}:{SERVER_PORT}/api"
SLEEP_TIME = 1

camera_queue = asyncio.Queue(maxsize=1)   # Shared queue for camera results

async def main():
    # Initialize the high-precision sensor driver
    try:
        sensor = AsyncUltraSensor(trigger_pin=23, echo_pin=24)
    except Exception as e:
        print(f"Failed to initialize sensor: {e}")
        sensor = None

    async with httpx.AsyncClient() as client:
        # Start camera task in background
        asyncio.create_task(camera_main(camera_queue))
        camera_data = 0
        
        print("Starting concurrent loops (Camera + Sensor)...")
        
        try:
            while True:
                # 1. Ultrasound Measurement (Async, non-blocking)
                sensor_data = None
                if sensor:
                    # Get median of 3 samples for stability
                    sensor_data = await sensor.get_filtered_distance(samples=3)
                
                # 2. Camera Result (Read latest from queue, non-blocking)
                try:
                    camera_data = camera_queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                    
                timestamp = time.strftime('%H:%M:%S')
                print(f"[{timestamp}] Sensor: {sensor_data} cm, People: {camera_data}")
                
                # 3. Send Ultrasound Data
                if sensor_data is not None:
                    try:
                        await client.post(
                            f"{BASE_URL}/distance/new",
                            json={"distance": float(sensor_data), "trackTime": datetime.now().isoformat()},
                            timeout=2
                        )
                    except Exception as e:
                        print(f"Error sending ultrasound: {e}")

                # 4. Send Camera Frame for Processing
                if camera_data:
                    try:
                        await client.post(
                            f"{BASE_URL}/camera/frames/process",
                            json={
                                "frameData": camera_data, 
                                "timestamp": datetime.now().isoformat()
                            },
                            timeout=5 # Increased timeout for ML processing
                        )
                    except Exception as e:
                        print(f"Error sending camera frame: {e}")
                
                await asyncio.sleep(SLEEP_TIME)
        
        finally:
            if sensor:
                sensor.cleanup()
            print("Cleaned up resources.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
