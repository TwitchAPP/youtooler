import requests
from argparse import ArgumentParser
from sys import stderr

def tor_session():
    session = requests.Session()
    session.proxies = {
        'http': 'socks5://127.0.0.1:9050',
        'https': 'socks5://127.0.0.1:9050'
    }

    return session

def get_current_ip(session: requests.Session) -> str:
    return session.get('https://api64.ipify.org/?format=json').json()['ip']

def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument('-u', '--url', required=True)

    return parser.parse_args()

def verify_youtube_url(url: str) -> bool:
    if not url.find('https://www.youtube.com/watch?v=') == 0:
        return False

    if not requests.get(url).status_code in range(200, 300):
        return False

    return True

def get_error_message(err: str) -> str:
    error_message = {
        'INVURL': 'The passed url is not valid.'
    }
    
    return error_message[err]

def main():
    session = tor_session()
    args = parse_arguments()

    if not verify_youtube_url(args.url):
        print(get_error_message('INVURL'), file=stderr)
        exit()

    req = session.get(args.url)

    # print(req.text)
    print(get_current_ip(session))

if __name__ == '__main__':
    main()
