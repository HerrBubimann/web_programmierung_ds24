from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, make_response
from flask_login import LoginManager, login_user, logout_user
from datenbank.models import db, User, Token, Topic, LearningGoal, StudyMethod
from config import Config
from bff.TokenManager import token_manager
from datetime import datetime
from sqlalchemy import or_
import os
from googleapiclient.discovery import build

app = Flask(__name__,
            template_folder=r'C:\Users\janje\PycharmProjects\web_programmierung_ds24\storefront\templates',
            #template_folder=r'C:\Users\JJ\Uni\web_programmierung_ds24\storefront\templates',
            static_folder=r'C:\Users\janje\PycharmProjects\web_programmierung_ds24\storefront\static')
            #static_folder=r'C:\Users\JJ\Uni\web_programmierung_ds24\storefront\static',)
app.config.from_object(Config)
db.init_app(app)

youtube = build('youtube', 'v3', developerKey='AIzaSyAxK2w1CW7w76e-nmvd459gpI9votx81vc')

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    """Lädt den Benutzer anhand der user_id aus der Datenbank."""
    return User.query.get(int(user_id))

def validate_token(token):
    """Prüft die Gültigkeit des Tokens und gibt den entsprechenden Benutzer zurück.
        (Direkt als Funktion implementiert, da der Nutzen einer eigenen Klasse hierfür nicht ersichtlich war.)"""
    if not token:
        return None

    token_instance = Token.query.filter_by(token=token).first()
    if token_instance is None:
        return None

    if not token_manager.is_token_valid(token):
        return None
    return User.query.get(token_instance.user_id)

@app.route('/')
def index():
    """Zeigt die Startseite an, wenn der Benutzer authentifiziert ist, sonst Weiterleitung zum Login."""
    token = request.cookies.get('auth_token')
    user = validate_token(token)
    if user:
        return render_template('index.html')
    else:
        print("Kein gültiger Benutzer gefunden, leite zur Login-Seite weiter.")
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Behandelt den Login-Prozess. Bei erfolgreicher Anmeldung wird ein Token erstellt und gesetzt."""
    if request.method == 'POST':
        data = request.get_json()
        username_or_email = data.get('username') or data.get('email')
        password = data.get('password')

        user = User.query.filter(
            or_(User.username == username_or_email, User.usermail == username_or_email),
            User.is_active_user == True
        ).first()

        if user and user.check_password(password):
            login_user(user)
            token = token_manager.get_or_create_token(user.id)

            response = make_response(jsonify({"message": "Login successful", "redirect": url_for('index')}))
            response.set_cookie('auth_token', token, httponly=True, secure=True, samesite='Strict')
            return response, 200
        else:
            return jsonify({"message": "Ungültige Anmeldedaten"}), 401
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    """Behandelt den Logout-Prozess. Löscht das Token und meldet den Benutzer ab."""
    token = request.cookies.get('auth_token')
    user = validate_token(token)
    if not user:
        return jsonify({"message": "Unauthorized"}), 401

    if token_manager.delete_token(user.id):
        logout_user()
        response = make_response(jsonify({"message": "Logout successful"}))
        response.set_cookie('auth_token', '', expires=0)
        return response, 200
    else:
        return jsonify({"message": "Fehler beim Logout"}), 401

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Behandelt die Registrierung eines neuen Benutzers."""
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({"message": "No data provided"}), 400

            username = data.get('username')
            password = data.get('password')
            usermail = data.get('email')

            if not username or not password or not usermail:
                return jsonify({"message": "Fehlende Pflichtfelder"}), 400

            if User.query.filter_by(username=username).first():
                return jsonify({"message": "Benutzername existiert bereits"}), 400
            if User.query.filter_by(usermail=usermail).first():
                return jsonify({"message": "Email existiert bereits"}), 400

            new_user = User(username=username, usermail=usermail)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            return jsonify({"message": "Benutzer erfolgreich registriert"}), 201

        except Exception as e:
            print(f"Error during registration: {e}")
            return jsonify({"message": f"Ein Fehler ist aufgetreten: {str(e)}"}), 500

    return render_template('register.html')

@app.route('/topics', methods=['GET'])
def get_topic():
    """Gibt alle Themen des authentifizierten Benutzers zurück."""
    token = request.cookies.get('auth_token')
    user = validate_token(token)
    topics = Topic.query.filter_by(user_id=user.id).all()

    if topics:
        topics_dict = [topic.to_dict() for topic in topics]
        return jsonify(topics_dict), 200
    else:
        return jsonify([]), 200

@app.route('/topics', methods=['POST'])
def create_topic():
    """Erstellt ein neues Thema für den authentifizierten Benutzer."""
    token = request.cookies.get('auth_token')
    user = validate_token(token)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    title = data.get('title')
    priority = data.get('priority')

    if not title:
        return jsonify({'error': 'Titel ist erforderlich'}), 400

    new_topic = Topic(name=title, priority=priority , user_id=user.id)
    db.session.add(new_topic)
    db.session.commit()

    return jsonify({'message': 'Thema erfolgreich erstellt', 'topic_id': new_topic.id}), 201

