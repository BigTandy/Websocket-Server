#Lilly PLP
#Nov 23 2021


import asyncio
import json
import logging
import websockets
import random as rand
from http import HTTPStatus as httpCode
#import jsonpickle 
import ssl
import pathlib
import html
import string
import hashlib
import os
import datetime
import mysql.connector.errors as mysqlErrors
# Me libs
import db
from classDefs import *


import jsonpickle

#Database's connections
DataConn = db.dataBase("mess_app")
userDC = db.userT()
dbS = db.dbStruct()



# Core of this code is from the websockets docs
# https://websockets.readthedocs.io/en/stable/
# More specificly here
# https://websockets.readthedocs.io/en/stable/intro/quickstart.html


#RELAY = []

GUILDS = []
USERS = set()
CONNS = set()
#TODO
#   Make sure memory overhead isnt too much
ALLUSERS = set()





#Grab all users and make their respective obj's
userstemp = DataConn.select("SELECT * FROM `users`", ())
for oosr in userstemp:
    print(f"{oosr['name']}#{oosr['delta']} ~~ {oosr['ident']}")
    if oosr["guilds"] != None:
        guilds = str(oosr["guilds"]).split(":")
    else:
        guilds = None

    ALLUSERS.add(usr(oosr["ident"], oosr["name"], oosr["delta"], guilds=guilds))





#Grab all guilds
guildDump = DataConn.select("SELECT * FROM `guilds`", ())

for guildd in guildDump:

    #Find the owner of the guild and store it in var to pass to guild constructer
    owner = None
    for oosr in ALLUSERS:
        if oosr.ident == guildd['owner_ident']:
            owner = oosr
            break
    else:
        raise Exception(f"Guild Without Owner, {guildd}")


    
    guildUsers = []
    #If there is a singular '*' in users column in DB that means add all users to guild
    if guildd['users'] == "*":
        guildUsers = ALLUSERS

    #iterate over ALLUSERS and pick out the ones in this guild and add them to the guild
    guildusersIdents = guildd['users'].split(":")
    for oosr in ALLUSERS:
        if oosr.ident in guildusersIdents:
            guildUsers.append(oosr)

    GUILDS.append(guild(guildd['ident'], guildd['name'], owner, users=None, aUsers=guildUsers))

    try:
        channels = dbS.mess_guilds.select(f"SELECT * FROM `GUILD_{guildd['ident']}`", ())
    except mysqlErrors.ProgrammingError:
        print(f"Guild {guildd} channels table not found")

    print(channels)













#setup defaults
sudoUsr = usr("-1", "su", "0000", [])
nullUser = usr("0", "Null", "0000",  [])

mainGuild = guild("0", "main", sudoUsr)
mainChannel = channel("0", "main", mainGuild)
mainGuild.addChannel(mainChannel)
mainGuild.systemChannel = mainChannel


sChannel = channel("1", "2ed", mainGuild)
mainGuild.addChannel(sChannel)


#secGuild = guild("1", "eyes", sudoUsr)
#secChannel = channel("3", "System", secGuild)
#secGuild.addChannel(secChannel)
#secGuild.systemChannel = secChannel


#mainChannel = channel("0", "main")


GUILDS.append(mainGuild)
#GUILDS.append(secGuild)




#Following line is for testing, remove after needed
#dbS.guildConstructor("0")
#TODO TODO^^^


#######################

#TODO
#   MAKE SURE THAT EVERY NEW GUILD / CHANNEL HAS ABSOULUT UNIQUE ID
#   CHECK AGAINST `IDENTS` TO MAKE SURE ITS UNIQUE

def rand_id(count=12):
    ident = []
    for spot in range(count): #was 12
        #ident.append(str(rand.randint(1,9)))
        ident.append(rand.choice(list(string.hexdigits)))
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




#Conn managment

async def register(conn):
    CONNS.add(conn)
    await notify_users()

async def unregister(conn):
    CONNS.remove(conn)
    await notify_users()



async def update(datum):
    if CONNS:
        for conn in CONNS:
            await conn.send(datum)


