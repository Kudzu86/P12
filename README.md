# Epic Events CRM

## Description


Une application en ligne de commande de gestion de relation client (CRM) pour Epic Events, une entreprise d'organisation d'événements.


## Fonctionnalités principales

Cette application permet :
- Gestion des clients et des contrats
- Gestion des événements
- Gestion des collaborateurs avec différents rôles (Commercial, Support, Gestion)
- Sécurisation des accès selon les rôles
- Suivi des erreurs avec Sentry

## Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants installés sur votre machine :

- Python 3.9+
- PostgreSQL
- pip

## Installation

### 1. Cloner le repository

```bash
git clone https://github.com/Kudzu86/P12
cd P12
```

### 2. Créer un environnement virtuel

```bash
python -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Ouvrir un second terminal

Ouvrez un second terminal pour ouvrir la base de données d'un coté et rentrer les commandes python de l'autre.
Entrer dans l'environnement virtuel dans ce terminal également :
```bash
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows
```
### 5. Configurer la base de données


1. Installer PostgreSQL sur votre machine si ce n'est pas déjà fait
   - Windows : [Télécharger PostgreSQL](https://www.postgresql.org/download/windows/)
   - Linux : `sudo apt-get install postgresql`
   - Mac : `brew install postgresql`

2. Se connecter à PostgreSQL et créer la base de données :
```bash
psql -U postgres -d epic_events_crm
```

3. Initialiser la base de données
```bash
python init_db.py
```

4. Créer un premier utilisateur administrateur :
```bash
python manage.py create_admin
```
Cela créera un utilisateur par défaut avec les identifiants suivants :

**Username : test_admin**
**Password : admin123**

Il est recommandé de changer le mot de passe après la première connexion.

### 6. Configuration

Créer un fichier .env à la racine du projet :

```bash
DB_ENGINE=postgresql
DB_NAME=epic_events_crm
DB_USER=admin           # L'utilisateur créé à l'étape précédente
DB_PASSWORD=secure_password  # Le mot de passe choisi à l'étape précédente
DB_HOST=localhost
DB_PORT=5432
JWT_SECRET_KEY=une_clé_secrète_longue_et_aléatoire
SENTRY_DSN=votre_dsn_sentry  # À récupérer sur Sentry.io
```


## Dépendances principales

- Click : Interface en ligne de commande
- SQLAlchemy : ORM pour la base de données
- PyJWT : Gestion des tokens d'authentification
- Sentry-SDK : Suivi des erreurs
- Pytest : Tests unitaires


## Structure du projet

P12/
├── config/
│   └── db.py
├── crud/
│   ├── create.py
│   ├── read.py
│   ├── update.py
│   └── delete.py
├── models/
│   ├── models.py
│   └── permissions.py
├── tests/
│   └── ...
├── auth.py
├── cli.py
├── diagramme.md
├── logger.py
├── manage.py
├── README.md 
└── requirements.txt


## Utilisation

**ATTENTION :** Ces commandes doivent être exécutées dans le terminal Python, et non dans celui de PostgreSQL (psql) !

### Authentification

```bash
# Connexion
python cli.py auth login

# Déconnexion
python cli.py auth logout
```

### Gestion des clients

```bash
# Lister les clients
python cli.py clients list

# Ajouter un client
python cli.py clients add

# Mettre à jour un client
python cli.py clients update <client_id>
```

### Gestion des contrats

```bash
# Lister les contrats
python cli.py contracts list

# Ajouter un contrat
python cli.py contracts add

# Mettre à jour un contrat
python cli.py contracts update <contract_id>
```

### Gestion des évenements

```bash
# Lister les événements
python cli.py events list

# Ajouter un événement
python cli.py events add

# Mettre à jour un événement
python cli.py events update <event_id>
```

### Gestion des collaborateurs (Admin)

```bash
# Lister les collaborateurs
python cli.py employees list

# Supprimer un collaborateur
python cli.py employees delete <employee_id>
```

## Structure et permissions

### Département Commercial

- Création et mise à jour de leurs clients
- Création d'événements pour leurs clients
- Lecture de tous les contrats/événements

### Département Support

- Mise à jour des événements qui leur sont assignés
- Lecture de tous les clients/contrats/événements

### Département Gestion

- Création/modification/suppression des collaborateurs
- Gestion complète des contrats
- Assignation des événements aux supports
- Lecture et modification de toutes les données


## Configuration Sentry

### 1. Créer un compte sur Sentry

- Se rendre sur Sentry.io
- Créer un nouveau compte ou se connecter

### 2. Configurer un projet

- Créer un nouveau projet Python
- Copier la clé DSN fournie
- La coller dans le fichier .env à la place de "votre_dsn_sentry"

```bash
# Ligne à modifier
SENTRY_DSN=votre_dsn_sentry
```


## Tests

### Exécuter les tests avec pytest

```bash
# Exécuter tous les tests
pytest -v

# Exécuter des tests spécifiques
pytest -v tests/test_crud.py      # Tests CRUD
pytest -v tests/test_auth.py      # Tests authentification
pytest -v tests/test_logger.py    # Tests Sentry
pytest -v tests/test_cli.py       # Tests interface CLI
```


## Modèles de données

### Client

- Nom complet
- Email
- Téléphone
- Entreprise
- Commercial attitré
- Date de création
- Dernière mise à jour

### Contrat

- Client
- Commercial
- Montant total
- Montant restant
- Date de création
- Statut de signature

### Événement

- Nom
- Contrat associé
- Contact support
- Dates (début/fin)
- Lieu
- Nombre de participants
- Notes


## Sécurité

### Mesures de sécurité

- Authentification JWT
- Système de permissions basé sur les rôles
- Variables d'environnement pour les secrets


## Licence

Ce projet est sous licence Kudzu-licence


## Contact

AUER ERIC - ericauer86@gmail.com
Lien du projet : https://github.com/Kudzu86/P12