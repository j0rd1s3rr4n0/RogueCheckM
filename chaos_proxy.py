import requests
import sqlite3

# Configuración de la base de datos
DATABASE_FILE = 'proxies.db'
PROXY_API_URL = 'http://pubproxy.com/api/proxy?last_check=60&format=txt'

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

def add_proxy(host, port):
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    # Insertar el proxy en la tabla
    cursor.execute('INSERT INTO proxies (host, port) VALUES (?, ?)', (host, port))

    connection.commit()
    connection.close()

def fetch_proxies_from_api():
    response = requests.get(PROXY_API_URL)
    if response.status_code == 200:
        proxy_data = response.text.strip().split(':')
        return proxy_data[0], int(proxy_data[1])
    else:
        print(f"No se pudo obtener el proxy de la API. Código de estado: {response.status_code}")
        return None

def update_proxies_from_api():
    proxy_host, proxy_port = fetch_proxies_from_api()
    if proxy_host and proxy_port:
        add_proxy(proxy_host, proxy_port)
        print(f"Proxy actualizado desde la API: {proxy_host}:{proxy_port}")
    else:
        print("No se pudo actualizar el proxy desde la API.")

def get_proxies():
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()
    # Obtener todos los proxies
    cursor.execute('SELECT host, port FROM proxies')
    proxies = cursor.fetchall()
    connection.close()
    return proxies

def interactive_menu():
    # Menú interactivo para el usuario
    print("1. Realizar solicitud")
    print("2. Actualizar proxies desde la API")
    print("3. Salir")

    choice = input("Ingrese su elección: ")

    if choice == '1':
        make_request()
    elif choice == '2':
        update_proxies_from_api()
    elif choice == '3':
        exit()
    else:
        print("Opción no válida. Inténtelo de nuevo.")
        interactive_menu()

def make_request():
    url = input("Ingrese la URL de la solicitud: ")
    payload = input("Ingrese los parámetros (si los hay): ")

    # Obtener la lista de proxies
    proxies = get_proxies()

    # Utilizar los proxies en cadena
    for proxy in proxies:
        proxy_url = f"http://{proxy[0]}:{proxy[1]}"
        try:
            response = requests.get(url, params=payload, proxies={"http": proxy_url, "https": proxy_url}, timeout=5)
            print(f"Proxy: {proxy_url}, Estado: {response.status_code}")
        except requests.RequestException as e:
            print(f"Proxy: {proxy_url}, Error: {e}")

    print("Solicitud completada.")

if __name__ == "__main__":
    create_database()
    while True:
        interactive_menu()
