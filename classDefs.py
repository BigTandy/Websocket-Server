

from typing import Dict
from db import dataBase


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


class usr:
    """
    Usr class holds info about users who are actively connected
    """

    def __init__(self, ident: str, name : str, delta : str):
        #DO NOT PUT ***ANY*** PRIVATE INFO HERE UNTIL WE OVERHAUL SENDING INFO TO CLIENTS
        """
        ?->
        public = {
            self.name = name
            self.ident = ident
            self.delta = delta
            #self.authToken = None
            self.perms = None
        }
        private = {
            #self.authToken = None
        }
        """
        self.name = name
        self.ident = ident
        self.delta = delta
        #self.authToken = None
        self.perms = None
    
    def dbGet(self):
        db = dataBase()
        rows = db.select("SELECT * FROM mess_app.users WHERE ident = '%s';", (self.ident))
        if rows:
            return rows
        else:
            return False
            


class channel:

    def __init__(self, ident: str, name) -> None:
        self.ident = ident
        self.name = name
        self.messages = []

    class msg:
        """
        Message Container Class, Defines a message
        """
        def __init__(self, author, message, ident: str, chan) -> None:
            self.content = message
            self.author = author #Pass whole User instence
            self.ident = ident
            self.chan = chan

            #self.channel

            
    def message_push(self, *args, **kwargs):
        mess = self.msg(*args, **kwargs, chan=self)
        self.messages.append(mess)
