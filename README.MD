# Username and Password Combination Checker
Scare for people who like leeching

This Python script is designed for generating and checking various combinations of usernames and passwords through HTTP requests. It utilizes multiple proxies for enhanced anonymity and parallel processing for efficient execution. The script can be configured to work with a custom domain URL through command-line arguments.

## Prerequisites

Ensure that you have the following prerequisites installed:

- Python 3.x
- Required Python packages (install using `pip install package_name`):
  - requests
  - concurrent.futures
  - tqdm
  - sqlite3
  - httpx

## Configuration

### Script Constants
Customize the script constants according to your preferences.
```python
DATABASE_PATH = 'data.db'  # Path to the SQLite database
USER_API_URL = 'https://api.generadordni.es/person/username?results=100'
PASS_API_URL = 'https://api.generadordni.es/person/password?results=100'
DOMAIN_URL = 'https://localhost/'  # Default domain URL
MAX_RETRIES = 3  # Maximum retry attempts for obtaining passwords with a proxy
REQUEST_TIMEOUT = 5  # Maximum request timeout in seconds
REQUEST_TIMEOUT_CHECK_PROXY = 1
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

Review the generated 'results.txt' file for HTTP request results. The file will contain responses for each combination tested.

```text
Example Output 1
Example Output 2
...
```

## Notes

- Adjust the number of generated combos, API URLs, and other parameters based on your specific requirements.
- Ensure you have an active internet connection for proxy validation and API requests.
- Customize error handling and logging as needed for your use case.