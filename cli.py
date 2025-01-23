import click
from auth import create_access_token, verify_token
from config.db import Session
from models.models import Employee

@click.group()
def cli():
    pass

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