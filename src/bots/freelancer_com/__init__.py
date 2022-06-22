import requests
import os
import re
from dotenv import load_dotenv

from scrapper_boilerplate import save_to_json


class FreelancerCom:

    BASE_URL = "https://www.freelancer.com"

    def __init__(self, session, telegram, job_storage, filters):
        self.telegram = telegram
        self.job_storage = job_storage
        self.request = session
        self.FILTERS = filters
        load_dotenv()

    def load_last_jobs(self):
        data_links = self.job_storage.select_by_link()
        saved_links = [link[0] for link in data_links if link != None]
        return saved_links

    def login(self):

        email = os.environ.get('FREELANCER_LOGIN')
        password = os.environ.get('FREELANCER_PASSWORD')

        url = "https://www.freelancer.com/ajax-api/auth/login.php"

        querystring = {"compact":"true","new_errors":"true","new_pools":"true"}

        payload = { 
            "user": email, 
            "password": password, 
            "device_token" : "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInN2IjoiMSJ9.eyJpc3MiOiJmcmVlbGFuY2VyLmNvbS9hdXRoIiwiaWF0IjoxNjU1ODM4NDEwLCJkZXZpY2VfaWQiOiJyc044SFQvdW9mY2lHbFlnblFFNEVvV0VmeHBWSTB6UyIsInR5cGUiOiJkZXZpY2UtdG9rZW4ifQ.cyegkXhJKNTd4dCQEDk3k6gDJXMCUKIMKlXXhES7t-I",
            "captcha": ''
        }
        headers = {
            "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        }

        response = self.request.post(url, data=payload, headers=headers, params=querystring)

        if response.status_code != 200:
            print(f"Erro: {response.status_code}")
            print('> erro ao realizar o login!')
            return

        return response.json()

    def get_jobs(self, search="", limit=10):

        url = "https://www.freelancer.com/api/projects/0.1/projects/active"

        querystring = {"limit":limit,"offset":"0","full_description":"true","job_details":"true","local_details":"true","location_details":"true","upgrade_details":"true","query":search,"sort_field":"submitdate","compact":"true","new_errors":"true","new_pools":"true"}

        headers = {
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        }

        response = self.request.get(url, headers=headers, params=querystring)

        if response.status_code != 200:
            print(f"Erro: {response.status_code}")
            print('> erro ao realizar o login!')
            return

        return response.json()

    def get_profile(self, user_id):

        url = "https://www.freelancer.com/api/users/0.1/users"

        querystring = {
            "users[]": user_id,
            "avatar":"true",
            "online_offline_details":"true",
            "status":"true",
            "support_status_details":"true",
            "limited_account":"true",
            "webapp":"1",
            "compact":"true",
            "new_errors":"true",
            "new_pools":"true"
        }

        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"}

        response = self.request.get(url, headers=headers, params=querystring)

        if response.status_code != 200:
            print(f"Erro: {response.status_code}")
            print('> erro ao realizar o login!')
            return

        print(response.json())
        return response.json()

    def parser(self, data):
        for projects in data['result']['projects']:
            status = projects['status']
            if status != 'active': continue

            saved_links = self.load_last_jobs()
            link = self.BASE_URL + "/projects/" + projects['seo_url'] 
            if link in saved_links: continue

            title = projects['title']
            if not re.compile('|'.join(self.FILTERS),re.IGNORECASE).search(r"\b{}\b".format(title.split())): continue
            description = projects['description']

            msg = f"Título: {title}\n\nDescrição: {description}\nLink: {link}"
            print(msg)
            print("\n\n")
            self.telegram.send_message(msg)
            self.job_storage.insert(title, link, '', description)


def send_freelancer_com(telegram, filters, job_storage):
    """
    send freela jobs to telegram
    """

    with requests.Session() as session:
        freelacer_com = FreelancerCom(session, telegram, job_storage, filters)
        for filter in filters:
            print(f"> getting for {filter}...")
            data = freelacer_com.get_jobs(filter.lower().replace(" ", "-"))
            freelacer_com.parser(data)
