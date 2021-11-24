import mysql.connector
import asyncio

class dataBase:

    def __init__(self) -> None:
        pass

    
    def select(self, query, values) -> list:
        db = mysql.connector.connect(user='python', password='', host='127.0.0.1', database='messages')
        cursor = db.cursor(dictionary=True, buffered=True)

        cursor.execute(query, values) # %s for item to be replaced in querry

        rows = cursor.fetchall()

        #db.commit()
        cursor.close()
        db.close()

        return rows


    def insert(self, query, values):
        db = mysql.connector.connect(user='python', password='', host='127.0.0.1', database='messages')
        cursor = db.cursor()

        cursor.execute(query, values) # %s for item to be replaced in querry

        db.commit()
        cursor.close()
        db.close()

    
