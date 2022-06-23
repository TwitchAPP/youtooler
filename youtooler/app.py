import atexit
import shutil
from colorama import Fore, Back, Style
from youtooler.thread import RequestThread

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

def start_application(url: str):
    socks_ports = [9050, 9052, 9054, 9056, 9058]
    threads = []

    atexit.register(clean_at_exit) # Exit handler

    for port in socks_ports:
        threads.append(RequestThread(url, port))
    
    for thread in threads:
        thread.start()

def clean_at_exit():
    '''
    Removes the temporary storage directory and its subdirectories.
    '''

    try:
        shutil.rmtree('/tmp/youtooler')
    except:
        pass
