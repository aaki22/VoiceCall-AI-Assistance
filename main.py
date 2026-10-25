import uvicorn

from src.main import app
from src.settings.settings import settings


__all__ = ["app"]


if __name__ == "__main__":
    uvicorn.run("src.main:app", host=settings.host, port=settings.port, reload=True)
