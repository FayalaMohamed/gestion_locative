"""Audit logging service for tracking entity changes"""
from datetime import datetime
from typing import Any, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect

from app.models.entities import AuditLog


class AuditService:
    @staticmethod
    def log_create(session: Session, entity) -> AuditLog:
        """Log creation of an entity"""
        table_name = entity.__class__.__name__.lower()
        entity_id = entity.id
        
        data_after = AuditService.entity_to_dict(entity)
        
        audit = AuditLog(
            table_nom=table_name,
            entite_id=entity_id,
            action="CREATE",
            donnees_avant=None,
            donnees_apres=data_after,
            created_at=datetime.utcnow()
        )
        session.add(audit)
        return audit

    @staticmethod
    def log_update(session: Session, entity, before_state: Dict[str, Any]) -> AuditLog:
        """Log update of an entity"""
        table_name = entity.__class__.__name__.lower()
        entity_id = entity.id
        
        data_after = AuditService.entity_to_dict(entity)
        
        audit = AuditLog(
            table_nom=table_name,
            entite_id=entity_id,
            action="UPDATE",
            donnees_avant=before_state,
            donnees_apres=data_after,
            created_at=datetime.utcnow()
        )
        session.add(audit)
        return audit

    @staticmethod
    def log_delete(session: Session, entity_class, entity_id: int, before_state: Dict[str, Any]) -> AuditLog:
        """Log deletion of an entity"""
        table_name = entity_class.__name__.lower()
        
        audit = AuditLog(
            table_nom=table_name,
            entite_id=entity_id,
            action="DELETE",
            donnees_avant=before_state,
            donnees_apres=None,
            created_at=datetime.utcnow()
        )
        session.add(audit)
        return audit

    @staticmethod
    def log_receipt(session: Session, paiement_id: int, receipt_number: str, file_path: str = None) -> AuditLog:
        """Log receipt generation"""
        audit = AuditLog(
            table_nom="paiement",
            entite_id=paiement_id,
            action="RECEIPT_GENERATED",
            donnees_avant=None,
            donnees_apres={"receipt_number": receipt_number, "file_path": file_path},
            created_at=datetime.utcnow()
        )
        session.add(audit)
        return audit

    @staticmethod
    def entity_to_dict(entity) -> Optional[Dict[str, Any]]:
        """Convert an entity to a JSON-compatible dictionary"""
        if entity is None:
            return None
        
        try:
            inspector = inspect(entity)
            result = {}
            
            for attr in inspector.attrs:
                key = attr.key
                value = attr.value
                
                if hasattr(value, '__dict__'):
                    if isinstance(value, list):
                        result[key] = [AuditService.entity_to_dict(item) for item in value]
                    elif hasattr(value, 'id'):
                        result[key] = {"id": value.id}
                    else:
                        result[key] = AuditService.entity_to_dict(value)
                elif isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif hasattr(value, 'value'):
                    result[key] = value.value if isinstance(value.value, (str, int, float, bool, type(None))) else str(value.value)
                elif not callable(value):
                    result[key] = value
            
            return result
        except Exception:
            return None
