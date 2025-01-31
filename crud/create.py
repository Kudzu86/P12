from config.db import Session
from models.models import Employee, Client, Contract, Event
from auth import verify_token
from models.permissions import verify_user_permission
from logger import log_exception, log_employee_modification, log_contract_signature


class CreateService:
   @staticmethod
   def create_employee(token, employee_data):
       """Créer un nouveau collaborateur."""
       if not verify_user_permission(token, 'manage_users'):
           raise PermissionError("Vous n'avez pas la permission de créer des collaborateurs")
       
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
           log_employee_modification(new_employee, "création")
           return session.merge(new_employee)
       except Exception as e:
           log_exception(e)
           session.rollback()
           raise
       finally:
           session.close()

   @staticmethod
   def create_client(token, client_data):
       """Créer un nouveau client."""
       employee = verify_token(token)
       if not employee:
           raise PermissionError("Token invalide")

       session = Session()
       try:
           current_user = session.merge(employee)
           
           if not (current_user.departement == Employee.COMMERCIAL or 
                  (current_user.departement == Employee.GESTION and 
                   verify_user_permission(token, 'manage_clients'))):
               raise PermissionError("Permissions insuffisantes")

           if current_user.departement == Employee.COMMERCIAL:
               client_data['commercial_id'] = current_user.id

           if not all([
               client_data.get('nom_complet'),
               client_data.get('email'),
               client_data.get('entreprise')
           ]):
               raise ValueError("Informations du client incomplètes")

           new_client = Client(**client_data)
           session.add(new_client)
           session.commit()
           session.refresh(new_client)
           return session.merge(new_client)
       except Exception as e:
           log_exception(e)
           session.rollback()
           raise
       finally:
           session.close()

   @staticmethod
   def create_contract(token, contract_data):
       """Créer un nouveau contrat."""
       if not verify_user_permission(token, 'manage_contracts'):
           raise PermissionError("Vous n'avez pas la permission de créer des contrats")
       
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
           
           # Log si le contrat est signé à la création
           if new_contract.est_signe:
               log_contract_signature(new_contract)
               
           return session.merge(new_contract)
       except Exception as e:
           log_exception(e)
           session.rollback()
           raise
       finally:
           session.close()

   @staticmethod
   def create_event(token, event_data):
       """Créer un nouvel événement."""
       if not verify_user_permission(token, 'manage_events'):
           raise PermissionError("Vous n'avez pas la permission de créer des événements")
       
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
           log_exception(e)
           session.rollback()
           raise
       finally:
           session.close()