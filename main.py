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
threshold = 10
value_array = [-1,-1,-1, -1, -1]

fw.ready()
bw.ready()
fw.turning_max = 45


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
    
    # Calculer la médiane
    if n % 2 == 0:  # Si le nombre d'éléments est pair
        median = (sorted_array[n // 2 - 1] + sorted_array[n // 2]) / 2
    else:  # Si le nombre d'éléments est impair
        median = sorted_array[n // 2]
        
    return median

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


def process_message(json_message):
    try:
        # Convertir le JSON string en dictionnaire Python
        data = json.loads(json_message)
        
        # Récupérer et arrondir les valeurs
        speed = int(float(data.get("speed", 0)) * 300)  # Multiplier par 150
        rotation = int(float(data.get("rotation", 0)) + 90)  # Arrondir la rotation
        
        # Limiter la rotation à 45 si nécessaire
        if rotation < 45:
            rotation = 45
        elif rotation > 135:
            rotation = 135
        else : 
            rotation = rotation
        return speed, rotation
    
    except (ValueError, TypeError, json.JSONDecodeError) as e:
        print(f"Erreur lors du traitement du message JSON : {e}")
        return None

async def send_status(websocket):
    """Send line follower status to Godot."""
    distance_state = 1
    startTime = None
    while True:
        distance = Ultra_A.get_distance()
        # print(f"measured distance {distance}")
        push_to_data_array(distance, value_array, 5)
        #print(f"value array: {value_array}")
        if distance_state <= 5:
            us_output = median_input(value_array)
            print("us_output", us_output)
            print("median complet", value_array)
        else: 
            us_output = -1
        # print(f"output de la mediane: {us_output}")
        lt_status_now = lf.read_digital()  # Read current sensor status
        
        array_message = []
        array_message.append(lt_status_now[0])
        array_message.append(lt_status_now[1])
        array_message.append(lt_status_now[2])
        array_message.append(lt_status_now[3])
        array_message.append(lt_status_now[4])
        elapsed_time = 0
        if startTime != None:
            elapsed_time = time.time() - startTime
            print(f"elapsed_time right now is {elapsed_time}")

        if us_output > 0:
            if us_output < 34 and distance_state == 1:
                distance_state = 2
                print("in state 2")
            elif us_output < 14 and distance_state == 2:
                distance_state = 3
                print("in state 3")
            elif us_output > 28 and distance_state == 3:
                distance_state = 4
                startTime = time.time()
                elapsed_time = 0
                print("first timer starteds in state 4")
        if elapsed_time > 4.25 and distance_state == 4:
            distance_state = 5
            startTime = time.time()
            elapsed_time = 0
            print("second timer started in state 5")
        elif elapsed_time > 3 and distance_state == 5:
            distance_state = 6
            startTime = time.time()
            elapsed_time = 0
            print("in state 6")
        elif elapsed_time >  2 and distance_state == 6:
            distance_state = 7
            print("in state 7")
        elif sum(lt_status_now) >= 1 and distance_state == 7:
            distance_state = 1
            print("back to state 1")

        array_message.append(distance_state)
        await websocket.send(json.dumps(array_message))
        print(array_message)

        await asyncio.sleep(0.2)  # Wait 100ms before next read

async def echo(websocket, path):
    """Handle incoming messages and launch send_status task."""
    asyncio.create_task(send_status(websocket))
    async for message in websocket:
        speed, rotation = process_message(message)
        if (speed < 0):
            speed = speed/-1
            bw.speed = speed
            bw.backward()
        elif (speed > 0):
            bw.speed = speed
            bw.forward()
        fw.turn(rotation)
        print(f"speed is {speed}, rotation is {rotation}")
        
def destroy():
	bw.stop()
	fw.turn(90)

async def main():
    try:
        try: 
            picar.setup()
            await calibrate()  # Calibrate before starting the server
            async with serve(echo, "localhost", 8765):
                await asyncio.Future()  # Run server forever
        except Exception as e:
            print(e)
            print('error try again in 5')
            destroy()
            time.sleep(5)
    except KeyboardInterrupt:
        destroy()
            

asyncio.run(main())
