import pytest
from click.testing import CliRunner
from cli import cli
from config.db import Session
from models.models import Employee, Client, Contract, Event
from models.permissions import setup_department_permissions, assign_department_permissions
from sqlalchemy import text
import os
import uuid
from datetime import datetime, timedelta


def generate_unique_email():
    return f"test_{uuid.uuid4()}@example.com"


def generate_unique_username():
    return f"test_user_{uuid.uuid4()}"


@pytest.fixture(autouse=True)
def setup():
    """Configuration de base pour tous les tests"""
    # Nettoyer la base de données
    session = Session()
    session.query(Event).delete()
    session.query(Contract).delete()
    session.query(Client).delete()
    session.execute(text('DELETE FROM employee_permissions'))
    session.query(Employee).delete()
    session.commit()
    session.close()

    # Supprimer le token s'il existe
    if os.path.exists(".token"):
        os.remove(".token")

    yield
    
    # Nettoyage après les tests
    if os.path.exists(".token"):
        os.remove(".token")


@pytest.fixture
def admin_user():
    """Crée un utilisateur admin et le connecte"""
    session = Session()
    setup_department_permissions()

    username = generate_unique_username()
    employee = Employee(
        username=username,
        email=generate_unique_email(),
        nom="Admin",
        prenom="Test",
        departement="GESTION"
    )
    employee.set_password("password123")
    session.add(employee)
    session.commit()
    assign_department_permissions(employee)
    session.commit()

    # Vérification des permissions
    employee_check = session.query(Employee).filter_by(username=username).first()
    session.close()

    # Login
    runner = CliRunner()
    runner.invoke(cli, ['auth', 'login'], input=f"{username}\npassword123\n")
    
    return runner


@pytest.fixture
def commercial_user():
    """Crée un utilisateur commercial et le connecte"""
    username = generate_unique_username()
    email = generate_unique_email()
    
    session = Session()
    setup_department_permissions()

    employee = Employee(
        username=username,
        email=email,
        nom="Commercial",
        prenom="Test",
        departement="COMMERCIAL"
    )
    employee.set_password("password123")
    session.add(employee)
    session.commit()
    assign_department_permissions(employee)
    session.commit()
    session.close()

    runner = CliRunner()
    runner.invoke(cli, ['auth', 'login'], input=f"{username}\npassword123\n")
    return runner


@pytest.fixture
def support_user():
    """Crée un utilisateur support et le connecte"""
    username = generate_unique_username()
    email = generate_unique_email()
    
    session = Session()
    setup_department_permissions()

    employee = Employee(
        username=username,
        email=email,
        nom="Support",
        prenom="Test",
        departement="SUPPORT"
    )
    employee.set_password("password123")
    session.add(employee)
    session.commit()
    assign_department_permissions(employee)
    session.commit()
    session.close()

    runner = CliRunner()
    runner.invoke(cli, ['auth', 'login'], input=f"{username}\npassword123\n")
    return runner


def test_auth():
    """Test authentification"""
    runner = CliRunner()
    username = generate_unique_username()
    password = "password123"

    # Créer un utilisateur
    session = Session()
    setup_department_permissions()
    employee = Employee(
        username=username,
        email=generate_unique_email(),
        nom="Test",
        prenom="User",
        departement="GESTION"
    )
    employee.set_password(password)
    session.add(employee)
    session.commit()
    session.close()

    # Test échec connexion
    result = runner.invoke(cli, ['auth', 'login'], 
                         input=f"{username}\nwrongpassword\n")
    assert "Échec de l'authentification" in result.output

    # Test réussite connexion
    result = runner.invoke(cli, ['auth', 'login'], 
                         input=f"{username}\n{password}\n")
    assert "Connexion réussie" in result.output

    # Test déconnexion
    result = runner.invoke(cli, ['auth', 'logout'])
    assert "Déconnexion réussie" in result.output

def test_client(admin_user):
    """Test création et liste des clients"""
    # S'assurer que les permissions sont en place
    session = Session()
    setup_department_permissions()
    session.close()

    result = admin_user.invoke(cli, ['clients', 'add'],
                             input="Test Client\ntest@test.com\nTest Enterprise\n123456789\n")
    assert result.exit_code == 0

    result = admin_user.invoke(cli, ['clients', 'list'])
    assert result.exit_code == 0
    assert "Test Client" in result.output


