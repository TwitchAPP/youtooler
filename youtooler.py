import requests
import threading
import torrequest
from colorama import Fore, Back, Style
from argparse import ArgumentParser
from sys import stderr

class RequestThread(threading.Thread):
    def __init__(self, url: str, socksPort: int, controlPort: int):
        threading.Thread.__init__(self)
        self.url = url
        self.socksPort = socksPort
        self.controlPort = controlPort

    def run(self):
        print(f'{Style.BRIGHT}{Fore.GREEN}Creating a new Tor circuit on ports: socks={self.socksPort} control={self.controlPort}{Style.RESET_ALL}')

        with torrequest.TorRequest(self.socksPort, self.controlPort) as tor:
            while True:
                response = tor.get(self.url)
                
                if response.status_code in range(200, 300):
                    print(f'{Style.BRIGHT}{Fore.GREEN}Tor IP: {get_external_ip(tor)}, Request status: {response.status_code}{Style.RESET_ALL}')
                else:
                    print(f'{Style.BRIGHT}{Fore.GREEN}Tor IP: {get_external_ip(tor)}, Request status: {Fore.RED}{response.status_code}{Style.RESET_ALL}')

                tor.reset_identity()

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

# Returns the current external IPV4 address
def get_external_ip(tor: torrequest.TorRequest) -> str:
    return tor.get('http://ipecho.net/plain').text
    # return tor.get('https://api64.ipify.org/?format=json').json()['ip']

# CLI args parser
def get_arguments():
    parser = ArgumentParser(description='YouTube automated views farmer based on TOR.')
    
    parser.add_argument('-u', '--url', help='The url of the target YouTube video.', required=True)
    parser.add_argument('-l', '--level', help='The amount of concurrent sessions to run (MIN=1, MAX=5).', required=False)
    parser.add_argument('-a', '--auth', help='Include this flag if you have TOR protected by a password.', required=False)

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
    config = [
        { 'SOCKS': 9050, 'CONTROL': 9051 },
        { 'SOCKS': 9052, 'CONTROL': 9053 },
        { 'SOCKS': 9054, 'CONTROL': 9055 },
        { 'SOCKS': 9056, 'CONTROL': 9057 },
        { 'SOCKS': 9058, 'CONTROL': 9059 },
    ]

    threads = []
    
    if not level in range(1, 6):
        print(get_error_message('INVLVL'), file=stderr)
        exit()

    for i in range(level):
        threads.append(RequestThread(url=url, socksPort=config[i]['SOCKS'], controlPort=config[i]['CONTROL']))
        threads[i].start()

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
    main()
