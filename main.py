import asyncio
from websockets import serve
import SunFounder_PiCar_S.example.SunFounder_Line_Follower.Line_Follower as LF
from SunFounder_PiCar_S.example.SunFounder_Ultrasonic_Avoidance.Ultrasonic_Avoidance import Ultrasonic_Avoidance
import picar
import json


lf = LF.Line_Follower()  
REFERENCES = [200, 200, 200, 200, 200]
lf.references = REFERENCES
UA = Ultrasonic_Avoidance.Ultrasonic_Avoidance(20)
threshold = 10
value_array = []

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

async def send_status(websocket):
    """Send line follower status to Godot."""
    while True:
        distance = UA.get_distance()
        push_to_data_array(distance, value_array, 10)
        us_output = median_input(value_array)
        lt_status_now = lf.read_digital()  # Read current sensor status
        
        message = {
            "lt_status": lt_status_now,
            "us_output": us_output
        }

        json_message = json.dumps(message)

        await websocket.send(json_message)  # Send the status to Godot
        print("Message envoyé : ", json_message)
        await asyncio.sleep(0.1)  # Wait 100ms before next read

async def echo(websocket, path):
    """Handle incoming messages and launch send_status task."""
    asyncio.create_task(send_status(websocket))
    async for message in websocket:
        print(message)

async def main():
    picar.setup()
    await calibrate()  # Calibrate before starting the server
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # Run server forever

asyncio.run(main())
