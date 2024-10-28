import RPi.GPIO as GPIO
import time

# Define the pin for the signal (B20)
SIG_PIN = 20  # Change this to match your setup

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(SIG_PIN, GPIO.OUT)
    print("Setup complete.")

def get_distance():
    # Trigger the signal
    GPIO.output(SIG_PIN, GPIO.HIGH)
    time.sleep(0.00002)  # 20 us
    GPIO.output(SIG_PIN, GPIO.LOW)
    
    # Measure the return time
    GPIO.setup(SIG_PIN, GPIO.IN)
    
    pulse_start = time.time()
    pulse_end = time.time()
    
    # Wait for the signal to go HIGH to start timing
    while GPIO.input(SIG_PIN) == 0:
        pulse_start = time.time()
    
    # Wait for the signal to go LOW to end timing
    while GPIO.input(SIG_PIN) == 1:
        pulse_end = time.time()
    
    # Calculate the time of flight
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Convert to distance in cm
    
    # Filter values outside the 2 cm to 800 cm range
    if distance < 2 or distance > 800:
        distance = 0
    
    GPIO.setup(SIG_PIN, GPIO.OUT)
    
    return round(distance, 2)

def loop():
    while True:
        distance = get_distance()
        print("Distance:", distance, "cm")
        time.sleep(0.1)

def cleanup():
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        setup()
        loop()
    except KeyboardInterrupt:
        cleanup()
