"""Configuration management module"""
import os
from pathlib import Path
from typing import Any, Optional

import yaml


class Config:
    """Configuration manager that reads from config.yaml"""
    
    _instance: Optional['Config'] = None
    _config: dict = {}
    
    def __new__(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> 'Config':
        """Get or create the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _load_config(self) -> None:
        """Load configuration from config.yaml"""
        config_path = self._find_config_file()
        
        if config_path and config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = {}
            self._create_default_config()
    
    def _find_config_file(self) -> Optional[Path]:
        """Find config.yaml in current directory or parent directories"""
        current = Path.cwd()
        
        for _ in range(5):
            config_path = current / 'config.yaml'
            if config_path.exists():
                return config_path
            current = current.parent
        
        return None
    
    def _create_default_config(self) -> None:
        """Create default configuration file"""
        default_config = {
            'app': {
                'name': 'Gestion Locative Pro',
                'version': '1.0.0',
                'debug': True
            },
            'database': {
                'type': 'sqlite',
                'path': 'data/gestion_locative.db'
            },
            'export': {
                'default_format': 'json',
                'backup_directory': 'backups'
            },
            'receipts': {
                'template_path': 'app/reports/templates',
                'output_path': 'data/receipts',
                'company_name': 'Gestion Immobilière',
                'company_address': '',
                'company_phone': ''
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'logs/app.log'
            }
        }
        
        self._config = default_config
        self.save_config()
    
    def save_config(self, path: Optional[str] = None) -> None:
        """Save current configuration to file"""
        save_path = Path(path) if path else self._find_config_file()
        
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, allow_unicode=True, default_flow_style=False)
    
    def get(self, *keys: str, default: Any = None) -> Any:
        """Get nested configuration value
        
        Example:
            config.get('database', 'path') -> returns database.path value
        """
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, value: Any, *keys: str) -> None:
        """Set nested configuration value
        
        Example:
            config.set('new_path', 'database', 'path')
        """
        current = self._config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    @property
    def database_path(self) -> str:
        """Get the full database path"""
        db_config = self.get('database', default={})
        path = db_config.get('path', 'data/gestion_locative.db')
        return self._resolve_path(path)

    def _resolve_path(self, path: str, default: str = '.') -> str:
        """Resolve a path, making relative paths absolute based on current directory"""
        if not path:
            return default
        if os.path.isabs(path):
            return path
        base_dir = Path.cwd()
        return str(base_dir / path)

    @property
    def backup_directory(self) -> str:
        """Get the full backup directory path"""
        path = self.get('export', 'backup_directory', default='data/backups')
        return self._resolve_path(path, 'data/backups')

    def get_signature_path(self) -> str:
        """Get the signature path (legacy - returns first signature or empty)"""
        signatures = self.get_signatures()
        if signatures:
            return signatures[0].get('path', '')
        # Fallback to legacy single signature
        path = self.get('receipts', 'signature_path', default='')
        if path:
            return self._resolve_path(path, '')
        return ''
    
    def get_signatures(self) -> list:
        """Get list of all signatures with their names and paths"""
        signatures = self.get('receipts', 'signatures', default=[])
        if not signatures:
            # Check for legacy single signature and migrate
            legacy_path = self.get('receipts', 'signature_path', default='')
            if legacy_path:
                signatures = [{'name': 'Signature 1', 'path': legacy_path}]
                self.set(signatures, 'receipts', 'signatures')
                # Clear legacy path to prevent remigration
                self.set('', 'receipts', 'signature_path')
                self.save_config()
        return signatures or []
    
    def add_signature(self, name: str, path: str) -> None:
        """Add a new signature"""
        signatures = self.get_signatures()
        signatures.append({'name': name, 'path': path})
        self.set(signatures, 'receipts', 'signatures')
        self.save_config()
    
    def remove_signature(self, index: int) -> None:
        """Remove a signature by index"""
        signatures = self.get_signatures()
        if 0 <= index < len(signatures):
            signatures.pop(index)
            self.set(signatures, 'receipts', 'signatures')
            # If no more signatures, clear legacy path to prevent remigration
            if not signatures:
                self.set('', 'receipts', 'signature_path')
            self.save_config()
    
    def get_company_names(self) -> list:
        """Get list of company names used for receipts"""
        names = self.get('receipts', 'company_names', default=[])
        if not names:
            # Check for legacy single company name and migrate
            legacy_name = self.get('receipts', 'company_name', default='')
            if legacy_name and legacy_name != 'Gestion Immobilière':
                names = [legacy_name]
                self.set(names, 'receipts', 'company_names')
                self.save_config()
            else:
                names = ['Gestion Immobilière']
        return names or ['Gestion Immobilière']
    
    def add_company_name(self, name: str) -> None:
        """Add a company name to the list (avoid duplicates)"""
        names = self.get_company_names()
        if name not in names:
            names.append(name)
            self.set(names, 'receipts', 'company_names')
            self.save_config()
    
    def set_default_company_name(self, name: str) -> None:
        """Set the default company name (first in the list)"""
        names = self.get_company_names()
        if name in names:
            names.remove(name)
        names.insert(0, name)
        self.set(names, 'receipts', 'company_names')
        self.save_config()

    @property
    def is_debug(self) -> bool:
        """Check if debug mode is enabled"""
        return self.get('app', 'debug', default=False)
    
    def reload(self) -> None:
        """Reload configuration from file"""
        self._load_config()
