import click
from datetime import datetime
from auth import create_access_token, verify_token
from config.db import Session
from models.models import Employee
from crud.create import CreateService
from crud.read import ReadService
from crud.update import UpdateService
from crud.delete import DeleteService


def get_token():
    """Récupère le token stocké"""
    try:
        with open(".token", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def validate_date(ctx, param, value):
    """Valide le format de date"""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError:
        raise click.BadParameter('Le format de date doit être YYYY-MM-DD HH:MM')


@click.group()
def cli():
    """Application de gestion d'événements"""
    pass


# Groupe de commandes d'authentification
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
    try:
        employee = session.query(Employee).filter_by(username=username).first()
        
        if employee and employee.check_password(password):
            token = create_access_token(username)
            with open(".token", "w") as f:
                f.write(token)
            click.echo("Connexion réussie !")
        else:
            click.echo("Échec de l'authentification")
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
        click.echo(f"Erreur lors de la déconnexion : {str(e)}")


# Groupe de commandes pour les clients
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

    clients = ReadService.get_all_clients(token)
    if not clients:
        click.echo("Aucun client trouvé ou accès non autorisé.")
        return
    
    click.echo("\nListe des Clients:")
    for client in clients:
        click.echo(f"ID: {client.id} | {client.nom_complet} | {client.entreprise} | {client.email}")


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
        click.echo(f"Erreur lors de la mise à jour : {str(e)}")


# Groupe de commandes pour les contrats
@cli.group()
def contracts():
    """Gestion des contrats"""
    pass


@contracts.command(name="list")
def list_contracts():
    """Liste tous les contrats accessibles"""
    token = get_token()
    if not token:
        click.echo("Vous devez être connecté")
        return

    contracts = ReadService.get_all_contracts(token)
    if not contracts:
        click.echo("Aucun contrat trouvé ou accès non autorisé.")
        return
    
    click.echo("\nListe des Contrats:")
    for contract in contracts:
        click.echo(
            f"ID: {contract.id} | Client: {contract.client.nom_complet} | "
            f"Montant total: {contract.montant_total}€ | Restant: {contract.montant_restant}€ | "
            f"Signé: {'Oui' if contract.est_signe else 'Non'}"
        )


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
        click.echo(f"Erreur lors de la mise à jour : {str(e)}")


# Groupe de commandes pour les événements
@cli.group()
def events():
    """Gestion des événements"""
    pass


@events.command(name="list")
def list_events():
    """Liste tous les événements accessibles"""
    token = get_token()
    if not token:
        click.echo("Vous devez être connecté")
        return

    events = ReadService.get_all_events(token)
    if not events:
        click.echo("Aucun événement trouvé ou accès non autorisé.")
        return
    
    click.echo("\nListe des Événements:")
    for event in events:
        click.echo(
            f"ID: {event.id} | {event.nom} | "
            f"Date: {event.date_debut.strftime('%Y-%m-%d %H:%M')} | "
            f"Lieu: {event.lieu} | "
            f"Contrat: {event.contrat.client.nom_complet}"
        )

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

    employees = ReadService.get_all_employees(token)
    if not employees:
        click.echo("Aucun employé trouvé.")
        return

    for employee in employees:
        click.echo(f"ID: {employee.id} | {employee.username} | {employee.departement}")

@employees.command(name="delete")
@click.argument('employee_id', type=int)
def delete_employee(employee_id):
    """Supprime un collaborateur"""
    token = get_token()
    if not token:
        click.echo("Vous devez être connecté")
        return

    try:
        ReadService.delete_employee(token, employee_id)
        click.echo("Collaborateur supprimé avec succès")
    except Exception as e:
        click.echo(f"Erreur lors de la suppression : {str(e)}")



@events.command(name="add")
@click.option('--nom', prompt=True, help="Nom de l'événement")
@click.option('--contrat-id', type=int, prompt=True, help="ID du contrat associé")
@click.option('--date-debut', prompt=True, callback=validate_date, help="Date de début (YYYY-MM-DD HH:MM)")
@click.option('--date-fin', prompt=True, callback=validate_date, help="Date de fin (YYYY-MM-DD HH:MM)")
@click.option('--lieu', prompt=True, help="Lieu de l'événement")
@click.option('--participants', type=int, prompt=True, help="Nombre de participants")
def add_event(nom, contrat_id, date_debut, date_fin, lieu, participants):
    """Ajoute un nouvel événement"""
    token = get_token()
    if not token:
        click.echo("Vous devez être connecté")
        return

    try:
        event_data = {
            'nom': nom,
            'contrat_id': contrat_id,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'lieu': lieu,
            'nb_participants': participants
        }

        event = CreateService.create_event(token, event_data)
        click.echo(f"Événement créé avec succès !")
    except Exception as e:
        click.echo(f"Erreur lors de la création de l'événement : {str(e)}")


@events.command(name="update")
@click.argument('event_id', type=int)
@click.option('--nom', help="Nouveau nom de l'événement")
@click.option('--date-debut', callback=validate_date, help="Nouvelle date de début (YYYY-MM-DD HH:MM)")
@click.option('--date-fin', callback=validate_date, help="Nouvelle date de fin (YYYY-MM-DD HH:MM)")
@click.option('--lieu', help="Nouveau lieu")
@click.option('--participants', type=int, help="Nouveau nombre de participants")
def update_event(event_id, nom, date_debut, date_fin, lieu, participants):
    """Met à jour un événement existant"""
    token = get_token()
    if not token:
        click.echo("Vous devez être connecté")
        return

    try:
        update_data = {}
        if nom:
            update_data['nom'] = nom
        if date_debut:
            update_data['date_debut'] = date_debut
        if date_fin:
            update_data['date_fin'] = date_fin
        if lieu:
            update_data['lieu'] = lieu
        if participants is not None:
            update_data['nb_participants'] = participants

        if update_data:
            UpdateService.update_event(token, event_id, update_data)
            click.echo("Événement mis à jour avec succès !")
        else:
            click.echo("Aucune modification demandée")
    except Exception as e:
        click.echo(f"Erreur lors de la mise à jour : {str(e)}")


if __name__ == '__main__':
    cli()