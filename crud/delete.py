from config.db import Session
from models.models import Employee
from auth import verify_token
from models.permissions import verify_user_permission
from sqlalchemy.orm.exc import NoResultFound


class DeleteService:
    @staticmethod
    def delete_employee(token, employee_id):
        """Supprime un collaborateur (réservé aux gestionnaires)"""
        employee = verify_token(token)
        if not employee:
            raise PermissionError("Authentification requise")

        session = Session()
        try:
            # Vérifie que l'utilisateur est gestionnaire
            current_user = session.query(Employee).filter_by(username=employee.username).first()
            if not current_user or current_user.departement != Employee.GESTION:
                raise PermissionError("Seuls les gestionnaires peuvent supprimer un collaborateur")

            # Trouver l'employé à supprimer
            employee_to_delete = session.query(Employee).get(employee_id)
            if not employee_to_delete:
                raise NoResultFound("Collaborateur non trouvé")

            session.delete(employee_to_delete)
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
