import pytest
from config.db import Session, Base, engine
from models.models import Employee, Client, Contract, Event, Permission
from crud.create import CreateService
from crud.update import UpdateService
from auth import create_access_token
from models.permissions import assign_department_permissions
import uuid
from datetime import datetime
from sqlalchemy import text


def generate_unique_email():
    return f"test_{uuid.uuid4()}@example.com"

def generate_unique_username():
    return f"test_user_{uuid.uuid4()}"

@pytest.fixture(autouse=True)
def cleanup_database():
    """Nettoie automatiquement la base de données après chaque test"""
    yield
    session = Session()
    try:
        # Suppression dans l'ordre pour respecter les contraintes
        session.query(Event).delete()
        session.query(Contract).delete()
        session.query(Client).delete()
        session.execute(text('DELETE FROM employee_permissions'))
        session.query(Employee).delete()
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

@pytest.fixture(scope="session", autouse=True)
def setup_permissions():
    """Configure les permissions de base nécessaires pour les tests"""
    session = Session()
    permissions = [
        Permission(code='manage_users', description='Gestion collaborateurs'),
        Permission(code='manage_contracts', description='Gestion des contrats'),
        Permission(code='manage_clients', description='Gestion des clients'),
        Permission(code='manage_events', description='Gestion des événements'),
        Permission(code='read_clients', description='Lecture des clients'),
        Permission(code='read_contracts', description='Lecture des contrats'),
        Permission(code='read_events', description='Lecture des événements')
    ]
    
    for perm in permissions:
        if not session.query(Permission).filter_by(code=perm.code).first():
            session.add(perm)
    
    session.commit()
    session.close()

@pytest.fixture
def test_tokens():
    """Génère deux tokens de test : un avec tous les droits (GESTION) et un limité (COMMERCIAL)"""
    session = Session()
    
    # Création utilisateur GESTION
    gestion_user = Employee(
        username=generate_unique_username(),
        email=generate_unique_email(),
        nom="Admin",
        prenom="System",
        departement="GESTION"
    )
    gestion_user.set_password("test123")
    session.add(gestion_user)
    
    # Création utilisateur COMMERCIAL
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
    
    # Attribution des permissions
    assign_department_permissions(gestion_user)
    assign_department_permissions(commercial_user)
    
    tokens = {
        "all_rights": create_access_token(gestion_user.username),
        "limited_rights": create_access_token(commercial_user.username)
    }
    
    return tokens


@pytest.fixture
def test_client():
    """Crée un client de test"""
    session = Session()
    client = Client(
        nom_complet="Client Test",
        email=generate_unique_email(),
        entreprise="Entreprise Test"
    )
    session.add(client)
    session.commit()
    client_id = client.id
    session.close()
    return client_id

@pytest.fixture
def test_contract(test_client):
    """Crée un contrat de test"""
    session = Session()
    contract = Contract(
        client_id=test_client,
        montant_total=1000.00,
        montant_restant=1000.00,
        est_signe=True
    )
    session.add(contract)
    session.commit()
    contract_id = contract.id
    session.close()
    return contract_id

def test_create_employee(test_tokens):
    """Test la création d'un employé avec différents niveaux de droits"""
    employee_data = {
        "username": generate_unique_username(),
        "email": generate_unique_email(),
        "nom": "Nouveau",
        "prenom": "Employé",
        "departement": "COMMERCIAL",
        "password": "test123"
    }

    # Test avec droits GESTION
    employee = CreateService.create_employee(test_tokens['all_rights'], employee_data)
    assert employee is not None
    assert employee.username == employee_data["username"]

    # Test avec droits COMMERCIAL (doit échouer)
    with pytest.raises(PermissionError):
        CreateService.create_employee(test_tokens['limited_rights'], employee_data)

def test_update_employee(test_tokens):
    """Test la modification d'un employé avec différents niveaux de droits"""
    session = Session()
    
    # Création d'un employé à modifier
    employee = Employee(
        username=generate_unique_username(),
        email=generate_unique_email(),
        nom="Original",
        prenom="Employé",
        departement="SUPPORT"
    )
    employee.set_password("test123")
    session.add(employee)
    session.commit()
    employee_id = employee.id
    session.close()

    update_data = {
        "departement": "COMMERCIAL",
        "nom": "Modifié"
    }

    # Test avec droits GESTION
    updated_employee = UpdateService.update_employee(test_tokens['all_rights'], employee_id, update_data)
    assert updated_employee.departement == "COMMERCIAL"
    assert updated_employee.nom == "Modifié"

    # Test avec droits COMMERCIAL (doit échouer)
    with pytest.raises(PermissionError):
        UpdateService.update_employee(test_tokens['limited_rights'], employee_id, update_data)

def test_create_contract(test_tokens, test_client):
    """Test la création d'un contrat avec différents niveaux de droits"""
    contract_data = {
        "client_id": test_client,
        "montant_total": 1000.00,
        "montant_restant": 1000.00,
        "est_signe": False
    }

    # Test avec droits GESTION
    contract = CreateService.create_contract(test_tokens['all_rights'], contract_data)
    assert contract is not None
    assert contract.client_id == test_client

    # Test avec droits COMMERCIAL (doit échouer)
    with pytest.raises(PermissionError):
        CreateService.create_contract(test_tokens['limited_rights'], contract_data)

def test_update_contract(test_tokens, test_contract):
    """Test la modification d'un contrat avec différents niveaux de droits"""
    update_data = {
        "est_signe": True,
        "montant_restant": 0.00
    }

    # Test avec droits GESTION
    updated_contract = UpdateService.update_contract(test_tokens['all_rights'], test_contract, update_data)
    assert updated_contract.est_signe == True
    assert updated_contract.montant_restant == 0.00

    # Test avec droits COMMERCIAL (doit échouer)
    with pytest.raises(PermissionError):
        UpdateService.update_contract(test_tokens['limited_rights'], test_contract, update_data)

def test_create_event(test_tokens, test_contract):
    """Test la création d'un événement avec différents niveaux de droits"""
    event_data = {
        "nom": "Événement Test",
        "contrat_id": test_contract,
        "date_debut": datetime.now(),
        "date_fin": datetime.now(),
        "lieu": "Lieu de Test",
        "nb_participants": 50
    }

    # Test avec droits GESTION
    event = CreateService.create_event(test_tokens['all_rights'], event_data)
    assert event is not None
    assert event.contrat_id == test_contract

    # Test avec droits COMMERCIAL (doit échouer)
    with pytest.raises(PermissionError):
        CreateService.create_event(test_tokens['limited_rights'], event_data)

def test_update_event(test_tokens, test_contract):
    """Test la modification d'un événement avec différents niveaux de droits"""
    # Création d'un événement à modifier
    session = Session()
    event = Event(
        nom="Événement Original",
        contrat_id=test_contract,
        date_debut=datetime.now(),
        date_fin=datetime.now(),
        lieu="Lieu Original",
        nb_participants=50
    )
    session.add(event)
    session.commit()
    event_id = event.id
    session.close()

    update_data = {
        "nom": "Événement Modifié",
        "lieu": "Nouveau Lieu",
        "nb_participants": 75
    }

    # Test avec droits GESTION
    updated_event = UpdateService.update_event(test_tokens['all_rights'], event_id, update_data)
    assert updated_event.nom == "Événement Modifié"
    assert updated_event.lieu == "Nouveau Lieu"
    assert updated_event.nb_participants == 75

    # Test avec droits COMMERCIAL (doit échouer)
    with pytest.raises(PermissionError):
        UpdateService.update_event(test_tokens['limited_rights'], event_id, update_data)