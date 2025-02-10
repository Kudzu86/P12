import pytest
from logger import init_sentry, log_exception, log_employee_modification, log_contract_signature
from models.models import Employee, Contract, Client
from config.db import Session
import uuid

# Initialiser Sentry AVANT les tests
init_sentry()

def test_exception_logging():
    """Test le logging d'une exception"""
    try:
        raise ValueError("Test d'erreur volontaire")
    except Exception as e:
        log_exception(e)

def test_employee_modification():
    """Test le logging de modification d'un employé"""
    session = Session()
    try:
        # Utiliser UUID pour générer des valeurs uniques
        unique_id = str(uuid.uuid4())
        employee = Employee(
            username=f"test_sentry_{unique_id}",
            email=f"test_{unique_id}@sentry.com",
            nom="Test",
            prenom="Sentry",
            departement="COMMERCIAL"
        )
        employee.set_password("test123")
        session.add(employee)
        session.commit()
        log_employee_modification(employee, "création test")
    finally:
        session.close()

def test_contract_signature():
    """Test le logging de signature contrat"""
    session = Session()
    try:
        # Utiliser UUID pour générer des valeurs uniques
        unique_id = str(uuid.uuid4())
        client = Client(
            nom_complet="Client Test",
            email=f"client_{unique_id}@test.com",
            entreprise="Test Inc",
            telephone="0123456789"
        )
        session.add(client)
        session.commit()

        contract = Contract(
            client_id=client.id,
            montant_total=1000,
            montant_restant=1000,
            est_signe=True
        )
        session.add(contract)
        session.commit()
        log_contract_signature(contract)
    finally:
        session.close()