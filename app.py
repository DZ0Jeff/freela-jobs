import os
import schedule
import re
from time import sleep

from utils.telegram import TelegramBot
from utils.parser_handler import init_crawler, init_parser, remove_whitespaces
from utils.webdriver_handler import dynamic_page
from utils.setup import setSelenium
from utils.file_handler import save_to_html
from dotenv import load_dotenv

from src.database import DataStorage


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
job_storage = DataStorage()
FILTERS = ["bot", "robo", "scrapper", "robô", "robot", "telegram", "crawler", "scrap", "scrapy", "beautifulsoap",   "raspagem", "raspagem", "extração"]


def send_99freela(telegram):
    """
    Send 99freela jobs to telegram

    :telegram: => telegram client
    """
    print('> Iniciando 99 freela...')

    base_link = 'https://www.99freelas.com.br'
    page = 1
    success = 0

    while True:
        try:
            freela_99 = init_crawler(f'{base_link}/projects?categoria=web-mobile-e-software&page={page}')
            job_list = freela_99.find('ul', class_="result-list")
        
            print(f'> Página: {page}')
            print('> Pegando as informações...')

            for job in job_list.find_all('li'):
                data_links = job_storage.select_by_link()
                saved_links = [link[0] for link in data_links if link != None]

                title:str = job.find('h1', class_="title").text
                link:str = base_link + job.select_one('h1 a')['href']
                
                # check if contains the filtered word after extracting more items
                if re.compile('|'.join(FILTERS),re.IGNORECASE).search(r"\b{}\b".format(title.split())):
                    client:str = job.find('p', class_="item-text client").text
                    description:str = job.find('div', class_="item-text description formatted-text").text
                    
                    if not link in saved_links:
                        print('Inserindo no banco de dados...')
                        job_storage.insert(title, link, client, description)
                        success += 1

                        msg:str = f"\nTítulo: {remove_whitespaces(title)}\n\nCliente: {remove_whitespaces(client)}\n\nDescrição: {remove_whitespaces(description)}\n\nLink: {link}\n\n"
                        telegram.send_message(msg)

                else:
                    print('> Não existente no filtro ou ja extraído!', end="\r")

            page += 1

        except AttributeError:
            print('> Final da página alcançando!')
            break
    
    if success == 0:
        telegram.send_message('[99freela] Não há novos trabalhos disponíveis')


def send_workana(telegram):
    """
    Send workana jobs to telegram

    :telegram: => telegram client
    """
    print('Iniciando workana...')

    base_link_workana = "https://www.workana.com"
    page = 1
    breakpoint_pagination = ""
    success = 0

    while True:
        print(f'> página: {page}')
        workana = init_crawler(f'https://www.workana.com/jobs?category=it-programming&language=pt&page={page}')
        
        if not workana:
            print('Erro do site saindo...')
            return
        
        projects = workana.find('div', id="projects")
        
        print('> Pegando as informações...', end="\n")
        for project in projects.find_all('div', class_="project-item"):
            data_name = job_storage.select_by_name()
            saved_names = [name[0] for name in data_name if name != None]

            link = base_link_workana + project.find('a')['href']
            title = project.find('h2').text
            
            details = project.find('div', class_="html-desc project-details").get_text(separator=" ")
            
            # if 404 fails use the breakpoint to stop pagination
            if breakpoint_pagination == link:
                print('> Limite alcançado!')
                break
            else:
                breakpoint_pagination = link

                if not title in saved_names and re.compile('|'.join(FILTERS),re.IGNORECASE).search(r"\b{}\b".format(title.split())):
                    job_storage.insert(title, link, '', details)
                    workana_msg = f"Título: {remove_whitespaces(title)}\n\nDetalhes: {details}\n\nLink: {link}"
                    telegram.send_message(workana_msg)
                    success += 1

                else:
                    print('> Vaga já enviada!', end="\r")
        
        page += 1

    if success == 0:
        telegram.send_message('[Workana] Não há dados disponíveis')


