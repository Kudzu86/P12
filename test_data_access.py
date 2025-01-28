from datetime import datetime
from config.db import Session
from models.models import Employee, Client, Contract, Event, Permission
from models.permissions import setup_department_permissions, assign_department_permissions
from services import DataService
from auth import create_access_token
import pytest
import uuid

def generate_unique_email():
    """Génère un email unique pour les tests"""
    return f"test_{uuid.uuid4()}@example.com"

def generate_unique_username():
    """Génère un username unique pour les tests"""
    return f"test_user_{uuid.uuid4()}"

def test_comprehensive_model_and_service_creation():
    """
    Test complet de création de modèles et vérification des services
    """
    # Configurer les permissions initiales
    setup_department_permissions()
    
    session = Session()

    try:
        # 1. Création d'un employé commercial
        commercial_username = generate_unique_username()
        commercial = Employee(
            username=commercial_username,
            email=generate_unique_email(),
            nom="Dupont",
            prenom="Jean",
            departement="COMMERCIAL"
        )
        commercial.set_password("test123")
        session.add(commercial)
        session.commit()

        # Assigner les permissions au commercial
        assign_department_permissions(commercial)
        session.commit()

        # Générer un token pour le commercial
        commercial_token = create_access_token(commercial_username)

        # 2. Création d'un client par le commercial
        client = Client(
            nom_complet="Client Test",
            email=generate_unique_email(),
            entreprise="Entreprise Test",
            commercial_id=commercial.id
        )
        session.add(client)
        session.commit()

        # 4. Création d'un employé de support
        support_username = generate_unique_username()
        support = Employee(
            username=support_username,
            email=generate_unique_email(),
            nom="Martin",
            prenom="Sophie",
            departement="SUPPORT"
        )
        support.set_password("test123")
        session.add(support)
        session.commit()

        # Assigner les permissions au support
        assign_department_permissions(support)
        session.commit()

        # Générer un token pour le support
        support_token = create_access_token(support_username)

        # 5. Création d'un contrat
        contrat = Contract(
            client_id=client.id,
            commercial_id=commercial.id,
            montant_total=1000.00,
            montant_restant=500.00,
            est_signe=False
        )
        session.add(contrat)
        session.commit()

        # 6. Création d'un événement
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

        # 7. Création d'un employé de gestion
        gestion_username = generate_unique_username()
        gestion = Employee(
            username=gestion_username,
            email=generate_unique_email(),
            nom="Admin",
            prenom="System",
            departement="GESTION"
        )
        gestion.set_password("test123")
        session.add(gestion)
        session.commit()

        # Assigner les permissions à la gestion
        assign_department_permissions(gestion)
        session.commit()

        # Générer un token pour la gestion
        gestion_token = create_access_token(gestion_username)

        # Vérifications des permissions et accès

        # Le commercial ne voit pas tous les clients (car pas de permission de gestion)
        commercial_clients = DataService.get_all_clients(commercial_token)
        assert len(commercial_clients) == 0

        # La gestion voit tous les clients
        gestion_clients = DataService.get_all_clients(gestion_token)
        assert len(gestion_clients) >= 1

        # Le commercial voit ses propres contrats
        commercial_contracts = DataService.get_all_contracts(commercial_token)
        assert len(commercial_contracts) == 1

        # La gestion voit tous les contrats
        gestion_contracts = DataService.get_all_contracts(gestion_token)
        assert len(gestion_contracts) >= 1

        # Le support ne voit pas les événements d'autres supports
        support_events = DataService.get_all_events(support_token)
        assert len(support_events) == 1

        print("Test complet de création de modèles et services réussi !")

    except Exception as e:
        session.rollback()
        raise

    finally:
        # Nettoyage
        try:
            session.query(Event).filter_by(nom="Événement de Test").delete()
            session.query(Contract).filter_by(montant_total=1000.00).delete()
            session.query(Client).filter_by(entreprise="Entreprise Test").delete()
            session.query(Employee).filter(
                Employee.username.in_([
                    commercial_username, 
                    support_username, 
                    gestion_username
                ])
            ).delete()
            session.commit()
        except Exception as e:
            session.rollback()
        finally:
            session.close()