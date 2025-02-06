import jwt
from datetime import datetime, timedelta
from config.db import Session
from models.models import Employee
import os
from jwt.exceptions import ExpiredSignatureError, PyJWTError


# Configuration
SECRET_KEY = os.getenv('JWT_SECRET_KEY')  # Récupère la clé du .env
ALGORITHM = "HS256"  # Algorithme de hashage pour JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Durée de validité du token

def create_access_token(username: str):

    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": username, "exp": expires}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    """
    1. Décode le token avec la clé secrète
    2. Vérifie que le token n'est pas expiré
    3. Retourne le user si valide, None sinon
    """
    try:
        # Décoder le token en utilisant la clé secrète et l'algorithme spécifié
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Récupérer le username à partir du payload
        username = payload.get("sub")
        
        # Vérifier que le username existe dans la base de données
        session = Session()
        try:
            # Rechercher l'utilisateur pour s'assurer qu'il existe
            employee = session.query(Employee).filter_by(username=username).first()
            
            # Retourner le username uniquement si l'utilisateur existe
            return employee
        finally:
            # Toujours fermer la session
            session.close()
    
    except (jwt.ExpiredSignatureError, jwt.PyJWTError) as e:
        # Gérer les erreurs d'expiration ou de décodage du token
        # Retourner None en cas d'erreur
        return None