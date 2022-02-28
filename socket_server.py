import asyncio
import websockets
import socket

receiver_clients = {}


async def add_to_receiver_clients(ws_client, message):
    token = ws_client.path.split('/')[-1]
    if message == "close session":
        for client_index in range(len(receiver_clients[token])):
            if ws_client == receiver_clients[token][client_index]:
                del receiver_clients[token][client_index]
                break
    else:
        if token in receiver_clients.keys():
            receiver_clients[token].append(ws_client)
        else:
            receiver_clients[token] = [ws_client]
        await ws_client.send(str({'STATE': 'OK'}))
    print(receiver_clients)


async def retrieve_data(websocket, path):
    if websocket.path != '/':
        async for message in websocket:
            await add_to_receiver_clients(websocket, message)
    else:
        async for message in websocket:
            data = eval(message)
            try:
                token = data[0]
                robo_data = data[1]
                clients_to_delete = []
                for client_index in range(len(receiver_clients[token])):
                    try:
                        await receiver_clients[token][client_index].send(str(robo_data))
                    except Exception as exc:
                        print('error occurred: ' + str(exc))
                        clients_to_delete.append([client_index])
                clients_to_delete.reverse()
                for i in clients_to_delete:
                    del receiver_clients[token][i]
            except Exception as exc:
                await websocket.send(str({'Error': str(exc)}))


async def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    ip = sock.getsockname()[0]
    print("Websocket Server running on:\n" + ip + ":8080")
    async with websockets.serve(retrieve_data, ip, 8080, ping_interval=None, ping_timeout=None):
        await asyncio.Future()  # run forever


asyncio.run(main())
