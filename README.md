# Gestion Locative Pro

Application de gestion immobilière pour entreprise de location de bureaux avec interface Qt.

## Structure du Projet

```
D:\code\locations\
├── app/
│   ├── __init__.py
│   ├── init_db.py              # Créer et initialiser la base de données
│   ├── models/
│   │   ├── __init__.py
│   │   └── entities.py         # Modèles SQLAlchemy
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py             # Classe de base Repository
│   │   ├── immeuble_repository.py
│   │   ├── bureau_repository.py
│   │   ├── locataire_repository.py
│   │   ├── contrat_repository.py
│   │   └── paiement_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── audit_service.py
│   │   ├── backup_service.py
│   │   ├── data_service.py
│   │   ├── google_drive_service.py
│   │   └── receipt_service.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py       # Gestion base de données SQLite
│   │   └── migrations/
│   │       ├── __init__.py
│   │       └── env.py          # Configuration Alembic
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py      # Fenêtre principale Qt
│   │   ├── grille_paiement.py  # Widget de grille de paiements
│   │   └── views/
│   │       ├── __init__.py
│   │       ├── base_view.py
│   │       ├── immeuble_view.py
│   │       ├── bureau_view.py
│   │       ├── locataire_view.py
│   │       ├── contrat_view.py
│   │       ├── paiement_view.py
│   │       ├── dashboard_view.py
│   │       └── settings_view.py
│   └── utils/
│       ├── __init__.py
│       └── config.py           # Configuration YAML
├── data/
│   ├── gestion_locative.db     # Base de données SQLite
│   └── backups/                # Sauvegardes locales
├── tests/
│   ├── __init__.py
│   ├── test_crud.py            # Tests CRUD Operations
│   ├── test_backup.py          # Tests Backup Functionality
│   ├── test_relation.py        # Tests Relationship
│   └── query_db.py             # Utilitaire de consultation
├── config.yaml                 # Configuration de l'application
├── run_tests.py                # Script de test unifié
└── requirements.txt            # Dépendances Python
```

## Vues de l'Application

### 1. Immeubles
- Liste des immeubles avec adresse
- Ajout/Modification/Suppression
- Filtrage par nom

### 2. Bureaux
- Liste des bureaux par immeuble
- Numéro, étage, surface
- Affichage automatique des immeubles parents
- Statut (occupé/libre)

### 3. Locataires
- Gestion des locataires (SARL, particuliers)
- Coordonnées (téléphone, email, CIN)
- Statut (Actif/Historique)
- Filtrage par statut

### 4. Contrats
- Contrat multi-bureaux (relation many-to-many)
- Grille rouge/vert des paiements
- **Filtre par statut** (Actif/Résilié)
- **Mois impayés** : nombre de mois non couverts par un loyer
  - Affichage cliquable pour voir la liste des mois

### 5. Paiements
- Types : Loyer, Caution, Pas de porte, Autre
- **Filtre par contrat** affichant :
  - Nom du locataire
  - Numéros des bureaux
- Grille de période (mois début/fin)
- Génération de reçus (placeholder)

### 6. Tableau de Bord
- Vue d'ensemble avec statistiques

### 7. Paramètres
- Configuration de l'application

## Prérequis

- Python 3.11+
- PySide6 (Qt 6)
- SQLAlchemy
- Alembic (migrations)

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

### Lancer l'application

```bash
python -m app.main
```

### Créer la base de données

```bash
# Base vide
python "D:\code\locations\app\init_db.py"

# Base avec données d'exemple
python "D:\code\locations\app\init_db.py" --seed
```

### Sur Windows

```powershell
# Supprimer et recréer avec données
Remove-Item data\gestion_locative.db -ErrorAction SilentlyContinue
python "D:\code\locations\app\init_db.py" --seed

# Lancer l'application
python -m app.main
```

## Tests

### Exécuter tous les tests

```bash
python run_tests.py
```

Ce script exécute tous les tests et affiche un rapport :
- Tests réussis : [PASS]
- Tests échoués : [FAIL]

### Tests individuels

```bash
# Tests CRUD
python tests/test_crud.py

# Tests de sauvegarde
python tests/test_backup.py

# Tests des relations
python tests/test_relation.py

# Consulter la base de données
python tests/query_db.py
```

### Nettoyage des sauvegardes de test

Les tests de sauvegarde (`test_backup.py`) créent des fichiers temporaires qui sont automatiquement supprimés après chaque exécution.

Les sauvegardes sont stockées dans `data/backups/`.

## Modèle de Données

```
Immeuble (1) ----> (N) Bureau (N) <---- (M) Contrat
                    ^                      |
                    |______________________|
                           (contrat_bureau)

Locataire (1) ----> (N) Contrat (1) ----> (N) Paiement
                              |
                              v
                           Recu
```

## Fonctionnalités Implémentées

- ✅ CRUD complet Immeubles, Bureaux, Locataires, Contrats, Paiements
- ✅ Relation many-to-many Contrats-Bureaux
- ✅ Grille rouge/vert des paiements
- ✅ Filtrage dans toutes les vues
- ✅ Calcul automatique des mois impayés
- ✅ Interface Qt avec PySide6
- ✅ Services (audit, données, reçus)
- ✅ Migrations de base de données
- ✅ Génération de reçus PDF
- ✅ Sauvegarde locale et Google Drive
- ✅ Tests unitaires avec rapport

## Configuration

### Google Drive Backup

Pour configurer la sauvegarde Google Drive, suivez le guide complet :

📖 **[Guide de configuration Google Drive](docs/GOOGLE_DRIVE_SETUP.md)**

Ce guide explique comment :
- Créer un projet Google Cloud
- Activer l'API Google Drive
- Configurer les identifiants OAuth 2.0
- Se connecter à Google Drive depuis l'application

### Configuration de l'application

Modifier `config.yaml` :

```yaml
app:
  debug: true

database:
  path: "data/gestion_locative.db"

export:
  backup_directory: "data/backups"

receipts:
  company_name: "Magic House"
  signature_path: "C:/path/to/signature.jpg"
```

## Licence

Propriétaire - Usage interne

## Création de l'Executable (.exe)

### Prérequis

1. Assurez-vous d'avoir conda installé avec l'environnement `location` activé
2. Avoir l'icône de l'application dans `app/ui/icon.png`

### Création de l'Executable

```bash
# Activer l'environnement conda
conda activate location

# Builder l'executable
pyinstaller --onefile --windowed --clean gestion_locative.spec
```

Ou avec conda run :

```bash
conda run -n location pyinstaller --clean gestion_locative.spec
```

### Fichiers à Distribuer au Client

Après la compilation, les fichiers suivants doivent être fournis au client :

```
Dossier de distribution/
├── GestionLocativePro.exe    # L'executable (100MB)
├── config.yaml               # Configuration de l'application
└── data/
    ├── gestion_locative.db   # Base de données (avec toutes les données)
    └── google_drive_token.json  # Token Google Drive (si utilisé)
```

### Structure des Chemins

L'application utilise des chemins relatifs, donc le dossier peut être placé n'importe où sur l'ordinateur du client :

```
C:\
└── Program Files\
    └── GestionLocativePro\
        ├── GestionLocativePro.exe
        ├── config.yaml
        └── data\
            ├── gestion_locative.db
            ├── backups\
            └── google_drive_token.json
```

### Notes de Distribution

- Le fichier `gestion_locative.db` contient toutes les données (immeubles, bureaux, locataires, contrats, paiements)
- Si le client change d'ordinateur, copiez simplement le dossier entier
- Les sauvegardes automatiques iront dans `data/backups/`
- L'icône de l'application est intégrée dans l'executable
