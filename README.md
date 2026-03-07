# Gestion Locative Pro

Application de gestion immobilière professionnelle pour entreprise de location de bureaux avec interface Qt moderne.

**Version**: 0.1  
**Technologie**: Python 3.11+ | PySide6 (Qt6) | SQLite | SQLAlchemy

## Fonctionnalités Principales

- **Gestion complète des immeubles et bureaux** avec suivi des statuts
- **Gestion des locataires** (SARL, particuliers) avec historique
- **Contrats multi-bureaux** avec relation many-to-many
- **Suivi des paiements** avec génération de reçus PDF
- **Tableau de bord** avec grille de paiements par immeuble
- **Gestion documentaire** avec arborescence personnalisable
- **Audit trail** complet de toutes les actions
- **Sauvegarde automatique** locale et Google Drive
- **Mise à jour automatique** de l'application
- **Migrations de base de données** automatiques

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
│   │   ├── paiement_repository.py
│   │   └── document_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── audit_service.py
│   │   ├── backup_service.py
│   │   ├── data_service.py
│   │   ├── document_service.py
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
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── base_view.py
│   │   │   ├── immeuble_view.py
│   │   │   ├── bureau_view.py
│   │   │   ├── locataire_view.py
│   │   │   ├── contrat_view.py
│   │   │   ├── paiement_view.py
│   │   │   ├── dashboard_view.py
│   │   │   ├── audit_view.py
│   │   │   └── settings_view.py
│   │   ├── dialogs/
│   │   │   ├── __init__.py
│   │   │   ├── document_browser_dialog.py
│   │   │   ├── document_upload_dialog.py
│   │   │   ├── receipt_options_dialog.py
│   │   │   └── tree_config_dialog.py
│   │   └── widgets/
│   │       ├── __init__.py
│   │       └── document_viewer_widget.py
│   └── utils/
│       ├── __init__.py
│       └── config.py           # Configuration YAML
├── data/
│   ├── gestion_locative.db     # Base de données SQLite
│   ├── backups/                # Sauvegardes locales
│   └── documents/              # Documents attachés
├── tests/
│   ├── __init__.py
│   ├── test_crud.py            # Tests CRUD Operations
│   ├── test_backup.py          # Tests Backup Functionality
│   ├── test_relation.py        # Tests Relationship
│   ├── test_update_system.py   # Tests Auto-updater
│   ├── test_receipt_features.py # Tests Receipt Generation
│   └── query_db.py             # Utilitaire de consultation
├── alembic/                    # Migrations de base de données
│   ├── versions/
│   └── env.py
├── config.yaml                 # Configuration de l'application
├── main.py                     # Point d'entrée principal
├── run_tests.py                # Script de test unifié
├── requirements.txt            # Dépendances Python
└── gestion_locative.spec       # Configuration PyInstaller
```

## Vues de l'Application

### 1. Immeubles
- Liste des immeubles avec adresse
- Ajout/Modification/Suppression
- Filtrage par nom
- Gestion documentaire intégrée

### 2. Bureaux
- Liste des bureaux par immeuble
- Numéro, étage, surface
- Affichage automatique des immeubles parents
- Statut (occupé/libre)
- Gestion documentaire intégrée

### 3. Locataires
- Gestion des locataires (SARL, particuliers)
- Coordonnées (téléphone, email, CIN)
- Statut (Actif/Historique)
- Filtrage par statut
- Gestion documentaire intégrée

### 4. Contrats
- Contrat multi-bureaux (relation many-to-many)
- Grille rouge/vert des paiements
- **Filtre par statut** (Actif/Résilié)
- **Mois impayés** : nombre de mois non couverts par un loyer
  - Affichage cliquable pour voir la liste des mois
- Gestion documentaire intégrée

### 5. Paiements
- Types : Loyer, Caution, Pas de porte, Autre
- **Frais supplémentaires** : électricité, eau, autres charges
- **Filtre par contrat** affichant :
  - Nom du locataire
  - Numéros des bureaux
- Grille de période (mois début/fin)
- **Génération de reçus PDF** avec signatures multiples
- Gestion documentaire intégrée

### 6. Tableau de Bord
- Vue d'ensemble avec grille de paiements par immeuble
- Filtre par statut de contrat (Actif/Résilié)
- Visualisation rapide des paiements en retard

### 7. Historique (Audit)
- Journal complet de toutes les actions
- Filtres par type d'action (CREATE, UPDATE, DELETE, RECEIPT_GENERATED)
- Recherche et filtrage par date
- Traçabilité totale des modifications

### 8. Paramètres
- Configuration de l'application
- Gestion des signatures multiples pour reçus
- Configuration Google Drive
- Gestion des sauvegardes

## Prérequis

- Python 3.11+
- Conda (recommandé) ou pip
- PySide6 (Qt 6)
- SQLAlchemy 2.0+
- Alembic (migrations)

## Installation

### 1. Cloner le repository

```bash
git clone https://github.com/FayalaMohamed/gestion_locative.git
cd gestion_locative
```

### 2. Créer l'environnement conda

```bash
conda create -n location python=3.11
conda activate location
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

## Utilisation

### Lancer l'application

```bash
# Activer l'environnement
conda activate location

# Lancer l'application
python main.py
```

### Créer la base de données

```bash
# Base vide
python app/init_db.py

# Base avec données d'exemple
python app/init_db.py --seed
```

### Sur Windows (PowerShell)

