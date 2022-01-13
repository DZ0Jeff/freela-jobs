import requests
from bs4 import BeautifulSoup
from requests.exceptions import InvalidSchema


def init_crawler(url):
    try:
        headers = {"User-agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"}

        page = requests.get(url, headers=headers)

        if page.status_code != 200:
            print(f'[ERRO {page.status_code}] Site indisponivel, tente novamente mais tarde')
            return

        return BeautifulSoup(page.text, "lxml")

    except InvalidSchema:
        print('Algo deu errado!')
        return

    except ConnectionError:
        print('Não conseguiu se conectar na página!')
        return

    except Exception:
        print('Algo deu errado :(')
        return

def init_parser(html):
    try:
        return BeautifulSoup(html, "lxml")

    except Exception:
        return


def remove_whitespaces(text):
    return ' '.join(text.split())