import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    INSTANCE_DIR = os.path.join(BASE_DIR, 'datenbank', 'instance')
    DATABASE_PATH = os.path.join(INSTANCE_DIR, 'learning_app.db')

    # SQLite-Datenbank-URI festlegen
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'eine_sehr_geheimer_key'