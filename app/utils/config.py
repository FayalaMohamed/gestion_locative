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
        
        if not os.path.isabs(path):
            base_dir = Path.cwd()
            path = str(base_dir / path)
        
        return path
    
    @property
    def is_debug(self) -> bool:
        """Check if debug mode is enabled"""
        return self.get('app', 'debug', default=False)
    
    def reload(self) -> None:
        """Reload configuration from file"""
        self._load_config()
