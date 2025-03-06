import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///learning_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'eine_sehr_geheime_key'
