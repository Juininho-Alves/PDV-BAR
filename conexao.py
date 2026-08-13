import sqlite3

def conection():
    conexao = sqlite3.connect('database.db')
    return conexao