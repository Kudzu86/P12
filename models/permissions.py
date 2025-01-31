from config.db import Session
from models.models import Permission, Employee
from auth import verify_token

def setup_department_permissions():
    """Configure les permissions initiales pour chaque département"""
    session = Session()
    
    try:
        # Permissions de base
        permissions = {
            'manage_users': 'Gestion collaborateurs',
            'delete_users': 'Suppression collaborateurs',
            'manage_contracts': 'Gestion des contrats',
            'manage_clients': 'Gestion des clients',
            'manage_events': 'Gestion des événements',
            'read_clients': 'Lecture des clients',
            'read_contracts': 'Lecture des contrats',
            'read_events': 'Lecture des événements'
        }

        # Création des permissions
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
    """Attribue les permissions selon le département"""
    session = Session()

    try:
        current_employee = session.merge(employee)
        current_employee.permissions.clear()
        
        # Permissions de lecture par défaut pour tous
        read_permissions = ['read_clients', 'read_contracts', 'read_events']
        for perm in read_permissions:
            permission = session.query(Permission).filter_by(code=perm).first()
            current_employee.permissions.append(permission)

        # Permissions spécifiques par département
        if current_employee.departement == Employee.COMMERCIAL:
            permission = session.query(Permission).filter_by(code='manage_clients').first()
            current_employee.permissions.append(permission)
        
        elif current_employee.departement == Employee.SUPPORT:
            permission = session.query(Permission).filter_by(code='manage_events').first()
            current_employee.permissions.append(permission)
        
        elif current_employee.departement == Employee.GESTION:
            permissions = [
                'manage_users', 'delete_users',  # Ajout de delete_users
                'manage_contracts', 'manage_clients', 'manage_events'
            ]
            for perm_code in permissions:
                permission = session.query(Permission).filter_by(code=perm_code).first()
                current_employee.permissions.append(permission)
        
        session.commit()
        print(f"Permissions attribuées à {current_employee.prenom} {current_employee.nom}")

    except Exception as e:
        print(f"Erreur lors de l'attribution des permissions : {e}")
        session.rollback()
    finally:
        session.close()

def verify_user_permission(token: str, required_permission: str):
    """Vérifie si l'utilisateur a la permission requise"""
    employee = verify_token(token)
    if not employee:
        return False
        
    # Autoriser la lecture pour tous
    if required_permission.startswith('read_'):
        return True

    # Vérifier les autres permissions
    for permission in employee.permissions:
        if permission.code == required_permission:
            return True
    
    return False