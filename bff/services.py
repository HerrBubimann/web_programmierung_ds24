import requests
from bff.TokenManager import token_manager

API_BASE_URL = 'http://localhost:5001'

def get_auth_token(user_id):
    return token_manager.get_or_create_token(user_id)

def get_topics(user_id):
    token = get_auth_token(user_id)
    try:
        session = requests.Session()
        session.cookies.set('auth_token', token)
        response = session.get(f'{API_BASE_URL}/topics')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen der Themen: {e}")
        return None

def get_learning_goals(user_id):
    token = get_auth_token(user_id)
    try:
        session = requests.Session()
        session.cookies.set('auth_token', token)
        response = session.get(f'{API_BASE_URL}/learning-goals')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen der Lernziele: {e}")
        return None

def create_topic(user_id, name, priority='medium'):
    token = get_auth_token(user_id)
    try:
        session = requests.Session()
        session.cookies.set('auth_token', token)
        response = session.post(
            f'{API_BASE_URL}/topics',
            json={'name': name, 'priority': priority}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Erstellen des Themas: {e}")
        return None

def create_learning_goal(user_id, topic_id, description, deadline):
    token = get_auth_token(user_id)
    try:
        session = requests.Session()
        session.cookies.set('auth_token', token)
        response = session.post(
            f'{API_BASE_URL}/learning-goals',
            json={'topic_id': topic_id, 'description': description, 'deadline': deadline}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Erstellen des Lernziels: {e}")
        return None