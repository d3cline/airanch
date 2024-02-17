from celery import shared_task
import requests
from django.conf import settings


@shared_task
def create_tunnel_port(id):
    #url = f'{API_BASE_URL}/osuser/'
    #headers = {'Authorization': f'Token {settings.OPALSTACK_API_KEY}'}
    #payload = {'username': username, 'email': email, 'password': password}
    #response = requests.post(url, headers=headers, json=payload)
    #return response.json()
    print(id)
    return id
