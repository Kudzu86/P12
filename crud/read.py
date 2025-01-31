from config.db import Session
from models.models import Employee, Client, Contract, Event
from auth import verify_token
from models.permissions import verify_user_permission


class ReadService:
    @staticmethod
    def get_all_clients(token):
        """Récupère tous les clients avec vérification de permissions."""
        employee = verify_token(token)
        if not employee:
            return []
        
        session = Session()
        try:
            # Récupérer l'utilisateur courant en utilisant son username
            current_user = session.query(Employee).filter_by(username=employee.username).first()
            if not current_user:
                return []
            
            if current_user.departement == Employee.GESTION:
                if verify_user_permission(token, 'manage_clients'):
                    return session.query(Client).all()
            elif current_user.departement == Employee.COMMERCIAL:
                # Les commerciaux voient leurs clients
                return session.query(Client).filter_by(commercial_id=current_user.id).all()
            
            return []
        finally:
            session.close()

    @staticmethod
    def get_all_contracts(token):
        """Récupère les contrats selon les permissions de l'utilisateur."""
        employee = verify_token(token)
        if not employee:
            return []

        session = Session()
        try:
            current_user = session.query(Employee).filter_by(username=employee.username).first()
            if not current_user:
                return []

            if current_user.departement == Employee.COMMERCIAL:
                return session.query(Contract).filter_by(commercial_id=current_user.id).all()
            elif current_user.departement == Employee.GESTION:
                if verify_user_permission(token, 'manage_contracts'):
                    return session.query(Contract).all()
            
            return []
        finally:
            session.close()

    @staticmethod
    def get_all_events(token):
        """Récupère les événements selon les permissions de l'utilisateur."""
        employee = verify_token(token)
        if not employee:
            return []

        session = Session()
        try:
            current_user = session.query(Employee).filter_by(username=employee.username).first()
            if not current_user:
                return []

            if current_user.departement == Employee.SUPPORT:
                return session.query(Event).filter_by(contact_support_id=current_user.id).all()
            elif current_user.departement == Employee.GESTION:
                if verify_user_permission(token, 'manage_events'):
                    return session.query(Event).all()
            
            return []
        finally:
            session.close()

    @staticmethod
    def get_all_employees(token):
        """Récupère tous les employés (réservé aux gestionnaires)"""
        employee = verify_token(token)
        if not employee:
            return []

        session = Session()
        try:
            current_user = session.query(Employee).filter_by(username=employee.username).first()
            if not current_user or current_user.departement != Employee.GESTION:
                raise PermissionError("Seuls les gestionnaires peuvent voir tous les employés")

            return session.query(Employee).all()
        finally:
            session.close()


    @staticmethod
    def delete_employee(token, employee_id):
        """Supprime un collaborateur"""
        if not verify_user_permission(token, 'delete_users'):
            raise PermissionError("Vous n'avez pas la permission de supprimer des collaborateurs")
        
        session = Session()
        try:
            employee = session.query(Employee).get(employee_id)
            if not employee:
                raise NoResultFound("Collaborateur non trouvé")
                
            session.delete(employee)
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()