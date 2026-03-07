# Guide de Release - Gestion Locative Pro

Ce guide explique comment créer et distribuer une nouvelle version de l'application avec support des migrations de base de données, de configuration et de mise à jour automatique.

## 📋 Prérequis

- Python 3.11+ avec conda
- Environnement conda `location` activé
- PyInstaller installé
- Accès au repository GitHub : `FayalaMohamed/gestion_locative`
- Icône de l'application dans `app/ui/icon.png`

## 🔄 Processus de Release Complet

### Étape 1: Préparation du Code

1. **Mettre à jour la version dans `main.py`**:
    ```python
    APP_VERSION = "0.2"  # Incrémenter pour chaque release
    ```

2. **Si vous modifiez le schéma de la base de données**:
    - Modifiez les modèles dans `app/models/entities.py`
    - Créez une migration Alembic:
      ```bash
      alembic revision --autogenerate -m "Description des changements"
      ```
    - Testez la migration:
      ```bash
      alembic upgrade head
      ```
    
3. **Si vous modifiez la configuration**:
    - Modifiez `app/utils/config.py` pour ajouter les nouveaux champs
    - Ajoutez la logique de migration dans `migrate_config()` dans `main.py`
    - Testez la migration de configuration

### Étape 2: Test Local

1. **Activer l'environnement**:
    ```bash
    conda activate location
    ```

2. **Tester les migrations**:
    ```bash
    python main.py
    ```
    - L'application doit démarrer sans erreurs
    - Les migrations doivent s'exécuter automatiquement
    - Vérifier dans la console: "Database migrations completed successfully"
    - Vérifier: "Config migration completed" (si applicable)

3. **Exécuter les tests**:
    ```bash
    python run_tests.py
    ```
    - Tous les tests doivent passer
    - Vérifier qu'il n'y a pas d'erreurs

4. **Tester la fonctionnalité**:
    - Vérifier que toutes les nouvelles fonctionnalités fonctionnent
    - Vérifier que les données existantes sont préservées
    - Tester les filtres et recherches
    - Vérifier la génération de reçus
    - Tester la gestion documentaire

### Étape 3: Créer l'Exécutable

1. **Builder avec PyInstaller**:
    ```bash
    # Activer l'environnement
    conda activate location
    
    # Builder l'exécutable
    pyinstaller --clean gestion_locative.spec
    ```

2. **Vérifier le build**:
    - L'exécutable est dans `dist/GestionLocativePro.exe`
    - Taille approximative : ~100MB
    - Tester l'exécutable localement :
      ```bash
      cd dist
      GestionLocativePro.exe
      ```
    - Vérifier que toutes les fonctionnalités marchent
    - Vérifier les migrations automatiques
    - Vérifier le système de mise à jour

### Étape 4: Préparer la Release GitHub

1. **Créer une sauvegarde de la base de données**:
    - Copier `data/gestion_locative.db` (avec des données de test)
    - Nommer: `gestion_locative_vide.db` (pour nouveaux clients)

2. **Créer le fichier ZIP pour les nouveaux clients**:
    ```
    GestionLocativePro_v0.2.zip
    ├── GestionLocativePro.exe
    ├── config.yaml
    ├── credentials/ (optionnel)
    │   └── credentials.json
    └── data/
        └── gestion_locative.db (base vide)
    ```

3. **Créer la Release sur GitHub**:
    - Aller sur: https://github.com/FayalaMohamed/gestion_locative/releases
    - Cliquer "Draft a new release"
    - **Tag version**: `v0.2` (doit correspondre à APP_VERSION)
    - **Release title**: `Version 0.2 - Description courte`
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
      ### Pour les clients existants:
      1. L'application détectera automatiquement la mise à jour
      2. Cliquez sur "Oui" pour télécharger et installer
      3. L'application redémarrera automatiquement
      
      ### Pour les nouveaux clients:
      1. Téléchargez `GestionLocativePro_v0.2.zip`
      2. Extrayez le dossier
      3. Lancez `GestionLocativePro.exe`
      
      ## Notes:
      - Une sauvegarde de votre base de données sera créée automatiquement
      - Vos données seront préservées
      - Les migrations s'exécutent automatiquement au démarrage
      ```

4. **Uploader les fichiers**:
    - `GestionLocativePro.exe` (obligatoire - l'updater le télécharge)
    - `GestionLocativePro_v0.2.zip` (optionnel - pour nouveaux clients)
    - Notes de release détaillées

### Étape 5: Distribution aux Clients

**Option A: Auto-updater (Recommandé)**
- Les clients ouvrent l'application
- Une notification apparaît automatiquement si une mise à jour est disponible
- Ou: Menu "Aide" → "Vérifier les mises à jour"
- L'application détecte la nouvelle version
- Cliquent "Oui" pour télécharger et installer
- L'application redémarre automatiquement avec les migrations

**Option B: Email manuel**
- Envoyez un email avec le lien GitHub
- Les clients téléchargent manuellement `GestionLocativePro.exe`
- Remplacent le fichier .exe existant
- L'application fait les migrations au démarrage

**Option C: Package complet**
- Envoyez le fichier ZIP complet
- Les clients extraient et remplacent tout le dossier
- Recommandé pour les mises à jour majeures

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
- [ ] Migration Alembic testée: `alembic upgrade head`
- [ ] Logic de migration config ajouté si nécessaire
- [ ] Exécutable buildé et testé localement
- [ ] Toutes les fonctionnalités testées dans l'exécutable
- [ ] Release créée sur GitHub avec tag correct
- [ ] Fichier .exe uploadé comme asset
- [ ] Fichier ZIP créé pour nouveaux clients (optionnel)
- [ ] Notes de release rédigées
- [ ] Test de l'auto-updater fait
- [ ] Documentation mise à jour si nécessaire

## 📝 Exemple Complet: Release v0.1 → v0.2

### Changements:
- Ajout champ `frais_electricite` dans paiements
- Nouveau paramètre dans config pour signatures multiples

### Étapes:

1. **Modifier modèle** (`app/models/entities.py`):
    ```python
    frais_electricite = Column(Numeric(10, 3), nullable=True, default=0)
    ```

2. **Créer migration**:
    ```bash
    conda activate location
    alembic revision --autogenerate -m "Add frais electricite"
    alembic upgrade head
    ```

3. **Modifier config migration** (`main.py`):
    ```python
    def migrate_config():
        config = Config()
        config_version = config.get('app', 'version', default='0')
        
        if config_version != APP_VERSION:
            print(f"Migrating config from v{config_version} to v{APP_VERSION}")
            
            # Migration de v0.1 à v0.2
            if config_version == "0.1":
                # Ajouter support signatures multiples
                if not config.get('receipts', 'signatures'):
                    config.set([], 'receipts', 'signatures')
            
            config.set(APP_VERSION, 'app', 'version')
            config.save_config()
    ```

4. **Mettre à jour version**:
    ```python
    APP_VERSION = "0.2"
    ```

5. **Tester**:
    ```bash
    python run_tests.py
    python main.py
    ```

6. **Builder**:
    ```bash
    pyinstaller --clean gestion_locative.spec
    ```

7. **Tester l'exécutable**:
    ```bash
    cd dist
    GestionLocativePro.exe
    ```

8. **Créer release GitHub** avec tag `v0.2`

9. **Les clients reçoivent la notification** et mettent à jour automatiquement!

---

**Questions?** 
- Consulter le code dans `main.py` pour les exemples de migration
- Vérifier `AGENTS.md` pour les guidelines de développement
- Vérifier `README.md` pour la documentation générale
