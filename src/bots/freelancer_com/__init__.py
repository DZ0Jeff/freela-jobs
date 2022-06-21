import os

from utils.webdriver_handler import explicit_wait
from scrapper_boilerplate import setSelenium, init_parser, remove_whitespaces

from time import sleep
from dotenv import load_dotenv

from selenium.webdriver.common.by import By


load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))


def getTextFromTag(project, tag, class_name):
    """
    Get text from tag

    args:
        project: html tag
        tag: html tag
        class_name: class name
    return:
        text: text from tag
    """
    try:
        return remove_whitespaces(project.find(tag, class_=class_name).text)

    except Exception:
        return ''


def login(driver, email, password):
    """
    Login to freelancer.com
    
    args:
        driver: webdriver
        email: email
        password: password
    return:
        True: if login is successful
    """


    if not(email, password) or (email, password) == "":
        print("Email e/ou senha vázios!, insira email e/ou senha!")
        return 

    driver.get('https://www.freelancer.com/login')
    driver.implicitly_wait(220)

    driver.find_element_by_css_selector('input[type="email"]').send_keys(email)
    driver.find_element_by_css_selector('input[type="password"]').send_keys(password)
    sleep(3)
    driver.find_element_by_css_selector('label.CheckboxLabel').click()
    sleep(3)
    driver.find_element_by_css_selector('button[type="submit"]').click()
    sleep(5)      
    return True      


def send_freelancer_com(telegram, options:dict, job_storage):
    """
    Send jobs from freelancer.com
    
    args:
        telegram: telegram bot
        options: options
        job_storage: job storage
    
    return:
        True: if send is successful
    """

    FILTERS = options['filters']
    REMOTE = options['remote']
    HEADLESS = options['headless']

    success = 0
    with setSelenium(headless=HEADLESS, remote_webdriver=REMOTE) as driver:
        BASE_LINK = "https://www.freelancer.com"
        # "https://www.freelancer.com/jobs/?keyword=bot"
        projects = []

        print('> iniciando freelancer.com')
        username = os.environ.get('FREELANCER_LOGIN')
        password = os.environ.get('FREELANCER_PASSWORD')

        status_login = login(driver, username, password)
        if not status_login: 
            print("> erro de login!")
            return
        
        print('> extraíndo vagas')
        for job_target in FILTERS:
            print(f"> Pesquisando por: {BASE_LINK}/search/projects?q={job_target.lower()}&status=open")
            # src_code = dynamic_page(driver, f'{BASE_LINK}/search/projects?q={job_target.lower()}')
            driver.get(f'{BASE_LINK}/search/projects?q={job_target.lower()}')
            
            waiter = explicit_wait(driver, By.XPATH, '/html/body/app-root/app-logged-in-shell/div/fl-container/div/div/app-search/app-search-projects/fl-bit/fl-container/fl-bit/fl-bit[2]/app-search-results/fl-card/fl-bit/fl-bit[2]/app-search-results-projects/fl-bit/fl-list')
            
            
            print("> parsing...")
            # find why projects is returning none
            if waiter is None: 
                print('> Elemento não achado!')
                continue

            projects = waiter.find_elements_by_css_selector('fl-list-item.ng-star-inserted')
            if len(projects) == 0: continue

            for project in projects:
                
                dataname = job_storage.select_by_name()
                saved_name = [name[0] for name in dataname if name != None]

                title = explicit_wait(driver, By.CSS_SELECTOR, 'fl-text.Project-title')
                
                if title: title.text 

                try:
                    link = BASE_LINK + project.find_element_by_css_selector("a.LinkElement")['href']
                
                except Exception:
                    raise

                description = project.find_element_by_css_selector('fl-text.Project-secondary-description').text 
                price = waiter.find_element_by_css_selector('fl-bit.Project-budget').text 

                # add message to telegram and send it!
                if not title in saved_name:
                    job_storage.insert(title, link, '', description)
                    projects.append(link)
                    freelancer_msg = f"Título: {title}\n\nDetalhes: {description}\n\nLink: {link}\n\nPreço: {price}"
                    print(freelancer_msg)
                    telegram.send_message(freelancer_msg)
                    success += 1

    if success == 0:
        telegram.send_message('[Freelancer.com] Não há dados disponíveis')

    print('> Finalizado!')
