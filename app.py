from utils.telegram import TelegramBot
from utils.setup import setSelenium
from utils.parser_handler import init_crawler, remove_whitespaces
import os
import schedule
from time import sleep


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    """
    Insert yout code here
    """
    telegram = TelegramBot(ROOT_DIR)

    print('> iniciando robô...', end="\n")
    soap = init_crawler('https://www.99freelas.com.br/projects?q=rob%C3%B4')
    job_list = soap.find('ul', class_="result-list")
    # print(job_list.prettify())

    # jobs_to_send = []
    print('> Pegando as informações...', end="\n")
    for job in job_list.find_all('li'):
        # print(job.text)
        link = job.select_one('h1 a')['href']
        title = job.find('h1', class_="title").text
        client = job.find('p', class_="item-text client").text
        description = job.find('div', class_="item-text description formatted-text").text

        # print('-'*60)
        # print('Link: ',link)
        # print('Título: ',title)
        # print('Descrição: ',remove_whitespaces(description))
        # print('Cliente: ', remove_whitespaces(client))
        # print('\n') 
        telegram.send_message(f"\nTítulo: {remove_whitespaces(title)}\n\nCliente: {remove_whitespaces(client)}\n\nDescrição: {remove_whitespaces(description)}\n\nLink: {link}\n\n")


if __name__ == "__main__":
    schedule.every().day.at("09:00").do(main)

    while True:
        schedule.run_pending()
        print('Listening...', end="\r")
        sleep(1)
