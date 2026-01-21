"""Base repository class with common CRUD operations"""
from typing import TypeVar, Generic, Optional, List, Type
from sqlalchemy.orm import Session

from app.models.entities import Base


T = TypeVar('T', bound=Base)


class BaseRepository(Generic[T]):
    """Base repository class providing common CRUD operations"""
    
    def __init__(self, session: Session, model_class: Type[T]):
        self.session = session
        self.model_class = model_class
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get an entity by its ID"""
        return self.session.query(self.model_class).filter(
            self.model_class.id == id
        ).first()
    
    def get_all(self) -> List[T]:
        """Get all entities"""
        return self.session.query(self.model_class).all()
    
    def create(self, **kwargs) -> T:
        """Create a new entity"""
        entity = self.model_class(**kwargs)
        self.session.add(entity)
        self.session.flush()
        return entity
    
    def update(self, entity: T, **kwargs) -> T:
        """Update an existing entity"""
        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        self.session.flush()
        return entity
    
    def delete(self, entity: T) -> bool:
        """Delete an entity"""
        try:
            self.session.delete(entity)
            self.session.flush()
            return True
        except Exception:
            self.session.rollback()
            return False
    
    def delete_by_id(self, id: int) -> bool:
        """Delete an entity by its ID"""
        entity = self.get_by_id(id)
        if entity:
            return self.delete(entity)
        return False
    
    def count(self) -> int:
        """Count all entities"""
        return self.session.query(self.model_class).count()
    
    def exists(self, id: int) -> bool:
        """Check if an entity exists by ID"""
        return self.session.query(
            self.session.query(self.model_class).filter(
                self.model_class.id == id
            ).exists()
        ).scalar()
    
    def filter_by(self, **kwargs) -> List[T]:
        """Filter entities by given criteria"""
        query = self.session.query(self.model_class)
        for key, value in kwargs.items():
            if hasattr(self.model_class, key):
                query = query.filter(getattr(self.model_class, key) == value)
        return query.all()
    
    def first(self, **kwargs) -> Optional[T]:
        """Get first entity matching criteria"""
        query = self.session.query(self.model_class)
        for key, value in kwargs.items():
            if hasattr(self.model_class, key):
                query = query.filter(getattr(self.model_class, key) == value)
        return query.first()
