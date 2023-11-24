import random
import requests
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import time

# Constantes
PROXY_API_URL = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'
USER_API_URL = 'https://api.generadordni.es/person/username?results=100'
PASS_API_URL = 'https://api.generadordni.es/person/password?results=100'
MAX_RETRIES = 3  # Número máximo de intentos para obtener contraseñas con un proxy

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
            return proxy
    except:
        pass

def get_usernames(proxy):
    try:
        response = requests.get(USER_API_URL, proxies={'http': proxy, 'https': proxy})
        usernames = random.sample(response.json(), 100)
        return usernames
    except Exception as e:
        #print(f"Error obteniendo nombres de usuario: {e}")
        return []

def geolocate_proxy():
    try:
        response = requests.get('https://ipapi.co/json/')
        geolocation = response.json()
        return geolocation
    except Exception as e:
        #print(f"Error obteniendo geolocalización: {e}")
        return {}

def get_passwords(proxy):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = requests.get(PASS_API_URL, proxies={'http': proxy, 'https': proxy})
            passwords = random.sample(response.json(), 100)
            return passwords
        except Exception as e:
            #print(f"Error obteniendo contraseñas: {e}")
            retries += 1
    return []

def main():
    print('Searching and Checking Proxies...')

    # Obtener proxies con threads
    with ThreadPoolExecutor() as executor:
        proxies = list(tqdm(executor.map(check_proxy, get_proxies()), total=len(get_proxies()), desc="Checking Proxies", unit=" proxies"))

    working_proxies = [proxy for proxy in proxies if proxy is not None]
    print(f'Found {len(working_proxies)} working proxies.')

    print('Searching for Usernames...')
    with ThreadPoolExecutor() as executor:
        usernames = list(tqdm(executor.map(get_usernames, working_proxies), total=len(working_proxies), desc="Getting Usernames"))

    print(f'Generated {sum(len(usernames_list) for usernames_list in usernames)} usernames.')

    print('Searching for Passwords...')
    with ThreadPoolExecutor() as executor:
        passwords = list(tqdm(executor.map(get_passwords, working_proxies), total=len(working_proxies), desc="Getting Passwords"))

    print(f'Generated {sum(len(passwords_list) for passwords_list in passwords)} passwords.')

if __name__ == "__main__":
    main()
