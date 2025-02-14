from config.db import Session
from models.models import Employee
from models.permissions import setup_department_permissions, assign_department_permissions

session = Session()

# 1. S'assurer que les permissions existent
setup_department_permissions()

# 2. Créer l'admin
admin = Employee(
    username="admin",
    email="admin@example.com",
    nom="Admin",
    prenom="Admin",
    departement="GESTION"  # En majuscules comme dans vos constantes
)
admin.set_password("admin")
session.add(admin)
session.commit()

# 3. Assigner les permissions
assign_department_permissions(admin)

session.close()