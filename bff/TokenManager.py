from datetime import datetime, timedelta
from datenbank.models import db, Token
import secrets

class TokenManager:
    def __init__(self):
        """Initialisiert den TokenManager mit einer Token-Lebensdauer von 36000 Sekunden (10 Stunden)."""
        self.token_lifetime = 36000

    @staticmethod
    def generate_token():
        """Generiert ein neues, sicheres Token mit einer Länge von 32 Zeichen (16 Bytes in Hexadezimaldarstellung)."""
        token = secrets.token_hex(16)
        return token

    def is_token_valid(self, token):
        """Überprüft, ob das Token gültig ist, basierend auf seiner Erstellungszeit und der Token-Lebensdauer."""
        token_instance = Token.query.filter_by(token=token).first()
        if token_instance:
            creation_time = datetime.fromtimestamp(token_instance.token_erstelldatum.timestamp())  # Konvertiere zurück
            if datetime.now() - creation_time < timedelta(seconds=self.token_lifetime):
                return True
        return False

    def get_or_create_token(self, user_id):
        """Gibt das vorhandene Token für den Benutzer zurück, falls es gültig ist. Andernfalls wird ein neues Token erstellt."""
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
        """Löscht das Token des Benutzers aus der Datenbank, falls vorhanden."""
        token_instance = Token.query.filter_by(user_id=user_id).first()
        if token_instance:
            db.session.delete(token_instance)
            db.session.commit()
            return True
        return False

token_manager = TokenManager()