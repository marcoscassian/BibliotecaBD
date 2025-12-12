import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "usbw",
    "port": 3307,
    "database": "db_trabalho3b",
}

DB_CONFIG_NO_DB = DB_CONFIG.copy()
DB_CONFIG_NO_DB.pop("database") 

def criar_banco():
    conn = mysql.connector.connect(**DB_CONFIG_NO_DB)
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS db_trabalho3b")
    cursor.close()
    conn.close()
    print("✓ Banco criado com sucesso!")

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)
