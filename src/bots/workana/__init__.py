import re
from scrapper_boilerplate import init_crawler, remove_whitespaces


def send_workana(telegram, options:dict, job_storage):
    """
    Send workana jobs to telegram

    :telegram: => telegram client
    """
    print('Iniciando workana...')

    base_link_workana = "https://www.workana.com"
    page = 1
    breakpoint_pagination = ""
    success = 0
    FILTERS = options['filters']

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
