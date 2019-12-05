#!/usr/bin/python3
import os
import asyncio
import json
import websockets
import psutil
import time

SERVER = ''# SERVER URL
HISTORY = []
HISTORY_LEN = 10

def get_tx_bytes():
    res = os.popen('ethtool -S rdma0 | grep vport_rdma_unicast_bytes').read().strip()
    res = [l.strip() for l in res.split('\n')]
    res = [l.split() for l in res]

    tx_bytes = [int(l[1]) for l in res if 'tx' in l[0]]
    rx_bytes = [int(l[1]) for l in res if 'rx' in l[0]]

    return tx_bytes, rx_bytes

def get_mem_util():
    return psutil.virtual_memory().percent

def get_cpu_util():
    return psutil.cpu_percent()


# add param: id
async def show_rates():
    pre_tx_bytes, pre_rx_bytes = get_tx_bytes()
    connected = False
    while True:
        async with websockets.connect("ws://localhost:10001") as websocket:
            await asyncio.sleep(1)
            cur_tx_bytes, cur_rx_bytes = get_tx_bytes()
            pre_tx_sum = sum(pre_tx_bytes)
            pre_rx_sum = sum(pre_rx_bytes)
            cur_tx_sum = sum(cur_tx_bytes)
            cur_rx_sum = sum(cur_rx_bytes)

            tx_diff = cur_tx_sum - pre_tx_sum
            rx_diff = cur_rx_sum - pre_rx_sum

            mem_util = get_mem_util()
            cpu_util = get_cpu_util()

            msg = {
                "tx": "{0:.2f}".format(tx_diff/(1024 ** 2)),
                "rx": "{0:.2f}".format(rx_diff/(1024 ** 2)),
                "cpu_usage": "{0: .2f}".format(cpu_util),
                "mem_util": "{0: .2f}".format(mem_util),
                "id": "0"
            }
            HISTORY.append(msg)

            msg = json.dumps(msg)

            await websocket.send(msg)
            #time.sleep(5)

            pre_tx_bytes = cur_tx_bytes
            pre_rx_bytes = cur_rx_bytes


if __name__ == '__main__':
    #server = websockets.serve(show_rates, 'localhost', 10001)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(show_rates())
    loop.run_forever()

