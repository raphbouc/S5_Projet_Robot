import time
import RPi.GPIO as GPIO

class Ultrasonic_Avoidance(object):
    timeout = 0.005

    def __init__(self, channel):
        self.channel = channel
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.channel, GPIO.OUT)

    def distance(self):
        # Shorter wait time between trigger signals
        GPIO.output(self.channel, False)
        time.sleep(0.01)
        GPIO.output(self.channel, True)
        time.sleep(0.00001)
        GPIO.output(self.channel, False)
        GPIO.setup(self.channel, GPIO.IN)

        timeout_start = time.time()
        pulse_start, pulse_end = 0, 0
        while GPIO.input(self.channel) == 0:
            pulse_start = time.time()
            if pulse_start - timeout_start > self.timeout:
                return -1
        while GPIO.input(self.channel) == 1:
            pulse_end = time.time()
            if pulse_end - timeout_start > self.timeout:
                return -1

        if pulse_start and pulse_end:
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 34300 / 2  # Speed of sound in cm/s
            return int(distance)
        else:
            return -1

    def get_distance(self, mount=3):  # Reduced mount to 3
        total_distance = 0
        for _ in range(mount):
            total_distance += self.distance()
        return total_distance // mount

    def less_than(self, alarm_gate):
        dis = self.get_distance()
        if dis >= 0 and dis <= alarm_gate:
            return 1
        elif dis > alarm_gate:
            return 0
        else:
            return -1

def test():
    UA = Ultrasonic_Avoidance(17)
    threshold = 10
    while True:
        distance = UA.get_distance()
        status = UA.less_than(threshold)
        if distance != -1:
            print(f'distance: {distance} cm')
        else:
            print('Read distance error.')

        if status == 1:
            print(f"Less than {threshold}")
        elif status == 0:
            print(f"Over {threshold}")
        else:
            print("Read distance error.")
        time.sleep(0.1)  # Reduced sleep time to avoid excessive delays

if __name__ == '__main__':
    test()
