import requests

API_BASE_URL = 'http://localhost:5000'

def get_topics():
    response = requests.get(f'{API_BASE_URL}/topics')
    return response.json()

def get_learning_goals():
    response = requests.get(f'{API_BASE_URL}/learning-goals')
    return response.json()

def create_topic(name, priority='medium'):
    response = requests.post(f'{API_BASE_URL}/topics', json={'name': name, 'priority': priority})
    return response.json()

def create_learning_goal(topic_id, description, deadline):
    response = requests.post(f'{API_BASE_URL}/learning-goals', json={'topic_id': topic_id, 'description': description, 'deadline': deadline})
    return response.json()
