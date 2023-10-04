import asyncio
import websockets

async def hello(websocket, path):
    print(f"New client connected.")
    
    message = "hello guys"
    await websocket.send(message)
    print(f"Sent to client: {message}")

    async for received_message in websocket:
        print(f"Received from client: {received_message}")

async def start_server():
    server = await websockets.serve(hello, "localhost", 8765)
    print(f"WebSocket server started and listening on ws://localhost:8765")
    await server.wait_closed()

asyncio.run(start_server())
