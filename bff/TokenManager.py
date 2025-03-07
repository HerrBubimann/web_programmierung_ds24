from datetime import datetime
from api.models import db, Token
import time
import secrets

class TokenManager:
    def __init__(self):
        """
        Initialisiert den TokenManager mit einer Gültigkeitsdauer für Tokens.
        """
        self.token_lifetime = 3600
        self.tokens = {}

    def generate_token(self):
        """
        Generiert einen neuen Token und speichert den Erstellungszeitpunkt.

        :return: Der generierte Token
        """
        token = secrets.token_hex(16)  # Erzeugt einen sicheren, zufälligen Token
        self.tokens[token] = time.time()  # Speichert den Erstellungszeitpunkt
        return token

    def is_token_valid(self, token, current_time):
        """
        Überprüft, ob der Token zu einem bestimmten Zeitpunkt gültig ist.

        :param token: Der zu überprüfende Token
        :param current_time: Der Zeitpunkt, zu dem die Gültigkeit überprüft wird (als Unix-Zeitstempel)
        :return: True, wenn der Token gültig ist, False sonst
        """
        if token in self.tokens:
            creation_time = self.tokens[token]
            if current_time - creation_time < self.token_lifetime:
                return True
            else:
                # Token ist abgelaufen, entferne ihn aus dem Speicher
                del self.tokens[token]
        return False

    def get_or_create_token(self, user_id):
        """
        Überprüft, ob der Benutzer einen gültigen Token hat. Falls nicht, wird ein neuer Token erstellt.

        :param user_id: Die ID des Benutzers, für den der Token überprüft oder erstellt werden soll
        :return: Der vorhandene oder neu erstellte Token
        """
        token_instance = Token.query.filter_by(user_id=user_id).first()

        if token_instance:
            current_time = time.time()
            if self.is_token_valid(token_instance.token, current_time):
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
        """
        Löscht den Token für einen bestimmten Benutzer aus der Datenbank.

        :param user_id: Die ID des Benutzers, dessen Token gelöscht werden soll
        :return: True, wenn der Token gelöscht wurde, False, wenn kein Token gefunden wurde
        """
        token_instance = Token.query.filter_by(user_id=user_id).first()
        if token_instance:
            db.session.delete(token_instance)
            db.session.commit()
            return True
        return False

token_manager = TokenManager()