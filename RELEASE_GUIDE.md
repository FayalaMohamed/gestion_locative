# Guide de Release - Gestion Locative Pro

Ce guide explique comment créer et distribuer une nouvelle version de l'application avec support des migrations de base de données et de configuration.

## 📋 Prérequis

- Python 3.11+ avec conda
- Environnement conda `location` activé
- PyInstaller installé
- Accès au repository GitHub

## 🔄 Processus de Release Complet

### Étape 1: Préparation du Code

1. **Mettre à jour la version dans `main.py`**:
   ```python
   APP_VERSION = "1"  # Incrémenter pour chaque release
   ```

2. **Si vous modifiez le schéma de la base de données**:
   - Modifiez les modèles dans `app/models/entities.py`
   - Créez une migration Alembic:
     ```bash
     alembic revision --autogenerate -m "Description des changements"
     ```
   
3. **Si vous modifiez la configuration**:
   - Modifiez `app/utils/config.py` pour ajouter les nouveaux champs
   - Ajoutez la logique de migration dans `migrate_config()` dans `main.py`

### Étape 2: Test Local

1. **Tester les migrations**:
   ```bash
   python main.py
   ```
   - L'application doit démarrer sans erreurs
   - Les migrations doivent s'exécuter automatiquement
   - Vérifier dans la console: "Database migrations completed successfully"

2. **Tester la fonctionnalité**:
   - Vérifier que toutes les nouvelles fonctionnalités fonctionnent
   - Vérifier que les données existantes sont préservées

### Étape 3: Créer l'Exécutable

1. **Builder avec PyInstaller**:
   ```bash
   pyinstaller --clean gestion_locative.spec
   ```

2. **Vérifier le build**:
   - L'exécutable est dans `dist/GestionLocativePro.exe`
   - Tester l'exécutable localement

### Étape 4: Préparer la Release GitHub

1. **Créer une sauvegarde de la base de données de test**:
   - Copier `data/gestion_locative.db` (avec des données de test)
   - Nommer: `gestion_locative_vide.db`

2. **Créer le fichier ZIP pour les nouveaux clients**:
   ```
   GestionLocativePro_v1.zip
   ├── GestionLocativePro.exe
   ├── config.yaml
   └── data/
       └── gestion_locative.db (base vide)
   ```

3. **Créer la Release sur GitHub**:
   - Aller sur: https://github.com/FayalaMohamed/gestion_locative/releases
   - Cliquer "Draft a new release"
   - **Tag version**: `v1` (doit correspondre à APP_VERSION)
   - **Release title**: `Version 1.0 - Description`
   - **Description**:
     ```markdown
     ## Nouveautés dans cette version:
     - Feature 1
     - Feature 2
     - Correction de bugs
     
     ## Migrations incluses:
     - Migration de base de données: Oui/Non
     - Migration de configuration: Oui/Non
     
     ## Installation:
     1. Téléchargez `GestionLocativePro.exe`
     2. Remplacez votre ancien fichier .exe
     3. L'application se mettra à jour automatiquement
     
     ## Notes:
     - Une sauvegarde de votre base de données sera créée automatiquement
     - Vos données seront préservées
     ```

