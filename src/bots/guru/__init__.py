from scrapper_boilerplate import setSelenium, init_parser, log, remove_whitespaces


def send_guru(telegram, job_storage, options:dict):
    print('> Iniciando guru...')
    success = 0

    HEADLESS = options['headless']
    REMOTE= options['remote']
    FILTERS= options['filters']

    for jobs in FILTERS:
        
        print(f"> extracting jobs...\nhttps://www.guru.com/jobs/search?q={jobs}")
        with setSelenium(headless=HEADLESS, remote_webdriver=REMOTE) as driver:
            driver.get(f'https://www.guru.com/jobs/search?q={jobs}')
            soap = init_parser(driver.page_source)

        container = soap.find('ul', class_="module_list cozy")

        # if not container: continue

        print("> parsing jobs...")
        for item in container.find_all('li'):
            data_links = job_storage.select_by_link()
            saved_links = [link[0] for link in data_links if link != None]

            try:
                title = item.find('h2', class_="jobRecord__title").text

            except AttributeError:
                continue

            link = "https://www.guru.com" + item.select_one('h2 a')['href']
            description = item.find('p', class_="jobRecord__desc").text
            client = item.find('div', class_="avatarinfo").text

            if not link in saved_links:
                job_storage.insert(title, link, client, description)
                msg = f"\nTítulo: {remove_whitespaces(title)}\n\nDescrição: {remove_whitespaces(description)}\n\nLink: {remove_whitespaces(link)}\n\nCliente: {remove_whitespaces(client)}\n\n"
                log(msg)
                telegram.send_message(msg)
                success += 1
    
    if success == 0:
        telegram.send_message('[Guru] Não há vagas disponíveis e/ou ocorreu um erro!')
