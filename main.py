import asyncio
from websockets.server import serve
import SunFounder_PiCar_S.example.SunFounder_Line_Follower.Line_Follower as LineFollower
import SunFounder_PiCar_S.example.line_follower as cali


async def send_status(websocket):
    lf = LineFollower.Line_Follower()  # Initialise le capteur de suivi de ligne
    cali.cali()  # Calibrage

    while True:
        lt_status_now = lf.read_digital()  # Lit l'état actuel du capteur
        await websocket.send(str(lt_status_now))  # Envoie lt_status_now à Godot
        await asyncio.sleep(0.1)  # Attends 100 ms avant la prochaine lecture


async def echo(websocket):
    # Lance une tâche asynchrone pour envoyer le statut en continu
    asyncio.create_task(send_status(websocket))

    # Gère les messages entrants s'il y a lieu
    async for message in websocket:
        await websocket.send(f"Message reçu : {message}")  # Répond pour tester la connexion


async def main():
    async with serve(echo, None, 8765):
        await asyncio.Future()  # run forever

asyncio.run(main())
