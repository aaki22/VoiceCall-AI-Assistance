from src.dependencies.repositories import get_call_repository
from src.repository.call_repository import CallRepository


def test_repository_dependency_factory_returns_repository():
    assert isinstance(get_call_repository(object()), CallRepository)
