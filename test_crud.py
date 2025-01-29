import pytest
from config.db import Session
from models.models import Employee, Client, Contract, Event
from crud import CRUDService
from auth import create_access_token
from models.permissions import setup_department_permissions, assign_department_permissions
import uuid
from datetime import datetime

def generate_unique_email():
   return f"test_{uuid.uuid4()}@example.com"

def generate_unique_username():
   return f"test_user_{uuid.uuid4()}"

@pytest.fixture(scope="function")
def test_tokens():
   """
   Fixture générant deux tokens :
   - Un token avec tous les droits (GESTION)
   - Un token avec des droits limités (COMMERCIAL)
   """
   session = Session()
   
   try:
       # Utilisateur avec tous les droits
       gestion_user = Employee(
           username=generate_unique_username(),
           email=generate_unique_email(),
           nom="Admin",
           prenom="System",
           departement="GESTION"
       )
       gestion_user.set_password("test123")
       session.add(gestion_user)
       session.commit()
       assign_department_permissions(gestion_user)
       gestion_token = create_access_token(gestion_user.username)

       # Utilisateur avec droits limités
       commercial_user = Employee(
           username=generate_unique_username(),
           email=generate_unique_email(),
           nom="Commercial",
           prenom="Limité",
           departement="COMMERCIAL"
       )
       commercial_user.set_password("test123")
       session.add(commercial_user)
       session.commit()
       assign_department_permissions(commercial_user)
       commercial_token = create_access_token(commercial_user.username)

       yield {
           "all_rights": gestion_token,
           "limited_rights": commercial_token
       }
   
   finally:
       session.close()

def test_create_employee(test_tokens):
   """
   Test la création d'un employé avec deux types de tokens
   """
   employee_data = {
       "username": generate_unique_username(),
       "email": generate_unique_email(),
       "nom": "Nouveau",
       "prenom": "Employé",
       "departement": "COMMERCIAL",
       "password": "test123"
   }

   # Test avec token ayant tous les droits
   employee = CRUDService.create_employee(
       test_tokens['all_rights'], 
       employee_data
   )
   assert employee is not None
   assert employee.username == employee_data["username"]

   # Test avec token aux droits limités
   with pytest.raises(PermissionError):
       CRUDService.create_employee(
           test_tokens['limited_rights'], 
           employee_data
       )

def test_update_employee(test_tokens):
   """
   Test la modification d'un employé avec deux types de tokens
   """
   session = Session()
   try:
       # Créer un employé à modifier
       original_employee = Employee(
           username=generate_unique_username(),
           email=generate_unique_email(),
           nom="Original",
           prenom="Employé",
           departement="SUPPORT"
       )
       original_employee.set_password("test123")
       session.add(original_employee)
       session.commit()
       employee_id = original_employee.id
   finally:
       session.close()
   
   # Données de mise à jour
   update_data = {
       "departement": "COMMERCIAL",
       "nom": "Modifié"
   }
   
   # Test avec token ayant tous les droits
   updated_employee = CRUDService.update_employee(
       test_tokens['all_rights'], 
       employee_id, 
       update_data
   )
   assert updated_employee.departement == "COMMERCIAL"
   assert updated_employee.nom == "Modifié"

   # Test avec token aux droits limités
   with pytest.raises(PermissionError):
       CRUDService.update_employee(
           test_tokens['limited_rights'], 
           employee_id, 
           update_data
       )

def test_create_contract(test_tokens):
   """
   Test la création d'un contrat avec deux types de tokens
   """
   session = Session()
   try:
       client = Client(
           nom_complet="Client Test",
           email=generate_unique_email(),
           entreprise="Entreprise Test"
       )
       session.add(client)
       session.commit()
       client_id = client.id
   finally:
       session.close()

   contract_data = {
       "client_id": client_id,
       "montant_total": 1000.00,
       "montant_restant": 1000.00,
       "est_signe": False
   }

   # Test avec token ayant tous les droits
   contract = CRUDService.create_contract(
       test_tokens['all_rights'], 
       contract_data
   )
   assert contract is not None
   assert contract.client_id == client_id

   # Test avec token aux droits limités
   with pytest.raises(PermissionError):
       CRUDService.create_contract(
           test_tokens['limited_rights'], 
           contract_data
       )

