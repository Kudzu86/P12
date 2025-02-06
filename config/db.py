from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker, declarative_base
import os


# Charger les variables d'environnement
load_dotenv()

# Récupérer les informations de connexion
DB_ENGINE = os.getenv("DB_ENGINE")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

    
# Construire l'URL de connexion
DATABASE_URL = f"{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Créer l'engine SQLAlchemy
engine = create_engine(DATABASE_URL)

# Créer une Session factory - elle va nous permettre de créer des sessions
Session = sessionmaker(bind=engine)

# Créer la classe Base dont vont hériter tous nos modèles
Base = declarative_base()

# Tester la connexion
try:
    with engine.connect() as connection:
        print("Connexion réussie à la base de données !")
except Exception as e:
    print("Erreur de connexion :", e)