

from typing import Dict

import datetime as dt
import json
from enum import Enum as enum, unique
import re
import copy

#from inspect import stack


class conn_obj:

    class NoConnectionAttached(Exception):
        def __init__(self, *args: object) -> None:
            super().__init__(*args)

    def __init__(self, websocket, user, view : Dict) -> None:
        self.websocket = websocket
        self.user = user
        self.view = view # {"Guild" : !Guild Obj!, "Channel" : !Channel Obj!}
        self.requestsPerMinute = 0
    
    async def send(self, datum):
        """
        Sends data to user
        """
        if self.websocket is None:
            raise self.NoConnectionAttached
        await self.websocket.send(datum)


class perm:
    pass



class usr:
    """
    Usr class holds info about users who are actively connected
    """

    def __init__(self, ident: str, name: str, delta: str, guilds: list):
        #DO NOT PUT ***ANY*** PRIVATE INFO HERE UNTIL WE OVERHAUL SENDING INFO TO CLIENTS
        #Grab info from DB then populate info

        self.name = name
        self.delta = delta
        self.ident = ident
        self.status = {
            "text": None,
            "online": None
        }

        self.conn = set()

        self.guilds = guilds
        
        self.notifs = []

        self.creation = None
        self.perms = None
        self.friends = set()
        self.blocked = set()

        


    def addGuild(self, guild):

        #https://pythonin1minute.com/who-called-me-how-to-get-the-caller-of-a-function-in-python/
        #print(f"stack: {stack()[1].function}")
        self.guilds.append(guild)



    def removeGuild(self, guild):
        self.guilds.remove(guild)
        #guild.removeUser(self)
    
    def notify(self, msg):
        self.notifs.append(msg)

    async def send(self, datum):
        if not self.conn:
            raise conn_obj.NoConnectionAttached
        else:
            for con in self.conn:
                #try:
                await con.send(datum)


    def addConn(self, conn):
        self.conn.add(conn)

    def removeConn(self, conn):
        self.conn.remove(conn)

 

class guild:
    
    def __init__(self, ident, name, owner: usr, systemChannel=None, users=None, aUsers=None) -> None:
        self.ident = ident
        self.name = name
        self.owner = owner #Owners?


        #-Unessicary?
        if users == None:
            self.users = []
        else:
            self.users = copy.deepcopy(users)
        

        if aUsers == None:
            pass
        else:
            for user in aUsers:
                self.addUser(user)
  

        self.systemChannel = systemChannel

        self.roles = []
        [
            {
                "Name": "",
                "Users": "",
            }
        ]

        self.channels = []

    def addChannel(self, chan):
        self.channels.append(chan)
    
    def removeChannel(self, chan):
        self.channels.remove(chan)

    def addUser(self, user):
        #print(f"User being added: ", user.name, " Guild: ", self.name)
        self.users.append(user)
        user.addGuild(self)
        #print("STACk2: ", stack()[1].function)

    def removeUser(self, user):
        self.users.remove(user)
        user.removeGuild(self)
    

    async def mess_up(self, mess):

        #print(jsonpickle.encode(self.users, unpicklable=False, max_depth=4, indent=4))
        
        for user in self.users:
            try:
                await user.send(json.dumps(
                    {
                        "type": "mess",
                        "data": mess.packer()
                    }
                    ))
                
            except conn_obj.NoConnectionAttached as e:
                print("user: ", user.name, " ", e)



class channel:

    def __init__(self, ident, name, guild: guild, messages=None) -> None:
            self.ident = ident
            self.name = name
            #TODO
            if messages is None:
                self.messages = []

            self.guild = guild
    

    def message_push(self, *args, **kwargs):
        mess = msg(*args, **kwargs, chan=self, datetime=dt.datetime.now())
        self.messages.append(mess)
        return mess

    def message_delete(self, msg):
        #Work on this- Lilly
        self.messages.remove(msg)

    def message_edit(self):
        #Work on this- Lilly
        pass

    def reply(self):
        pass



@unique
class msgType(enum):
    NORM = 0
    REPLY = 1
    FILE = 2


class msg:
    """
    New Message Class
    """
    def __init__(self, author: usr, content, ident: str, chan: channel, datetime: dt.datetime, type=msgType.NORM, editedBool=False, file=None) -> None:
        self.author = author
        self.ident = ident
        self.type = type
        self.chan = chan
        self.datetime = datetime
        self.content = content
        self.editedBool = editedBool
        self.file=file #Should be bytes


        self.pingable = ["everyone"]
        self.slashs = ["queer"]



    def packer(self):

        

        pattern = re.compile(r'@[a-z]+#[1-9]{4}', re.IGNORECASE)
        mentionsTemp = pattern.findall(self.content)
        mentions = []
        for ment in mentionsTemp:
            mentions.append(str(ment)[1:])
        
        arrCont = self.content.split()
        for case in self.pingable:
            if f"@{case}" in arrCont:
                mentions.append(str(case))

        packed = {
            "ident": self.ident,
            "type": self.type.name,

            "content": self.content,

            "author": {                            
                "ident": self.author.ident,
                "name": self.author.name, 
                "delta": self.author.delta,
            },

            "datetime": str(self.datetime),


            "edited": self.editedBool,
            "mentions": mentions,

            "fileAttachment": self.file,


            "guild": {
                "ident": self.chan.guild.ident,
                "name": self.chan.guild.name,
            },
            "channel": {
                "ident": self.chan.ident,
                "name": self.chan.name,
            },       
        }

        return packed