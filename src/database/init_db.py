from src.database.session import Base, engine
from src.schema import call  # noqa: F401


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
