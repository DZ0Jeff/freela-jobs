from utils.telegram import TelegramBot
from utils.setup import setSelenium
from utils.parser_handler import init_crawler, remove_whitespaces
import os
import schedule
from time import sleep


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def send_99freela(telegram):
    """
    Send 99freela jobs to telegram

    :telegram: => telegram client
    """
    freela_99 = init_crawler('https://www.99freelas.com.br/projects?q=rob%C3%B4')
    job_list = freela_99.find('ul', class_="result-list")
   
    print('> Pegando as informações...', end="\n")
    for job in job_list.find_all('li'):

        link = job.select_one('h1 a')['href']
        title = job.find('h1', class_="title").text
        client = job.find('p', class_="item-text client").text
        description = job.find('div', class_="item-text description formatted-text").text
        telegram.send_message(f"\nTítulo: {remove_whitespaces(title)}\n\nCliente: {remove_whitespaces(client)}\n\nDescrição: {remove_whitespaces(description)}\n\nLink: {link}\n\n")


def send_workana(telegram):
    """
    Send workana jobs to telegram

    :telegram: => telegram client
    """
    base_link_workana = "https://www.workana.com"
    workana = init_crawler('https://www.workana.com/jobs?category=it-programming&language=pt&query=Crawler')
    projects = workana.find('div', id="projects")
    
    print('> Pegando as informações...', end="\n")
    for project in projects.find_all('div', class_="project-item"):
    
        link = base_link_workana + project.find('a')['href']
        title = project.find('h2').text
        details = project.find('div', class_="html-desc project-details").get_text(separator=" ")

        workana_msg = f"Título: {remove_whitespaces(title)}\n\nDetalhes: {details}\n\nLink: {link}"
        telegram.send_message(workana_msg)


def main():
    """
    send freela jobs to telegram
    """
    telegram = TelegramBot(ROOT_DIR)

    print('> iniciando robô...', end="\n")
    send_99freela(telegram)
    send_workana(telegram)

    
if __name__ == "__main__":
    schedule.every().monday.at("12:00").do(main)
    schedule.every().wednesday.at("12:00").do(main)
    schedule.every().friday.at("12:00").do(main)

    while True:
        schedule.run_pending()
        print('Listening...', end="\r")
        sleep(1)
