import websockets
import asyncio
import json
import functools


buf_list = []
buf_dir = {
    'tx': '',
    'rx': '',
    'cpu_usage': '',
    'mem_util': ''
}

url_receive = "localhost"
post_receive = 10001

url_send = "localhost"
post_send = 10002

'''
receive from vm
param:
    dic{
        'tx': '',
        'rx': '',
        'cpu_usage': '',
        'mem_util': '',
        'id': ''
    }
'''
async def recv_nic_inform(websocket, path, buf):
    request = await websocket.recv()
    request_dict = json.loads(request)
    buf_order = int(request_dict['id'])
    if buf_order <  len(buf_list):
        buf[buf_order]['tx'] = request_dict['tx']
        buf[buf_order]['rx'] = request_dict['rx']
        buf[buf_order]['cpu_usage'] = request_dict['cpu_usage']
        buf[buf_order]['mem_util'] = request_dict['mem_util']
    else:
        dir={
            'tx': request_dict['tx'],
            'rx': request_dict['rx'],
            'cpu_usage': request_dict['cpu_usage'],
            'mem_util': request_dict['mem_util']
        }
        buf.append(dir)
    print(f"request: {request} ")
    print("tx: ", request_dict['tx'])
    print("rx: ", request_dict['rx'])
    print("cpu_usage: ", request_dict['cpu_usage'])
    print("mem_util: ", request_dict['mem_util'])

'''
send vm(id=order) to front end
param: order(0,amount of vm)
'''
async def send_nic_inform(websocket, path, buff):
    order = await websocket.recv()
    order = int(order)
    if order < len(buff):
        msg = {
            "tx": f"{buff[order]['tx']}",
            "rx": f"{buff[order]['rx']}",
            "cpu_usage": f"{buff[order]['cpu_usage']}",
            "mem_util": f"{buff[order]['mem_util']}"
        }
        print(msg)

        msg = json.dumps(msg)
        await websocket.send(msg)
    else:
        msg = "null"
        await websocket.send(msg)


print('waiting for connection...')


if __name__ == "__main__":
  #receive server
  bound_handler = functools.partial(recv_nic_inform, buf=buf_list)
  server = websockets.serve(bound_handler, url_receive, post_receive)
  asyncio.ensure_future(server)

  #send server
  bound_handler_front = functools.partial(send_nic_inform, buff=buf_list)
  server_front = websockets.serve(bound_handler_front, url_send, post_send)
  asyncio.ensure_future(server_front)
  #asyncio.get_event_loop().run_until_complete(server_front)

  asyncio.get_event_loop().run_forever()
