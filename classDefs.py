

from typing import Dict


class conn_obj:

    class NoConnectionAttached(Exception):
        def __init__(self, *args: object) -> None:
            super().__init__(*args)

    def __init__(self, websocket, user, view : Dict) -> None:
        self.websocket = websocket
        self.user = user
        self.view = view # {"Guild" : !Guild Obj!, "Channel" : !Channel Obj!}
    
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

    :param websocket: Websocket obj, pass None if no connection attached
    :param ident: This is the identifying number for the class, give 0 if user is not in DB
    """

    def __init__(self, ident, name):

        self.name = name
        #self.ident_ = rand_id()
        self.ident = ident

#class msg:
#    """
#    Message Container Class, Defines a message
#    """
#    def __init__(self, author, message, ident) -> None:
#        self.content = message
#        self.author = author #Pass whole User instence
#        self.ident = ident
#        #self.channel


class channel:

    def __init__(self, ident, name) -> None:
        self.ident = ident
        self.name = name
        self.messages = []

    class msg:
        """
        Message Container Class, Defines a message
        """
        def __init__(self, author, message, ident, chan) -> None:
            self.content = message
            self.author = author #Pass whole User instence
            self.ident = ident
            self.chan = chan

            #self.channel

            
    def message_push(self, *args, **kwargs):
        mess = self.msg(*args, **kwargs, chan=self)
        self.messages.append(mess)
