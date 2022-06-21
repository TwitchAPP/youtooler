import atexit
import requests
import threading
import random
import time
import shutil
from colorama import Fore, Back, Style
from argparse import ArgumentParser
from sys import stderr
from os import system, mkdir

class RequestThread(threading.Thread):
    def __init__(self, url: str, socks_port: int):
        threading.Thread.__init__(self)
        self.url = url
        self.socks_port = socks_port

    def run(self):
        torrc_path = create_temp_torrc(self.socks_port)

        system(f'tor -f {torrc_path} > /dev/null &')

        print(f'{Style.BRIGHT}{Fore.GREEN}Created a new Tor circuit on port: socks={self.socks_port}{Style.RESET_ALL}')

        # Binding session proxies to tor
        session = requests.Session()
        session.proxies = {
            'http': f'socks5://127.0.0.1:{self.socks_port}',
            'https': f'socks5://127.0.0.1:{self.socks_port}'
        }

        # Request cycle
        while True:
            try:
                response = session.get(self.url)
            except:
                pass

            if response.status_code in range(200, 300):
                print(f'{Style.BRIGHT}{Fore.GREEN}Tor IP: {get_external_ip(session)}\t|   Request status: {response.status_code}{Style.RESET_ALL}')
            else:
                print(f'{Style.BRIGHT}{Fore.GREEN}Tor IP: {get_external_ip(session)}\t|   Request status: {Fore.RED}{response.status_code}{Style.RESET_ALL}')

            # Sleeping from 5 to 10 seconds
            rand_sleep = random.uniform(5, 10)
            time.sleep(rand_sleep)

# Prints the logo and description
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

# Creates a temporary torrc file
def create_temp_torrc(socks_port: int) -> str:
    TORRC_PATH = f'/tmp/youtooler/torrc.{socks_port}'
    DATA_DIR = f'/tmp/youtooler/{socks_port}'

    try:
        mkdir('/tmp/youtooler/')
    except:
        pass
    
    try:
        mkdir(DATA_DIR)
    except:
        pass

    with open(TORRC_PATH, 'w') as torrc:
        torrc.write(f'SocksPort {socks_port}\nDataDirectory {DATA_DIR}')
        torrc.close()

    return TORRC_PATH

# Returns the current external IPV4 address
def get_external_ip(session: requests.Session) -> str:
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

# CLI args parser
def get_arguments():
    parser = ArgumentParser(description='YouTube automated views farmer based on TOR.')
    
    parser.add_argument('-u', '--url', help='The url of the target YouTube video.', required=True)
    parser.add_argument('-l', '--level', help='The amount of concurrent sessions to run (MIN=1, MAX=5).', required=False)

    return parser.parse_args()

# Checks if 'url' is an existing YouTube video
def verify_youtube_url(url: str) -> bool:
    if not url.find('https://www.youtube.com/watch?v=') == 0:
        return False

    if not requests.get(url).status_code in range(200, 300):
        return False

    return True

# Print the error message corresponding to 'err'
def get_error_message(err: str) -> str:
    error_message = {
        'INVURL': 'The passed url is not valid.',
        'INVLVL': 'The number of sessions specified is not valid (MIN=1, MAX=5).'
    }
    
    return f'{Style.BRIGHT}{Fore.RED}Error: {error_message[err]}{Style.RESET_ALL}'

def start_application(url: str, level: int=1):
    socks_ports = [9050, 9052, 9054, 9056, 9058]
    threads = []
    
    if not level in range(1, 6):
        print(get_error_message('INVLVL'), file=stderr)
        exit()

    for i in range(level):
        threads.append(RequestThread(url, socks_ports[i]))
        threads[i].start()

def clean_at_exit():
    try:
        shutil.rmtree('/tmp/youtooler')
    except:
        pass

def main():
    # Startup
    print_logo()

    # CLI args parsing
    args = get_arguments()

    if verify_youtube_url(args.url):
        start_application(args.url, int(args.level))
    else:
        print(get_error_message('INVURL'), stderr)

if __name__ == '__main__':
    # Exit handler
    atexit.register(clean_at_exit)
    main()
