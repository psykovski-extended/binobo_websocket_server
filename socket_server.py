import asyncio
import websockets
import psycopg2
from ast import literal_eval
import time
import socket


async def store_data(data, token):
    cursor.execute("select * from data_access_token;")
    res = cursor.fetchall()
    token_id = 0
    for row in res:
        if row[1] == token:
            token_id = row[0]
            break

    if token_id == 0:
        return False

    time_ = round(time.time() * 1000)
    query = """INSERT INTO robot_data (
                if_tip, if_middle, if_base, if_base_rot,
                mf_tip, mf_middle, mf_base, mf_base_rot,
                rf_tip, rf_middle, rf_base, rf_base_rot,
                p_tip, p_middle, p_base, p_base_rot,
                th_tip, th_base, th_rot_orthogonal, th_rot_palm,
                wr_lr, wr_bf, data_access_token_id, uploaded_on,
                expired, sampling_rate
            ) VALUES
            """
    for i in data:
        query += "(" + str(i[0]) + "," + str(i[1]) + "," + str(i[2]) + "," + str(i[3]) + "," + str(
            i[4]) + "," + str(i[5]) + "," + str(i[6]) + "," + str(i[7]) + "," + str(
            i[8]) + "," + str(i[9]) + "," + str(i[10]) + "," + str(i[11]) + "," + str(
            i[12]) + "," + str(i[13]) + "," + str(i[14]) + "," + str(i[15]) + "," + str(
            i[16]) + "," + str(i[17]) + "," + str(i[18]) + "," + str(i[19]) + "," + str(
            i[20]) + "," + str(i[21]) + "," + str(token_id) + "," + str(time_) + "," + "false" + "," + "30),"

    try:
        cursor.execute(query[:-1] + ";")
        connection.commit()
    except Exception:
        return False
    return True


async def retrieve_data(websocket, path):
    async for message in websocket:
        data = literal_eval(message)
        try:
            await store_data(data[1], data[0])
        except Exception as exc:
            await websocket.send(str({'Error': str(exc)}))


async def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    ip = sock.getsockname()[0]
    print("Websocket Server running on:\n" + ip + ":8080")
    async with websockets.serve(retrieve_data, ip, 8080, ping_interval=None):
        await asyncio.Future()  # run forever


connection = None
# password = input("Your Database Password: ")
try:
    connection = psycopg2.connect(host='binobo_database',
                                  database='binobo_db',
                                  user='postgres',
                                  password="password",
                                  port=5432)
    time.sleep(1)

    print("Database-Connection status: True")

    cursor = connection.cursor()
except Exception as e:
    print(e)
    print("Database-Connection status: False")

asyncio.run(main())
