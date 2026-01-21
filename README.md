# Gestion Locative Pro

Application de gestion immobilière pour entreprise de location de bureaux.

## Structure du Projet

```
D:\code\locations\
├── app/
│   ├── __init__.py
│   ├── init_db.py              # Créer et initialiser la base de données
│   ├── test_crud.py            # Tests Phase 2 - CRUD complet
│   ├── query_db.py             # Interroger la base de données
│   ├── models/
│   │   ├── __init__.py
│   │   └── entities.py         # Modèles SQLAlchemy
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py             # Classe de base Repository
│   │   ├── immeuble_repository.py
│   │   ├── bureau_repository.py
│   │   ├── Locataire_repository.py
│   │   ├── contrat_repository.py
│   │   └── paiement_repository.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py       # Gestion base de données SQLite
│   └── utils/
│       ├── __init__.py
│       └── config.py           # Configuration YAML
├── config.yaml                 # Configuration de l'application
├── requirements.txt            # Dépendances Python
└── alembic.ini                 # Configuration migrations
```

## Prérequis

- Python 3.11+
- Conda (optionnel mais recommandé)

## Installation

```bash
# Créer l'environnement conda
conda create -n gestion_locative python=3.11 -y
conda activate gestion_locative

# Installer les dépendances
pip install -r requirements.txt
```

## Gestion de la Base de Données

### Emplacement de la base de données

La base de données SQLite est stockée à : `data/gestion_locative.db`

### Supprimer et recréer la base de données

```bash
# 1. Supprimer l'ancienne base
rm data/gestion_locative.db

# 2. Créer une nouvelle base vide
python "D:\code\locations\app\init_db.py"

# 3. OU créer avec les données d'exemple (recommandé pour tester)
python "D:\code\locations\app\init_db.py" --seed
```

### Que contient `--seed` ?

Les données d'exemple incluent :

- **4 Immeubles** : Centre Ville, Ariana, Lac, Mutuelleville
- **12 Bureaux** : Divers numéros et surfaces
- **2 Locataires Actifs** : SARL Tech et Entreprise Plus
- **5 Contrats** : Différentes combinaisons bureaux/locataires
- **20+ Paiements** : Loyers et cautions sur 2024

### Sur Windows (avec PowerShell)

```powershell
# Supprimer la base
Remove-Item data\gestion_locative.db -ErrorAction SilentlyContinue

# Recréer avec données
python "D:\code\locations\app\init_db.py" --seed
```

### Réinitialiser complètement (cmd)

```cmd
del data\gestion_locative.db
python D:\code\locations\app\init_db.py --seed
```

## Utilisation

### 1. Créer et initialiser la base de données

```bash
# Créer la base de données (vide)
python "D:\code\locations\app\init_db.py"

# Créer la base de données AVEC données exemple
python "D:\code\locations\app\init_db.py" --seed
```

**Résultat :** `data/gestion_locative.db`

### 2. Interroger la base de données

```bash
python "D:\code\locations\query_db.py"
```

Affiche :
- Liste des immeubles
- Liste des locataires
- Liste des contrats avec leurs bureaux
- Liste des paiements

### 3. Lancer les tests Phase 2 (CRUD)

```bash
python "D:\code\locations\app\test_crud.py"
```

Teste toutes les opérations CRUD :
- Immeuble : Create, Read, Update, Search
- Bureau : Create, Read, Update disponibilité, List par immeuble
- Locataire : Create, Read, Update, Activate/Deactivate, Search
- Contrat : Create avec validation, Résiliation, Ajouter/Retirer bureaux
- Paiement : Create loyer/caution, Total payé, Mois impayés
- Grille : Calcul rouge/vert

## Architecture

### Modèle de Données (Many-to-Many)

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

### Modèle Contrat

Un contrat peut包含 **plusieurs bureaux** (relation many-to-many).

```python
# Exemple : Un contrat pour 3 bureaux
contrat = Contrat(
    Locataire_id=1,
    montant_mensuel=7500.000,  # Total pour tous les bureaux
    bureaux=[bureau101, bureau102, bureau103]
)
```

### Modèle Paiement

Les paiements sont liés au contrat (pas au bureau individually).

```python
# Paiement loyer couvrant 3 mois
paiement = Paiement(
    Locataire_id=1,
    contrat_id=1,
    type_paiement=TypePaiement.LOYER,
    montant_total=7500.000,
    date_paiement=date(2024, 1, 1),
    date_debut_periode=date(2024, 1, 1),
    date_fin_periode=date(2024, 3, 31)
)
```

### Grille Rouge/Vert

Calculée dynamiquement depuis les paiements :

```
2024:
Mois:      Jan  Fev  Mar  Avr  Mai  Jui  Jui  Aou  Sep  Oct  Nov  Dec
Statut:    VER  VER  VER  ROU  ROU  VER  VER  VER  ROU  ROU  ROU  ROU
```

- **VER** (Vert) = Mois payé
- **ROU** (Rouge) = Mois impayé

## Commandes SQL Utilisées

### Créer la base
```python
from app.database.connection import init_database
db = init_database()
```

### Requêtes simples
```python
from app.repositories import ImmeubleRepository

db = init_database()
repo = ImmeubleRepository(db.session)

# Lire tous
immeubles = repo.get_all()

# Lire par ID
immeuble = repo.get_by_id(1)

# Rechercher
resultats = repo.search("Centre")

# Filtrer
actifs = repo.get_actifs()
```

## Phases de Développement

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Terminée | Modélisation & Base de données |
| Phase 2 | ✅ Terminée | CRUD Métiers |
| Phase 3 | ⏳ À faire | CRUD Paiements |
| Phase 4 | ⏳ À faire | Grille Rouge/Vert (UI) |
| Phase 5 | ⏳ À faire | Génération Reçus PDF |
| Phase 6 | ⏳ À faire | Export JSON/CSV |
| Phase 7 | ⏳ À faire | Interface Qt |
| Phase 8 | ⏳ À faire | Finitions & Déploiement |

## Configuration

Modifier `config.yaml` pour adapter l'application :

```yaml
app:
  name: "Gestion Locative Pro"
  debug: true

database:
  path: "data/gestion_locative.db"

export:
  default_format: "json"
  backup_directory: "backups"

receipts:
  company_name: "Gestion Immobilière"
  company_address: ""
  company_phone: ""
```

## Dépannage

### Erreur "ModuleNotFoundError"
```bash
# Vérifier l'installation des dépendances
pip install -r requirements.txt
```

### Erreur "FOREIGN KEY constraint failed"

Cette erreur se produit quand vous essayez de supprimer un enregistrement qui a des dépendances.

**Solution :** Supprimez d'abord les enregistrements liés, puis celle-ci.

**Ou réinitialisez complètement la base :**
```bash
rm data/gestion_locative.db
python "D:\code\locations\app\init_db.py" --seed
```

### Activer l'environnement conda
```bash
conda activate gestion_locative
```

## Licence

Propriétaire - Usage interne