#async def notify_state():
#    if CONNS:  # asyncio.wait doesn't accept an empty list
#        message = state_event()
#        await update(message)

async def notify_users():
    if CONNS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await update(message)





def users_event():
    #, "users": list(CONNS)

    #--!! Replace JSON PICKLE !!--#
    #TODO,
    # Only brodcast a new user conn to the guilds and friends of user, anyone else can poll the API to check if user is online
    temps = []
    for user in USERS:
        temps.append({
            "user": {
                "name": user.name,
                "delta": user.delta,
                "status": user.status,
                "ident": user.ident,

            }
        })

    return json.dumps({"type": "users", "uCount": len(USERS), "cCount": len(CONNS), "reged": temps})






# """Error handler"""

async def errorSend(conn, errCode, info=""):
    await conn.send((json.dumps({"type": "error", "code": errCode, "info": info})))




#######################




# https://nitratine.net/blog/post/how-to-hash-passwords-in-python/
def passHash(password, salt=None):
    if salt is None:
        salt = os.urandom(32)

    hashed = hashlib.pbkdf2_hmac("sha256", password.encode('utf-8'), salt, 100000)
    #print(len(hashed))
    return (hashed, salt)


def passVer(password, salt, oldhash):
    newHash = passHash(password, salt)[0]
    if newHash == oldhash:
        return True
    else:
        return False


def tokenGen():
    temp = []
    for i in range(50):
        temp.append(rand.choice(string.ascii_letters + string.digits))
    return "".join(temp)


def tokenDBgen(name, delta):
    while True:
        newAuth = tokenGen()
        CheckRows = DataConn.select("SELECT * FROM `mess_app`.`users` WHERE token = %s AND NOT name = %s AND NOT delta = %s;", (newAuth, name, delta))
        if CheckRows:
            continue
        else:
            return newAuth


async def user_login(conn, name, delta, pw):
    #rows = DataConn.select("SELECT * FROM mess_app.users WHERE name = %s;", (name))
    rows = userDC.selectNameDelta(name, delta)
    print(rows)
    if rows:
        rows = rows[0]
        if passVer(pw, rows["salt"], rows["passwd"]):

            #newAuth = tokenDBgen(name, delta)

            #print(rows)
            #user = usr(rows["ident"], rows["name"], rows["delta"])
            #DO NOT UNCOMMENT BELOW LINE, THAT LEAKS THE AUTH TOKEN TO EVERYONE
            #user.authToken = newAuth

            #TOKEN UPDATE TODO
            #userDC.updateToken(newAuth, rows["ident"])

            await conn.send(json.dumps({"type": "login", "code": httpCode.OK, "token": rows["token"], "name": rows["name"], "delta": rows["delta"]}))
            return True
            #conn.user = user
            #USERS.add(user)
            #await notify_users()
            #return user
        else:
            #await conn.send(json.dumps({"type": "login", "code": httpCode.UNAUTHORIZED}))
            return False
    else:
        #await conn.send(json.dumps({"type": "login", "code": httpCode.UNAUTHORIZED}))
        return False


async def user_reg(conn, name, pw):
    #make ranadom delta, 4 chars
    #Salt / Hash
    #

    #syms = string.symbols

    if name.lower() == "null":
        await conn.send(json.dumps({"type": "signup", "code": httpCode.NOT_ACCEPTABLE}))
        return
    
    if name.lower() == "su":
        await conn.send(json.dumps({"type": "signup", "code": httpCode.NOT_ACCEPTABLE}))
        return

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


    
    newAuth = tokenDBgen(name, delta)
    userDC.updateToken(newAuth, ident)


    await conn.send(json.dumps({"type": "signup", "code": httpCode.OK, "ident": ident, "delta": delta, "username": name, "token": newAuth}))
    return delta
    #await user_login(conn, name, delta, pw)



