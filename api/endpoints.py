from flask import Flask, jsonify, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from api.models import db, User, Topic, LearningGoal
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Benutzername existiert bereits'}), 400

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Benutzer erfolgreich registriert'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        return jsonify({'message': 'Erfolgreich eingeloggt'}), 200
    return jsonify({'error': 'Ungültige Anmeldedaten'}), 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Erfolgreich ausgeloggt'}), 200

@app.route('/topics', methods=['POST'])
@login_required
def create_topic():
    data = request.json
    new_topic = Topic(name=data['name'], priority=data.get('priority', 'medium'), user_id=current_user.id)
    db.session.add(new_topic)
    db.session.commit()
    return jsonify(new_topic.to_dict()), 201

@app.route('/topics', methods=['GET'])
@login_required
def get_topics():
    topics = Topic.query.filter_by(user_id=current_user.id).all()
    return jsonify([topic.to_dict() for topic in topics]), 200

@app.route('/learning-goals', methods=['POST'])
@login_required
def create_learning_goal():
    data = request.json
    new_goal = LearningGoal(topic_id=data['topic_id'], description=data['description'], deadline=data['deadline'], user_id=current_user.id)
    db.session.add(new_goal)
    db.session.commit()
    return jsonify(new_goal.to_dict()), 201

@app.route('/learning-goals', methods=['GET'])
@login_required
def get_learning_goals():
    goals = LearningGoal.query.filter_by(user_id=current_user.id).all()
    return jsonify([goal.to_dict() for goal in goals]), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
