from datetime import datetime
from config.db import Session
from models.models import Employee, Client, Contract, Event, Permission
from models.permissions import setup_department_permissions, assign_department_permissions
from crud.read import ReadService
from auth import create_access_token
from sqlalchemy import text
import pytest
import uuid


def generate_unique_email():
    return f"test_{uuid.uuid4()}@example.com"


def generate_unique_username():
    return f"test_user_{uuid.uuid4()}"


def clean_database(session):
    """Nettoie la base de données dans le bon ordre"""
    try:
        session.query(Event).delete()
        session.query(Contract).delete()
        session.query(Client).delete()
        session.execute(text('DELETE FROM employee_permissions'))
        session.query(Employee).delete()
        session.commit()
    except Exception:
        session.rollback()
        raise


@pytest.fixture(scope="function")
def setup_test_data():
    """Fixture pour configurer les données de test"""
    session = Session()
    
    # Nettoyage initial
    clean_database(session)
    
    # Configuration initiale des permissions
    setup_department_permissions()

    try:
        # 1. Création du commercial
        commercial = Employee(
            username=generate_unique_username(),
            email=generate_unique_email(),
            nom="Dupont",
            prenom="Jean",
            departement="COMMERCIAL"
        )
        commercial.set_password("test123")
        session.add(commercial)
        session.commit()
        assign_department_permissions(commercial)

        # 2. Création du support
        support = Employee(
            username=generate_unique_username(),
            email=generate_unique_email(),
            nom="Martin",
            prenom="Sophie",
            departement="SUPPORT"
        )
        support.set_password("test123")
        session.add(support)
        session.commit()
        assign_department_permissions(support)

        # 3. Création de la gestion
        gestion = Employee(
            username=generate_unique_username(),
            email=generate_unique_email(),
            nom="Admin",
            prenom="System",
            departement="GESTION"
        )
        gestion.set_password("test123")
        session.add(gestion)
        session.commit()
        assign_department_permissions(gestion)

        # 4. Création du client
        client = Client(
            nom_complet="Client Test",
            email=generate_unique_email(),
            entreprise="Entreprise Test",
            commercial_id=commercial.id
        )
        session.add(client)
        session.commit()

        # 5. Création du contrat
        contrat = Contract(
            client_id=client.id,
            commercial_id=commercial.id,
            montant_total=1000.00,
            montant_restant=500.00,
            est_signe=False
        )
        session.add(contrat)
        session.commit()

        # 6. Création de l'événement
        event = Event(
            nom="Événement de Test",
            contrat_id=contrat.id,
            contact_support_id=support.id,
            date_debut=datetime.now(),
            date_fin=datetime.now(),
            lieu="Lieu de Test",
            nb_participants=10
        )
        session.add(event)
        session.commit()

        # Création des tokens
        tokens = {
            'commercial': create_access_token(commercial.username),
            'support': create_access_token(support.username),
            'gestion': create_access_token(gestion.username)
        }

        test_data = {
            'tokens': tokens,
            'employees': {'commercial': commercial, 'support': support, 'gestion': gestion},
            'client': client,
            'contrat': contrat,
            'event': event
        }

        yield test_data

    except Exception:
        session.rollback()
        raise

    finally:
        clean_database(session)
        session.close()


@pytest.fixture(autouse=True)
def session():
    """Fixture pour gérer la session de base de données"""
    session = Session()
    yield session
    session.close()


def test_commercial_access(setup_test_data, session):
    """Test des accès du commercial"""
    tokens = setup_test_data['tokens']
    
    # Test accès aux clients
    commercial_clients = ReadService.get_all_clients(tokens['commercial'])
    assert len(commercial_clients) == 1
    assert commercial_clients[0].nom_complet == "Client Test"

    # Test accès aux contrats
    commercial_contracts = ReadService.get_all_contracts(tokens['commercial'])
    assert len(commercial_contracts) == 1
    assert commercial_contracts[0].montant_total == 1000.00


def test_support_access(setup_test_data, session):
    """Test des accès du support"""
    tokens = setup_test_data['tokens']
    
    # Test accès aux événements
    support_events = ReadService.get_all_events(tokens['support'])
    assert len(support_events) == 1
    assert support_events[0].nom == "Événement de Test"

    # Test accès aux clients (ne devrait pas en voir)
    support_clients = ReadService.get_all_clients(tokens['support'])
    assert len(support_clients) == 0


def test_gestion_access(setup_test_data, session):
    """Test des accès de la gestion"""
    tokens = setup_test_data['tokens']
    
    # Test accès à toutes les données
    gestion_clients = ReadService.get_all_clients(tokens['gestion'])
    assert len(gestion_clients) == 1

    gestion_contracts = ReadService.get_all_contracts(tokens['gestion'])
    assert len(gestion_contracts) == 1

    gestion_events = ReadService.get_all_events(tokens['gestion'])
    assert len(gestion_events) == 1