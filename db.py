import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="",          # ex: "meubanco.mysql.uhserver.com"
        user="",       # ex: "admin"
        password="",     # ex: "minhasenha123"
        database="" # nome do seu banco criado
    )
