import random
import requests
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import sqlite3
import httpx
import signal
import sys
import time

conn = "CONECTION SQLITE"

# Constantes
DATABASE_PATH = 'data.db'  # Path to the SQLite database
USER_API_URL = 'https://api.generadordni.es/person/username?results=100'
PASS_API_URL = 'https://api.generadordni.es/person/password?results=100'
DOMAIN_URL = 'https://localhost/'  # Default domain URL
MAX_RETRIES = 3  # Maximum retry attempts for obtaining passwords with a proxy
REQUEST_TIMEOUT = 5  # Maximum request timeout in seconds
REQUEST_TIMEOUT_CHECK_PROXY = 1

def signal_handler(sig, frame):
        print("Ctrl+C presionado. Cancelando la ejecución...")
        sys.exit(0)
        
def create_tables(conn):
    try:
        try:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS proxys (id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT, port INT)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS Usernames (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS Passwords (id INTEGER PRIMARY KEY AUTOINCREMENT, password TEXT)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS Emails (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS Pastebins (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, code TEXT)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS Combos (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)''')
            conn.commit()
            cursor.close()
        except Exception as e:
            print(f"Error al crear las tablas en la base de datos: {e}")
    except KeyboardInterrupt:
        print("Ctrl+C presionado. Cancelando la ejecución...")

def check_proxy(proxy):
    try:
        try:
            response = requests.get('https://www.google.com', proxies={'http': proxy, 'https': proxy}, timeout=REQUEST_TIMEOUT_CHECK_PROXY)
            if response.status_code == 200:
                insert_proxy(conn=conn,proxy=proxy)
                return proxy
        except Exception as e:
            pass
    except KeyboardInterrupt:
        print("Ctrl+C presionado. Cancelando la ejecución...")

def insert_proxy(conn, proxy):
    try:
        try:
            cursor = conn.cursor()
            ip, port = proxy.split(':') if ':' in proxy else (proxy, None)
            cursor.execute("INSERT INTO proxys (ip, port) VALUES (?, ?)", (ip, port))
            conn.commit()
            cursor.close()
        except Exception as e:
            # print(f"Error al insertar el proxy en la base de datos: {e}")
            pass
    except KeyboardInterrupt:
        print("Ctrl+C presionado. Cancelando la ejecución...")

def get_proxys():
    proxy_urls = [
        'https://www.proxy-list.download/api/v1/get?type=http',
        'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all',
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
        'https://www.proxy-list.download/api/v1/get?type=https',
        'https://api.proxyscrape.com/v2/?request=getproxies&protocol=https&timeout=10000&country=all',
        'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt',
        'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',
        'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
        'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt',
        'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'
    ]
    proxys = []
    try:
        for url in proxy_urls:
            try:
                response = requests.get(url, timeout=REQUEST_TIMEOUT)
                proxys.extend(response.text.split('\r\n'))
            except Exception as e:
                pass
    except KeyboardInterrupt:
        print("Ctrl+C presionado. Cancelando la ejecución...")
    return proxys


def request_web(url, proxys):
    try:
        try:
            with httpx.Client() as client:
                response = client.get(url, proxys=proxys, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                return response.text
        except (httpx.RequestError, httpx.TimeoutException) as e:
            return
            #return f"Error al hacer la solicitud HTTP para {url}: {e}"
    except KeyboardInterrupt:
        print("Ctrl+C presionado. Cancelando la ejecución...")
    

def request_web_combos(combos, proxys):
    """Envía solicitudes HTTP para combos de usernames y passwords."""
    domain = DOMAIN_URL
    try:
        try:
            results = []
            description = f"Sending HTTP Requests to {DOMAIN_URL}"
            for combo in tqdm(combos, desc=description, unit="combo_proxy"):
                username, password = combo
                url = f' https://{domain}?username={username}&password={password}'

                proxy = random.choice(proxys) if proxys else None
                try:
                    response = requests.get(url, proxies={'http': proxy, 'https': proxy} if proxy else None, timeout=REQUEST_TIMEOUT)
                    response.raise_for_status()
                    results.append(response.text)
                except requests.RequestException as e:
                    # Manejar errores de solicitud, incluida la cancelación
                    # print(f"Error al hacer la solicitud HTTP para {url}: {e}")
                    # results.append(f"Error al hacer la solicitud HTTP para {url}: {e}")
                    # break  # Cancelar el bucle en caso de error
                    pass

            return results

        except Exception as e:
            # print(f"Error en la función request_web_combos: {e}")
            return []
    except KeyboardInterrupt:
        print("Ctrl+C presionado. Cancelando la ejecución...")

def insert_usernames(conn, usernames):
    try:
        try:
            cursor = conn.cursor()
            for username in usernames:
                cursor.execute("INSERT INTO Usernames (username) VALUES (?)", (username,))
            conn.commit()
            cursor.close()
        except Exception as e:
            print(f"Error al insertar los usernames en la base de datos: {e}")
    except KeyboardInterrupt:
        print("Ctrl+C presionado. Cancelando la ejecución...")

def insert_passwords(conn, passwords):
    try:
        try:
            cursor = conn.cursor()
            for password in passwords:
                cursor.execute("INSERT INTO Passwords (password) VALUES (?)", (password,))
            conn.commit()
            cursor.close()
        except Exception as e:
            print(f"Error al insertar los passwords en la base de datos: {e}")
    except KeyboardInterrupt:
        print("Ctrl+C presionado. Cancelando la ejecución...")

def get_usernames(proxy):
    try:
        try:
            with sqlite3.connect(DATABASE_PATH) as conn:
                response = requests.get(USER_API_URL, proxies={'http': proxy, 'https': proxy}, timeout=REQUEST_TIMEOUT)
                usernames = random.sample(response.json(), 100)
                insert_usernames(conn, usernames)
                return usernames
        except Exception as e:
            return []
    except KeyboardInterrupt:
        print("Ctrl+C presionado. Cancelando la ejecución...")

def get_passwords(proxy):
    try:
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
    except KeyboardInterrupt:
        print("Ctrl+C presionado. Cancelando la ejecución...")

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
    
    if "--url" in sys.argv or "-u" in sys.argv:
        index = sys.argv.index("--url") if "--url" in sys.argv else sys.argv.index("-u")
        global DOMAIN_URL
        DOMAIN_URL = sys.argv[index + 1]
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        global conn
        with sqlite3.connect(DATABASE_PATH) as conn:
            create_tables(conn)

            # print('Searching and Checking proxys...')
            with ThreadPoolExecutor() as executor:
                proxys = list(tqdm(executor.map(lambda x: check_proxy(x), get_proxys()), total=len(get_proxys()), desc="Searching and Checking proxys", unit=" proxys"))
            working_proxys = [proxy for proxy in proxys if proxy is not None]
            print(f'Found {len(working_proxys)} working proxys.')
            
            if not working_proxys:
                print("CANCELED ACCOUNT CHECKING DUE TO LACK OF proxys")
                return

            # print('Searching for Usernames and Passwords...')
            with ThreadPoolExecutor() as executor:
                usernames = list(tqdm(executor.map(lambda x: get_usernames(x), working_proxys), total=len(working_proxys), desc="Searching Usernames and Passwords",unit=" combos_proxy"))

            # print('Checking Valid Formats...')
            with ThreadPoolExecutor() as executor:
                passwords = list(tqdm(executor.map(lambda x: get_passwords(x), working_proxys), total=len(working_proxys), desc="Checking Valid Formats"))

            generate_combos(conn)  # Generar combos antes de enviar solicitudes HTTP

            combos_len = min(len(usernames),len(passwords))  # Número arbitrario de combos a enviar
            print(f'Obtained {combos_len} usernames and passwords.')

            # print('Generating and Sending HTTP Requests...')
            with ThreadPoolExecutor() as executor:
                combos = [(record[0], record[1]) for record in conn.execute("SELECT username, password FROM Combos").fetchall()]
                # results = list(tqdm(executor.map(lambda x: request_web_combos(x, working_proxys), [combos[i:i + 100] for i in range(0, len(combos), 100)]), desc="Generating and Sending HTTP Requests...", total=len(combos)))
                results = list(executor.map(lambda x: request_web_combos(x, working_proxys), [combos[i:i + 100] for i in range(0, len(combos), 100)]))
                
            # Guardar los resultados en el archivo results.txt
            with open('results.txt', 'w') as results_file:
                for result_set in results:
                    for result in result_set:
                        print(result)
                        results_file.write(result + '\n')
    except KeyboardInterrupt:
        print("Ctrl+C presionado. Cancelando la ejecución...")

if __name__ == "__main__":
    main()