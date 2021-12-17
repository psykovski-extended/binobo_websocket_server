import asyncio
import websockets
import mysql.connector
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

    for i in data:
        print(i)
        query = """INSERT INTO robot_data (
            p_tip, p_middle, p_base, p_base_rot,
            rf_tip, rf_middle, rf_base, rf_base_rot,
            mf_tip, mf_middle, mf_base, mf_base_rot,
            if_tip, if_middle, if_base, if_base_rot,
            th_tip, th_base, th_rot_orthogonal, th_rot_palm,
            wr_lr, wr_bf, data_access_token_id, uploaded_on,
            expired, sampling_rate
        ) VALUES (
        """ + str(int(i[0])) + "," + str(int(i[1])) + "," + str(int(i[2])) + "," + str(int(i[3])) + "," + str(
            int(i[4])) + "," + str(int(i[5])) + \
                "," + str(int(i[6])) + "," + str(int(i[7])) + "," + str(int(i[8])) + "," + str(int(i[9])) + "," + str(
            int(i[10])) + "," + \
                str(int(i[11])) + "," + str(int(i[12])) + "," + str(int(i[13])) + "," + str(int(i[14])) + "," + str(
            int(i[15])) + "," + \
                str(int(i[16])) + "," + str(int(i[17])) + "," + str(int(i[18])) + "," + str(int(i[19])) + "," + str(
            int(i[20])) + "," + \
                str(int(i[21])) + "," + str(token_id) + "," + str(time_) + "," + "false" + "," + "30);"

        try:
            cursor.execute(query)
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
            websocket.send(str({'Error': str(exc)}))


async def main():
    ip = socket.gethostbyname(socket.gethostname())
    print("Websocket Server running on:\n" + ip + ":8080")
    async with websockets.serve(retrieve_data, ip, 8080):
        await asyncio.Future()  # run forever


connection = None
password = input("Your Database Password: ")
try:
    connection = mysql.connector.connect(host='localhost',
                                         database='binobo_db',
                                         user='root',
                                         password=password)
    while not connection.is_connected():
        pass

    print("Database-Connection status: " + str(connection.is_connected()))

    cursor = connection.cursor()
except Exception as e:
    print(e)

asyncio.run(main())
