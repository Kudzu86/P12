import bcrypt

# Test simple de hashage
password = "motdepasse123"

# Convertir en bytes et hasher
password_bytes = password.encode('utf-8')
hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

print("Mot de passe original:", password)
print("Mot de passe hashé:", hashed)

# Vérifier le mot de passe
is_valid = bcrypt.checkpw(password_bytes, hashed)
print("Vérification réussie:", is_valid)

# Test avec mauvais mot de passe
wrong_password = "mauvaismdp"
is_wrong = bcrypt.checkpw(wrong_password.encode('utf-8'), hashed)
print("Mauvais mot de passe accepté:", is_wrong)