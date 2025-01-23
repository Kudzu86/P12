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
    """
    1. Crée un dictionnaire avec :
       - 'sub' : identifiant utilisateur (username)
       - 'exp' : date d'expiration (maintenant + 30 min)
    2. Encode ce dictionnaire en JWT
    3. Retourne le token encodé
    """
    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": username, "exp": expires}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    """
    1. Décode le token avec la clé secrète
    2. Vérifie que le token n'est pas expiré
    3. Retourne le username si valide, None sinon
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        return username if username else None
    except (jwt.ExpiredSignatureError, jwt.JWTError):
        return None