4. **Uploader les fichiers**:
   - `GestionLocativePro.exe` (obligatoire - l'updater le télécharge)
   - `GestionLocativePro_v1.zip` (optionnel - pour nouveaux clients)
   - Notes de release détaillées

### Étape 5: Distribution aux Clients Existants

**Option A: Auto-updater (Recommandé)**
- Les clients ouvrent l'application
- Vont dans "Aide" → "Vérifier les mises à jour"
- L'application détecte la nouvelle version
- Cliquent "Oui" pour télécharger et installer
- L'application redémarre automatiquement avec les migrations

**Option B: Email manuel**
- Envoyez un email avec le lien GitHub
- Les clients téléchargent manuellement
- Remplacent le fichier .exe
- L'application fait les migrations au démarrage

## 🗄️ Gestion des Migrations

### Structure des Migrations Alembic

Les migrations sont dans `alembic/versions/`. Chaque fichier représente une version du schéma.

**Créer une nouvelle migration**:
```bash
alembic revision --autogenerate -m "Ajout table X"
```

**Appliquer les migrations**:
```bash
alembic upgrade head
```

**Voir l'historique**:
```bash
alembic history
```

### Migration de Configuration

Si vous ajoutez de nouveaux champs à `config.yaml`, modifiez `migrate_config()` dans `main.py`:

```python
def migrate_config():
    config = Config()
    config_version = config.get('app', 'version', default='0')
    
    if config_version != APP_VERSION:
        print(f"Migrating config from v{config_version} to v{APP_VERSION}")
        
        # Exemple: migration de v0 à v1
        if config_version == "0":
            # Ajouter nouveau champ avec valeur par défaut
            if not config.get('new_section', 'new_key'):
                config.set('default_value', 'new_section', 'new_key')
        
        # Mettre à jour la version
        config.set(APP_VERSION, 'app', 'version')
        config.save_config()
```

## 🔒 Sauvegardes Automatiques

### Avant une Mise à Jour

Quand l'utilisateur installe une mise à jour:
1. La base de données est sauvegardée automatiquement
2. Le fichier de sauvegarde est nommé: `gestion_locative_backup_YYYYMMDD_HHMMSS.db`
3. La sauvegarde est dans le dossier `data/`

### Restauration Manuelle

Si quelque chose ne va pas:
1. Fermer l'application
2. Aller dans `data/`
3. Renommer la sauvegarde: `gestion_locative_backup_XXX.db` → `gestion_locative.db`
4. Redémarrer l'application

## 🐛 Dépannage

### Problème: "Database migrations failed"

**Solution**:
```bash
# Vérifier l'état des migrations
alembic current

# Forcer une migration spécifique
alembic upgrade +1

# En cas de problème majeur, réinitialiser:
alembic downgrade base
alembic upgrade head
```

### Problème: Config corrompue

**Solution**:
1. Supprimer `config.yaml`
2. L'application recréera le fichier avec les valeurs par défaut
3. Reconfigurer les signatures/paramètres

### Problème: Auto-updater ne fonctionne pas

**Vérifications**:
1. Vérifier que la version dans `main.py` correspond au tag GitHub
2. Vérifier que le fichier .exe est bien uploadé comme "Asset"
3. Vérifier que le repository est public
4. Vérifier la connexion internet du client

## 📊 Checklist de Release

Avant de publier une nouvelle version, vérifier:

- [ ] Version incrémentée dans `main.py` (`APP_VERSION`)
- [ ] Tests passent: `python run_tests.py`
- [ ] Application démarre sans erreurs
- [ ] Migration Alembic créée si schéma modifié
- [ ] Logic de migration config ajouté si nécessaire
- [ ] Exécutable buildé et testé
- [ ] Release créée sur GitHub avec tag correct
- [ ] Fichier .exe uploadé comme asset
- [ ] Notes de release rédigées
- [ ] Test de l'auto-updater fait

## 📝 Exemple Complet: Release v1.0 → v1.1

### Changements:
- Ajout champ `frais_electricite` dans paiements
- Nouveau paramètre dans config

### Étapes:

1. **Modifier modèle** (`app/models/entities.py`):
   ```python
   frais_electricite = Column(Numeric(10, 3), nullable=True, default=0)
   ```

2. **Créer migration**:
   ```bash
   alembic revision --autogenerate -m "Add frais electricite"
   ```

3. **Modifier config migration** (`main.py`):
   ```python
   if config_version == "1":
       config.set([], 'new_section', 'new_list')
   ```

4. **Mettre à jour version**:
   ```python
   APP_VERSION = "1.1"
   ```

5. **Builder et tester**

6. **Créer release GitHub** avec tag `v1.1`

7. **Les clients reçoivent la notification** et mettent à jour automatiquement!

---

**Questions?** Consultez le code dans `main.py` pour les exemples de migration.