@app.route('/learning_goals', methods=['GET'])
def get_learning_goals():
    """Gibt alle Lernziele des authentifizierten Benutzers zurück, sortiert nach Frist."""
    token = request.cookies.get('auth_token')
    user = validate_token(token)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        goals = LearningGoal.query.join(Topic).filter_by(user_id=user.id).order_by(LearningGoal.deadline).all()
        goals_data = []

        for goal in goals:
            deadline = goal.deadline
            if isinstance(deadline, str):
                try:
                    deadline = datetime.fromisoformat(deadline)
                except ValueError:
                    deadline = None
            goals_data.append({
                'id': goal.id,
                'topic_name': goal.topic.name if goal.topic else None,
                'description': goal.description,
                'deadline': deadline.strftime('%Y-%m-%d') if deadline else None
            })
        return jsonify(goals_data), 200
    except Exception as e:
        app.logger.error(f"error beim Abrufen von Lernzielen: {str(e)}")
        return jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500

@app.route('/learning_goals', methods=['POST'])
def create_learning_goal():
    """Erstellt ein neues Lernziel für den authentifizierten Benutzer."""
    token = request.cookies.get('auth_token')
    user = validate_token(token)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    topic_id = data.get('topic_id')
    description = data.get('description')
    deadline = data.get('deadline')

    if not topic_id or not description or not deadline:
        return jsonify({'error': 'topic_id, description und deadline sind erforderlich'}), 400

    topic = Topic.query.filter_by(id=topic_id, user_id=user.id).first()
    if not topic:
        return jsonify({'error': 'Thema nicht gefunden'}), 404

    new_learning_goal = LearningGoal(
        topic_id=topic_id,
        description=description,
        deadline=deadline,
        user_id=user.id
    )
    db.session.add(new_learning_goal)
    db.session.commit()

    return jsonify({'message': 'Lernziel erfolgreich erstellt', 'learning_goal_id': new_learning_goal.id}), 201

@app.route('/learning_goals/<int:goal_id>')
def learning_goal_detail(goal_id):
    """
    Gibt die Details eines bestimmten Lernziels zurück.
    """
    token = request.cookies.get('auth_token')
    user = validate_token(token)
    if not user:
        return redirect(url_for('login'))

    goal = LearningGoal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        return jsonify({'error': 'Lernziel nicht gefunden'}), 404

    return render_template('goal_detail.html', goal=goal)


@app.route('/study_methods', methods=['POST'])
def create_study_method():
    """
    Erstellt eine neue Lernmethode für ein bestimmtes Lernziel.
    """
    token = request.cookies.get('auth_token')
    user = validate_token(token)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    goal_id = data.get('goal_id')
    method_type = data.get('type')
    content = data.get('content')

    goal = LearningGoal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        return jsonify({'error': 'Lernziel nicht gefunden'}), 404

    new_method = StudyMethod(
        method_type=method_type,
        content=content,
        goal_id=goal_id
    )
    db.session.add(new_method)
    db.session.commit()

    return jsonify({'message': 'Methode gespeichert', 'method': new_method.to_dict()}), 201


@app.route('/study_methods/<int:goal_id>', methods=['GET'])
def get_study_methods(goal_id):
    """
    Gibt alle Lernmethoden für ein bestimmtes Lernziel des Benutzers zurück.
    """
    token = request.cookies.get('auth_token')
    user = validate_token(token)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    methods = StudyMethod.query.join(LearningGoal).filter(
        StudyMethod.goal_id == goal_id,
        LearningGoal.user_id == user.id
    ).all()

    return jsonify([method.to_dict() for method in methods]), 200


@app.route('/study_methods/<int:goal_id>/<string:content>', methods=['DELETE'])
def delete_study_method(goal_id, content):
    """Löscht eine Lernmethode anhand der YouTube-ID/content"""
    token = request.cookies.get('auth_token')
    user = validate_token(token)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    method = StudyMethod.query.join(LearningGoal).filter(
        StudyMethod.content == content,
        StudyMethod.goal_id == goal_id,
        LearningGoal.user_id == user.id
    ).first()

    if not method:
        return jsonify({'error': 'Methode nicht gefunden'}), 404

    db.session.delete(method)
    db.session.commit()

    return jsonify({'message': 'Methode erfolgreich gelöscht'}), 200

@app.route('/youtube-search')
def youtube_search():
    search_query = request.args.get('q', '')
    youtube_request = youtube.search().list(  # Name geändert
        q=search_query,
        part='snippet',
        type='video',
        maxResults=5,
        videoEmbeddable='true'
    )
    response = youtube_request.execute()
    return jsonify(response['items'])

def main():
    with app.app_context():
        if not os.path.exists(Config.INSTANCE_DIR):
            os.makedirs(Config.INSTANCE_DIR)
        db.create_all()
    app.run(debug=True, port=5001)

if __name__ == '__main__':
    main()