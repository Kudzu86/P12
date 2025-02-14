from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from config.db import Session
from models.models import Employee, Client, Contract, Event
from auth import verify_token
from enum import Enum


# Définition des types de filtres disponibles
class ContractFilterGestion(Enum):
    """Filtres disponibles pour les contrats (utilisateurs GESTION)"""
    ALL = "all"
    WITH_SUPPORT = "with_support"
    WITHOUT_SUPPORT = "without_support"

class ContractFilterCommercial(Enum):
    """Filtres disponibles pour les contrats (utilisateurs COMMERCIAL)"""
    ALL = "all"
    SIGNED = "signed"
    UNSIGNED = "unsigned"
    FULLY_PAID = "fully_paid"
    NOT_FULLY_PAID = "not_fully_paid"

class EventFilterSupport(Enum):
    """Filtres disponibles pour les événements (utilisateurs SUPPORT)"""
    ALL = "all"
    MY_EVENTS = "my_events"


class ReadService:
    @staticmethod
    def get_all_clients(token):
        """
        Récupère tous les clients de la base de données.
        Tous les collaborateurs peuvent voir tous les clients en lecture seule.
        Charge la relation avec le commercial pour l'affichage.
        
        Args:
            token: Token d'authentification de l'utilisateur

        Returns:
            Liste complète des clients avec leurs commerciaux associés
        """
        employee = verify_token(token)
        if not employee:
            return []
        
        session = Session()
        try:
            current_user = session.query(Employee).filter_by(username=employee.username).first()
            if not current_user:
                return []
            
            # Chargement des clients avec leur commercial
            return session.query(Client)\
                .options(joinedload(Client.commercial_attitré))\
                .order_by(Client.id)\
                .all()
        finally:
            session.close()

    @staticmethod
    def get_all_contracts(token, filter_mode=None):
        employee = verify_token(token)
        if not employee:
            return []

        session = Session()
        try:
            current_user = session.query(Employee).filter_by(username=employee.username).first()
            if not current_user:
                return []

            # Base query avec toutes les relations nécessaires pour l'affichage
            base_query = session.query(Contract)\
                .options(joinedload(Contract.client))\
                .options(joinedload(Contract.commercial))\
                .options(joinedload(Contract.evenement))\
                .options(joinedload(Contract.evenement).joinedload(Event.contact_support))\
                .order_by(Contract.id)

            # Filtres pour les gestionnaires
            if current_user.departement == Employee.GESTION:
                if filter_mode == ContractFilterGestion.WITH_SUPPORT:
                    return base_query\
                        .join(Event, Contract.id == Event.contrat_id)\
                        .filter(Event.contact_support_id.isnot(None))\
                        .all()
                elif filter_mode == ContractFilterGestion.WITHOUT_SUPPORT:
                    return base_query\
                        .outerjoin(Event, Contract.id == Event.contrat_id)\
                        .filter(or_(Event.id.is_(None), Event.contact_support_id.is_(None)))\
                        .all()

            # Filtres pour les commerciaux
            elif current_user.departement == Employee.COMMERCIAL:
                if filter_mode == ContractFilterCommercial.SIGNED:
                    return base_query.filter(Contract.est_signe == True).all()
                elif filter_mode == ContractFilterCommercial.UNSIGNED:
                    return base_query.filter(Contract.est_signe == False).all()
                elif filter_mode == ContractFilterCommercial.FULLY_PAID:
                    return base_query.filter(Contract.montant_restant == 0).all()
                elif filter_mode == ContractFilterCommercial.NOT_FULLY_PAID:
                    return base_query.filter(Contract.montant_restant > 0).all()

            # Par défaut, retourner tous les contrats
            return base_query.all()
        finally:
            session.close()

    @staticmethod
    def get_all_events(token, filter_mode=None):
        employee = verify_token(token)
        if not employee:
            return []

        session = Session()
        try:
            current_user = session.query(Employee).filter_by(username=employee.username).first()
            if not current_user:
                return []

            # Base query avec toutes les relations pour l'affichage complet
            base_query = session.query(Event)\
                .options(joinedload(Event.contrat))\
                .options(joinedload(Event.contact_support))\
                .options(joinedload(Event.contrat).joinedload(Contract.client))\
                .order_by(Event.id)

            # Filtre optionnel pour le support
            if current_user.departement == Employee.SUPPORT and filter_mode == EventFilterSupport.MY_EVENTS:
                return base_query.filter(Event.contact_support_id == current_user.id).all()

            # Par défaut, tout le monde voit tous les événements
            return base_query.all()
        finally:
            session.close()

    @staticmethod
    def get_all_employees(token):
        employee = verify_token(token)
        if not employee:
            return []

        session = Session()
        try:
            current_user = session.query(Employee).filter_by(username=employee.username).first()
            if not current_user or current_user.departement != Employee.GESTION:
                raise PermissionError("Seuls les gestionnaires peuvent voir tous les employés")

            # Chargement des employés avec leurs permissions
            return session.query(Employee)\
                .options(joinedload(Employee.permissions))\
                .order_by(Employee.id)\
                .all()
        finally:
            session.close()