

from typing import Dict
from db import dataBase
import datetime as dt





class Dill:

    def __init__(self) -> None:
        publics = {
            "usr": ["name", "ident", "perms", "delta"],
            "msg": []
        }
        

    




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
        """
        ?->
        public = {
            self.name = name
            self.ident = ident
            self.delta = delta
            self.perms = None
        }
        private = {
            self.authToken = None
            self.guilds = []
        }
        """
        self.name = name
        self.delta = delta
        self.ident = ident

        self.guilds = set()

        self.status = ""
        self.statusText = ""

        self.creation = None

        #self.authToken = None
        self.perms = None
    
    def dbGet(self):
        db = dataBase()
        rows = db.select("SELECT * FROM `mess_app`.`users` WHERE `ident` = %s;", (self.ident))
        if rows:
            return rows
        else:
            return False
    
    def addGuild(self, guild):
        self.guilds.add(guild)

    def removeGuild(self, guild):
        self.guilds.remove(guild)

 
class guild:

    def __init__(self, ident:str, name:str, owner:usr, ):
        self.ident = ident
        self.name = name
        self.owner = owner #Add co-owners?

        self.channels = set()

        self.creation = None
    

    class channel:

        def __init__(self, ident: str, name:str) -> None:
            self.ident = ident
            self.name = name
            self.messages = []
            self.type = None

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

                #self.channel

                
        def message_push(self, *args, **kwargs):

            mess = self.msg(*args, **kwargs, chan=self, datetime=dt.datetime.now())
            self.messages.append(mess)

        def message_delete(self, msg:msg):
            #Work on this- Lilly
            self.messages.remove(msg)

        def message_edit(self):
            #Work on this- Lilly
            pass

        def reply(self):
            pass