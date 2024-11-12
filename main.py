import asyncio
from websockets import serve
import SunFounder_PiCar_S.example.SunFounder_Line_Follower.Line_Follower as LF
import picar

lf = LF.Line_Follower()  
REFERENCES = [200, 200, 200, 200, 200]
lf.references = REFERENCES

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
        lt_status_now = lf.read_digital()  # Read current sensor status
        await websocket.send(str(lt_status_now))  # Send the status to Godot
        await asyncio.sleep(0.1)  # Wait 100ms before next read

async def echo(websocket, path):
    """Handle incoming messages and launch send_status task."""
    asyncio.create_task(send_status(websocket))
    async for message in websocket:
        await websocket.send(f"Message reçu : {message}")  # Echo received message

async def main():
    picar.setup()
    await calibrate()  # Calibrate before starting the server
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # Run server forever

asyncio.run(main())
