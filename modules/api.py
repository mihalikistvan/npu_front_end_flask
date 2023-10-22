import requests
from requests.auth import HTTPBasicAuth
import os
base_url = os.getenv('base_url')


class api_connection():

    def __init__(self):
        self.base_url = os.getenv('base_url')
        self.headers = {'Accept': 'application/json', 'x-api-key':os.getenv('api_key')}

    def search_creations(self):
        response = requests.get(url=self.base_url+'creations')
        return response.json()
    
    def search_one_creation(self):
        response = requests.get(url=self.base_url+f'creations')
        return response.json()[0]['brick_dict']
    
    def search_creations_by_bricks(self,brick_name):
        response = requests.get(url=self.base_url+f'creation_by_bricks/{brick_name}')
        return response.json()
    
    def search_one_creation(self,creation_id):
        response = requests.get(url=self.base_url+f'creations/{creation_id}')
        return response.json()

    def search_creation_ratings(self,creation_id):
        response = requests.get(url=self.base_url+f'ratings/{creation_id}')
        return response.json()

    def add_rating(self,creation_id,uniqueness,creativity,rated_by):
        url=self.base_url+f'ratings/{creation_id}'
        data={
            'uniqueness':uniqueness,
            'creativity':creativity,
            'rated_by':rated_by
        }
        resp = requests.post(url=url, headers=self.headers, data=data) 
        return resp.json()
    
    def search_bricks(self):
        response = requests.get(url=self.base_url+'bricks')
        return response.json()[0]['brick_dict']

    def upload(self, form,files,email):
        url = self.base_url+'upload'
        files = {'file': (files.filename,files.read())}
        data ={'creation_name':form.get('creation_name'),
                'description': form.get('creation_description'),
                'user_email':email,
                'bricks':form.getlist('brick_list')}
        resp = requests.post(url=url, headers=self.headers, files=files,data=data) 
        print(resp.json())
