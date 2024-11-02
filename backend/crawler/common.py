from typing import Optional
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError

import requests

domain = 'https://me.pusan.ac.kr'

from bs4 import BeautifulSoup

def fetch(path: str) -> Optional[BeautifulSoup]:
    try:
        test = len(path) == 0 or path.startswith('/')
        _path = path if test else f'/{path}'

        response = requests.get(f'{domain}{_path}', timeout = 3.0)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            return soup

    except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
        return
