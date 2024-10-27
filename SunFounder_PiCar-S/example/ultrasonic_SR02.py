import time
import RPi.GPIO as GPIO

SIG_PIN = 38  # Utiliser GPIO 38 pour le signal du capteur
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # Désactiver les avertissements

def get_distance():
    # Configurer SIG_PIN en sortie pour envoyer une impulsion
    GPIO.setup(SIG_PIN, GPIO.OUT)
    
    # Générer une impulsion de 20 us pour déclencher la mesure
    GPIO.output(SIG_PIN, GPIO.HIGH)
    time.sleep(0.00002)  # 20 microsecondes
    GPIO.output(SIG_PIN, GPIO.LOW)

    # Configurer SIG_PIN en entrée pour lire la durée de l'écho
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
    print("Measurement stopped by user.")

finally:
    GPIO.cleanup()
