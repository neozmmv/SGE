# Crie um arquivo "db.py" e preencha no seguinte formato:

```
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="IP_SERVIDOR",
        user="USUARIO",
        password="SENHA",
        database="DATABASE"
    )
```
