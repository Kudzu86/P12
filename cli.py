import click
from datetime import datetime
from auth import create_access_token, verify_token
from config.db import Session
from models.models import Employee
from crud.create import CreateService
from crud.read import ReadService, ContractFilterGestion, ContractFilterCommercial, EventFilterSupport
from crud.update import UpdateService
from crud.delete import DeleteService
from logger import init_sentry, log_exception

# Initialisation de Sentry au démarrage de l'application
init_sentry()

def get_token():
    """Récupère le token stocké dans le fichier .token"""
    try:
        with open(".token", "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def validate_date(ctx, param, value):
    """
    Valide le format de date pour les entrées utilisateur.
    Format attendu : YYYY-MM-DD HH:MM
    """
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError:
        raise click.BadParameter('Le format de date doit être YYYY-MM-DD HH:MM')

@click.group()
def cli():
    """Application de gestion d'événements Epic Events"""
    pass

# === Groupe de commandes d'authentification ===
@cli.group()
def auth():
    """Commandes d'authentification"""
    pass

@auth.command()
@click.option("--username", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
def login(username, password):
    """Authentification de l'utilisateur"""
    session = Session()
    print(f"Connexion à la base de données : {session.bind.url}")
    print(f"Username: {username}")

    try:
        employee = session.query(Employee).filter_by(username=username).first()
        if employee and employee.check_password(password):
            token = create_access_token(username)
            with open(".token", "w", encoding='utf-8') as f:
                f.write(token)
            click.echo("Connexion réussie !")
        else:
            click.echo("Échec de l'authentification")
    except Exception as e:
        log_exception(e)
        click.echo(f"Erreur lors de l'authentification: {str(e)}")
    finally:
        session.close()

@auth.command()
def logout():
    """Déconnexion de l'utilisateur"""
    try:
        with open(".token", "w") as f:
            f.write("")
        click.echo("Déconnexion réussie !")
    except Exception as e:
        log_exception(e)
        click.echo(f"Erreur lors de la déconnexion : {str(e)}")

# === Groupe de commandes pour les clients ===
@cli.group()
def clients():
    """Gestion des clients"""
    pass

@clients.command(name="list")
def list_clients():
    """Liste tous les clients accessibles"""
    token = get_token()
    if not token:
        click.echo("Vous devez être connecté")
        return

    try:
        clients = ReadService.get_all_clients(token)
        if not clients:
            click.echo("Aucun client trouvé ou accès non autorisé.")
            return
        
        click.echo("\nListe des Clients:")
        for client in clients:
            commercial = "Non assigné"
            if client.commercial_attitré:
                commercial = client.commercial_attitré.username
                
            click.echo(
                f"ID: {client.id} | "
                f"Nom complet: {client.nom_complet} | "
                f"Email: {client.email} | "
                f"Entreprise: {client.entreprise} | "
                f"Téléphone: {client.telephone or 'Non renseigné'} | "
                f"Commercial: {commercial} | "
                f"Date création: {client.date_creation.strftime('%Y-%m-%d %H:%M')} | "
                f"Dernière mise à jour: {client.derniere_mise_a_jour.strftime('%Y-%m-%d %H:%M')}"
            )
    except Exception as e:
        log_exception(e)
        click.echo(f"Erreur lors de la récupération des clients : {str(e)}")

@clients.command(name="add")
@click.option('--nom', prompt=True, help="Nom complet du client")
@click.option('--email', prompt=True, help="Email du client")
@click.option('--entreprise', prompt=True, help="Nom de l'entreprise")
@click.option('--telephone', prompt=True, help="Numéro de téléphone", default="")
def add_client(nom, email, entreprise, telephone):
    """Ajoute un nouveau client"""
    token = get_token()
    if not token:
        click.echo("Vous devez être connecté")
        return

    try:
        client_data = {
            'nom_complet': nom,
            'email': email,
            'entreprise': entreprise,
            'telephone': telephone
        }
        client = CreateService.create_client(token, client_data)
        click.echo(f"Client {client.nom_complet} créé avec succès !")
    except Exception as e:
        log_exception(e)
        click.echo(f"Erreur lors de la création du client : {str(e)}")

@clients.command(name="update")
@click.argument('client_id', type=int)
@click.option('--nom', help="Nouveau nom complet")
@click.option('--email', help="Nouvel email")
@click.option('--entreprise', help="Nouvelle entreprise")
@click.option('--telephone', help="Nouveau téléphone")
def update_client(client_id, nom, email, entreprise, telephone):
    """Met à jour un client existant"""
    token = get_token()
    if not token:
        click.echo("Vous devez être connecté")
        return

    try:
        update_data = {}
        if nom:
            update_data['nom_complet'] = nom
        if email:
            update_data['email'] = email
        if entreprise:
            update_data['entreprise'] = entreprise
        if telephone:
            update_data['telephone'] = telephone

        if update_data:
            UpdateService.update_client(token, client_id, update_data)
            click.echo("Client mis à jour avec succès !")
        else:
            click.echo("Aucune modification demandée")
    except Exception as e:
        log_exception(e)
        click.echo(f"Erreur lors de la mise à jour : {str(e)}")

# === Groupe de commandes pour les contrats ===
@cli.group()
def contracts():
    """Gestion des contrats"""
    pass

@contracts.command(name="list")
@click.option('--filter', 'filter_mode',
              type=click.Choice(['all', 'with_support', 'without_support',
                               'signed', 'unsigned', 'fully_paid', 'not_fully_paid']),
              default='all',
              help="Mode de filtrage des contrats selon le rôle")
def list_contracts(filter_mode):
    """Liste tous les contrats accessibles avec options de filtrage"""
    token = get_token()
    if not token:
        click.echo("Vous devez être connecté")
        return

    try:
        # Déterminer le type de filtre selon le rôle
        employee = verify_token(token)
        session = Session()
        current_user = session.query(Employee).filter_by(username=employee.username).first()
        
        if current_user.departement == Employee.GESTION:
            filter_enum = ContractFilterGestion(filter_mode) if filter_mode in ['all', 'with_support', 'without_support'] else None
        elif current_user.departement == Employee.COMMERCIAL:
            filter_enum = ContractFilterCommercial(filter_mode) if filter_mode in ['all', 'signed', 'unsigned', 'fully_paid', 'not_fully_paid'] else None
        else:
            filter_enum = None

        contracts = ReadService.get_all_contracts(token, filter_enum)
        if not contracts:
            click.echo("Aucun contrat trouvé ou accès non autorisé.")
            return
        
        click.echo("\nListe des Contrats:")
        for contract in contracts:
            # Gestion de l'affichage du support
            support_info = "Non assigné"
            if hasattr(contract, 'evenement') and contract.evenement and contract.evenement.contact_support:
                support_info = contract.evenement.contact_support.username

            # Gestion de l'affichage du commercial
            commercial_info = "Non assigné"
            if contract.commercial:
                commercial_info = contract.commercial.username
                
            click.echo(
                f"ID: {contract.id} | "
                f"Client: {contract.client.nom_complet} | "
                f"Commercial: {commercial_info} | "
                f"Montant total: {contract.montant_total}€ | "
                f"Montant restant: {contract.montant_restant}€ | "
                f"Signé: {'Oui' if contract.est_signe else 'Non'} | "
                f"Date création: {contract.date_creation.strftime('%Y-%m-%d %H:%M')} | "
                f"Support: {support_info}"
            )
    except Exception as e:
        log_exception(e)
        click.echo(f"Erreur lors de la récupération des contrats : {str(e)}")
    finally:
        session.close()


@contracts.command(name="add")
@click.option('--client-id', type=int, prompt=True, help="ID du client")
@click.option('--montant-total', type=float, prompt=True, help="Montant total du contrat")
@click.option('--montant-restant', type=float, prompt=True, help="Montant restant à payer")
@click.option('--est-signe', is_flag=True, prompt=True, help="Le contrat est-il signé ?")
def add_contract(client_id, montant_total, montant_restant, est_signe):
    """Ajoute un nouveau contrat"""
    token = get_token()
    if not token:
        click.echo("Vous devez être connecté")
        return

    try:
        contract_data = {
            'client_id': client_id,
            'montant_total': montant_total,
            'montant_restant': montant_restant,
            'est_signe': est_signe
        }

        contract = CreateService.create_contract(token, contract_data)
        click.echo(f"Contrat créé avec succès !")
    except Exception as e:
        log_exception(e)
        click.echo(f"Erreur lors de la création du contrat : {str(e)}")


@contracts.command(name="update")
@click.argument('contract_id', type=int)
@click.option('--montant-total', type=float, help="Nouveau montant total")
@click.option('--montant-restant', type=float, help="Nouveau montant restant")
@click.option('--est-signe', type=bool, help="Nouveau statut de signature")
def update_contract(contract_id, montant_total, montant_restant, est_signe):
    """Met à jour un contrat existant"""
    token = get_token()
    if not token:
        click.echo("Vous devez être connecté")
        return

    try:
        update_data = {}
        if montant_total is not None:
            update_data['montant_total'] = montant_total
        if montant_restant is not None:
            update_data['montant_restant'] = montant_restant
        if est_signe is not None:
            update_data['est_signe'] = est_signe

        if update_data:
            UpdateService.update_contract(token, contract_id, update_data)
            click.echo("Contrat mis à jour avec succès !")
        else:
            click.echo("Aucune modification demandée")
    except Exception as e:
        log_exception(e)
        click.echo(f"Erreur lors de la mise à jour : {str(e)}")

@cli.group()
def employees():
   """Gestion des collaborateurs"""
   pass


@employees.command(name="list")
def list_employees():
   """Liste tous les employés"""
   token = get_token()
   if not token:
       click.echo("Vous devez être connecté")
       return

   try:
       employees = ReadService.get_all_employees(token)
       if not employees:
           click.echo("Aucun employé trouvé.")
           return

       for employee in employees:
           click.echo(
                f"ID: {employee.id} | "
                f"Username: {employee.username} | "
                f"Nom: {employee.nom} | "
                f"Prénom: {employee.prenom} | "
                f"Email: {employee.email} | "
                f"Téléphone: {employee.telephone or 'Non renseigné'} | "
                f"Département: {employee.departement} | "
                f"Date création: {employee.date_creation.strftime('%Y-%m-%d %H:%M')} | "
            )
   except Exception as e:
       log_exception(e)
       click.echo(f"Erreur lors de la récupération des employés : {str(e)}")


@employees.command(name="add")
@click.option('--username', prompt=True, help="Nom d'utilisateur")
@click.option('--email', prompt=True, help="Email")
@click.option('--nom', prompt=True, help="Nom")
@click.option('--prenom', prompt=True, help="Prénom")
@click.option('--telephone', prompt=True, help="Téléphone", default="")
@click.option('--departement', type=click.Choice(['COMMERCIAL', 'SUPPORT', 'GESTION'], case_sensitive=False), prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
def add_employee(username, email, nom, prenom, telephone, departement, password):
    """Ajoute un nouveau collaborateur"""
    token = get_token()
    if not token:
        click.echo("Vous devez être connecté")
        return

    try:
        employee_data = {
            'username': username,
            'email': email,
            'nom': nom,
            'prenom': prenom,
            'telephone': telephone,
            'departement': departement.upper(),
            'password': password
        }

        employee = CreateService.create_employee(token, employee_data)
        click.echo(f"Collaborateur {employee.prenom} {employee.nom} créé avec succès !")
    except Exception as e:
        log_exception(e)
        click.echo(f"Erreur lors de la création du collaborateur : {str(e)}")


@employees.command(name="update")
@click.argument('employee_id', type=int)
@click.option('--username', help="Nouveau nom d'utilisateur")
@click.option('--email', help="Nouvel email")
@click.option('--nom', help="Nouveau nom")
@click.option('--prenom', help="Nouveau prénom")
@click.option('--telephone', help="Nouveau téléphone")
@click.option('--departement', type=click.Choice(['COMMERCIAL', 'SUPPORT', 'GESTION'], case_sensitive=False))
@click.option('--password', help="Nouveau mot de passe", hide_input=True)
def update_employee(employee_id, username, email, nom, prenom, telephone, departement, password):
    """Met à jour un collaborateur existant"""
    token = get_token()
    if not token:
        click.echo("Vous devez être connecté")
        return

    try:
        update_data = {}
        if username:
            update_data['username'] = username
        if email:
            update_data['email'] = email
        if nom:
            update_data['nom'] = nom
        if prenom:
            update_data['prenom'] = prenom
        if telephone:
            update_data['telephone'] = telephone
        if departement:
            update_data['departement'] = departement.upper()
        if password:
            update_data['password'] = password

        if update_data:
            UpdateService.update_employee(token, employee_id, update_data)
            click.echo("Collaborateur mis à jour avec succès !")
        else:
            click.echo("Aucune modification demandée")
    except Exception as e:
        log_exception(e)
        click.echo(f"Erreur lors de la mise à jour : {str(e)}")


@employees.command(name="delete")
@click.argument('employee_id', type=int)
def delete_employee(employee_id):
   """Supprime un collaborateur"""
   token = get_token()
   if not token:
       click.echo("Vous devez être connecté")
       return

   try:
       DeleteService.delete_employee(token, employee_id)
       click.echo("Collaborateur supprimé avec succès")
   except Exception as e:
       log_exception(e)
       click.echo(f"Erreur lors de la suppression : {str(e)}")

       
# Groupe de commandes pour les événements
@cli.group()
def events():
    """Gestion des événements"""
    pass

@events.command(name="list")
@click.option('--filter', 'filter_mode',
              type=click.Choice(['all', 'my_events']),
              default='all',
              help="Mode de filtrage des événements")
def list_events(filter_mode):
    """
    Liste les événements avec option de filtrage :
    - Tous les événements (all)
    - Uniquement mes événements (my_events) pour les supports
    """
    token = get_token()
    if not token:
        click.echo("Vous devez être connecté")
        return

    try:
        # Convertir le mode de filtrage en enum
        filter_enum = EventFilterSupport(filter_mode) if filter_mode in ['all', 'my_events'] else None
        
        events = ReadService.get_all_events(token, filter_enum)
        if not events:
            click.echo("Aucun événement trouvé ou accès non autorisé.")
            return
        
        click.echo("\nListe des Événements:")
        for event in events:
            support_info = event.contact_support.username if event.contact_support else "Non assigné"
            click.echo(
                f"ID: {event.id} | {event.nom} | "
                f"Date: {event.date_debut.strftime('%Y-%m-%d %H:%M')} | "
                f"Lieu: {event.lieu} | "
                f"Contrat: {event.contrat.client.nom_complet} | "
                f"Support: {support_info} | "
                f"Participants: {event.nb_participants or 'Non renseigné'} | "
                f"Notes: {event.notes or 'Aucune'}" 
            )
    except Exception as e:
        log_exception(e)
        click.echo(f"Erreur lors de la récupération des événements : {str(e)}")


@events.command(name="add")
@click.option('--nom', prompt=True, help="Nom de l'événement")
@click.option('--lieu', prompt=True, help="Lieu de l'événement")
@click.option('--date-debut', type=click.DateTime(formats=["%Y-%m-%d %H:%M"]), prompt=True, help="Date de début")
@click.option('--date-fin', type=click.DateTime(formats=["%Y-%m-%d %H:%M"]), prompt=True, help="Date de fin")
@click.option('--contrat-id', type=int, prompt=True, help="ID du contrat associé")
@click.option('--nb-participants', type=int, prompt=True, help="Nombre de participants", default=0)
@click.option('--notes', help="Notes sur l'événement", default="")
def add_event(nom, lieu, date_debut, date_fin, contrat_id, nb_participants, notes):
    """Ajoute un nouvel événement"""
    token = get_token()
    if not token:
        click.echo("Vous devez être connecté")
        return

    try:
        event_data = {
            'nom': nom,
            'lieu': lieu,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'contrat_id': contrat_id,
            'nb_participants': nb_participants,
            'notes': notes
        }

        event = CreateService.create_event(token, event_data)
        click.echo(f"Événement créé avec succès !")
    except Exception as e:
        log_exception(e)
        click.echo(f"Erreur lors de la création de l'événement : {str(e)}")


@events.command(name="update")
@click.argument('event_id', type=int)
@click.option('--nom', help="Nouveau nom de l'événement")
@click.option('--lieu', help="Nouveau lieu")
@click.option('--date-debut', type=click.DateTime(formats=["%Y-%m-%d %H:%M"]), help="Nouvelle date de début")
@click.option('--date-fin', type=click.DateTime(formats=["%Y-%m-%d %H:%M"]), help="Nouvelle date de fin")
@click.option('--contrat-id', type=int, help="Nouveau ID de contrat")
@click.option('--contact-support-id', type=int, help="ID du support assigné")
@click.option('--nb-participants', type=int, help="Nombre de participants")
@click.option('--notes', help="Notes sur l'événement", required=False, default="")
def update_event(event_id, nom, lieu, date_debut, date_fin, contrat_id, contact_support_id, nb_participants, notes):
    """Met à jour un événement existant"""
    token = get_token()
    if not token:
        click.echo("Vous devez être connecté")
        return

    try:
        update_data = {}
        if nom:
            update_data['nom'] = nom
        if lieu:
            update_data['lieu'] = lieu
        if date_debut:
            update_data['date_debut'] = date_debut
        if date_fin:
            update_data['date_fin'] = date_fin
        if contrat_id:
            update_data['contrat_id'] = contrat_id
        if contact_support_id:
            update_data['contact_support_id'] = contact_support_id
        if nb_participants is not None:
            update_data['nb_participants'] = nb_participants
        if notes:
            update_data['notes'] = notes

        if update_data:
            UpdateService.update_event(token, event_id, update_data)
            click.echo("Événement mis à jour avec succès !")
        else:
            click.echo("Aucune modification demandée")
    except Exception as e:
        log_exception(e)
        click.echo(f"Erreur lors de la mise à jour : {str(e)}")


if __name__ == "__main__":
    cli()
