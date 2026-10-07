from fastapi import Depends
from sqlalchemy.orm import Session
from abastecepyme.infrastructure.database.session import get_db
from abastecepyme.infrastructure.repositories.sql_element_repository import SQLElementRepository
from abastecepyme.infrastructure.repositories.sql_dependency_repository import SQLDependencyRepository
from abastecepyme.application.use_cases.create_element import CreateElementUseCase
from abastecepyme.application.use_cases.list_elements import ListElementsUseCase
from abastecepyme.application.use_cases.register_dependency import RegisterDependencyUseCase
from abastecepyme.application.use_cases.list_dependencies import ListDependenciesUseCase
from abastecepyme.application.use_cases.get_graph import GetGraphUseCase

def get_element_repository(db: Session = Depends(get_db)) -> SQLElementRepository:
    return SQLElementRepository(db)

def get_dependency_repository(db: Session = Depends(get_db)) -> SQLDependencyRepository:
    return SQLDependencyRepository(db)

def get_create_element_use_case(
    repo: SQLElementRepository = Depends(get_element_repository)
) -> CreateElementUseCase:
    return CreateElementUseCase(repo)

def get_list_elements_use_case(
    repo: SQLElementRepository = Depends(get_element_repository)
) -> ListElementsUseCase:
    return ListElementsUseCase(repo)

def get_register_dependency_use_case(
    elem_repo: SQLElementRepository = Depends(get_element_repository),
    dep_repo: SQLDependencyRepository = Depends(get_dependency_repository)
) -> RegisterDependencyUseCase:
    return RegisterDependencyUseCase(elem_repo, dep_repo)

def get_list_dependencies_use_case(
    repo: SQLDependencyRepository = Depends(get_dependency_repository)
) -> ListDependenciesUseCase:
    return ListDependenciesUseCase(repo)

def get_graph_use_case(
    elem_repo: SQLElementRepository = Depends(get_element_repository),
    dep_repo: SQLDependencyRepository = Depends(get_dependency_repository)
) -> GetGraphUseCase:
    return GetGraphUseCase(elem_repo, dep_repo)
