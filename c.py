from config.db import Session
from models.models import Employee

session = Session()

admin = Employee(
    username="admin",
    email="admin@example.com",
    nom="Admin",
    prenom="Admin",
    departement="Gestion"
)
admin.set_password("admin")
session.add(admin)
session.commit()
session.close()
