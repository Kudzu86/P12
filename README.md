# Epic Events CRM

## Description


Une application en ligne de commande de gestion de relation client (CRM) pour Epic Events, une entreprise d'organisation d'événements.


## Fonctionnalités principales

Cette application permet :
- Gestion des clients et des contrats
- Gestion des événements
- Gestion des collaborateurs avec différents rôles (Commercial, Support, Gestion)
- Sécurisation des accès et filtres selon les rôles
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

### 4. Configuration


1. Installer PostgreSQL sur votre machine si ce n'est pas déjà fait
   - Windows : [Télécharger PostgreSQL](https://www.postgresql.org/download/windows/)
   - Linux : `sudo apt-get install postgresql`
   - Mac : `brew install postgresql`

2. Créer un fichier .env à la racine du projet :
```bash
DB_ENGINE=postgresql
DB_NAME=epic_events_crm
DB_USER=admin
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432
JWT_SECRET_KEY=une_clé_secrète_longue_et_aléatoire
SENTRY_DSN=votre_dsn_sentry  # À récupérer sur Sentry.io
```

3. Initialiser la base de données
```bash
python init_db.py
```

4. Identifiants

Vous pourrez vous connecter en tant qu'admin avec les identifiants suivants :

**Username : admin**
**Password : admin**

Il est recommandé de changer le mot de passe après la première connexion.



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


### Authentification

```bash
# Connexion
python cli.py auth login

# Déconnexion
python cli.py auth logout
```

### Utiliser --help


EXEMPLE :

```bash
# Listez les différents choix de mise à jour pour un client
python cli.py clients update --help                     
```

Vous aurez alors affiché :

```bash
Connexion réussie à la base de données !
Usage: cli.py clients update [OPTIONS] CLIENT_ID

  Met à jour un client existant

Options:
  --nom TEXT         Nouveau nom complet
  --email TEXT       Nouvel email
  --entreprise TEXT  Nouvelle entreprise
  --telephone TEXT   Nouveau téléphone
  --help             Show this message and exit.
```

Vous pourrez donc modifier facilement les informations du clients en faisant :

```bash
# Modification du mail du client
python cli.py clients update <client_id> --email exempleemail@exemple.com

# ou modifier son numéro de téléphone
python cli.py clients update <client_id> --telephone 0614487421
```


### Gestion des clients

```bash
# Lister les clients
python cli.py clients list

# Ajouter un client
python cli.py clients add

# Mettre à jour le nom d'un client
python cli.py clients update <client_id> --nom "Nouveau Nom"
```

### Gestion des contrats

```bash
# Lister les contrats (avec filtres selon le rôle)
python cli.py contracts list                         # Liste complète
python cli.py contracts list --filter with_support   # Contrats avec support (Gestion)
python cli.py contracts list --filter without_support # Contrats sans support (Gestion)
python cli.py contracts list --filter signed         # Contrats signés (Commercial)
python cli.py contracts list --filter unsigned       # Contrats non signés (Commercial)
python cli.py contracts list --filter fully_paid     # Contrats payés (Commercial)
python cli.py contracts list --filter not_fully_paid # Contrats non payés (Commercial)

# Ajouter un contrat (Gestion uniquement)
python cli.py contracts add

# Mettre à jour un contrat
python cli.py contracts update <contract_id> --montant-total <montant> --montant-restant <montant> --est-signe <true/false>
```

### Gestion des évenements

```bash
# Lister les événements (avec filtres pour le support)
python cli.py events list                    # Liste complète
python cli.py events list --filter my_events # Mes événements (Support)

# Ajouter un événement (Commercial pour contrats signés)
python cli.py events add

# Mettre à jour un événement
python cli.py events update <event_id> --nom "Nom" --lieu "Lieu" --date-debut "2024-12-01 14:00" --date-fin "2024-12-01 18:00"

# Assigner un support (Gestion uniquement)
python cli.py events update <event_id> --contact-support-id <support_id>
```

### Gestion des collaborateurs (Admin)

```bash
# Lister les collaborateurs
python cli.py employees list

# Ajouter un collaborateur
python cli.py employees add

# Mettre à jour le departement d'un collaborateur
python cli.py employees update <employee_id> --departement support

# Supprimer un collaborateur
python cli.py employees delete <employee_id>
```

## Structure et permissions

### Département Commercial

- Lecture complète des clients/contrats/événements
- Création et mise à jour de leurs clients
- Création d'événements pour leurs contrats signés
- Filtres spéciaux pour les contrats

### Département Support

- Lecture de tous les clients/contrats/événements
- Mise à jour des événements qui leur sont assignés
- Filtre pour voir leurs événements

### Département Gestion

- Création/modification/suppression des collaborateurs
- Gestion complète des contrats
- Assignation des événements aux supports
- Lecture et modification de toutes les données
- Filtres spéciaux pour les contrats


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

### Employees

- Username (unique)
- Mot de passe (hashé)
- Numéro employé (unique, optionnel)
- Email (unique)
- Nom
- Prénom
- Téléphone (optionnel)
- Département (COMMERCIAL, SUPPORT, GESTION)
- Date de création
- Permissions associées
- Relations avec :
      Clients (pour les commerciaux)
      Contrats (pour les commerciaux)
      Événements (pour les supports)


### Clients

- Nom complet
- Email
- Téléphone
- Entreprise
- Commercial attitré
- Date de création
- Dernière mise à jour
- Relations avec :
      Commercial attitré
      Contrats associés

### Contrats

- Client
- Commercial
- Montant total
- Montant restant
- Date de création
- Statut de signature
- Relations avec :
      Client
      Commercial
      Évènement associé

### Events

- Nom
- Contrat associé
- Contact support
- Dates (début/fin)
- Lieu
- Nombre de participants
- Notes
- Relations avec :
      Contrat
      Support assigné


## Sécurité

### Mesures de sécurité

- Authentification JWT
- Mots de passe hashés avec bcrypt
- Système de permissions basé sur les rôles
- Variables d'environnement pour les secrets
- Gestion des sessions SQLAlchemy


## Licence

Ce projet est sous licence Kudzu-licence


## Contact

AUER ERIC - ericauer86@gmail.com
Lien du projet : https://github.com/Kudzu86/P12