def test_update_contract(test_tokens):
   """
   Test la modification d'un contrat avec deux types de tokens
   """
   session = Session()
   try:
       client = Client(
           nom_complet="Client Test",
           email=generate_unique_email(),
           entreprise="Entreprise Test"
       )
       session.add(client)
       session.commit()
       
       original_contract = Contract(
           client_id=client.id,
           montant_total=1000.00,
           montant_restant=1000.00,
           est_signe=False
       )
       session.add(original_contract)
       session.commit()
       contract_id = original_contract.id
   finally:
       session.close()
   
   update_data = {
       "est_signe": True,
       "montant_restant": 0.00
   }
   
   # Test avec token ayant tous les droits
   updated_contract = CRUDService.update_contract(
       test_tokens['all_rights'], 
       contract_id, 
       update_data
   )
   assert updated_contract.est_signe == True
   assert updated_contract.montant_restant == 0.00

   # Test avec token aux droits limités
   with pytest.raises(PermissionError):
       CRUDService.update_contract(
           test_tokens['limited_rights'], 
           contract_id, 
           update_data
       )

def test_create_event(test_tokens):
   """
   Test la création d'un événement avec deux types de tokens
   """
   session = Session()
   try:
       client = Client(
           nom_complet="Client Test",
           email=generate_unique_email(),
           entreprise="Entreprise Test"
       )
       session.add(client)
       session.commit()
       
       contract = Contract(
           client_id=client.id,
           montant_total=1000.00,
           montant_restant=0.00,
           est_signe=True
       )
       session.add(contract)
       session.commit()
       contract_id = contract.id
   finally:
       session.close()
   
   event_data = {
       "nom": "Événement Test",
       "contrat_id": contract_id,
       "date_debut": datetime.now(),
       "date_fin": datetime.now(),
       "lieu": "Lieu de Test",
       "nb_participants": 50
   }

   # Test avec token ayant tous les droits
   event = CRUDService.create_event(
       test_tokens['all_rights'], 
       event_data
   )
   assert event is not None
   assert event.contrat_id == contract_id

   # Test avec token aux droits limités
   with pytest.raises(PermissionError):
       CRUDService.create_event(
           test_tokens['limited_rights'], 
           event_data
       )

def test_update_event(test_tokens):
   """
   Test la modification d'un événement avec deux types de tokens
   """
   session = Session()
   try:
       client = Client(
           nom_complet="Client Test",
           email=generate_unique_email(),
           entreprise="Entreprise Test"
       )
       session.add(client)
       session.commit()
       
       contract = Contract(
           client_id=client.id,
           montant_total=1000.00,
           montant_restant=0.00,
           est_signe=True
       )
       session.add(contract)
       session.commit()
       
       original_event = Event(
           nom="Événement Original",
           contrat_id=contract.id,
           date_debut=datetime.now(),
           date_fin=datetime.now(),
           lieu="Lieu Original",
           nb_participants=50
       )
       session.add(original_event)
       session.commit()
       event_id = original_event.id
   finally:
       session.close()
   
   update_data = {
       "nom": "Événement Modifié",
       "lieu": "Nouveau Lieu",
       "nb_participants": 75
   }
   
   # Test avec token ayant tous les droits
   updated_event = CRUDService.update_event(
       test_tokens['all_rights'], 
       event_id, 
       update_data
   )
   assert updated_event.nom == "Événement Modifié"
   assert updated_event.lieu == "Nouveau Lieu"
   assert updated_event.nb_participants == 75

   # Test avec token aux droits limités
   with pytest.raises(PermissionError):
       CRUDService.update_event(
           test_tokens['limited_rights'], 
           event_id, 
           update_data
       )