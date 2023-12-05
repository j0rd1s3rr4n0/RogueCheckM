import json
import requests
import sqlite3
from urllib.parse import urlparse
import inquirer
from inquirer.errors import ValidationError

# Configuración de la base de datos y la URL de configuración
DATABASE_FILE = 'proxies.db'
CONFIG_URL = "https://j0rd1s3rr4n0.github.io/api/RogueCheckM/config.json"

# Inicializar la variable config
config = None

# Variable para rastrear el camino de los proxies
proxy_path = []

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
        for source in proxy_sources:
            try:
                response = requests.get(source)
                proxies.extend(response.text.strip().split('\r\n'))
            except requests.RequestException as e:
                print(f"No se pudo obtener proxies de {source}. Error: {e}")

        return proxies
    except requests.RequestException as e:
        print(f"No se pudo obtener la configuración. Error: {e}")
        return []

# Función para actualizar proxies desde la configuración
def update_proxies_from_config_main():
    global config, proxy_path
    proxies = fetch_proxies_from_config()
    if proxies:
        config = proxies
        for proxy in proxies:
            # Manejar proxies con formato incorrecto
            try:
                ip, port = proxy.split(':')
                add_proxy(ip, int(port))
            except ValueError:
                pass
        proxy_path = config.copy()  # Inicializa el camino de proxies con la configuración actual
        print(f"Proxies actualizados desde la configuración.")
    else:
        print("No se pudo actualizar los proxies desde la configuración.")

# Función de menú interactivo con inquirer
def interactive_menu_inquirer():
    global proxy_path
    # Llamar a la función para actualizar proxies desde la configuración
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

    while True:
        answers = inquirer.prompt(questions)

        # Obtener la función correspondiente a la opción seleccionada
        selected_option = answers["choice"]
        if selected_option == "exit_program":
            exit()
        elif selected_option == "make_request":
            make_request_menu()

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

def get_proxies():
    global config
    return config  # Utiliza config directamente ya que es una lista de proxies

# Función de menú interactivo para realizar solicitud con URL verificada
def make_request_menu():
    global proxy_path
    url = get_valid_url()
    payload = {}

    # Obtener la lista de proxies
    proxies = get_proxies()
    if len(proxies) != 0:
        # Utilizar los proxies en cadena
        for proxy in proxies:
            proxy_url = f"http://{proxy}"
            try:
                response = requests.get(url, params=payload, proxies={"http": proxy_url, "https": proxy_url}, timeout=2)
                print(f"Proxy: {proxy_url}, Estado: {response.status_code}")
                print("Contenido de la respuesta:")
                print(response.text)
                print("Solicitud completada.")
            except requests.RequestException as e:
                #print(f"Proxy: {proxy_url}, Error: {e}")
                pass
            finally:
                proxy_path.append(proxy_url)  # Agrega el proxy actual al camino
        print(f"Recorrido de la solicitud: {' -> '.join(proxy_path)}\n")  # Imprime el recorrido del proxy

    # Restaura el camino de proxies a la configuración original
    proxy_path = config.copy()

# Función para manejar la excepción de Ctrl+C
def handle_ctrl_c(signum, frame):
    print("\nSaliendo del programa de manera esperada.")
    exit()

# Bucle principal
if __name__ == "__main__":
    # Configurar el manejador de la señal para Ctrl+C
    import signal
    signal.signal(signal.SIGINT, handle_ctrl_c)

    create_database()
    interactive_menu_inquirer()