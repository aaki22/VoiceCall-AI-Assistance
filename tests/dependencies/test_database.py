from src.dependencies.database import get_db


def test_database_dependency_is_callable():
    assert callable(get_db)
