from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from abastecepyme.domain.interfaces.dependency_repository import DependencyRepository
from abastecepyme.domain.entities.dependency import Dependency
from abastecepyme.infrastructure.database.models.dependency_model import DependencyModel

class SQLDependencyRepository(DependencyRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, dependency: Dependency) -> Dependency:
        model = DependencyModel(
            requiring_element_id=dependency.requiring_element_id,
            required_element_id=dependency.required_element_id
        )
        self.db.merge(model)
        self.db.commit()
        return dependency

    def get_dependencies_for_element(self, element_id: UUID) -> List[Dependency]:
        models = self.db.query(DependencyModel).filter(
            DependencyModel.requiring_element_id == element_id
        ).all()
        
        return [
            Dependency(
                requiring_element_id=m.requiring_element_id,
                required_element_id=m.required_element_id
            ) for m in models
        ]
