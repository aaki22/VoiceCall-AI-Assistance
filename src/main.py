from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from src.constants.audio import GENERATED_AUDIO_DIR
from src.constants.routes import AUDIO_MOUNT_NAME, AUDIO_MOUNT_PATH, HEALTH_DB_PATH, HEALTH_PATH
from src.database.session import engine
from src.exception.handlers import register_exception_handlers
from src.logging.config import configure_logging
from src.routes.voice_webhook import router as voice_webhook_router
from src.settings.settings import settings
from src.utils.file_paths import ensure_audio_dir


def create_app() -> FastAPI:
    configure_logging(settings.log_level)
    app = FastAPI(title=settings.app_name)
    ensure_audio_dir()
    app.mount(AUDIO_MOUNT_PATH, StaticFiles(directory=GENERATED_AUDIO_DIR), name=AUDIO_MOUNT_NAME)
    app.include_router(voice_webhook_router)
    register_exception_handlers(app)

    @app.get(HEALTH_PATH)
    async def health():
        return {"status": "ok"}

    @app.get(HEALTH_DB_PATH)
    async def health_db():
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("src.main:app", host=settings.host, port=settings.port, reload=True)
