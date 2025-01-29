from config.db import Session
from models.models import Employee, Client, Contract, Event
from auth import verify_token
from models.permissions import verify_user_permission
from sqlalchemy.orm.exc import NoResultFound


class CRUDService:
    @staticmethod
    def create_employee(token, employee_data):
        """
        Créer un nouveau collaborateur
        """
        # Vérifier les permissions
        if not verify_user_permission(token, 'manage_users'):
            raise PermissionError("Vous n'avez pas la permission de créer des collaborateurs")
        
        # Validation des données
        if not all([
            employee_data.get('username'), 
            employee_data.get('email'), 
            employee_data.get('departement')
        ]):
            raise ValueError("Informations du collaborateur incomplètes")
        
        session = Session()
        try:
            new_employee = Employee(**employee_data)
            session.add(new_employee)
            session.commit()
            session.refresh(new_employee)
            return session.merge(new_employee)
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def update_employee(token, employee_id, update_data):
        """
        Modifier un collaborateur
        """
        # Vérifier les permissions
        if not verify_user_permission(token, 'manage_users'):
            raise PermissionError("Vous n'avez pas la permission de modifier des collaborateurs")
        
        session = Session()
        try:
            employee = session.query(Employee).get(employee_id)
            if not employee:
                raise NoResultFound("Collaborateur non trouvé")
            
            # Mettre à jour les champs
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
    def create_contract(token, contract_data):
        """
        Créer un nouveau contrat
        """
        # Vérifier les permissions
        if not verify_user_permission(token, 'manage_contracts'):
            raise PermissionError("Vous n'avez pas la permission de créer des contrats")
        
        # Validation des données
        if not all([
            contract_data.get('client_id'), 
            contract_data.get('montant_total') is not None,
            contract_data.get('montant_restant') is not None
        ]):
            raise ValueError("Informations du contrat incomplètes")
        
        session = Session()
        try:
            new_contract = Contract(**contract_data)
            session.add(new_contract)
            session.commit()
            session.refresh(new_contract)
            return session.merge(new_contract)
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def update_contract(token, contract_id, update_data):
        """
        Modifier un contrat
        """
        # Vérifier les permissions
        if not verify_user_permission(token, 'manage_contracts'):
            raise PermissionError("Vous n'avez pas la permission de modifier des contrats")
        
        session = Session()
        try:
            contract = session.query(Contract).get(contract_id)
            if not contract:
                raise NoResultFound("Contrat non trouvé")
            
            # Mettre à jour les champs
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
    def create_event(token, event_data):
        """
        Créer un nouvel événement
        """
        # Vérifier les permissions
        if not verify_user_permission(token, 'manage_events'):
            raise PermissionError("Vous n'avez pas la permission de créer des événements")
        
        # Validation des données
        if not all([
            event_data.get('nom'), 
            event_data.get('contrat_id'),
            event_data.get('date_debut'),
            event_data.get('date_fin'),
            event_data.get('lieu')
        ]):
            raise ValueError("Informations de l'événement incomplètes")
        
        session = Session()
        try:
            new_event = Event(**event_data)
            session.add(new_event)
            session.commit()
            session.refresh(new_event)
            return session.merge(new_event)
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def update_event(token, event_id, update_data):
        """
        Modifier un événement
        """
        # Vérifier les permissions
        if not verify_user_permission(token, 'manage_events'):
            raise PermissionError("Vous n'avez pas la permission de modifier des événements")
        
        session = Session()
        try:
            event = session.query(Event).get(event_id)
            if not event:
                raise NoResultFound("Événement non trouvé")
            
            # Mettre à jour les champs
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