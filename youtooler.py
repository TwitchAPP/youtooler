import requests
from torrequest import TorRequest
from colorama import Fore, Back, Style
from argparse import ArgumentParser
from sys import stderr

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
def get_external_ip(session: TorRequest) -> str:
    return session.get('https://api64.ipify.org/?format=json').json()['ip']

# CLI args parser
def get_arguments():
    parser = ArgumentParser()
    parser.add_argument('-u', '--url', help='The url of the target YouTube video.', required=True)
    parser.add_argument('-l', '--level', help='The amount of concurrent sessions to run (MIN=1, MAX=5).', required=False)
    parser.add_argument('-p', '--proxy-port', help='Specify custom TOR proxy port.', required=False)
    parser.add_argument('-c', '--ctrl-port', help='Specify custom TOR control port.', required=False)
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
        'INVSES': 'The number of sessions specified is not valid (MIN=1, MAX=5).',
        'STPTOR': 'Another istance of TOR is running on the same port, stop it and re-launch the program.'
    }
    
    return f'Error: {error_message[err]}'

def main():
    print_logo()

    # CLI args parsing
    args = get_arguments()

if __name__ == '__main__':
    main()
