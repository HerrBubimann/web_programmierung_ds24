from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from bff.controllers import get_user_topics, get_user_learning_goals, add_topic_for_user, add_learning_goal_for_user
from api.models import db, User
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        topics = get_user_topics(current_user.id)
        goals = get_user_learning_goals(current_user.id)
        return render_template('index.html', topics=topics, goals=goals)
    else:
        return redirect(url_for('login'))

@app.route('/add-topic', methods=['POST'])
@login_required
def add_topic():
    name = request.form.get('name')
    priority = request.form.get('priority', 'medium')
    if name:
        add_topic_for_user(current_user.id, name, priority)
        flash('Thema erfolgreich hinzugefügt')
    else:
        flash('Name darf nicht leer sein')
    return redirect(url_for('index'))

@app.route('/add-goal', methods=['POST'])
@login_required
def add_goal():
    topic_id = request.form.get('topic_id')
    description = request.form.get('description')
    deadline = request.form.get('deadline')
    if topic_id and description and deadline:
        add_learning_goal_for_user(current_user.id, topic_id, description, deadline)
        flash('Lernziel erfolgreich hinzugefügt')
    else:
        flash('Bitte fülle alle Felder aus')
    return redirect(url_for('index'))

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
            return jsonify({"message": "Login successful", "redirect": url_for('index')}), 200
        else:
            return jsonify({"message": "Ungültige Anmeldedaten"}), 401
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

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

    # Render the registration page for GET requests
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)