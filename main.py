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
REFERENCES = [200, 200, 200, 200, 200]
lf.references = REFERENCES
Ultra_A = UA.Ultrasonic_Avoidance(20)
fw = front_wheels.Front_Wheels(db='config')
bw = back_wheels.Back_Wheels(db='config')
threshold = 10
value_array = []

fw.ready()
bw.ready()
fw.turning_max = 45


def push_to_data_array(input, array, max_length):
    if len(array) < max_length:
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
    mount = 100  # Number of measurements for average calculation

    # White calibration
    print("Place sensors on white surface...")
    await asyncio.sleep(4)  # Give some time to place the sensors
    white_references = lf.get_average(mount)

    # Black calibration
    print("Place sensors on black surface...")
    await asyncio.sleep(4)  # Give some time to place the sensors
    black_references = lf.get_average(mount)

    # Calculate middle references
    for i in range(5):
        references[i] = (white_references[i] + black_references[i]) / 2
    lf.references = references

    print("Calibration completed. References:", references)

def process_message(json_message):
    try:
        # Convertir le JSON string en dictionnaire Python
        data = json.loads(json_message)
        
        # Récupérer et arrondir les valeurs
        speed = int(float(data.get("speed", 0)))  # Arrondir la vitesse
        rotation = int(float(data.get("rotation", 0)))  # Arrondir la rotation
        
        # Limiter la rotation à 45 si nécessaire
        if rotation > 45:
            rotation = 45
        
        return speed, rotation
    
    except (ValueError, TypeError, json.JSONDecodeError) as e:
        print(f"Erreur lors du traitement du message JSON : {e}")
        return None

async def send_status(websocket):
    """Send line follower status to Godot."""
    while True:
        distance = Ultra_A.get_distance()
        push_to_data_array(distance, value_array, 10)
        us_output = median_input(value_array)
        lt_status_now = lf.read_digital()  # Read current sensor status
        
        array_message = []
        array_message.append(lt_status_now[0])
        array_message.append(lt_status_now[1])
        array_message.append(lt_status_now[2])
        array_message.append(lt_status_now[3])
        array_message.append(lt_status_now[4])
        array_message.append(us_output)

        await websocket.send(json.dumps(array_message))

        await asyncio.sleep(0.1)  # Wait 100ms before next read

async def echo(websocket, path):
    """Handle incoming messages and launch send_status task."""
    asyncio.create_task(send_status(websocket))
    async for message in websocket:
        speed, rotation = process_message(message)
        bw.speed = speed
        fw.turn(rotation)
        print(speed, rotation)
        
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
