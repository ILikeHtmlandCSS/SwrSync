import mysql.connector

conn = [mysql.connector.connect()]


def createConnection(name, passwd):
    conn[0] = mysql.connector.connect(
        host="45.136.30.30",
        user=name,
        password=passwd,
        database="swr",
        buffered=True
    )
    return conn[0].cursor()


def getConnection():
    if conn[0].is_connected():
        return conn[0]
    else:
        return "There is no valid MySql connection!"


def getCursor():
    if conn[0].is_connected():
        return conn[0].cursor()
