import time
import RPi.GPIO as GPIO

SIG_PIN = 38  # PIN GPIO pour le signal du capteur (modifiez en fonction de votre configuration)
GPIO.setmode(GPIO.BCM)
GPIO.setup(SIG_PIN, GPIO.OUT)

def get_distance():
    # Générer une impulsion de 20 µs pour déclencher la mesure
    GPIO.output(SIG_PIN, GPIO.HIGH)
    time.sleep(0.00002)  # 20 microsecondes
    GPIO.output(SIG_PIN, GPIO.LOW)

    # Mettre le pin en mode input pour lire la durée de l'écho
    GPIO.setup(SIG_PIN, GPIO.IN)

    # Lire le temps de la durée de l'impulsion
    rx_time = GPIO.wait_for_edge(SIG_PIN, GPIO.FALLING, timeout=100) # Temps maximum d'attente 100 ms
    
    if rx_time is None:
        return 0  # Pas de réponse dans le délai imparti

    distance = rx_time * 34 / 2000.0  # Convertir le temps en distance (en cm)

    # Limiter la distance entre 2 cm et 800 cm
    if distance < 2 or distance > 800:
        return 0

    return distance

try:
    while True:
        distance = get_distance()
        print(f"distance: {distance:.2f} CM")
        time.sleep(0.01)  # Pause de 10 ms

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
