import time
import RPi.GPIO as GPIO

class Ultrasonic_Avoidance(object):
    timeout = 0.005

    def __init__(self, channel):
        self.channel = channel
        GPIO.setmode(GPIO.BCM)

    def distance(self):
        # Configuration de la broche en mode sortie avant d'envoyer le signal
        GPIO.setup(self.channel, GPIO.OUT)
        GPIO.output(self.channel, False)
        time.sleep(0.005)  # Réduit le délai de stabilisation à 5ms
        GPIO.output(self.channel, True)
        time.sleep(0.00001)  # Pulse de 10 microsecondes
        GPIO.output(self.channel, False)
        
        # Configuration de la broche en mode entrée pour lire la réponse
        GPIO.setup(self.channel, GPIO.IN)

        timeout_start = time.time()
        pulse_start, pulse_end = 0, 0

        # Attente du début de l'impulsion (la broche passe à HIGH)
        while GPIO.input(self.channel) == 0:
            pulse_start = time.time()
            if pulse_start - timeout_start > self.timeout:
                return -1  # Timeout si trop long

        # Attente de la fin de l'impulsion (la broche repasse à LOW)
        while GPIO.input(self.channel) == 1:
            pulse_end = time.time()
            if pulse_end - timeout_start > self.timeout:
                return -1  # Timeout si trop long

        if pulse_start and pulse_end:
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 34300 / 2  # Calcul de la distance en cm (vitesse du son)
            return int(distance)
        else:
            return 1000  # En cas d'erreur dans la mesure

    def get_distance(self, mount=3):  # Réduction du nombre de mesures
        total_distance = 0
        for _ in range(mount):
            total_distance += self.distance()
        return total_distance // mount  # Moyenne des distances mesurées

    def less_than(self, alarm_gate):
        dis = self.get_distance()
        if dis >= 0 and dis <= alarm_gate:
            return 1  # Moins que le seuil
        elif dis > alarm_gate:
            return 0  # Plus que le seuil
        else:
            return -1  # Erreur de lecture

def test():
    UA = Ultrasonic_Avoidance(17)
    threshold = 10
    while True:
        distance = UA.get_distance()
        status = UA.less_than(threshold)
        
        if distance != -1:
            print(f'distance: {distance} cm')
        else:
            print('Read distance error. 1')

        if status == 1:
            print(f"Less than {threshold}")
        elif status == 0:
            print(f"Over {threshold}")
        else:
            print("Read distance error. 2")
        
        time.sleep(0.05)  # Réduit à 50ms pour rendre la boucle encore plus réactive

if __name__ == '__main__':
    test()
