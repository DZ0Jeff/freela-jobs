from scrapper_boilerplate import init_crawler, remove_whitespaces

import re


def send_99freela(telegram, options:dict, job_storage):
    """
    Send 99freela jobs to telegram

    :telegram: => telegram client
    """
    print('> Iniciando 99 freela...')

    base_link = 'https://www.99freelas.com.br'
    page = 1
    success = 0
    FILTERS = options['filters']

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
