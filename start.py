import random
import requests
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Instala la librería tqdm si aún no la tienes instalada
# Puedes instalarla con pip install tqdm

# Constantes
PROXY_API_URL = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'
USER_API_URL = 'https://api.generadordni.es/person/username?results=100'
PASS_API_URL = 'https://api.generadordni.es/person/password?results=100'

def get_proxies():
    try:
        response = requests.get(PROXY_API_URL)
        proxies = response.text.split('\r\n')
        return proxies
    except Exception as e:
        print(f"Error obteniendo proxies: {e}")
        return []

def check_proxy(proxy):
    try:
        response = requests.get('https://www.google.com', proxies={'http': proxy, 'https': proxy}, timeout=5)
        if response.status_code == 200:
            tqdm.write(f"{proxy}\t- [🚨]")
            time.sleep(0.2)
            tqdm.flush()
            return proxy
    except:
        pass

def get_usernames(proxies):
    try:
        # Seleccionar un proxy aleatorio de la lista de proxies que funcionan
        proxy = random.choice(proxies)
        response = requests.get(USER_API_URL, proxies={'http': proxy, 'https': proxy})
        usernames = random.sample(response.json(), 100)
        print(response)
        return usernames
    except Exception as e:
        print(f"Error obteniendo nombres de usuario: {e}")
        return []

def get_passwords(proxies):
    try:
        # Seleccionar un proxy aleatorio de la lista de proxies que funcionan
        proxy = random.choice(proxies)
        response = requests.get(PASS_API_URL, proxies={'http': proxy, 'https': proxy})
        passwords = random.sample(response.json(), 100)
        return passwords
    except Exception as e:
        print(f"Error obteniendo contraseñas: {e}")
        return []

def main():
    print('Searching and Checking Proxies...')

    # Obtener proxies con threads
    with ThreadPoolExecutor() as executor:
        proxies = list(tqdm(executor.map(check_proxy, get_proxies()), total=len(get_proxies()), desc="Checking Proxies"))

    working_proxies = [proxy for proxy in proxies if proxy is not None]

    print(f'Found {len(working_proxies)} working proxies.')

    print('Searching for Usernames...')
    usernames = get_usernames(working_proxies)
    print(f'Generated {len(usernames)} usernames.')

    print('Searching for Passwords...')
    passwords = get_passwords(working_proxies)
    print(f'Generated {len(passwords)} passwords.')

if __name__ == "__main__":
    main()
