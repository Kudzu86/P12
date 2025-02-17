```mermaid
classDiagram
    class Employee {
        +Integer id
        +String username
        +String password
        +String prenom
        +String nom
        +String email
        +String numero_employe
        +String telephone
        +String departement
        +DateTime date_creation
        +permissions[]
        +set_password()
        +check_password()
    }

    class Permission {
        +Integer id
        +String code
        +String description
    }

    class Commercial {
        +List~Client~ clients
        +List~Contract~ contrats
        +create_client()
        +update_client()
        +create_event()
    }

    class Support {
        +List~Event~ evenements
        +update_event()
    }

    class Gestion {
        +create_employee()
        +update_employee()
        +delete_employee()
        +create_contract()
        +assign_support()
    }

    class Client {
        +Integer id
        +String nom_complet
        +String email
        +String telephone
        +String entreprise
        +DateTime date_creation
        +DateTime derniere_mise_a_jour
        +Commercial commercial_attitré
    }
    
    class Contract {
        +Integer id
        +Client client
        +Commercial commercial
        +Decimal montant_total
        +Decimal montant_restant
        +DateTime date_creation
        +Boolean est_signe
    }
    
    class Event {
        +Integer id
        +String nom
        +Contract contrat
        +DateTime date_debut
        +DateTime date_fin
        +String lieu
        +Integer nb_participants
        +String notes
        +Support contact_support
    }

    Employee <|-- Commercial: hérite
    Employee <|-- Support: hérite
    Employee <|-- Gestion: hérite
    Employee "*" --o "*" Permission: employee_permissions

    Commercial "1" --> "*" Client: gère
    Commercial "1" --> "*" Contract: responsable
    Support "1" --> "*" Event: organise
    Client "1" --> "*" Contract: possède
    Contract "1" --> "1" Event: associé à
```mermaid