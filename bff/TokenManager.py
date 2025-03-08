from datetime import datetime, timedelta
from datenbank.models import db, Token
import secrets

class TokenManager:
    def __init__(self):
        self.token_lifetime = 36000

    @staticmethod
    def generate_token():
        token = secrets.token_hex(16)
        return token

    def is_token_valid(self, token):
        token_instance = Token.query.filter_by(token=token).first()
        if token_instance:
            creation_time = datetime.fromtimestamp(token_instance.token_erstelldatum.timestamp())  # Konvertiere zurück
            if datetime.now() - creation_time < timedelta(seconds=self.token_lifetime):
                return True
        return False

    def get_or_create_token(self, user_id):
        token_instance = Token.query.filter_by(user_id=user_id).first()

        if token_instance:
            current_time = datetime.now()
            if self.is_token_valid(token_instance.token):
                return token_instance.token
            else:
                db.session.delete(token_instance)
                db.session.commit()

        new_token = self.generate_token()
        new_token_instance = Token(token=new_token, token_erstelldatum=datetime.now(), user_id=user_id)
        db.session.add(new_token_instance)
        db.session.commit()

        return new_token

    @staticmethod
    def delete_token(user_id):
        token_instance = Token.query.filter_by(user_id=user_id).first()
        if token_instance:
            db.session.delete(token_instance)
            db.session.commit()
            return True
        return False

token_manager = TokenManager()