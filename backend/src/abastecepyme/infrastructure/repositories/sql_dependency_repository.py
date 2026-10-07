from typing import List
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from abastecepyme.core.exceptions import DuplicateDependencyException
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
        self.db.add(model)
        try:
            self.db.commit()
        except IntegrityError:
            # La clave primaria compuesta impide repetir la arista (incluso con peticiones simultáneas)
            self.db.rollback()
            raise DuplicateDependencyException(
                str(dependency.requiring_element_id),
                str(dependency.required_element_id)
            )
        return dependency

    def exists(self, requiring_element_id: UUID, required_element_id: UUID) -> bool:
        return self.db.query(DependencyModel).filter(
            DependencyModel.requiring_element_id == requiring_element_id,
            DependencyModel.required_element_id == required_element_id
        ).first() is not None

    def get_all(self) -> List[Dependency]:
        models = self.db.query(DependencyModel).all()
        return [
            Dependency(
                requiring_element_id=m.requiring_element_id,
                required_element_id=m.required_element_id
            ) for m in models
        ]

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