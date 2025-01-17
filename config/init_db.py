from config.db import Base, engine
from models.models import Employee, Permission, Client, Contract, Event
from models.permissions import setup_department_permissions

def init_database():
    """Initialise la base de données et configure les permissions"""
    # Création de toutes les tables définies dans models.py
    Base.metadata.create_all(engine)
    print("Tables créées avec succès !")
    
    # Configuration des permissions de base
    setup_department_permissions()

if __name__ == "__main__":
    init_database()