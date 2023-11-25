import random
import requests
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import sqlite3

# Constantes
DATABASE_PATH = 'data.db'  # Ruta de la base de datos SQLite
PROXY_API_URL = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'
USER_API_URL = 'https://api.generadordni.es/person/username?results=100'
PASS_API_URL = 'https://api.generadordni.es/person/password?results=100'
MAX_RETRIES = 3  # Número máximo de intentos para obtener contraseñas con un proxy
REQUEST_TIMEOUT = 5  # Tiempo máximo de espera para las solicitudes en segundos

def create_tables(conn):
    try:
        cursor = conn.cursor()
        # Tabla de Proxies
        cursor.execute('''CREATE TABLE IF NOT EXISTS Proxies
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT, port INT)''')
        # Tabla de Usernames
        cursor.execute('''CREATE TABLE IF NOT EXISTS Usernames
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT)''')
        # Tabla de Passwords
        cursor.execute('''CREATE TABLE IF NOT EXISTS Passwords
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, password TEXT)''')
        # Tabla de Emails
        cursor.execute('''CREATE TABLE IF NOT EXISTS Emails
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT)''')
        # Tabla de Pastebins
        cursor.execute('''CREATE TABLE IF NOT EXISTS Pastebins
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, code TEXT)''')
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al crear las tablas en la base de datos: {e}")

def insert_usernames(conn, usernames):
    try:
        cursor = conn.cursor()
        for username in usernames:
            cursor.execute("INSERT INTO Usernames (username) VALUES (?)", (username,))
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al insertar los usernames en la base de datos: {e}")

def insert_passwords(conn, passwords):
    try:
        cursor = conn.cursor()
        for password in passwords:
            cursor.execute("INSERT INTO Passwords (password) VALUES (?)", (password,))
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al insertar los passwords en la base de datos: {e}")

def get_proxies():
    try:
        response = requests.get(PROXY_API_URL, timeout=REQUEST_TIMEOUT)
        proxies = response.text.split('\r\n')
        return proxies
    except Exception as e:
        print(f"Error obteniendo proxies: {e}")
        return []

def check_proxy(proxy):
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            # Código de verificación del proxy y almacenamiento en la base de datos
            response = requests.get('https://www.google.com', proxies={'http': proxy, 'https': proxy}, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                # Almacenar el proxy en la base de datos si es válido
                insert_proxy(conn, proxy)
                return proxy
    except Exception as e:
        pass

def insert_proxy(conn, proxy):
    try:
        cursor = conn.cursor()
        ip, port = proxy.split(':') if ':' in proxy else (proxy, None)
        cursor.execute("INSERT INTO Proxies (ip, port) VALUES (?, ?)", (ip, port))
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al insertar el proxy en la base de datos: {e}")

def get_usernames(proxy):
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            response = requests.get(USER_API_URL, proxies={'http': proxy, 'https': proxy}, timeout=REQUEST_TIMEOUT)
            usernames = random.sample(response.json(), 100)
            insert_usernames(conn, usernames)  # Insertar usernames en la base de datos
            return usernames
    except Exception as e:
        return []

def get_passwords(proxy):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            with sqlite3.connect(DATABASE_PATH) as conn:
                response = requests.get(PASS_API_URL, proxies={'http': proxy, 'https': proxy}, timeout=REQUEST_TIMEOUT)
                passwords = random.sample(response.json(), 100)
                insert_passwords(conn, passwords)  # Insertar passwords en la base de datos
                return passwords
        except Exception as e:
            retries += 1
    return []

def main():
    # Crear o conectar a la base de datos
    with sqlite3.connect(DATABASE_PATH) as conn:
        # Crear las tablas si no existen
        create_tables(conn)

        print('Searching and Checking Proxies...')
        # Obtener proxies con threads
        with ThreadPoolExecutor() as executor:
            proxies = list(tqdm(executor.map(lambda x: check_proxy(x), get_proxies()), total=len(get_proxies()), desc="Checking Proxies", unit=" proxies"))
        working_proxies = [proxy for proxy in proxies if proxy is not None]
        print(f'Found {len(working_proxies)} working proxies.')

        print('Searching for Usernames and Passwords...')
        with ThreadPoolExecutor() as executor:
            usernames = list(tqdm(executor.map(lambda x: get_usernames(x), working_proxies), total=len(working_proxies), desc="Getting Usernames"))

        print('Checking Valid Formats...')
        with ThreadPoolExecutor() as executor:
            passwords = list(tqdm(executor.map(lambda x: get_passwords(x), working_proxies), total=len(working_proxies), desc="Getting Passwords"))
        combos_len = min(sum(len(usernames_list) for usernames_list in usernames), sum(len(passwords_list) for passwords_list in passwords))
        print(f'Generated {combos_len} usernames.')
        print(f'Generated {combos_len} passwords.')

if __name__ == "__main__":
    main()
