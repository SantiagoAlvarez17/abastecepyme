from typing import List, Optional
from uuid import UUID
from sqlalchemy import func
from sqlalchemy.orm import Session
from abastecepyme.domain.interfaces.element_repository import ElementRepository
from abastecepyme.domain.entities.element import Element
from abastecepyme.infrastructure.database.models.element_model import ElementModel

class SQLElementRepository(ElementRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, element: Element) -> Element:
        model = ElementModel(
            id=element.id,
            name=element.name,
            element_type=element.element_type,
            is_active=element.is_active
        )
        self.db.merge(model)
        self.db.commit()
        return element

    def get_by_id(self, element_id: UUID) -> Optional[Element]:
        model = self.db.query(ElementModel).filter(ElementModel.id == element_id).first()
        if not model:
            return None
        return Element(
            id=model.id,
            name=model.name,
            element_type=model.element_type,
            is_active=model.is_active
        )

    def get_by_name(self, name: str) -> Optional[Element]:
        model = self.db.query(ElementModel).filter(
            func.lower(ElementModel.name) == name.lower()
        ).first()
        if not model:
            return None
        return Element(
            id=model.id,
            name=model.name,
            element_type=model.element_type,
            is_active=model.is_active
        )

    def get_all(self, active_only: bool = True) -> List[Element]:
        query = self.db.query(ElementModel)
        if active_only:
            query = query.filter(ElementModel.is_active == True)
        
        models = query.all()
        return [
            Element(
                id=m.id,
                name=m.name,
                element_type=m.element_type,
                is_active=m.is_active
            ) for m in models
        ]
