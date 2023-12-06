import json
import requests
import sqlite3
from urllib.parse import urlparse
import inquirer
from inquirer.errors import ValidationError
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent
import multiprocessing

# Configuración de la base de datos y la URL de configuración
DATABASE_FILE = 'proxies.db'
CONFIG_URL = "https://j0rd1s3rr4n0.github.io/api/RogueCheckM/config.json"

# Lista global de proxies verificados
verified_proxies = []

# Función para obtener el número máximo de max_workers basado en los procesadores disponibles
def get_max_workers():
    num_processors = multiprocessing.cpu_count()
    percentage_of_processors = 0.75  # Puedes ajustar este valor según tus necesidades
    return int(num_processors * percentage_of_processors)

# Función para crear la base de datos
def create_database():
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    # Crear la tabla de proxies si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proxies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host TEXT NOT NULL,
            port INTEGER NOT NULL
        )
    ''')

    connection.commit()
    connection.close()

# Función para agregar un proxy a la base de datos
def add_proxy(host, port):
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    # Insertar el proxy en la tabla
    cursor.execute('INSERT INTO proxies (host, port) VALUES (?, ?)', (host, port))

    connection.commit()
    connection.close()

# Función para verificar si la cadena es una URL válida
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

# Función para obtener proxies desde la configuración
def fetch_proxies_from_config():
    try:
        response = requests.get(CONFIG_URL)
        config_data = json.loads(response.text)
        proxy_sources = config_data.get("proxy_sources", [])
        proxies = []

        def fetch_proxy(source):
            try:
                response = requests.get(source)
                return response.text.strip().split('\r\n')
            except requests.RequestException as e:
                print(f"No se pudo obtener proxies de {source}. Error: {e}")
                return []

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(fetch_proxy, source) for source in proxy_sources]
            for future in futures:
                proxies.extend(future.result())

        return proxies
    except requests.RequestException as e:
        print(f"No se pudo obtener la configuración. Error: {e}")
        return []

# Función para verificar si un proxy es funcional
def test_proxy(proxy):
    try:
        response = requests.get("https://www.google.com", proxies={"http": proxy, "https": proxy}, timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Función para actualizar proxies verificados
def update_verified_proxies():
    global verified_proxies
    proxies_to_verify = fetch_proxies_from_config()

    with ThreadPoolExecutor(max_workers=5) as executor:
        verified_proxies = [proxy for proxy in proxies_to_verify if executor.submit(test_proxy, f"http://{proxy}").result()]

# Función para actualizar proxies desde la configuración
def update_proxies_from_config_main():
    create_database()
    update_verified_proxies()
    print(f"Proxies actualizados desde la configuración.")

# Función de menú interactivo con inquirer
def interactive_menu_inquirer():
    update_proxies_from_config_main()

    questions = [
        inquirer.List(
            "choice",
            message="Seleccione una opción:",
            choices=[
                ("Realizar solicitud", "make_request"),
                ("Actualizar proxies desde la configuración", "update_proxies_from_config_main"),
                ("Salir", "exit_program"),
            ],
        )
    ]

    max_workers = get_max_workers()

    while True:
        answers = inquirer.prompt(questions)

        selected_option = answers["choice"]
        if selected_option == "exit_program":
            exit()
        elif selected_option == "make_request":
            make_request_menu(max_workers)

# Función para ingresar la URL con verificación
def get_valid_url():
    questions = [
        inquirer.Text(
            "url",
            message="Ingrese la URL de la solicitud:",
            validate=lambda _, response: is_valid_url(response) or "Por favor, ingrese una URL válida.",
        )
    ]

    answer = inquirer.prompt(questions)
    return answer["url"]

# Función para obtener proxies válidos
def get_proxies():
    global verified_proxies
    return verified_proxies

# Función para realizar una solicitud a través de una cadena de proxies
def make_request(url, proxies_chain, user_agent):
    payload = {}
    headers = {'User-Agent': user_agent}

    try:
        for i, proxy_url in enumerate(proxies_chain):
            proxies = {"http": proxy_url, "https": proxy_url}
            response = requests.get(url, params=payload, proxies=proxies, headers=headers, timeout=5)
            
            print(f"\033[94m[*]\033[0m Realizando Solicitud a {url}")
            print(f"\033[92m[!]\033[0m Camino usado {' -> '.join(proxies_chain[:i+1])} --> {url}")
            print(f"\033[91m[!]\033[0m Proxy {i + 1}: {proxy_url}, Estado: {response.status_code}")

            if response.status_code != 200:
                print(f"\033[91m[!]\033[0m Solicitud fallida en este proxy. Deteniendo la cadena.")
                break

        print("\033[92m[!]\033[0m Contenido de la respuesta:")
        print(response.text)
        print("\033[92m[!]\033[0m Solicitud completada.")
        return True
    except requests.RequestException as e:
        return False

# Función de menú interactivo para realizar solicitud con URL verificada
def make_request_menu(max_workers):
    url = get_valid_url()
    user_agent = UserAgent().random

    proxies = get_proxies()
    if len(proxies) >= 2:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in range(len(proxies) - 1):
                first_proxy = proxies[i]
                second_proxy = proxies[i + 1]
                proxies_chain = [f"http://{first_proxy}", f"http://{second_proxy}"]

                try:
                    make_request(url, proxies_chain, user_agent)
                except requests.RequestException as e:
                    pass

# Función para manejar la excepción de Ctrl+C
def handle_ctrl_c(signum, frame):
    print("\n\033[93m[!]\033[0m Saliendo del programa de manera esperada.")
    exit()

# Bucle principal
if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, handle_ctrl_c)

    interactive_menu_inquirer()
