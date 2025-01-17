```mermaid
classDiagram
    class Employee {
        +String username
        +String password
        +String first_name
        +String last_name
        +String email
        +String numero_employe
        +String telephone
        +String departement
        +permissions[]
    }

    class Commercial {
        +List~Client~ clients
        +List~Contract~ contrats
        +manage_clients()
    }

    class Support {
        +List~Event~ evenements
        +manage_events()
    }

    class Gestion {
        +manage_users()
        +manage_contracts()
    }

    class Client {
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

    Commercial "1" --> "*" Client: gère
    Commercial "1" --> "*" Contract: responsable
    Support "1" --> "*" Event: organise
    Client "1" --> "*" Contract: possède
    Contract "1" --> "1" Event: associé à
```mermaid