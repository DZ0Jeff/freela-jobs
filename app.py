# from utils.running import load_status, write_status
from bs4 import BeautifulSoup
from sqlalchemy.sql.expression import true
from utils.telegram import TelegramBot
from utils.parser_handler import init_crawler, remove_whitespaces
import os
from time import sleep
import schedule
import re
from src.database import DataStorage


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
job_storage = DataStorage()
FILTERS = ["bot", "robo", "scrapper", "robô", "telegram", "crawler", "scrap", "scrapy", "beautifulsoap", "raspagem", "raspagem", "extração"]


def send_99freela(telegram, saved_links):
    """
    Send 99freela jobs to telegram

    :telegram: => telegram client
    """
    print('> Iniciando 99 freela...')

    base_link = 'https://www.99freelas.com.br'
    page = 1

    while True:
        try:
            freela_99 = init_crawler(f'{base_link}/projects?categoria=web-mobile-e-software&page={page}')
            job_list = freela_99.find('ul', class_="result-list")
        
            print(f'> Página: {page}')
            print('> Pegando as informações...')

            for job in job_list.find_all('li'):
                title:str = job.find('h1', class_="title").text
                link:str = base_link + job.select_one('h1 a')['href']
                
                # check if contains the filtered word after extracting more items
                if re.compile('|'.join(FILTERS),re.IGNORECASE).search(r"\b{}\b".format(title.split())):
                    client:str = job.find('p', class_="item-text client").text
                    description:str = job.find('div', class_="item-text description formatted-text").text
                    
                    if not link in saved_links:
                        print('Inserindo no banco de dados...')
                        job_storage.insert(title, link, client, description)

                        msg:str = f"\nTítulo: {remove_whitespaces(title)}\n\nCliente: {remove_whitespaces(client)}\n\nDescrição: {remove_whitespaces(description)}\n\nLink: {link}\n\n"
                        telegram.send_message(msg)

                else:
                    print('> Não existente no filtro ou ja extraído!', end="\r")

            page += 1

        except AttributeError:
            print('> Final da página alcançando!')
            break


def send_workana(telegram, saved_links):
    """
    Send workana jobs to telegram

    :telegram: => telegram client
    """
    print('Iniciando workana...')

    base_link_workana = "https://www.workana.com"
    page = 1
    breakpoint_pagination = ""

    while True:
        # workana = init_crawler('https://www.workana.com/jobs?category=it-programming&language=pt&query=Crawler')
        print(f'> página: {page}')
        workana = init_crawler(f'https://www.workana.com/jobs?category=it-programming&language=pt&page={page}')
        
        if not workana:
            print('Erro do site saindo...')
            return
        
        projects = workana.find('div', id="projects")
        
        print('> Pegando as informações...', end="\n")
        for project in projects.find_all('div', class_="project-item"):

            link = base_link_workana + project.find('a')['href']
            title = project.find('h2').text
            if re.compile('|'.join(FILTERS),re.IGNORECASE).search(r"\b{}\b".format(title.split())):
                details = project.find('div', class_="html-desc project-details").get_text(separator=" ")
                
                # if 404 fails use the breakpoint to stop pagination
                if breakpoint_pagination == link:
                    print('> Limite alcançado!')
                    break
                else:
                    breakpoint_pagination = link

                if not link in saved_links and link != '':
                    job_storage.insert(title, link, '', details)
                    workana_msg = f"Título: {remove_whitespaces(title)}\n\nDetalhes: {details}\n\nLink: {link}"
                    telegram.send_message(workana_msg)

            else:
                print('> Vaga já enviada!', end="\r")
        
        page += 1


def main():
    """
    send freela jobs to telegram
    """
    print('> iniciando robô...', end="\n")
    telegram = TelegramBot(ROOT_DIR)
    links = job_storage.select_by_link()
    saved_links = [link[0] for link in links if link != None]

    print('> extraíndo trabalhos...')
    send_99freela(telegram, saved_links)
    send_workana(telegram, saved_links)
    
    
if __name__ == "__main__":
    schedule.every().monday.at("12:00").do(main)
    schedule.every().wednesday.at("12:00").do(main)
    schedule.every().friday.at("12:00").do(main)

    while True:
        schedule.run_pending()
        print('Listening...', end="\r")
        sleep(1)

    