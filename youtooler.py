import atexit
import os
import random
import requests
import shutil
import signal
import subprocess
import threading
import time
from argparse import ArgumentParser
from colorama import Fore, Back, Style
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from sys import stderr

# PIDs of the subprocesses to kill when exiting
tor_pids = []

class Tor():
    def __init__(self, socks_port: int):
        self.socks_port = socks_port
        self.process_pid = -1
        self.torrc_path = self.__create_temp_torrc__(socks_port)

    def start_tor(self):
        tor_process = subprocess.Popen(['tor', '-f', self.torrc_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.process_pid = tor_process.pid

        return tor_process

    def kill_tor(self):
        os.kill(self.process_pid, signal.SIGTERM)

    def get_external_address(self):
        '''
        Returns the external IP address with the help of a random IP API.\n
        Each time the function gets called, a random API is chosen to retrieve the IP address.\n
        The function checks whether an API is working or not, if it isn't then another one is chosen.
        '''

        apis = [
            'https://api.ipify.org',
            'https://api.my-ip.io/ip',
            'https://checkip.amazonaws.com',
            'https://icanhazip.com',
            'https://ifconfig.me/ip',
            'https://ip.rootnet.in',
            'https://ipapi.co/ip',
            'https://ipinfo.io/ip',
            'https://myexternalip.com/raw',
            'https://trackip.net/ip',
            'https://wtfismyip.com/text'
        ]

        proxies = {
            'http': f'socks5://localhost:{self.socks_port}',
            'https': f'socks5://localhost:{self.socks_port}'
        }

        for _ in apis:
            api = random.choice(apis)

            try:
                response = requests.get(api, proxies=proxies)
            except:
                pass

            if response.status_code in range(200, 300):
                return response.text.strip()
            else: # Removing API if not working
                apis.pop(apis.index(api))
    
    def __create_temp_torrc__(self, socks_port: int):
        '''
        Creates a temporary torrc file inside the program's storage directory (/tmp/youtooler).\n
        Also creates a temporary DataDirectory (used by TOR).\n
        Example torrc:\n
        --------------\n
        SocksPort 9050\n
        DataDirectory /tmp/youtooler/9050
        '''

        DATA_DIR = f'/tmp/youtooler/{socks_port}'
        TORRC_PATH = f'/tmp/youtooler/torrc.{socks_port}'
        
        try:
            os.mkdir(DATA_DIR)
        except:
            print(get_error_message('DTADIR'), file=stderr)
            exit()
        else:
            with open(TORRC_PATH, 'w') as torrc:
                torrc.write(f'SocksPort {socks_port}\nDataDirectory {DATA_DIR}\n')
                torrc.close()

        return TORRC_PATH

class RequestThread(threading.Thread):
    '''
    Takes the target YouTube url and the socks_port for TOR as parameters.\n
    Proxies each request through TOR using a random User-Agent.\n
    For each TOR instance a temporary torrc file and DataDirectory are created, they will be deleted when the program exits.\n
    To store the components needed by the program to run a temporary directory (/tmp/youtooler/) will be created.
    '''

    def __init__(self, url: str, socks_port: int):
        threading.Thread.__init__(self)
        self.url = url
        self.socks_port = socks_port

    def run(self):
        tor = Tor(self.socks_port)

        # Chrome WebDriver setup
        options = Options()
        options.add_argument(f'--proxy-server=socks5://localhost:{self.socks_port}')
        options.add_argument('--disable-audio-output')

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.set_window_size(width=800, height=600)

        while True:
            # Creating new TOR circuit on the specified socks_port
            try:
                tor_process = tor.start_tor()
                tor_pids.append(tor_process.pid)
            except:
                print(f'{Style.BRIGHT}{Fore.GREEN}Failed while creating a new Tor circuit on socks_port: {self.socks_port}{Style.RESET_ALL}')
                exit()
            else:
                print(f'{Style.BRIGHT}{Fore.GREEN}Created a new Tor circuit on socks_port: {self.socks_port}{Style.RESET_ALL}')

            try:
                driver.get(f'{self.url}&t={random.randint(1, 300)}s')
            except:
                pass
            else:
                print(f'{Style.BRIGHT}{Fore.GREEN}Current thread: {self.name} | Tor IP: {tor.get_external_address()}{Style.RESET_ALL}')

            # Killing subprocess in order to create a new TOR circuit
            tor.kill_tor()
            tor_pids.pop(tor_pids.index(tor_process.pid))

            driver.delete_all_cookies()

            time.sleep(random.uniform(20, 30))

def print_logo():
    print(f'{Style.BRIGHT}')
    print(f'{Fore.MAGENTA}                         _____.___.           {Fore.CYAN}___________           .__                ')
    print(f'{Fore.MAGENTA}               />        \\__  |   | ____  __ _{Fore.CYAN}\\__    ___/___   ____ |  |   {Fore.MAGENTA}___________ ')
    print(f'{Fore.MAGENTA}  ()          //----------/   |   |/  _ \\|  |  \\{Fore.CYAN}|    | /  _ \\ /  _ \\|  | {Fore.MAGENTA}_/ __ \\_  __ \\----------\\')
    print(f'{Fore.YELLOW} (*)OXOXOXOXO(*>          \\____   (  <_> )  |  /{Fore.CYAN}|    |(  <_> |  <_> )  |_{Fore.YELLOW}\\  ___/|  | \\/           \\')
    print(f'{Fore.YELLOW}  ()          \\\\----------/ ______|\\____/|____/ {Fore.CYAN}|____| \\____/ \\____/|____/{Fore.YELLOW}\\___  >__|---------------\\   ')
    print(f'{Fore.YELLOW}               \>         \\/                                      {Fore.YELLOW}            \\/       ')
    print(f'\n{Fore.WHITE}{Back.RED}Developers assume no liability and are not responsible for any misuse or damage caused by this program.')
    print(f'{Style.RESET_ALL}')

def create_storage_dir() -> str:
    '''
    Creates the temporary storage directory of the program (/tmp/youtooler).\n
    Returns the path to the storage directory.
    '''

    STORAGE_DIR = '/tmp/youtooler'

    try:
        os.mkdir(STORAGE_DIR)
    except:
        print(get_error_message('STRDIR'), file=stderr)
        exit()

    return STORAGE_DIR

def get_arguments():
    '''
    Returns a Namespace containing the cli args.
    '''
    
    parser = ArgumentParser(description='YouTube automated views farmer based on TOR.')
    parser.add_argument('-u', '--url', help='The url of the target YouTube video.', required=True)

    return parser.parse_args()

def verify_youtube_url(url: str) -> bool:
    '''
    Checks whether the passed url is a real YouTube video.
    '''
    
    if not url.find('https://www.youtube.com/watch?v=') == 0:
        return False

    if not requests.get(url).status_code in range(200, 300):
        return False

    return True

def get_error_message(err: str) -> str:
    '''
    Returns the error message corresponding to the passed error code (err).
    '''
    
    error_message = {
        'INVURL': 'The passed url is not valid.',
        'STRDIR': 'Could not create the storage directory... run the program again.',
        'DTADIR': 'Could not create the data directory... run the program again.'
    }
    
    return f'{Style.BRIGHT}{Fore.RED}Error: {error_message[err]}{Style.RESET_ALL}'

def start_application(url: str):
    socks_ports = [9050, 9052, 9054, 9056, 9058]
    threads = []

    create_storage_dir()

    for port in socks_ports:
        threads.append(RequestThread(url, port))
    
    for thread in threads:
        thread.start()

def clean_at_exit():
    '''
    Kills the TOR subprocesses.
    Removes the temporary storage directory and its subdirectories.
    '''

    # Killing subprocesses
    for pid in tor_pids:
        os.kill(pid, signal.SIGTERM)

    try:
        shutil.rmtree('/tmp/youtooler')
    except:
        pass

def main():
    print_logo()

    args = get_arguments()

    if verify_youtube_url(args.url):
        start_application(args.url)
    else:
        print(get_error_message('INVURL'), stderr)

if __name__ == '__main__':
    atexit.register(clean_at_exit) # Exit handler
    main()
