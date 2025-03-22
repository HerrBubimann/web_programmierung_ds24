from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    usermail = db.Column(db.String(100),unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_active_user = db.Column(db.Boolean, default=True, nullable=False)

    token = db.relationship('Token', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_active(self):
        return self.is_active_user

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return self.has_token() and self.is_active_user

    def has_token(self):
        return self.token if self.token_id else None

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.String(10), default='medium')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    learning_goals = db.relationship('LearningGoal', back_populates='topic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'priority': self.priority,
            'user_id': self.user_id
        }

class LearningGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    deadline = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic = db.relationship('Topic', back_populates='learning_goals')

    def to_dict(self):
        return {
            'id': self.id,
            'topic_id': self.topic_id,
            'description': self.description,
            'deadline': self.deadline,
            'user_id': self.user_id
        }

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), nullable=False)
    token_erstelldatum = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class StudyMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    method_type = db.Column(db.String(50), nullable=False)  # 'cards', 'mindmap', 'summary', 'video'
    content = db.Column(db.Text, nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('learning_goal.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.method_type,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }
