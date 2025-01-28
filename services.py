from config.db import Session
from models.models import Client, Contract, Event, Employee
from models.permissions import verify_user_permission
from auth import verify_token


class DataService:
    @staticmethod
    def get_all_clients(token):
        """
        Récupère tous les clients avec vérification de permissions.
        """
        session = Session()
        try:
            # Vérifier le token et les permissions
            if not verify_user_permission(token, 'manage_clients'):
                return []
            
            return session.query(Client).all()
        finally:
            session.close()

    @staticmethod
    def get_all_contracts(token):
        """
        Récupère les contrats selon les permissions de l'utilisateur.
        """
        session = Session()
        try:
            # Vérifier le token
            username = verify_token(token)
            if not username:
                return []

            # Récupérer l'utilisateur courant
            current_user = session.query(Employee).filter_by(username=username).first()

            # Filtrage selon le département
            if current_user.departement == Employee.COMMERCIAL:
                # Commercial : voir uniquement ses propres contrats
                return session.query(Contract).filter_by(commercial_id=current_user.id).all()
            
            elif current_user.departement == Employee.GESTION:
                # Gestion : voir tous les contrats
                if verify_user_permission(token, 'manage_contracts'):
                    return session.query(Contract).all()
            
            return []
        finally:
            session.close()

    @staticmethod
    def get_all_events(token):
        """
        Récupère les événements selon les permissions de l'utilisateur.
        """
        session = Session()
        try:
            # Vérifier le token
            username = verify_token(token)
            if not username:
                return []

            # Récupérer l'utilisateur courant
            current_user = session.query(Employee).filter_by(username=username).first()

            # Filtrage selon le département
            if current_user.departement == Employee.SUPPORT:
                # Support : voir uniquement ses propres événements
                return session.query(Event).filter_by(contact_support_id=current_user.id).all()
            
            elif current_user.departement == Employee.GESTION:
                # Gestion : voir tous les événements
                if verify_user_permission(token, 'manage_events'):
                    return session.query(Event).all()
            
            return []
        finally:
            session.close()