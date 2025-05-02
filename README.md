# Crie um arquivo "db.py" no seguinte formato:

```
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="168.75.73.251",          # ex: "meubanco.mysql.uhserver.com"
        user="admin_sge",       # ex: "admin"
        password="AdminSGE09042@12",     # ex: "minhasenha123"
        database="gestao_escolar" # nome do seu banco criado
    )
```
