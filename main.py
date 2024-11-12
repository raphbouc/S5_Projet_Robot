import asyncio
from websockets import serve
# Correct imports based on module names and file structure
import SunFounder_PiCar_S.example.SunFounder_Line_Follower.Line_Follower as LF
import SunFounder_PiCar_S.example.line_follower as cali
import picar


async def send_status(websocket):
    # Initialize the line follower sensor
    lf = LF.Line_Follower()  
    
    while True:
        lt_status_now = lf.read_digital()  # Read current sensor status
        await websocket.send(str(lt_status_now))  # Send the status to Godot
        print(lt_status_now)
        await asyncio.sleep(0.1)  # Wait 100ms before next read

async def echo(websocket, path):
    # Launch a background task to send status continuously
    asyncio.create_task(send_status(websocket))

    # Handle incoming messages
    async for message in websocket:
        await websocket.send(f"Message reçu : {message}")  # Echo received message for testing

async def main():
    picar.setup()
    print("Starting Cali")
    cali.cali()  # Calibrate
    print("Ending Cali")
    # Specify the host (localhost) and port (8765)
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # Run server forever

asyncio.run(main())
