import random
import threading
import time
from colorama import Fore, Style
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from youtooler.tor import Tor
from webdriver_manager.chrome import ChromeDriverManager

class RequestThread(threading.Thread):
    '''
    Extends threading.Thread\n
    Takes the target YouTube url and the socks_port for TOR as parameters.\n
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
                tor.start_tor()
            except:
                print(f'{Style.BRIGHT}{Fore.GREEN}Failed while creating a new Tor circuit on socks_port: {self.socks_port}{Style.RESET_ALL}')
                exit()
            else:
                print(f'{Style.BRIGHT}{Fore.GREEN}Created a new Tor circuit on socks_port: {self.socks_port}{Style.RESET_ALL}')

            try:
                driver.get(f'{self.url}&t={random.randint(1, 300)}s')
            except:
                print(f'{Style.BRIGHT}{Fore.RED}Unsuccessful request made by {self.name} | Tor IP: {tor.get_external_address()}{Style.RESET_ALL}')
            else:
                print(f'{Style.BRIGHT}{Fore.GREEN}Successful request made by {self.name} | Tor IP: {tor.get_external_address()}{Style.RESET_ALL}')

            # Killing subprocess in order to create a new TOR circuit
            tor.kill_tor()
            print(f'{Style.BRIGHT}{Fore.YELLOW}Closing Tor circuit on socks_port: {self.socks_port}{Style.RESET_ALL}')

            driver.delete_all_cookies()

            time.sleep(random.uniform(20, 30))
