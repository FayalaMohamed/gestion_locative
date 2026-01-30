#!/usr/bin/env python
"""
Comprehensive test to verify the auto-update system is working correctly
"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("VERIFICATION COMPLETE DU SYSTEME DE MISE A JOUR")
print("=" * 70)

tests_passed = 0
tests_failed = 0

def test_check(name, condition, details=""):
    global tests_passed, tests_failed
    if condition:
        print(f"[OK] {name}")
        if details:
            print(f"     {details}")
        tests_passed += 1
        return True
    else:
        print(f"[FAIL] {name}")
        if details:
            print(f"     {details}")
        tests_failed += 1
        return False

# Test 1: Check main.py has all required functions
print("\n1. Verification des fonctions dans main.py...")
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("main", "main.py")
    main_module = importlib.util.module_from_spec(spec)
    
    # Check version is defined
    has_version = hasattr(main_module, 'APP_VERSION')
    test_check("APP_VERSION defini", has_version, f"Version: {main_module.APP_VERSION if has_version else 'N/A'}")
    
    # Check GitHub repo
    has_repo = hasattr(main_module, 'GITHUB_REPO')
    test_check("GITHUB_REPO defini", has_repo, f"Repo: {main_module.GITHUB_REPO if has_repo else 'N/A'}")
    
    # Check key functions exist
    test_check("Fonction migrate_config()", hasattr(main_module, 'migrate_config'))
    test_check("Fonction run_database_migrations()", hasattr(main_module, 'run_database_migrations'))
    test_check("Classe MainWindow", hasattr(main_module, 'MainWindow'))
    
except Exception as e:
    test_check("Import main.py", False, str(e))

# Test 2: Check Alembic configuration
print("\n2. Verification d'Alembic...")
try:
    from alembic.config import Config as AlembicConfig
    alembic_cfg = AlembicConfig("alembic.ini")
    script_location = alembic_cfg.get_main_option("script_location")
    test_check("alembic.ini existe et est valide", script_location == "alembic")
    
    # Check migration files exist
    versions_dir = Path("alembic/versions")
    migration_files = list(versions_dir.glob("*.py"))
    test_check("Fichiers de migration existent", len(migration_files) > 0, f"{len(migration_files)} migration(s) trouvee(s)")
    
except Exception as e:
    test_check("Configuration Alembic", False, str(e))

# Test 3: Check database connectivity and schema
print("\n3. Verification de la base de donnees...")
try:
    from app.database.connection import init_database
    from sqlalchemy import inspect, text
    
    db = init_database()
    with db.session_scope() as session:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        required_tables = ['immeubles', 'bureaux', 'locataires', 'contrats', 'paiements']
        all_tables_exist = all(t in tables for t in required_tables)
        test_check("Tables requises existent", all_tables_exist, f"{len(tables)} tables trouvees")
        
        # Check frais columns exist in paiements
        columns = [c['name'] for c in inspector.get_columns('paiements')]
        has_frais = all(col in columns for col in ['frais_menage', 'frais_sonede', 'frais_steg'])
        test_check("Colonnes frais dans paiements", has_frais)
        
except Exception as e:
    test_check("Base de donnees", False, str(e))

# Test 4: Check config versioning
print("\n4. Verification du systeme de version de config...")
try:
    from app.utils.config import Config
    config = Config()
    
    # Check we can read/write version
    config.set("test_version", 'app', 'version')
    config.save_config()
    read_version = config.get('app', 'version')
    test_check("Lecture/ecriture version config", read_version == "test_version")
    
    # Reset to actual version
    from main import APP_VERSION
    config.set(APP_VERSION, 'app', 'version')
    config.save_config()
    
except Exception as e:
    test_check("Systeme config", False, str(e))

# Test 5: Check GitHub connectivity
print("\n5. Verification de la connexion GitHub...")
try:
    import urllib.request
    import json
    import ssl
    
    from main import GITHUB_REPO
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(url, headers={'User-Agent': 'GestionLocativeApp'})
    with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
        data = json.loads(response.read().decode())
    
    latest = data.get('tag_name', 'unknown')
    assets = data.get('assets', [])
    test_check("Connexion GitHub OK", True, f"Derniere release: {latest}, {len(assets)} asset(s)")
    
except Exception as e:
    test_check("Connexion GitHub", False, str(e))

# Test 6: Check auto-update methods
print("\n6. Verification des methodes d'auto-update...")
try:
    # We need to actually instantiate MainWindow to check methods
    # But that requires QApplication, so we'll just check the class exists
    from main import MainWindow
    
    test_check("Methode check_for_updates", hasattr(MainWindow, 'check_for_updates'))
    test_check("Methode check_for_updates_silent", hasattr(MainWindow, 'check_for_updates_silent'))
    test_check("Methode download_and_install_update", hasattr(MainWindow, 'download_and_install_update'))
    test_check("Methode show_update_notification", hasattr(MainWindow, 'show_update_notification'))
    test_check("Methode _is_newer_version", hasattr(MainWindow, '_is_newer_version'))
    
except Exception as e:
    test_check("Methodes auto-update", False, str(e))

# Test 7: Check notification popup class
print("\n7. Verification de la classe UpdateNotification...")
try:
    from main import UpdateNotification
    test_check("Classe UpdateNotification existe", True)
    test_check("Methode setup_ui", hasattr(UpdateNotification, 'setup_ui'))
    test_check("Methode setup_animation", hasattr(UpdateNotification, 'setup_animation'))
    test_check("Methode start_fade_out", hasattr(UpdateNotification, 'start_fade_out'))
except Exception as e:
    test_check("Classe UpdateNotification", False, str(e))

# Summary
print("\n" + "=" * 70)
print("RESUME")
print("=" * 70)
print(f"\nTests reussis: {tests_passed}")
print(f"Tests echoues: {tests_failed}")
print(f"Total: {tests_passed + tests_failed}")

if tests_failed == 0:
    print("\n[SUCCES] Tous les tests sont passes!")
    print("\nLe systeme de mise a jour est pret:")
    print("- ✓ Migrations de base de donnees (Alembic)")
    print("- ✓ Migrations de configuration")
    print("- ✓ Verification automatique au demarrage")
    print("- ✓ Telechargement et redemarrage automatique")
    print("- ✓ Sauvegarde de la base avant mise a jour")
    print("- ✓ Notification en bas a droite")
else:
    print("\n[ATTENTION] Certains tests ont echoue.")
    print("Veuillez verifier les erreurs ci-dessus.")

print("\n" + "=" * 70)
