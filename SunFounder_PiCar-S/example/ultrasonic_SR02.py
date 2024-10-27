import time
import RPi.GPIO as GPIO

SIG_PIN = 20  # Using GPIO 38 for the sensor signal
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # Disable warnings about already-used channels

def get_distance():
    # Set SIG_PIN as output to send a pulse
    GPIO.setup(SIG_PIN, GPIO.OUT)
    
    # Generate a 20 us pulse to trigger the measurement
    GPIO.output(SIG_PIN, GPIO.HIGH)
    time.sleep(0.00002)  # 20 microseconds
    GPIO.output(SIG_PIN, GPIO.LOW)

    # Set SIG_PIN as input to read the echo duration
    GPIO.setup(SIG_PIN, GPIO.IN)

    # Measure the time duration of the pulse
    rx_time = GPIO.wait_for_edge(SIG_PIN, GPIO.FALLING, timeout=100)  # Maximum wait time of 100 ms
    
    if rx_time is None:
        return 0  # No response within the given time

    distance = rx_time * 34 / 2000.0  # Convert time to distance (in cm)

    # Limit distance to between 2 cm and 800 cm
    if distance < 2 or distance > 800:
        return 0

    return distance

try:
    while True:
        distance = get_distance()
        print("distance: {:.2f} CM".format(distance))
        time.sleep(0.01)  # 10 ms pause between readings

except KeyboardInterrupt:
    print("Measurement stopped by user.")

finally:
    GPIO.cleanup()
