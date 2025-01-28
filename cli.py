import click
from auth import create_access_token, verify_token
from config.db import Session
from models.models import Employee
from services import DataService

@cli.group()
def list():
    """Commandes pour lister les données"""
    pass

@list.command('clients')
@click.option('--token', prompt=True, help='Token d\'authentification')
def list_clients(token):
    """Lister tous les clients accessibles"""
    clients = DataService.get_all_clients(token)
    if not clients:
        click.echo("Aucun client trouvé ou accès non autorisé.")
        return
    
    for client in clients:
        click.echo(f"{client.nom_complet} - {client.entreprise}")

@list.command('contracts')
@click.option('--token', prompt=True, help='Token d\'authentification')
def list_contracts(token):
    """Lister tous les contrats accessibles"""
    contracts = DataService.get_all_contracts(token)
    if not contracts:
        click.echo("Aucun contrat trouvé ou accès non autorisé.")
        return
    
    for contract in contracts:
        click.echo(f"Contrat {contract.id} - Client: {contract.client.nom_complet}")

@list.command('events')
@click.option('--token', prompt=True, help='Token d\'authentification')
def list_events(token):
    """Lister tous les événements accessibles"""
    events = DataService.get_all_events(token)
    if not events:
        click.echo("Aucun événement trouvé ou accès non autorisé.")
        return
    
    for event in events:
        click.echo(f"{event.nom} - Date: {event.date_debut}")

@cli.command()
@click.option("--username", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
def login(username, password):
    """Authentification de l'utilisateur"""
    session = Session()
    employee = session.query(Employee).filter_by(username=username).first()
    
    if employee and employee.check_password(password):
        token = create_access_token(username)
        # Sauvegarder le token dans un fichier
        with open(".token", "w") as f:
            f.write(token)
        click.echo("Connexion réussie!")
    else:
        click.echo("Échec de l'authentification")
    
    session.close()

if __name__ == "__main__":
    cli()