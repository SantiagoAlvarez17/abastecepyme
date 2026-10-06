from sqlalchemy import Column, ForeignKey, Uuid
from abastecepyme.infrastructure.database.models.base import Base

class DependencyModel(Base):
    __tablename__ = 'element_dependencies'

    requiring_element_id = Column(Uuid(as_uuid=True), ForeignKey('elements.id'), primary_key=True)
    required_element_id = Column(Uuid(as_uuid=True), ForeignKey('elements.id'), primary_key=True)
