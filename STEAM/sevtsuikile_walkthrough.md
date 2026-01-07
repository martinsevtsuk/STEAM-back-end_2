# Walkthrough: Robust Ultrasonic Sensor Implementation

The ultrasonic sensor was previously returning "garbage info" or failing due to the overhead of Python timing or the "busy-wait" nature of the C++ driver. I have switched the implementation to use the `pigpio` library, which provides hardware-timed callbacks for microsecond precision.

## Key Changes

### 1. Robust Async Sensor Driver

Revised [async_ultra.py](file:///Users/kds/Code/steam_raspberry_type_shi/async_ultra.py) to use `pigpio` callbacks.

- **Hardware Timing**: Instead of Python checking the pin state in a loop (which varies based on CPU load), `pigpio` records the exact microsecond timestamp of the echo pulse edges in the Pi's DMA hardware.
- **True Async**: The driver now uses `asyncio.Future`. It sends the trigger pulse and then "yields" control. When the hardware detects the echo end, it triggers a callback that resolves the future. This allows the camera to process images while sound is traveling in the air.

### 2. Concurrent Main Loop

Updated [main.py](file:///Users/kds/Code/steam_raspberry_type_shi/main.py) to handle both sensors seamlessly.

- Initializing `AsyncUltraSensor` once.
- Running camera detection in the background.
- Periodically fetching filtered (median) distance readings to eliminate noise.
- Sending both results to the backend.

### 3. Dependency Management

Added `pigpio` to [requirements.txt](file:///Users/kds/Code/steam_raspberry_type_shi/requirements.txt).

> [!NOTE] > **Legacy Files Kept**: As requested, `ultra_driver.cpp` and `compile_driver.sh` were not deleted. They are preserved in the repository for historical reference.

## Verification Summary

Since this is a hardware-dependent fix, verification must be performed on the Raspberry Pi.

### How to Verify

1.  **Install dependencies**:
    ```bash
    pip install pigpio
    ```
2.  **Start the pigpio daemon** (Critical):
    ```bash
    sudo pigpiod
    ```
3.  **Run the standalone test script**:
    ```bash
    python verify_sensor_pigpio.py
    ```
    - Observe if the readings are stable and match actual distances.
4.  **Run the main application**:
    ```bash
    python main.py
    ```
    - Ensure the log shows continuous updates for both "Sensor" and "People".

## Code Comparison (Old vs New Logic)

| Feature             | Old (C++/Python loop)       | New (pigpio Callbacks)           |
| :------------------ | :-------------------------- | :------------------------------- |
| **Precision**       | Millisecond (unstable)      | **Microsecond (hardware-timed)** |
| **Blocking**        | Blocks thread while waiting | **Non-blocking (async/await)**   |
| **Noise Filtering** | Minimal                     | **Median of 5 samples**          |
| **Reliability**     | "Garbage info" on busy CPU  | **Constant precision**           |
