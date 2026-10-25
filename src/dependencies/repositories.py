from sqlalchemy.orm import Session

from src.repository.call_repository import CallRepository


def get_call_repository(db: Session) -> CallRepository:
    return CallRepository(db)
