import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="IP_SERVER",
        user="USER",
        password="PASSWORD",
        database="DATABASE"
    )
