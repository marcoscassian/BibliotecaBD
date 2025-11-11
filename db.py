import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "port": 3307,
    "database": "db_trabalho3B",
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)
