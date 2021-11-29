
import json
from typing import Dict
#from db import dataBase
import datetime as dt




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

    def __init__(self, ident: str, name : str, delta : str, ):
        #DO NOT PUT ***ANY*** PRIVATE INFO HERE UNTIL WE OVERHAUL SENDING INFO TO CLIENTS

        self.name = name
        self.delta = delta
        self.ident = ident

        self.conn = set()

        self.guilds = set()
        
        self.status = {
            "text": None,
            "online": None
        }

        self.notifs = []

        self.creation = None
        self.perms = None
        self.friends = set()
        self.blocked = set()

        #Grab info from DB then populate info
    

    def notify(self, msg):
        self.notifs.append(msg)

    async def realSend(self, datum):
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

    def addGuild(self, guild):
        self.guilds.add(guild)
        #Update DB

    def removeGuild(self, guild):
        self.guilds.remove(guild)
        #Update DB
    



class guild:
    #Make guild with info from db?
    #Same w/t classes and msg and usr?
    """
    Guild class, defines guilds, analogus to discord servers
    
    """

    def __init__(self, ident:str, name:str, owner:usr, ):
        self.ident = ident
        self.name = name
        self.owner = owner #Add co-owners?
        self.systemChannel = None

        self.channels = []
        self.users = set()

        self.creation = None

        #Grab info from DB then populate info
    

    def addChannel(self, *args, **kwargs):
        chan = self.channel(*args, **kwargs, guild=self)
        self.channels.append(chan)
        #Update DB
        return chan
    
    def removeChannel(self, chan):
        self.channels.remove(chan)
        #Update DB
    

    class channel:
        """
        Channel class, defines channels in guilds
        """

        def __init__(self, ident: str, name:str, guild) -> None:
            self.ident = ident
            self.name = name
            self.messages = []
            self.guild = guild
            self.type = None

            #Grab info from DB then populate info

        def message_push(self, *args, **kwargs):

            mess = self.msg(*args, **kwargs, chan=self, datetime=dt.datetime.now())
            self.messages.append(mess)
            return mess

        def message_delete(self, msg):
            #Work on this- Lilly
            # Add this to msg class?
            self.messages.remove(msg)

        def message_edit(self):
            #Work on this- Lilly
            # Add this to msg class?
            pass

        def reply(self):
            #Work on this- Lilly
            pass

        class msg:
            """
            Message Container Class, Defines a message
            """
            def __init__(self, author: usr, message, ident: str, chan, datetime) -> None:
                self.content = message
                self.author = author #Pass whole User instence
                self.ident = ident
                self.chan = chan
                self.datetime = datetime

                #Grab info from DB then populate info
 



    
