import random
import requests
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import sqlite3
import httpx

# Constantes
DATABASE_PATH = 'data.db'  # Ruta de la base de datos SQLite
PROXY_API_URL = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'
USER_API_URL = 'https://api.generadordni.es/person/username?results=100'
PASS_API_URL = 'https://api.generadordni.es/person/password?results=100'
MAX_RETRIES = 3  # Número máximo de intentos para obtener contraseñas con un proxy
REQUEST_TIMEOUT = 2  # Tiempo máximo de espera para las solicitudes en segundos
REQUEST_TIMEOUT_CHECK_PROXY = 0.5

def create_tables(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Proxies
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT, port INT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Usernames
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Passwords
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, password TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Emails
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Pastebins
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, code TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Combos
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)''')
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al crear las tablas en la base de datos: {e}")

def check_proxy(proxy):
    try:
        response = requests.get('https://www.google.com', proxies={'http': proxy, 'https': proxy}, timeout=REQUEST_TIMEOUT_CHECK_PROXY)
        if response.status_code == 200:
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

def get_proxies():
    try:
        response = requests.get(PROXY_API_URL, timeout=REQUEST_TIMEOUT)
        proxies = response.text.split('\r\n')
        return proxies
    except Exception as e:
        print(f"Error obteniendo proxies: {e}")
        return []

def request_web(url, proxies):
    try:
        with httpx.Client() as client:
            response = client.get(url, proxies=proxies, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.text
    except (httpx.RequestError, httpx.TimeoutException) as e:
        return
        #return f"Error al hacer la solicitud HTTP para {url}: {e}"
    

def request_web_combos(combos, proxies):
    """Envía solicitudes HTTP para combos de usernames y passwords."""
    try:
        results = []
        for combo in tqdm(combos, desc="Sending HTTP Requests", unit=" combo"):
            username, password = combo
            url = f' https://95c7-81-60-169-15.ngrok-free.app?username={username}&password={password}'

            proxy = random.choice(proxies) if proxies else None
            try:
                response = requests.get(url, proxies={'http': proxy, 'https': proxy} if proxy else None, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                results.append(response.text)
            except requests.RequestException as e:
                # Manejar errores de solicitud, incluida la cancelación
                # print(f"Error al hacer la solicitud HTTP para {url}: {e}")
                results.append(f"Error al hacer la solicitud HTTP para {url}: {e}")
                # break  # Cancelar el bucle en caso de error
                pass

        return results

    except Exception as e:
        # print(f"Error en la función request_web_combos: {e}")
        return []

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

def get_usernames(proxy):
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            response = requests.get(USER_API_URL, proxies={'http': proxy, 'https': proxy}, timeout=REQUEST_TIMEOUT)
            usernames = random.sample(response.json(), 100)
            insert_usernames(conn, usernames)
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
                insert_passwords(conn, passwords)
                return passwords
        except Exception as e:
            retries += 1
    return []

def generate_combos(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Combos")  # Limpiar tabla de combos antes de regenerar
        cursor.execute("SELECT username FROM Usernames")
        usernames = [record[0] for record in cursor.fetchall()]
        cursor.execute("SELECT password FROM Passwords")
        passwords = [record[0] for record in cursor.fetchall()]

        # Generar combos y agregarlos a la base de datos
        for _ in range(100):  # Número arbitrario de combos a generar
            username = random.choice(usernames)
            password = random.choice(passwords)
            cursor.execute("INSERT INTO Combos (username, password) VALUES (?, ?)", (username, password))

        conn.commit()
        cursor.close()

    except Exception as e:
        print(f"Error al generar combos: {e}")

def main():
    with sqlite3.connect(DATABASE_PATH) as conn:
        create_tables(conn)

        print('Searching and Checking Proxies...')
        with ThreadPoolExecutor() as executor:
            proxies = list(tqdm(executor.map(lambda x: check_proxy(x), get_proxies()), total=len(get_proxies()), desc="Checking Proxies", unit=" proxies"))
        working_proxies = [proxy for proxy in proxies if proxy is not None]
        print(f'Found {len(working_proxies)} working proxies.')

        if not working_proxies:
            print("CANCELED ACCOUNT CHECKING DUE TO LACK OF PROXIES")
            return

        print('Searching for Usernames and Passwords...')
        with ThreadPoolExecutor() as executor:
            usernames = list(tqdm(executor.map(lambda x: get_usernames(x), working_proxies), total=len(working_proxies), desc="Getting Usernames"))

        print('Checking Valid Formats...')
        with ThreadPoolExecutor() as executor:
            passwords = list(tqdm(executor.map(lambda x: get_passwords(x), working_proxies), total=len(working_proxies), desc="Getting Passwords"))

        generate_combos(conn)  # Generar combos antes de enviar solicitudes HTTP

        combos_len = 100  # Número arbitrario de combos a enviar
        print(f'Generated {combos_len} usernames and passwords.')

        print('Generating and Sending HTTP Requests...')
        with ThreadPoolExecutor() as executor:
            combos = [(record[0], record[1]) for record in conn.execute("SELECT username, password FROM Combos").fetchall()]
            results = list(
                executor.map(
                    lambda x: request_web_combos(x, working_proxies),
                    [combos[i:i + 100] for i in range(0, len(combos), 100)]
                )
            )

            # Imprimir los resultados si es necesario
            for result_set in results:
                for result in result_set:
                    print(result)

if __name__ == "__main__":
    main()
