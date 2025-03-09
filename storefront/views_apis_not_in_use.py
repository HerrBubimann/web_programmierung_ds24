from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, make_response
from flask_login import LoginManager, login_user, logout_user
from datenbank.models import db, User, Token, Topic, LearningGoal
from config import Config
from bff.TokenManager import token_manager
from datetime import datetime
from sqlalchemy import or_
import os

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

def validate_token(token):
    if not token:
        return None

    token_instance = Token.query.filter_by(token=token).first()
    if token_instance is None:
        return None

    if not token_manager.is_token_valid(token):
        return None
    return User.query.get(token_instance.user_id)

@app.route('/learning-goals/<int:goal_id>', methods=['GET'])
def get_learning_goal_with_id(goal_id):
    token = request.cookies.get('auth_token')
    user = validate_token(token)
    goal = LearningGoal.query.filter_by(id=goal_id, user_id=user.id).first()
    if goal:
        return jsonify(goal.to_dict()), 200
    else:
        return jsonify({'error': 'Lernziel nicht gefunden'}), 404

@app.route('/learning-goals/<int:goal_id>', methods=['PUT'])
def update_learning_goal(goal_id):
    token = request.cookies.get('auth_token')
    user = validate_token(token)
    goal = LearningGoal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        return jsonify({'error': 'Lernziel nicht gefunden'}), 404

    data = request.json
    goal.description = data.get('description', goal.description)
    goal.deadline = data.get('deadline', goal.deadline)
    db.session.commit()
    return jsonify(goal.to_dict()), 200

@app.route('/learning-goals/<int:goal_id>', methods=['DELETE'])
def delete_learning_goal(goal_id):
    token = request.cookies.get('auth_token')
    user = validate_token(token)
    goal = LearningGoal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        return jsonify({'error': 'Lernziel nicht gefunden'}), 404

    db.session.delete(goal)
    db.session.commit()
    return jsonify({'message': 'Lernziel erfolgreich gelöscht'}), 200


@app.route('/topics/<int:topic_id>', methods=['GET'])
def get_topic_with_id(topic_id):
    token = request.cookies.get('auth_token')
    user = validate_token(token)
    topic = Topic.query.filter_by(id=topic_id, user_id=user.id).first()
    if topic:
        return jsonify(topic.to_dict()), 200
    else:
        return jsonify({'error': 'Thema nicht gefunden'}), 404

@app.route('/topics/<int:topic_id>', methods=['PUT'])
def update_topic(topic_id):
    token = request.cookies.get('auth_token')
    user = validate_token(token)
    topic = Topic.query.filter_by(id=topic_id, user_id=user.id).first()
    if not topic:
        return jsonify({'error': 'Thema nicht gefunden'}), 404

    data = request.json
    topic.name = data.get('name', topic.name)
    topic.priority = data.get('priority', topic.priority)
    db.session.commit()
    return jsonify(topic.to_dict()), 200

@app.route('/topics/<int:topic_id>', methods=['DELETE'])
def delete_topic(topic_id):
    token = request.cookies.get('auth_token')
    user = validate_token(token)
    topic = Topic.query.filter_by(id=topic_id, user_id=user.id).first()
    if not topic:
        return jsonify({'error': 'Thema nicht gefunden'}), 404

    db.session.delete(topic)
    db.session.commit()
    return jsonify({'message': 'Thema erfolgreich gelöscht'}), 200