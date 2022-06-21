import atexit
import os
import random
import requests
import requests_random_user_agent
import shutil
import threading
import time
from argparse import ArgumentParser
from colorama import Fore, Back, Style
from sys import stderr

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
        # Starting new TOR instance on the specified socks_port
        torrc_path = create_temp_torrc(self.socks_port)
        os.system(f'tor -f {torrc_path} > /dev/null &')

        print(f'{Style.BRIGHT}{Fore.GREEN}Created a new Tor circuit on socks port: {self.socks_port}{Style.RESET_ALL}')

        while True:
            # Proxying requests through TOR
            session = requests.Session()
            session.proxies = {
                'http': f'socks5://127.0.0.1:{self.socks_port}',
                'https': f'socks5://127.0.0.1:{self.socks_port}'
            }

            try:
                response = session.get(self.url)
            except:
                pass
            else:
                if response.status_code in range(200, 300):
                    print(f'{Style.BRIGHT}{Fore.GREEN}Tor IP: {get_external_ip(session)}\t|   Request status: {response.status_code}{Style.RESET_ALL}')
                else:
                    print(f'{Style.BRIGHT}{Fore.GREEN}Tor IP: {get_external_ip(session)}\t|   Request status: {Fore.RED}{response.status_code}{Style.RESET_ALL}')

            # Sleeping between 5 and 10 seconds
            time.sleep(random.uniform(5, 10))

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

def create_temp_torrc(socks_port: int) -> str:
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

def get_external_ip(session: requests.Session) -> str:
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

    for _ in apis:
        api = random.choice(apis)
        response = session.get(api)
        
        if response.status_code in range(200, 300):
            return response.text.strip()
        else: # Removing API if not working
            apis.pop(apis.index(api))

def get_arguments():
    parser = ArgumentParser(description='YouTube automated views farmer based on TOR.')
    
    parser.add_argument('-u', '--url', help='The url of the target YouTube video.', required=True)
    parser.add_argument('-l', '--level', help='The amount of concurrent sessions to run (MIN=1, MAX=5).', required=False)

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
        'INVLVL': 'The number of sessions specified is not valid (MIN=1, MAX=5).',
        'STRDIR': 'Could not create the storage directory... run the program again.',
        'DTADIR': 'Could not create the data directory... run the program again.'
    }
    
    return f'{Style.BRIGHT}{Fore.RED}Error: {error_message[err]}{Style.RESET_ALL}'

def start_application(url: str, level: int=1):
    socks_ports = [9050, 9052, 9054, 9056, 9058]
    threads = []

    create_storage_dir()

    if not level in range(1, 6):
        print(get_error_message('INVLVL'), file=stderr)
        exit()

    for i in range(level):
        threads.append(RequestThread(url, socks_ports[i]))
        threads[i].start()

def clean_at_exit():
    '''
    Removes the temporary storage directory and its subdirectories.
    '''

    try:
        shutil.rmtree('/tmp/youtooler')
    except:
        pass

def main():
    print_logo()

    args = get_arguments()

    if verify_youtube_url(args.url):
        start_application(args.url, int(args.level))
    else:
        print(get_error_message('INVURL'), stderr)

if __name__ == '__main__':
    atexit.register(clean_at_exit) # Exit handler
    main()