async def tokenLogin(conn, name, delta, token):

    
    rows = userDC.selectNameDelta(name, delta)
    if rows:
        rows = rows[0]
        if rows["token"] == token:
                #TODO
                #   Pull from ALLUSERS
                #user = usr(rows["ident"], rows["name"], rows["delta"], guilds=str(rows["guilds"]).split(":"))

                #Find user in ALLUSERS and use that
                for ALLUSER_user in ALLUSERS:
                    if rows["ident"] == ALLUSER_user.ident:
                        user = ALLUSER_user
                        break
                    else:
                        continue



                #? #Get Guilds and other user data and dump here
                await conn.send(json.dumps(
                    {
                    "type": "login",
                    "code": httpCode.OK,
                    "nameIdent": {
                        "name": rows["name"],
                        "delta": rows["delta"],
                        "ident": rows["ident"],
                    },
                    "guilds": str(rows["guilds"]).split(":")

                    }))

                conn.user = user
                user.conn.add(conn)

                #TODO
                # Iterate over all of users' guilds and add them
                mainGuild.addUser(user)

                #OOGA
                #secGuild.addUser(user)

                #Grab all guild idents from DB and actually add the user to them, TODO, Wtf, Like add user to online users in guild now seems odd, ig TODO add offline users to guild, then online users when they come online then remove them when offline
                for guild in user.guilds:
                    if type(guild) == str:
                        for listGuild in GUILDS:
                            if listGuild.ident == guild:
                                listGuild.addUser(user)
                                user.guilds.remove(guild)
                                break
                        else:
                            raise Exception(f"Guild: <ident({guild})> Not found, tokenLogin near `for guild`")
                    


                print(user.guilds)

                #Package all user data

                #Honestly have little clue why this is here, does it send the user their guilds?, incomphrensible
                meGuilds = []
                for guild in user.guilds:
                    print(guild)

                    oosers = []
                    for ooser in guild.users:
                        #oosers = []
                        oosers.append({
                                    "ident": ooser.ident,
                                    "namedelta": {"name": ooser.name, "delta": ooser.delta}
                                })

                    channs = []
                    for chan in guild.channels:
                        messages = []
                        for mess in chan.messages:
                            messages.append(mess.packer())
                        channs.append({
                            "ident": chan.ident,
                            "name": chan.name,
                            "messages": messages,
                            "guild_ident": chan.guild.ident,
                        })
                    meGuilds.append({
                        "ident": guild.ident,
                        "name": guild.name,
                        "owner": {"namedelta": {"name": guild.owner.name, "delta": guild.owner.delta}, "ident": guild.owner.ident},
                        "users": oosers,
                        "channels": channs,
                        "systemChannel": guild.systemChannel.ident
                    })

                #send the data to user
                await conn.send(json.dumps({
                    "type": "userburst",
                    "data": {
                        "ident": user.ident,
                        "namedelta": {"name": user.name, "delta": user.delta},
                        "status": user.status,
                        "guilds": meGuilds
                    }
                }))

                USERS.add(user)
                await notify_users()
                return user
        else:
            print(rows, " token ", token, " name ", name, " delta ", delta)
            return False
            #await conn.send(json.dumps({"type": "login", "code": httpCode.UNAUTHORIZED}))
            
    else:
        return False
        #await conn.send(json.dumps({"type": "login", "code": httpCode.UNAUTHORIZED, "namedelta": name + delta, "token": token}))





def connect(conn, data):
    pass


async def user(conn, data):

    if data["subact"] == "login":
        ret = await user_login(conn, data["name"], data["delta"], data["pass"])
        if ret == False:
            conn.send(json.dumps({"type": "login", "code": httpCode.UNAUTHORIZED}))
            return

    elif data["subact"] == "signup":
        await user_reg(conn, data["name"], data["pass"])
        
    elif data["subact"] == "tokenLogin":
        ret = await tokenLogin(conn, data["name"], data["delta"], data["token"])
        if ret == False:
            await conn.send(json.dumps({"type": "login", "code": httpCode.UNAUTHORIZED}))
            return

    #elif data["subact"] == "update":
    #    if conn.user.ident == "0":
    #        return
    #
    #    if data["type"] == "name":
    #        pass
    #        #conn.user.name = data["data"]
    #        #user_db_update(conn.user, "name", data["data"])
    #        #user.name(data["data"])


