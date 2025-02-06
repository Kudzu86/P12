import sentry_sdk
from sentry_sdk import capture_exception, capture_message
import os
from dotenv import load_dotenv


load_dotenv()

def init_sentry():
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        traces_sample_rate=1.0,
        environment="development"
    )

def log_exception(error):
    """Log les exceptions inattendues"""
    capture_exception(error)

def log_employee_modification(employee, action):
    """Log les modifications des collaborateurs"""
    capture_message(
        f"Modification collaborateur: {action}",
        level="info",
        extras={
            "employee_id": employee.id,
            "username": employee.username,
            "action": action
        }
    )

def log_contract_signature(contract):
    """Log la signature d'un contrat"""
    capture_message(
        "Signature de contrat",
        level="info",
        extras={
            "contract_id": contract.id,
            "client": contract.client.nom_complet,
            "montant": contract.montant_total
        }
    )