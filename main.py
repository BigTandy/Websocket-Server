#Lilly PLP
#Nov 23 2021


import asyncio
import json
import logging
import websockets
import random as rand
from http import HTTPStatus as httpCode
import jsonpickle
import ssl
import pathlib
import html
import string
import hashlib
import os

# Me libs
import db
from classDefs import *

# Core of this code is from the websockets docs
# https://websockets.readthedocs.io/en/stable/


RELAY = []

CHANNELS = []
USERS = set()
CONNS = set()



#setup defaults
mainChannel = channel(0, "main")
nullUser = usr(0, "Null", "0000")


CHANNELS.append(mainChannel)


DataConn = db.dataBase()
userDC = db.userT()



def rand_id(count=5):
    ident = []
    for spot in range(count): #was 12
        ident.append(str(rand.randint(1,9)))
    return str("".join(ident))


def rand_chars(howmany : int):
    charsStr = string.ascii_letters
    chars = []
    for c in charsStr:
        chars.append(c)

    temp = []
    for num in range(howmany):
        temp.append(chars[rand.randint(0,len(chars) - 1)])
    return temp


def tokenGen():
    temp = []
    for i in range(50):
        temp.append(rand.choice(string.ascii_letters + string.digits))
    return "".join(temp)


# https://nitratine.net/blog/post/how-to-hash-passwords-in-python/
def passHash(password, salt=None):
    if salt is None:
        salt = os.urandom(32)

    hashed = hashlib.pbkdf2_hmac("sha256", password.encode('utf-8'), salt, 100000)
    print(len(hashed))
    return (hashed, salt)


def passVer(password, salt, oldhash):
    newHash = passHash(password, salt)[0]
    if newHash == oldhash:
        return True
    else:
        return False


for x in range(10):
    CHANNELS.append(channel(rand_id(), str(x)))




# Begin Active Funcs

def state_event():
    sub = RELAY[-1]
    
    temp = {
                "messobj" : {
                    "message" : sub.content,
                    "message_id" : sub.ident,
                    "auth_id" : sub.author.ident,
                    "auth_name" : sub.author.name,
                    "channel" : json.loads(jsonpickle.encode(sub.chan, unpicklable=False))
                }
    }

    return json.dumps({"type": "mess", "data" : json.loads(jsonpickle.encode(sub, unpicklable=False)) })
    #return json.dumps({"type": "mess", "data" : temp })


def whole_event():
    temp = []

    for sub in RELAY:
        temp.append(
            {
                "messobj" : {
                    "message" : sub.content,
                    "message_id" : sub.ident,
                    "auth_id" : sub.author.ident,
                    "auth_name" : sub.author.name,
                    "channel" : json.loads(jsonpickle.encode(sub.chan, unpicklable=False))
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


def channel_event():
    
    #jsonpickle.encode(CHANNELS, unpicklable=False)
    return json.dumps({"type": "chan_burst", "data": json.loads(jsonpickle.encode(CHANNELS, unpicklable=False)) })




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


async def user_login(conn, name, delta, pw):
    #rows = DataConn.select("SELECT * FROM mess_app.users WHERE name = %s;", (name))
    rows = userDC.selectNameDelta(name, delta)
    print(rows)
    if rows:
        rows = rows[0]
        if passVer(pw, rows["salt"], rows["passwd"]):
            while True:
                newAuth = tokenGen()
                CheckRows = DataConn.select("SELECT * FROM `mess_app`.`users` WHERE token = '%s';", (newAuth))
                if CheckRows:
                    continue
                else:
                    break
            #print(rows)
            assert rows is dict
            user = usr(rows["ident"], rows["name"])
            user.authToken = newAuth
            await conn.send(json.dumps({"type": "login", "code": httpCode.OK, "token": newAuth}))
            conn.user = user
            USERS.add(user)
            await notify_users()
            return user
        else:
            return False
    else:
        return False


async def user_reg(conn, name, pw):
    #make ranadom delta, 4 chars
    #Salt / Hash
    #

    allRows = userDC.selectAll()

    delta = rand_id(4)

    while True:
        ident = rand_id()
        rows = DataConn.select("SELECT * FROM `users` WHERE `ident` = '%s';", (ident))
        if rows:
            continue
        else:
            break
    
    hashed, salt = passHash(pw)

    userDC.insert(name, delta, ident, hashed, salt)
    await conn.send(json.dumps({"type": "signup", "code": httpCode.OK, "delta": delta, "username": name}))
    return delta
    #await user_login(conn, name, delta, pw)



async def tokenLogin(conn, token):
    pass


def user_db_update(user, column, value):
    #rows = DataConn.update("UPDATE `users` SET name = %s WHERE ident = '%s';", (value, user.ident))
    pass


async def errorSend(conn, errCode):
    await conn.send((json.dumps({"type": "error", "code": errCode})))



async def main(websocket, path):
    # register(websocket) sends user_event() to websocket
    #user = usr(0)
    #await register(user)

    conn = conn_obj(websocket, nullUser, {"channel": mainChannel})
    await register(conn)
    

    try:
        #await websocket.send(whole_event())
        await websocket.send(channel_event())
        async for message in websocket:
            data = json.loads(message)

            temp_data = []
            for arg in data.values():
                temp_data.append(html.escape(arg))
            data = dict(zip(data.keys(), temp_data))


            if data["action"] == "connect":
                pass
            
            elif data["action"] == "user":
                if data["subact"] == "login":
                    await user_login(conn, data["name"], data["delta"], data["pass"])

                elif data["subact"] == "signup":
                    await user_reg(conn, data["name"], data["pass"])
                    


                elif data["subact"] == "update":
                    if conn.user.name == "Null":
                        continue

                    if data["type"] == "name":
                        conn.user.name = data["data"]
                        user_db_update(conn.user, "name", data["data"])
                        #user.name(data["data"])
            

            elif data["action"] == "cViewChange":
                try:
                    temp_c_id_change = int(data["channel"])

                    for Tchan in CHANNELS:
                        if Tchan.ident == temp_c_id_change:
                            conn.view = {"channel": Tchan}
                            break
                    else:
                        await conn.send(json.dumps({"type": "error", "code": httpCode.NOT_ACCEPTABLE}))


                except ValueError as e:
                    await conn.send(json.dumps({"type": "error", "code": httpCode.BAD_REQUEST}))
            
            elif data["action"] == "mess":

                if len(html.escape(data["message"])) > 60000:
                    await errorSend(conn, httpCode.NOT_ACCEPTABLE)

                conn.view["channel"].message_push(conn.user, html.escape(data["message"]), rand_id())
                RELAY.append(conn.view["channel"].messages[-1])


                await notify_state()
            else:
                await errorSend(conn, httpCode.BAD_REQUEST)
                #write error codes

                #await websocket.send(json.dumps({"type": "error", "code": "001", "text": "action not defined"}))





    finally:
        await unregister(conn)




ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
ssl_context.load_cert_chain(localhost_pem)



start_server = websockets.serve(main, "", 6789, ssl=ssl_context)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()