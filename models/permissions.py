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
        #Récupérer l'employé de la session courante
        current_employee = session.merge(employee)
        #Vider les permissions de l'employé
        current_employee.permissions.clear()
        
        if current_employee.departement == Employee.COMMERCIAL:
            permission = session.query(Permission).filter_by(code='manage_clients').first()
            current_employee.permissions.append(permission)
        
        elif current_employee.departement == Employee.SUPPORT:
            permission = session.query(Permission).filter_by(code='manage_events').first()
            current_employee.permissions.append(permission)
        
        elif current_employee.departement == Employee.GESTION:
            manage_users = session.query(Permission).filter_by(code='manage_users').first()
            manage_contracts = session.query(Permission).filter_by(code='manage_contracts').first()
            manage_clients = session.query(Permission).filter_by(code='manage_clients').first()
            manage_events = session.query(Permission).filter_by(code='manage_events').first()            
            current_employee.permissions.extend([manage_users, manage_clients, manage_events, manage_contracts])
        
        session.commit()
        print(f"Permissions attribuées à {current_employee.prenom} {current_employee.nom}")

    except Exception as e:
        print(f"Erreur lors de l'attribution des permissions : {e}")
        session.rollback()
    
    finally:
        session.close()


def verify_user_permission(token: str, required_permission: str):
    # 1. Vérifier la validité du token
    employee = verify_token(token)
    # Si le token est invalide (None ou expiré), retourne False
    if not employee:
        return False
        
    # 4. Parcourir les permissions de l'employé
    for permission in employee.permissions:
        # 5. Vérifier si l'une des permissions correspond à la permission requise
        if permission.code == required_permission:
            return True
    
    # 6. Si aucune permission ne correspond, retourne False
    return False
