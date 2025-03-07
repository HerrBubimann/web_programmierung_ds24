from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from bff.controllers import get_user_topics, get_user_learning_goals, add_topic_for_user, add_learning_goal_for_user
from api.models import db, User
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
db.init_app(app)

jwt = JWTManager(app)

@app.route('/')
@jwt_required()
def index():
    current_user_id = get_jwt_identity()
    topics = get_user_topics(current_user_id)
    goals = get_user_learning_goals(current_user_id)
    return render_template('index.html', topics=topics, goals=goals)

@app.route('/add-topic', methods=['POST'])
@jwt_required()
def add_topic():
    current_user_id = get_jwt_identity()
    name = request.form.get('name')
    priority = request.form.get('priority', 'medium')
    if name:
        add_topic_for_user(current_user_id, name, priority)
        flash('Thema erfolgreich hinzugefügt')
    else:
        flash('Name darf nicht leer sein')
    return redirect(url_for('index'))

@app.route('/add-goal', methods=['POST'])
@jwt_required()
def add_goal():
    current_user_id = get_jwt_identity()
    topic_id = request.form.get('topic_id')
    description = request.form.get('description')
    deadline = request.form.get('deadline')
    if topic_id and description and deadline:
        add_learning_goal_for_user(current_user_id, topic_id, description, deadline)
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
            access_token = create_access_token(identity=user.id)
            return jsonify({"message": "Login successful", "access_token": access_token, "redirect": url_for('index')}), 200
        else:
            return jsonify({"message": "Ungültige Anmeldedaten"}), 401
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # Da JWT stateless ist, gibt es keine serverseitige Sitzung zu beenden.
    # Der Client muss das Token einfach verwerfen.
    return jsonify({"message": "Logout successful"}), 200

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

    # Get request
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)