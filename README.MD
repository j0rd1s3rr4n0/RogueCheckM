# RogueCheckM

RogueCheckM is a Python script designed for generating and checking various combinations of usernames and passwords through HTTP requests. It utilizes multiple proxies for enhanced anonymity and parallel processing for efficient execution. The script can be configured to work with a custom domain URL through command-line arguments.

## Prerequisites

Ensure that you have the following prerequisites installed:

- Python 3.x
- Required Python packages (install using `pip install package_name`):
  - requests
  - concurrent.futures
  - tqdm
  - sqlite3
  - httpx
  - colorama

You can find a list of all required dependencies in the requirements.txt file.
```bash
pip install -r requirements.txt
```

## Configuration

### Script Constants
Customize the script constants according to your preferences.
```python
MAX_RETRIES = 3  # Maximum retry attempts for obtaining passwords with a proxy
REQUEST_TIMEOUT = 1  # Maximum request timeout in seconds
REQUEST_TIMEOUT_CHECK_PROXY = 2
DATABASE_PATH = None  # Path to the SQLite database
NEW_URL = False
DOMAIN_URL = None  # Default domain URL
SERVICE_NAME = None
USER_API_URL = None
PASS_API_URL = None
MAX_WORKERS = None
```

### Command-Line Argument for Custom Domain URL

The script now checks for the presence of a command-line argument specifying a custom domain URL. If present, it updates the `DOMAIN_URL` variable accordingly.

```python
# Example command-line usage:
# python main.py --url http://custom_domain_url.com
# or
# python main.py -u http://custom_domain_url.com

if "--url" in sys.argv or "-u" in sys.argv:
    index = sys.argv.index("--url") if "--url" in sys.argv else sys.argv.index("-u")
    DOMAIN_URL = sys.argv[index + 1]
```

## Execution

Run the script by executing the following command in your terminal:

```bash
python main.py
```

For specifying a custom domain URL:

```bash
python main.py --url http://custom_domain_url.com
```

or

```bash
python main.py -u http://custom_domain_url.com
```

## Execution Flow

The execution flow remains the same as described in the previous guide. The script now dynamically updates the `DOMAIN_URL` based on the command-line arguments provided.

## Example
### Input

Suppose you want to check username and password combinations for a custom domain "http://example.com". Run the script with the following command:

```bash
python main.py --url http://example.com
```

### Output
```bash
Searching and Checking proxies...: 3988 proxies [03:00, 22.13 proxies/s]
Found 1517 working proxies.
Searching Usernames and Passwords: 100%|██████████████████████████████████| 1517/1517 [00:10<00:00,  2.56 combos_proxy/s]
Checking Valid Formats: 100%|██████████████████████████████████| 1517/1517 [02:18<00:00,  1.47it/s]
Generated 1517 usernames and passwords.
Sending HTTP Requests to http://example.com: 100%|██████████████████████████████████| 100/100 [05:04<00:00,  3.05s/combo_proxy]
```

## Notes

- Adjust the number of generated combos, API URLs, and other parameters based on your specific requirements.
- Ensure you have an active internet connection for proxy validation and API requests.
- Customize error handling and logging as needed for your use case.

## Testing
```bash
python -m unittest discover
```