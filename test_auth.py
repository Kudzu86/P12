from config.db import Session
from models.models import Employee
from models.permissions import verify_user_permission, assign_department_permissions
from auth import verify_token


def create_test_user():
    session = Session()
    try:
        existing = session.query(Employee).filter_by(username="test_user").first()
        if existing:
            # Vérifiez et assignez les permissions si nécessaire
            if not existing.permissions:
                assign_department_permissions(existing)
                session.commit()
            print("Utilisateur test existe déjà")
            return
        
        employee = Employee(
            username="test_user",
            email="test@test.com",
            nom="Test",
            prenom="User",
            departement="COMMERCIAL"
        )
        employee.set_password("test123")
        session.add(employee)
        session.commit()
        
        assign_department_permissions(employee)
        
        print("Utilisateur test créé")
        
    finally:
        session.close()


def test_permissions():
    # Lire le token
    with open('.token', 'r') as f:
        token = f.read()
    
    # Tester différentes permissions
    print(verify_user_permission(token, 'manage_clients'))  # True pour commercial
    print(verify_user_permission(token, 'manage_users'))    # False pour commercial


if __name__ == "__main__":
    create_test_user()
    test_permissions()
