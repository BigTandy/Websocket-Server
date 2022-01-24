from asyncio.tasks import _register_task
import copy
import mysql.connector
import asyncio
import json
import classDefs as cd



with open("/home/pi/!Sec/dbAuth.json") as file:
    data = file.read().replace('\n', '')

auths = json.loads(data)



class dataBase:

    def __init__(self, dbSelex) -> None:
        self.dbSelex = dbSelex

    
    def select(self, query, values) -> list:
        db = mysql.connector.connect(user=auths["user"], password=auths["password"], host=auths["host"], database=self.dbSelex)
        cursor = db.cursor(dictionary=True, buffered=True)

        cursor.execute(query, values) # %s for item to be replaced in querry

        rows = cursor.fetchall()

        #db.commit()
        cursor.close()
        db.close()

        return rows


    def execute(self, query, values):
        db = mysql.connector.connect(user=auths["user"], password=auths["password"], host=auths["host"], database=auths["database"])
        cursor = db.cursor()

        cursor.execute(query, values) # %s for item to be replaced in querry

        db.commit()
        cursor.close()
        db.close()




class dbStruct:

    def __init__(self) -> None:
        self.mess_app = dataBase("mess_app")
        self.mess_guilds = dataBase("mess_guilds") 
        self.mess_chans = dataBase("mess_channs")
    


        

        







class userT:

    def __init__(self) -> None:
        self.db = dataBase("mess_app")

    def insert(self, name, delta, ident, passhash, salt):
        self.db.execute("INSERT INTO `users`(`id`, `name`, `delta`, `ident`, `passwd`, `salt`, `token`) VALUES (NULL, %s, %s, %s, %s, %s, NULL);", (name, delta, ident, passhash, salt))
    
    def selectNameDelta(self, name, delta):
        row = self.db.select("SELECT * FROM `users` WHERE `name` = %s AND `delta` = %s;", (name, delta))
        if not row:
            return False
        else:
            return row
    
    def selectIdent(self, ident):
        row = self.db.select("SELECT * FROM `users` WHERE `ident` = '%s'", ident)
        if not row:
            return False
        else:
            return row
    
    def selectAll(self):
        return self.db.select("SELECT * FROM `users`;", ())
    
    def updateToken(self, token, ident):
        # https://stackoverflow.com/questions/9394291/python-and-mysqldb-substitution-of-table-resulting-in-syntax-error/9394450#9394450
        self.db.execute("UPDATE `users` SET `token`=%s WHERE `ident` = %s", (token, ident))
        rows = self.selectIdent(ident)
        if rows:
            rows = rows[0]
            assert rows["token"] == token
    
