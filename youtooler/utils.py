import os
import requests
from argparse import ArgumentParser
from colorama import Fore, Style
from sys import stderr

def create_storage_dir() -> str:
    '''
    Creates the temporary storage directory of the program ('/tmp/youtooler') and returns its path.
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
    
    parser = ArgumentParser(description='YouTube auto-viewer BOT based on TOR.')
    parser.add_argument('-u', '--url', help='The url of the target YouTube video.', required=True)

    return parser.parse_args()

def get_error_message(err: str) -> str:
    '''
    Returns the error message corresponding to the passed error code.
    '''
    
    error_message = {
        'INVURL': 'The passed url is not valid.',
        'STRDIR': 'Could not create the storage directory... run the program again.',
        'DTADIR': 'Could not create the data directory... run the program again.'
    }
    
    return f'{Style.BRIGHT}{Fore.RED}Error: {error_message[err]}{Style.RESET_ALL}'

def verify_youtube_url(url: str) -> bool:
    '''
    Checks whether the passed url is a real YouTube video or not.
    '''
    
    if not url.find('https://www.youtube.com/watch?v=') == 0:
        return False

    if not requests.get(url).status_code in range(200, 300):
        return False

    return True
