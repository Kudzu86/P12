from config.db import Session
from models.models import Employee, Client, Contract, Event
from auth import verify_token
from models.permissions import verify_user_permission
from sqlalchemy.orm.exc import NoResultFound


class UpdateService:
    @staticmethod
    def update_employee(token, employee_id, update_data):
        """Modifier un collaborateur."""
        if not verify_user_permission(token, 'manage_users'):
            raise PermissionError("Vous n'avez pas la permission de modifier des collaborateurs")
        
        session = Session()
        try:
            employee = session.query(Employee).get(employee_id)
            if not employee:
                raise NoResultFound("Collaborateur non trouvé")
            
            for key, value in update_data.items():
                setattr(employee, key, value)
            
            session.commit()
            session.refresh(employee)
            return session.merge(employee)
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def update_client(token, client_id, update_data):
        """Modifier un client."""
        employee = verify_token(token)
        if not employee:
            raise PermissionError("Token invalide")

        session = Session()
        try:
            current_user = session.merge(employee)
            client = session.query(Client).get(client_id)

            if not client:
                raise NoResultFound("Client non trouvé")

            if not (current_user.departement == Employee.COMMERCIAL and client.commercial_id == current_user.id) and \
               not (current_user.departement == Employee.GESTION and verify_user_permission(token, 'manage_clients')):
                raise PermissionError("Permissions insuffisantes")

            for key, value in update_data.items():
                setattr(client, key, value)
            
            session.commit()
            session.refresh(client)
            return session.merge(client)
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def update_contract(token, contract_id, update_data):
        """Modifier un contrat."""
        if not verify_user_permission(token, 'manage_contracts'):
            raise PermissionError("Vous n'avez pas la permission de modifier des contrats")
        
        session = Session()
        try:
            contract = session.query(Contract).get(contract_id)
            if not contract:
                raise NoResultFound("Contrat non trouvé")
            
            for key, value in update_data.items():
                setattr(contract, key, value)
            
            session.commit()
            session.refresh(contract)
            return session.merge(contract)
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def update_event(token, event_id, update_data):
        """Modifier un événement."""
        if not verify_user_permission(token, 'manage_events'):
            raise PermissionError("Vous n'avez pas la permission de modifier des événements")
        
        session = Session()
        try:
            event = session.query(Event).get(event_id)
            if not event:
                raise NoResultFound("Événement non trouvé")
            
            for key, value in update_data.items():
                setattr(event, key, value)
            
            session.commit()
            session.refresh(event)
            return session.merge(event)
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()