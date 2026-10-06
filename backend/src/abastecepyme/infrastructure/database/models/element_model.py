from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, Uuid
from abastecepyme.infrastructure.database.models.base import Base
from abastecepyme.domain.enums.element_type import ElementType

class ElementModel(Base):
    __tablename__ = 'elements'

    id = Column(Uuid(as_uuid=True), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    element_type = Column(SQLEnum(ElementType), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
