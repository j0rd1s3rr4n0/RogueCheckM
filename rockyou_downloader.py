import sqlite3
import os
from concurrent.futures import ThreadPoolExecutor

# Descargar rockyou.txt si no existe
if not os.path.exists('dicts/rockyou.txt'):
    os.system('mkdir dicts')
    os.system('curl -L -o dicts/rockyou.txt https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt')

# Conectar a la base de datos
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Passwords (
        id INTEGER PRIMARY KEY,
        password TEXT
    )
''')
conn.commit()

# Función para insertar en la base de datos
def insert_password(password):
    cursor.execute('INSERT INTO Passwords (password) VALUES (?)', (password,))
    conn.commit()

# Abrir el archivo rockyou.txt y realizar inserciones en paralelo
with open('dicts/rockyou.txt', 'r', encoding='utf-8', errors='ignore') as file:
    passwords = [line.strip() for line in file]

with ThreadPoolExecutor() as executor:
    executor.map(insert_password, passwords)

# Cerrar la conexión a la base de datos
conn.close()

print("Inserciones completadas.")
