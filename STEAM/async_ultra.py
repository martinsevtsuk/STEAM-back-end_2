import asyncio
import pigpio
import time
import statistics
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AsyncUltraSensor:
    def __init__(self, trigger_pin=23, echo_pin=24):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.pi = pigpio.pi()
        
        if not self.pi.connected:
            logger.error("Could not connect to pigpiod. Is 'sudo pigpiod' running?")
            raise RuntimeError("pigpio connection failed")

        # Set up pins
        self.pi.set_mode(self.trigger_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.echo_pin, pigpio.INPUT)
        
        # Internal state for measurement
        self._tick_high = None
        self._future = None
        
        # Set up callback for the echo pin
        self._cb = self.pi.callback(self.echo_pin, pigpio.EITHER_EDGE, self._cbf)
        logger.info(f"AsyncUltraSensor initialized on Trig={trigger_pin}, Echo={echo_pin}")

    def _cbf(self, gpio, level, tick):
        """Callback function for pigpio to capture edge timing."""
        if level == 1:
            self._tick_high = tick
        else:
            if self._tick_high is not None:
                diff = pigpio.tickDiff(self._tick_high, tick)
                if self._future and not self._future.done():
                    self._future.set_result(diff)
                self._tick_high = None

    async def get_distance(self, timeout=0.1):
        """
        Trigger a measurement and wait for the echo pulse duration.
        Returns distance in cm or None on timeout.
        """
        self._future = asyncio.get_running_loop().create_future()
        
        # Send 10us trigger pulse
        self.pi.gpio_trigger(self.trigger_pin, 10, 1)
        
        try:
            # Wait for the callback to set the result
            duration_us = await asyncio.wait_for(self._future, timeout=timeout)
            
            # Distance = (time * speed_of_sound) / 2
            # 343 m/s = 0.0343 cm/us
            distance_cm = (duration_us * 0.0343) / 2
            return distance_cm
        except asyncio.TimeoutError:
            return None
        finally:
            self._future = None

    async def get_filtered_distance(self, samples=5, delay=0.03):
        """
        Get the median of multiple measurements to filter noise.
        """
        readings = []
        for _ in range(samples):
            d = await self.get_distance()
            if d is not None and 2.0 < d < 400.0:
                readings.append(d)
            await asyncio.sleep(delay)
            
        if not readings:
            return None
            
        return statistics.median(readings)

    def cleanup(self):
        """Stop the callback and disconnect from pigpio."""
        if self._cb:
            self._cb.cancel()
        if self.pi:
            self.pi.stop()

async def main():
    """Local test loop"""
    sensor = None
    try:
        sensor = AsyncUltraSensor(trigger_pin=23, echo_pin=24)
        print("Starting sensor loop... Press Ctrl+C to stop.")
        while True:
            dist = await sensor.get_filtered_distance(samples=3)
            if dist is not None:
                print(f"Distance: {dist:.1f} cm")
            else:
                print("Distance: -- (Timeout or Out of Range)")
            await asyncio.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if sensor:
            sensor.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
