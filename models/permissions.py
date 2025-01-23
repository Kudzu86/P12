from config.db import Session
from models.models import Permission, Employee
from auth import verify_token


def setup_department_permissions():
    """
    Configure les permissions initiales pour chaque département.
    Cette fonction doit être exécutée une seule fois à l'initialisation de la BDD.
    """
    # Création d'une session pour interagir avec la BDD
    session = Session()
    
    try:
        # Définition des permissions de base
        permissions = {
            'manage_users': 'Gestion collaborateurs',
            'manage_contracts': 'Gestion des contrats',
            'manage_clients': 'Gestion des clients',
            'manage_events': 'Gestion des évènements'
        }

        # Création des permissions dans la BDD si elles n'existent pas déjà
        for code, description in permissions.items():
            if not session.query(Permission).filter_by(code=code).first():
                permission = Permission(code=code, description=description)
                session.add(permission)
        
        session.commit()
        print("Permissions configurées avec succès !")

    except Exception as e:
        print(f"Erreur lors de la configuration des permissions : {e}")
        session.rollback()
    
    finally:
        session.close()


def assign_department_permissions(employee):
    """
    Attribue les permissions à un employé selon son département.
    À appeler lors de la création d'un nouvel employé.
    """
    session = Session()
    
    try:
        # Récupérer l'employé dans la session courante
        current_employee = session.merge(employee)
        
        # Attribution des permissions selon le département
        if current_employee.departement == Employee.COMMERCIAL:
            permission = session.query(Permission).filter_by(code='manage_clients').first()
            if permission not in current_employee.permissions:
                current_employee.permissions.append(permission)
        
        elif current_employee.departement == Employee.SUPPORT:
            permission = session.query(Permission).filter_by(code='manage_events').first()
            if permission not in current_employee.permissions:
                current_employee.permissions.append(permission)
        
        elif current_employee.departement == Employee.GESTION:
            manage_users = session.query(Permission).filter_by(code='manage_users').first()
            manage_contracts = session.query(Permission).filter_by(code='manage_contracts').first()
            current_employee.permissions.extend([p for p in [manage_users, manage_contracts] if p not in current_employee.permissions])
        
        session.commit()
        print(f"Permissions attribuées à {current_employee.prenom} {current_employee.nom}")

    except Exception as e:
        print(f"Erreur lors de l'attribution des permissions : {e}")
        session.rollback()
    
    finally:
        session.close()


def verify_user_permission(token: str, required_permission: str):
    username = verify_token(token)
    if not username:
        return False
        
    session = Session()
    employee = session.query(Employee).filter_by(username=username).first()
    
    for permission in employee.permissions:
        if permission.code == required_permission:
            return True
    return False