def send_freelancer_com(telegram):


    def login(driver, email, password):
        driver.get('https://www.freelancer.com/login')
        driver.implicitly_wait(220)

        driver.find_element_by_css_selector('input[type="email"]').send_keys(email)
        driver.find_element_by_css_selector('input[type="password"]').send_keys(password)
        sleep(3)
        driver.find_element_by_css_selector('label.CheckboxLabel').click()
        sleep(3)
        driver.find_element_by_css_selector('button[type="submit"]').click()
        sleep(5)            


    def getTextFromTag(project, tag, class_name):
        try:
            return remove_whitespaces(project.find(tag, class_=class_name).text)

        except Exception:
            return ''


    success = 0
    with setSelenium() as driver:
        BASE_LINK = "https://www.freelancer.com"
        # "https://www.freelancer.com/jobs/?keyword=bot"
        projects = []

        print('> iniciando freelancer.com')
        load_dotenv(os.path.join(ROOT_DIR, '.env'))
        username = os.environ.get('FREELANCER_LOGIN')
        password = os.environ.get('FREELANCER_PASSWORD')

        login(driver, username, password)
        
        print('> extraíndo vagas')
        for job_target in FILTERS:
            print(f'> Pesquisando por: {job_target}')
            src_code = dynamic_page(driver, f'{BASE_LINK}/search/projects?q={job_target.lower()}')

            freelancer_com = init_parser(src_code)
            if not freelancer_com: continue
            
            projects = freelancer_com.find('ul', class_='search-result-list')

            if projects is None: continue

            for project in projects.find_all('li', recursive=False):
                
                dataname = job_storage.select_by_name()
                saved_name = [name[0] for name in dataname if name != None]

                title = getTextFromTag(project, 'h2', "info-card-title")
                try:
                    link = BASE_LINK + project.find('a', "search-result-link")['href']
                
                except Exception:
                    continue

                description = getTextFromTag(project, 'p', "info-card-description")
                price = getTextFromTag(project, 'div', "info-card-price")

                # add message to telegram and send it!
                if not title in saved_name:
                    job_storage.insert(title, link, '', description)
                    projects.append(link)
                    freelancer_msg = f"Título: {title}\n\nDetalhes: {description}\n\nLink: {link}\n\nPreço: {price}"
                    print(freelancer_msg)
                    # telegram.send_message(freelancer_msg)
                    success += 1

    if success == 0:
        telegram.send_message('[Freelancer.com] Não há dados disponíveis')

    print('> Finalizado!')


def send_upwork(telegram):
    

    def extract(link, success):
        print('> iniciando webdriver...')
        with setSelenium(False) as driver:
            src_code = dynamic_page(driver, link)
            upworks = init_parser(src_code)

        print('> extraíndo dados...')
        projects = upworks.select_one('div[data-ng-if="!moreResultsLoaded"]')

        if not projects: return

        for job in projects.select('div div section'):
            
            data_links = job_storage.select_by_link()
            saved_links = [link[0] for link in data_links if link != None]

            try:
                title = job.find('h4').text
                details = job.find('span', attrs={'data-ng-bind-html':'truncatedHtml'}).text
                link = BASE_LINK + job.find('h4').find('a')['href']
                type = remove_whitespaces(job.find('strong', class_="js-type text-muted").text)
            
            except Exception:
                print('> Error to extract job!')
                continue

            print(type)
            print(title)
            print(details)
            print(link)
            print('-' * 40)

            if re.compile('|'.join(FILTERS),re.IGNORECASE).search(r"\b{}\b".format(title.split())) and not link in saved_links:
                job_storage.insert(title, link, '', details)
                msg = f"\nTítulo: {title}\n\nDescrição: {details}\n\nLink: {link}\n\n"
                telegram.send_message(msg)
                success += 1


    BASE_LINK = "https://www.upwork.com"
    success = 0
    print('> iniciando upwork...')
    for i in FILTERS:
        extract(f'{BASE_LINK}/ab/jobs/search/t/1/?q={i.lower()}&sort=recency', success)
    
    if success == 0:
        telegram.send_message('[UPWorks] Não há dados disponíveis')
    
    print('> Finalizado!')


def main():
    """
    send freela jobs to telegram
    """
    print('> iniciando robô...', end="\n")
    telegram = TelegramBot(ROOT_DIR)

    # print('> extraíndo trabalhos...')
    send_99freela(telegram)
    send_workana(telegram)
    # send_freelancer_com(telegram)
    send_upwork(telegram)
    
    
if __name__ == "__main__":
    main()
    schedule.every().monday.at("12:30").do(main)
    schedule.every().wednesday.at("12:30").do(main)
    schedule.every().friday.at("12:30").do(main)

    while True:
        schedule.run_pending()
        print('Listening...', end="\r")
        sleep(1)
    
    