def test_contract(admin_user):
    """Test création et liste des contrats"""
    # Créer un client d'abord
    result = admin_user.invoke(cli, ['clients', 'add'],
                             input="Test Client\ntest@test.com\nTest Enterprise\n123456789\n")
    assert result.exit_code == 0

    # Créer un contrat
    result = admin_user.invoke(cli, ['contracts', 'add'],
                             input="1\n1000.0\n1000.0\ny\n")
    assert result.exit_code == 0


def test_event(admin_user):
    """Test création et liste des événements"""
    # Créer les prérequis
    admin_user.invoke(cli, ['clients', 'add'],
                     input="Test Client\ntest@test.com\nTest Enterprise\n123456789\n")
    admin_user.invoke(cli, ['contracts', 'add'],
                     input="1\n1000.0\n1000.0\ny\n")

    # Test simplifié : juste vérifier l'accès à la liste
    result = admin_user.invoke(cli, ['events', 'list'])
    assert result.exit_code == 0


def test_gestion_permissions(admin_user):
    """Test basique des permissions de gestion"""
    # Vérifier l'accès aux fonctionnalités de gestion
    result = admin_user.invoke(cli, ['clients', 'list'])
    assert result.exit_code == 0


def test_updates(admin_user):
    """Test la mise à jour d'un client"""
    # Créer un client
    admin_user.invoke(cli, ['clients', 'add'],
                     input="Test Client\ntest@test.com\nTest Enterprise\n123456789\n")

    # Faire une mise à jour simple
    result = admin_user.invoke(cli, ['clients', 'update', '1', '--nom', 'Updated Client'])
    assert result.exit_code == 0
    

def test_commercial_permissions(commercial_user):
    """Test les permissions du commercial"""
    # Créer un client
    result = commercial_user.invoke(cli, ['clients', 'add'],
                                  input="Test Client\ntest@test.com\nTest Enterprise\n123456789\n")
    assert "créé avec succès" in result.output

    # Vérifier accès lecture aux événements
    result = commercial_user.invoke(cli, ['events', 'list'])
    assert result.exit_code == 0  # Peut lire les événements


def test_support_permissions(support_user):
    """Test les permissions du support"""
    # Vérifier accès lecture aux clients
    result = support_user.invoke(cli, ['clients', 'list'])
    assert result.exit_code == 0

    # Vérifier accès lecture aux contrats
    result = support_user.invoke(cli, ['contracts', 'list'])
    assert result.exit_code == 0


def test_unauthorized():
    """Test accès sans authentification"""
    runner = CliRunner()
    
    # Test accès sans auth
    for resource in ['clients', 'contracts', 'events']:
        result = runner.invoke(cli, [resource, 'list'])
        assert "Vous devez être connecté" in result.output


def test_read_access_all():
    """Test que tous les utilisateurs ont accès en lecture"""
    departments = ['COMMERCIAL', 'SUPPORT', 'GESTION']
    
    for dept in departments:
        session = Session()
        username = generate_unique_username()
        
        # Créer utilisateur
        employee = Employee(
            username=username,
            email=generate_unique_email(),
            nom=f"Test {dept}",
            prenom="User",
            departement=dept
        )
        employee.set_password("password123")
        session.add(employee)
        session.commit()
        assign_department_permissions(employee)
        session.commit()
        session.close()

        # Login
        runner = CliRunner()
        runner.invoke(cli, ['auth', 'login'],
                     input=f"{username}\npassword123\n")

        # Vérifier accès lecture
        for resource in ['clients', 'contracts', 'events']:
            result = runner.invoke(cli, [resource, 'list'])
            assert result.exit_code == 0

def test_delete_employee(admin_user):
    """Test que le gestionnaire peut supprimer un collaborateur"""
    session = Session()
    username = generate_unique_username()
    email = generate_unique_email()
    
    # Créer un collaborateur
    employee = Employee(
        username=username,
        email=email,
        nom="Test Collaborateur",
        prenom="User",
        departement="COMMERCIAL"
    )
    employee.set_password("password123")
    session.add(employee)
    session.commit()

    # Récupérer l'ID de l'employé nouvellement créé
    employee_id = session.query(Employee).filter_by(username=username).first().id
    session.close()

    # Vérifier qu'il est bien créé
    result = admin_user.invoke(cli, ['employees', 'list'])
    assert username in result.output

    # Supprimer l'employé
    result = admin_user.invoke(cli, ['employees', 'delete', str(employee_id)])
    assert "Collaborateur supprimé avec succès" in result.output

    # Vérifier qu'il a été supprimé
    result = admin_user.invoke(cli, ['employees', 'list'])
    assert username not in result.output