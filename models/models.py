from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Table, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime
from config.db import Base
import bcrypt

employee_permissions = Table(
   'employee_permissions', 
   Base.metadata,
   Column('employee_id', Integer, ForeignKey('employees.id'), primary_key=True),
   Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

class Employee(Base):
   """Modèle pour les employés"""
   __tablename__ = 'employees'

   # Constantes pour les départements
   COMMERCIAL = 'COMMERCIAL'
   SUPPORT = 'SUPPORT'
   GESTION = 'GESTION'
   DEPARTMENT_CHOICES = [COMMERCIAL, SUPPORT, GESTION]

   # Colonnes de la table
   id = Column(Integer, primary_key=True)
   username = Column(String(50), unique=True, nullable=False)
   password = Column(String(255), nullable=False)  # Stockera le hash du mot de passe
   numero_employe = Column(String(10), unique=True)
   email = Column(String(100), unique=True, nullable=False)
   nom = Column(String(50), nullable=False)
   prenom = Column(String(50), nullable=False)
   telephone = Column(String(20))
   departement = Column(String(10), nullable=False)
   date_creation = Column(DateTime, default=datetime.utcnow)

   # Relations avec les autres tables
   permissions = relationship('Permission', secondary=employee_permissions, back_populates='employees', lazy='joined')
   clients = relationship("Client", back_populates="commercial_attitré")
   contrats = relationship("Contract", back_populates="commercial")
   evenements = relationship("Event", back_populates="contact_support")

   def set_password(self, password):
       """Hash le mot de passe avant de le stocker"""
       password_bytes = password.encode('utf-8')
       salt = bcrypt.gensalt()
       hashed = bcrypt.hashpw(password_bytes, salt)
       self.password = hashed.decode('utf-8')

   def check_password(self, password):
       """Vérifie si le mot de passe est correct"""
       return bcrypt.checkpw(
           password.encode('utf-8'), 
           self.password.encode('utf-8')
       )

   def __repr__(self):
       """Représentation de l'objet pour le débug"""
       return f"{self.prenom} {self.nom} ({self.departement})"

class Permission(Base):
   """Modèle pour les permissions"""
   __tablename__ = 'permissions'

   id = Column(Integer, primary_key=True)
   code = Column(String(50), unique=True, nullable=False)
   description = Column(String(100))

   # Relation avec Employee
   employees = relationship('Employee', secondary=employee_permissions, back_populates='permissions')

class Client(Base):
   """Modèle pour les clients"""
   __tablename__ = 'clients'

   id = Column(Integer, primary_key=True)
   nom_complet = Column(String(100), nullable=False)
   email = Column(String(100), unique=True, nullable=False)
   telephone = Column(String(20))
   entreprise = Column(String(100), nullable=False)
   date_creation = Column(DateTime, default=datetime.utcnow)
   derniere_mise_a_jour = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
   commercial_id = Column(Integer, ForeignKey('employees.id'))

   # Relations
   commercial_attitré = relationship("Employee", back_populates="clients")
   contrats = relationship("Contract", back_populates="client")

   def __repr__(self):
       return f"{self.nom_complet} - {self.entreprise}"

class Contract(Base):
   """Modèle pour les contrats"""
   __tablename__ = 'contracts'

   id = Column(Integer, primary_key=True)
   client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
   commercial_id = Column(Integer, ForeignKey('employees.id'))
   montant_total = Column(DECIMAL(10, 2), nullable=False)
   montant_restant = Column(DECIMAL(10, 2), nullable=False)
   date_creation = Column(DateTime, default=datetime.utcnow)
   est_signe = Column(Boolean, default=False)

   # Relations
   client = relationship("Client", back_populates="contrats")
   commercial = relationship("Employee", back_populates="contrats")
   evenement = relationship("Event", back_populates="contrat", uselist=False)

   def __repr__(self):
       return f"Contrat {self.id} - {self.client}"

class Event(Base):
   """Modèle pour les événements"""
   __tablename__ = 'events'

   id = Column(Integer, primary_key=True)
   nom = Column(String(200), nullable=False)
   contrat_id = Column(Integer, ForeignKey('contracts.id'), unique=True, nullable=False)
   date_debut = Column(DateTime, nullable=False)
   date_fin = Column(DateTime, nullable=False)
   lieu = Column(String(200), nullable=False)
   nb_participants = Column(Integer)
   notes = Column(String(1000))
   contact_support_id = Column(Integer, ForeignKey('employees.id'))

   # Relations
   contrat = relationship("Contract", back_populates="evenement")
   contact_support = relationship("Employee", back_populates="evenements")

   def __repr__(self):
       return f"{self.nom} - {self.contrat.client.nom_complet}"