```powershell
# Activer l'environnement
conda activate location

# Supprimer et recréer avec données
Remove-Item data\gestion_locative.db -ErrorAction SilentlyContinue
python app\init_db.py --seed

# Lancer l'application
python main.py
```

## Tests

### Exécuter tous les tests

```bash
# Activer l'environnement
conda activate location

# Exécuter tous les tests
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

# Tests du système de mise à jour
python tests/test_update_system.py

# Tests de génération de reçus
python tests/test_receipt_features.py

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

### Gestion des Données
- ✅ CRUD complet Immeubles, Bureaux, Locataires, Contrats, Paiements
- ✅ Relation many-to-many Contrats-Bureaux
- ✅ Calcul automatique des mois impayés
- ✅ Filtrage avancé dans toutes les vues
- ✅ Recherche instantanée

### Interface Utilisateur
- ✅ Interface Qt moderne avec PySide6
- ✅ Navigation fluide avec sidebar
- ✅ Grille de paiements rouge/vert par immeuble
- ✅ Tableau de bord avec statistiques
- ✅ Thème visuel cohérent

### Documents et Reçus
- ✅ Gestion documentaire avec arborescence personnalisable
- ✅ Upload et visualisation de documents
- ✅ Génération de reçus PDF professionnels
- ✅ Support de signatures multiples
- ✅ Export et impression

### Audit et Traçabilité
- ✅ Journal complet de toutes les actions
- ✅ Historique des modifications
- ✅ Filtres par type d'action et date
- ✅ Traçabilité totale

### Sauvegarde et Migration
- ✅ Sauvegarde locale automatique
- ✅ Sauvegarde Google Drive
- ✅ Migrations de base de données automatiques (Alembic)
- ✅ Migration de configuration automatique

### Mise à Jour
- ✅ Système de mise à jour automatique
- ✅ Vérification des nouvelles versions
- ✅ Téléchargement et installation automatiques
- ✅ Notifications non-bloquantes

### Qualité
- ✅ Tests unitaires complets avec rapport
- ✅ Gestion d'erreurs robuste
- ✅ Logging détaillé

## Configuration

### Google Drive Backup

Pour configurer la sauvegarde Google Drive, vous devez :

1. Créer un projet Google Cloud
2. Activer l'API Google Drive
3. Configurer les identifiants OAuth 2.0
4. Télécharger le fichier `credentials.json` dans le dossier `credentials/`

L'application vous guidera pour l'authentification lors de la première utilisation.

### Configuration de l'application

Modifier `config.yaml` :

```yaml
app:
  debug: true
  version: "0.1"

database:
  path: "data/gestion_locative.db"

export:
  backup_directory: "data/backups"

receipts:
  company_name: "Magic House"
  company_names:
    - Magic House
    - Autre Société
  signature_path: ""
  signatures:
    - "C:/path/to/signature1.png"
    - "C:/path/to/signature2.png"
```

### Gestion des Signatures Multiples

L'application supporte plusieurs signatures pour les reçus :
- Ajoutez les chemins des images de signatures dans `config.yaml`
- Les signatures seront appliquées en alternance sur les reçus générés
- Configuration via la vue Paramètres

## Création de l'Executable (.exe)

### Prérequis

1. Python 3.11+ avec conda
2. Environnement `location` activé
3. PyInstaller installé
4. Icône de l'application dans `app/ui/icon.png`

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
├── GestionLocativePro.exe    # L'executable (~100MB)
├── config.yaml               # Configuration de l'application
├── credentials/              # Dossier pour Google Drive (optionnel)
│   └── credentials.json      # Identifiants OAuth 2.0
└── data/
    ├── gestion_locative.db   # Base de données (avec toutes les données)
    ├── backups/              # Dossier de sauvegardes
    └── documents/            # Documents attachés
```

### Structure des Chemins

L'application utilise des chemins relatifs, donc le dossier peut être placé n'importe où sur l'ordinateur du client :

```
C:\
└── Program Files\
    └── GestionLocativePro\
        ├── GestionLocativePro.exe
        ├── config.yaml
        ├── credentials\
        │   └── credentials.json
        └── data\
            ├── gestion_locative.db
            ├── backups\
            ├── documents\
            └── google_drive_token.json
```

### Notes de Distribution

- Le fichier `gestion_locative.db` contient toutes les données
- Si le client change d'ordinateur, copiez simplement le dossier entier
- Les sauvegardes automatiques iront dans `data/backups/`
- Les documents attachés sont dans `data/documents/`
- L'icône de l'application est intégrée dans l'executable
- Les migrations de base de données s'exécutent automatiquement au démarrage

## Mise à Jour Automatique

L'application intègre un système de mise à jour automatique :

1. **Vérification automatique** au démarrage
2. **Notification non-bloquante** si une mise à jour est disponible
3. **Téléchargement et installation** en un clic
4. **Sauvegarde automatique** avant la mise à jour
5. **Redémarrage automatique** de l'application

Pour vérifier manuellement les mises à jour : Menu "Aide" → "Vérifier les mises à jour"

## Guide de Release

Pour créer et distribuer une nouvelle version, consultez le guide complet :

📖 **[Guide de Release](RELEASE_GUIDE.md)**

Ce guide explique comment :
- Préparer une nouvelle version
- Gérer les migrations de base de données
- Créer et tester l'exécutable
- Publier sur GitHub
- Distribuer aux clients

## Licence

Propriétaire - Usage interne

## Support

Pour toute question ou problème :
- Consulter la documentation dans `AGENTS.md`
- Vérifier les issues sur GitHub
- Contacter l'équipe de développement
