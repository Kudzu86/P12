from datetime import datetime
from config.db import Session
from models.models import Employee, Client, Contract, Event
import pytest
import sqlalchemy
import uuid

def generate_unique_email():
    """Génère un email unique pour les tests"""
    return f"test_{uuid.uuid4()}@example.com"

def generate_unique_username():
    """Génère un username unique pour les tests"""
    return f"test_user_{uuid.uuid4()}"

def test_basic_model_creation():
    """
    Test basique de création et de relations entre modèles
    """
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

        # Vérifier la création de l'employé
        assert commercial.username == commercial_username
        assert commercial.check_password("test123") is True

        # 2. Création d'un client
        client = Client(
            nom_complet="Client Test",
            email=generate_unique_email(),
            entreprise="Entreprise Test",
            commercial_id=commercial.id
        )
        session.add(client)
        session.commit()

        # Vérifier les relations client-commercial
        assert len(commercial.clients) == 1
        assert commercial.clients[0] == client

        # 3. Création d'un contrat
        contrat = Contract(
            client_id=client.id,
            commercial_id=commercial.id,
            montant_total=1000.00,
            montant_restant=500.00,
            est_signe=False
        )
        session.add(contrat)
        session.commit()

        # Vérifier les relations de contrat
        assert contrat.client == client
        assert contrat.commercial == commercial

        # 4. Création d'un support
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

        # 5. Création d'un événement
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

        # Vérifier les relations d'événement
        assert event.contrat == contrat
        assert event.contact_support == support

        print("Test de création de modèles réussi !")

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
                Employee.username.in_([commercial_username, support_username])
            ).delete()
            session.commit()
        except Exception as e:
            session.rollback()
        finally:
            session.close()