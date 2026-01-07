import asyncio
from async_ultra import AsyncUltraSensor
import signal
import sys

async def run_test():
    print("--- Sensor Verification Script (PIGPIO) ---")
    print("1. Ensure 'sudo pigpiod' is running.")
    print("2. Wiring: Trig=BCM 23 (Pin 16), Echo=BCM 24 (Pin 18)")
    print("-------------------------------------------")
    
    sensor = None
    try:
        sensor = AsyncUltraSensor(trigger_pin=23, echo_pin=24)
        print("Sensor started successfully. Reading continuously...")
        
        while True:
            # Single measurement for raw speed test
            dist = await sensor.get_distance()
            if dist is not None:
                print(f"Raw Reading: {dist:6.1f} cm")
            else:
                print("Raw Reading: TIMEOUT")
            
            # Filtered reading for stability
            f_dist = await sensor.get_filtered_distance(samples=5)
            if f_dist is not None:
                print(f"Filtered (Median of 5): {f_dist:6.1f} cm")
            else:
                print("Filtered: --")
                
            print("-" * 20)
            await asyncio.sleep(0.5)
            
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        if "pigpio connection failed" in str(e):
            print(">>> Did you forget to run 'sudo pigpiod'?")
    finally:
        if sensor:
            sensor.cleanup()
        print("\nTest finished.")

if __name__ == "__main__":
    try:
        asyncio.run(run_test())
    except KeyboardInterrupt:
        pass
