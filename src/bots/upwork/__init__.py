import re
from scrapper_boilerplate import setSelenium, init_parser, remove_whitespaces
from utils.webdriver_handler import dynamic_page

from time import sleep


def send_upwork(telegram, job_storage, FILTERS, HEADLESS, REMOTE):
    

    def extract(link, success):
        print('> iniciando webdriver...')

        try:
            driver = setSelenium(headless=HEADLESS, remote_webdriver=REMOTE) 

        except Exception:
            sleep(10)
            driver = setSelenium(headless=HEADLESS, remote_webdriver=REMOTE)

        with driver:
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
