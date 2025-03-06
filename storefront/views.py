from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from bff.controllers import get_user_topics, get_user_learning_goals, add_topic_for_user, add_learning_goal_for_user
from api.models import db, User

app = Flask(__name__)
app.secret_key = 'eine_sehr_geheime_key'

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
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Ungültige Anmeldedaten')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Benutzername existiert bereits')
        else:
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Benutzer erfolgreich registriert')
            return redirect(url_for('login'))
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)