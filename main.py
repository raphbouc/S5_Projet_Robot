import asyncio
from websockets import serve
import SunFounder_PiCar_S.example.SunFounder_Line_Follower.Line_Follower as LF
import SunFounder_PiCar_S.example.SunFounder_Ultrasonic_Avoidance.Ultrasonic_Avoidance as UA
import picar
import SunFounder_PiCar.picar.back_wheels as back_wheels
import SunFounder_PiCar.picar.front_wheels as front_wheels
import json
import time

lf = LF.Line_Follower()
REFERENCES = [56.0, 71.0, 70.0, 78.5, 51.5]
lf.references = REFERENCES
Ultra_A = UA.Ultrasonic_Avoidance(20)
fw = front_wheels.Front_Wheels(db='config')
bw = back_wheels.Back_Wheels(db='config')

fw.ready()
bw.ready()
fw.turning_max = 45

value_array = [-1, -1, -1, -1 , -1]  # Partagé
us_output = -1  # Stocke la médiane calculée

# Création d'un verrou pour synchroniser l'accès aux variables partagées
value_array_lock = asyncio.Lock()
us_output_lock = asyncio.Lock()


def push_to_data_array(input, array, max_length):
    if len(array) < max_length:
        if input < 70:
            array.append(input)
    else:
        array.pop(0)
        array.append(input)


def median_input(array):
    sorted_array = sorted(array)
    n = len(sorted_array)
    if n % 2 == 0:  # Si pair
        median = (sorted_array[n // 2 - 1] + sorted_array[n // 2]) / 2
    else:  # Si impair
        median = sorted_array[n // 2]
    return median


async def update_distance():
    """Tâche dédiée pour lire les distances et calculer la médiane."""
    global value_array, us_output
    while True:
        distance = Ultra_A.get_distance()
        print("distance", distance)
        # Utilisation du verrou pour mettre à jour value_array
        async with value_array_lock:
            if distance != -1:
                push_to_data_array(distance, value_array, 5)
            local_value_array = value_array.copy()

        # Calcul de la médiane sous verrou
        async with us_output_lock:
            us_output = median_input(local_value_array)

        await asyncio.sleep(0.1)  # Lecture toutes les 100ms

async def calibrate():
    """Calibrate the line follower sensor."""
    print("Starting calibration")
    references = [0, 0, 0, 0, 0]
    num_measurements = 5  # Number of measurements to average

    # White calibration
    print("Place sensors on white surface...")
    fw.turn(0)
    await asyncio.sleep(4)  # Give some time to place the sensors
    white_values = [lf.get_average(100) for _ in range(num_measurements)]
    white_references = [sum(values) / num_measurements for values in zip(*white_values)]

    # Black calibration
    print("Place sensors on black surface...")
    fw.turn(90)
    await asyncio.sleep(4)  # Give some time to place the sensors
    black_values = [lf.get_average(100) for _ in range(num_measurements)]
    black_references = [sum(values) / num_measurements for values in zip(*black_values)]

    # Calculate middle references
    references = [(w + b) / 2 for w, b in zip(white_references, black_references)]
    lf.references = references

    print("Calibration completed. References:", references)
    

async def send_status(websocket):
    """Envoie les données du suiveur de ligne et de la distance."""
    global us_output, value_array
    distance_state = 1
    startTime = None
    while True:
        lt_status_now = lf.read_digital()  # Lecture des capteurs de ligne

        array_message = lt_status_now.copy()
        elapsed_time = 0
        if startTime:
            elapsed_time = time.time() - startTime
            print(f"Elapsed time: {elapsed_time}")

        # Lecture de `us_output` sous verrou
        async with us_output_lock:
            local_us_output = us_output

        # Logique d'état basée sur `us_output`
        if local_us_output > 0:
            if local_us_output < 33 and distance_state == 1:
                distance_state = 2
                print("In state 2")
            elif local_us_output < 13 and distance_state == 2:
                distance_state = 3
                print("In state 3")
            elif local_us_output > 27 and distance_state == 3:
                distance_state = 4
                startTime = time.time()
                elapsed_time = 0
                print("First timer started in state 4")
        if elapsed_time > 4.25 and distance_state == 4:
            distance_state = 5
            elapsed_time = 0
            startTime = time.time()
            print("Second timer started in state 5")
        elif elapsed_time > 3 and distance_state == 5:
            distance_state = 6
            elapsed_time = 0
            startTime = time.time()
            print("In state 6")
        elif elapsed_time > 2 and distance_state == 6:
            distance_state = 7
            print("In state 7")
        elif sum(lt_status_now) >= 1 and distance_state == 7:
            distance_state = 1
            value_array = [-1, -1, -1, -1, -1]
            print("Back to state 1")

        array_message.append(distance_state)
        await websocket.send(json.dumps(array_message))
        await asyncio.sleep(0.2)  # Pause entre les envois


async def echo(websocket, path):
    """Gère les messages entrants et lance `send_status`."""
    asyncio.create_task(send_status(websocket))
    async for message in websocket:
        speed, rotation = process_message(message)
        if speed < 0:
            bw.speed = abs(speed)
            bw.backward()
        else:
            bw.speed = speed
            bw.forward()
        fw.turn(rotation)
        print(f"Speed: {speed}, Rotation: {rotation}")


def process_message(json_message):
    try:
        data = json.loads(json_message)
        speed = int(float(data.get("speed", 0)) * 300)
        rotation = int(float(data.get("rotation", 0)) + 90)
        rotation = max(45, min(rotation, 135))
        return speed, rotation
    except Exception as e:
        print(f"Error processing message: {e}")
        return None


def destroy():
    bw.stop()
    fw.turn(90)


async def main():
    try:
        picar.setup()
        await calibrate()
        asyncio.create_task(update_distance())  # Démarre la tâche async
        async with serve(echo, "localhost", 8765):
            await asyncio.Future()  # Garder le serveur actif
    except Exception as e:
        print(e)
        print('error try again in 5')
        destroy()
        time.sleep(5)
    except KeyboardInterrupt:
        destroy()


asyncio.run(main())

