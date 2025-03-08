from flask import current_app
from bff.services import get_topics, get_learning_goals, create_topic, create_learning_goal

def get_user_topics(user_id):
    try:
        topics = get_topics(user_id)
        user_topics = [topic for topic in topics if topic.get('user_id') == user_id]
        return user_topics
    except Exception as e:
        current_app.logger.error(f"Fehler beim Abrufen der Themen: {e}")
        return []

def get_user_learning_goals(user_id):
    try:
        goals = get_learning_goals(user_id)
        user_goals = [goal for goal in goals if goal.get('user_id') == user_id]
        return user_goals
    except Exception as e:
        current_app.logger.error(f"Fehler beim Abrufen der Lernziele: {e}")
        return []

def add_topic_for_user(user_id, name, priority='medium'):
    try:
        response = create_topic(user_id=user_id, name=name, priority=priority)
        return response
    except Exception as e:
        current_app.logger.error(f"Fehler beim Erstellen des Themas: {e}")
        return None

def add_learning_goal_for_user(user_id, topic_id, description, deadline):
    try:
        response = create_learning_goal(topic_id=topic_id, description=description, deadline=deadline, user_id=user_id)
        return response
    except Exception as e:
        current_app.logger.error(f"Fehler beim Erstellen des Lernziels: {e}")
        return None
