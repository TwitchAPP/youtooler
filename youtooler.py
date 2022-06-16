import requests
from colorama import Fore, Style
from argparse import ArgumentParser
from sys import stderr
from os import system

# Prints the logo and description
def print_logo():
    print(f'{Style.BRIGHT}')
    print(f'{Fore.MAGENTA} _____.___.           {Fore.RED}___________           .__                ')
    print(f'{Fore.MAGENTA}\\__  |   | ____  __ _{Fore.RED}\\__    ___/___   ____ |  |   {Fore.MAGENTA}___________ ')
    print(f'{Fore.MAGENTA} /   |   |/  _ \\|  |  \\{Fore.RED}|    | /  _ \\ /  _ \\|  | {Fore.MAGENTA}_/ __ \\_  __ \\')
    print(f'{Fore.YELLOW} \\____   (  <_> )  |  /{Fore.RED}|    |(  <_> |  <_> )  |_{Fore.YELLOW}\\  ___/|  | \\/')
    print(f'{Fore.YELLOW} / ______|\\____/|____/ {Fore.RED}|____| \\____/ \\____/|____/{Fore.YELLOW}\\___  >__|   ')
    print(f'{Fore.YELLOW} \\/                                                  {Fore.YELLOW}\\/       ')
    print(f'{Style.RESET_ALL}')

# Returns an array of requests.Session() objects proxied using tor
def tor_sessions(nOfSessions: int=1):
    SOCKS_PORTS = [9050, 9060, 9070, 9080, 9090]
    sessions = []
    
    if not nOfSessions in range(1, 6): # Max of 5 concurrent sessions
        print(get_error_message('INVSES'))
        exit()

    system('sudo systemctl stop tor.service')

    for i in range(nOfSessions):
        system(f'tor -f ./conf/torrc.{i}')

        sessions.append(requests.Session())
        sessions[i].proxies = {
            'http': f'socks5://127.0.0.1:{SOCKS_PORTS[i]}',
            'https': f'socks5://127.0.0.1:{SOCKS_PORTS[i]}'
        }

    return sessions

# Returns the current external IPV4 address
def get_external_ip(session: requests.Session) -> str:
    return session.get('https://api64.ipify.org/?format=json').json()['ip']

# CLI args parser
def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument('-u', '--url', required=True)
    parser.add_argument('-s', '--sessions', required=False)

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
        'INVSES': 'The number of sessions specified is not valid (MIN=1, MAX=5).'
    }
    
    return f'Error: {error_message[err]}'

def main():
    print_logo()

    args = parse_arguments()

    # if not args.sessions == None:
    #     sessions = tor_sessions(int(args.sessions))
    # else:
    #     sessions = tor_sessions()

    # if not verify_youtube_url(args.url):
    #     print(get_error_message('INVURL'), file=stderr)
    #     exit()

    # for session in sessions:
    #     print(get_external_ip(session))

if __name__ == '__main__':
    main()
