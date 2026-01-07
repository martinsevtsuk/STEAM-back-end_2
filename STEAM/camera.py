import cv2 as cv
import base64
import asyncio
import time

async def camera_main(queue):
    """
    Captures frames from the camera, encodes them as JPEG in base64,
    and pushes them to the shared queue.
    """
    capture = cv.VideoCapture(0)
    
    # Low resolution to save bandwidth and processing power
    capture.set(cv.CAP_PROP_FRAME_WIDTH, 160)
    capture.set(cv.CAP_PROP_FRAME_HEIGHT, 120)
    capture.set(cv.CAP_PROP_FPS, 10)

    if not capture.isOpened():
        print("Cannot open camera. Exiting...")
        return

    print("Camera capture started (ML offloaded)...")

    try:
        while True:
            ret, frame = capture.read()
            if not ret:
                print("Cannot receive frame. Exiting...")
                break
            
            # Encode frame as JPEG
            # Use lower quality to reduce payload size (0-100)
            success, buffer = cv.imencode('.jpg', frame, [int(cv.IMWRITE_JPEG_QUALITY), 60])
            
            if success:
                # Convert to base64 string
                base64_frame = base64.b64encode(buffer).decode('utf-8')
                
                # Push base64 frame to queue (overwrites old data)
                if queue.full():
                    try:
                        queue.get_nowait()   # remove oldest entry
                    except asyncio.QueueEmpty:
                        pass
                
                queue.put_nowait(base64_frame)

            await asyncio.sleep(0) # Yield control to event loop
            
    finally:
        capture.release()
        print("Camera released.")

if __name__ == "__main__":
    print("Starting camera capture test...")
    q = asyncio.Queue(maxsize=1)
    try:
        asyncio.run(camera_main(q))
    except KeyboardInterrupt:
        print("Stopped.")
