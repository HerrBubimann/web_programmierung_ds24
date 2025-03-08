from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, make_response
from flask_login import LoginManager, login_user, logout_user
from bff.controllers import add_topic_for_user, add_learning_goal_for_user
from datenbank.models import db, User, Token, Topic, LearningGoal
from config import Config
from bff.TokenManager import token_manager

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def validate_token(token):
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
    token = request.cookies.get('auth_token')
    user = validate_token(token)
    if user:
        return render_template('index.html')
    else:
        print("Kein gültiger Benutzer gefunden, leite zur Login-Seite weiter.")
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username_or_email = data.get('username') or data.get('email')
        password = data.get('password')

        user = User.query.filter(
            (User.username == username_or_email) | (User.usermail == username_or_email) & (User.is_active == True)
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
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({"message": "No data provided"}), 400

            username = data.get('username')
            password = data.get('password')
            usermail = data.get('email')

            if not username or not password or not usermail:
                return jsonify({"message": "Missing required fields"}), 400

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
    token = request.cookies.get('auth_token')
    user = validate_token(token)
    topics = Topic.query.filter_by(user_id=user.id).all()
    if topics:
        topics_dict = [topic.to_dict() for topic in topics]
        return jsonify(topics_dict), 200
    else:
        return jsonify({'error': 'Thema nicht gefunden'}), 404

@app.route('/topics', methods=['POST'])
def create_topic():
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

@app.route('/learning_goals', methods=['GET'])
def get_learning_goal():
    token = request.cookies.get('auth_token')
    user = validate_token(token)
    goals = LearningGoal.query.filter_by(user_id=user.id).all()
    if goals:
        goals_dict = [goal.to_dict() for goal in goals]
        return jsonify(goals_dict), 200
    else:
        return jsonify({'error': 'Keine Lernziel vorhanden'}), 205
    return jsonify({'error': 'Lernziel nicht gefunden'}), 404

@app.route('/learning_goals', methods=['POST'])
def create_learning_goal():
    token = request.cookies.get('auth_token')
    user = validate_token(token)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    topic_id = data.get('topic_id')
    description = data.get('description')
    deadline = data.get('deadline')

    if not topic_id:
        return jsonify({'error': 'topic_id und goal sind erforderlich'}), 400

    topic = Topic.query.filter_by(topic_id=topic_id,description=description,deadline=deadline, user_id=user.id).first()
    if not topic:
        return jsonify({'error': 'Thema nicht gefunden'}), 404

    new_learning_goal = LearningGoal(topic_id=topic_id,description=description,deadline=deadline, user_id=user.id)
    db.session.add(new_learning_goal)
    db.session.commit()

    return jsonify({'message': 'Lernziel erfolgreich erstellt', 'learning_goal_id': new_learning_goal.id}), 201

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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)