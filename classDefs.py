

class conn_obj:

    class NoConnectionAttached(Exception):
        def __init__(self, *args: object) -> None:
            super().__init__(*args)

    def __init__(self, websocket, user) -> None:
        self.websocket = websocket
        self.user = user
    
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

    def __setitem__(self, val, dat):
        try:
            setattr(self, val, dat)
            return True
        except Exception as e:
            return False

    def __getitem__(self, val):
        try:
            temp = getattr(self, val)
            return temp
        except AttributeError as e:
            return None
    

class msg:
    """
    Message Container Class, Defines a message
    """
    def __init__(self, author, message, ident) -> None:
        self.content = message
        self.author = author #Pass whole User instence
        self.ident = ident
    
    def __setitem__(self, val, dat):
        try:
            setattr(self, val, dat)
            return True
        except Exception as e:
            return False

    def __getitem__(self, val):
        try:
            temp = getattr(self, val)
            return temp
        except AttributeError as e:
            return None



class channel:

    def __init__(self, ident) -> None:
        self.ident = ident
        self.messages = set()

    
    def message_push(self, mess : msg):
        self.messages.add(mess)

