# from socket import *
import io
import asyncio
import websockets
import json

url = "localhost"
post = 10002


async def test():
    while True:
        async with websockets.connect(f'ws://{url}:{post}') as websocket:    
            num = input("request order: ")
            await websocket.send(num)
            msg = await websocket.recv()
            dict = json.loads(msg)
            print(dict)
            if dict != None:
                print(dict['tx'])
                print(dict['rx'])
                print(dict['cpu_usage'].strip())
                print(dict['mem_util'].strip())
            else:
              print(msg)

loop = asyncio.get_event_loop()
loop.run_until_complete(test())
loop.run_forever()
