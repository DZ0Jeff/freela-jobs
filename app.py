from utils.setup import setSelenium
from utils.parser_handler import init_crawler
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    """
    Insert yout code here
    """
    soap = init_crawler('https://www.99freelas.com.br/projects?q=rob%C3%B4')
    job_list = soap.find('ul', class_="result-list")
    # print(job_list.prettify())
    for job in job_list.find_all('li'):
        # print(job.text)
        title = job.find('h1', class_="title").text
        client = job.find('p', class_="item-text client").text
        print(title)

if __name__ == "__main__":
    main()
