import sqlite3


def init_db():
    with open('schemas.sql', 'r') as arquivo:
        conn = sqlite3.connect('database.db')
        conn.executescript(arquivo.read())
        conn.close()


init_db()
