from scrapper_boilerplate import init_crawler



def send_toogit(telegram, job_storage, FILTERS):
    """
    Send jobs from toogit.com
    
    args:
        telegram: Telegram object
        job_storage: DataStorage object
        FILTERS: list of strings
    
    return:
        None
    """

    print('> Iniciando toogit...')
    success = 0


    def extract(telegram, success, url):
        BASE_URL = "https://www.toogit.com"
        print(f'> extraíndo {url}')
        soap = init_crawler(url)

        jobs = soap.find('div', id="sjl01").find_all('div', class_="job-item")
        # print(f'{len(jobs)} jobs found!')
        for job in jobs:
            data_links = job_storage.select_by_link()
            saved_links = [link[0] for link in data_links if link != None]

            data = {}
            try:
                data['title'] = job.find('h4').get_text()
            
            except AttributeError:
                continue
            
            data['date'] = job.find('div', class_='mb10').get_text()
            data['desc'] = job.find('div', class_='mb15 text-truncate-wrap').get_text()
            data['link'] = BASE_URL + job.find('a')['href']

            if not data['link'] in saved_links:
                job_storage.insert(data['title'], data['link'], '', data['desc'])
                msg = f"\nTítulo: {data['title']}\n\nDescrição: {data['desc']}\n\nLink: {data['link']}\n\n"
                telegram.send_message(msg)
                print(msg)
                print('\n')
                success += 1
        
        # pagination
        next_btn = soap.find('li', class_="next")
        if next_btn:
            next_link = next_btn.find('a')
            if next_link:
                next_url = next_link['href']
                print(f'Next page: {next_url}')
                send_toogit(telegram, BASE_URL + next_url)

        return success


    for job in FILTERS:
        success = extract(telegram, success, f'https://www.toogit.com/find-freelance-jobs?JobSearch%5B_q%5D=web+scrapping&JobSearch%5B_q%5D={job}')

    if success == 0:
        telegram.send_message('[Toogit] Não há vagas disponíveis e/ou ocorreu um erro!')
