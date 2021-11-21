import asyncio
import json
import logging
import websockets
import random as rand
import db
from classDefs import *
import jsonpickle


logging.basicConfig()

#STATE = {"value": 0}

#RELAY = set()
RELAY = []
USERS = set()
CONNS = set()

nullUser = usr(0, "Null")


DataConn = db.dataBase()


def rand_id():
    ident = []
    for spot in range(5): #was 12
        ident.append(str(rand.randint(1,9)))
    return int("".join(ident))



# Begin Active Funcs

def state_event():
    sub = RELAY[-1]

    temp = {
                "messobj" : {
                    "message" : sub.content,
                    "message_id" : sub.ident,
                    "auth_id" : sub.author.ident,
                    "auth_name" : sub.author.name
                }
    }

    return json.dumps({"type": "mess", "data" : temp})

def whole_event():
    temp = []

    for sub in RELAY:
        temp.append(
            {
                "messobj" : {
                    "message" : sub.content,
                    "message_id" : sub.ident,
                    "auth_id" : sub.author.ident,
                    "auth_name" : sub.author.name
                }
            }
        )
    
    return json.dumps({"type": "mess_all", "data" : temp})
    #return json.dumps({"type": "state", **STATE})

def users_event():
    #, "users": list(CONNS)
    if USERS:
        print(jsonpickle.encode(list(USERS)[0]))
    return json.dumps({"type": "users", "uCount": len(USERS), "cCount": len(CONNS)})

async def update(datum):
    if CONNS:
        for conn in CONNS:
            await conn.send(datum)

async def notify_state():
    if CONNS:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        await update(message)

async def notify_users():
    if CONNS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await update(message)

async def register(conn):
    CONNS.add(conn)
    await notify_users()

async def unregister(conn):
    CONNS.remove(conn)
    await notify_users()




def user_db_handle(user):
    rows = DataConn.select("SELECT * FROM messages.users WHERE ident = '%s';", (user.ident))
    print(rows)
    if len(rows) == 0:
        print(user)

async def user_login(conn, name, pw):
    rows = DataConn.select("SELECT * FROM messages.users WHERE name = %s AND passwd = %s;", (name, pw))
    print(rows)
    if rows:
        user = usr(rows[0]["ident"], rows[0]["name"])
        conn.user = user
        USERS.add(user)
        await notify_users()
        return user



def user_db_update(user, column, value):
    rows = DataConn.select("UPDATE messages.users SET name = %s WHERE ident = '%s';", (value, user.ident))


async def main(websocket, path):
    # register(websocket) sends user_event() to websocket
    #user = usr(0)
    #await register(user)

    conn = conn_obj(websocket, nullUser)
    await register(conn)

    try:
        await websocket.send(whole_event())
        async for message in websocket:
            data = json.loads(message)


            if data["action"] == "connect":
                pass
            
            elif data["action"] == "user":
                if data["subact"] == "login":
                    await user_login(conn, data["name"], data["pass"])

                elif data["subact"] == "update":
                    if conn.user.name == "Null":
                        continue

                    if data["type"] == "name":
                        conn.user.name = data["data"]
                        user_db_update(conn.user, "name", data["data"])
                        #user.name(data["data"])
            
            elif data["action"] == "mess":
                message = msg(conn.user, data["message"], rand_id())
                #RELAY.add(message)
                RELAY.append(message)
                await notify_state()
            else:
                #write error codes
                await websocket.send(json.dumps({"type": "error", "code": "001", "text": "action not defined"}))





    finally:
        await unregister(conn)


start_server = websockets.serve(main, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()