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
│   │   ├──Locataire_repository.py
│   │   ├── contrat_repository.py
│   │   └── paiement_repository.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py       # Gestion base de données SQLite
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py      # Fenêtre principale Qt
│   │   └── views/
│   │       ├── base_view.py
│   │       ├── immeuble_view.py
│   │       ├── bureau_view.py
│   │       ├── locataire_view.py
│   │       ├── contrat_view.py
│   │       ├── paiement_view.py
│   │       └── dashboard_view.py
│   └── utils/
│       ├── __init__.py
│       └── config.py           # Configuration YAML
├── config.yaml                 # Configuration de l'application
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
- Placeholder (en construction)

## Prérequis

- Python 3.11+
- PySide6 (Qt 6)
- SQLAlchemy

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
- ⏳ Tableau de bord (en construction)
- ⏳ Génération PDF des reçus

## Configuration

Modifier `config.yaml` :

```yaml
app:
  name: "Gestion Locative Pro"
  debug: true

database:
  path: "data/gestion_locative.db"
```

## Licence

Propriétaire - Usage interne