async def ViewChange(conn, data):
    

    guildTo = data["guild"]
    channTo = data["channel"]


    found = False
    for userGuild in conn.user.guilds:
        #print(f"UG: {userGuild.ident}")
        if str(userGuild.ident) == str(guildTo):
            conn.view["guild"] = userGuild
            
            for chann in userGuild.channels:
                print(f"UC: {chann.ident}")
                if str(chann.ident) == str(channTo):
                    conn.view["channel"] = chann
                    #print(">-???-<")
                    found = True
                    break
            else:
                continue
        if found:
            break
    else:
        await conn.send(json.dumps({"type": "error", "code": httpCode.NOT_FOUND}))
        #print(f"G: {guildTo} C: {channTo}\nGuilds: {conn.user.guilds}")




async def messHandle(conn, data):

    print("MessHandle Called")
    

    if len(data["message"]) > 6000:
        await errorSend(conn, httpCode.NOT_ACCEPTABLE, "MessToLong")
        print("Mess to Long", jsonpickle.encode(data))
        return

    mess = conn.view["channel"].message_push(conn.user, data["message"], rand_id())
    await conn.view["guild"].mess_up(mess)
    #print(f"V:\nG: ", conn.view["guild"].name, "\nC: ", conn.view["channel"].name)


    

    #RELAY.append(conn.view["channel"].messages[-1])
    #print(jsonpickle.encode(mess, indent=4))
    #print(jsonpickle.encode(conn.view["guild"], indent=4))
    #print(jsonpickle.encode(conn.user, indent=4))



    #await notify_state()


async def errorSend(conn, errCode, info=""):
    await conn.send(json.dumps({"type": "error", "code": errCode, "info": info}))

#TODO
async def objRequest(conn, data):
    pass

async def badRequest(conn, data):
    await errorSend(conn, httpCode.BAD_REQUEST)





apiRefine = {
    "user": user,
    "ViewChange": ViewChange,
    "mess": messHandle,
}

async def main(websocket, path):
    # register(websocket) sends user_event() to websocket
    #user = usr(0)
    #await register(user)

    conn = conn_obj(websocket, nullUser, {"guild": mainGuild, "channel": mainChannel})
    await register(conn)
    

    try:
        #await websocket.send(whole_event())
        #await websocket.send(channel_event())
        #await websocket.send(users_event())

        #Request User/Connection Credentials
        await conn.send(json.dumps({"type": "credentialReq"}))


        async for message in websocket:
            data = json.loads(message)

            temp_data = []
            for arg in data.values():
                if type(arg) == str:
                    temp_data.append(html.escape(arg))
                else:
                    temp_data.append(arg)
            data = dict(zip(data.keys(), temp_data))

            
            #Execute the call from the client
            if data["action"] != "user":
                if conn.user.ident == "0":
                    await conn.send(json.dumps({"type": "credentialReq"}))
                    continue


            await apiRefine[data["action"]](conn, data)

            #try:
            #    await apiRefine[data["action"]](conn, data)
            #except KeyError as e:
            #    await conn.send(json.dumps({"type": "error", "code": 400, "sub": "API", "info": f"Bad API Request: {e}"}))
            #except Exception as e:
            #    print(e, data, data["action"])
            #    await errorSend(conn, httpCode.INTERNAL_SERVER_ERROR)
            #    #await conn.send(errorSend(conn, httpCode.INTERNAL_SERVER_ERROR))        



    finally:
        if conn.user.name != "Null":
            print("USER BEING REMOVED: ", conn.user.name, "#", conn.user.delta)
            conn.user.conn.remove(conn)
            USERS.remove(conn.user)
            
        await unregister(conn)
        await notify_users()




ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
ssl_context.load_cert_chain(localhost_pem)



start_server = websockets.serve(main, "", 6789, ssl=ssl_context)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()